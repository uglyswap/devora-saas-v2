# Documentation Squad

Professional technical and API documentation generation for the Devora transformation orchestration system.

## Overview

The Documentation Squad provides world-class documentation generation capabilities including technical documentation (README, ADRs, architecture docs), API documentation (OpenAPI, Postman), and developer guides.

## Agents

### 1. Technical Writer Agent

Generates comprehensive technical documentation following industry best practices.

**Capabilities:**
- Professional README generation with badges and Table of Contents
- Architecture Decision Records (ADRs) following MADR format
- Multi-platform installation guides (macOS, Linux, Windows)
- System architecture documentation with Mermaid diagrams
- Changelog generation following Keep a Changelog
- Troubleshooting guides and FAQ sections
- Contributing guidelines

**Output Formats:**
- `README.md` - Project overview with complete documentation
- `docs/adr/ADR-XXX-title.md` - Architecture Decision Records
- `docs/INSTALLATION.md` - Installation guide
- `docs/ARCHITECTURE.md` - Architecture documentation
- `CHANGELOG.md` - Version history

### 2. API Documenter Agent

Creates comprehensive API documentation and specifications.

**Capabilities:**
- OpenAPI 3.0+ specification generation
- Postman Collection v2.1 creation with examples and tests
- GraphQL schema documentation
- Multi-language integration guides (JavaScript, Python, Go, cURL)
- SDK documentation with code examples
- Authentication flow documentation (OAuth2, JWT, API Keys)
- Rate limiting and error handling guides
- Webhook documentation

**Output Formats:**
- `docs/api/openapi-*.yaml` - OpenAPI specification
- `docs/api/*-postman-collection.json` - Postman collection
- `docs/api/integration-guide.md` - Integration guide
- `docs/api/sdk-docs.md` - SDK documentation
- `docs/api/graphql-schema.md` - GraphQL documentation

## Installation

```bash
# The agents are part of the orchestration system
cd orchestration/agents/documentation_squad
```

## Usage

### Technical Writer Agent

```python
import asyncio
from documentation_squad import TechnicalWriterAgent

async def main():
    # Initialize agent
    agent = TechnicalWriterAgent(api_key="your-openrouter-api-key")

    # Generate README
    result = await agent.generate_readme(
        project_name="My Awesome Project",
        project_description="A revolutionary tool for developers",
        tech_stack=["Python", "FastAPI", "PostgreSQL"],
        features=[
            "Real-time collaboration",
            "Advanced analytics",
            "Secure authentication"
        ]
    )

    print(result["documentation"])
    print(f"Save to: {result['filename']}")

    # Generate ADR
    adr_result = await agent.generate_adr(
        project_name="My Project",
        decision_context="""
        We need to choose a database for our application.
        Requirements: ACID compliance, good performance, PostgreSQL compatibility.
        Options: PostgreSQL, MySQL, MongoDB.
        """,
        tech_stack=["PostgreSQL", "SQLAlchemy"]
    )

    print(adr_result["documentation"])

    # Generate Installation Guide
    install_result = await agent.generate_installation_guide(
        project_name="My Project",
        project_description="Complete installation guide",
        tech_stack=["Python 3.11+", "PostgreSQL 15+", "Redis"],
        requirements=[
            "Python 3.11 or higher",
            "PostgreSQL 15 or higher",
            "Redis 7+",
            "Docker (optional)"
        ]
    )

    # Generate Architecture Documentation
    arch_result = await agent.generate_architecture_docs(
        project_name="My Project",
        architecture_details="""
        System uses microservices architecture with:
        - API Gateway (FastAPI)
        - Authentication Service
        - Business Logic Services
        - PostgreSQL database
        - Redis cache
        - Message queue (RabbitMQ)
        """,
        tech_stack=["FastAPI", "PostgreSQL", "Redis", "RabbitMQ"]
    )

    # Generate Changelog
    changelog_result = await agent.generate_changelog(
        project_name="My Project",
        version="1.2.0",
        changes={
            "added": [
                "New authentication flow with OAuth2",
                "Real-time notifications via WebSockets"
            ],
            "changed": [
                "Improved database query performance",
                "Updated API response format"
            ],
            "fixed": [
                "Memory leak in background tasks",
                "Race condition in user registration"
            ],
            "security": [
                "Updated dependencies with security patches"
            ]
        }
    )

if __name__ == "__main__":
    asyncio.run(main())
```

