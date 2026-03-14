# app.py
import os
import shutil
import importlib
import streamlit as st
from ingest import run_ingest

st.set_page_config(
    page_title="Helios Docs Assistant — Ask Your Documentation",
    page_icon="🤖",
    layout="wide"
)

# ── Session state defaults ────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "docs_ready" not in st.session_state:
    st.session_state.docs_ready = False
if "uploaded_doc_names" not in st.session_state:
    st.session_state.uploaded_doc_names = []

# ── Helper: wipe and re-ingest ────────────────────────────────────


def ingest_docs(files):
    # Save uploaded files to docs/
    if os.path.exists("./docs"):
        shutil.rmtree("./docs")
    os.makedirs("./docs")

    for f in files:
        with open(os.path.join("./docs", f.name), "wb") as out:
            out.write(f.getbuffer())

    # Delete old collections from ChromaDB (solves storage bloat)
    try:
        import chromadb
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        existing = client.list_collections()
        for col in existing:
            if col.name.startswith("helios_"):
                client.delete_collection(col.name)
                print(f"🗑️ Deleted old collection: {col.name}")
    except Exception as e:
        print(f"Could not clean old collections: {e}")

    # Create new unique collection
    import time
    collection_name = f"helios_{int(time.time())}"
    st.session_state.collection_name = collection_name

    run_ingest(collection_name=collection_name)

    import rag
    importlib.reload(rag)


# ════════════════════════════════════════════════════════════════
# SCREEN 1 — Upload screen (shown when no docs are ready)
# ════════════════════════════════════════════════════════════════
if not st.session_state.docs_ready:
    # Centered upload UI
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.title("🤖 Helios Docs Assistant")
        st.subheader("Ask questions about any documentation")
        st.markdown(
            "Upload your markdown (`.md`) files and I'll answer "
            "any question about them instantly — with source attribution."
        )
        st.divider()

        uploaded_files = st.file_uploader(
            "Upload your documentation files",
            type=["md"],
            accept_multiple_files=True,
            help="Upload one or more .md files — API docs, guides, READMEs, anything"
        )

        if uploaded_files:
            st.markdown(f"**{len(uploaded_files)} file(s) ready to upload:**")
            for f in uploaded_files:
                st.markdown(f"- 📄 `{f.name}` ({round(f.size/1024, 1)} KB)")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 Build Knowledge Base", use_container_width=True, type="primary"):
                with st.spinner("Reading and indexing your documents..."):
                    ingest_docs(uploaded_files)
                    st.session_state.docs_ready = True
                    st.session_state.uploaded_doc_names = [
                        f.name for f in uploaded_files]
                    st.session_state.messages = []
                st.rerun()
        else:
            st.info("👆 Upload at least one `.md` file to get started")

# ════════════════════════════════════════════════════════════════
# SCREEN 2 — Chat screen (shown once docs are ingested)
# ════════════════════════════════════════════════════════════════
else:
    from rag import ask

    # ── Sidebar ──────────────────────────────────────────────────
    with st.sidebar:
        st.title("⚙️ Settings")
        st.divider()

        # Uploaded docs info
        st.subheader("📚 Knowledge Base")
        for name in st.session_state.uploaded_doc_names:
            st.markdown(f"- 📄 `{name}`")

        # Multi-doc filtering
        st.divider()
        st.subheader("🔍 Filter by Document")
        filter_options = ["All Documents"] + \
            st.session_state.uploaded_doc_names
        filter_source = st.selectbox("Search in:", filter_options)

        # Explainability toggle
        st.divider()
        st.subheader("🧠 Explainability")
        show_chunks = st.toggle(
            "Show retrieved chunks", value=False,
            help="See exactly which parts of the docs were used to answer"
        )

        # Upload new docs
        st.divider()
        st.subheader("📄 Upload New Docs")
        new_files = st.file_uploader(
            "Replace knowledge base",
            type=["md"],
            accept_multiple_files=True
        )
        if new_files:
            if st.button("🔄 Re-ingest", use_container_width=True):
                with st.spinner("Re-indexing..."):
                    ingest_docs(new_files)
                    st.session_state.uploaded_doc_names = [
                        f.name for f in new_files]
                    st.session_state.messages = []
                st.success("✅ Knowledge base updated!")
                st.rerun()

        # Reset everything
        st.divider()
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        if st.button("⬅️ Upload New Docs", use_container_width=True):
            st.session_state.docs_ready = False
            st.session_state.messages = []
            st.session_state.uploaded_doc_names = []
            st.rerun()

    # ── Chat area ─────────────────────────────────────────────────
    st.title("🤖 Helios Docs Assistant")
    doc_list = ", ".join(
        [f"`{n}`" for n in st.session_state.uploaded_doc_names])
    st.caption(f"Answering questions about: {doc_list}")
    st.divider()

    # Display previous messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                if msg.get("sources"):
                    st.caption(f"📄 Sources: {', '.join(msg['sources'])}")
                if show_chunks and msg.get("chunks"):
                    with st.expander("🧠 View retrieved chunks"):
                        for i, chunk in enumerate(msg["chunks"]):
                            st.markdown(
                                f"**Chunk {i+1}** — `{chunk['source']}`")
                            st.code(chunk["content"], language="markdown")
                            st.divider()

    # Chat input
    if question := st.chat_input("Ask anything about your docs..."):
        with st.chat_message("user"):
            st.markdown(question)
        st.session_state.messages.append({"role": "user", "content": question})

        with st.chat_message("assistant"):
            with st.spinner("Searching docs..."):
                history = st.session_state.messages[:-1]
                filter_val = None if filter_source == "All Documents" else filter_source
                result = ask(question, chat_history=history,
                             filter_source=filter_val)

            st.markdown(result["answer"])
            if result["sources"]:
                st.caption(f"📄 Sources: {', '.join(result['sources'])}")
            if show_chunks and result["chunks"]:
                with st.expander("🧠 View retrieved chunks"):
                    for i, chunk in enumerate(result["chunks"]):
                        st.markdown(f"**Chunk {i+1}** — `{chunk['source']}`")
                        st.code(chunk["content"], language="markdown")
                        st.divider()

        st.session_state.messages.append({
            "role": "assistant",
            "content": result["answer"],
            "sources": result["sources"],
            "chunks": result["chunks"]
        })
