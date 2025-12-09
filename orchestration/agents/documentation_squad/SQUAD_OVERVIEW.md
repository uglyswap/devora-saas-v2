# Documentation Squad - Technical Overview

## Project Structure

```
documentation_squad/
├── __init__.py                          # Squad module exports and metadata (2.8 KB)
├── technical_writer.py                  # Technical Writer Agent (19 KB)
├── api_documenter.py                    # API Documenter Agent (22 KB)
├── example_usage.py                     # Usage examples and demos (7.7 KB)
├── test_documentation_squad.py          # Unit tests (16 KB)
├── README.md                            # User documentation (9.4 KB)
└── SQUAD_OVERVIEW.md                    # This file
```

**Total Code**: ~77 KB of professional Python code and documentation

## Agents Overview

### 1. TechnicalWriterAgent (`technical_writer.py`)

**Class**: `TechnicalWriterAgent(BaseAgent)`

**Purpose**: Generate comprehensive technical documentation for software projects.

**Key Features**:
- README generation with shields, badges, and proper structure
- Architecture Decision Records (ADRs) following standard templates
- Installation guides with platform-specific instructions
- System architecture documentation with Mermaid diagrams
- Template-based generation for consistency
- Filename suggestions for proper documentation structure

**Methods**:
```python
# Main methods
validate_input(input_data) -> bool
execute(input_data, **kwargs) -> Dict[str, Any]
format_output(raw_output) -> Dict[str, Any]

# Helper methods
generate_readme(project_name, context, tech_stack=None)
generate_adr(project_name, decision_context, tech_stack=None)
generate_installation_guide(project_name, context, tech_stack=None)
generate_architecture_docs(project_name, context, tech_stack=None)
```

**Documentation Types**:
- `readme`: Complete README.md with all sections
- `adr`: Architecture Decision Record
- `installation`: Installation and setup guide
- `architecture`: System architecture documentation
- `custom`: Custom documentation format

**Templates**:
- Pre-built templates for each documentation type
- Markdown formatting with proper structure
- Mermaid diagram support
- Code blocks with syntax highlighting

### 2. APIDocumenterAgent (`api_documenter.py`)

**Class**: `APIDocumenterAgent(BaseAgent)`

**Purpose**: Create comprehensive API documentation and specifications.

**Key Features**:
- OpenAPI 3.0+ specification generation (YAML/JSON)
- Postman Collection v2.1 creation
- GraphQL schema documentation
- REST API endpoint documentation
- SDK usage guides for multiple languages
- Integration tutorials with code examples
- Authentication flow documentation

**Methods**:
```python
# Main methods
validate_input(input_data) -> bool
execute(input_data, **kwargs) -> Dict[str, Any]
format_output(raw_output) -> Dict[str, Any]

# Helper methods
generate_openapi_spec(api_name, api_details, base_url, auth_type, version)
generate_postman_collection(api_name, api_details, base_url, auth_type)
generate_integration_guide(api_name, api_details, base_url, auth_type)
generate_sdk_documentation(api_name, api_details, language, base_url, auth_type)
```

**Documentation Types**:
- `openapi`: OpenAPI 3.0 specification
- `postman`: Postman Collection v2.1
- `integration_guide`: API integration tutorial
- `sdk_docs`: SDK documentation for specific language
- `graphql`: GraphQL schema and operations

**Templates**:
- OpenAPI 3.0 YAML/JSON structure
- Postman Collection v2.1 format
- Integration guide structure
- SDK documentation template

## Technical Architecture

### Inheritance Structure

```
BaseAgent (from core.base_agent)
    ├── TechnicalWriterAgent
    └── APIDocumenterAgent
```

### Base Agent Features (Inherited)

Both agents inherit from `BaseAgent` which provides:

- **LLM Integration**: OpenRouter API connection for multiple models
- **Logging**: Comprehensive logging with configurable levels
- **Metrics Tracking**: Token usage, execution time, retry counts
- **Error Handling**: Retry logic with exponential backoff
- **Callbacks**: Progress notification system
- **Validation**: Input validation framework
- **Configuration**: Flexible agent configuration

### Agent Lifecycle

```
1. Initialization
   └── AgentConfig setup
   └── Template loading
   └── Logger configuration

2. Input Validation
   └── validate_input()
   └── Check required fields
   └── Validate doc_type

3. Execution
   └── Build prompt from template
   └── Call LLM via OpenRouter
   └── Process response

4. Output Formatting
   └── format_output()
   └── Extract structured content
   └── Suggest filenames
   └── Package metadata

5. Return
   └── Success/failure status
   └── Generated content
   └── Execution metrics
```

## Configuration

### AgentConfig Parameters

```python
AgentConfig(
    name="AgentName",                    # Agent identifier
    model="anthropic/claude-3.5-sonnet", # LLM model
    api_key="your-openrouter-key",      # API key
    temperature=0.7,                     # Creativity (0.0-1.0)
    max_tokens=4096,                     # Max response tokens
    timeout=60,                          # Request timeout (seconds)
    max_retries=3,                       # Retry attempts
    log_level="INFO"                     # Logging level
)
```

