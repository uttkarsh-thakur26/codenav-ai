import json
import os

import faiss
import numpy as np


class FAISSRepository:
    def __init__(self, dimension: int = 384) -> None:
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.chunk_store: list[dict] = []

    def add_chunks(self, chunks: list[dict]) -> None:
        if not chunks:
            return

        valid_chunks = [chunk for chunk in chunks if "embedding" in chunk]
        if not valid_chunks:
            return

        embeddings = [chunk["embedding"] for chunk in valid_chunks]
        vectors = np.array(embeddings, dtype=np.float32)
        self.index.add(vectors)

        for chunk in valid_chunks:
            stored_chunk = dict(chunk)
            stored_chunk.pop("embedding", None)
            self.chunk_store.append(stored_chunk)

    def search(self, query_vector: list[float], top_k: int = 5) -> list[dict]:
        if top_k <= 0 or self.index.ntotal == 0:
            return []

        query_vector_np = np.array(query_vector, dtype=np.float32).reshape(1, self.dimension)
        distances, indices = self.index.search(query_vector_np, top_k)

        results: list[dict] = []
        for idx, score in zip(indices[0], distances[0]):
            if idx == -1:
                continue
            if idx >= len(self.chunk_store):
                continue

            matched_chunk = dict(self.chunk_store[idx])
            matched_chunk["score"] = float(score)
            results.append(matched_chunk)

        return results

    def save_local(self, repo_name: str) -> None:
        os.makedirs(os.path.join("data", "indexes"), exist_ok=True)
        indexes_dir = os.path.join(os.getcwd(), "data", "indexes")
        os.makedirs(indexes_dir, exist_ok=True)

        index_path = os.path.join(indexes_dir, f"{repo_name}.index")
        metadata_path = os.path.join(indexes_dir, f"{repo_name}_metadata.json")

        faiss.write_index(self.index, index_path)
        with open(metadata_path, "w", encoding="utf-8") as metadata_file:
            json.dump(self.chunk_store, metadata_file, ensure_ascii=False)

    def load_local(self, repo_name: str) -> bool:
        indexes_dir = os.path.join(os.getcwd(), "data", "indexes")
        index_path = os.path.join(indexes_dir, f"{repo_name}.index")
        metadata_path = os.path.join(indexes_dir, f"{repo_name}_metadata.json")

        if not (os.path.exists(index_path) and os.path.exists(metadata_path)):
            return False

        self.index = faiss.read_index(index_path)
        self.dimension = self.index.d
        with open(metadata_path, encoding="utf-8") as metadata_file:
            self.chunk_store = json.load(metadata_file)
        return True

