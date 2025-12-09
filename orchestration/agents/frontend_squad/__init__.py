"""
Frontend Squad agents for the Devora orchestration system.

This module provides specialized agents for frontend development including:
- UI/UX Designer: Design systems, wireframes, user flows
- Frontend Developer: React/Next.js/TypeScript development
- Component Architect: Component library architecture and design

Usage:
    from orchestration.agents.frontend_squad import (
        UIUXDesignerAgent,
        FrontendDeveloperAgent,
        ComponentArchitectAgent
    )

    # Initialize agents
    designer = UIUXDesignerAgent(api_key="your-key")
    developer = FrontendDeveloperAgent(api_key="your-key")
    architect = ComponentArchitectAgent(api_key="your-key")

    # Execute tasks
    design_result = await designer.execute({
        "task": "design_system",
        "feature": "dashboard",
        "brand": {"primary_color": "#3B82F6"}
    })

    code_result = await developer.execute({
        "task": "create_component",
        "component_name": "UserDashboard",
        "requirements": "Display user stats"
    })

    spec_result = await architect.execute({
        "task": "create_component_spec",
        "components": ["Button", "Input"]
    })
"""

from .ui_ux_designer import UIUXDesignerAgent
from .frontend_developer import FrontendDeveloperAgent
from .component_architect import ComponentArchitectAgent

__all__ = [
    "UIUXDesignerAgent",
    "FrontendDeveloperAgent",
    "ComponentArchitectAgent",
]

# Squad metadata
SQUAD_INFO = {
    "name": "Frontend Squad",
    "description": "Specialized agents for frontend development and design",
    "agents": {
        "ui_ux_designer": {
            "class": UIUXDesignerAgent,
            "description": "UI/UX design, wireframes, design systems, accessibility",
            "capabilities": [
                "Generate wireframes and mockups",
                "Define design systems (colors, typography, spacing)",
                "Create user flows and journey maps",
                "Analyze accessibility (WCAG compliance)",
                "Design responsive layouts",
                "Create component specifications"
            ]
        },
        "frontend_developer": {
            "class": FrontendDeveloperAgent,
            "description": "React/Next.js/TypeScript development",
            "capabilities": [
                "Generate React/Next.js components with TypeScript",
                "Implement state management (Context, Zustand, React Query)",
                "Create custom hooks",
                "Optimize performance (memoization, code splitting)",
                "Implement responsive layouts",
                "Handle async data fetching",
                "Error boundaries and error handling"
            ]
        },
        "component_architect": {
            "class": ComponentArchitectAgent,
            "description": "Component library architecture and design",
            "capabilities": [
                "Design component library architecture",
                "Structure shadcn/ui component integration",
                "Define component APIs (props, interfaces)",
                "Create TypeScript type definitions",
                "Generate Storybook documentation",
                "Establish naming conventions",
                "Design compound components"
            ]
        }
    },
    "workflows": {
        "design_to_code": {
            "description": "Complete design to implementation workflow",
            "steps": [
                {
                    "agent": "ui_ux_designer",
                    "task": "Create design system and wireframes"
                },
                {
                    "agent": "component_architect",
                    "task": "Design component architecture and APIs"
                },
                {
                    "agent": "frontend_developer",
                    "task": "Implement components with TypeScript"
                }
            ]
        },
        "component_creation": {
            "description": "Create a new component from scratch",
            "steps": [
                {
                    "agent": "ui_ux_designer",
                    "task": "Design component UI and interactions"
                },
                {
                    "agent": "component_architect",
                    "task": "Define component API and variants"
                },
                {
                    "agent": "frontend_developer",
                    "task": "Implement component code"
                },
                {
                    "agent": "component_architect",
                    "task": "Create Storybook documentation"
                }
            ]
        },
        "design_system_creation": {
            "description": "Create a complete design system",
            "steps": [
                {
                    "agent": "ui_ux_designer",
                    "task": "Define design tokens and visual language"
                },
                {
                    "agent": "component_architect",
                    "task": "Structure component library"
                },
                {
                    "agent": "frontend_developer",
                    "task": "Implement base components"
                }
            ]
        }
    }
}


def get_squad_info() -> dict:
    """
    Get information about the Frontend Squad.

    Returns:
        Dictionary with squad metadata, agents, and workflows
    """
    return SQUAD_INFO


def create_frontend_squad(api_key: str, model: str = "openai/gpt-4o") -> dict:
    """
    Create all Frontend Squad agents with the given configuration.

    Args:
        api_key: OpenRouter API key
        model: LLM model to use (default: gpt-4o)

    Returns:
        Dictionary of instantiated agents

    Example:
        squad = create_frontend_squad(api_key="your-key")
        designer = squad["ui_ux_designer"]
        developer = squad["frontend_developer"]
        architect = squad["component_architect"]
    """
    return {
        "ui_ux_designer": UIUXDesignerAgent(api_key=api_key, model=model),
        "frontend_developer": FrontendDeveloperAgent(api_key=api_key, model=model),
        "component_architect": ComponentArchitectAgent(api_key=api_key, model=model),
    }


async def execute_workflow(
    workflow_name: str,
    agents: dict,
    context: dict
) -> list:
    """
    Execute a predefined Frontend Squad workflow.

    Args:
        workflow_name: Name of the workflow to execute
        agents: Dictionary of instantiated agents
        context: Initial context for the workflow

    Returns:
        List of results from each workflow step

    Raises:
        ValueError: If workflow_name is not found

    Example:
        squad = create_frontend_squad(api_key="your-key")
        results = await execute_workflow(
            "component_creation",
            squad,
            {"component_name": "Button", "requirements": "Primary action button"}
        )
    """
    if workflow_name not in SQUAD_INFO["workflows"]:
        raise ValueError(f"Unknown workflow: {workflow_name}")

    workflow = SQUAD_INFO["workflows"][workflow_name]
    results = []

    for step in workflow["steps"]:
        agent_name = step["agent"]
        if agent_name not in agents:
            raise ValueError(f"Agent not found in squad: {agent_name}")

        agent = agents[agent_name]
        result = await agent.execute(context)
        results.append({
            "step": step,
            "result": result
        })

        # Update context with result for next step
        context["previous_step"] = result

    return results
