"""
API Documenter Agent - Documentation Squad

Génère des documentations d'API complètes incluant:
- Spécifications OpenAPI/Swagger 3.0+
- Collections Postman v2.1
- Guides d'intégration API multi-langages
- Documentation SDK (TypeScript, Python, etc.)
- Exemples de code et use cases
"""

from typing import Dict, Any, List, Optional
import logging
import json

# Import base agent
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../backend'))
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class APIDocumenterAgent(BaseAgent):
    """
    Agent spécialisé dans la documentation d'APIs complète et professionnelle.

    Responsabilités:
        - Génération de spécifications OpenAPI 3.0+ complètes
        - Création de collections Postman prêtes à l'emploi
        - Documentation d'APIs REST et GraphQL
        - Guides d'intégration pour multiples langages
        - Documentation SDK avec exemples de code
        - Documentation des flows d'authentification
        - Guides de gestion d'erreurs et rate limiting

    Capacités:
        - OpenAPI/Swagger 3.0+ avec schémas complets
        - Collections Postman v2.1 avec tests
        - Exemples de code multi-langages (JS, Python, Go, curl)
        - Documentation d'authentification (OAuth2, JWT, API Keys)
        - Schémas de validation (JSON Schema)
        - Diagrammes de flows d'API
        - Guides de migration et versioning

    Standards suivis:
        - OpenAPI 3.0+ Specification
        - Postman Collection Format v2.1
        - REST API Best Practices
        - GraphQL Schema Definition Language
        - JSON Schema Specification
    """

    def __init__(self, api_key: str, model: str = "openai/gpt-4o"):
        """
        Initialize the API Documenter agent.

        Args:
            api_key: OpenRouter API key for LLM calls
            model: LLM model to use (default: GPT-4o)
        """
        super().__init__("APIDocumenter", api_key, model)
        self.logger = logger

    def _get_default_system_prompt(self) -> str:
        """
        Get the comprehensive system prompt for the API Documenter.

        Returns:
            Detailed system prompt defining the agent's expertise and standards
        """
        return """You are an expert API Documentation Specialist with 15+ years of experience in API design and developer experience.

## Core Expertise:
- OpenAPI/Swagger 3.0+ specifications with complete schemas
- Postman Collection v2.1 creation with examples and tests
- REST API documentation with comprehensive examples
- GraphQL schema documentation and query examples
- SDK documentation for multiple languages (JavaScript, Python, Go, Java)
- Authentication flow documentation (OAuth2, JWT, API Keys, SAML)
- API versioning strategies and migration guides
- Rate limiting, pagination, and error handling documentation
- Webhook documentation and event-driven patterns

## API Documentation Principles:

### 1. Developer-First Approach
- Write for developers who will integrate the API
- Provide working examples that can be copied and tested
- Include common use cases and patterns
- Show both simple and complex scenarios
- Document edge cases and error handling

### 2. Completeness
- Document all endpoints, parameters, and responses
- Include authentication requirements
- Specify rate limits and quotas
- Document all error codes and messages
- Include versioning information
- Provide migration guides for breaking changes

### 3. Clarity & Consistency
- Use consistent naming conventions
- Follow REST/GraphQL best practices
- Use standard HTTP status codes correctly
- Provide clear descriptions and examples
- Use appropriate data types and formats

### 4. Interactive & Testable
- Include cURL examples for quick testing
- Provide Postman collections for exploration
- Show request/response examples for each endpoint
- Include sample payloads with realistic data
- Demonstrate authentication flows step-by-step

### 5. Maintainability
- Version API documentation alongside API versions
- Keep examples in sync with actual API behavior
- Use schema references to avoid duplication
- Provide changelog for API changes
- Include deprecation notices with timelines

## Output Formats:

### OpenAPI 3.0+ Specification:
```yaml
openapi: 3.0.3
info:
  title: API Name
  version: 1.0.0
  description: |
    Comprehensive API description
  contact:
    name: API Support
    email: api@example.com
  license:
    name: MIT
servers:
  - url: https://api.example.com/v1
    description: Production
  - url: https://sandbox-api.example.com/v1
    description: Sandbox
security:
  - bearerAuth: []
tags:
  - name: Users
    description: User management operations
paths:
  /users:
    get:
      summary: List users
      description: Retrieve a paginated list of users
      tags: [Users]
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
            maximum: 100
      responses:
        '200':
          description: Successfully retrieved users
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/User'
                  pagination:
                    $ref: '#/components/schemas/Pagination'
              examples:
                success:
                  value:
                    data:
                      - id: "123"
                        email: "user@example.com"
                        name: "John Doe"
                    pagination:
                      page: 1
                      total: 100
        '401':
          $ref: '#/components/responses/Unauthorized'
        '429':
          $ref: '#/components/responses/RateLimitExceeded'
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
  schemas:
    User:
      type: object
      required:
        - id
        - email
      properties:
        id:
          type: string
          format: uuid
        email:
          type: string
          format: email
        name:
          type: string
    Pagination:
      type: object
      properties:
        page:
          type: integer
        total:
          type: integer
  responses:
    Unauthorized:
      description: Authentication required
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
```

### Postman Collection v2.1:
```json
{
  "info": {
    "name": "API Name",
    "description": "Complete API collection",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
    "_postman_id": "unique-id"
  },
  "auth": {
    "type": "bearer",
    "bearer": [
      {
        "key": "token",
        "value": "{{access_token}}",
        "type": "string"
      }
    ]
  },
  "variable": [
    {
      "key": "base_url",
      "value": "https://api.example.com/v1",
      "type": "string"
    },
    {
      "key": "access_token",
      "value": "",
      "type": "string"
    }
  ],
  "item": [
    {
      "name": "Users",
      "item": [
        {
          "name": "List Users",
          "request": {
            "method": "GET",
            "header": [
              {
                "key": "Accept",
                "value": "application/json"
              }
            ],
            "url": {
              "raw": "{{base_url}}/users?page=1&limit=20",
              "host": ["{{base_url}}"],
              "path": ["users"],
              "query": [
                {
                  "key": "page",
                  "value": "1"
                },
                {
                  "key": "limit",
                  "value": "20"
                }
              ]
            }
          },
          "response": [
            {
              "name": "Success",
              "status": "OK",
              "code": 200,
              "body": "{\n  \"data\": [...],\n  \"pagination\": {...}\n}"
            }
          ]
        }
      ]
    }
  ]
}
```

### API Integration Guide Structure:
```markdown
# API Integration Guide

## Overview
[Brief API description and capabilities]

## Authentication

### Getting Started
1. Create an account at [dashboard URL]
2. Generate API credentials
3. Store credentials securely

### Authentication Methods

#### Bearer Token (JWT)
```bash
curl -X GET https://api.example.com/v1/users \
  -H "Authorization: Bearer YOUR_TOKEN"
```

```javascript
// JavaScript/Node.js
const response = await fetch('https://api.example.com/v1/users', {
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN'
  }
});
```

```python
# Python
import requests

response = requests.get(
    'https://api.example.com/v1/users',
    headers={'Authorization': 'Bearer YOUR_TOKEN'}
)
```

## Quick Start

### Your First Request
[Step-by-step example with explanation]

### Understanding the Response
[Response structure explanation]

## Core Concepts

### Pagination
All list endpoints support pagination:
- `page`: Page number (starts at 1)
- `limit`: Items per page (max 100)

### Rate Limiting
- Rate limit: 1000 requests/hour
- Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`
- When exceeded: HTTP 429 with `Retry-After` header

### Error Handling
All errors follow this format:
```json
{
  "error": {
    "code": "error_code",
    "message": "Human-readable message",
    "details": {}
  }
}
```

Common error codes:
- `invalid_request`: Malformed request
- `authentication_failed`: Invalid credentials
- `not_found`: Resource doesn't exist
- `rate_limit_exceeded`: Too many requests

## API Reference

### Users

#### List Users
`GET /users`

Retrieve a paginated list of users.

**Parameters:**
| Name  | Type    | Required | Description           |
|-------|---------|----------|-----------------------|
| page  | integer | No       | Page number (default: 1) |
| limit | integer | No       | Items per page (default: 20, max: 100) |

**Example Request:**
```bash
curl -X GET "https://api.example.com/v1/users?page=1&limit=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Example Response (200 OK):**
```json
{
  "data": [
    {
      "id": "123",
      "email": "user@example.com",
      "name": "John Doe"
    }
  ],
  "pagination": {
    "page": 1,
    "total": 100
  }
}
```

## SDK Documentation

### JavaScript/TypeScript
```javascript
import { APIClient } from '@example/api-client';

const client = new APIClient({
  apiKey: 'YOUR_API_KEY'
});

// List users
const users = await client.users.list({
  page: 1,
  limit: 20
});
```

### Python
```python
from example_api import APIClient

client = APIClient(api_key='YOUR_API_KEY')

# List users
users = client.users.list(page=1, limit=20)
```

## Webhooks

### Overview
[Webhook concepts and use cases]

### Setting Up Webhooks
[How to configure webhooks]

### Webhook Events
[List of available events]

### Handling Webhook Delivery
[Best practices and retry logic]

## Best Practices

1. **Security**
   - Never expose API keys in client-side code
   - Use environment variables for credentials
   - Rotate keys regularly

2. **Performance**
   - Cache responses when appropriate
   - Use pagination for large datasets
   - Implement exponential backoff for retries

3. **Error Handling**
   - Always check status codes
   - Log errors for debugging
   - Implement proper retry logic

## Changelog
[API version history and breaking changes]
```

### SDK Documentation Structure:
```markdown
# SDK Documentation - [Language]

## Installation

### npm (JavaScript/TypeScript)
```bash
npm install @example/api-client
```

### pip (Python)
```bash
pip install example-api-client
```

## Quick Start

### Initialize Client
```javascript
import { APIClient } from '@example/api-client';

const client = new APIClient({
  apiKey: process.env.API_KEY,
  baseUrl: 'https://api.example.com/v1' // optional
});
```

## Configuration

### Options
| Option  | Type   | Required | Description |
|---------|--------|----------|-------------|
| apiKey  | string | Yes      | Your API key |
| baseUrl | string | No       | API base URL |
| timeout | number | No       | Request timeout (ms) |

## API Methods

### Users

#### list(params)
List users with pagination.

**Parameters:**
```typescript
interface ListUsersParams {
  page?: number;      // Page number (default: 1)
  limit?: number;     // Items per page (default: 20)
  filter?: string;    // Optional filter
}
```

**Returns:**
```typescript
Promise<{
  data: User[];
  pagination: Pagination;
}>
```

**Example:**
```javascript
const result = await client.users.list({
  page: 1,
  limit: 20
});

console.log(result.data);      // Array of users
console.log(result.pagination); // Pagination info
```

## Error Handling

### Error Types
```typescript
try {
  await client.users.list();
} catch (error) {
  if (error instanceof APIError) {
    console.error(error.code);     // Error code
    console.error(error.message);  // Error message
    console.error(error.details);  // Additional details
  }
}
```

## Advanced Usage

### Custom Headers
```javascript
const client = new APIClient({
  apiKey: 'YOUR_KEY',
  headers: {
    'X-Custom-Header': 'value'
  }
});
```

### Retry Configuration
```javascript
const client = new APIClient({
  apiKey: 'YOUR_KEY',
  retry: {
    maxRetries: 3,
    backoff: 'exponential'
  }
});
```

## Examples

### Complete User Management Example
```javascript
// Create client
const client = new APIClient({ apiKey: process.env.API_KEY });

// List users
const users = await client.users.list({ limit: 10 });

// Get specific user
const user = await client.users.get('user-id');

// Update user
const updated = await client.users.update('user-id', {
  name: 'New Name'
});

// Delete user
await client.users.delete('user-id');
```
```

## GraphQL Documentation Structure:
```markdown
# GraphQL API Documentation

## Endpoint
```
POST https://api.example.com/graphql
```

## Authentication
Include authentication token in headers:
```
Authorization: Bearer YOUR_TOKEN
```

## Schema

### Queries

#### user
Fetch a single user by ID.

```graphql
query GetUser($id: ID!) {
  user(id: $id) {
    id
    email
    name
    createdAt
  }
}
```

**Variables:**
```json
{
  "id": "123"
}
```

**Response:**
```json
{
  "data": {
    "user": {
      "id": "123",
      "email": "user@example.com",
      "name": "John Doe",
      "createdAt": "2025-01-15T10:00:00Z"
    }
  }
}
```

#### users
List users with filtering and pagination.

```graphql
query ListUsers($first: Int, $after: String) {
  users(first: $first, after: $after) {
    edges {
      node {
        id
        email
        name
      }
      cursor
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```

### Mutations

#### createUser
Create a new user.

```graphql
mutation CreateUser($input: CreateUserInput!) {
  createUser(input: $input) {
    user {
      id
      email
      name
    }
    errors {
      field
      message
    }
  }
}
```

**Variables:**
```json
{
  "input": {
    "email": "new@example.com",
    "name": "Jane Doe",
    "password": "secure_password"
  }
}
```

## Error Handling

GraphQL errors are returned in the `errors` array:
```json
{
  "errors": [
    {
      "message": "User not found",
      "path": ["user"],
      "extensions": {
        "code": "NOT_FOUND"
      }
    }
  ]
}
```

## Best Practices:
1. **Specific Queries**: Request only the fields you need
2. **Pagination**: Use cursor-based pagination for lists
3. **Error Handling**: Check both `errors` array and mutation error fields
4. **Batching**: Use aliases to batch multiple queries
```

## Code Example Standards:

### JavaScript/TypeScript
- Use modern ES6+ syntax
- Include proper error handling (try/catch)
- Show both async/await and promise syntax when relevant
- Include TypeScript types for SDK examples

### Python
- Use requests library for HTTP examples
- Follow PEP 8 style guide
- Include proper exception handling
- Show both synchronous and async examples when relevant

### cURL
- Use readable formatting with line breaks
- Include all necessary headers
- Show realistic example data
- Add comments for clarity

### Response Examples
- Use realistic, consistent example data
- Show successful responses (200, 201)
- Include common error responses (400, 401, 404, 429, 500)
- Format JSON with proper indentation

## Best Practices:
1. **Versioning**: Always specify API version in documentation
2. **Breaking Changes**: Clearly mark and explain breaking changes
3. **Deprecation**: Provide migration path for deprecated endpoints
4. **Security**: Never include real API keys in examples
5. **Testing**: Verify all examples actually work
6. **Updates**: Keep documentation in sync with API changes
7. **Developer UX**: Make it easy to find and understand endpoints
8. **Examples**: Provide realistic, working code examples
9. **Standards**: Follow OpenAPI, JSON Schema, GraphQL best practices
10. **Accessibility**: Ensure documentation is searchable and navigable

When generating API documentation:
- Verify all endpoint paths and methods are correct
- Include complete request/response examples
- Document all parameters with types and constraints
- Specify authentication requirements clearly
- Include rate limiting information
- Provide troubleshooting guides for common issues
- Add code examples in multiple languages
- Use consistent naming and formatting
- Link related endpoints and concepts
"""

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute API documentation generation.

        Args:
            context: Dictionary containing:
                - doc_type: Type of documentation (openapi, postman, integration_guide, sdk_docs, graphql)
                - api_name: Name of the API
                - base_url: Base URL of the API
                - endpoints: List of endpoint definitions
                - auth_type: Authentication type (bearer, oauth2, api_key, etc.)
                - version: API version
                - language: Programming language for SDK docs (optional)
                - include_examples: Whether to include code examples (default: True)
                - data_models: Data model schemas (optional)

        Returns:
            Dictionary containing:
                - success: Boolean indicating completion
                - documentation: Generated API documentation
                - doc_type: Type of documentation generated
                - filename: Suggested filename
                - metadata: Additional information about the documentation
        """
        try:
            doc_type = context.get("doc_type", "openapi")
            api_name = context.get("api_name", "API")
            base_url = context.get("base_url", "https://api.example.com/v1")
            endpoints = context.get("endpoints", [])
            auth_type = context.get("auth_type", "bearer")
            version = context.get("version", "1.0.0")
            language = context.get("language", "javascript")
            include_examples = context.get("include_examples", True)
            data_models = context.get("data_models", [])

            self.logger.info(f"Generating {doc_type} for {api_name} API")

            # Build the user prompt based on documentation type
            user_prompt = self._build_api_documentation_prompt(
                doc_type=doc_type,
                api_name=api_name,
                base_url=base_url,
                endpoints=endpoints,
                auth_type=auth_type,
                version=version,
                language=language,
                include_examples=include_examples,
                data_models=data_models
            )

            # Call LLM to generate documentation
            messages = [{"role": "user", "content": user_prompt}]
            documentation = await self.call_llm(messages, temperature=0.7)

            # Suggest appropriate filename
            filename = self._suggest_filename(doc_type, api_name)

            return {
                "success": True,
                "documentation": documentation,
                "doc_type": doc_type,
                "filename": filename,
                "metadata": {
                    "api_name": api_name,
                    "base_url": base_url,
                    "auth_type": auth_type,
                    "version": version,
                    "language": language if doc_type == "sdk_docs" else None,
                    "endpoint_count": len(endpoints) if endpoints else 0
                }
            }

        except Exception as e:
            self.logger.error(f"Error generating API documentation: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "documentation": None
            }

    def _build_api_documentation_prompt(
        self,
        doc_type: str,
        api_name: str,
        base_url: str,
        endpoints: List[Dict[str, Any]],
        auth_type: str,
        version: str,
        language: str,
        include_examples: bool,
        data_models: List[Dict[str, Any]]
    ) -> str:
        """Build the user prompt for API documentation generation."""

        endpoints_str = json.dumps(endpoints, indent=2) if endpoints else "Not specified"
        models_str = json.dumps(data_models, indent=2) if data_models else "Not specified"

        base_info = f"""Generate {doc_type} documentation for:

