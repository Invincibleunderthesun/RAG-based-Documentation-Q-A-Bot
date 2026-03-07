# ingest.py
# Step 1: Load docs → Step 2: Chunk them → Step 3: Embed → Step 4: Store in ChromaDB

from langchain_community.document_loaders import DirectoryLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma

# ── Config ──────────────────────────────────────────────────────
DOCS_PATH = "./docs"
CHROMA_PATH = "./chroma_db"
EMBED_MODEL = "all-MiniLM-L6-v2"   # small, fast, runs locally for free

# ── Step 1: Load all markdown files from /docs ───────────────────
print("📂 Loading documents...")
loader = DirectoryLoader(
    DOCS_PATH,
    glob="**/*.md",
    loader_cls=UnstructuredMarkdownLoader
)
documents = loader.load()
print(f"   Loaded {len(documents)} documents")

# ── Step 2: Split into chunks ────────────────────────────────────
print("✂️  Splitting into chunks...")
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,        # max characters per chunk
    chunk_overlap=50,      # overlap so context isn't lost at boundaries
    separators=["\n## ", "\n### ", "\n", " "]  # split at headings first
)
chunks = splitter.split_documents(documents)
print(f"   Created {len(chunks)} chunks")

# ── Step 3 & 4: Embed and store in ChromaDB ─────────────────────
print("🧠 Embedding and storing in ChromaDB...")
embeddings = SentenceTransformerEmbeddings(model_name=EMBED_MODEL)

db = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=CHROMA_PATH
)

print(f"✅ Done! {len(chunks)} chunks stored in '{CHROMA_PATH}'")
