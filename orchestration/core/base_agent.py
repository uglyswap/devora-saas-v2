"""
Base Agent Module for Devora Orchestration System

This module provides the abstract base class for all agents in the Devora
transformation orchestration system. It handles LLM connections via OpenRouter API,
logging, token management, and callback mechanisms.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
import json
import requests
from datetime import datetime


class AgentStatus(Enum):
    """Status enumeration for agent execution states."""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class AgentConfig:
    """Configuration for agent initialization and behavior.

    Attributes:
        name: Unique identifier for the agent
        model: LLM model to use (e.g., 'anthropic/claude-3.5-sonnet')
        temperature: Sampling temperature (0.0 to 1.0)
        max_tokens: Maximum tokens for response
        api_key: OpenRouter API key
        timeout: Request timeout in seconds
        max_retries: Maximum retry attempts for failed requests
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    name: str
    model: str = "anthropic/claude-3.5-sonnet"
    temperature: float = 0.7
    max_tokens: int = 4096
    api_key: Optional[str] = None
    timeout: int = 60
    max_retries: int = 3
    log_level: str = "INFO"


@dataclass
class AgentMetrics:
    """Metrics tracking for agent execution.

    Attributes:
        total_tokens: Total tokens used (prompt + completion)
        prompt_tokens: Tokens in the prompt
        completion_tokens: Tokens in the completion
        execution_time: Time taken for execution in seconds
        retry_count: Number of retries performed
        error_count: Number of errors encountered
    """
    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    execution_time: float = 0.0
    retry_count: int = 0
    error_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "total_tokens": self.total_tokens,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "execution_time": self.execution_time,
            "retry_count": self.retry_count,
            "error_count": self.error_count
        }