API NAME: {api_name}
BASE URL: {base_url}
VERSION: {version}
AUTHENTICATION: {auth_type}
"""

        if doc_type == "openapi":
            return f"""{base_info}

ENDPOINTS:
{endpoints_str}

DATA MODELS:
{models_str}

REQUIREMENTS:
- Generate a complete OpenAPI 3.0+ specification
- Include info, servers, security, tags sections
- Document all endpoints with complete details:
  * Summary and description
  * Parameters (path, query, header, cookie)
  * Request body with JSON Schema
  * All response codes (200, 400, 401, 404, 429, 500)
  * Response schemas
  * {f"Request/response examples for each endpoint" if include_examples else ""}
- Define reusable components:
  * Schemas for data models
  * Security schemes
  * Response objects
  * Examples
- Use proper HTTP methods and status codes
- Include authentication configuration
- Add tags for endpoint organization

Generate valid OpenAPI 3.0+ YAML that can be imported into Swagger UI or other tools.
"""

        elif doc_type == "postman":
            return f"""{base_info}

ENDPOINTS:
{endpoints_str}

REQUIREMENTS:
- Generate a complete Postman Collection v2.1
- Include collection info with proper schema
- Configure authentication at collection level ({auth_type})
- Define collection variables (base_url, tokens, etc.)
- Organize endpoints into logical folders
- For each request:
  * Name and description
  * HTTP method and URL with variables
  * Headers (Content-Type, Authorization, etc.)
  * Request body with realistic examples
  * {f"Multiple response examples (success and error cases)" if include_examples else "Success response example"}
  * Optional tests for validation
