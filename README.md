<p align="center">
  <h1 align="center">🧭 CodeNav AI</h1>
  <p align="center">
    <strong>A full-stack, local RAG assistant for chatting with GitHub repositories.</strong>
  </p>
  <p align="center">
    Clone any public repo. Index it. Ask questions in plain English.<br/>
    Powered by retrieval-augmented generation with OpenAI, FAISS, and a modern React frontend.
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/react-18-61DAFB?logo=react&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/FAISS-vector--search-orange" />
  <img src="https://img.shields.io/badge/OpenAI-GPT--4o-412991?logo=openai&logoColor=white" />
</p>

---

## ✨ Features

| Feature | Description |
|---|---|
| 🐍 **Polyglot Ingestion** | Python files are parsed via AST for precise function/class extraction. JS, TS, and JSX files are chunked using a raw-text strategy. |
| 💾 **Persistent Caching** | Cloned repos and FAISS indexes are stored locally in `data/`, so re-visits are instant. |
| 🔄 **Smart Updates** | Runs `git pull` on cached repos — if the repo hasn't changed, indexing is skipped entirely. |
| 🏗️ **Architecture Summarizer** | One-click generation of a structured Markdown overview of any indexed repository. |
| 🖥️ **Modern UI** | Vite-powered React frontend with Tailwind CSS, real-time Markdown rendering, and a clean chat interface. |

---

## 🛠️ Tech Stack

### Backend

- **[FastAPI](https://fastapi.tiangolo.com/)** — async REST API framework
- **[LangChain](https://www.langchain.com/)** — prompt orchestration and LLM abstraction
- **[OpenAI API](https://platform.openai.com/)** — GPT-4o Turbo for answer generation
- **[FAISS](https://github.com/facebookresearch/faiss)** — high-performance vector similarity search
- **[Sentence Transformers](https://www.sbert.net/)** — `all-MiniLM-L6-v2` for embedding generation
- **[GitPython](https://gitpython.readthedocs.io/)** — repository cloning and management

### Frontend

- **[React 18](https://react.dev/)** + **[Vite](https://vitejs.dev/)** — fast dev server and HMR
- **[Tailwind CSS](https://tailwindcss.com/)** — utility-first styling
- **[Lucide React](https://lucide.dev/)** — icon library
- **[react-markdown](https://github.com/remarkjs/react-markdown)** + **remark-gfm** — Markdown rendering in chat

---

## 📐 Architecture

```
User Question
     │
     ▼
┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌────────────┐    ┌──────────┐
│  Clone   │───▶│  AST / Raw   │───▶│  Embed with  │───▶│  FAISS     │───▶│  OpenAI  │
│  Repo    │    │  Parse       │    │  MiniLM-L6   │    │  Similarity│    │  GPT-4o  │
│ (git)    │    │  Chunking    │    │  v2          │    │  Search    │    │  Answer  │
└──────────┘    └──────────────┘    └──────────────┘    └────────────┘    └──────────┘
```

### How the RAG Pipeline Works

1. **Clone** — The target GitHub repo is cloned (or pulled if already cached) into `data/repos/`.
2. **Parse** — Python files go through AST extraction to isolate functions and classes. JS/TS/JSX files are split into fixed-size text chunks. A `README.md`, if present, is ingested as a documentation chunk.
3. **Embed** — All chunks are encoded into 384-dimensional vectors using `all-MiniLM-L6-v2`.
4. **Index** — Vectors are stored in a FAISS `IndexFlatL2` index, persisted to `data/indexes/`.
5. **Retrieve** — User queries are embedded and matched against the index via L2 similarity search (`top_k=5`).
6. **Generate** — The retrieved code context and the original question are passed to GPT-4o Turbo, which produces a grounded answer citing file paths and line numbers.

---

## 📁 Project Structure

```
codenav-ai/
├── api/
│   └── server.py            # FastAPI endpoints (/index_repo, /ask, /repo_summary, etc.)
├── ingestion/
│   └── repo_loader.py       # Git clone & pull with persistent caching
├── parsing/
│   └── code_parser.py       # AST parser + raw-text fallback chunker
├── processing/
│   └── chunker.py           # Formats parsed entities into retrievable chunks
├── embeddings/
│   └── embedder.py          # Sentence Transformer embedding generation
├── vector_store/
│   └── faiss_index.py       # FAISS index with save/load persistence
├── retrieval/
│   └── retriever.py         # Query embedding + similarity search orchestrator
├── rag/
│   └── generator.py         # LLM prompt construction and answer generation
├── frontend/
│   ├── src/
│   │   ├── components/      # Sidebar, ChatWindow, ChatInput, Message
│   │   ├── services/api.js  # Frontend API abstraction layer
│   │   └── App.jsx          # Root component with state management
│   └── vite.config.js       # Dev server proxy to FastAPI backend
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- An [OpenAI API key](https://platform.openai.com/api-keys)

### 1. Clone the repository

```bash
git clone https://github.com/uttkarsh-thakur26/codenav-ai.git
cd codenav-ai
```

### 2. Backend setup

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-your-key-here
```

### 3. Frontend setup

```bash
cd frontend
npm install
cd ..
```

---

## ▶️ Running the App

Open **two terminals** from the project root:

**Terminal 1 — Backend**

```bash
uvicorn api.server:app --reload --reload-exclude "data/*"
```

**Terminal 2 — Frontend**

```bash
cd frontend
npm run dev
```

The frontend dev server proxies API requests to the FastAPI backend automatically (configured in `vite.config.js`).

| Service  | URL                     |
|----------|-------------------------|
| Frontend | http://localhost:5173   |
| Backend  | http://localhost:8000   |
| API Docs | http://localhost:8000/docs |

---

## 🔒 What's Excluded from Git

The `.gitignore` ensures sensitive and generated data never reaches the repository:

| Path | Reason |
|---|---|
| `data/` | Cloned repos and FAISS indexes (local cache) |
| `.env` | API keys and secrets |
| `venv/` | Python virtual environment |
| `__pycache__/` | Python bytecode |
| `frontend/node_modules/` | npm dependencies |

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/index_repo` | Clone and index a GitHub repository |
| `POST` | `/ask` | Ask a question about the indexed repo |
| `GET` | `/repo_summary` | Generate an architecture summary |
| `GET` | `/cached_repos` | List all locally cached repositories |
| `DELETE` | `/cached_repos/{name}` | Delete a cached repository and its index |

---

## 👤 Author

**Uttkarsh Thakur**
- GitHub: [@uttkarsh-thakur26](https://github.com/uttkarsh-thakur26)

---

<p align="center">
  Built with 🧠 RAG, ⚡ FAISS, and ☕ late-night debugging.
</p>
