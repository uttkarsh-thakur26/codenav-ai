import os
import shutil
import stat

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from embeddings.embedder import CodeEmbedder
from ingestion.repo_loader import clone_github_repo
from parsing.code_parser import extract_code_entities
from processing.chunker import chunk_parsed_data
from rag.generator import AnswerGenerator
from retrieval.retriever import CodeRetriever
from vector_store.faiss_index import FAISSRepository


load_dotenv()

app = FastAPI(title="CodeNav AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows your React app to connect
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

active_retriever = None
active_generator = None
active_repo_name = None


class RepoRequest(BaseModel):
    url: str


class AskRequest(BaseModel):
    question: str


def _remove_readonly(func, path, _):
    """Clear the readonly bit and reattempt the removal."""
    os.chmod(path, stat.S_IWRITE)
    func(path)


def _extract_repo_name(repo_url: str) -> str:
    cleaned = repo_url.strip().rstrip("/")
    name = cleaned.rsplit("/", 1)[-1]
    if name.endswith(".git"):
        name = name[:-4]
    if not name:
        raise ValueError(f"Could not determine repository name from URL: {repo_url}")
    return name


@app.post("/index_repo")
def index_repo(request: RepoRequest) -> dict:
    global active_retriever, active_generator, active_repo_name

    try:
        repo_name = _extract_repo_name(request.url)
        repo_path, has_changes = clone_github_repo(request.url)
        vector_db = FAISSRepository()
        embedder = CodeEmbedder()

        if not has_changes and vector_db.load_local(repo_name):
            active_retriever = CodeRetriever(embedder=embedder, vector_store=vector_db)
            active_generator = AnswerGenerator()
            active_repo_name = repo_name
            return {"status": "success", "cache_hit": True, "indexed_chunks": len(vector_db.chunk_store)}

        ignore_dirs = {'.git', 'venv', '.venv', 'env', 'node_modules', '__pycache__', 'dist', 'build'}
        allowed_extensions = {'.py', '.js', '.jsx', '.ts', '.tsx'}

        parsed_entities: list[dict] = []
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            for file_name in files:
                if os.path.splitext(file_name)[1] not in allowed_extensions:
                    continue

                file_path = os.path.join(root, file_name)
                parsed_entities.extend(extract_code_entities(file_path))

        chunks = chunk_parsed_data(parsed_entities=parsed_entities, repo_path=repo_path)

        readme_path = next(
            (os.path.join(repo_path, f) for f in os.listdir(repo_path) if f.lower() == "readme.md"),
            None,
        )
        if readme_path and os.path.isfile(readme_path):
            with open(readme_path, encoding="utf-8", errors="ignore") as readme_file:
                readme_text = readme_file.read()
            chunks.append({
                "page_content": f"File: README.md\nType: documentation\nName: Project Readme\nContent:\n{readme_text}",
                "metadata": {
                    "relative_path": "README.md",
                    "type": "documentation",
                    "name": "Project Readme",
                },
            })

        embedded_chunks = embedder.embed_chunks(chunks)

        vector_db.add_chunks(embedded_chunks)
        vector_db.save_local(repo_name)

        active_retriever = CodeRetriever(embedder=embedder, vector_store=vector_db)
        active_generator = AnswerGenerator()
        active_repo_name = repo_name

        return {"status": "success", "cache_hit": False, "indexed_chunks": len(chunks)}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to index repository: {exc}") from exc


@app.post("/ask")
def ask_question(request: AskRequest) -> dict:
    if active_retriever is None or active_generator is None:
        raise HTTPException(
            status_code=400,
            detail="No repository indexed. Please call /index_repo first.",
        )

    try:
        context = active_retriever.retrieve_context(request.question, top_k=5)
        answer = active_generator.generate(request.question, context)
        return {"answer": answer}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to generate answer: {exc}") from exc


@app.get("/cached_repos")
def list_cached_repos() -> dict:
    repos_dir = os.path.join("data", "repos")
    if not os.path.isdir(repos_dir):
        return {"repos": []}

    repos = [
        name for name in os.listdir(repos_dir)
        if not name.startswith(".") and os.path.isdir(os.path.join(repos_dir, name))
    ]
    return {"repos": sorted(repos)}


@app.delete("/cached_repos/{repo_name}")
def delete_cached_repo(repo_name: str) -> dict:
    global active_retriever, active_generator, active_repo_name

    repo_dir = os.path.join("data", "repos", repo_name)
    index_file = os.path.join("data", "indexes", f"{repo_name}.index")
    meta_file = os.path.join("data", "indexes", f"{repo_name}_metadata.json")

    try:
        if os.path.exists(repo_dir):
            shutil.rmtree(repo_dir, onerror=_remove_readonly)
        if os.path.exists(index_file):
            os.remove(index_file)
        if os.path.exists(meta_file):
            os.remove(meta_file)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to delete {repo_name}: {exc}") from exc

    if active_repo_name == repo_name:
        active_retriever = None
        active_generator = None
        active_repo_name = None

    return {"status": "success", "message": f"Deleted {repo_name}"}


@app.get("/repo_summary")
def repo_summary() -> dict:
    if active_retriever is None or active_generator is None:
        raise HTTPException(
            status_code=400,
            detail="No repository is currently indexed.",
        )

    search_query = "README architecture system design tech stack main entry setup configuration"

    prompt = (
        "Analyze the provided codebase context and generate a comprehensive Architecture Summary. "
        "Do not invent information. Format the output strictly in Markdown with the following structure:\n\n"
        "# 🏗️ Project Architecture Summary\n"
        "## 🎯 Purpose (What does this project do?)\n"
        "## 💻 Tech Stack (Languages, Frameworks, Databases)\n"
        "## 🧩 Core Components (Key files/folders and their roles)\n"
        "## 🚀 Key Features\n\n"
        "Make it highly readable and professional."
    )

    try:
        context = active_retriever.retrieve_context(search_query, top_k=5)
        summary = active_generator.generate(prompt, context)
        return {"summary": summary}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {exc}") from exc

