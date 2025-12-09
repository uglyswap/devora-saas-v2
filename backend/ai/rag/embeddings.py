"""
Embedding Service for RAG

Supports:
- OpenRouter embeddings (via OpenAI-compatible API)
- OpenAI embeddings (text-embedding-3-small, text-embedding-3-large)
- Sentence transformers (local)
- Caching for repeated embeddings
"""

import logging
import hashlib
from typing import List, Optional, Dict, Any
from enum import Enum
import httpx
import asyncio

logger = logging.getLogger(__name__)


class EmbeddingProvider(str, Enum):
    OPENROUTER = "openrouter"
    OPENAI = "openai"
    LOCAL = "local"


class EmbeddingService:
    OPENAI_MODELS = {
        "text-embedding-3-small": {"dimensions": 1536, "cost_per_1m": 0.02},
        "text-embedding-3-large": {"dimensions": 3072, "cost_per_1m": 0.13},
        "text-embedding-ada-002": {"dimensions": 1536, "cost_per_1m": 0.10},
    }

    OPENROUTER_MODELS = {
        "openai/text-embedding-3-small": {"dimensions": 1536, "cost_per_1m": 0.02},
        "openai/text-embedding-3-large": {"dimensions": 3072, "cost_per_1m": 0.13},
        "openai/text-embedding-ada-002": {"dimensions": 1536, "cost_per_1m": 0.10},
    }

    PROVIDER_URLS = {
        EmbeddingProvider.OPENROUTER: "https://openrouter.ai/api/v1",
        EmbeddingProvider.OPENAI: "https://api.openai.com/v1",
    }

    def __init__(
        self,
        api_key: str,
        model: str = "openai/text-embedding-3-small",
        provider: EmbeddingProvider = EmbeddingProvider.OPENROUTER,
        cache_embeddings: bool = True,
        use_openai: Optional[bool] = None,
    ):
        self.api_key = api_key
        self.model = model
        self.cache_embeddings = cache_embeddings
        if use_openai is not None:
            self.provider = EmbeddingProvider.OPENAI if use_openai else EmbeddingProvider.LOCAL
        else:
            self.provider = provider
        self.base_url = self.PROVIDER_URLS.get(self.provider, "https://openrouter.ai/api/v1")
        self._cache: Dict[str, List[float]] = {}
        self._stats = {"total_requests": 0, "cache_hits": 0, "total_tokens": 0, "total_cost": 0.0}
        self._local_model = None

    def _get_cache_key(self, text: str) -> str:
        return hashlib.md5(f"{self.model}:{text}".encode()).hexdigest()

    async def embed(self, text: str) -> List[float]:
        return await self.embed_text(text)

    async def embed_text(self, text: str) -> List[float]:
        if self.cache_embeddings:
            cache_key = self._get_cache_key(text)
            if cache_key in self._cache:
                self._stats["cache_hits"] += 1
                return self._cache[cache_key]
        if self.provider == EmbeddingProvider.LOCAL:
            embedding = await self._embed_local([text])
        else:
            embedding = await self._embed_api([text])
        result = embedding[0]
        if self.cache_embeddings:
            self._cache[cache_key] = result
        self._stats["total_requests"] += 1
        return result

    async def embed_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        if not texts:
            return []
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            if self.provider == EmbeddingProvider.LOCAL:
                embeddings = await self._embed_local(batch)
            else:
                embeddings = await self._embed_api(batch)
            all_embeddings.extend(embeddings)
            self._stats["total_requests"] += len(batch)
        return all_embeddings

    async def _embed_api(self, texts: List[str]) -> List[List[float]]:
        try:
            if self.provider == EmbeddingProvider.OPENROUTER:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "HTTP-Referer": "https://devora.ai",
                    "X-Title": "Devora",
                    "Content-Type": "application/json",
                }
            else:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/embeddings",
                    headers=headers,
                    json={"input": texts, "model": self.model},
                )
                if response.status_code == 200:
                    result = response.json()
                    embeddings = [item["embedding"] for item in result["data"]]
                    usage = result.get("usage", {})
                    tokens = usage.get("total_tokens", len(" ".join(texts).split()))
                    self._stats["total_tokens"] += tokens
                    models = self.OPENROUTER_MODELS if self.provider == EmbeddingProvider.OPENROUTER else self.OPENAI_MODELS
                    model_info = models.get(self.model, {"cost_per_1m": 0.02})
                    cost = (tokens / 1_000_000) * model_info["cost_per_1m"]
                    self._stats["total_cost"] += cost
                    logger.debug(f"[Embeddings] Generated {len(embeddings)} embeddings, {tokens} tokens, ${cost:.4f}")
                    return embeddings
                else:
                    raise Exception(f"{self.provider.value} API error: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"[Embeddings] {self.provider.value} embedding failed: {e}")
            raise

    async def _embed_local(self, texts: List[str]) -> List[List[float]]:
        try:
            if self._local_model is None:
                from sentence_transformers import SentenceTransformer
                self._local_model = SentenceTransformer("all-MiniLM-L6-v2")
                logger.info("[Embeddings] Loaded local model: all-MiniLM-L6-v2")
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None,
                lambda: self._local_model.encode(texts, convert_to_numpy=True).tolist()
            )
            logger.debug(f"[Embeddings] Generated {len(embeddings)} local embeddings")
            return embeddings
        except ImportError:
            logger.error("[Embeddings] sentence-transformers not installed")
            raise
        except Exception as e:
            logger.error(f"[Embeddings] Local embedding failed: {e}")
            raise

    def get_stats(self) -> Dict[str, Any]:
        hit_rate = self._stats["cache_hits"] / self._stats["total_requests"] if self._stats["total_requests"] > 0 else 0.0
        return {
            **self._stats,
            "provider": self.provider.value,
            "model": self.model,
            "cache_size": len(self._cache),
            "cache_hit_rate": hit_rate,
        }

    def clear_cache(self):
        self._cache.clear()
        logger.info("[Embeddings] Cache cleared")


EmbeddingsService = EmbeddingService


async def quick_embed(
    text: str,
    api_key: str,
    model: str = "openai/text-embedding-3-small",
    provider: EmbeddingProvider = EmbeddingProvider.OPENROUTER,
) -> List[float]:
    service = EmbeddingService(api_key=api_key, model=model, provider=provider)
    return await service.embed_text(text)
