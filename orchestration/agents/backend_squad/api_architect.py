"""
API Architect Agent - Designs REST/GraphQL APIs with OpenAPI documentation.

This agent specializes in:
- API architecture and design patterns
- OpenAPI/Swagger documentation generation
- Pydantic/Zod schema validation
- API versioning strategies
- RESTful and GraphQL best practices
"""

from typing import Dict, Any, List
import json
import logging

# Import base agent from backend
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../backend'))
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class APIArchitect(BaseAgent):
    """Agent specialized in API architecture and design.

    Responsibilities:
    - Design RESTful API endpoints and structure
    - Generate GraphQL schemas and resolvers
    - Create OpenAPI/Swagger documentation
    - Define request/response validation schemas (Pydantic for Python, Zod for TypeScript)
    - Plan API versioning strategy
    - Design authentication and authorization flows
    - Define rate limiting and caching strategies

    Tech Stack:
    - OpenAPI 3.1 specification
    - Pydantic v2 (Python validation)
    - Zod (TypeScript validation)
    - GraphQL Schema Language
    - JSON Schema
    - FastAPI / Next.js API Routes
    """

    def __init__(self, api_key: str, model: str = "openai/gpt-4o"):
        """Initialize the API Architect agent.

        Args:
            api_key: OpenRouter API key for LLM calls
            model: LLM model to use (default: GPT-4o)
        """
        super().__init__("APIArchitect", api_key, model)
        self.logger = logger

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute API architecture design task.

        Args:
            task: Dictionary containing:
                - requirements: List of functional requirements
                - data_models: List of data model definitions
                - api_type: "rest" or "graphql"
                - auth_type: "jwt", "oauth2", "api_key", etc.
                - versioning: Boolean for API versioning

        Returns:
            Dictionary containing:
                - success: Boolean indicating completion
                - api_spec: OpenAPI specification or GraphQL schema
                - schemas: List of validation schemas (Pydantic/Zod)
                - endpoints: List of endpoint definitions
                - documentation: API documentation
        """
        requirements = task.get("requirements", [])
        data_models = task.get("data_models", [])
        api_type = task.get("api_type", "rest")
        auth_type = task.get("auth_type", "jwt")
        versioning = task.get("versioning", True)

        system_prompt = """You are an expert API architect with deep knowledge of RESTful and GraphQL API design.

## Your Expertise:
- API design patterns (REST, GraphQL, RPC)
- OpenAPI/Swagger 3.1 specification
- API versioning strategies (URI, Header, Content negotiation)
- Authentication flows (JWT, OAuth2, API Keys)
- Rate limiting and throttling
- Caching strategies (ETags, Cache-Control)
- Pagination patterns (offset, cursor, page-based)
- Error handling and status codes
- API documentation best practices

## Output Requirements:

### For REST APIs:
1. **OpenAPI 3.1 Specification** - Complete spec with:
   - All endpoints with HTTP methods
   - Request/response schemas
   - Authentication/security schemes
   - Error responses
   - Examples for each endpoint

2. **Validation Schemas** - Pydantic models (Python) or Zod schemas (TypeScript):
   - Input validation models
   - Response models
   - Reusable components

3. **Endpoint Documentation** - For each endpoint:
   - Purpose and description
   - Request parameters (path, query, body)
   - Response format and status codes
   - Authentication requirements
   - Rate limits
   - Example requests/responses

### For GraphQL APIs:
1. **GraphQL Schema** - Complete schema with:
   - Type definitions
   - Queries
   - Mutations
   - Subscriptions (if needed)
   - Input types
   - Enums and interfaces

2. **Resolver Structure** - Outline of resolver functions
3. **Documentation** - Query/mutation examples

## Best Practices to Follow:
- Use consistent naming conventions (camelCase for JSON, snake_case for Python)
- Implement proper HTTP status codes
- Design idempotent operations where appropriate
- Include pagination for list endpoints
- Implement filtering, sorting, and searching
- Use HATEOAS principles for discoverability
- Version APIs from the start
- Include comprehensive error responses
- Design with security in mind
- Optimize for performance (caching, compression)

