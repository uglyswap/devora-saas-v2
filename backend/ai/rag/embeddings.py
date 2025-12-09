"""
Embedding Service for RAG

Supports:
- OpenAI embeddings (text-embedding-3-small, text-embedding-3-large)
- Sentence transformers (local)
- Caching for repeated embeddings
"""

import logging
import hashlib
from typing import List, Optional, Dict, Any
import httpx
import asyncio

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings"""

    OPENAI_MODELS = {
        "text-embedding-3-small": {"dimensions": 1536, "cost_per_1m": 0.02},
        "text-embedding-3-large": {"dimensions": 3072, "cost_per_1m": 0.13},
        "text-embedding-ada-002": {"dimensions": 1536, "cost_per_1m": 0.10},
    }

    def __init__(
        self,
        api_key: str,
        model: str = "text-embedding-3-small",
        use_openai: bool = True,
        cache_embeddings: bool = True,
    ):
        self.api_key = api_key
        self.model = model
        self.use_openai = use_openai
        self.cache_embeddings = cache_embeddings

        # Embedding cache
        self._cache: Dict[str, List[float]] = {}

        # Stats
        self._stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
        }

        # Local model (lazy load)
        self._local_model = None

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text"""
        return hashlib.md5(f"{self.model}:{text}".encode()).hexdigest()

    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text

        Args:
            text: Text to embed

        Returns:
            List of float values (embedding vector)
        """
        # Check cache
        if self.cache_embeddings:
            cache_key = self._get_cache_key(text)
            if cache_key in self._cache:
                self._stats["cache_hits"] += 1
                return self._cache[cache_key]

        # Generate embedding
        if self.use_openai:
            embedding = await self._embed_openai([text])
            result = embedding[0]
        else:
            embedding = await self._embed_local([text])
            result = embedding[0]

        # Cache result
        if self.cache_embeddings:
            self._cache[cache_key] = result

        self._stats["total_requests"] += 1

        return result

    async def embed_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """
        Generate embeddings for multiple texts

        Args:
            texts: List of texts to embed
            batch_size: Number of texts to process in one batch

        Returns:
            List of embedding vectors
        """
        all_embeddings = []

        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            if self.use_openai:
                embeddings = await self._embed_openai(batch)
            else:
                embeddings = await self._embed_local(batch)

            all_embeddings.extend(embeddings)
            self._stats["total_requests"] += len(batch)

        return all_embeddings

    async def _embed_openai(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI API"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/embeddings",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "input": texts,
                        "model": self.model,
                    },
                )

                if response.status_code == 200:
                    result = response.json()

                    # Extract embeddings
                    embeddings = [item["embedding"] for item in result["data"]]

                    # Update stats
                    usage = result.get("usage", {})
                    tokens = usage.get("total_tokens", len(" ".join(texts).split()))
                    self._stats["total_tokens"] += tokens

                    # Calculate cost
                    model_info = self.OPENAI_MODELS.get(self.model, {"cost_per_1m": 0.02})
                    cost = (tokens / 1_000_000) * model_info["cost_per_1m"]
                    self._stats["total_cost"] += cost

                    logger.debug(
                        f"[Embeddings] Generated {len(embeddings)} embeddings, "
                        f"{tokens} tokens, ${cost:.4f}"
                    )

                    return embeddings

                else:
                    raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")

        except Exception as e:
            logger.error(f"[Embeddings] OpenAI embedding failed: {e}")
            raise

    async def _embed_local(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using local sentence transformer model"""
        try:
            # Lazy load model
            if self._local_model is None:
                from sentence_transformers import SentenceTransformer
                self._local_model = SentenceTransformer("all-MiniLM-L6-v2")
                logger.info("[Embeddings] Loaded local model: all-MiniLM-L6-v2")

            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None,
                lambda: self._local_model.encode(texts, convert_to_numpy=True).tolist()
            )

            logger.debug(f"[Embeddings] Generated {len(embeddings)} local embeddings")

            return embeddings

        except ImportError:
            logger.error("[Embeddings] sentence-transformers not installed. Install with: pip install sentence-transformers")
            raise
        except Exception as e:
            logger.error(f"[Embeddings] Local embedding failed: {e}")
            raise

    def get_stats(self) -> Dict[str, Any]:
        """Get embedding statistics"""
        hit_rate = (
            self._stats["cache_hits"] / self._stats["total_requests"]
            if self._stats["total_requests"] > 0
            else 0.0
        )

        return {
            **self._stats,
            "cache_size": len(self._cache),
            "cache_hit_rate": hit_rate,
        }

    def clear_cache(self):
        """Clear embedding cache"""
        self._cache.clear()
        logger.info("[Embeddings] Cache cleared")


# Utility function for quick embedding
async def quick_embed(text: str, api_key: str, model: str = "text-embedding-3-small") -> List[float]:
    """
    Quick embedding without managing service lifecycle

    Args:
        text: Text to embed
        api_key: OpenAI API key
        model: Embedding model to use

    Returns:
        Embedding vector
    """
    service = EmbeddingService(api_key=api_key, model=model)
    return await service.embed_text(text)
