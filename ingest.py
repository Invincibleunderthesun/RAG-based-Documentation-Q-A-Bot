# ingest.py
import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv
load_dotenv()

# ── Config ──────────────────────────────────────────────────────
DOCS_PATH = "./docs"
CHROMA_PATH = "./chroma_db"
EMBED_MODEL = "all-MiniLM-L6-v2"


def run_ingest(collection_name="helios_docs"):
    print("📂 Loading documents...")
    documents = []
    for filename in os.listdir(DOCS_PATH):
        if filename.endswith(".md"):
            filepath = os.path.join(DOCS_PATH, filename)
            loader = TextLoader(filepath, encoding="utf-8")
            docs = loader.load()
            for doc in docs:
                doc.metadata["source"] = filename
            documents.extend(docs)
    print(f"   Loaded {len(documents)} documents")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n## ", "\n### ", "\n", " "]
    )
    chunks = splitter.split_documents(documents)
    print(f"   Created {len(chunks)} chunks")

    print("🧠 Embedding and storing in ChromaDB...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH,
        collection_name=collection_name
    )
    print(
        f"✅ Done! {len(chunks)} chunks stored in collection '{collection_name}'")
    return collection_name


if __name__ == "__main__":
    run_ingest()
