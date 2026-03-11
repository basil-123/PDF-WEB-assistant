# 🧠 DocuMind AI — Context-Aware Document Assistant

A production-quality RAG (Retrieval-Augmented Generation) application that allows users to build a **multi-source knowledge base** from PDFs, web pages, and text notes — then query it using an autonomous **ReAct Agent** powered by Meta's Llama 3 (via Groq).

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square)
![LangChain](https://img.shields.io/badge/LangChain-0.3-green?style=flat-square)
![Llama3](https://img.shields.io/badge/LLM-Llama%203%2070B-purple?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

---

## ✨ Key Features

| Feature | Description |
|---|---|
| **Multi-Source RAG** | Upload **PDFs**, scrape **web pages**, or paste **raw text** to build your knowledge base |
| **Web Scraping** | Paste any URL — the system fetches, extracts, and indexes the content automatically |
| **Hybrid Search** | Combines **Semantic Search** (ChromaDB + HuggingFace Embeddings) and **BM25 Keyword Search** for superior retrieval |
| **ReAct Agent** | Uses the Reason+Act framework — the LLM autonomously decides when and how to query the knowledge base, self-corrects, and performs multi-step reasoning |
| **Conversational Memory** | Maintains full context across the chat session for follow-up questions |
| **Source Citations** | Every answer includes citations with source type, filename/URL, and page number |
| **Agent Reasoning UI** | Expandable panel showing the agent's step-by-step thought process (Thought → Action → Observation) |
| **Premium Dark UI** | Glassmorphism-inspired Streamlit interface with gradients, animations, and responsive layout |
| **100% Free Stack** | Llama 3 (70B) via Groq's free tier + local HuggingFace embeddings = **$0 cost** |

---

## 🏗️ Architecture

```
User Query
    │
    ▼
┌──────────────┐
│  ReAct Agent │  (Llama 3 via Groq)
│  Reason+Act  │
└──────┬───────┘
       │  Decides to search
       ▼
┌──────────────────────────┐
│   Hybrid Retriever       │
│  ┌─────────┐ ┌─────────┐ │
│  │  BM25   │ │ Chroma  │ │
│  │ Keyword │ │Semantic │ │
│  └─────────┘ └─────────┘ │
└──────────┬───────────────┘
           │  Returns relevant chunks
           ▼
┌──────────────────────────┐
│   Multi-Source Store     │
│  📄 PDFs                │
│  🌐 Scraped Web Pages   │
│  📝 Text Notes          │
└──────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
cd document_assistant
pip install -r requirements.txt
```

### 2. Get Your Free API Key

1. Go to [console.groq.com](https://console.groq.com/)
2. Sign up (free) and generate an API key (`gsk_...`)
3. Either paste it into the app sidebar or create a `.env` file:

```env
GROQ_API_KEY=gsk_your_key_here
```

### 3. Run

```bash
streamlit run app.py
```

The app opens in your browser at `http://localhost:8501`.

---

## 📖 Usage

1. **Enter your Groq API key** in the sidebar
2. **Add sources** using any combination:
   - 📄 Upload one or more PDF files
   - 🌐 Paste a URL to scrape a web page
   - 📝 Type or paste raw text notes
3. **Ask questions** in the chat — the ReAct agent will autonomously search and reason
4. **Expand the reasoning panel** to see the agent's thought process
5. **Ask follow-ups** — the agent remembers context from the conversation

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| **LLM** | Meta Llama 3 (70B) via [Groq](https://groq.com/) |
| **Embeddings** | `all-MiniLM-L6-v2` (Local, via HuggingFace) |
| **Vector Store** | ChromaDB |
| **Keyword Search** | BM25 (via `rank-bm25`) |
| **Agent Framework** | LangChain (ReAct pattern) |
| **Web Scraping** | BeautifulSoup4 + Requests |
| **UI** | Streamlit |
| **Memory** | LangChain ConversationBufferMemory |

---

## 📁 Project Structure

```
document_assistant/
├── app.py              # Main application (UI + RAG + Agent)
├── requirements.txt    # Python dependencies
├── .env.example        # API key template
├── data_docs/          # Optional: sample PDF storage
└── README.md           # This file
```

---

## 📄 License

MIT License — feel free to use, modify, and distribute.
