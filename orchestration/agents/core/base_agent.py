"""
Base agent class for the orchestration system.

This module provides the foundational BaseAgent class that all specialized agents
inherit from. It includes LLM communication, memory management, and task execution.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import asyncio
import logging
import httpx
import os

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Base class for all agents in the orchestration system.

    Provides common functionality for LLM interaction, memory management,
    and task execution patterns.

    Attributes:
        name: Agent's unique identifier
        api_key: OpenRouter API key for LLM access
        model: LLM model identifier (default: gpt-4o)
        memory: Conversation history for context retention
        system_prompt: Agent's specialized system instructions
    """

    def __init__(
        self,
        name: str,
        api_key: str,
        model: str = "openai/gpt-4o",
        system_prompt: Optional[str] = None
    ):
        """
        Initialize a new agent.

        Args:
            name: Unique identifier for this agent
            api_key: OpenRouter API key
            model: LLM model to use (default: gpt-4o)
            system_prompt: Optional custom system prompt
        """
        self.name = name
        self.api_key = api_key
        self.model = model
        self.memory: List[Dict[str, Any]] = []
        self._system_prompt = system_prompt or self._get_default_system_prompt()

    @property
    def system_prompt(self) -> str:
        """Get the agent's system prompt."""
        return self._system_prompt

    @abstractmethod
    def _get_default_system_prompt(self) -> str:
        """
        Get the default system prompt for this agent.

        Must be implemented by subclasses to define their specialized behavior.

        Returns:
            System prompt string defining agent's role and capabilities
        """
        pass

    def add_to_memory(self, role: str, content: str) -> None:
        """
        Add a message to agent's conversation memory.

        Args:
            role: Message role (system, user, assistant)
            content: Message content
        """
        self.memory.append({
            "role": role,
            "content": content
        })

    def get_memory(self) -> List[Dict[str, Any]]:
        """
        Get agent's conversation memory.

        Returns:
            List of message dictionaries with role and content
        """
        return self.memory

    def clear_memory(self) -> None:
        """Clear agent's conversation memory."""
        self.memory = []

    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's main task.

        This is the primary method that defines what the agent does.
        Must be implemented by subclasses.

        Args:
            context: Task context with input data and parameters

        Returns:
            Result dictionary with output data and status
        """
        pass

    async def call_llm(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Call the LLM API with the given messages.

        Args:
            messages: List of message dictionaries
            system_prompt: Optional override for system prompt
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            LLM response content

        Raises:
            Exception: If API call fails
        """
        full_messages = []

        # Add system prompt
        prompt = system_prompt or self._system_prompt
        if prompt:
            full_messages.append({"role": "system", "content": prompt})

        full_messages.extend(messages)

        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "model": self.model,
                    "messages": full_messages,
                    "temperature": temperature
                }

                if max_tokens:
                    payload["max_tokens"] = max_tokens

                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "HTTP-Referer": os.environ.get('FRONTEND_URL', 'http://localhost:3000'),
                        "X-Title": "Devora",
                        "Content-Type": "application/json"
                    },
                    json=payload,
                    timeout=120.0
                )

                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]

                    # Add to memory
                    self.add_to_memory("assistant", content)

                    return content
                else:
                    error_msg = f"LLM API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    raise Exception(error_msg)

        except Exception as e:
            logger.error(f"LLM call failed for {self.name}: {str(e)}")
            raise

    def format_context(self, context: Dict[str, Any]) -> str:
        """
        Format context dictionary into a readable string for LLM.

        Args:
            context: Context dictionary

        Returns:
            Formatted string representation
        """
        lines = []
        for key, value in context.items():
            if isinstance(value, (dict, list)):
                lines.append(f"{key}:")
                lines.append(f"```json\n{value}\n```")
            else:
                lines.append(f"{key}: {value}")
        return "\n".join(lines)

    async def validate_output(self, output: Dict[str, Any]) -> bool:
        """
        Validate agent output format.

        Can be overridden by subclasses for custom validation.

        Args:
            output: Output dictionary to validate

        Returns:
            True if output is valid, False otherwise
        """
        return "status" in output and "result" in output
