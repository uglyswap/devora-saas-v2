"""
Test suite for Documentation Squad agents.

Tests both Technical Writer and API Documenter agents with various scenarios.
"""

import pytest
import asyncio
import os
from technical_writer import TechnicalWriterAgent
from api_documenter import APIDocumenterAgent


# Test fixtures
@pytest.fixture
def api_key():
    """Get API key from environment or use test key."""
    return os.getenv("OPENROUTER_API_KEY", "test-api-key")


@pytest.fixture
def technical_writer(api_key):
    """Create Technical Writer agent instance."""
    return TechnicalWriterAgent(api_key=api_key)


@pytest.fixture
def api_documenter(api_key):
    """Create API Documenter agent instance."""
    return APIDocumenterAgent(api_key=api_key)


# Technical Writer Tests

@pytest.mark.asyncio
async def test_technical_writer_initialization(technical_writer):
    """Test Technical Writer agent initialization."""
    assert technical_writer is not None
    assert technical_writer.name == "TechnicalWriter"
    assert technical_writer.api_key is not None


@pytest.mark.asyncio
async def test_generate_readme(technical_writer):
    """Test README generation."""
    result = await technical_writer.generate_readme(
        project_name="Test Project",
        project_description="A test project for documentation",
        tech_stack=["Python", "FastAPI"],
        features=["Feature 1", "Feature 2"]
    )

    assert result is not None
    assert "success" in result
    if result["success"]:
        assert "documentation" in result
        assert "filename" in result
        assert result["filename"] == "README.md"
        assert "metadata" in result
        assert result["metadata"]["project_name"] == "Test Project"


@pytest.mark.asyncio
async def test_generate_adr(technical_writer):
    """Test ADR generation."""
    result = await technical_writer.generate_adr(
        project_name="Test Project",
        decision_context="We need to choose a database. Options: PostgreSQL, MySQL.",
        tech_stack=["PostgreSQL"]
    )

    assert result is not None
    assert "success" in result
    if result["success"]:
        assert "documentation" in result
        assert "filename" in result
        assert "adr" in result["filename"].lower()


@pytest.mark.asyncio
async def test_generate_installation_guide(technical_writer):
    """Test installation guide generation."""
    result = await technical_writer.generate_installation_guide(
        project_name="Test Project",
        project_description="Installation guide test",
        tech_stack=["Python 3.11+", "PostgreSQL"],
        requirements=["Python 3.11+", "PostgreSQL 15+"]
    )

    assert result is not None
    assert "success" in result
    if result["success"]:
        assert "documentation" in result
        assert "filename" in result
        assert "INSTALLATION" in result["filename"]


@pytest.mark.asyncio
async def test_generate_architecture_docs(technical_writer):
    """Test architecture documentation generation."""
    result = await technical_writer.generate_architecture_docs(
        project_name="Test Project",
        architecture_details="System uses microservices with FastAPI and PostgreSQL",
        tech_stack=["FastAPI", "PostgreSQL", "Redis"]
    )

    assert result is not None
    assert "success" in result
    if result["success"]:
        assert "documentation" in result
        assert "filename" in result
        assert "ARCHITECTURE" in result["filename"]


@pytest.mark.asyncio
async def test_generate_changelog(technical_writer):
    """Test changelog generation."""
    result = await technical_writer.generate_changelog(
        project_name="Test Project",
        version="1.0.0",
        changes={
            "added": ["New feature X"],
            "changed": ["Updated feature Y"],
            "fixed": ["Bug fix Z"]
        }
    )

    assert result is not None
    assert "success" in result
    if result["success"]:
        assert "documentation" in result
        assert "filename" in result
        assert "CHANGELOG" in result["filename"]


@pytest.mark.asyncio
async def test_technical_writer_execute_custom(technical_writer):
    """Test custom documentation via execute method."""
    result = await technical_writer.execute({
        "doc_type": "readme",
        "project_name": "Custom Project",
        "project_description": "Custom test",
        "tech_stack": ["Python"],
        "features": ["Test feature"],
        "audience": "developers",
        "include_diagrams": False
    })

    assert result is not None
    assert "success" in result
    if result["success"]:
        assert "documentation" in result
        assert "metadata" in result
        assert result["metadata"]["includes_diagrams"] == False


# API Documenter Tests

@pytest.mark.asyncio
async def test_api_documenter_initialization(api_documenter):
    """Test API Documenter agent initialization."""
    assert api_documenter is not None
    assert api_documenter.name == "APIDocumenter"
    assert api_documenter.api_key is not None


