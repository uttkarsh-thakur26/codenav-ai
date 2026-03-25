import os


def chunk_parsed_data(parsed_entities: list[dict], repo_path: str) -> list[dict]:
    chunks: list[dict] = []

    for entity in parsed_entities:
        file_path = entity.get("file_path", "")
        relative_path = ""
        if file_path:
            try:
                # Works for absolute/relative paths on the same drive.
                relative_path = os.path.relpath(file_path, repo_path)
            except ValueError:
                # On Windows, relpath can fail for different drives.
                relative_path = file_path

        page_content = (
            f"File: {relative_path}\n"
            f"Type: {entity.get('type', '')}\n"
            f"Name: {entity.get('name', '')}\n"
            "Code:\n"
            f"{entity.get('code', '')}"
        )

        chunks.append(
            {
                "page_content": page_content,
                "metadata": {
                    "relative_path": relative_path,
                    "name": entity.get("name", ""),
                    "type": entity.get("type", ""),
                    "start_line": entity.get("start_line"),
                    "end_line": entity.get("end_line"),
                },
            }
        )

    return chunks