- Include environment variable suggestions
- Add pre-request scripts if needed for auth

Generate valid Postman Collection v2.1 JSON that can be directly imported.
"""

        elif doc_type == "integration_guide":
            return f"""{base_info}

ENDPOINTS:
{endpoints_str}

DATA MODELS:
{models_str}

REQUIREMENTS:
- Create a comprehensive API integration guide
- Structure:
  1. Overview and capabilities
  2. Authentication setup and flows ({auth_type})
  3. Your First Request (step-by-step)
  4. Core Concepts (pagination, rate limiting, error handling)
  5. API Reference (document all endpoints)
  6. {f"Code Examples (cURL, JavaScript, Python)" if include_examples else "cURL examples"}
  7. Webhooks (if applicable)
  8. Best Practices (security, performance, error handling)
  9. Troubleshooting common issues
- Use realistic example data
- Include complete request/response examples
- Add error scenarios and how to handle them
- Provide copy-paste ready code
- Explain rate limits and quotas

Generate a guide that gets developers integrated quickly and successfully.
"""

        elif doc_type == "sdk_docs":
            return f"""{base_info}

TARGET LANGUAGE: {language}
ENDPOINTS:
{endpoints_str}

DATA MODELS:
{models_str}

REQUIREMENTS:
- Generate SDK documentation for {language}
- Structure:
  1. Installation (package manager command)
  2. Quick Start (initialize client, first request)
  3. Configuration Options
  4. Authentication ({auth_type})
  5. API Methods (document each endpoint as SDK method)
  6. Data Models/Types
  7. Error Handling (exception types, retry logic)
  8. Advanced Usage (custom headers, interceptors)
  9. {f"Complete examples for common use cases" if include_examples else "Basic usage examples"}