@pytest.mark.asyncio
async def test_generate_openapi_spec(api_documenter):
    """Test OpenAPI specification generation."""
    endpoints = [
        {
            "path": "/users",
            "method": "GET",
            "summary": "List users",
            "parameters": [
                {"name": "page", "in": "query", "type": "integer"}
            ]
        }
    ]

    result = await api_documenter.generate_openapi_spec(
        api_name="Test API",
        base_url="https://api.test.com/v1",
        endpoints=endpoints,
        auth_type="bearer",
        version="1.0.0"
    )

    assert result is not None
    assert "success" in result
    if result["success"]:
        assert "documentation" in result
        assert "filename" in result
        assert "openapi" in result["filename"]
        assert result["metadata"]["api_name"] == "Test API"
        assert result["metadata"]["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_generate_postman_collection(api_documenter):
    """Test Postman collection generation."""
    endpoints = [
        {
            "path": "/users",
            "method": "GET",
            "summary": "List users"
        },
        {
            "path": "/users/{id}",
            "method": "GET",
            "summary": "Get user"
        }
    ]

    result = await api_documenter.generate_postman_collection(
        api_name="Test API",
        base_url="https://api.test.com/v1",
        endpoints=endpoints,
        auth_type="bearer"
    )

    assert result is not None
    assert "success" in result
    if result["success"]:
        assert "documentation" in result
        assert "filename" in result
        assert "postman" in result["filename"]


@pytest.mark.asyncio
async def test_generate_integration_guide(api_documenter):
    """Test integration guide generation."""
    endpoints = [
        {
            "path": "/auth/login",
            "method": "POST",
            "summary": "Login"
        },
        {
            "path": "/users",
            "method": "GET",
            "summary": "List users"
        }
    ]

    result = await api_documenter.generate_integration_guide(
        api_name="Test API",
        base_url="https://api.test.com/v1",
        endpoints=endpoints,
        auth_type="bearer"
    )

    assert result is not None
    assert "success" in result
    if result["success"]:
        assert "documentation" in result
        assert "filename" in result
        assert "integration-guide" in result["filename"]


@pytest.mark.asyncio
async def test_generate_sdk_documentation_javascript(api_documenter):
    """Test SDK documentation generation for JavaScript."""
    endpoints = [
        {
            "path": "/users",
            "method": "GET",
            "summary": "List users"
        }
    ]

    result = await api_documenter.generate_sdk_documentation(
        api_name="Test API",
        language="javascript",
        base_url="https://api.test.com/v1",
        endpoints=endpoints,
        auth_type="bearer"
    )

    assert result is not None
    assert "success" in result
    if result["success"]:
        assert "documentation" in result
        assert "filename" in result
        assert result["metadata"]["language"] == "javascript"


@pytest.mark.asyncio
async def test_generate_sdk_documentation_python(api_documenter):
    """Test SDK documentation generation for Python."""
    endpoints = [
        {
            "path": "/users",
            "method": "GET",
            "summary": "List users"
        }
    ]

    result = await api_documenter.generate_sdk_documentation(
        api_name="Test API",
        language="python",
        base_url="https://api.test.com/v1",
        endpoints=endpoints,
        auth_type="bearer"
    )

    assert result is not None
    assert "success" in result
    if result["success"]:
        assert "documentation" in result
        assert "filename" in result
        assert result["metadata"]["language"] == "python"


@pytest.mark.asyncio
async def test_api_documenter_execute_custom(api_documenter):
    """Test custom API documentation via execute method."""
    endpoints = [
        {
            "path": "/test",
            "method": "GET",
            "summary": "Test endpoint"
        }
    ]

    result = await api_documenter.execute({
        "doc_type": "openapi",
        "api_name": "Custom API",
        "base_url": "https://custom.api.com",
        "endpoints": endpoints,
        "auth_type": "oauth2",
        "version": "2.0.0",
        "include_examples": True
    })

    assert result is not None
    assert "success" in result
    if result["success"]:
        assert "documentation" in result
        assert "metadata" in result
        assert result["metadata"]["auth_type"] == "oauth2"


# Integration Tests

@pytest.mark.asyncio
async def test_documentation_workflow(technical_writer, api_documenter):
    """Test complete documentation workflow with both agents."""
    # Generate README
    readme_result = await technical_writer.generate_readme(
        project_name="Workflow Test",
        project_description="Testing complete workflow",
        tech_stack=["Python", "FastAPI"],
        features=["API", "Documentation"]
    )

    assert readme_result["success"]

    # Generate API docs
    endpoints = [{"path": "/test", "method": "GET", "summary": "Test"}]
    api_result = await api_documenter.generate_openapi_spec(
        api_name="Workflow Test API",
        base_url="https://api.test.com",
        endpoints=endpoints
    )

    assert api_result["success"]


# Error Handling Tests

@pytest.mark.asyncio
async def test_technical_writer_missing_required_fields():
    """Test error handling for missing required fields."""
    writer = TechnicalWriterAgent(api_key="test-key")

    # Missing project_name should still work but with defaults
    result = await writer.execute({
        "doc_type": "readme",
        "project_description": "Test"
    })

    assert result is not None
    assert "success" in result


@pytest.mark.asyncio
async def test_api_documenter_empty_endpoints():
    """Test handling of empty endpoints list."""
    documenter = APIDocumenterAgent(api_key="test-key")

    result = await documenter.execute({
        "doc_type": "openapi",
        "api_name": "Empty API",
        "base_url": "https://api.test.com",
        "endpoints": [],
        "auth_type": "bearer"
    })

    assert result is not None
    assert "success" in result


# Filename Suggestion Tests

@pytest.mark.asyncio
async def test_technical_writer_filename_suggestions(technical_writer):
    """Test filename suggestions for different doc types."""
    assert technical_writer._suggest_filename("readme", "Test") == "README.md"
    assert technical_writer._suggest_filename("changelog", "Test") == "CHANGELOG.md"
    assert "INSTALLATION" in technical_writer._suggest_filename("installation", "Test")
    assert "ARCHITECTURE" in technical_writer._suggest_filename("architecture", "Test")
    assert "adr" in technical_writer._suggest_filename("adr", "Test")


@pytest.mark.asyncio
async def test_api_documenter_filename_suggestions(api_documenter):
    """Test filename suggestions for different API doc types."""
    assert "openapi" in api_documenter._suggest_filename("openapi", "Test API")
    assert "postman" in api_documenter._suggest_filename("postman", "Test API")
    assert "integration-guide" in api_documenter._suggest_filename("integration_guide", "Test API")
    assert "sdk" in api_documenter._suggest_filename("sdk_docs", "Test API")


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
