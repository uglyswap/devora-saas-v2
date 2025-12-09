"""
Document Loader for RAG

Provides utilities for:
- Loading documents from various formats (MD, Python, TypeScript, etc.)
- Chunking documents into smaller pieces for embedding
- Extracting relevant sections from code files
"""

import logging
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class DocumentType(str, Enum):
    MARKDOWN = "markdown"
    PYTHON = "python"
    TYPESCRIPT = "typescript"
    JAVASCRIPT = "javascript"
    JSON = "json"
    YAML = "yaml"
    TEXT = "text"
    CODE = "code"


@dataclass
class Document:
    id: str
    content: str
    source: str
    doc_type: DocumentType
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Chunk:
    id: str
    content: str
    source: str
    doc_type: DocumentType
    start_line: int
    end_line: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChunkConfig:
    chunk_size: int = 1000
    chunk_overlap: int = 200
    min_chunk_size: int = 100
    max_chunk_size: int = 2000
    split_by_headers: bool = True
    split_by_functions: bool = True


class DocumentLoader:
    TYPE_MAP = {
        ".md": DocumentType.MARKDOWN,
        ".py": DocumentType.PYTHON,
        ".ts": DocumentType.TYPESCRIPT,
        ".tsx": DocumentType.TYPESCRIPT,
        ".js": DocumentType.JAVASCRIPT,
        ".jsx": DocumentType.JAVASCRIPT,
        ".json": DocumentType.JSON,
        ".yaml": DocumentType.YAML,
        ".yml": DocumentType.YAML,
        ".txt": DocumentType.TEXT,
    }

    def __init__(self, config: Optional[ChunkConfig] = None):
        self.config = config or ChunkConfig()

    def load_file(self, file_path: str) -> Optional[Document]:
        path = Path(file_path)
        if not path.exists():
            return None
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            return None
        ext = path.suffix.lower()
        doc_type = self.TYPE_MAP.get(ext, DocumentType.TEXT)
        return Document(
            id=str(path.absolute()),
            content=content,
            source=str(path),
            doc_type=doc_type,
            metadata={"filename": path.name, "extension": ext},
        )

    def load_directory(self, directory: str, extensions: Optional[List[str]] = None, recursive: bool = True) -> List[Document]:
        path = Path(directory)
        if not path.exists():
            return []
        documents = []
        pattern = "**/*" if recursive else "*"
        ignore = ["node_modules", "__pycache__", ".git", "venv"]
        for fp in path.glob(pattern):
            if fp.is_dir() or any(p in str(fp) for p in ignore):
                continue
            if extensions and fp.suffix.lower() not in extensions:
                continue
            doc = self.load_file(str(fp))
            if doc:
                documents.append(doc)
        return documents

    def chunk_document(self, document: Document) -> List[Chunk]:
        if document.doc_type == DocumentType.MARKDOWN:
            return self._chunk_markdown(document)
        return self._chunk_text(document)

    def chunk_documents(self, documents: List[Document]) -> List[Chunk]:
        all_chunks = []
        for doc in documents:
            all_chunks.extend(self.chunk_document(doc))
        return all_chunks

    def _chunk_markdown(self, document: Document) -> List[Chunk]:
        chunks = []
        lines = document.content.split("\n")
        current_chunk, current_start, chunk_index = [], 0, 0
        for i, line in enumerate(lines):
            if line.startswith("#") and current_chunk:
                content = "\n".join(current_chunk)
                if len(content) >= self.config.min_chunk_size:
                    chunks.append(Chunk(
                        id=f"{document.id}#chunk-{chunk_index}",
                        content=content, source=document.source,
                        doc_type=document.doc_type, start_line=current_start,
                        end_line=i-1, metadata=document.metadata
                    ))
                    chunk_index += 1
                current_chunk, current_start = [line], i
            else:
                current_chunk.append(line)
        if current_chunk:
            content = "\n".join(current_chunk)
            if len(content) >= self.config.min_chunk_size:
                chunks.append(Chunk(
                    id=f"{document.id}#chunk-{chunk_index}",
                    content=content, source=document.source,
                    doc_type=document.doc_type, start_line=current_start,
                    end_line=len(lines)-1, metadata=document.metadata
                ))
        return chunks

    def _chunk_text(self, document: Document) -> List[Chunk]:
        chunks = []
        lines = document.content.split("\n")
        current_chunk, current_start, current_len, chunk_index = [], 0, 0, 0
        for i, line in enumerate(lines):
            current_chunk.append(line)
            current_len += len(line) + 1
            if current_len >= self.config.chunk_size:
                content = "\n".join(current_chunk)
                chunks.append(Chunk(
                    id=f"{document.id}#chunk-{chunk_index}",
                    content=content, source=document.source,
                    doc_type=document.doc_type, start_line=current_start,
                    end_line=i, metadata=document.metadata
                ))
                chunk_index += 1
                current_chunk, current_start, current_len = [], i+1, 0
        if current_chunk:
            content = "\n".join(current_chunk)
            if len(content) >= self.config.min_chunk_size:
                chunks.append(Chunk(
                    id=f"{document.id}#chunk-{chunk_index}",
                    content=content, source=document.source,
                    doc_type=document.doc_type, start_line=current_start,
                    end_line=len(lines)-1, metadata=document.metadata
                ))
        return chunks


def load_and_chunk_files(paths: List[str], config: Optional[ChunkConfig] = None) -> List[Chunk]:
    loader = DocumentLoader(config)
    documents = []
    for path in paths:
        p = Path(path)
        if p.is_file():
            doc = loader.load_file(str(p))
            if doc:
                documents.append(doc)
        elif p.is_dir():
            documents.extend(loader.load_directory(str(p)))
    return loader.chunk_documents(documents)
