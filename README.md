# 🤖 NexaCommerce Docs Assistant — RAG-based Q&A Bot

A production-style AI assistant that answers natural language questions about API documentation using **Retrieval-Augmented Generation (RAG)**. Built with LangChain, ChromaDB, Groq (LLaMA 3), and Streamlit.

> Ask *"What is the rate limit for the login endpoint?"* and get a precise, sourced answer instantly — no ctrl+F, no digging through pages.

---

## 🎯 What It Does

Engineers waste hours searching through API docs. This bot lets you query documentation in plain English and get accurate, grounded answers with source attribution — and honestly says *"I couldn't find that"* instead of hallucinating.

---

## 🏗️ Architecture

```
docs/ (Markdown files)
  │
  ▼
ingest.py ──► Chunking (RecursiveCharacterTextSplitter)
  │
  ▼
Embeddings (sentence-transformers/all-MiniLM-L6-v2)
  │
  ▼
ChromaDB (local vector store)
  │
  ▼
rag.py ──► Similarity Search → Prompt Engineering → Groq LLaMA 3
  │
  ▼
app.py ──► Streamlit Chat UI
```

---

## ✨ Features

- **Natural language querying** — ask questions the way you'd ask a colleague
- **Source attribution** — every answer shows which doc file it came from
- **Hallucination prevention** — answers only from your docs, not the model's imagination
- **Persistent vector store** — ingest once, query forever
- **Chat history** — full conversation memory within a session
- **Clean UI** — Streamlit chat interface, runs in the browser

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| LLM | LLaMA 3 8B via Groq API |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` |
| Vector Store | ChromaDB |
| RAG Framework | LangChain |
| UI | Streamlit |
| Docs Format | Markdown |

---

## 🚀 Running Locally

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/nexa-rag.git
cd nexa-rag
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
Create a `.env` file in the project root:
```
GROQ_API_KEY=your-groq-api-key-here
```
Get a free API key at [console.groq.com](https://console.groq.com)

### 5. Ingest your documents
```bash
python ingest.py
```

### 6. Run the app
```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 📁 Project Structure

```
nexa-rag/
│
├── docs/                        # Source documentation (Markdown)
│   ├── user_service.md
│   ├── orders_service.md
│   └── recommendations_service.md
│
├── chroma_db/                   # Auto-generated vector store (git ignored)
├── venv/                        # Virtual environment (git ignored)
│
├── ingest.py                    # Load, chunk, embed and store docs
├── rag.py                       # Retrieval + LLM pipeline
├── app.py                       # Streamlit chat UI
│
├── .env                         # API keys (git ignored)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 💡 Example Questions

- *"What error code do I get if I login with wrong credentials?"*
- *"Can I cancel an order that has already been shipped?"*
- *"How often are recommendation models retrained?"*
- *"What happens to my data when I delete my account?"*
- *"What does a recommendation score of 0.97 mean?"*

---

## 🔧 Adding Your Own Docs

1. Drop any `.md` files into the `docs/` folder
2. Delete the existing `chroma_db/` folder
3. Re-run `python ingest.py`
4. That's it — the bot now knows your new docs

---

## 🌐 Deployment

Deployed on **Streamlit Community Cloud** — [Live Demo →](#)

---

## 👤 Author

**Harsh Naik** — Engineer 1 QA @ Rakuten  
[LinkedIn](https://linkedin.com/in/harsh-naik-30b38a201) · [GitHub](https://github.com/Invincibleunderthesun)