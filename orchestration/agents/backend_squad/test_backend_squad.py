"""
Test script for Backend Squad agents.

This script validates that all agents can be imported and initialized correctly.
Run with: python -m pytest test_backend_squad.py -v
"""

import sys
import os

# Add backend to path for BaseAgent import
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../backend'))

import pytest
from api_architect import APIArchitect
from backend_developer import BackendDeveloper
from integration_specialist import IntegrationSpecialist


class TestBackendSquad:
    """Test suite for Backend Squad agents."""

    @pytest.fixture
    def api_key(self):
        """Mock API key for testing."""
        return "test-api-key-123"

    def test_api_architect_initialization(self, api_key):
        """Test that APIArchitect can be initialized."""
        agent = APIArchitect(api_key=api_key)
        assert agent.name == "APIArchitect"
        assert agent.api_key == api_key
        assert agent.model == "openai/gpt-4o"

    def test_backend_developer_initialization(self, api_key):
        """Test that BackendDeveloper can be initialized."""
        agent = BackendDeveloper(api_key=api_key)
        assert agent.name == "BackendDeveloper"
        assert agent.api_key == api_key

    def test_integration_specialist_initialization(self, api_key):
        """Test that IntegrationSpecialist can be initialized."""
        agent = IntegrationSpecialist(api_key=api_key)
        assert agent.name == "IntegrationSpecialist"
        assert agent.api_key == api_key

    def test_all_agents_have_execute_method(self, api_key):
        """Test that all agents implement execute method."""
        agents = [
            APIArchitect(api_key),
            BackendDeveloper(api_key),
            IntegrationSpecialist(api_key),
        ]

        for agent in agents:
            assert hasattr(agent, 'execute')
            assert callable(agent.execute)

    def test_all_agents_have_memory(self, api_key):
        """Test that all agents inherit memory from BaseAgent."""
        agents = [
            APIArchitect(api_key),
            BackendDeveloper(api_key),
            IntegrationSpecialist(api_key),
        ]

        for agent in agents:
            assert hasattr(agent, 'memory')
            assert hasattr(agent, 'add_to_memory')
            assert hasattr(agent, 'get_memory')
            assert hasattr(agent, 'clear_memory')


def test_module_exports():
    """Test that __init__.py exports all agents correctly."""
    from . import (
        APIArchitect,
        BackendDeveloper,
        IntegrationSpecialist,
        BACKEND_SQUAD_AGENTS,
        get_agent,
        list_agents,
    )

    # Test that classes are exported
    assert APIArchitect is not None
    assert BackendDeveloper is not None
    assert IntegrationSpecialist is not None

    # Test metadata
    assert "api_architect" in BACKEND_SQUAD_AGENTS
    assert "backend_developer" in BACKEND_SQUAD_AGENTS
    assert "integration_specialist" in BACKEND_SQUAD_AGENTS

    # Test factory function
    agent = get_agent("api_architect", api_key="test-key")
    assert isinstance(agent, APIArchitect)

    # Test list function
    agents = list_agents()
    assert len(agents) == 3


def test_agent_capabilities():
    """Test that agent capabilities are documented."""
    from . import BACKEND_SQUAD_AGENTS

    for agent_name, metadata in BACKEND_SQUAD_AGENTS.items():
        assert "class" in metadata
        assert "description" in metadata
        assert "capabilities" in metadata
        assert len(metadata["capabilities"]) > 0


if __name__ == "__main__":
    # Quick manual test
    print("Testing Backend Squad agents...")

    api_key = "test-key"

    print("\n1. Testing APIArchitect...")
    api_architect = APIArchitect(api_key=api_key)
    print(f"   ✓ Name: {api_architect.name}")

    print("\n2. Testing BackendDeveloper...")
    backend_dev = BackendDeveloper(api_key=api_key)
    print(f"   ✓ Name: {backend_dev.name}")

    print("\n3. Testing IntegrationSpecialist...")
    integration = IntegrationSpecialist(api_key=api_key)
    print(f"   ✓ Name: {integration.name}")

    print("\n4. Testing module exports...")
    from . import list_agents, get_agent

    agents = list_agents()
    print(f"   ✓ Available agents: {', '.join(agents.keys())}")

    print("\n5. Testing factory function...")
    agent = get_agent("api_architect", api_key="test")
    print(f"   ✓ Created: {agent.name}")

    print("\n✅ All tests passed!")
