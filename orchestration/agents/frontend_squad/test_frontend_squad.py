"""
Unit tests for Frontend Squad agents.

Run with:
    pytest orchestration/agents/frontend_squad/test_frontend_squad.py -v
"""

import pytest
import asyncio
import os
from unittest.mock import Mock, patch, AsyncMock

from orchestration.agents.frontend_squad import (
    UIUXDesignerAgent,
    FrontendDeveloperAgent,
    ComponentArchitectAgent,
    create_frontend_squad,
    get_squad_info,
    execute_workflow
)


@pytest.fixture
def mock_api_key():
    """Provide a mock API key for testing."""
    return "test-api-key-12345"


@pytest.fixture
def mock_llm_response():
    """Provide a mock LLM response."""
    return """
# Design System

Here's a comprehensive design system:

```json
{
  "colors": {
    "primary": "#3B82F6",
    "secondary": "#8B5CF6"
  },
  "typography": {
    "fontFamily": "Inter",
    "sizes": ["xs", "sm", "base", "lg", "xl"]
  }
}
```

This design system includes colors and typography.
"""


@pytest.fixture
def mock_code_response():
    """Provide a mock code response."""
    return """
Here's the component:

```tsx
import React from 'react';

interface ButtonProps {
  variant?: 'primary' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  children
}) => {
  return (
    <button className={`btn btn-${variant} btn-${size}`}>
      {children}
    </button>
  );
};
```

This component supports multiple variants and sizes.
"""