## Security Considerations:
- Authentication on all protected endpoints
- Input validation on all requests
- Rate limiting to prevent abuse
- CORS configuration
- SQL injection prevention
- XSS protection
- CSRF tokens for state-changing operations

## Output Format:
Return a JSON structure with:
```json
{
  "api_type": "rest" | "graphql",
  "openapi_spec": { ... },  // For REST
  "graphql_schema": "...",  // For GraphQL
  "schemas": [
    {
      "name": "UserCreateSchema",
      "language": "python" | "typescript",
      "content": "..."
    }
  ],
  "endpoints": [
    {
      "path": "/api/v1/users",
      "method": "POST",
      "description": "...",
      "auth_required": true,
      "rate_limit": "100/hour",
      "request_schema": "UserCreateSchema",
      "response_schema": "UserResponse"
    }
  ],
  "versioning_strategy": "...",
  "authentication_flow": "...",
  "documentation": "..."
}
```
"""

        context = f"""## Project Requirements:
{json.dumps(requirements, indent=2)}

## Data Models:
{json.dumps(data_models, indent=2)}

## API Configuration:
- Type: {api_type.upper()}
- Authentication: {auth_type.upper()}
- Versioning: {"Enabled" if versioning else "Disabled"}

---
Design a complete API architecture that:
1. Covers all functional requirements
2. Follows REST/GraphQL best practices
3. Includes comprehensive validation schemas
4. Provides clear documentation
5. Implements security best practices
6. Optimizes for scalability and performance

