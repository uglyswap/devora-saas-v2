# Devora Architecture Documentation

## Table of Contents

- [System Overview](#system-overview)
- [Architecture Principles](#architecture-principles)
- [Component Architecture](#component-architecture)
- [Multi-Agent System](#multi-agent-system)
- [Data Flow](#data-flow)
- [Security Architecture](#security-architecture)
- [Deployment Architecture](#deployment-architecture)
- [Scalability & Performance](#scalability--performance)

---

## System Overview

Devora is an AI-powered code generation SaaS platform built on a **microservices-inspired architecture** with a **multi-agent orchestration system** at its core.

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                       CLIENT LAYER                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Browser    │  │  Mobile App  │  │  API Client  │       │
│  │   (React)    │  │  (Future)    │  │    (SDK)     │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
└─────────┼──────────────────┼──────────────────┼──────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                   ┌─────────▼─────────┐
                   │   NGINX/CDN       │
                   │   (Reverse Proxy) │
                   └─────────┬─────────┘
                             │
┌────────────────────────────┼────────────────────────────────┐
│                    APPLICATION LAYER                         │
│                            │                                 │
│     ┌──────────────────────▼──────────────────────┐         │
│     │        FastAPI Server (Python 3.10)         │         │
│     │  ┌────────────────────────────────────┐     │         │
│     │  │     API Router (/api/*)            │     │         │
│     │  │  • Auth Routes                     │     │         │
│     │  │  • Project Routes                  │     │         │
│     │  │  • Generation Routes               │     │         │
│     │  │  • Billing Routes                  │     │         │
│     │  │  • Admin Routes                    │     │         │
│     │  └────────────┬───────────────────────┘     │         │
│     │               │                             │         │
│     │  ┌────────────▼───────────────────────┐     │         │
│     │  │   Multi-Agent Orchestrator         │     │         │
│     │  │  ┌─────────────────────────────┐   │     │         │
│     │  │  │   Context Compressor        │   │     │         │
│     │  │  └─────────────┬───────────────┘   │     │         │
│     │  │  ┌─────────────▼───────────────┐   │     │         │
│     │  │  │   Architect Agent           │   │     │         │
│     │  │  └─────────────┬───────────────┘   │     │         │
│     │  │                │                    │     │         │
│     │  │  ┌─────────────┼───────────────┐   │     │         │
│     │  │  │  Parallel Execution Layer   │   │     │         │
│     │  │  │  ┌──────┐ ┌──────┐ ┌──────┐│   │     │         │
│     │  │  │  │Front │ │Back  │ │  DB  ││   │     │         │
│     │  │  │  │ end  │ │ end  │ │Agent ││   │     │         │
│     │  │  │  └──────┘ └──────┘ └──────┘│   │     │         │
│     │  │  └─────────────┬───────────────┘   │     │         │
│     │  │  ┌─────────────▼───────────────┐   │     │         │
│     │  │  │   Reviewer Agent            │   │     │         │
│     │  │  └─────────────────────────────┘   │     │         │
│     │  └────────────────────────────────────┘     │         │
│     └─────────────────────────────────────────────┘         │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────┼──────────────────────────────────┐
│                   DATA LAYER                                 │
│     ┌────────────────────▼────────────────────┐             │
│     │         MongoDB (Motor Async)           │             │
│     │  • projects                             │             │
│     │  • users                                │             │
│     │  • settings                             │             │
│     │  • conversations                        │             │
│     │  • subscriptions                        │             │
│     └─────────────────────────────────────────┘             │
│                                                              │
│     ┌──────────────────────────────────────────┐            │
│     │  PostgreSQL (Memori SDK - Optional)      │            │
│     │  • persistent_memory                     │            │
│     │  • user_context                          │            │
│     └──────────────────────────────────────────┘            │
└──────────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────┼──────────────────────────────────┐
│                 EXTERNAL SERVICES                            │
│     ┌────────────────────▼────────────────────┐             │
│     │  OpenRouter API (AI Models)             │             │
│     │  • GPT-4o, GPT-5                        │             │
│     │  • Claude 4 Sonnet/Opus                 │             │
│     │  • Gemini 2.5 Pro                       │             │
│     └─────────────────────────────────────────┘             │
│                                                              │
│     ┌──────────────────────────────────────────┐            │
│     │  Third-Party Services                    │            │
│     │  • Stripe (Payments)                     │            │
│     │  • GitHub API (Export)                   │            │
│     │  • Vercel API (Deploy)                   │            │
│     │  • Resend (Email)                        │            │
│     └──────────────────────────────────────────┘            │
└──────────────────────────────────────────────────────────────┘
```

---

## Architecture Principles

### 1. Separation of Concerns

- **Frontend**: Pure presentation layer (React) with no business logic
- **Backend**: API layer with business logic and orchestration
- **Agents**: Specialized AI workers with single responsibilities
- **Data**: Centralized persistence with MongoDB

### 2. Agent-Based Design

Each agent has a **single, well-defined responsibility**:

| Agent | Responsibility | Input | Output |
|-------|---------------|-------|--------|
| **ArchitectAgent** | Analyze requirements & design system | User prompt, context | Architecture JSON |
| **FrontendAgent** | Generate UI components | Architecture spec | Next.js pages, components |
| **BackendAgent** | Generate API & auth | Architecture spec | API routes, middleware |
| **DatabaseAgent** | Design data models & RLS | Architecture spec | Supabase schemas, RLS policies |
| **ReviewerAgent** | Validate & iterate | Generated code | Feedback, approval |
| **ContextCompressor** | Manage token limits | Conversation history | Compressed context |

### 3. Async-First

- **Motor** for async MongoDB operations
- **httpx** for async HTTP requests
- **asyncio.gather()** for parallel agent execution
- **SSE (Server-Sent Events)** for real-time streaming

### 4. Fail-Safe & Resilient

- **Iterative Review Loop**: Max 2 iterations for code improvement
- **Token Management**: Automatic context compression at 85% capacity
- **Error Handling**: Try/catch at every agent level
- **Fallback Strategies**: Default templates if generation fails

---

## Component Architecture

### Backend Components

#### 1. FastAPI Server (`server.py`)

**Core Routes:**
```python
/api/
├── /                        # Health check
├── /settings                # User settings CRUD
├── /projects                # Project management
│   ├── GET /                # List all projects
│   ├── POST /               # Create project
│   ├── GET /{id}            # Get project
│   ├── PUT /{id}            # Update project
│   └── DELETE /{id}         # Delete project
├── /conversations           # Chat history
├── /generate/
│   ├── /openrouter          # Simple generation
│   ├── /agentic             # Multi-agent HTML/CSS/JS
│   └── /fullstack           # Full-stack Next.js
├── /github/export           # GitHub integration
├── /vercel/deploy           # Vercel deployment
└── /stripe/
    ├── /checkout            # Create session
    └── /webhook             # Handle events
```

**Middleware Stack:**
```python
app.add_middleware(CORSMiddleware)       # CORS handling
app.include_router(auth_router)          # Authentication
app.include_router(billing_router)       # Stripe billing
app.include_router(admin_router)         # Admin panel
app.include_router(support_router)       # Support tickets
```

#### 2. Authentication System (`auth.py`)

**JWT-Based Authentication:**
```python
class AuthService:
    def create_access_token(data: dict) -> str
    def verify_token(token: str) -> dict
    def hash_password(password: str) -> str
    def verify_password(plain: str, hashed: str) -> bool
```

**Protected Routes:**
```python
@app.get("/api/projects")
async def get_projects(current_user: dict = Depends(get_current_user)):
    # Only authenticated users can access
```

#### 3. Billing System (`routes_billing.py`, `stripe_service.py`)

**Stripe Integration:**
```python
class StripeService:
    def create_checkout_session(user_id: str, plan: str) -> dict
    def create_customer(email: str) -> str
    def handle_webhook(event: dict) -> None
    def cancel_subscription(subscription_id: str) -> None
```

**Webhook Events:**
- `checkout.session.completed` → Activate subscription
- `invoice.payment_succeeded` → Extend access
- `invoice.payment_failed` → Suspend account
- `customer.subscription.deleted` → Downgrade to free

#### 4. Memory Service (`memory_service.py`)

**Memori SDK Integration:**
```python
class DevoraMemory:
    async def store_conversation(user_id: str, project_id: str, messages: list)
    async def retrieve_context(user_id: str, project_id: str) -> dict
    async def update_user_preferences(user_id: str, prefs: dict)
    async def get_similar_projects(description: str, limit: int) -> list
```

**Benefits:**
- Persistent context across sessions
- User preference learning
- Project similarity matching
- Long-term memory beyond token limits

---

## Multi-Agent System

### OrchestratorV2 Architecture

**Workflow:**

```python
class OrchestratorV2:
    def __init__(self, model: str, api_key: str):
        self.architect = ArchitectAgent(model, api_key)
        self.frontend = FrontendAgent(model, api_key)
        self.backend = BackendAgent(model, api_key)
        self.database = DatabaseAgent(model, api_key)
        self.reviewer = ReviewerAgent(model, api_key)
        self.compressor = ContextCompressor()

    async def orchestrate(self, prompt: str, context: dict) -> dict:
        # 1. Compress context if needed
        compressed = self.compressor.compress(context)

        # 2. Architect analyzes and plans
        architecture = await self.architect.analyze(prompt, compressed)

        # 3. Parallel execution of specialized agents
        frontend_task = self.frontend.generate(architecture)
        backend_task = self.backend.generate(architecture)
        database_task = self.database.generate(architecture)

        results = await asyncio.gather(
            frontend_task,
            backend_task,
            database_task
        )

        # 4. Review and iterate
        review = await self.reviewer.review(results)

        if review['status'] == 'ITERATE' and iterations < 2:
            # Regenerate based on feedback
            return await self.orchestrate_iteration(review)

        return {
            'files': results,
            'review': review,
            'architecture': architecture
        }
```

### Agent Implementation Pattern

**Base Agent:**
```python
class BaseAgent:
    def __init__(self, model: str, api_key: str):
        self.model = model
        self.api_key = api_key
        self.client = httpx.AsyncClient()

    async def call_llm(self, prompt: str, context: dict) -> str:
        response = await self.client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json={
                "model": self.model,
                "messages": self._build_messages(prompt, context),
                "temperature": 0.7
            },
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": settings.FRONTEND_URL
            }
        )
        return response.json()['choices'][0]['message']['content']

    def _build_messages(self, prompt: str, context: dict) -> list:
        # Subclass implements specific system prompt
        raise NotImplementedError
```

**Specialized Agent Example:**
```python
class FrontendAgent(BaseAgent):
    SYSTEM_PROMPT = """
    You are an expert Next.js 14+ developer specializing in:
    - App Router architecture
    - Server Components and Client Components
    - Tailwind CSS and shadcn/ui
    - Responsive design
    - Accessibility (WCAG 2.1)

    Generate production-ready, type-safe code.
    """

    async def generate(self, architecture: dict) -> dict:
        prompt = self._build_generation_prompt(architecture)
        code = await self.call_llm(prompt, architecture)
        return self._parse_generated_code(code)
```

---

## Data Flow

### 1. User Request Flow

```
User (Browser)
  │
  │ POST /api/generate/fullstack
  │ { prompt, model, project_type }
  │
  ▼
FastAPI Server
  │
  │ Validate request (Pydantic)
  │ Authenticate user (JWT)
  │ Check subscription limits
  │
  ▼
OrchestratorV2
  │
  │ 1. Load conversation history from MongoDB
  │ 2. Compress context if needed
  │
  ▼
ArchitectAgent
  │
  │ Analyze requirements
  │ Select template (SaaS, E-commerce, etc.)
  │
  ▼
Parallel Execution (asyncio.gather)
  │
  ├─► FrontendAgent → Next.js pages, components
  ├─► BackendAgent  → API routes, auth
  └─► DatabaseAgent → Supabase schemas, RLS
  │
  ▼
ReviewerAgent
  │
  │ Validate code quality
  │ Check for errors
  │ Decision: APPROVE or ITERATE
  │
  ▼
Response to User (SSE Stream)
  │
  │ {
  │   "event": "progress",
  │   "data": { "stage": "frontend", "percent": 60 }
  │ }
  │
  ▼
Save to MongoDB
  │
  │ projects.insert_one({
  │   id, name, files, conversation_history,
  │   github_repo_url, vercel_url, created_at
  │ })
  │
  ▼
Return Final Result
  │
  └─► User receives generated project
```

### 2. Export to GitHub Flow

```
User clicks "Export to GitHub"
  │
  ▼
POST /api/github/export
  │
  │ { project_id, repo_name, github_token }
  │
  ▼
GitHub Service
  │
  │ 1. Create repository via PyGithub
  │ 2. Initialize with README
  │ 3. Create file tree structure
  │ 4. Commit all project files
  │ 5. Push to main branch
  │
  ▼
Update Project in MongoDB
  │
  │ projects.update_one(
  │   { id: project_id },
  │   { $set: { github_repo_url: repo_url } }
  │ )
  │
  ▼
Return repo URL to user
```

### 3. Stripe Webhook Flow

```
Stripe Event Triggered
  │
  ▼
POST /api/stripe/webhook
  │
  │ Verify signature (Stripe SDK)
  │
  ▼
Event Handler
  │
  ├─► checkout.session.completed
  │   └─► Create/update user subscription
  │
  ├─► invoice.payment_succeeded
  │   └─► Extend subscription period
  │
  ├─► invoice.payment_failed
  │   └─► Suspend account, send email
  │
  └─► customer.subscription.deleted
      └─► Downgrade to free plan
  │
  ▼
Update MongoDB
  │
  │ users.update_one(
  │   { stripe_customer_id: customer_id },
  │   { $set: { subscription_status, plan } }
  │ )
  │
  ▼
Send confirmation email (Resend API)
```

---

## Security Architecture

### 1. Authentication & Authorization

**JWT Token Structure:**
```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "plan": "pro",
  "exp": 1234567890
}
```

**Token Lifecycle:**
```
Login → Generate JWT (30min expiry) → Store in httpOnly cookie →
Validate on each request → Refresh before expiry → Logout (clear cookie)
```

**Protected Route Example:**
```python
async def get_current_user(
    token: str = Depends(oauth2_scheme)
) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(401, "Invalid token")
        return payload
    except JWTError:
        raise HTTPException(401, "Invalid token")
```

### 2. API Key Security

**Encryption at Rest:**
```python
from cryptography.fernet import Fernet

class EncryptionService:
    def __init__(self):
        self.cipher = Fernet(settings.ENCRYPTION_KEY)

    def encrypt(self, plain_text: str) -> str:
        return self.cipher.encrypt(plain_text.encode()).decode()

    def decrypt(self, encrypted: str) -> str:
        return self.cipher.decrypt(encrypted.encode()).decode()
```

**Usage:**
```python
# Store
encrypted_key = encryption.encrypt(user_api_key)
await db.settings.update_one(
    {"id": settings_id},
    {"$set": {"openrouter_api_key": encrypted_key}}
)

# Retrieve
encrypted = settings['openrouter_api_key']
api_key = encryption.decrypt(encrypted)
```

### 3. Input Validation

**Pydantic Models:**
```python
class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    files: List[ProjectFile] = Field(default_factory=list)

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()
```

### 4. Rate Limiting

**Implementation:**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/generate/fullstack")
@limiter.limit("10/minute")
async def generate_fullstack(request: Request, ...):
    # Limited to 10 requests per minute per IP
    pass
```

### 5. CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),  # Whitelist only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)
```

---

## Deployment Architecture

### Production Stack

```
┌──────────────────────────────────────────┐
│           Cloudflare / CDN               │
│  • DDoS protection                       │
│  • SSL termination                       │
│  • Static asset caching                  │
└──────────────┬───────────────────────────┘
               │
┌──────────────▼───────────────────────────┐
│         Nginx Reverse Proxy              │
│  • Load balancing                        │
│  • Request routing                       │
│  • Gzip compression                      │
└──────────────┬───────────────────────────┘
               │
        ┌──────┴──────┐
        │             │
┌───────▼──────┐  ┌──▼──────────┐
│   Frontend   │  │   Backend   │
│   (React)    │  │  (FastAPI)  │
│   Port 3000  │  │  Port 8000  │
│              │  │             │
│   Nginx      │  │  Uvicorn    │
│   Static     │  │  Workers    │
│   Serving    │  │  (4x)       │
└──────────────┘  └──────┬──────┘
                         │
                  ┌──────┴──────┐
                  │             │
          ┌───────▼──────┐  ┌──▼────────┐
          │   MongoDB    │  │ PostgreSQL│
          │   Replica Set│  │  (Memori) │
          └──────────────┘  └───────────┘
```

### Docker Compose Setup

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - MONGO_URL=mongodb://mongo:27017
    depends_on:
      - mongo
    restart: always

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    environment:
      - REACT_APP_BACKEND_URL=http://backend:8000
    restart: always

  mongo:
    image: mongo:7.0
    volumes:
      - mongo_data:/data/db
    ports:
      - "27017:27017"
    restart: always

volumes:
  mongo_data:
```

### Environment-Specific Configurations

**Development:**
- Hot reload enabled
- Debug logging
- CORS allows all origins
- Mock Stripe webhooks

**Staging:**
- Similar to production
- Test Stripe keys
- Separate database
- Performance profiling enabled

**Production:**
- Optimized builds
- Error tracking (Sentry)
- Restricted CORS
- Live Stripe webhooks
- Database backups (daily)

---

## Scalability & Performance

### 1. Horizontal Scaling

**Backend:**
```
Load Balancer
  │
  ├─► FastAPI Instance 1 (Uvicorn worker 1-4)
  ├─► FastAPI Instance 2 (Uvicorn worker 1-4)
  ├─► FastAPI Instance 3 (Uvicorn worker 1-4)
  └─► FastAPI Instance 4 (Uvicorn worker 1-4)
```

**Database:**
- MongoDB Replica Set (3 nodes)
- Read replicas for queries
- Write to primary only

### 2. Caching Strategy

**Application-Level:**
```python
from functools import lru_cache

@lru_cache(maxsize=128)
async def get_openrouter_models(api_key: str) -> list:
    # Cache model list for 1 hour
    pass
```

**Redis (Future):**
- Session storage
- Rate limiting counters
- Generated code cache (24h)

### 3. Performance Optimizations

**Async Operations:**
```python
# Parallel agent execution
results = await asyncio.gather(
    frontend_agent.generate(),
    backend_agent.generate(),
    database_agent.generate()
)
# 3x faster than sequential
```

**Database Indexing:**
```javascript
db.projects.createIndex({ "user_id": 1, "created_at": -1 })
db.users.createIndex({ "email": 1 }, { unique: true })
db.settings.createIndex({ "id": 1 }, { unique: true })
```

**Pagination:**
```python
@app.get("/api/projects")
async def get_projects(
    skip: int = 0,
    limit: int = 20,
    user: dict = Depends(get_current_user)
):
    projects = await db.projects.find(
        {"user_id": user['user_id']}
    ).skip(skip).limit(limit).to_list(limit)
    return projects
```

### 4. Monitoring & Observability

**Metrics to Track:**
- Request latency (p50, p95, p99)
- Error rates by endpoint
- Agent execution time
- Token usage per request
- Database query performance
- Memory consumption

**Tools:**
- **Prometheus** - Metrics collection
- **Grafana** - Visualization
- **Sentry** - Error tracking
- **DataDog APM** - Application performance

---

## Future Architecture Enhancements

### 1. Message Queue Integration

```
User Request → FastAPI → RabbitMQ → Worker Pool → Response
```

**Benefits:**
- Decouple request from execution
- Handle spikes in traffic
- Retry failed jobs
- Background processing

### 2. Microservices Decomposition

```
API Gateway
  │
  ├─► Auth Service (JWT, OAuth)
  ├─► Project Service (CRUD)
  ├─► Generation Service (Agents)
  ├─► Billing Service (Stripe)
  └─► Export Service (GitHub, Vercel)
```

### 3. Multi-Region Deployment

```
User Location → Route to Nearest Region
  │
  ├─► US-East (Primary)
  ├─► EU-West (Secondary)
  └─► Asia-Pacific (Secondary)
```

**Challenges:**
- Data replication latency
- Consistent user sessions
- Cost optimization

### 4. Event-Driven Architecture

```
Event Bus (Kafka/AWS EventBridge)
  │
  ├─► project.created → Trigger welcome email
  ├─► generation.completed → Update analytics
  ├─► subscription.upgraded → Notify sales team
  └─► export.failed → Alert monitoring
```

---

## Conclusion

Devora's architecture is designed for:
- **Scalability** - Horizontal scaling at every layer
- **Reliability** - Fail-safe agents, retry mechanisms
- **Security** - Defense in depth, encryption, validation
- **Performance** - Async-first, parallel execution, caching
- **Maintainability** - Clear separation of concerns, modular agents

For questions or contributions, see [CONTRIBUTING.md](./CONTRIBUTING.md).