### API Documenter Agent

```python
import asyncio
from documentation_squad import APIDocumenterAgent

async def main():
    # Initialize agent
    agent = APIDocumenterAgent(api_key="your-openrouter-api-key")

    # Define API endpoints
    endpoints = [
        {
            "path": "/users",
            "method": "GET",
            "summary": "List users",
            "description": "Retrieve a paginated list of users",
            "parameters": [
                {"name": "page", "in": "query", "type": "integer"},
                {"name": "limit", "in": "query", "type": "integer"}
            ],
            "responses": {
                "200": {
                    "description": "Success",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "data": {"type": "array"},
                            "pagination": {"type": "object"}
                        }
                    }
                }
            }
        },
        {
            "path": "/users/{id}",
            "method": "GET",
            "summary": "Get user",
            "description": "Retrieve a single user by ID",
            "parameters": [
                {"name": "id", "in": "path", "type": "string", "required": True}
            ]
        },
        {
            "path": "/users",
            "method": "POST",
            "summary": "Create user",
            "description": "Create a new user",
            "requestBody": {
                "required": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string"},
                        "name": {"type": "string"}
                    }
                }
            }
        }
    ]

    # Generate OpenAPI Specification
    openapi_result = await agent.generate_openapi_spec(
        api_name="My API",
        base_url="https://api.example.com/v1",
        endpoints=endpoints,
        auth_type="bearer",
        version="1.0.0"
    )

    print(openapi_result["documentation"])
    print(f"Save to: {openapi_result['filename']}")

    # Generate Postman Collection
    postman_result = await agent.generate_postman_collection(
        api_name="My API",
        base_url="https://api.example.com/v1",
        endpoints=endpoints,
        auth_type="bearer"
    )

    # Generate Integration Guide
    guide_result = await agent.generate_integration_guide(
        api_name="My API",
        base_url="https://api.example.com/v1",
        endpoints=endpoints,
        auth_type="bearer"
    )

    # Generate SDK Documentation (JavaScript)
    sdk_js_result = await agent.generate_sdk_documentation(
        api_name="My API",
        language="javascript",
        base_url="https://api.example.com/v1",
        endpoints=endpoints,
        auth_type="bearer"
    )

    # Generate SDK Documentation (Python)
    sdk_py_result = await agent.generate_sdk_documentation(
        api_name="My API",
        language="python",
        base_url="https://api.example.com/v1",
        endpoints=endpoints,
        auth_type="bearer"
    )

if __name__ == "__main__":
    asyncio.run(main())
```

### Using execute() Method Directly

Both agents support the `execute()` method for more control:

