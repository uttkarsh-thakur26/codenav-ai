import ast
from pathlib import Path
from typing import Any


class CodeExtractor(ast.NodeVisitor):
    def __init__(self, source_lines: list[str], file_path: str) -> None:
        self.source_lines = source_lines
        self.file_path = file_path
        self.extracted_items: list[dict[str, Any]] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        self._extract_node_data(node, "function")
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> Any:
        self._extract_node_data(node, "function")
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> Any:
        self._extract_node_data(node, "class")
        self.generic_visit(node)

    def _extract_node_data(self, node: ast.AST, item_type: str) -> None:
        start_line = getattr(node, "lineno", None)
        end_line = getattr(node, "end_lineno", start_line)

        if start_line is None or end_line is None:
            return

        raw_code = "".join(self.source_lines[start_line - 1 : end_line])
        self.extracted_items.append(
            {
                "name": getattr(node, "name", ""),
                "type": item_type,
                "file_path": self.file_path,
                "start_line": start_line,
                "end_line": end_line,
                "code": raw_code,
            }
        )


def extract_raw_text(file_path: str, chunk_size: int = 50) -> list[dict[str, Any]]:
    """Split a file into fixed-size line chunks as a fallback when AST parsing
    is unavailable or returns nothing."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines(keepends=True)
    resolved = str(path.resolve())
    chunks: list[dict[str, Any]] = []

    for i in range(0, len(lines), chunk_size):
        chunk_lines = lines[i : i + chunk_size]
        start = i + 1
        end = i + len(chunk_lines)
        chunks.append({
            "name": "raw_chunk",
            "type": "code_block",
            "start_line": start,
            "end_line": end,
            "code": "".join(chunk_lines),
            "file_path": resolved,
        })

    return chunks


def extract_code_entities(file_path: str) -> list[dict[str, Any]]:
    """Extract classes and functions from a source file.

    For .py files the AST-based CodeExtractor is tried first; if the AST yields
    no results (e.g. purely procedural code) or the file is not Python, the raw
    text chunker is used as a fallback.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if path.suffix == ".py":
        source_code = path.read_text(encoding="utf-8")
        source_lines = source_code.splitlines(keepends=True)
        tree = ast.parse(source_code)

        extractor = CodeExtractor(source_lines=source_lines, file_path=str(path.resolve()))
        extractor.visit(tree)

        if extractor.extracted_items:
            return extractor.extracted_items

    return extract_raw_text(file_path)