class BaseAgent(ABC):
    """Abstract base class for all Devora orchestration agents.

    This class provides the foundation for creating specialized agents with
    LLM integration, logging, metrics tracking, and error handling capabilities.

    Attributes:
        config: Agent configuration
        status: Current execution status
        metrics: Execution metrics
        logger: Configured logger instance
        callbacks: List of progress callback functions
    """

    def __init__(
        self,
        config: AgentConfig,
        callbacks: Optional[List[Callable]] = None
    ):
        """Initialize the base agent.

        Args:
            config: Agent configuration object
            callbacks: Optional list of callback functions for progress updates
        """
        self.config = config
        self.status = AgentStatus.IDLE
        self.metrics = AgentMetrics()
        self.callbacks = callbacks or []

        # Setup logging
        self.logger = self._setup_logger()

        # Validate configuration
        self._validate_config()

        self.logger.info(f"Agent '{self.config.name}' initialized with model '{self.config.model}'")

    def _setup_logger(self) -> logging.Logger:
        """Setup and configure logger for the agent.

        Returns:
            Configured logger instance
        """
        logger = logging.getLogger(f"devora.agent.{self.config.name}")
        logger.setLevel(getattr(logging, self.config.log_level.upper()))

        # Create console handler if not already exists
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _validate_config(self) -> None:
        """Validate agent configuration.

        Raises:
            ValueError: If configuration is invalid
        """
        if not self.config.name:
            raise ValueError("Agent name cannot be empty")

        if not self.config.api_key:
            raise ValueError("OpenRouter API key is required")

        if not 0.0 <= self.config.temperature <= 1.0:
            raise ValueError("Temperature must be between 0.0 and 1.0")

        if self.config.max_tokens <= 0:
            raise ValueError("max_tokens must be positive")

        if self.config.timeout <= 0:
            raise ValueError("timeout must be positive")

    def _notify_callbacks(self, event: str, data: Dict[str, Any]) -> None:
        """Notify all registered callbacks of an event.

        Args:
            event: Event type/name
            data: Event data to pass to callbacks
        """
        for callback in self.callbacks:
            try:
                callback(event, data)
            except Exception as e:
                self.logger.error(f"Callback error: {str(e)}")

    def _call_llm(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Call the LLM via OpenRouter API.

        Args:
            prompt: User prompt to send to the LLM
            system_message: Optional system message
            **kwargs: Additional parameters to override config

        Returns:
            Dictionary containing response and metadata

        Raises:
            requests.RequestException: If API call fails after retries
        """
        url = "https://openrouter.ai/api/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "HTTP-Referer": "https://github.com/devora-transformation",
            "Content-Type": "application/json"
        }

        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": kwargs.get("model", self.config.model),
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens)
        }

        # Retry logic
        for attempt in range(self.config.max_retries):
            try:
                start_time = datetime.now()

                response = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=self.config.timeout
                )
                response.raise_for_status()

                execution_time = (datetime.now() - start_time).total_seconds()
                result = response.json()

                # Update metrics
                usage = result.get("usage", {})
                self.metrics.prompt_tokens += usage.get("prompt_tokens", 0)
                self.metrics.completion_tokens += usage.get("completion_tokens", 0)
                self.metrics.total_tokens += usage.get("total_tokens", 0)
                self.metrics.execution_time += execution_time

                self.logger.debug(
                    f"LLM call successful. Tokens: {usage.get('total_tokens', 0)}, "
                    f"Time: {execution_time:.2f}s"
                )

                return {
                    "content": result["choices"][0]["message"]["content"],
                    "usage": usage,
                    "model": result.get("model"),
                    "execution_time": execution_time
                }

            except requests.RequestException as e:
                self.metrics.retry_count += 1
                self.logger.warning(
                    f"LLM call attempt {attempt + 1}/{self.config.max_retries} failed: {str(e)}"
                )

                if attempt == self.config.max_retries - 1:
                    self.metrics.error_count += 1
                    raise

        raise requests.RequestException("Max retries exceeded")

    @abstractmethod
    def validate_input(self, input_data: Any) -> bool:
        """Validate input data before processing.

        Args:
            input_data: Input data to validate

        Returns:
            True if input is valid, False otherwise

        Raises:
            ValueError: If input validation fails with specific error
        """
        pass

    @abstractmethod
    def execute(self, input_data: Any, **kwargs) -> Any:
        """Execute the agent's main task.

        Args:
            input_data: Input data to process
            **kwargs: Additional execution parameters

        Returns:
            Processed output data

        Raises:
            Exception: If execution fails
        """
        pass

    @abstractmethod
    def format_output(self, raw_output: Any) -> Dict[str, Any]:
        """Format raw output into standardized structure.

        Args:
            raw_output: Raw output from execution

        Returns:
            Formatted output dictionary
        """
        pass

    def run(self, input_data: Any, **kwargs) -> Dict[str, Any]:
        """Main entry point to run the agent.

        This method orchestrates the full agent lifecycle:
        validation, execution, formatting, and metrics collection.

        Args:
            input_data: Input data to process
            **kwargs: Additional execution parameters

        Returns:
            Dictionary containing formatted output and metadata
        """
        try:
            self.status = AgentStatus.RUNNING
            self._notify_callbacks("agent_started", {"agent": self.config.name})

            self.logger.info(f"Starting execution for agent '{self.config.name}'")

            # Validate input
            self.logger.debug("Validating input data")
            if not self.validate_input(input_data):
                raise ValueError("Input validation failed")

            self._notify_callbacks("validation_complete", {"status": "success"})

            # Execute
            self.logger.debug("Executing agent logic")
            start_time = datetime.now()

            raw_output = self.execute(input_data, **kwargs)

            execution_time = (datetime.now() - start_time).total_seconds()
            self.metrics.execution_time += execution_time

            self._notify_callbacks("execution_complete", {"time": execution_time})

            # Format output
            self.logger.debug("Formatting output")
            formatted_output = self.format_output(raw_output)

            self.status = AgentStatus.COMPLETED
            self._notify_callbacks("agent_completed", {
                "agent": self.config.name,
                "metrics": self.metrics.to_dict()
            })

            self.logger.info(
                f"Agent '{self.config.name}' completed successfully. "
                f"Total tokens: {self.metrics.total_tokens}, "
                f"Time: {self.metrics.execution_time:.2f}s"
            )

            return {
                "status": "success",
                "output": formatted_output,
                "metrics": self.metrics.to_dict(),
                "agent": self.config.name,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.status = AgentStatus.FAILED
            self.metrics.error_count += 1

            self.logger.error(f"Agent execution failed: {str(e)}", exc_info=True)
            self._notify_callbacks("agent_failed", {
                "agent": self.config.name,
                "error": str(e)
            })

            return {
                "status": "failed",
                "error": str(e),
                "metrics": self.metrics.to_dict(),
                "agent": self.config.name,
                "timestamp": datetime.now().isoformat()
            }

    def reset_metrics(self) -> None:
        """Reset agent metrics to initial state."""
        self.metrics = AgentMetrics()
        self.logger.debug("Metrics reset")

    def get_metrics(self) -> Dict[str, Any]:
        """Get current agent metrics.

        Returns:
            Dictionary containing current metrics
        """
        return self.metrics.to_dict()

    def add_callback(self, callback: Callable) -> None:
        """Add a progress callback function.

        Args:
            callback: Callable that accepts (event: str, data: dict)
        """
        self.callbacks.append(callback)
        self.logger.debug(f"Callback added. Total callbacks: {len(self.callbacks)}")

    def remove_callback(self, callback: Callable) -> None:
        """Remove a progress callback function.

        Args:
            callback: Callback to remove
        """
        if callback in self.callbacks:
            self.callbacks.remove(callback)
            self.logger.debug(f"Callback removed. Total callbacks: {len(self.callbacks)}")
