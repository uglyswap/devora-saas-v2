"""
Token Counter Utility

Provides precise token counting using tiktoken for various LLM models.
Useful for:
- Estimating API costs
- Preventing context window overflow
- Truncating content to fit limits
"""

from typing import List, Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# Try to import tiktoken, provide fallback if not available
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    logger.warning("tiktoken not installed. Using character-based estimation.")


class TokenCounter:
    """Token counting utility using tiktoken.

    Supports multiple encoding schemes for different models:
    - cl100k_base: GPT-4, GPT-3.5-turbo, Claude 3.x
    - p50k_base: Codex, GPT-3
    - o200k_base: GPT-4o

    Falls back to character estimation if tiktoken is unavailable.
    """

    # Model to encoding mapping
    MODEL_ENCODINGS = {
        # OpenAI models
        "gpt-4": "cl100k_base",
        "gpt-4-turbo": "cl100k_base",
        "gpt-4o": "o200k_base",
        "gpt-4o-mini": "o200k_base",
        "gpt-3.5-turbo": "cl100k_base",

        # OpenRouter prefixed models
        "openai/gpt-4": "cl100k_base",
        "openai/gpt-4-turbo": "cl100k_base",
        "openai/gpt-4o": "o200k_base",
        "openai/gpt-4o-mini": "o200k_base",
        "openai/gpt-3.5-turbo": "cl100k_base",

        # Anthropic models (use cl100k as approximation)
        "claude-3-opus": "cl100k_base",
        "claude-3-sonnet": "cl100k_base",
        "claude-3-haiku": "cl100k_base",
        "claude-3.5-sonnet": "cl100k_base",
        "anthropic/claude-3-opus": "cl100k_base",
        "anthropic/claude-3-sonnet": "cl100k_base",
        "anthropic/claude-3-haiku": "cl100k_base",
        "anthropic/claude-3.5-sonnet": "cl100k_base",

        # Google models (use cl100k as approximation)
        "google/gemini-pro": "cl100k_base",
        "google/gemini-pro-1.5": "cl100k_base",
    }

    # Model context window limits
    MODEL_LIMITS = {
        "gpt-4": 8192,
        "gpt-4-32k": 32768,
        "gpt-4-turbo": 128000,
        "gpt-4o": 128000,
        "gpt-4o-mini": 128000,
        "gpt-3.5-turbo": 16385,
        "claude-3-opus": 200000,
        "claude-3-sonnet": 200000,
        "claude-3-haiku": 200000,
        "claude-3.5-sonnet": 200000,
        "gemini-pro": 32000,
        "gemini-pro-1.5": 1000000,
    }

    # Characters per token approximation
    CHARS_PER_TOKEN = 4

    def __init__(self, model: str = "gpt-4o"):
        """Initialize token counter for a specific model.

        Args:
            model: The model name to use for token counting
        """
        self.model = model
        self._encoding = None
        self._encoding_name = self._get_encoding_name(model)

    def _get_encoding_name(self, model: str) -> str:
        """Get the encoding name for a model."""
        # Try direct lookup
        if model in self.MODEL_ENCODINGS:
            return self.MODEL_ENCODINGS[model]

        # Try with prefix removed
        for prefix in ["openai/", "anthropic/", "google/"]:
            if model.startswith(prefix):
                base_model = model[len(prefix):]
                if base_model in self.MODEL_ENCODINGS:
                    return self.MODEL_ENCODINGS[base_model]

        # Default to cl100k_base
        return "cl100k_base"

    def _get_encoding(self):
        """Lazy load the tokenizer encoding."""
        if self._encoding is None and TIKTOKEN_AVAILABLE:
            try:
                self._encoding = tiktoken.get_encoding(self._encoding_name)
            except Exception as e:
                logger.warning(f"Failed to load encoding {self._encoding_name}: {e}")
                try:
                    self._encoding = tiktoken.get_encoding("cl100k_base")
                except Exception as e2:
                    logger.error(f"Failed to load fallback encoding: {e2}")
        return self._encoding

    def count(self, text: str) -> int:
        """Count tokens in a text string.

        Args:
            text: The text to count tokens for

        Returns:
            Number of tokens in the text
        """
        if not text:
            return 0

        encoding = self._get_encoding()

        if encoding:
            try:
                return len(encoding.encode(text))
            except Exception as e:
                logger.warning(f"Token counting failed, using estimation: {e}")

        # Fallback to character estimation
        return len(text) // self.CHARS_PER_TOKEN

    def count_messages(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None
    ) -> int:
        """Count tokens in a list of chat messages.

        Accounts for message formatting overhead used by chat models.

        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: Optional system prompt to include

        Returns:
            Total token count including formatting overhead
        """
        total = 0

        # Add system prompt if provided
        if system_prompt:
            total += self.count(system_prompt)
            total += 4  # Overhead for system message formatting

        # Count each message
        for message in messages:
            # Content tokens
            content = message.get("content", "")
            total += self.count(content)

            # Role tokens (typically 1 token)
            total += 1

            # Message formatting overhead (varies by model, estimate 4)
            total += 4

        # Reply priming overhead
        total += 3

        return total

    def count_file(self, file_content: str, file_name: str = "") -> Dict[str, Any]:
        """Count tokens in a file with detailed breakdown.

        Args:
            file_content: The file content
            file_name: Optional file name for context

        Returns:
            Dict with token count and metadata
        """
        token_count = self.count(file_content)
        char_count = len(file_content)
        line_count = file_content.count('\n') + 1

        return {
            "file": file_name,
            "tokens": token_count,
            "characters": char_count,
            "lines": line_count,
            "tokens_per_line": token_count / line_count if line_count > 0 else 0
        }

    def truncate_to_limit(
        self,
        text: str,
        max_tokens: int,
        truncation_marker: str = "\n... (truncated)"
    ) -> Tuple[str, bool]:
        """Truncate text to fit within a token limit.

        Args:
            text: The text to truncate
            max_tokens: Maximum allowed tokens
            truncation_marker: Text to append when truncating

        Returns:
            Tuple of (truncated_text, was_truncated)
        """
        if not text:
            return text, False

        current_tokens = self.count(text)

        if current_tokens <= max_tokens:
            return text, False

        # Account for truncation marker
        marker_tokens = self.count(truncation_marker)
        target_tokens = max_tokens - marker_tokens

        if target_tokens <= 0:
            return truncation_marker, True

        encoding = self._get_encoding()

        if encoding:
            try:
                # Use tiktoken for precise truncation
                tokens = encoding.encode(text)
                truncated_tokens = tokens[:target_tokens]
                truncated_text = encoding.decode(truncated_tokens)
                return truncated_text + truncation_marker, True
            except Exception as e:
                logger.warning(f"Tiktoken truncation failed: {e}")

        # Fallback: character-based truncation
        target_chars = target_tokens * self.CHARS_PER_TOKEN
        truncated_text = text[:target_chars]

        # Try to break at a newline for cleaner output
        last_newline = truncated_text.rfind('\n')
        if last_newline > target_chars * 0.8:  # If newline is in last 20%
            truncated_text = truncated_text[:last_newline]

        return truncated_text + truncation_marker, True

    def truncate_messages_to_limit(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int,
        system_prompt: Optional[str] = None,
        keep_last: int = 2
    ) -> Tuple[List[Dict[str, str]], int]:
        """Truncate message history to fit within token limit.

        Removes oldest messages first while keeping the most recent ones.

        Args:
            messages: List of message dicts
            max_tokens: Maximum allowed tokens
            system_prompt: Optional system prompt (counts towards limit)
            keep_last: Minimum number of recent messages to keep

        Returns:
            Tuple of (truncated_messages, removed_count)
        """
        if not messages:
            return messages, 0

        current_tokens = self.count_messages(messages, system_prompt)

        if current_tokens <= max_tokens:
            return messages, 0

        # Start removing from the oldest (index 0)
        truncated = list(messages)
        removed_count = 0

        while (
            len(truncated) > keep_last and
            self.count_messages(truncated, system_prompt) > max_tokens
        ):
            truncated.pop(0)
            removed_count += 1

        return truncated, removed_count

    def get_model_limit(self, model: Optional[str] = None) -> int:
        """Get the context window limit for a model.

        Args:
            model: Model name (uses instance model if not provided)

        Returns:
            Context window size in tokens
        """
        model = model or self.model

        # Try direct lookup
        if model in self.MODEL_LIMITS:
            return self.MODEL_LIMITS[model]

        # Try with prefix removed
        for prefix in ["openai/", "anthropic/", "google/"]:
            if model.startswith(prefix):
                base_model = model[len(prefix):]
                if base_model in self.MODEL_LIMITS:
                    return self.MODEL_LIMITS[base_model]

        # Default limit
        logger.warning(f"Unknown model limit for {model}, using default 8192")
        return 8192

    def estimate_cost(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        model: Optional[str] = None
    ) -> float:
        """Estimate cost based on token usage.

        Args:
            prompt_tokens: Number of input tokens
            completion_tokens: Number of output tokens
            model: Model name (uses instance model if not provided)

        Returns:
            Estimated cost in USD
        """
        model = model or self.model

        # Cost per 1M tokens
        costs = {
            "gpt-4": {"input": 30.0, "output": 60.0},
            "gpt-4-turbo": {"input": 10.0, "output": 30.0},
            "gpt-4o": {"input": 5.0, "output": 15.0},
            "gpt-4o-mini": {"input": 0.15, "output": 0.6},
            "gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
            "claude-3-opus": {"input": 15.0, "output": 75.0},
            "claude-3-sonnet": {"input": 3.0, "output": 15.0},
            "claude-3-haiku": {"input": 0.25, "output": 1.25},
            "claude-3.5-sonnet": {"input": 3.0, "output": 15.0},
        }

        # Normalize model name
        for prefix in ["openai/", "anthropic/", "google/"]:
            if model.startswith(prefix):
                model = model[len(prefix):]
                break

        if model not in costs:
            # Default to GPT-4o pricing
            model = "gpt-4o"

        pricing = costs[model]
        input_cost = (prompt_tokens / 1_000_000) * pricing["input"]
        output_cost = (completion_tokens / 1_000_000) * pricing["output"]

        return input_cost + output_cost


# Convenience functions for quick usage

def count_tokens(text: str, model: str = "gpt-4o") -> int:
    """Quick function to count tokens in text.

    Args:
        text: The text to count
        model: Model to use for tokenization

    Returns:
        Token count
    """
    counter = TokenCounter(model)
    return counter.count(text)


def count_message_tokens(
    messages: List[Dict[str, str]],
    system_prompt: Optional[str] = None,
    model: str = "gpt-4o"
) -> int:
    """Quick function to count tokens in messages.

    Args:
        messages: List of message dicts
        system_prompt: Optional system prompt
        model: Model to use for tokenization

    Returns:
        Token count
    """
    counter = TokenCounter(model)
    return counter.count_messages(messages, system_prompt)


def truncate_to_token_limit(
    text: str,
    max_tokens: int,
    model: str = "gpt-4o"
) -> str:
    """Quick function to truncate text to token limit.

    Args:
        text: The text to truncate
        max_tokens: Maximum tokens allowed
        model: Model to use for tokenization

    Returns:
        Truncated text
    """
    counter = TokenCounter(model)
    truncated, _ = counter.truncate_to_limit(text, max_tokens)
    return truncated
