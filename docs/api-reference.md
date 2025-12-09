# Devora API Reference

Complete API documentation for Devora's backend services.

## Base URL

```
Production: https://api.devora.app
Development: http://localhost:8000
```

## Authentication

All API requests require an API key in the request body or as a Bearer token.

```bash
# Using request body
curl -X POST https://api.devora.app/api/v3/orchestrate/execute \
  -H "Content-Type: application/json" \
  -d '{"prompt": "...", "api_key": "sk-your-api-key"}'

# Using Bearer token (for protected routes)
curl -X GET https://api.devora.app/api/projects \
  -H "Authorization: Bearer your-jwt-token"
```

---

## Orchestration API V3

The orchestration API handles AI-powered code generation with multi-agent coordination.

### Execute Task (Streaming)

Generate code with real-time SSE streaming.

```http
POST /api/v3/orchestrate/execute
```

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| prompt | string | ✅ | User's request (10-50000 chars) |
| api_key | string | ✅ | OpenRouter API key |
| context | object | ❌ | Additional context |
| files | array | ❌ | Existing project files |
| model | string | ❌ | LLM model (default: claude-3.5-sonnet) |
| priority | string | ❌ | low, medium, high, critical |
| max_iterations | number | ❌ | Max iterations (1-10, default: 3) |
| timeout_seconds | number | ❌ | Timeout (30-1800, default: 300) |
| quality_level | string | ❌ | basic, standard, strict, enterprise |
| enable_quality_gates | boolean | ❌ | Enable quality checks (default: true) |
| auto_fix | boolean | ❌ | Auto-fix issues (default: true) |
| agents_to_use | array | ❌ | Specific agents to use |
| parallel_execution | boolean | ❌ | Run agents in parallel (default: true) |

**Example Request:**

```javascript
const eventSource = new EventSource('/api/v3/orchestrate/execute');

// Send request via fetch first
const response = await fetch('/api/v3/orchestrate/execute', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    prompt: 'Create a React dashboard with charts and navigation',
    api_key: 'sk-your-key',
    quality_level: 'standard',
    max_iterations: 3
  })
});

// Get task ID from headers
const taskId = response.headers.get('X-Task-ID');

// Stream events
const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  const text = decoder.decode(value);
  const lines = text.split('\n');

  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const event = JSON.parse(line.slice(6));
      console.log(event.event_type, event.progress);
    }
  }
}
```

**SSE Event Types:**

| Event Type | Description |
|------------|-------------|
| start | Task started |
| planning | Planning phase began |
| agent_start | An agent started working |
| agent_progress | Agent progress update |
| agent_complete | Agent finished |
| quality_gate | Quality gate check |
| iteration | New iteration started |
| complete | Task completed successfully |
| error | An error occurred |
| end | Stream ended |

**Event Data Structure:**

```typescript
interface ProgressEvent {
  event_type: string;
  phase: string;
  agent?: string;
  message: string;
  progress: number; // 0-100
  data?: any;
  timestamp: string; // ISO 8601
}
```

---

### Execute Task (Async)

Start a task and poll for results.

```http
POST /api/v3/orchestrate/execute/async
```

**Response:**

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "Task queued for execution",
  "poll_url": "/api/v3/orchestrate/status/550e8400-e29b-41d4-a716-446655440000"
}
```

---

### Get Task Status

Check the status of a task.

```http
GET /api/v3/orchestrate/status/{task_id}
```

**Response:**

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "progress": 45.5,
  "current_phase": "frontend_generation",
  "agents_active": ["architect", "frontend"],
  "metrics": {
    "tokens_used": 15000,
    "files_generated": 5
  },
  "result": null,
  "error": null,
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:31:30Z"
}
```

**Status Values:**

| Status | Description |
|--------|-------------|
| pending | Task queued, not started |
| running | Task in progress |
| completed | Task finished successfully |
| failed | Task failed with error |
| cancelled | Task was cancelled |

---

### Cancel Task

Cancel a running or pending task.

```http
POST /api/v3/orchestrate/status/{task_id}/cancel
```

**Response:**

