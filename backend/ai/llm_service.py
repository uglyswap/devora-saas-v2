"""
Advanced LLM Service with Multi-Provider Support

Features:
- Multiple LLM providers (OpenRouter, Anthropic, OpenAI)
- Exponential backoff retry logic
- Token counting and cost tracking
- Streaming support
- Request/response logging
- Automatic failover between providers
"""

import asyncio
import logging
import time
from enum import Enum
from typing import Dict, Any, List, Optional, AsyncGenerator, Callable
from dataclasses import dataclass, field
import httpx
import tiktoken
from datetime import datetime

logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    OPENROUTER = "openrouter"
    ANTHROPIC = "anthropic"
    OPENAI = "openai"


@dataclass
class LLMConfig:
    """Configuration for LLM service"""
    provider: LLMProvider = LLMProvider.OPENROUTER
    api_key: str = ""
    model: str = "openai/gpt-4o"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    timeout: float = 120.0
    max_retries: int = 3
    retry_delay: float = 1.0
    retry_multiplier: float = 2.0
    fallback_models: List[str] = field(default_factory=list)
    enable_streaming: bool = False
    enable_cost_tracking: bool = True
    enable_logging: bool = True


@dataclass
class LLMUsageStats:
    """Token usage and cost statistics"""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost: float = 0.0
    latency_ms: float = 0.0
    model: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)