Generate the complete API specification with all schemas and documentation.
"""

        messages = [{"role": "user", "content": context}]

        self.logger.info(f"[{self.name}] Designing {api_type.upper()} API architecture...")

        response = await self.call_llm(messages, system_prompt)

        # Parse the response
        api_spec = self._parse_api_specification(response)

        self.logger.info(f"[{self.name}] API design complete: {len(api_spec.get('endpoints', []))} endpoints")

        return {
            "success": True,
            "api_spec": api_spec,
            "schemas": api_spec.get("schemas", []),
            "endpoints": api_spec.get("endpoints", []),
            "documentation": api_spec.get("documentation", ""),
            "raw_response": response
        }

    async def generate_openapi_spec(self, endpoints: List[Dict[str, Any]],
                                   schemas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate OpenAPI 3.1 specification from endpoints and schemas.

        Args:
            endpoints: List of endpoint definitions
            schemas: List of data schemas

        Returns:
            Complete OpenAPI 3.1 specification
        """
        system_prompt = """Generate a complete OpenAPI 3.1 specification.

Include:
- info section with API details
- servers configuration
- paths with all operations
- components/schemas with reusable schemas
- security schemes
- tags for organization

Follow OpenAPI 3.1 specification exactly."""

        context = f"""## Endpoints:
{json.dumps(endpoints, indent=2)}

## Schemas:
{json.dumps(schemas, indent=2)}

Generate complete OpenAPI 3.1 spec in JSON format.
"""

        messages = [{"role": "user", "content": context}]
        response = await self.call_llm(messages, system_prompt)

        try:
            # Extract JSON from response
            spec = self._extract_json(response)
            return spec
        except Exception as e:
            self.logger.error(f"Failed to parse OpenAPI spec: {e}")
            return {"error": str(e)}

    async def generate_validation_schemas(self, data_models: List[Dict[str, Any]],
                                         language: str = "python") -> List[Dict[str, str]]:
        """Generate validation schemas (Pydantic or Zod).

        Args:
            data_models: List of data model definitions
            language: "python" (Pydantic) or "typescript" (Zod)

        Returns:
            List of schema files with content
        """
        system_prompt = f"""Generate validation schemas using {'Pydantic v2' if language == 'python' else 'Zod'}.

{'For Pydantic:' if language == 'python' else 'For Zod:'}
{'- Use BaseModel with Field validators' if language == 'python' else '- Use z.object() with proper types'}
{'- Include field descriptions and constraints' if language == 'python' else '- Include .describe() for documentation'}
{'- Use proper type hints' if language == 'python' else '- Use TypeScript types'}
{'- Implement custom validators where needed' if language == 'python' else '- Implement .refine() for custom validation'}
- Create both input and output schemas
- Include examples in docstrings

Output format:
```{'python' if language == 'python' else 'typescript'}
// filepath: schemas/[name].{'py' if language == 'python' else 'ts'}
[complete code]
```
"""

        context = f"""## Data Models:
{json.dumps(data_models, indent=2)}

Generate validation schemas for each model in {language}.
"""

        messages = [{"role": "user", "content": context}]
        response = await self.call_llm(messages, system_prompt)

        # Parse code blocks
        schemas = self._parse_code_blocks(response)

        self.logger.info(f"Generated {len(schemas)} validation schema(s)")

        return schemas

    async def design_versioning_strategy(self, api_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Design API versioning strategy.

        Args:
            api_spec: Current API specification

        Returns:
            Versioning strategy documentation and implementation guide
        """
        system_prompt = """Design a comprehensive API versioning strategy.

Consider:
1. Versioning method (URI, Header, Content-Type)
2. Deprecation policy
3. Migration paths
4. Breaking vs non-breaking changes
5. Documentation for each version
6. Backwards compatibility

Provide:
- Recommended versioning approach with justification
- Implementation examples
- Migration guide template
- Deprecation timeline
"""

        context = f"""## Current API Spec:
{json.dumps(api_spec, indent=2)}

Design the versioning strategy for this API.
"""

        messages = [{"role": "user", "content": context}]
        response = await self.call_llm(messages, system_prompt)

        return {
            "success": True,
            "strategy": response
        }

    def _parse_api_specification(self, response: str) -> Dict[str, Any]:
        """Parse API specification from LLM response.

        Args:
            response: Raw LLM response

        Returns:
            Parsed API specification
        """
        try:
            # Try to extract JSON
            spec = self._extract_json(response)
            return spec
        except Exception as e:
            self.logger.warning(f"Failed to parse as JSON, using raw response: {e}")
            return {
                "raw_content": response,
                "endpoints": [],
                "schemas": [],
                "documentation": response
            }

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Extract JSON from text that might contain markdown code blocks.

        Args:
            text: Text potentially containing JSON

        Returns:
            Parsed JSON object
        """
        import re

        # Try to find JSON in code blocks
        json_pattern = r'```(?:json)?\s*(\{[\s\S]*?\})\s*```'
        matches = re.findall(json_pattern, text)

        if matches:
            return json.loads(matches[0])

        # Try to parse entire text as JSON
        return json.loads(text)

    def _parse_code_blocks(self, response: str) -> List[Dict[str, str]]:
        """Parse code blocks with filepath comments.

        Args:
            response: LLM response containing code blocks

        Returns:
            List of files with name, content, and language
        """
        import re

        files = []

        # Pattern to match code blocks with optional filepath
        pattern = r'```(\w+)?\n(?:(?://|#)\s*filepath:\s*(.+?)\n)?([\s\S]*?)```'

        matches = re.findall(pattern, response)

        for match in matches:
            language, filepath, code = match
            code = code.strip()

            if not code:
                continue

            if filepath:
                filepath = filepath.strip()
            else:
                # Try to extract from first line of code
                first_line = code.split('\n')[0] if code else ''
                if 'filepath:' in first_line.lower():
                    filepath = first_line.split('filepath:')[1].strip()
                    code = '\n'.join(code.split('\n')[1:])  # Remove filepath line
                else:
                    filepath = f"schema_{len(files)}.{language or 'txt'}"

            if not language:
                # Infer from filepath
                if filepath.endswith('.py'):
                    language = 'python'
                elif filepath.endswith('.ts'):
                    language = 'typescript'
                else:
                    language = 'text'

            files.append({
                "name": filepath,
                "content": code,
                "language": language
            })

        return files