```json
{
  "message": "Task cancelled",
  "task_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

### Quick Generate

Simplified generation with defaults.

```http
POST /api/v3/orchestrate/quick-generate
```

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| prompt | string | ✅ | What to build |
| api_key | string | ✅ | OpenRouter API key |
| template | string | ❌ | Template to use |
| style | string | ❌ | Design style (default: modern) |

**Example:**

```json
{
  "prompt": "A landing page for a SaaS product",
  "api_key": "sk-...",
  "template": "nextjs",
  "style": "minimalist"
}
```

---

### Refine Code

Modify existing code.

```http
POST /api/v3/orchestrate/refine
```

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| files | array | ✅ | Current project files |
| instruction | string | ✅ | What to change |
| api_key | string | ✅ | OpenRouter API key |
| selected_element | object | ❌ | Targeted element |

**Selected Element Structure:**

```json
{
  "selector": "#main-button",
  "xpath": "/html/body/div/button",
  "tag": "button",
  "classes": ["btn", "primary"],
  "id": "main-button",
  "text": "Click me"
}
```

---

### Debug Code

Fix errors in code.

```http
POST /api/v3/orchestrate/debug
```

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| files | array | ✅ | Project files |
| error_message | string | ✅ | Error description |
| api_key | string | ✅ | OpenRouter API key |
| console_logs | array | ❌ | Console output |

---

### List Agents

Get available AI agents.

```http
GET /api/v3/orchestrate/agents
```

**Response:**

```json
{
  "agents": [
    {
      "id": "architect",
      "name": "Architect Agent",
      "description": "Designs system architecture and technical specifications",
      "capabilities": [
        "system_design",
        "technology_selection",
        "file_structure",
        "dependency_management"
      ]
    },
    {
      "id": "frontend",
      "name": "Frontend Agent",
      "description": "Implements UI components and user interactions",
      "capabilities": [
        "react_components",
        "tailwind_styling",
        "responsive_design",
        "accessibility"
      ]
    }
  ]
}
```

---

### List Quality Levels

Get available quality levels.

```http
GET /api/v3/orchestrate/quality-levels
```

**Response:**

```json
{
  "levels": [
    {
      "id": "basic",
      "name": "Basic",
      "description": "Quick validation for prototypes",
      "checks": ["syntax", "basic_structure"]
    },
    {
      "id": "standard",
      "name": "Standard",
      "description": "Recommended for most projects",
      "checks": ["syntax", "types", "linting", "basic_security"]
    },
    {
      "id": "strict",
      "name": "Strict",
      "description": "Thorough checks for production code",
      "checks": ["syntax", "types", "linting", "security_audit", "performance", "accessibility"]
    },
    {
      "id": "enterprise",
      "name": "Enterprise",
      "description": "Maximum quality for enterprise applications",
      "checks": ["syntax", "types", "linting", "security_audit", "performance", "accessibility", "compliance", "documentation"]
    }
  ]
}
```

---

### Get Metrics

Get global orchestration metrics.

```http
GET /api/v3/orchestrate/metrics
```

**Response:**

```json
{
  "total_tasks": 1523,
  "completed": 1420,
  "failed": 45,
  "running": 8,
  "success_rate": 96.9,
  "average_duration_seconds": 35.7
}
```

---

### Health Check

Check API health.

```http
GET /api/v3/orchestrate/health
```

**Response:**

```json
{
  "status": "healthy",
  "version": "3.0.0",
  "tasks_in_memory": 42,
  "timestamp": "2025-01-15T10:30:00Z"
}
```

---

## Projects API

Manage user projects.

### List Projects

```http
GET /api/projects
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| limit | number | Max results (default: 20) |
| offset | number | Pagination offset |
| sort | string | Sort field |
| order | string | asc or desc |

### Get Project

```http
GET /api/projects/{project_id}
```

### Create Project

```http
POST /api/projects
```

**Request Body:**

```json
{
  "name": "My Project",
  "description": "A cool app",
  "template": "react"
}
```

### Update Project

```http
PUT /api/projects/{project_id}
```

### Delete Project

```http
DELETE /api/projects/{project_id}
```

---

## Deployment API

Deploy projects to hosting providers.

### Deploy to Vercel

```http
POST /api/deploy/vercel
```

**Request Body:**

```json
{
  "project_id": "...",
  "token": "vercel-token",
  "project_name": "my-app",
  "framework": "nextjs"
}
```

### Deploy to Netlify

```http
POST /api/deploy/netlify
```

### Deploy to Cloudflare

```http
POST /api/deploy/cloudflare
```

### Get Deployment Status

```http
GET /api/deploy/{deployment_id}/status
```

---

## Error Handling

All errors follow this format:

```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {}
}
```

**Common Error Codes:**

| Code | HTTP Status | Description |
|------|-------------|-------------|
| UNAUTHORIZED | 401 | Invalid or missing API key |
| FORBIDDEN | 403 | Insufficient permissions |
| NOT_FOUND | 404 | Resource not found |
| VALIDATION_ERROR | 422 | Invalid request body |
| RATE_LIMITED | 429 | Too many requests |
| INTERNAL_ERROR | 500 | Server error |

---

## Rate Limits

| Endpoint | Limit | Window |
|----------|-------|--------|
| /execute | 10 | 1 minute |
| /quick-generate | 30 | 1 minute |
| /refine | 20 | 1 minute |
| Others | 100 | 1 minute |

Rate limit headers are included in responses:

```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 8
X-RateLimit-Reset: 1705318200
```

---

## WebSocket API

Real-time updates via WebSocket.

### Connect

```javascript
const ws = new WebSocket('wss://api.devora.app/ws');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'subscribe',
    channel: 'project:123'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data.type, data.payload);
};
```

### Events

| Type | Description |
|------|-------------|
| project:update | Project was modified |
| file:change | File content changed |
| deploy:status | Deployment status update |
| agent:progress | Agent progress update |

---

## SDK Examples

### JavaScript/TypeScript

```typescript
import { DevoraClient } from '@devora/sdk';

const client = new DevoraClient({
  apiKey: 'sk-...',
  baseUrl: 'https://api.devora.app'
});

// Generate code
const result = await client.generate({
  prompt: 'Create a todo app',
  quality: 'standard'
});

// Stream progress
for await (const event of client.generateStream({
  prompt: 'Create a dashboard'
})) {
  console.log(event.progress, event.message);
}
```

### Python

```python
from devora import DevoraClient

client = DevoraClient(api_key="sk-...")

# Generate code
result = client.generate(
    prompt="Create a todo app",
    quality="standard"
)

# Stream progress
for event in client.generate_stream(prompt="Create a dashboard"):
    print(event.progress, event.message)
```

---

## Changelog

### v3.0.0 (2025-01)
- Added SSE streaming for task execution
- Added quality gates system
- Added parallel agent execution
- Added task cancellation
- Improved error handling

### v2.0.0 (2024-12)
- Multi-agent orchestration
- Context compression
- Template support

### v1.0.0 (2024-11)
- Initial release