class LLMService:
    """Advanced LLM service with retry logic, cost tracking, and multi-provider support"""

    # Cost per 1M tokens (approximate, update as needed)
    MODEL_COSTS = {
        "openai/gpt-4o": {"input": 5.0, "output": 15.0},
        "openai/gpt-4o-mini": {"input": 0.15, "output": 0.6},
        "openai/gpt-4-turbo": {"input": 10.0, "output": 30.0},
        "anthropic/claude-3.5-sonnet": {"input": 3.0, "output": 15.0},
        "anthropic/claude-3-opus": {"input": 15.0, "output": 75.0},
        "anthropic/claude-3-haiku": {"input": 0.25, "output": 1.25},
        "google/gemini-pro-1.5": {"input": 1.25, "output": 5.0},
    }

    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = httpx.AsyncClient(timeout=config.timeout)
        self.total_stats = {
            "requests": 0,
            "errors": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "total_latency_ms": 0.0,
        }
        self._tokenizer = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    def _get_tokenizer(self):
        """Get or create tokenizer for token counting"""
        if self._tokenizer is None:
            try:
                # Use cl100k_base for GPT-4 and Claude
                self._tokenizer = tiktoken.get_encoding("cl100k_base")
            except Exception as e:
                logger.warning(f"Failed to load tokenizer: {e}")
                self._tokenizer = None
        return self._tokenizer

    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        tokenizer = self._get_tokenizer()
        if tokenizer is None:
            # Rough approximation: 1 token ≈ 4 characters
            return len(text) // 4
        try:
            return len(tokenizer.encode(text))
        except Exception as e:
            logger.warning(f"Token counting failed: {e}")
            return len(text) // 4

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int, model: str) -> float:
        """Estimate cost based on token usage"""
        costs = self.MODEL_COSTS.get(model, {"input": 5.0, "output": 15.0})
        input_cost = (prompt_tokens / 1_000_000) * costs["input"]
        output_cost = (completion_tokens / 1_000_000) * costs["output"]
        return input_cost + output_cost

    def _get_provider_endpoint(self) -> str:
        """Get API endpoint for current provider"""
        if self.config.provider == LLMProvider.OPENROUTER:
            return "https://openrouter.ai/api/v1/chat/completions"
        elif self.config.provider == LLMProvider.ANTHROPIC:
            return "https://api.anthropic.com/v1/messages"
        elif self.config.provider == LLMProvider.OPENAI:
            return "https://api.openai.com/v1/chat/completions"
        else:
            raise ValueError(f"Unsupported provider: {self.config.provider}")

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for current provider"""
        if self.config.provider == LLMProvider.OPENROUTER:
            return {
                "Authorization": f"Bearer {self.config.api_key}",
                "HTTP-Referer": "https://devora.ai",
                "X-Title": "Devora",
                "Content-Type": "application/json",
            }
        elif self.config.provider == LLMProvider.ANTHROPIC:
            return {
                "x-api-key": self.config.api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            }
        elif self.config.provider == LLMProvider.OPENAI:
            return {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            }
        else:
            raise ValueError(f"Unsupported provider: {self.config.provider}")

    def _prepare_request_body(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Prepare request body for current provider"""
        # OpenRouter and OpenAI use the same format
        if self.config.provider in [LLMProvider.OPENROUTER, LLMProvider.OPENAI]:
            full_messages = []
            if system_prompt:
                full_messages.append({"role": "system", "content": system_prompt})
            full_messages.extend(messages)

            body = {
                "model": self.config.model,
                "messages": full_messages,
                "temperature": kwargs.get("temperature", self.config.temperature),
                "stream": kwargs.get("stream", self.config.enable_streaming),
            }

            if self.config.max_tokens:
                body["max_tokens"] = self.config.max_tokens

            return body

        # Anthropic uses a different format
        elif self.config.provider == LLMProvider.ANTHROPIC:
            body = {
                "model": self.config.model,
                "messages": messages,
                "temperature": kwargs.get("temperature", self.config.temperature),
                "max_tokens": self.config.max_tokens or 4096,
            }

            if system_prompt:
                body["system"] = system_prompt

            return body

        raise ValueError(f"Unsupported provider: {self.config.provider}")

    async def _execute_with_retry(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> tuple[str, LLMUsageStats]:
        """Execute LLM call with exponential backoff retry"""
        last_error = None
        delay = self.config.retry_delay

        for attempt in range(self.config.max_retries):
            try:
                start_time = time.time()

                endpoint = self._get_provider_endpoint()
                headers = self._get_headers()
                body = self._prepare_request_body(messages, system_prompt, **kwargs)

                if self.config.enable_logging:
                    logger.info(f"[LLM] Calling {self.config.provider} with model {self.config.model}")

                response = await self.client.post(
                    endpoint,
                    headers=headers,
                    json=body,
                )

                latency_ms = (time.time() - start_time) * 1000

                if response.status_code == 200:
                    result = response.json()

                    # Extract response based on provider
                    if self.config.provider in [LLMProvider.OPENROUTER, LLMProvider.OPENAI]:
                        content = result["choices"][0]["message"]["content"]
                        usage = result.get("usage", {})
                        prompt_tokens = usage.get("prompt_tokens", 0)
                        completion_tokens = usage.get("completion_tokens", 0)
                    elif self.config.provider == LLMProvider.ANTHROPIC:
                        content = result["content"][0]["text"]
                        usage = result.get("usage", {})
                        prompt_tokens = usage.get("input_tokens", 0)
                        completion_tokens = usage.get("output_tokens", 0)
                    else:
                        raise ValueError(f"Unsupported provider: {self.config.provider}")

                    # Calculate stats
                    total_tokens = prompt_tokens + completion_tokens
                    estimated_cost = self.estimate_cost(
                        prompt_tokens,
                        completion_tokens,
                        self.config.model
                    )

                    stats = LLMUsageStats(
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        total_tokens=total_tokens,
                        estimated_cost=estimated_cost,
                        latency_ms=latency_ms,
                        model=self.config.model,
                    )

                    # Update global stats
                    self.total_stats["requests"] += 1
                    self.total_stats["total_tokens"] += total_tokens
                    self.total_stats["total_cost"] += estimated_cost
                    self.total_stats["total_latency_ms"] += latency_ms

                    if self.config.enable_logging:
                        logger.info(
                            f"[LLM] Success: {total_tokens} tokens, "
                            f"${estimated_cost:.4f}, {latency_ms:.0f}ms"
                        )

                    return content, stats

                else:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    logger.error(f"[LLM] API error: {error_msg}")
                    last_error = Exception(error_msg)

            except Exception as e:
                logger.error(f"[LLM] Request failed (attempt {attempt + 1}/{self.config.max_retries}): {e}")
                last_error = e

            # Wait before retry (exponential backoff)
            if attempt < self.config.max_retries - 1:
                await asyncio.sleep(delay)
                delay *= self.config.retry_multiplier

        # All retries failed
        self.total_stats["errors"] += 1
        raise Exception(f"LLM call failed after {self.config.max_retries} retries: {last_error}")

    async def complete(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> tuple[str, LLMUsageStats]:
        """
        Complete a chat conversation

        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: Optional system prompt
            **kwargs: Additional arguments (temperature, max_tokens, etc.)

        Returns:
            Tuple of (response_text, usage_stats)
        """
        return await self._execute_with_retry(messages, system_prompt, **kwargs)

    async def complete_with_fallback(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        fallback_models: Optional[List[str]] = None,
        **kwargs
    ) -> tuple[str, LLMUsageStats]:
        """
        Complete with automatic fallback to alternative models on failure

        Args:
            messages: List of message dicts
            system_prompt: Optional system prompt
            fallback_models: List of fallback models to try (uses config if not provided)
            **kwargs: Additional arguments

        Returns:
            Tuple of (response_text, usage_stats)
        """
        models_to_try = [self.config.model]
        if fallback_models:
            models_to_try.extend(fallback_models)
        elif self.config.fallback_models:
            models_to_try.extend(self.config.fallback_models)

        last_error = None

        for model in models_to_try:
            try:
                original_model = self.config.model
                self.config.model = model

                result = await self.complete(messages, system_prompt, **kwargs)

                self.config.model = original_model
                return result

            except Exception as e:
                logger.warning(f"[LLM] Model {model} failed, trying next: {e}")
                last_error = e
                self.config.model = self.config.model  # Reset

        raise Exception(f"All models failed. Last error: {last_error}")

    async def stream_complete(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        callback: Optional[Callable[[str], None]] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Stream completion tokens

        Args:
            messages: List of message dicts
            system_prompt: Optional system prompt
            callback: Optional callback for each token
            **kwargs: Additional arguments

        Yields:
            Response tokens as they arrive
        """
        endpoint = self._get_provider_endpoint()
        headers = self._get_headers()
        body = self._prepare_request_body(messages, system_prompt, stream=True, **kwargs)

        async with self.client.stream("POST", endpoint, headers=headers, json=body) as response:
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {await response.aread()}")

            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break

                    try:
                        import json
                        chunk = json.loads(data)

                        # Extract content based on provider
                        if self.config.provider in [LLMProvider.OPENROUTER, LLMProvider.OPENAI]:
                            delta = chunk["choices"][0]["delta"]
                            if "content" in delta:
                                token = delta["content"]
                                if callback:
                                    callback(token)
                                yield token
                        elif self.config.provider == LLMProvider.ANTHROPIC:
                            if chunk["type"] == "content_block_delta":
                                token = chunk["delta"]["text"]
                                if callback:
                                    callback(token)
                                yield token
                    except Exception as e:
                        logger.warning(f"[LLM] Stream parsing error: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get overall usage statistics"""
        avg_latency = (
            self.total_stats["total_latency_ms"] / self.total_stats["requests"]
            if self.total_stats["requests"] > 0
            else 0
        )

        return {
            **self.total_stats,
            "avg_latency_ms": avg_latency,
            "success_rate": (
                (self.total_stats["requests"] - self.total_stats["errors"])
                / self.total_stats["requests"]
                if self.total_stats["requests"] > 0
                else 1.0
            ),
        }

    def reset_stats(self):
        """Reset usage statistics"""
        self.total_stats = {
            "requests": 0,
            "errors": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "total_latency_ms": 0.0,
        }


# Convenience function for quick usage
async def quick_complete(
    prompt: str,
    api_key: str,
    model: str = "openai/gpt-4o",
    provider: LLMProvider = LLMProvider.OPENROUTER,
    system_prompt: Optional[str] = None,
) -> str:
    """
    Quick completion without managing service lifecycle

    Args:
        prompt: User prompt
        api_key: API key
        model: Model to use
        provider: LLM provider
        system_prompt: Optional system prompt

    Returns:
        Response text
    """
    config = LLMConfig(
        provider=provider,
        api_key=api_key,
        model=model,
    )

    async with LLMService(config) as service:
        response, _ = await service.complete(
            messages=[{"role": "user", "content": prompt}],
            system_prompt=system_prompt,
        )
        return response