### Supported Models (via OpenRouter)

- `anthropic/claude-3.5-sonnet` ⭐ Recommended
- `anthropic/claude-opus-4.5` (Most capable)
- `openai/gpt-4o`
- `openai/gpt-4-turbo`
- `google/gemini-pro-1.5`
- `meta-llama/llama-3.1-70b-instruct`

## Input/Output Specifications

### TechnicalWriterAgent Input

```python
{
    "doc_type": "readme",        # Required: Type of documentation
    "context": "...",            # Required: Project context
    "project_name": "Project",   # Optional: Project name
    "tech_stack": ["Python"],    # Optional: Technologies
    "audience": "developers",    # Optional: Target audience
    "include_diagrams": true     # Optional: Include Mermaid diagrams
}
```

### TechnicalWriterAgent Output

```python
{
    "status": "success",
    "output": {
        "content": "# README...",
        "metadata": {
            "type": "readme",
            "project": "Project",
            "details": {...}
        },
        "file_suggestions": {
            "primary": "README.md",
            "alternative": "docs/readme.md"
        }
    },
    "metrics": {
        "total_tokens": 1500,
        "execution_time": 5.2
    },
    "agent": "TechnicalWriter",
    "timestamp": "2025-12-09T03:30:00"
}
```

### APIDocumenterAgent Input

```python
{
    "doc_type": "openapi",       # Required: Type of API docs
    "api_details": "...",        # Required: API specifications
    "api_name": "API",           # Optional: API name
    "base_url": "https://...",   # Optional: Base URL
    "auth_type": "bearer",       # Optional: Auth type
    "version": "1.0.0",          # Optional: API version
    "language": "javascript"     # Optional: For SDK docs
}
```

### APIDocumenterAgent Output

```python
{
    "status": "success",
    "output": {
        "content": "openapi: 3.0.0...",
        "structured_content": {...},  # Parsed JSON if applicable
        "metadata": {
            "type": "openapi",
            "api": "API",
            "details": {...}
        },
        "file_suggestions": {
            "primary": "docs/api/openapi-api.yaml",
            "alternative": "docs/openapi-api.yaml"
        }
    },
    "metrics": {...},
    "agent": "APIDocumenter",
    "timestamp": "2025-12-09T03:30:00"
}
```

## Usage Examples

### Example 1: Generate README

```python
from orchestration.core.base_agent import AgentConfig
from orchestration.agents.documentation_squad import TechnicalWriterAgent

config = AgentConfig(
    name="TechnicalWriter",
    model="anthropic/claude-3.5-sonnet",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

agent = TechnicalWriterAgent(config)

result = agent.generate_readme(
    project_name="My Project",
    context="A web application for task management",
    tech_stack=["Python", "FastAPI", "PostgreSQL", "React"]
)

print(result["output"]["content"])
```

### Example 2: Generate OpenAPI Spec

```python
from orchestration.core.base_agent import AgentConfig
from orchestration.agents.documentation_squad import APIDocumenterAgent

config = AgentConfig(
    name="APIDocumenter",
    model="anthropic/claude-3.5-sonnet",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

agent = APIDocumenterAgent(config)

result = agent.generate_openapi_spec(
    api_name="Task Management API",
    api_details="""
    GET /api/v1/tasks - List all tasks
    POST /api/v1/tasks - Create a new task
    GET /api/v1/tasks/{id} - Get task by ID
    PUT /api/v1/tasks/{id} - Update task
    DELETE /api/v1/tasks/{id} - Delete task
    """,
    base_url="https://api.example.com",
    auth_type="bearer",
    version="1.0.0"
)

# Save to file
with open("openapi.yaml", "w") as f:
    f.write(result["output"]["content"])
```

### Example 3: Using the Run Method

```python
# Using the full run() method for complete lifecycle
result = agent.run({
    "doc_type": "adr",
    "context": "Decision to use microservices architecture",
    "project_name": "My Project"
})

if result["status"] == "success":
    content = result["output"]["content"]
    metrics = result["metrics"]
    print(f"Generated in {metrics['execution_time']:.2f}s")
    print(f"Used {metrics['total_tokens']} tokens")
else:
    print(f"Error: {result['error']}")
```

## Testing

### Unit Tests

The `test_documentation_squad.py` file contains comprehensive unit tests:

**Test Coverage**:
- Agent initialization
- Input validation (valid and invalid cases)
- Prompt building for all documentation types
- Filename suggestions
- Output formatting
- Mocked LLM execution
- Module imports and integration

**Test Classes**:
- `TestTechnicalWriterAgent`: 15+ test cases
- `TestAPIDocumenterAgent`: 15+ test cases
- `TestDocumentationSquadIntegration`: Squad-level tests

