import os
from dotenv import load_dotenv

# This loads the GOOGLE_API_KEY from your .env file automatically
load_dotenv()

from ingestion.repo_loader import clone_github_repo, cleanup_repo_dir
from parsing.code_parser import extract_code_entities
from processing.chunker import chunk_parsed_data
from embeddings.embedder import CodeEmbedder
from vector_store.faiss_index import FAISSRepository
from retrieval.retriever import CodeRetriever
from rag.generator import AnswerGenerator

def test_full_rag_pipeline():
    test_repo = "https://github.com/encode/starlette" 
    print(f"⏳ Cloning {test_repo}...")
    repo_path = clone_github_repo(test_repo)
    
    try:
        # We are still focusing on the routing file for speed
        target_file = os.path.join(repo_path, "starlette", "routing.py")
        if not os.path.exists(target_file):
            print(f"❌ Could not find {target_file}")
            return
            
        print(f"⏳ Parsing {target_file}...")
        entities = extract_code_entities(target_file)
        
        print("⏳ Chunking data...")
        chunks = chunk_parsed_data(entities, repo_path)
        
        print("⏳ Generating embeddings...")
        embedder = CodeEmbedder()
        embedded_chunks = embedder.embed_chunks(chunks)
        
        print("⏳ Indexing in FAISS...")
        vector_db = FAISSRepository()
        vector_db.add_chunks(embedded_chunks)
        
        # --- ORCHESTRATION ---
        print("⏳ Setting up Retriever and Generator...")
        retriever = CodeRetriever(embedder, vector_db)
        generator = AnswerGenerator() # Initializes Gemini using your .env key
        
        # A complex question requiring the LLM to read the code and explain the logic
        user_question = "Explain how the Route class handles matching. What does it return if it matches?"
        print(f"\n🗣️  User Question: '{user_question}'")
        
        print("⏳ Retrieving context from Vector DB...")
        context = retriever.retrieve_context(user_question, top_k=3)
        
        print("⏳ Sending context and question to Gemini...\n")
        print("🤖 --- Gemini's Response ---")
        answer = generator.generate(user_question, context)
        print(answer)
        print("\n---------------------------\n")
        
    finally:
        print("🧹 Cleaning up...")
        cleanup_repo_dir(repo_path)
        print("✨ Full pipeline test complete!")

if __name__ == "__main__":
    test_full_rag_pipeline()