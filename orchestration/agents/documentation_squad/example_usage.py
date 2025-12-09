"""
Example usage of Documentation Squad agents.

This file demonstrates how to use the Technical Writer and API Documenter agents
to generate various types of documentation.
"""

import asyncio
import os
from technical_writer import TechnicalWriterAgent
from api_documenter import APIDocumenterAgent


async def example_technical_writer():
    """
    Examples for Technical Writer Agent.
    """
    print("=" * 80)
    print("TECHNICAL WRITER AGENT EXAMPLES")
    print("=" * 80)

    # Initialize agent
    api_key = os.getenv("OPENROUTER_API_KEY", "your-api-key-here")
    agent = TechnicalWriterAgent(api_key=api_key)

    # Example 1: Generate README
    print("\n1. Generating README...")
    readme_result = await agent.generate_readme(
        project_name="Devora Orchestration",
        project_description="AI-powered orchestration system for software transformation",
        tech_stack=["Python 3.11+", "FastAPI", "PostgreSQL", "Redis", "OpenRouter API"],
        features=[
            "Multi-agent orchestration with specialized squads",
            "Async task execution and monitoring",
            "Context-aware agents with memory",
            "Extensible plugin architecture",
            "Real-time progress tracking"
        ]
    )

    if readme_result["success"]:
        print(f"✓ README generated ({readme_result['metadata']['word_count']} words)")
        print(f"  Save to: {readme_result['filename']}")
        print(f"\nPreview:\n{readme_result['documentation'][:500]}...\n")
    else:
        print(f"✗ Error: {readme_result['error']}")

    # Example 2: Generate ADR
    print("\n2. Generating Architecture Decision Record...")
    adr_result = await agent.generate_adr(
        project_name="Devora Orchestration",
        decision_context="""
        Decision: Choosing OpenRouter over direct OpenAI integration

        Context:
        - Need to support multiple LLM providers (OpenAI, Anthropic, etc.)
        - Want to avoid vendor lock-in
        - Need flexible model selection
        - Want unified API for multiple providers

        Options considered:
        1. Direct OpenAI API integration
        2. LangChain for abstraction
        3. OpenRouter for unified access

        Requirements:
        - Support for GPT-4, Claude, and other models
        - Simple API integration
        - Cost-effective routing
        - Easy model switching
        """,
        tech_stack=["OpenRouter API", "httpx", "asyncio"]
    )

    if adr_result["success"]:
        print(f"✓ ADR generated")
        print(f"  Save to: {adr_result['filename']}")
    else:
        print(f"✗ Error: {adr_result['error']}")

    # Example 3: Generate Installation Guide
    print("\n3. Generating Installation Guide...")
    install_result = await agent.generate_installation_guide(
        project_name="Devora Orchestration",
        project_description="Complete setup guide for the orchestration system",
        tech_stack=["Python 3.11+", "PostgreSQL 15+", "Redis 7+", "Docker"],
        requirements=[
            "Python 3.11 or higher",
            "PostgreSQL 15 or higher",
            "Redis 7+",
            "Docker and Docker Compose (optional)",
            "OpenRouter API key",
            "At least 4GB RAM",
            "10GB disk space"
        ]
    )

    if install_result["success"]:
        print(f"✓ Installation guide generated")
        print(f"  Save to: {install_result['filename']}")
    else:
        print(f"✗ Error: {install_result['error']}")

    # Example 4: Generate Architecture Documentation
    print("\n4. Generating Architecture Documentation...")
    arch_result = await agent.generate_architecture_docs(
        project_name="Devora Orchestration",
        architecture_details="""
        The system uses a microservices-inspired architecture with:

        Frontend:
        - Next.js 14 with App Router
        - TailwindCSS + shadcn/ui
        - Real-time updates via WebSockets
        - State management with Zustand

        Backend:
        - FastAPI for REST API
        - PostgreSQL for persistent data
        - Redis for caching and pub/sub
        - Background task queue with Celery

        Orchestration Layer:
        - Multi-agent system with specialized squads
        - Async task execution
        - Context-aware agents with memory
        - LLM integration via OpenRouter

        Infrastructure:
        - Docker containers for services
        - Nginx reverse proxy
        - Let's Encrypt for SSL
        - Cloudflare for CDN and DDoS protection

        External Services:
        - OpenRouter for LLM access
        - Supabase for additional database features
        - Stripe for payments
        - Sentry for error tracking
        """,
        tech_stack=["FastAPI", "Next.js", "PostgreSQL", "Redis", "Docker", "OpenRouter"]
    )

    if arch_result["success"]:
        print(f"✓ Architecture documentation generated")
        print(f"  Save to: {arch_result['filename']}")
    else:
        print(f"✗ Error: {arch_result['error']}")

    # Example 5: Generate Changelog
    print("\n5. Generating Changelog...")
    changelog_result = await agent.generate_changelog(
        project_name="Devora Orchestration",
        version="1.2.0",
        changes={
            "added": [
                "Documentation Squad with Technical Writer and API Documenter agents",
                "Async task execution support",
                "Real-time progress tracking via WebSockets",
                "Multi-agent collaboration workflows"
            ],
            "changed": [
                "Improved agent memory management",
                "Updated OpenRouter API integration",
                "Enhanced error handling and retry logic",
                "Optimized database query performance"
            ],
            "fixed": [
                "Memory leak in long-running agent tasks",
                "Race condition in concurrent agent execution",
                "WebSocket connection stability issues",
                "Incorrect error propagation in nested workflows"
            ],
            "security": [
                "Updated dependencies with security patches",
                "Added rate limiting to API endpoints",
                "Improved API key validation"
            ]
        }
    )

    if changelog_result["success"]:
        print(f"✓ Changelog entry generated")
        print(f"  Save to: {changelog_result['filename']}")
    else:
        print(f"✗ Error: {changelog_result['error']}")