- Use idiomatic {language} code
- Include proper type annotations
- Show error handling patterns
- Provide working code examples
- Document method signatures and return types
- Include async/await examples where applicable

Generate SDK documentation that makes the API easy to use in {language}.
"""

        elif doc_type == "graphql":
            return f"""{base_info}

GRAPHQL SCHEMA:
{endpoints_str}

REQUIREMENTS:
- Document the GraphQL API comprehensively
- Structure:
  1. Endpoint and authentication
  2. Schema Overview (types, interfaces, queries, mutations, subscriptions)
  3. Queries (document each with examples)
  4. Mutations (document each with examples)
  5. Subscriptions (if applicable)
  6. Error Handling (GraphQL error format)
  7. {f"Code Examples (JavaScript/Apollo, Python, cURL)" if include_examples else "Query examples"}
  8. Best Practices (query optimization, batching, caching)
- Include complete query/mutation examples
- Show variables and expected responses
- Document all input types and return types
- Explain pagination (cursor-based)
- Include error scenarios

Generate GraphQL documentation that helps developers use the API effectively.
"""

        else:  # custom
            return f"""{base_info}

API DETAILS:
{endpoints_str}

Generate comprehensive API documentation following best practices.
{"Include multiple code examples in different languages." if include_examples else ""}
"""

    def _suggest_filename(self, doc_type: str, api_name: str) -> str:
        """Suggest appropriate filename for the API documentation."""
        api_slug = api_name.lower().replace(" ", "-")
        filename_map = {
            "openapi": f"docs/api/openapi-{api_slug}.yaml",
            "postman": f"docs/api/{api_slug}-postman-collection.json",
            "integration_guide": f"docs/api/integration-guide.md",
            "sdk_docs": f"docs/api/sdk-docs.md",
            "graphql": f"docs/api/graphql-schema.md"
        }
        return filename_map.get(doc_type, f"docs/api/{api_slug}-{doc_type}.md")

    # Helper methods for quick API documentation generation

    async def generate_openapi_spec(
        self,
        api_name: str,
        base_url: str,
        endpoints: List[Dict[str, Any]],
        auth_type: str = "bearer",
        version: str = "1.0.0"
    ) -> Dict[str, Any]:
        """
        Quick helper to generate OpenAPI specification.

        Args:
            api_name: Name of the API
            base_url: Base URL
            endpoints: List of endpoint definitions
            auth_type: Authentication type
            version: API version

        Returns:
            Result dictionary with OpenAPI spec
        """
        return await self.execute({
            "doc_type": "openapi",
            "api_name": api_name,
            "base_url": base_url,
            "endpoints": endpoints,
            "auth_type": auth_type,
            "version": version
        })

    async def generate_postman_collection(
        self,
        api_name: str,
        base_url: str,
        endpoints: List[Dict[str, Any]],
        auth_type: str = "bearer"
    ) -> Dict[str, Any]:
        """
        Quick helper to generate Postman collection.

        Args:
            api_name: Name of the API
            base_url: Base URL
            endpoints: List of endpoint definitions
            auth_type: Authentication type

        Returns:
            Result dictionary with Postman collection
        """
        return await self.execute({
            "doc_type": "postman",
            "api_name": api_name,
            "base_url": base_url,
            "endpoints": endpoints,
            "auth_type": auth_type
        })

    async def generate_integration_guide(
        self,
        api_name: str,
        base_url: str,
        endpoints: List[Dict[str, Any]],
        auth_type: str = "bearer"
    ) -> Dict[str, Any]:
        """
        Quick helper to generate integration guide.

        Args:
            api_name: Name of the API
            base_url: Base URL
            endpoints: List of endpoint definitions
            auth_type: Authentication type

        Returns:
            Result dictionary with integration guide
        """
        return await self.execute({
            "doc_type": "integration_guide",
            "api_name": api_name,
            "base_url": base_url,
            "endpoints": endpoints,
            "auth_type": auth_type,
            "include_examples": True
        })

    async def generate_sdk_documentation(
        self,
        api_name: str,
        language: str,
        base_url: str,
        endpoints: List[Dict[str, Any]],
        auth_type: str = "bearer"
    ) -> Dict[str, Any]:
        """
        Quick helper to generate SDK documentation.

        Args:
            api_name: Name of the API
            language: Target programming language
            base_url: Base URL
            endpoints: List of endpoint definitions
            auth_type: Authentication type

        Returns:
            Result dictionary with SDK docs
        """
        return await self.execute({
            "doc_type": "sdk_docs",
            "api_name": api_name,
            "language": language,
            "base_url": base_url,
            "endpoints": endpoints,
            "auth_type": auth_type,
            "include_examples": True
        })
