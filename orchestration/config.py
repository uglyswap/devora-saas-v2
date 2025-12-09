"""
Devora Orchestration - Configuration
=====================================

Central configuration for the orchestration system.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class ModelProvider(str, Enum):
    """Supported LLM providers via OpenRouter."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    META = "meta"
    MISTRAL = "mistral"


@dataclass
class ModelConfig:
    """Configuration for a specific LLM model."""
    id: str
    provider: ModelProvider
    max_tokens: int
    cost_per_1k_input: float
    cost_per_1k_output: float
    supports_vision: bool = False
    supports_functions: bool = True


# Available models with their configurations
MODELS: Dict[str, ModelConfig] = {
    # Anthropic Claude
    "claude-opus-4.5": ModelConfig(
        id="anthropic/claude-opus-4-5-20251101",
        provider=ModelProvider.ANTHROPIC,
        max_tokens=200000,
        cost_per_1k_input=0.015,
        cost_per_1k_output=0.075,
        supports_vision=True
    ),
    "claude-sonnet-4": ModelConfig(
        id="anthropic/claude-sonnet-4-20250514",
        provider=ModelProvider.ANTHROPIC,
        max_tokens=200000,
        cost_per_1k_input=0.003,
        cost_per_1k_output=0.015,
        supports_vision=True
    ),
    "claude-3.5-sonnet": ModelConfig(
        id="anthropic/claude-3.5-sonnet",
        provider=ModelProvider.ANTHROPIC,
        max_tokens=200000,
        cost_per_1k_input=0.003,
        cost_per_1k_output=0.015,
        supports_vision=True
    ),

    # OpenAI GPT
    "gpt-4o": ModelConfig(
        id="openai/gpt-4o",
        provider=ModelProvider.OPENAI,
        max_tokens=128000,
        cost_per_1k_input=0.005,
        cost_per_1k_output=0.015,
        supports_vision=True
    ),
    "gpt-4o-mini": ModelConfig(
        id="openai/gpt-4o-mini",
        provider=ModelProvider.OPENAI,
        max_tokens=128000,
        cost_per_1k_input=0.00015,
        cost_per_1k_output=0.0006,
        supports_vision=True
    ),

    # Google Gemini
    "gemini-2.0-flash": ModelConfig(
        id="google/gemini-2.0-flash-exp",
        provider=ModelProvider.GOOGLE,
        max_tokens=1000000,
        cost_per_1k_input=0.0001,
        cost_per_1k_output=0.0004,
        supports_vision=True
    ),
}


@dataclass
class SquadConfig:
    """Configuration for a squad of agents."""
    name: str
    description: str
    agents: List[str]
    priority: int = 1  # 1 = highest priority


# Squad configurations
SQUAD_CONFIGS: Dict[str, SquadConfig] = {
    "frontend_squad": SquadConfig(
        name="Frontend Squad",
        description="UI/UX design, React/Next.js development, component architecture",
        agents=["ui_ux_designer", "frontend_developer", "component_architect"],
        priority=1
    ),
    "backend_squad": SquadConfig(
        name="Backend Squad",
        description="API design, server development, third-party integrations",
        agents=["api_architect", "backend_developer", "integration_specialist"],
        priority=1
    ),
    "data_squad": SquadConfig(
        name="Data Squad",
        description="Database architecture, analytics, search & RAG",
        agents=["database_architect", "analytics_engineer", "search_rag_specialist"],
        priority=2
    ),
    "business_squad": SquadConfig(
        name="Business Squad",
        description="Product management, copywriting, pricing, compliance, growth",
        agents=["product_manager", "copywriter", "pricing_strategist",
                "compliance_officer", "growth_engineer"],
        priority=2
    ),
    "devops_squad": SquadConfig(
        name="DevOps Squad",
        description="Infrastructure, security, monitoring",
        agents=["infrastructure_engineer", "security_engineer", "monitoring_engineer"],
        priority=1
    ),
    "qa_squad": SquadConfig(
        name="QA Squad",
        description="Testing, code review",
        agents=["test_engineer", "code_reviewer"],
        priority=1
    ),
    "performance_squad": SquadConfig(
        name="Performance Squad",
        description="Performance optimization, bundle optimization, database optimization",
        agents=["performance_engineer", "bundle_optimizer", "database_optimizer"],
        priority=2
    ),
    "documentation_squad": SquadConfig(
        name="Documentation Squad",
        description="Technical writing, API documentation",
        agents=["technical_writer", "api_documenter"],
        priority=3
    ),
    "accessibility_squad": SquadConfig(
        name="Accessibility Squad",
        description="WCAG compliance, internationalization",
        agents=["accessibility_expert", "i18n_specialist"],
        priority=2
    ),
    "ai_ml_squad": SquadConfig(
        name="AI/ML Squad",
        description="LLM integration, ML operations",
        agents=["ai_engineer", "ml_ops_engineer"],
        priority=2
    ),
}


@dataclass
class WorkflowStep:
    """A single step in a workflow."""
    name: str
    description: str
    squads: List[str]
    parallel: bool = False
    required: bool = True
    timeout_seconds: int = 300


@dataclass
class WorkflowConfig:
    """Configuration for a workflow."""
    name: str
    description: str
    steps: List[WorkflowStep]
    quality_gate_enabled: bool = True
    max_iterations: int = 3


@dataclass
class QualityGateConfig:
    """Configuration for the quality gate."""
    checks: List[str] = field(default_factory=lambda: [
        "typescript_check",
        "lint_check",
        "test_coverage",
        "security_audit",
        "performance_check"
    ])
    min_coverage: float = 80.0
    auto_fix_enabled: bool = True
    max_fix_iterations: int = 3
    required_checks: List[str] = field(default_factory=lambda: [
        "typescript_check",
        "lint_check",
        "security_audit"
    ])


@dataclass
class OrchestrationConfig:
    """Main orchestration configuration."""
    default_model: str = "claude-3.5-sonnet"
    max_parallel_agents: int = 5
    timeout_seconds: int = 600
    quality_gate: QualityGateConfig = field(default_factory=QualityGateConfig)
    enable_logging: bool = True
    log_level: str = "INFO"
    enable_metrics: bool = True
    enable_callbacks: bool = True


# Default configuration instance
DEFAULT_CONFIG = OrchestrationConfig()