async def example_api_documenter():
    """
    Examples for API Documenter Agent.
    """
    print("\n" + "=" * 80)
    print("API DOCUMENTER AGENT EXAMPLES")
    print("=" * 80)

    # Initialize agent
    api_key = os.getenv("OPENROUTER_API_KEY", "your-api-key-here")
    agent = APIDocumenterAgent(api_key=api_key)

    # Define sample API endpoints
    endpoints = [
        {
            "path": "/agents",
            "method": "GET",
            "summary": "List all agents",
            "description": "Retrieve a paginated list of available agents",
            "tags": ["Agents"],
            "parameters": [
                {
                    "name": "squad",
                    "in": "query",
                    "description": "Filter by squad name",
                    "schema": {"type": "string"}
                },
                {
                    "name": "page",
                    "in": "query",
                    "description": "Page number",
                    "schema": {"type": "integer", "default": 1}
                },
                {
                    "name": "limit",
                    "in": "query",
                    "description": "Items per page",
                    "schema": {"type": "integer", "default": 20, "maximum": 100}
                }
            ],
            "responses": {
                "200": {
                    "description": "Success",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "data": {
                                        "type": "array",
                                        "items": {"$ref": "#/components/schemas/Agent"}
                                    },
                                    "pagination": {"$ref": "#/components/schemas/Pagination"}
                                }
                            }
                        }
                    }
                }
            }
        },
        {
            "path": "/agents/{agent_id}",
            "method": "GET",
            "summary": "Get agent details",
            "description": "Retrieve detailed information about a specific agent",
            "tags": ["Agents"],
            "parameters": [
                {
                    "name": "agent_id",
                    "in": "path",
                    "required": True,
                    "description": "Agent ID",
                    "schema": {"type": "string"}
                }
            ],
            "responses": {
                "200": {
                    "description": "Success",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Agent"}
                        }
                    }
                },
                "404": {
                    "description": "Agent not found"
                }
            }
        },
        {
            "path": "/tasks",
            "method": "POST",
            "summary": "Create a new task",
            "description": "Submit a new task for agent execution",
            "tags": ["Tasks"],
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "required": ["agent_id", "context"],
                            "properties": {
                                "agent_id": {
                                    "type": "string",
                                    "description": "ID of the agent to execute the task"
                                },
                                "context": {
                                    "type": "object",
                                    "description": "Task context and parameters"
                                },
                                "priority": {
                                    "type": "string",
                                    "enum": ["low", "normal", "high"],
                                    "default": "normal"
                                }
                            }
                        }
                    }
                }
            },
            "responses": {
                "201": {
                    "description": "Task created",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Task"}
                        }
                    }
                }
            }
        },
        {
            "path": "/tasks/{task_id}",
            "method": "GET",
            "summary": "Get task status",
            "description": "Retrieve the current status and result of a task",
            "tags": ["Tasks"],
            "parameters": [
                {
                    "name": "task_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"}
                }
            ],
            "responses": {
                "200": {
                    "description": "Success",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Task"}
                        }
                    }
                }
            }
        }
    ]

    # Example 1: Generate OpenAPI Specification
    print("\n1. Generating OpenAPI Specification...")
    openapi_result = await agent.generate_openapi_spec(
        api_name="Devora Orchestration API",
        base_url="https://api.devora.ai/v1",
        endpoints=endpoints,
        auth_type="bearer",
        version="1.0.0"
    )

    if openapi_result["success"]:
        print(f"✓ OpenAPI spec generated")
        print(f"  Save to: {openapi_result['filename']}")
        print(f"  Endpoints documented: {openapi_result['metadata']['endpoint_count']}")
    else:
        print(f"✗ Error: {openapi_result['error']}")

    # Example 2: Generate Postman Collection
    print("\n2. Generating Postman Collection...")
    postman_result = await agent.generate_postman_collection(
        api_name="Devora Orchestration API",
        base_url="https://api.devora.ai/v1",
        endpoints=endpoints,
        auth_type="bearer"
    )

    if postman_result["success"]:
        print(f"✓ Postman collection generated")
        print(f"  Save to: {postman_result['filename']}")
        print(f"  Import this into Postman to test the API")
    else:
        print(f"✗ Error: {postman_result['error']}")

    # Example 3: Generate Integration Guide
    print("\n3. Generating Integration Guide...")
    guide_result = await agent.generate_integration_guide(
        api_name="Devora Orchestration API",
        base_url="https://api.devora.ai/v1",
        endpoints=endpoints,
        auth_type="bearer"
    )

    if guide_result["success"]:
        print(f"✓ Integration guide generated")
        print(f"  Save to: {guide_result['filename']}")
    else:
        print(f"✗ Error: {guide_result['error']}")

    # Example 4: Generate SDK Documentation (JavaScript)
    print("\n4. Generating SDK Documentation (JavaScript)...")
    sdk_js_result = await agent.generate_sdk_documentation(
        api_name="Devora Orchestration API",
        language="javascript",
        base_url="https://api.devora.ai/v1",
        endpoints=endpoints,
        auth_type="bearer"
    )

    if sdk_js_result["success"]:
        print(f"✓ JavaScript SDK documentation generated")
        print(f"  Save to: {sdk_js_result['filename']}")
    else:
        print(f"✗ Error: {sdk_js_result['error']}")

    # Example 5: Generate SDK Documentation (Python)
    print("\n5. Generating SDK Documentation (Python)...")
    sdk_py_result = await agent.generate_sdk_documentation(
        api_name="Devora Orchestration API",
        language="python",
        base_url="https://api.devora.ai/v1",
        endpoints=endpoints,
        auth_type="bearer"
    )

    if sdk_py_result["success"]:
        print(f"✓ Python SDK documentation generated")
        print(f"  Save to: {sdk_py_result['filename']}")
    else:
        print(f"✗ Error: {sdk_py_result['error']}")