class TestUIUXDesignerAgent:
    """Tests for UI/UX Designer Agent."""

    @pytest.mark.asyncio
    async def test_initialization(self, mock_api_key):
        """Test agent initialization."""
        agent = UIUXDesignerAgent(api_key=mock_api_key)

        assert agent.name == "ui_ux_designer"
        assert agent.api_key == mock_api_key
        assert agent.model == "openai/gpt-4o"
        assert len(agent.memory) == 0

    @pytest.mark.asyncio
    async def test_system_prompt(self, mock_api_key):
        """Test that system prompt is properly set."""
        agent = UIUXDesignerAgent(api_key=mock_api_key)

        assert "UI/UX Designer" in agent.system_prompt
        assert "accessibility" in agent.system_prompt.lower()
        assert "WCAG" in agent.system_prompt

    @pytest.mark.asyncio
    async def test_execute_design_system(self, mock_api_key, mock_llm_response):
        """Test executing design system task."""
        agent = UIUXDesignerAgent(api_key=mock_api_key)

        with patch.object(agent, 'call_llm', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_llm_response

            result = await agent.execute({
                "task": "design_system",
                "feature": "app",
                "brand": {"primary_color": "#3B82F6"}
            })

            assert result["status"] == "success"
            assert result["task_type"] == "design_system"
            assert result["feature"] == "app"
            mock_llm.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_design_system_convenience(self, mock_api_key, mock_llm_response):
        """Test convenience method for design system creation."""
        agent = UIUXDesignerAgent(api_key=mock_api_key)

        with patch.object(agent, 'call_llm', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_llm_response

            result = await agent.create_design_system(
                brand={"primary_color": "#3B82F6"},
                accessibility_level="WCAG AA"
            )

            assert result["status"] == "success"
            assert "result" in result

    @pytest.mark.asyncio
    async def test_generate_wireframe(self, mock_api_key, mock_llm_response):
        """Test wireframe generation."""
        agent = UIUXDesignerAgent(api_key=mock_api_key)

        with patch.object(agent, 'call_llm', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_llm_response

            result = await agent.generate_wireframe(
                feature="Dashboard",
                requirements="Stats cards and charts"
            )

            assert result["status"] == "success"
            assert result["task_type"] == "wireframe"

    @pytest.mark.asyncio
    async def test_error_handling(self, mock_api_key):
        """Test error handling in execute method."""
        agent = UIUXDesignerAgent(api_key=mock_api_key)

        with patch.object(agent, 'call_llm', side_effect=Exception("API Error")):
            result = await agent.execute({
                "task": "design_system",
                "feature": "app"
            })

            assert result["status"] == "error"
            assert "error" in result
            assert "API Error" in result["error"]


class TestFrontendDeveloperAgent:
    """Tests for Frontend Developer Agent."""

    @pytest.mark.asyncio
    async def test_initialization(self, mock_api_key):
        """Test agent initialization."""
        agent = FrontendDeveloperAgent(api_key=mock_api_key)

        assert agent.name == "frontend_developer"
        assert agent.api_key == mock_api_key
        assert len(agent.memory) == 0

    @pytest.mark.asyncio
    async def test_system_prompt(self, mock_api_key):
        """Test that system prompt is properly set."""
        agent = FrontendDeveloperAgent(api_key=mock_api_key)

        assert "Frontend Developer" in agent.system_prompt
        assert "React" in agent.system_prompt
        assert "TypeScript" in agent.system_prompt
        assert "Next.js" in agent.system_prompt

    @pytest.mark.asyncio
    async def test_execute_create_component(self, mock_api_key, mock_code_response):
        """Test creating a component."""
        agent = FrontendDeveloperAgent(api_key=mock_api_key)

        with patch.object(agent, 'call_llm', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_code_response

            result = await agent.execute({
                "task": "create_component",
                "component_name": "Button",
                "requirements": "Clickable button with variants"
            })

            assert result["status"] == "success"
            assert result["task_type"] == "create_component"
            assert result["component_name"] == "Button"
            assert "code" in result["result"]

    @pytest.mark.asyncio
    async def test_create_component_convenience(self, mock_api_key, mock_code_response):
        """Test convenience method for component creation."""
        agent = FrontendDeveloperAgent(api_key=mock_api_key)

        with patch.object(agent, 'call_llm', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_code_response

            result = await agent.create_component(
                name="Card",
                component_type="ui",
                requirements="Display content with header and footer"
            )

            assert result["status"] == "success"
            assert result["component_name"] == "Card"

    @pytest.mark.asyncio
    async def test_extract_dependencies(self, mock_api_key):
        """Test dependency extraction from code."""
        agent = FrontendDeveloperAgent(api_key=mock_api_key)

        code = """
        import React from 'react';
        import { Button } from '@/components/ui/button';
        import axios from 'axios';
        import { formatDate } from './utils';
        """

        deps = agent._extract_dependencies(code)

        assert "react" in deps
        assert "axios" in deps
        # Relative imports should not be included
        assert "./utils" not in deps

    @pytest.mark.asyncio
    async def test_extract_code_blocks(self, mock_api_key, mock_code_response):
        """Test code block extraction."""
        agent = FrontendDeveloperAgent(api_key=mock_api_key)

        blocks = agent._extract_code_blocks(mock_code_response)

        assert len(blocks) > 0
        assert "Button" in blocks[0]
        assert "interface" in blocks[0]


class TestComponentArchitectAgent:
    """Tests for Component Architect Agent."""

    @pytest.mark.asyncio
    async def test_initialization(self, mock_api_key):
        """Test agent initialization."""
        agent = ComponentArchitectAgent(api_key=mock_api_key)

        assert agent.name == "component_architect"
        assert agent.api_key == mock_api_key

    @pytest.mark.asyncio
    async def test_system_prompt(self, mock_api_key):
        """Test that system prompt is properly set."""
        agent = ComponentArchitectAgent(api_key=mock_api_key)

        assert "Component Architect" in agent.system_prompt
        assert "architecture" in agent.system_prompt.lower()
        assert "shadcn/ui" in agent.system_prompt

    @pytest.mark.asyncio
    async def test_execute_design_library(self, mock_api_key, mock_llm_response):
        """Test designing a component library."""
        agent = ComponentArchitectAgent(api_key=mock_api_key)

        with patch.object(agent, 'call_llm', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_llm_response

            result = await agent.execute({
                "task": "design_component_library",
                "components": ["Button", "Input", "Card"]
            })

            assert result["status"] == "success"
            assert result["task_type"] == "design_component_library"

    @pytest.mark.asyncio
    async def test_design_compound_component(self, mock_api_key, mock_code_response):
        """Test designing a compound component."""
        agent = ComponentArchitectAgent(api_key=mock_api_key)

        with patch.object(agent, 'call_llm', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_code_response

            result = await agent.design_compound_component(
                component_name="Form",
                sub_components=["FormField", "FormLabel"]
            )

            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_extract_sections(self, mock_api_key):
        """Test section extraction from markdown."""
        agent = ComponentArchitectAgent(api_key=mock_api_key)

        text = """
## Section 1
Content for section 1

## Section 2
Content for section 2
More content
"""

        sections = agent._extract_sections(text)

        assert "Section 1" in sections
        assert "Section 2" in sections
        assert "Content for section 1" in sections["Section 1"]


class TestSquadFunctions:
    """Tests for squad-level functions."""

    def test_get_squad_info(self):
        """Test getting squad information."""
        info = get_squad_info()

        assert info["name"] == "Frontend Squad"
        assert "ui_ux_designer" in info["agents"]
        assert "frontend_developer" in info["agents"]
        assert "component_architect" in info["agents"]
        assert len(info["workflows"]) > 0

    def test_create_frontend_squad(self, mock_api_key):
        """Test creating the complete squad."""
        squad = create_frontend_squad(api_key=mock_api_key, model="test-model")

        assert "ui_ux_designer" in squad
        assert "frontend_developer" in squad
        assert "component_architect" in squad

        # Verify agent types
        assert isinstance(squad["ui_ux_designer"], UIUXDesignerAgent)
        assert isinstance(squad["frontend_developer"], FrontendDeveloperAgent)
        assert isinstance(squad["component_architect"], ComponentArchitectAgent)

        # Verify configuration
        assert squad["ui_ux_designer"].model == "test-model"
        assert squad["frontend_developer"].api_key == mock_api_key

    @pytest.mark.asyncio
    async def test_execute_workflow(self, mock_api_key, mock_llm_response):
        """Test executing a workflow."""
        squad = create_frontend_squad(api_key=mock_api_key)

        # Mock all agent execute methods
        for agent in squad.values():
            agent.execute = AsyncMock(return_value={
                "status": "success",
                "result": "test result"
            })

        results = await execute_workflow(
            workflow_name="component_creation",
            agents=squad,
            context={"component_name": "TestComponent"}
        )

        assert len(results) > 0
        # Verify that workflow steps were executed
        for step_result in results:
            assert "step" in step_result
            assert "result" in step_result
            assert step_result["result"]["status"] == "success"

    @pytest.mark.asyncio
    async def test_execute_workflow_invalid_name(self, mock_api_key):
        """Test executing workflow with invalid name."""
        squad = create_frontend_squad(api_key=mock_api_key)

        with pytest.raises(ValueError, match="Unknown workflow"):
            await execute_workflow(
                workflow_name="invalid_workflow",
                agents=squad,
                context={}
            )


class TestIntegration:
    """Integration tests for the Frontend Squad."""

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not os.getenv("OPENROUTER_API_KEY"),
        reason="Requires OPENROUTER_API_KEY environment variable"
    )
    async def test_real_api_call(self):
        """Test with real API (requires API key)."""
        api_key = os.getenv("OPENROUTER_API_KEY")
        agent = UIUXDesignerAgent(api_key=api_key)

        result = await agent.execute({
            "task": "wireframe",
            "feature": "Login Page",
            "requirements": "Email and password inputs, submit button"
        })

        assert result["status"] == "success"
        assert "result" in result

    @pytest.mark.asyncio
    async def test_full_workflow_mock(self, mock_api_key, mock_llm_response, mock_code_response):
        """Test full workflow with mocked LLM calls."""
        squad = create_frontend_squad(api_key=mock_api_key)

        # Mock LLM calls for each agent
        with patch.object(squad["ui_ux_designer"], 'call_llm', new_callable=AsyncMock) as mock1, \
             patch.object(squad["component_architect"], 'call_llm', new_callable=AsyncMock) as mock2, \
             patch.object(squad["frontend_developer"], 'call_llm', new_callable=AsyncMock) as mock3:

            mock1.return_value = mock_llm_response
            mock2.return_value = mock_code_response
            mock3.return_value = mock_code_response

            results = await execute_workflow(
                workflow_name="component_creation",
                agents=squad,
                context={
                    "component_name": "SearchBar",
                    "requirements": "Search input with auto-complete"
                }
            )

            # Verify all steps completed
            assert len(results) == len(get_squad_info()["workflows"]["component_creation"]["steps"])
            for step_result in results:
                assert step_result["result"]["status"] == "success"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