**Running Tests**:
```bash
# With pytest (if installed)
pytest test_documentation_squad.py -v

# With unittest
python test_documentation_squad.py
```

### Manual Testing

Use `example_usage.py` for manual testing:

```bash
export OPENROUTER_API_KEY='your-key'
python example_usage.py
```

## Module Exports

The `__init__.py` file provides:

```python
# Agent classes
from documentation_squad import TechnicalWriterAgent, APIDocumenterAgent

# Utility functions
from documentation_squad import (
    get_squad_info,    # Get squad metadata
    list_agents,       # List available agents
    get_agent_class    # Get agent class by name
)

# Constants
from documentation_squad import (
    SQUAD_NAME,
    SQUAD_DESCRIPTION,
    SQUAD_AGENTS
)
```

## Error Handling

### Common Errors

1. **Invalid doc_type**
   - Error: `ValueError: Invalid doc_type`
   - Solution: Use valid types from documentation

2. **Missing required fields**
   - Error: `ValueError: Missing required field: context`
   - Solution: Provide all required fields

3. **API Key issues**
   - Error: `ValueError: OpenRouter API key is required`
   - Solution: Set `OPENROUTER_API_KEY` environment variable

4. **Token limit exceeded**
   - Error: Rate limit or token limit
   - Solution: Increase `max_tokens` or reduce input size

### Error Response Format

```python
{
    "status": "failed",
    "error": "Error message",
    "metrics": {...},
    "agent": "AgentName",
    "timestamp": "2025-12-09T03:30:00"
}
```

## Performance Metrics

### Typical Metrics (Claude 3.5 Sonnet)

| Task | Tokens | Time | Cost (est.) |
|------|--------|------|-------------|
| README (small) | 800-1200 | 3-5s | $0.02-0.03 |
| README (large) | 2000-3000 | 8-12s | $0.05-0.08 |
| ADR | 1000-1500 | 4-6s | $0.03-0.04 |
| OpenAPI spec | 1500-2500 | 6-10s | $0.04-0.06 |
| Integration guide | 2500-4000 | 10-15s | $0.06-0.10 |

*Note: Costs are estimates based on OpenRouter pricing*

## Best Practices

### For TechnicalWriterAgent

1. **Provide Context**: Detailed project description yields better docs
2. **Specify Tech Stack**: Helps generate accurate technical content
3. **Define Audience**: Clarify who will read the documentation
4. **Enable Diagrams**: Use Mermaid diagrams for architecture docs
5. **Review Output**: Always review and customize generated content

### For APIDocumenterAgent

1. **Complete Endpoint List**: Include all endpoints with methods
2. **Specify Auth Flow**: Clearly document authentication
3. **Provide Examples**: Include request/response examples
4. **Version Properly**: Use semantic versioning
5. **Validate Output**: Test OpenAPI specs with validators

## Integration with Devora System

### Squad Registration

The Documentation Squad integrates with the Devora orchestration system:

```python
# In orchestration system
from agents.documentation_squad import get_squad_info, get_agent_class

squad_info = get_squad_info()
print(f"Squad: {squad_info['name']}")
print(f"Agents: {', '.join(squad_info['agents'])}")

# Instantiate agent dynamically
TechWriterClass = get_agent_class("technical_writer")
agent = TechWriterClass(config)
```

### Orchestration Workflow

```python
# Example orchestration workflow
def generate_project_documentation(project_data):
    # 1. Generate README
    readme = technical_writer.generate_readme(...)

    # 2. Generate API docs
    api_spec = api_documenter.generate_openapi_spec(...)

    # 3. Generate integration guide
    guide = api_documenter.generate_integration_guide(...)

    return {
        "readme": readme,
        "api_spec": api_spec,
        "guide": guide
    }
```

## Future Enhancements

### Planned Features

1. **Multi-language support**: Generate docs in multiple languages
2. **Diagram generation**: Auto-generate architecture diagrams
3. **Version diffing**: Compare documentation versions
4. **Template customization**: User-defined templates
5. **Batch processing**: Generate multiple docs in one call
6. **PDF export**: Convert markdown to PDF
7. **Interactive docs**: Generate interactive API documentation

### Potential Improvements

- Caching of similar requests
- Incremental documentation updates
- Integration with Git for versioning
- Automated documentation publishing
- Code-to-docs synchronization
- Documentation quality scoring

## Contributing

To add new documentation types:

1. Add template method in agent class
2. Update `_build_prompt()` method
3. Add to valid types in `validate_input()`
4. Update tests
5. Update documentation

## Support and Resources

- **Main Documentation**: `README.md`
- **Examples**: `example_usage.py`
- **Tests**: `test_documentation_squad.py`
- **Base Agent**: `../../core/base_agent.py`
- **Devora System**: `../../README.md`

## License

Part of the Devora Transformation Orchestration System.

---

**Documentation Squad** - Making documentation generation effortless with AI