async def example_custom_documentation():
    """
    Example of using the execute() method directly for custom documentation.
    """
    print("\n" + "=" * 80)
    print("CUSTOM DOCUMENTATION EXAMPLES")
    print("=" * 80)

    api_key = os.getenv("OPENROUTER_API_KEY", "your-api-key-here")
    writer = TechnicalWriterAgent(api_key=api_key)

    # Custom README with specific settings
    print("\n1. Custom README generation...")
    result = await writer.execute({
        "doc_type": "readme",
        "project_name": "Custom Microservice",
        "project_description": "A specialized microservice for data processing",
        "tech_stack": ["Python 3.11", "FastAPI", "Celery", "Redis"],
        "features": [
            "Asynchronous task processing",
            "Real-time monitoring dashboard",
            "Automatic scaling based on load"
        ],
        "audience": "backend developers",
        "include_diagrams": True,
        "version": "2.0.0"
    })

    if result["success"]:
        print(f"✓ Custom README generated")
        print(f"  Word count: {result['metadata']['word_count']}")
        print(f"  Includes diagrams: {result['metadata']['includes_diagrams']}")
    else:
        print(f"✗ Error: {result['error']}")


async def main():
    """
    Run all examples.
    """
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "DOCUMENTATION SQUAD EXAMPLES" + " " * 30 + "║")
    print("╚" + "=" * 78 + "╝")

    # Check for API key
    if not os.getenv("OPENROUTER_API_KEY"):
        print("\n⚠ Warning: OPENROUTER_API_KEY environment variable not set!")
        print("  Set it with: export OPENROUTER_API_KEY='your-key-here'")
        print("  Examples will use placeholder API key.\n")

    try:
        # Run Technical Writer examples
        await example_technical_writer()

        # Run API Documenter examples
        await example_api_documenter()

        # Run custom documentation examples
        await example_custom_documentation()

        print("\n" + "=" * 80)
        print("ALL EXAMPLES COMPLETED")
        print("=" * 80)
        print("\nNext steps:")
        print("1. Review the generated documentation")
        print("2. Save outputs to appropriate files")
        print("3. Integrate into your documentation workflow")
        print("4. Customize prompts and templates as needed")
        print()

    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user.")
    except Exception as e:
        print(f"\n\n✗ Error running examples: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
