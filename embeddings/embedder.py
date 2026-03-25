from sentence_transformers import SentenceTransformer


class CodeEmbedder:
    def __init__(self) -> None:
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed_chunks(self, chunks: list[dict]) -> list[dict]:
        page_contents = [chunk.get("page_content", "") for chunk in chunks]
        embeddings = self.model.encode(page_contents).tolist()

        for chunk, embedding in zip(chunks, embeddings):
            chunk["embedding"] = embedding

        return chunks

