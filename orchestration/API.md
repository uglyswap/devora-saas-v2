# API Documentation

Documentation complète de l'API REST du système d'orchestration Devora.

> **Note**: Cette API n'est pas encore implémentée. Ce document décrit l'architecture API prévue pour le système d'orchestration.

---

## Table des Matières

- [Vue d'Ensemble](#vue-densemble)
- [Architecture API](#architecture-api)
- [Authentication](#authentication)
- [Endpoints](#endpoints)
  - [Agents](#agents-endpoints)
  - [Workflows](#workflows-endpoints)
  - [Jobs](#jobs-endpoints)
  - [Metrics](#metrics-endpoints)
- [WebSocket](#websocket)
- [Rate Limiting](#rate-limiting)
- [Exemples](#exemples)
- [SDKs](#sdks)
- [Erreurs](#erreurs)

---

## Vue d'Ensemble

L'API Devora Orchestration permet d'interagir avec le système multi-agents via HTTP REST et WebSocket.

### Base URL

```
Production:  https://api.devora.ai/v1
Staging:     https://api-staging.devora.ai/v1
Development: http://localhost:8000/v1
```

### Formats

- **Request**: JSON
- **Response**: JSON
- **Encoding**: UTF-8
- **Date Format**: ISO 8601 (ex: `2024-12-09T10:30:00Z`)

### Versioning

L'API utilise le versioning via URL:
- Version actuelle: `v1`
- Format: `/v{version}/endpoint`

---

## Architecture API

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT                                  │
└─────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
            ┌───────▼────────┐     ┌────────▼────────┐
            │   REST API     │     │   WebSocket     │
            │   (HTTP)       │     │   (Real-time)   │
            └───────┬────────┘     └────────┬────────┘
                    │                       │
            ┌───────▼───────────────────────▼────────┐
            │        API Gateway (FastAPI)           │
            │  - Auth Middleware                     │
            │  - Rate Limiting                       │
            │  - Request Validation                  │
            │  - Response Formatting                 │
            └────────────────┬───────────────────────┘
                             │
            ┌────────────────┴────────────────┐
            │                                 │
    ┌───────▼────────┐             ┌─────────▼─────────┐
    │ Orchestration  │             │   Job Queue       │
    │    Engine      │             │   (Redis/Celery)  │
    └───────┬────────┘             └─────────┬─────────┘
            │                                 │
    ┌───────▼─────────────────────────────────▼─────┐
    │              Agent Registry                    │
    │   - 28 Agents disponibles                     │
    │   - Health checks                             │
    │   - Load balancing                            │
    └───────────────────────────────────────────────┘
```

---

## Authentication

### API Key Authentication

Toutes les requêtes nécessitent une clé API dans le header:

```http
Authorization: Bearer YOUR_API_KEY
```

### Obtenir une Clé API

```bash
POST /v1/auth/api-keys
Content-Type: application/json

{
  "name": "My Application",
  "scopes": ["agents:execute", "workflows:run"]
}
```

**Response**:
```json
{
  "api_key": "dvr_sk_live_1234567890abcdef",
  "name": "My Application",
  "scopes": ["agents:execute", "workflows:run"],
  "created_at": "2024-12-09T10:30:00Z",
  "expires_at": null
}
```

### Scopes Disponibles

| Scope | Description |
|-------|-------------|
| `agents:read` | Lire informations des agents |
| `agents:execute` | Exécuter des agents |
| `workflows:read` | Lire workflows disponibles |
| `workflows:run` | Exécuter des workflows |
| `jobs:read` | Consulter jobs |
| `jobs:cancel` | Annuler jobs |
| `metrics:read` | Accès aux métriques |
| `admin:*` | Tous les droits (admin) |

---

## Endpoints

### Agents Endpoints

#### Lister les Agents Disponibles

```http
GET /v1/agents
```

**Response**:
```json
{
  "agents": [
    {
      "id": "product_manager",
      "name": "Product Manager",
      "squad": "business",
      "description": "Génère PRD, user stories, roadmap",
      "capabilities": [
        "prd_generation",
        "user_stories",
        "roadmap",
        "prioritization"
      ],
      "status": "available",
      "health": {
        "healthy": true,
        "last_check": "2024-12-09T10:30:00Z"
      }
    },
    {
      "id": "ui_ux_designer",
      "name": "UI/UX Designer",
      "squad": "frontend",
      "description": "Design systems, wireframes, accessibility",
      "capabilities": [
        "design_system",
        "wireframes",
        "user_flows",
        "accessibility_audit"
      ],
      "status": "available"
    }
  ],
  "total": 28,
  "available": 7,
  "unavailable": 21
}
```

#### Obtenir Détails d'un Agent

```http
GET /v1/agents/{agent_id}
```

**Exemple**:
```bash
curl -X GET https://api.devora.ai/v1/agents/product_manager \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response**:
```json
{
  "id": "product_manager",
  "name": "Product Manager",
  "squad": "business",
  "description": "Expert Product Manager pour PRD et roadmap",
  "capabilities": [
    "prd_generation",
    "user_stories",
    "roadmap",
    "prioritization"
  ],
  "input_schema": {
    "type": "object",
    "properties": {
      "task_type": {
        "type": "string",
        "enum": ["prd", "user_story", "roadmap", "prioritization"]
      },
      "context": {
        "type": "string",
        "description": "Description du besoin"
      }
    },
    "required": ["task_type", "context"]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "status": {"type": "string"},
      "output": {"type": "string"},
      "metadata": {"type": "object"}
    }
  },
  "config": {
    "default_model": "anthropic/claude-3.5-sonnet",
    "default_temperature": 0.7,
    "max_tokens": 4096
  },
  "pricing": {
    "per_request": 0.05,
    "per_1k_tokens": 0.012
  }
}
```

#### Exécuter un Agent

```http
POST /v1/agents/{agent_id}/execute
Content-Type: application/json

{
  "input": {
    "task_type": "prd",
    "context": "Application mobile de livraison",
    "target_audience": "urbains 18-45 ans"
  },
  "config": {
    "model": "anthropic/claude-3.5-sonnet",
    "temperature": 0.7,
    "max_tokens": 8192
  },
  "async": false,
  "webhook_url": "https://myapp.com/webhook"
}
```

**Paramètres**:
- `input` (required): Input data selon schema de l'agent
- `config` (optional): Override de configuration
- `async` (optional): Mode asynchrone (défaut: `false`)
- `webhook_url` (optional): URL pour callback (si async=true)

**Response (Sync)**:
```json
{
  "job_id": "job_1234567890",
  "status": "completed",
  "output": {
    "status": "success",
    "output": "# Product Requirements Document\n\n...",
    "metadata": {
      "task_type": "prd",
      "timestamp": "2024-12-09T10:35:00Z"
    }
  },
  "metrics": {
    "total_tokens": 3542,
    "prompt_tokens": 450,
    "completion_tokens": 3092,
    "execution_time": 15.34,
    "cost": 0.042
  },
  "created_at": "2024-12-09T10:34:45Z",
  "completed_at": "2024-12-09T10:35:00Z"
}
```

**Response (Async)**:
```json
{
  "job_id": "job_1234567890",
  "status": "queued",
  "agent_id": "product_manager",
  "created_at": "2024-12-09T10:34:45Z",
  "eta_seconds": 20,
  "webhook_url": "https://myapp.com/webhook"
}
```

#### Health Check d'un Agent

```http
GET /v1/agents/{agent_id}/health
```

**Response**:
```json
{
  "agent_id": "product_manager",
  "healthy": true,
  "last_execution": "2024-12-09T10:30:00Z",
  "avg_response_time": 15.2,
  "error_rate": 0.5,
  "uptime": 99.9
}
```

---

### Workflows Endpoints

#### Lister les Workflows

```http
GET /v1/workflows
```

**Response**:
```json
{
  "workflows": [
    {
      "id": "full_stack_development",
      "name": "Full Stack Development",
      "description": "Développement complet d'une application",
      "squads": ["business", "frontend", "backend", "data", "qa", "devops"],
      "agents_count": 18,
      "estimated_time": "20-40 minutes",
      "estimated_cost": "$1.00-$2.00",
      "complexity": "high"
    },
    {
      "id": "api_development",
      "name": "API Development",
      "description": "Conception et développement d'API REST/GraphQL",
      "squads": ["business", "backend", "documentation", "qa"],
      "agents_count": 4,
      "estimated_time": "5-10 minutes",
      "estimated_cost": "$0.25-$0.50",
      "complexity": "medium"
    }
  ],
  "total": 10
}
```

#### Détails d'un Workflow

```http
GET /v1/workflows/{workflow_id}
```

**Response**:
```json
{
  "id": "api_development",
  "name": "API Development",
  "description": "Conception et développement d'API complète",
  "version": "1.0",
  "steps": [
    {
      "order": 1,
      "name": "Requirements Analysis",
      "squad": "business",
      "agents": ["product_manager", "business_analyst"],
      "estimated_time": "2-3 minutes"
    },
    {
      "order": 2,
      "name": "API Design",
      "squad": "backend",
      "agents": ["api_architect"],
      "estimated_time": "3-5 minutes"
    }
  ],
  "input_schema": {
    "type": "object",
    "properties": {
      "api_name": {"type": "string"},
      "description": {"type": "string"},
      "api_type": {
        "type": "string",
        "enum": ["rest", "graphql"]
      }
    },
    "required": ["api_name", "description", "api_type"]
  },
  "output_schema": {...}
}
```

#### Exécuter un Workflow

```http
POST /v1/workflows/{workflow_id}/run
Content-Type: application/json

{
  "input": {
    "project_name": "TaskMaster Pro",
    "description": "Application de gestion de tâches",
    "tech_stack": {
      "frontend": ["React", "Tailwind"],
      "backend": ["FastAPI", "PostgreSQL"]
    },
    "requirements": [
      "Authentification JWT",
      "CRUD tâches",
      "Collaboration temps réel"
    ]
  },
  "config": {
    "model": "anthropic/claude-3.5-sonnet",
    "parallel_execution": true,
    "stop_on_error": false
  },
  "async": true,
  "webhook_url": "https://myapp.com/webhook"
}
```

**Response**:
```json
{
  "job_id": "wf_job_9876543210",
  "workflow_id": "full_stack_development",
  "status": "running",
  "progress": {
    "current_step": 2,
    "total_steps": 6,
    "percentage": 33
  },
  "steps_status": [
    {
      "step": "requirements_analysis",
      "status": "completed",
      "completed_at": "2024-12-09T10:35:00Z"
    },
    {
      "step": "api_design",
      "status": "running",
      "started_at": "2024-12-09T10:35:01Z"
    }
  ],
  "created_at": "2024-12-09T10:34:00Z",
  "eta_seconds": 1200
}
```

---

### Jobs Endpoints

#### Lister les Jobs

```http
GET /v1/jobs?status=running&limit=20
```

**Query Parameters**:
- `status`: Filter par status (`queued`, `running`, `completed`, `failed`)
- `agent_id`: Filter par agent
- `workflow_id`: Filter par workflow
- `limit`: Nombre de résultats (défaut: 20, max: 100)
- `offset`: Pagination offset

**Response**:
```json
{
  "jobs": [
    {
      "job_id": "job_1234567890",
      "type": "agent",
      "agent_id": "product_manager",
      "status": "running",
      "progress": 65,
      "created_at": "2024-12-09T10:34:00Z",
      "started_at": "2024-12-09T10:34:01Z"
    }
  ],
  "total": 45,
  "limit": 20,
  "offset": 0
}
```

#### Détails d'un Job

```http
GET /v1/jobs/{job_id}
```

**Response**:
```json
{
  "job_id": "job_1234567890",
  "type": "agent",
  "agent_id": "product_manager",
  "status": "completed",
  "input": {
    "task_type": "prd",
    "context": "..."
  },
  "output": {
    "status": "success",
    "output": "...",
    "metadata": {...}
  },
  "metrics": {
    "total_tokens": 3542,
    "execution_time": 15.34,
    "cost": 0.042
  },
  "created_at": "2024-12-09T10:34:00Z",
  "started_at": "2024-12-09T10:34:01Z",
  "completed_at": "2024-12-09T10:34:16Z"
}
```

#### Annuler un Job

```http
POST /v1/jobs/{job_id}/cancel
```

**Response**:
```json
{
  "job_id": "job_1234567890",
  "status": "cancelled",
  "cancelled_at": "2024-12-09T10:35:00Z"
}
```

#### Télécharger l'Output d'un Job

```http
GET /v1/jobs/{job_id}/output
Accept: application/json
```

**Response**: Output complet du job

---

### Metrics Endpoints

#### Métriques Globales

```http
GET /v1/metrics
```

**Response**:
```json
{
  "period": "last_24h",
  "summary": {
    "total_jobs": 1245,
    "completed_jobs": 1198,
    "failed_jobs": 47,
    "success_rate": 96.2,
    "total_tokens": 2450000,
    "total_cost": 29.40,
    "avg_execution_time": 12.5
  },
  "by_agent": {
    "product_manager": {
      "executions": 245,
      "avg_tokens": 3200,
      "avg_time": 15.2,
      "success_rate": 98.0
    }
  },
  "by_workflow": {
    "api_development": {
      "executions": 52,
      "avg_tokens": 18000,
      "avg_time": 320.5,
      "success_rate": 94.2
    }
  }
}
```

#### Métriques d'un Agent

```http
GET /v1/metrics/agents/{agent_id}?period=7d
```

**Query Parameters**:
- `period`: `1h`, `24h`, `7d`, `30d`, `all`

**Response**:
```json
{
  "agent_id": "product_manager",
  "period": "7d",
  "metrics": {
    "total_executions": 856,
    "successful": 842,
    "failed": 14,
    "success_rate": 98.4,
    "total_tokens": 2740000,
    "avg_tokens_per_execution": 3200,
    "total_cost": 32.88,
    "avg_cost_per_execution": 0.038,
    "avg_execution_time": 15.2,
    "p50_execution_time": 14.5,
    "p95_execution_time": 22.1,
    "p99_execution_time": 28.5
  },
  "timeline": [
    {
      "date": "2024-12-09",
      "executions": 122,
      "tokens": 390000,
      "cost": 4.68
    }
  ]
}
```

---

## WebSocket

### Connection

```javascript
const ws = new WebSocket('wss://api.devora.ai/v1/ws');

// Authenticate
ws.send(JSON.stringify({
  type: 'auth',
  token: 'YOUR_API_KEY'
}));
```

### Subscribe to Job Updates

```javascript
// Subscribe to job updates
ws.send(JSON.stringify({
  type: 'subscribe',
  channel: 'job',
  job_id: 'job_1234567890'
}));

// Receive updates
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === 'job_update') {
    console.log(`Status: ${data.status}`);
    console.log(`Progress: ${data.progress}%`);
  }

  if (data.type === 'job_completed') {
    console.log('Job completed!');
    console.log(data.output);
  }
};
```

### Events

| Event | Description |
|-------|-------------|
| `job_queued` | Job ajouté à la queue |
| `job_started` | Exécution démarrée |
| `job_progress` | Mise à jour de progression |
| `job_completed` | Job terminé avec succès |
| `job_failed` | Job échoué |
| `agent_event` | Événement spécifique de l'agent |

**Example Event**:
```json
{
  "type": "job_progress",
  "job_id": "job_1234567890",
  "status": "running",
  "progress": 65,
  "current_step": "api_design",
  "message": "Generating OpenAPI specification...",
  "timestamp": "2024-12-09T10:35:00Z"
}
```

---

## Rate Limiting

### Limites par Tier

| Tier | Requests/min | Concurrent Jobs | Monthly Tokens |
|------|-------------|-----------------|----------------|
| Free | 10 | 1 | 100,000 |
| Pro | 60 | 5 | 1,000,000 |
| Business | 300 | 20 | 10,000,000 |
| Enterprise | Custom | Custom | Custom |

### Headers de Rate Limit

Chaque réponse inclut:

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1702123456
```

### Dépassement de Limite

**Response (429 Too Many Requests)**:
```json
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Rate limit exceeded. Retry after 60 seconds.",
    "retry_after": 60
  }
}
```

---

## Exemples

### cURL

**Exécuter un Agent**:
```bash
curl -X POST https://api.devora.ai/v1/agents/product_manager/execute \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "task_type": "prd",
      "context": "Application de livraison de repas",
      "target_audience": "urbains 18-45 ans"
    },
    "async": false
  }'
```

**Lancer un Workflow**:
```bash
curl -X POST https://api.devora.ai/v1/workflows/api_development/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "api_name": "TaskMaster API",
      "description": "API REST pour gestion de tâches",
      "api_type": "rest",
      "requirements": [
        "CRUD utilisateurs",
        "CRUD tâches"
      ]
    },
    "async": true,
    "webhook_url": "https://myapp.com/webhook"
  }'
```

### Python SDK

```python
from devora import DevoraClient

# Initialize client
client = DevoraClient(api_key="YOUR_API_KEY")

# Execute agent (sync)
result = client.agents.execute(
    agent_id="product_manager",
    input={
        "task_type": "prd",
        "context": "Application de livraison"
    }
)

print(result.output)
print(f"Tokens: {result.metrics.total_tokens}")

# Execute workflow (async)
job = client.workflows.run(
    workflow_id="api_development",
    input={
        "api_name": "TaskMaster API",
        "api_type": "rest",
        "requirements": [...]
    },
    async_mode=True
)

# Wait for completion
result = job.wait(timeout=600)

# Or poll status
while not job.is_complete():
    status = job.get_status()
    print(f"Progress: {status.progress}%")
    time.sleep(5)

result = job.get_result()
```

### JavaScript/TypeScript SDK

```typescript
import { DevoraClient } from '@devora/sdk';

const client = new DevoraClient({
  apiKey: 'YOUR_API_KEY',
  baseUrl: 'https://api.devora.ai/v1'
});

// Execute agent
const result = await client.agents.execute({
  agentId: 'product_manager',
  input: {
    task_type: 'prd',
    context: 'Application de livraison'
  }
});

console.log(result.output);

// Execute workflow with WebSocket updates
const job = await client.workflows.run({
  workflowId: 'api_development',
  input: {...},
  async: true
});

// Subscribe to updates
job.on('progress', (update) => {
  console.log(`Progress: ${update.progress}%`);
});

job.on('completed', (result) => {
  console.log('Workflow completed!');
  console.log(result.deliverables);
});

job.on('error', (error) => {
  console.error('Workflow failed:', error);
});
```

### Go SDK

```go
package main

import (
    "context"
    "fmt"
    "github.com/devora/sdk-go"
)

func main() {
    client := devora.NewClient("YOUR_API_KEY")

    // Execute agent
    result, err := client.Agents.Execute(context.Background(), &devora.AgentExecuteRequest{
        AgentID: "product_manager",
        Input: map[string]interface{}{
            "task_type": "prd",
            "context":   "Application de livraison",
        },
    })

    if err != nil {
        panic(err)
    }

    fmt.Println(result.Output)
    fmt.Printf("Tokens: %d\n", result.Metrics.TotalTokens)
}
```

---

## SDKs

### Officiels

- **Python**: `pip install devora`
- **JavaScript/TypeScript**: `npm install @devora/sdk`
- **Go**: `go get github.com/devora/sdk-go`

### Communautaires

- **Ruby**: `gem install devora-ruby`
- **PHP**: `composer require devora/sdk`
- **Java**: Maven Central `com.devora:sdk`

### CLI

```bash
# Install
npm install -g @devora/cli

# Configure
devora config set api-key YOUR_API_KEY

# Execute agent
devora agents execute product_manager \
  --input '{"task_type": "prd", "context": "..."}'

# Run workflow
devora workflows run api_development \
  --input input.json \
  --output result.json \
  --watch  # Follow progress
```

---

## Erreurs

### Codes d'Erreur Standard

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `invalid_request` | 400 | Requête invalide |
| `authentication_failed` | 401 | API key invalide |
| `forbidden` | 403 | Accès refusé |
| `not_found` | 404 | Ressource introuvable |
| `rate_limit_exceeded` | 429 | Rate limit dépassé |
| `internal_error` | 500 | Erreur interne |
| `service_unavailable` | 503 | Service temporairement indisponible |

### Format d'Erreur

```json
{
  "error": {
    "code": "invalid_request",
    "message": "Missing required field: task_type",
    "details": {
      "field": "task_type",
      "provided": null,
      "expected": "string"
    },
    "request_id": "req_1234567890",
    "timestamp": "2024-12-09T10:35:00Z"
  }
}
```

### Gestion des Erreurs (Python)

```python
from devora import DevoraClient, DevoraError, RateLimitError

client = DevoraClient(api_key="YOUR_API_KEY")

try:
    result = client.agents.execute(...)
except RateLimitError as e:
    print(f"Rate limit exceeded. Retry after {e.retry_after}s")
    time.sleep(e.retry_after)
    # Retry
except DevoraError as e:
    print(f"Error: {e.code} - {e.message}")
    print(f"Request ID: {e.request_id}")
```

---

## Webhooks

### Configuration

```bash
POST /v1/webhooks
Content-Type: application/json

{
  "url": "https://myapp.com/webhook",
  "events": ["job.completed", "job.failed"],
  "secret": "webhook_secret_key"
}
```

### Payload

```json
{
  "event": "job.completed",
  "job_id": "job_1234567890",
  "timestamp": "2024-12-09T10:35:00Z",
  "data": {
    "status": "completed",
    "output": {...},
    "metrics": {...}
  },
  "signature": "sha256=..."
}
```

### Vérification de Signature

```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(f"sha256={expected}", signature)
```

---

## Best Practices

### 1. Authentification

```python
# ✅ BON: Utiliser variables d'environnement
import os
api_key = os.getenv("DEVORA_API_KEY")

# ❌ MAUVAIS: Hardcoder la clé
api_key = "dvr_sk_live_1234567890"
```

### 2. Gestion d'Erreurs

```python
# ✅ BON: Retry avec backoff exponentiel
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=60)
)
def execute_agent(client, agent_id, input_data):
    return client.agents.execute(agent_id, input_data)
```

### 3. Mode Asynchrone

```python
# ✅ BON: Utiliser async pour workflows longs
job = client.workflows.run(
    workflow_id="full_stack_development",
    input={...},
    async_mode=True,
    webhook_url="https://myapp.com/webhook"
)

# Ne pas attendre, traiter via webhook
return {"job_id": job.id}

# ❌ MAUVAIS: Bloquer pendant 20 minutes
result = client.workflows.run(
    workflow_id="full_stack_development",
    input={...},
    async_mode=False  # Timeout!
)
```

### 4. Monitoring

```python
# Logger tous les appels
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

result = client.agents.execute(...)

logger.info(
    "Agent executed",
    extra={
        "agent_id": "product_manager",
        "job_id": result.job_id,
        "tokens": result.metrics.total_tokens,
        "cost": result.metrics.cost
    }
)
```

---

## Changelog API

### v1.0 (2024-12-09) - Planned

- Initial API design
- Agent execution endpoints
- Workflow orchestration endpoints
- WebSocket real-time updates
- Rate limiting
- Webhooks

### Future (Roadmap)

- **v1.1**: Batch processing, custom agents
- **v1.2**: Agent training/fine-tuning
- **v2.0**: GraphQL API, advanced caching

---

## Support & Resources

- **Documentation**: https://docs.devora.ai
- **API Reference**: https://api.devora.ai/docs (Swagger UI)
- **Status Page**: https://status.devora.ai
- **Support**: support@devora.ai
- **GitHub**: https://github.com/devora-ai/orchestration

---

**API Documentation maintenue par**: DevOps Squad
**Dernière mise à jour**: 2024-12-09
**Version API**: v1 (planned)
