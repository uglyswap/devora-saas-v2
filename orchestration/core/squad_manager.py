"""
Squad Manager - Manages 10 Specialized Squads for Devora

This module manages the 10 squads containing 28 specialized agents:
- Squad Architecture (3 agents)
- Squad Frontend (3 agents)
- Squad Backend (3 agents)
- Squad Quality (3 agents)
- Squad AI (3 agents)
- Squad Design (3 agents)
- Squad Business (3 agents)
- Squad Infrastructure (3 agents)
- Squad Data (3 agents)
- Squad Mobile (3 agents)

Each squad has specific responsibilities and dependencies.
"""

import asyncio
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime


class SquadType(Enum):
    """Types of squads in the system."""
    ARCHITECTURE = "architecture"
    FRONTEND = "frontend"
    BACKEND = "backend"
    QUALITY = "quality"
    AI = "ai"
    DESIGN = "design"
    BUSINESS = "business"
    INFRASTRUCTURE = "infrastructure"
    DATA = "data"
    MOBILE = "mobile"


@dataclass
class Squad:
    """Represents a squad of specialized agents.

    Attributes:
        name: Squad name
        type: Squad type
        agents: List of agent names in the squad
        description: Squad description
        dependencies: List of squad names this squad depends on
        priority: Execution priority (0-10)
    """
    name: str
    type: SquadType
    agents: List[str]
    description: str
    dependencies: List[str] = None
    priority: int = 5

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class SquadManager:
    """Manages all squads and their agents.

    This manager handles:
    - Squad registration and configuration
    - Agent assignment to squads
    - Squad execution and coordination
    - Dependency management between squads
    - Load balancing and resource allocation
    """

    def __init__(
        self,
        api_key: str,
        model: str = "anthropic/claude-3.5-sonnet",
        callbacks: Optional[List[Callable]] = None
    ):
        """Initialize squad manager.

        Args:
            api_key: OpenRouter API key
            model: Default LLM model to use
            callbacks: List of callback functions
        """
        self.api_key = api_key
        self.model = model
        self.callbacks = callbacks or []

        # Setup logging
        self.logger = logging.getLogger("devora.squad_manager")
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        # Initialize squads
        self.squads: Dict[str, Squad] = {}
        self._register_squads()

        # Agent registry
        self.agents: Dict[str, Any] = {}

        self.logger.info(f"SquadManager initialized with {len(self.squads)} squads")

    def _register_squads(self) -> None:
        """Register all 10 squads with their agents and dependencies."""

        # Squad 1: Architecture
        self.squads["architecture"] = Squad(
            name="architecture",
            type=SquadType.ARCHITECTURE,
            agents=["architect", "tech_lead", "security_architect"],
            description="High-level architecture, technical leadership, security design",
            dependencies=[],
            priority=10
        )

        # Squad 2: Frontend
        self.squads["frontend"] = Squad(
            name="frontend",
            type=SquadType.FRONTEND,
            agents=["react_developer", "ui_ux_designer", "performance_expert"],
            description="React/Next.js development, UI/UX design, frontend performance",
            dependencies=["architecture", "design"],
            priority=7
        )

        # Squad 3: Backend
        self.squads["backend"] = Squad(
            name="backend",
            type=SquadType.BACKEND,
            agents=["api_developer", "database_expert", "integration_specialist"],
            description="API development, database design, system integration",
            dependencies=["architecture", "data"],
            priority=8
        )

        # Squad 4: Quality
        self.squads["quality"] = Squad(
            name="quality",
            type=SquadType.QUALITY,
            agents=["tester", "code_reviewer", "devops_engineer"],
            description="Testing, code review, CI/CD, deployment",
            dependencies=["frontend", "backend"],
            priority=6
        )

        # Squad 5: AI
        self.squads["ai"] = Squad(
            name="ai",
            type=SquadType.AI,
            agents=["ai_ml_engineer", "prompt_engineer", "data_scientist"],
            description="AI/ML integration, prompt engineering, data science",
            dependencies=["data", "backend"],
            priority=5
        )

        # Squad 6: Design
        self.squads["design"] = Squad(
            name="design",
            type=SquadType.DESIGN,
            agents=["product_designer", "ux_researcher", "design_system_lead"],
            description="Product design, UX research, design systems",
            dependencies=["business"],
            priority=9
        )

        # Squad 7: Business
        self.squads["business"] = Squad(
            name="business",
            type=SquadType.BUSINESS,
            agents=["product_manager", "business_analyst", "strategy_consultant"],
            description="Product management, business analysis, strategy",
            dependencies=[],
            priority=10
        )

        # Squad 8: Infrastructure
        self.squads["infrastructure"] = Squad(
            name="infrastructure",
            type=SquadType.INFRASTRUCTURE,
            agents=["cloud_architect", "sre", "platform_engineer"],
            description="Cloud infrastructure, reliability, platform engineering",
            dependencies=["architecture"],
            priority=7
        )

        # Squad 9: Data
        self.squads["data"] = Squad(
            name="data",
            type=SquadType.DATA,
            agents=["data_engineer", "analytics_engineer", "bi_developer"],
            description="Data pipelines, analytics, business intelligence",
            dependencies=["architecture"],
            priority=8
        )

        # Squad 10: Mobile
        self.squads["mobile"] = Squad(
            name="mobile",
            type=SquadType.MOBILE,
            agents=["ios_developer", "android_developer", "react_native_expert"],
            description="iOS, Android, React Native mobile development",
            dependencies=["architecture", "design", "backend"],
            priority=5
        )

        self.logger.info("All 10 squads registered successfully")

    def get_squad(self, squad_name: str) -> Optional[Squad]:
        """Get squad by name.

        Args:
            squad_name: Name of the squad

        Returns:
            Squad object or None if not found
        """
        return self.squads.get(squad_name)

    def get_available_squads(self) -> List[str]:
        """Get list of all available squad names.

        Returns:
            List of squad names
        """
        return list(self.squads.keys())

    def get_squad_info(self, squad_name: str) -> Dict[str, Any]:
        """Get detailed information about a squad.

        Args:
            squad_name: Name of the squad

        Returns:
            Dictionary with squad information
        """
        squad = self.squads.get(squad_name)
        if not squad:
            return {"error": f"Squad '{squad_name}' not found"}

        return {
            "name": squad.name,
            "type": squad.type.value,
            "agents": squad.agents,
            "description": squad.description,
            "dependencies": squad.dependencies,
            "priority": squad.priority,
            "agent_count": len(squad.agents)
        }

    def get_agents_for_task(self, task_type: str) -> List[str]:
        """Get recommended agents for a specific task type.

        Args:
            task_type: Type of task (e.g., 'frontend', 'api', 'testing')

        Returns:
            List of recommended agent names
        """
        task_mappings = {
            "frontend": ["react_developer", "ui_ux_designer", "performance_expert"],
            "backend": ["api_developer", "database_expert", "integration_specialist"],
            "api": ["api_developer", "backend_developer", "integration_specialist"],
            "database": ["database_expert", "data_engineer", "backend_developer"],
            "testing": ["tester", "code_reviewer", "devops_engineer"],
            "design": ["product_designer", "ux_researcher", "ui_ux_designer"],
            "architecture": ["architect", "tech_lead", "security_architect"],
            "mobile": ["ios_developer", "android_developer", "react_native_expert"],
            "ai": ["ai_ml_engineer", "prompt_engineer", "data_scientist"],
            "data": ["data_engineer", "analytics_engineer", "data_scientist"],
            "infrastructure": ["cloud_architect", "sre", "platform_engineer"],
            "security": ["security_architect", "code_reviewer", "sre"],
            "performance": ["performance_expert", "sre", "database_expert"],
            "business": ["product_manager", "business_analyst", "strategy_consultant"]
        }

        return task_mappings.get(task_type.lower(), [])

    def get_squad_dependencies(self) -> Dict[str, List[str]]:
        """Get dependency graph for all squads.

        Returns:
            Dictionary mapping squad names to their dependencies
        """
        return {
            squad.name: squad.dependencies
            for squad in self.squads.values()
        }

    async def execute_squad(
        self,
        squad_name: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute all agents in a squad.

        Args:
            squad_name: Name of squad to execute
            context: Execution context with task details

        Returns:
            Combined results from all agents in the squad
        """
        squad = self.squads.get(squad_name)
        if not squad:
            raise ValueError(f"Squad '{squad_name}' not found")

        self.logger.info(f"Executing squad: {squad_name} ({len(squad.agents)} agents)")

        start_time = datetime.now()

        # Execute all agents in the squad in parallel
        tasks = []
        for agent_name in squad.agents:
            task = self._execute_agent(agent_name, context)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Aggregate results
        outputs = {}
        errors = []
        total_tokens = 0
        agents_executed = 0

        for agent_name, result in zip(squad.agents, results):
            if isinstance(result, Exception):
                self.logger.error(f"Agent {agent_name} failed: {str(result)}")
                errors.append({
                    "agent": agent_name,
                    "error": str(result)
                })
            else:
                outputs[agent_name] = result
                agents_executed += 1

                if isinstance(result, dict):
                    metrics = result.get("metrics", {})
                    total_tokens += metrics.get("total_tokens", 0)

        execution_time = (datetime.now() - start_time).total_seconds()

        return {
            "squad": squad_name,
            "status": "completed" if not errors else "partial",
            "outputs": outputs,
            "errors": errors,
            "metrics": {
                "execution_time": execution_time,
                "total_tokens": total_tokens,
                "agents_executed": agents_executed,
                "agents_total": len(squad.agents)
            },
            "timestamp": datetime.now().isoformat()
        }

    async def _execute_agent(
        self,
        agent_name: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single agent.

        Args:
            agent_name: Name of the agent
            context: Execution context

        Returns:
            Agent execution result
        """
        # For now, simulate agent execution
        # In production, this would load and execute actual agent instances
        self.logger.debug(f"Executing agent: {agent_name}")

        # Simulate processing delay
        await asyncio.sleep(0.5)

        # Build agent-specific prompt based on context
        prompt = self._build_agent_prompt(agent_name, context)

        # Call LLM (simplified for now)
        try:
            result = await self._call_agent_llm(agent_name, prompt, context)
            return result
        except Exception as e:
            self.logger.error(f"Agent {agent_name} execution failed: {str(e)}")
            raise

    def _build_agent_prompt(
        self,
        agent_name: str,
        context: Dict[str, Any]
    ) -> str:
        """Build agent-specific prompt.

        Args:
            agent_name: Name of the agent
            context: Execution context

        Returns:
            Formatted prompt for the agent
        """
        task = context.get("task", "")
        requirements = context.get("requirements", {})

        # Agent role descriptions
        roles = {
            "architect": "You are a Senior Software Architect responsible for high-level system design.",
            "tech_lead": "You are a Technical Lead responsible for technical decisions and team guidance.",
            "security_architect": "You are a Security Architect responsible for security design and compliance.",
            "react_developer": "You are a Senior React Developer specialized in Next.js and modern frontend.",
            "ui_ux_designer": "You are a UI/UX Designer responsible for user experience and interface design.",
            "performance_expert": "You are a Performance Expert focused on frontend optimization.",
            "api_developer": "You are a Senior API Developer specialized in RESTful and GraphQL APIs.",
            "database_expert": "You are a Database Expert specialized in PostgreSQL and optimization.",
            "integration_specialist": "You are an Integration Specialist for third-party services and APIs.",
            "tester": "You are a QA Engineer responsible for testing strategy and execution.",
            "code_reviewer": "You are a Senior Code Reviewer ensuring code quality and best practices.",
            "devops_engineer": "You are a DevOps Engineer responsible for CI/CD and deployment.",
            "ai_ml_engineer": "You are an AI/ML Engineer specialized in LLM integration.",
            "prompt_engineer": "You are a Prompt Engineer expert in optimizing LLM interactions.",
            "data_scientist": "You are a Data Scientist focused on analysis and ML models.",
            "product_designer": "You are a Product Designer creating user-centered designs.",
            "ux_researcher": "You are a UX Researcher conducting user research and testing.",
            "design_system_lead": "You are a Design System Lead maintaining design consistency.",
            "product_manager": "You are a Product Manager defining product strategy and roadmap.",
            "business_analyst": "You are a Business Analyst translating business needs into requirements.",
            "strategy_consultant": "You are a Strategy Consultant providing strategic guidance.",
            "cloud_architect": "You are a Cloud Architect designing cloud infrastructure.",
            "sre": "You are a Site Reliability Engineer ensuring system reliability.",
            "platform_engineer": "You are a Platform Engineer building internal platforms.",
            "data_engineer": "You are a Data Engineer building data pipelines and ETL.",
            "analytics_engineer": "You are an Analytics Engineer creating analytics models.",
            "bi_developer": "You are a BI Developer building business intelligence dashboards.",
            "ios_developer": "You are an iOS Developer specialized in Swift and SwiftUI.",
            "android_developer": "You are an Android Developer specialized in Kotlin.",
            "react_native_expert": "You are a React Native Expert for cross-platform mobile."
        }

        role = roles.get(agent_name, f"You are a {agent_name.replace('_', ' ').title()}.")

        prompt = f"""{role}

TASK:
{task}

REQUIREMENTS:
{requirements}

Provide your expert analysis, recommendations, and implementation guidance for your specific area of expertise.
Be specific, actionable, and consider best practices.

Format your response as JSON with:
{{
  "analysis": "your analysis",
  "recommendations": ["recommendation 1", "recommendation 2"],
  "implementation": {{
    "approach": "implementation approach",
    "considerations": ["consideration 1", "consideration 2"],
    "risks": ["risk 1", "risk 2"]
  }},
  "next_steps": ["step 1", "step 2"]
}}"""

        return prompt

    async def _call_agent_llm(
        self,
        agent_name: str,
        prompt: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Call LLM for agent execution.

        Args:
            agent_name: Name of the agent
            prompt: Agent prompt
            context: Execution context

        Returns:
            Agent execution result
        """
        import requests
        import json

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 4096
        }

        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()

            result = response.json()
            content = result["choices"][0]["message"]["content"]

            # Try to parse JSON response
            try:
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()

                agent_output = json.loads(content)
            except json.JSONDecodeError:
                # If not JSON, use raw content
                agent_output = {
                    "raw_response": content,
                    "analysis": content[:500]
                }

            usage = result.get("usage", {})

            return {
                "agent": agent_name,
                "status": "success",
                "output": agent_output,
                "metrics": {
                    "total_tokens": usage.get("total_tokens", 0),
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0)
                },
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            raise Exception(f"LLM call failed for {agent_name}: {str(e)}")

    def get_squad_by_type(self, squad_type: SquadType) -> Optional[Squad]:
        """Get squad by type.

        Args:
            squad_type: Type of squad

        Returns:
            Squad object or None
        """
        for squad in self.squads.values():
            if squad.type == squad_type:
                return squad
        return None

    def get_all_agents(self) -> List[str]:
        """Get list of all agents across all squads.

        Returns:
            List of all agent names
        """
        all_agents = []
        for squad in self.squads.values():
            all_agents.extend(squad.agents)
        return all_agents
