"""
Data Squad - Specialized agents for data, analytics, and search.

This module contains expert agents for:
- Database architecture and optimization
- Analytics and metrics tracking
- Search and RAG implementations
"""

from .database_architect import DatabaseArchitectAgent
from .analytics_engineer import AnalyticsEngineerAgent
from .search_rag_specialist import SearchRAGSpecialistAgent

__all__ = [
    'DatabaseArchitectAgent',
    'AnalyticsEngineerAgent',
    'SearchRAGSpecialistAgent',
    'AGENTS_METADATA',
    'get_agent',
    'list_agents'
]

# Agent metadata for orchestration
AGENTS_METADATA = {
    'database_architect': {
        'class': DatabaseArchitectAgent,
        'name': 'Database Architect',
        'description': 'Expert in PostgreSQL/MongoDB schema design, migrations, RLS, and optimization',
        'capabilities': [
            'schema_design',
            'migrations',
            'rls_policies',
            'index_optimization',
            'type_generation',
            'data_modeling'
        ],
        'tags': ['database', 'postgresql', 'supabase', 'schema', 'sql']
    },
    'analytics_engineer': {
        'class': AnalyticsEngineerAgent,
        'name': 'Analytics Engineer',
        'description': 'Expert in analytics implementation, event tracking, and metrics',
        'capabilities': [
            'event_tracking',
            'metrics_definition',
            'dashboard_creation',
            'ab_testing',
            'funnel_analysis',
            'posthog_setup',
            'mixpanel_setup'
        ],
        'tags': ['analytics', 'metrics', 'tracking', 'posthog', 'mixpanel', 'kpi']
    },
    'search_rag_specialist': {
        'class': SearchRAGSpecialistAgent,
        'name': 'Search & RAG Specialist',
        'description': 'Expert in search implementation and RAG systems',
        'capabilities': [
            'fulltext_search',
            'vector_search',
            'hybrid_search',
            'rag_pipeline',
            'embeddings',
            'semantic_search'
        ],
        'tags': ['search', 'rag', 'embeddings', 'vector', 'semantic', 'pgvector']
    }
}


def get_agent(agent_type: str, api_key: str, model: str = "openai/gpt-4o"):
    """
    Factory function to create agents by type.

    Args:
        agent_type: Type of agent to create
        api_key: OpenRouter API key
        model: LLM model to use

    Returns:
        Agent instance

    Example:
        >>> agent = get_agent('database_architect', api_key)
        >>> result = await agent.execute(task)
    """
    metadata = AGENTS_METADATA.get(agent_type)
    if not metadata:
        raise ValueError(f"Unknown agent type: {agent_type}. Available: {list(AGENTS_METADATA.keys())}")

    agent_class = metadata['class']
    return agent_class(api_key, model)


def list_agents():
    """
    List all available agents in the Data Squad.

    Returns:
        Dictionary of agent metadata
    """
    return AGENTS_METADATA


# Example usage
if __name__ == "__main__":
    import asyncio
    import os

    async def demo():
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            print("Error: OPENROUTER_API_KEY not set")
            return

        print("Data Squad Agents:")
        print("=" * 60)

        for agent_id, metadata in AGENTS_METADATA.items():
            print(f"\n{metadata['name']}")
            print(f"  ID: {agent_id}")
            print(f"  Description: {metadata['description']}")
            print(f"  Capabilities: {', '.join(metadata['capabilities'])}")
            print(f"  Tags: {', '.join(metadata['tags'])}")

        print("\n" + "=" * 60)
        print("\nDemo: Creating and testing Database Architect agent...")

        # Create agent
        agent = get_agent('database_architect', api_key)

        # Simple test task
        task = {
            "architecture": {"type": "SaaS", "multi_tenant": True},
            "data_models": [
                {
                    "name": "User",
                    "fields": {"email": "string", "name": "string"}
                }
            ],
            "features": ["Authentication"],
            "optimization_target": "balanced"
        }

        result = await agent.execute(task)

        print(f"\nAgent execution successful: {result['success']}")
        print(f"Generated {len(result['files'])} file(s)")

        if result['files']:
            print(f"\nFirst file: {result['files'][0]['name']}")
            print(f"Language: {result['files'][0]['language']}")
            print(f"Preview:\n{result['files'][0]['content'][:200]}...")

    # Run demo
    asyncio.run(demo())
