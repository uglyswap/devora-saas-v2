"""
RAG Engine - Moteur de Retrieval-Augmented Generation

Ce module orchestre le systeme RAG complet pour enrichir le contexte des agents avec:
- Documentation des librairies
- Patterns de code existants
- Historique des generations reussies
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

from .embeddings import EmbeddingService, EmbeddingProvider
from .vector_store import VectorStore, VectorStoreConfig, VectorStoreType, SearchResult
from .document_loader import DocumentLoader, ChunkConfig, Chunk, load_and_chunk_files

logger = logging.getLogger(__name__)


class RAGSource(str, Enum):
    DOCS = "docs"
    PATTERNS = "patterns"
    HISTORY = "history"
    CODE = "code"
    ALL = "all"


@dataclass
class RAGConfig:
    embedding_api_key: str
    embedding_model: str = "openai/text-embedding-3-small"
    embedding_provider: EmbeddingProvider = EmbeddingProvider.OPENROUTER
    vector_store_type: VectorStoreType = VectorStoreType.MEMORY
    score_threshold: float = 0.7
    max_context_tokens: int = 4000
    chunk_size: int = 1000
    chunk_overlap: int = 200


@dataclass
class RetrievedContext:
    content: str
    source: str
    score: float
    source_type: RAGSource
    metadata: Dict[str, Any] = field(default_factory=dict)


class RAGEngine:
    def __init__(self, config: RAGConfig):
        self.config = config
        self.embedding_service = EmbeddingService(
            api_key=config.embedding_api_key,
            model=config.embedding_model,
            provider=config.embedding_provider,
        )
        vector_config = VectorStoreConfig(
            store_type=config.vector_store_type,
            dimension=1536,
        )
        self.vector_store = VectorStore(vector_config)
        self.document_loader = DocumentLoader(
            ChunkConfig(
                chunk_size=config.chunk_size,
                chunk_overlap=config.chunk_overlap,
            )
        )
        self._initialized = False
        self._stats = {"queries": 0, "documents_indexed": 0, "retrievals": 0}

    async def initialize(self):
        if self._initialized:
            return
        logger.info("[RAGEngine] Initializing...")
        self._initialized = True
        logger.info("[RAGEngine] Ready")

    async def index_documents(
        self,
        paths: List[str],
        source_type: RAGSource = RAGSource.DOCS,
    ) -> int:
        logger.info(f"[RAGEngine] Indexing documents from {len(paths)} paths...")
        chunks = load_and_chunk_files(
            paths,
            ChunkConfig(
                chunk_size=self.config.chunk_size,
                chunk_overlap=self.config.chunk_overlap,
            )
        )
        if not chunks:
            logger.warning("[RAGEngine] No chunks to index")
            return 0
        texts = [c.content for c in chunks]
        embeddings = await self.embedding_service.embed_batch(texts)
        ids = [c.id for c in chunks]
        metadatas = [{**c.metadata, "source_type": source_type.value} for c in chunks]
        await self.vector_store.add_batch(ids, texts, embeddings, metadatas)
        self._stats["documents_indexed"] += len(chunks)
        logger.info(f"[RAGEngine] Indexed {len(chunks)} chunks")
        return len(chunks)

    async def index_text(
        self,
        text: str,
        source: str,
        source_type: RAGSource = RAGSource.DOCS,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        doc_id = f"{source_type.value}:{source}"
        embedding = await self.embedding_service.embed_text(text)
        meta = metadata or {}
        meta["source_type"] = source_type.value
        await self.vector_store.add(doc_id, text, embedding, meta)
        self._stats["documents_indexed"] += 1
        return doc_id

    async def retrieve_relevant_context(
        self,
        query: str,
        sources: Optional[List[RAGSource]] = None,
        k: int = 5,
    ) -> List[RetrievedContext]:
        sources = sources or [RAGSource.ALL]
        self._stats["queries"] += 1
        query_embedding = await self.embedding_service.embed_text(query)
        filter_meta = None
        if RAGSource.ALL not in sources:
            filter_meta = {"source_type": sources[0].value}
        results = await self.vector_store.search(query_embedding, top_k=k, filter_metadata=filter_meta)
        contexts = []
        for r in results:
            if r.score >= self.config.score_threshold:
                source_type = RAGSource(r.metadata.get("source_type", "docs"))
                contexts.append(RetrievedContext(
                    content=r.text,
                    source=r.id,
                    score=r.score,
                    source_type=source_type,
                    metadata=r.metadata,
                ))
        self._stats["retrievals"] += len(contexts)
        logger.info(f"[RAGEngine] Retrieved {len(contexts)} contexts for query")
        return contexts

    async def augment_prompt(
        self,
        original_prompt: str,
        contexts: List[RetrievedContext],
        max_context_chars: Optional[int] = None,
    ) -> str:
        if not contexts:
            return original_prompt
        max_chars = max_context_chars or (self.config.max_context_tokens * 4)
        context_parts = []
        current_length = 0
        for ctx in sorted(contexts, key=lambda x: x.score, reverse=True):
            if current_length + len(ctx.content) > max_chars:
                break
            context_parts.append(f"[{ctx.source_type.value.upper()}] {ctx.content}")
            current_length += len(ctx.content)
        if not context_parts:
            return original_prompt
        context_block = "\n\n".join(context_parts)
        augmented = f"""## Relevant Context
{context_block}

## Original Request
{original_prompt}"""
        return augmented

    async def query(
        self,
        prompt: str,
        sources: Optional[List[RAGSource]] = None,
        k: int = 5,
    ) -> tuple[str, List[RetrievedContext]]:
        contexts = await self.retrieve_relevant_context(prompt, sources, k)
        augmented_prompt = await self.augment_prompt(prompt, contexts)
        return augmented_prompt, contexts

    def get_stats(self) -> Dict[str, Any]:
        return {
            **self._stats,
            "embedding_stats": self.embedding_service.get_stats(),
        }

    async def clear(self):
        await self.vector_store.clear()
        self.embedding_service.clear_cache()
        self._stats = {"queries": 0, "documents_indexed": 0, "retrievals": 0}
        logger.info("[RAGEngine] Cleared all data")


async def create_rag_engine(
    api_key: str,
    model: str = "openai/text-embedding-3-small",
    provider: EmbeddingProvider = EmbeddingProvider.OPENROUTER,
) -> RAGEngine:
    config = RAGConfig(
        embedding_api_key=api_key,
        embedding_model=model,
        embedding_provider=provider,
    )
    engine = RAGEngine(config)
    await engine.initialize()
    return engine