```python
import asyncio
from documentation_squad import TechnicalWriterAgent, APIDocumenterAgent

async def main():
    writer = TechnicalWriterAgent(api_key="your-api-key")

    # Custom documentation generation
    result = await writer.execute({
        "doc_type": "readme",
        "project_name": "Custom Project",
        "project_description": "Detailed description",
        "tech_stack": ["Python", "FastAPI"],
        "features": ["Feature 1", "Feature 2"],
        "audience": "developers",
        "include_diagrams": True
    })

    if result["success"]:
        print("Documentation generated successfully!")
        print(result["documentation"])
        print(f"Metadata: {result['metadata']}")
    else:
        print(f"Error: {result['error']}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Documentation Types Supported

### Technical Writer

| Type | Description | Output File |
|------|-------------|-------------|
| `readme` | Project README with badges, TOC, examples | `README.md` |
| `adr` | Architecture Decision Record (MADR format) | `docs/adr/ADR-*.md` |
| `installation` | Multi-platform installation guide | `docs/INSTALLATION.md` |
| `architecture` | System architecture with diagrams | `docs/ARCHITECTURE.md` |
| `changelog` | Version changelog (Keep a Changelog) | `CHANGELOG.md` |

### API Documenter

| Type | Description | Output File |
|------|-------------|-------------|
| `openapi` | OpenAPI 3.0+ specification | `docs/api/openapi-*.yaml` |
| `postman` | Postman Collection v2.1 | `docs/api/*-collection.json` |
| `integration_guide` | API integration guide with examples | `docs/api/integration-guide.md` |
| `sdk_docs` | SDK documentation for specific language | `docs/api/sdk-*.md` |
| `graphql` | GraphQL schema documentation | `docs/api/graphql-*.md` |

## Standards Followed

### Technical Documentation
- **Keep a Changelog**: Changelog formatting and versioning
- **Semantic Versioning**: Version number conventions
- **MADR**: Markdown Any Decision Records for ADRs
- **README Best Practices**: Shields/badges, clear structure, examples

### API Documentation
- **OpenAPI 3.0+**: Complete API specification standard
- **Postman Collection v2.1**: Standard collection format
- **JSON Schema**: Data model validation schemas
- **REST Best Practices**: HTTP methods, status codes, resource naming
- **GraphQL SDL**: Schema Definition Language

## Features

### Technical Writer Features
- Automatic badge/shield generation
- Mermaid diagram creation
- Multi-platform instructions
- Code syntax highlighting
- Table of contents generation
- Cross-referencing
- Version-aware documentation

### API Documenter Features
- Complete OpenAPI schemas
- Multi-language code examples
- Authentication flow diagrams
- Error code documentation
- Rate limiting guides
- Pagination examples
- Webhook documentation
- SDK code generation

## Configuration Options

### Technical Writer

```python
context = {
    "doc_type": "readme",           # Type of documentation
    "project_name": "Project",       # Project name
    "project_description": "Desc",   # Brief description
    "tech_stack": ["Python"],        # Technologies used
    "features": ["Feature 1"],       # Key features (optional)
    "requirements": ["Req 1"],       # Installation requirements (optional)
    "architecture_details": "...",   # Architecture info (optional)
    "decision_context": "...",       # ADR context (optional)
    "version": "1.0.0",             # Version number (optional)
    "changes": {...},               # Changelog changes (optional)
    "audience": "developers",        # Target audience
    "include_diagrams": True         # Include Mermaid diagrams
}
```

### API Documenter

```python
context = {
    "doc_type": "openapi",          # Type of documentation
    "api_name": "API",              # API name
    "base_url": "https://...",      # Base URL
    "endpoints": [...],             # Endpoint definitions
    "auth_type": "bearer",          # Authentication type
    "version": "1.0.0",            # API version
    "language": "javascript",       # Language for SDK docs
    "include_examples": True,       # Include code examples
    "data_models": [...]           # Data model schemas (optional)
}
```

## Best Practices

### Technical Documentation
1. **Clear Structure**: Use consistent heading hierarchy
2. **Code Examples**: Provide working, testable examples
3. **Visual Aids**: Include diagrams for complex concepts
4. **Progressive Disclosure**: Simple examples first, advanced later
5. **Keep Updated**: Sync documentation with code changes

### API Documentation
1. **Complete Specs**: Document all endpoints, parameters, responses
2. **Real Examples**: Use realistic data in examples
3. **Error Handling**: Document all error codes and scenarios
4. **Authentication**: Clearly explain auth flows
5. **Versioning**: Maintain docs for each API version

## Integration with Devora Orchestration

These agents can be integrated into larger workflows:

```python
from orchestration.core.orchestrator import Orchestrator
from documentation_squad import TechnicalWriterAgent, APIDocumenterAgent

async def documentation_workflow():
    orchestrator = Orchestrator(api_key="your-key")

    # Register agents
    writer = TechnicalWriterAgent(api_key="your-key")
    api_doc = APIDocumenterAgent(api_key="your-key")

    # Create workflow
    workflow = [
        {
            "agent": writer,
            "task": {
                "doc_type": "readme",
                "project_name": "My Project",
                # ... other params
            }
        },
        {
            "agent": api_doc,
            "task": {
                "doc_type": "openapi",
                "api_name": "My API",
                # ... other params
            }
        }
    ]

    # Execute workflow
    results = await orchestrator.execute_workflow(workflow)
    return results
```

## Support

For issues, questions, or contributions related to the Documentation Squad:

1. Check existing documentation in `docs/`
2. Review example usage in `example_usage.py`
3. Run tests in `test_documentation_squad.py`
4. Contact the development team

## License

Part of the Devora transformation orchestration system.
