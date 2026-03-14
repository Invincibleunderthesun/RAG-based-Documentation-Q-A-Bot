# 🤖 Helios Docs Assistant — RAG-based Q&A Bot

A production-style AI assistant that answers natural language questions about any documentation using **Retrieval-Augmented Generation (RAG)**. Upload your own markdown files and get precise, grounded answers instantly — with conversation memory, source attribution, and full explainability.

> Ask *"What is the rate limit for the login endpoint?"* and get a precise, sourced answer instantly — no ctrl+F, no digging through pages.

---

## 🌐 Live Demo

**[Try it live →]https://rag-based-documentation-q-a-bot-fdlw5yaqszmsuepvhhbsdg.streamlit.app/**

---

## 🎯 What It Does

Engineers waste hours searching through API docs. Helios Docs Assistant lets you upload any markdown documentation and query it in plain English — getting accurate, grounded answers with source attribution. It honestly says *"I couldn't find that"* instead of hallucinating, and remembers context across follow-up questions.

---

## 🏗️ Architecture

```
Your .md files (uploaded via UI)
        │
        ▼
ingest.py ──► Chunking (RecursiveCharacterTextSplitter)
        │
        ▼
Embeddings (sentence-transformers/all-MiniLM-L6-v2)
        │
        ▼
ChromaDB (named collections — storage managed automatically)
        │
        ▼
rag.py ──► Similarity Search → Prompt Engineering → GPT-OSS 120B (Groq)
        │
        ▼
app.py ──► Streamlit Chat UI
```

---

## ✨ Features

- **Dynamic doc upload** — upload any `.md` files via UI, no code changes needed
- **Natural language querying** — ask questions the way you'd ask a colleague
- **Conversation memory** — follow-up questions work naturally without repeating context
- **Source attribution** — every answer cites which doc file it came from
- **Multi-doc filtering** — limit search to a specific document from the sidebar
- **Chunk explainability** — toggle to see exactly which chunks were used to answer
- **Hallucination prevention** — answers only from your docs, never made up
- **Storage management** — old ChromaDB collections cleaned up automatically on re-ingest
- **Clean UX flow** — upload screen → knowledge base build → chat, all guided

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| LLM | GPT-OSS 120B via Groq API |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` |
| Vector Store | ChromaDB (named collections) |
| RAG Framework | LangChain |
| UI | Streamlit |
| Docs Format | Markdown |
| Memory | Sliding window conversation history |

---

## 🚀 Running Locally

### 1. Clone the repo
```bash
git clone https://github.com/Invincibleunderthesun/RAG-based-Documentation-Q-A-Bot.git
cd RAG-based-Documentation-Q-A-Bot
```

### 2. Create and activate virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
Create a `.streamlit/secrets.toml` file:
```toml
GROQ_API_KEY = "your-groq-api-key-here"
```
Get a free API key at [console.groq.com](https://console.groq.com)

### 5. Run the app
```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

### 6. Upload your docs and start asking!
- Upload one or more `.md` files via the UI
- Click **Build Knowledge Base**
- Ask anything about your documentation

---

## 📁 Project Structure

```
RAG-based-Documentation-Q-A-Bot/
│
├── docs/                        # Auto-created when user uploads files
├── chroma_db/                   # Auto-generated vector store (git ignored)
├── venv/                        # Virtual environment (git ignored)
│
├── ingest.py                    # Load, chunk, embed and store docs
├── rag.py                       # Retrieval + LLM pipeline with memory
├── app.py                       # Streamlit chat UI
│
├── .streamlit/
│   └── secrets.toml             # API keys (git ignored)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 💡 Example Questions

Once you upload your docs, try questions like:

- *"What error code do I get for wrong login credentials?"*
- *"Can I cancel an order that has already been shipped?"*
- *"How often are recommendation models retrained?"*
- *"What happens to my data when I delete my account?"*

Then follow up with:
- *"What is the rate limit for that endpoint?"*
- *"And what about partial refunds?"*

The bot remembers context across the conversation.

---

## 🧪 Key Design Decisions

**Named ChromaDB Collections** — Instead of deleting the `chroma_db` folder on re-ingest (which causes Windows file lock errors), old collections are deleted from within ChromaDB itself before creating a new one. This solves both the lock issue and storage bloat.

**Context-aware Retrieval** — Follow-up questions use the last assistant response as additional search context, so vague questions like *"what about its rate limit?"* correctly retrieve the right chunks.

**Grounded Prompting** — The LLM is explicitly instructed to answer only from retrieved context, preventing hallucination. If the answer isn't in the docs, it says so.

---

## 🔧 Adding Your Own Docs

1. Open the app
2. Upload any `.md` files via the upload screen
3. Click **Build Knowledge Base**
4. Start asking questions — that's it!

To update the knowledge base, click **Upload New Docs** in the sidebar and re-upload.

---

## 👤 Author

**Harsh Naik** — Software Engineer 1 @ Rakuten  
[LinkedIn](https://linkedin.com/in/harsh-naik-30b38a201) · [GitHub](https://github.com/Invincibleunderthesun)
