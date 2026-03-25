class CodeRetriever:
    def __init__(self, embedder, vector_store) -> None:
        self.embedder = embedder
        self.vector_store = vector_store

    def retrieve_context(self, query: str, top_k: int = 5) -> str:
        query_vector = self.embedder.model.encode(query).tolist()
        results = self.vector_store.search(query_vector=query_vector, top_k=top_k)

        formatted_chunks: list[str] = []
        for item in results:
            metadata = item.get("metadata", {})
            file_path = metadata.get("relative_path", "unknown")
            entity_name = metadata.get("name", "unknown")
            code_snippet = item.get("page_content", "")

            formatted_chunks.append(
                "--------------------\n"
                f"File Path: {file_path}\n"
                f"Entity Name: {entity_name}\n"
                f"Code Snippet:\n{code_snippet}"
            )

        return "\n".join(formatted_chunks)

