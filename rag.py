# rag.py
# Takes a user question → finds relevant chunks → asks Claude → returns answer

import os
from urllib import response

from click import prompt
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from dotenv import load_dotenv
from groq import Groq

# ── Config ──────────────────────────────────────────────────────
CHROMA_PATH = "./chroma_db"
EMBED_MODEL = "all-MiniLM-L6-v2"
TOP_K = 4   # how many chunks to retrieve per question
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
# ── Load ChromaDB (runs once when app starts) ────────────────────
embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)

# ── Core RAG function ────────────────────────────────────────────


def ask(question: str) -> dict:
    # 1. Search ChromaDB for most relevant chunks
    results = db.similarity_search(question, k=TOP_K)

    # 2. Build context from retrieved chunks
    context = "\n\n---\n\n".join([doc.page_content for doc in results])

    # 3. Build prompt
    prompt = f"""You are a helpful assistant for NexaCommerce API documentation.
Answer the user's question using ONLY the context provided below.
If the answer is not in the context, say "I couldn't find that in the documentation."
Always be concise and specific.

CONTEXT:
{context}

QUESTION:
{question}
"""

    # 4. Call Claude API
    # Replace the client.messages.create block with:
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",   # free, fast model
        messages=[{"role": "user", "content": prompt}],
        temperature=1,
        max_completion_tokens=8192,
        top_p=1,
        reasoning_effort="medium",
        stream=False,
        stop=None
    )

    answer = response.choices[0].message.content

    # 5. Return answer + the sources used
    sources = list(set([
        doc.metadata.get("source", "unknown").split("\\")[-1]
        for doc in results
    ]))

    return {"answer": answer, "sources": sources}


# ── Quick test (only runs when you execute this file directly) ───
if __name__ == "__main__":
    test_questions = [
        "What error code do I get if I try to login with wrong credentials?",
        "Can I cancel an order that has already been shipped?",
        "How often are recommendation models retrained?",
    ]

    for q in test_questions:
        print(f"\n❓ {q}")
        result = ask(q)
        print(f"💬 {result['answer']}")
        print(f"📄 Sources: {result['sources']}")
        print("-" * 60)
