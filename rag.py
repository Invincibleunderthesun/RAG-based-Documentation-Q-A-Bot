# rag.py
import os
import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

# ── Config ───────────────────────────────────────────────────────
CHROMA_PATH = "./chroma_db"
EMBED_MODEL = "all-MiniLM-L6-v2"
TOP_K = 4

# ── Load ChromaDB & Groq client (once on startup) ────────────────
embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)


def get_db():
    try:
        collection = st.session_state.get("collection_name", "helios_docs")
    except Exception:
        collection = "helios_docs"
    return Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings,
        collection_name=collection
    )


db = get_db()

try:
    api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("❗ GROQ_API_KEY not found!")
    st.stop()

client = Groq(api_key=api_key)

# ── Core RAG function with conversation memory ───────────────────


def ask(question: str, chat_history: list = [], filter_source: str = None) -> dict:

    # 1. Build smarter search query using last assistant answer as context
    if chat_history and len(chat_history) >= 2:
        # Get last assistant response to give retrieval better context
        last_assistant = next(
            (m["content"]
             for m in reversed(chat_history) if m["role"] == "assistant"),
            ""
        )
        # Combine last answer + current question for richer retrieval
        search_query = f"{last_assistant[:300]} {question}"
    else:
        search_query = question

    # 2. Search ChromaDB — with optional source filter
    if filter_source and filter_source != "All Services":
        results = db.similarity_search(
            search_query,
            k=TOP_K,
            filter={"source": filter_source}
        )
    else:
        results = db.similarity_search(search_query, k=TOP_K)

    # 3. Build context from chunks
    context = "\n\n---\n\n".join([doc.page_content for doc in results])

    # 4. Build messages array with full chat history for memory
    system_prompt = """You are a helpful assistant for documents present.
Answer questions using ONLY the context provided below.
If the answer is not in the context, say "I couldn't find that in the documentation."
Be concise, specific, and refer to previous messages in the conversation if relevant.

CONTEXT:
""" + context

    # Convert chat history to Groq message format
    messages = [{"role": "system", "content": system_prompt}]
    for msg in chat_history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": question})

    # 5. Call Groq with full conversation
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages,
        max_tokens=8192,
        stream=False
    )

    answer = response.choices[0].message.content

    # 6. Return answer + sources + raw chunks (for explainability)
    sources = list(set([
        doc.metadata.get("source", "unknown")
        for doc in results
    ]))

    chunks = [
        {
            "content": doc.page_content,
            "source": doc.metadata.get("source", "unknown")
        }
        for doc in results
    ]

    return {
        "answer": answer,
        "sources": sources,
        "chunks": chunks  # we'll use this in Feature 2
    }
