"""
Client LLM unifié pour l'orchestration Devora.

Gère les appels à l'API OpenRouter avec:
- Rate limiting
- Retry avec exponential backoff
- Streaming support
- Token counting
"""

import asyncio
import json
import os
from dataclasses import dataclass
from typing import AsyncIterator, Dict, List, Optional, Any
from enum import Enum

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)


class ModelType(Enum):
    """Types de modèles supportés."""
    SONNET = "anthropic/claude-3.5-sonnet"
    HAIKU = "anthropic/claude-3.5-haiku"
    OPUS = "anthropic/claude-opus-4"
    GPT4 = "openai/gpt-4-turbo"
    DEEPSEEK = "deepseek/deepseek-chat"


@dataclass
class LLMResponse:
    """Réponse standardisée du LLM."""
    content: str
    model: str
    tokens_used: int
    finish_reason: str
    raw_response: Optional[Dict[str, Any]] = None


@dataclass
class LLMConfig:
    """Configuration du client LLM."""
    api_key: str
    base_url: str = "https://openrouter.ai/api/v1"
    timeout: int = 300
    max_retries: int = 3
    rate_limit_delay: float = 1.0


class RateLimitError(Exception):
    """Exception levée quand on dépasse le rate limit."""
    pass


class LLMClient:
    """Client unifié pour les appels LLM via OpenRouter."""

    def __init__(self, config: Optional[LLMConfig] = None):
        """
        Initialise le client LLM.

        Args:
            config: Configuration du client. Si None, utilise les variables d'environnement.
        """
        if config is None:
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                raise ValueError("OPENROUTER_API_KEY manquante dans l'environnement")
            config = LLMConfig(api_key=api_key)

        self.config = config
        self.client = httpx.AsyncClient(
            base_url=config.base_url,
            timeout=config.timeout,
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "HTTP-Referer": "https://devora.ai",
                "X-Title": "Devora Orchestration",
            },
        )
        self._last_request_time = 0.0

    async def _enforce_rate_limit(self):
        """Applique le rate limiting entre les requêtes."""
        now = asyncio.get_event_loop().time()
        elapsed = now - self._last_request_time
        if elapsed < self.config.rate_limit_delay:
            await asyncio.sleep(self.config.rate_limit_delay - elapsed)
        self._last_request_time = asyncio.get_event_loop().time()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, RateLimitError)),
    )
    async def complete(
        self,
        messages: List[Dict[str, str]],
        model: ModelType = ModelType.SONNET,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs,
    ) -> LLMResponse:
        """
        Effectue une complétion LLM.

        Args:
            messages: Liste de messages au format OpenAI
            model: Type de modèle à utiliser
            temperature: Température de génération (0-1)
            max_tokens: Nombre maximum de tokens à générer
            **kwargs: Paramètres additionnels pour l'API

        Returns:
            LLMResponse contenant la réponse du modèle

        Raises:
            RateLimitError: Si le rate limit est dépassé
            httpx.HTTPError: En cas d'erreur HTTP
        """
        await self._enforce_rate_limit()

        payload = {
            "model": model.value,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs,
        }

        try:
            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise RateLimitError("Rate limit dépassé") from e
            raise

        data = response.json()

        choice = data["choices"][0]
        usage = data.get("usage", {})

        return LLMResponse(
            content=choice["message"]["content"],
            model=data["model"],
            tokens_used=usage.get("total_tokens", 0),
            finish_reason=choice.get("finish_reason", "unknown"),
            raw_response=data,
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, RateLimitError)),
    )
    async def stream(
        self,
        messages: List[Dict[str, str]],
        model: ModelType = ModelType.SONNET,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs,
    ) -> AsyncIterator[str]:
        """
        Effectue une complétion en streaming.

        Args:
            messages: Liste de messages au format OpenAI
            model: Type de modèle à utiliser
            temperature: Température de génération
            max_tokens: Nombre maximum de tokens
            **kwargs: Paramètres additionnels

        Yields:
            Chunks de texte au fur et à mesure de la génération

        Raises:
            RateLimitError: Si le rate limit est dépassé
        """
        await self._enforce_rate_limit()

        payload = {
            "model": model.value,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
            **kwargs,
        }

        try:
            async with self.client.stream(
                "POST", "/chat/completions", json=payload
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if not line.strip() or line.startswith(":"):
                        continue

                    if line.startswith("data: "):
                        data_str = line[6:]

                        if data_str == "[DONE]":
                            break

                        try:
                            data = json.loads(data_str)
                            delta = data["choices"][0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
                        except (json.JSONDecodeError, KeyError):
                            continue

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise RateLimitError("Rate limit dépassé") from e
            raise

    def count_tokens(self, text: str, model: ModelType = ModelType.SONNET) -> int:
        """
        Estime le nombre de tokens dans un texte.

        Note: Utilise une approximation simple. Pour un comptage précis,
        utiliser tiktoken ou l'API du modèle.

        Args:
            text: Texte à analyser
            model: Modèle de référence

        Returns:
            Nombre estimé de tokens
        """
        # Approximation simple: ~4 caractères par token pour les modèles Claude/GPT
        return len(text) // 4

    async def close(self):
        """Ferme le client HTTP."""
        await self.client.aclose()

    async def __aenter__(self):
        """Support du context manager async."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Ferme le client à la sortie du context."""
        await self.close()


# Factory function pour faciliter l'utilisation
async def create_llm_client(api_key: Optional[str] = None) -> LLMClient:
    """
    Crée une instance de LLMClient.

    Args:
        api_key: Clé API OpenRouter. Si None, utilise la variable d'environnement.

    Returns:
        Instance configurée de LLMClient
    """
    if api_key:
        config = LLMConfig(api_key=api_key)
        return LLMClient(config)
    return LLMClient()
