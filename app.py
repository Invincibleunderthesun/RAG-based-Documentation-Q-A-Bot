# app.py
import os

import streamlit as st
from rag import ask
from ingest import run_ingest

# Auto-ingest if chroma_db doesn't exist (needed for cloud deployment)
if not os.path.exists("./chroma_db"):
    with st.spinner("⚙️ Setting up knowledge base for first time..."):
        run_ingest()

# ── Page config ─────────────────────────────────────────────────
st.set_page_config(
    page_title="H Docs Assistant",
    page_icon="🤖",
    layout="centered"
)

# ── Header ───────────────────────────────────────────────────────
st.title("🤖 H Docs Assistant")
st.caption("Ask anything about the User, Orders, or Recommendations APIs")
st.divider()

# ── Chat history (stored in session so it persists while app runs)
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Display previous messages ────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "sources" in msg:
            st.caption(f"📄 Sources: {', '.join(msg['sources'])}")

# ── Chat input ───────────────────────────────────────────────────
if question := st.chat_input("Ask a question about the API docs..."):

    # Show user message
    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})

    # Get answer from RAG pipeline
    with st.chat_message("assistant"):
        with st.spinner("Searching docs..."):
            result = ask(question)

        st.markdown(result["answer"])
        st.caption(f"📄 Sources: {', '.join(result['sources'])}")

    # Save assistant message to history
    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"],
        "sources": result["sources"]
    })
