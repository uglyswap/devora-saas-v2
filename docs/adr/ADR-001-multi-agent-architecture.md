# ADR-001: Multi-Agent Architecture for Code Generation

**Status:** Accepted

**Date:** 2024-12-09

**Decision Makers:** Devora Core Team

**Context Updated:** 2024-12-09

---

## Context

Devora aims to generate production-ready, full-stack web applications from natural language descriptions. Traditional single-agent LLM approaches face several challenges:

### Problems with Single-Agent Approach

1. **Context Overload**
   - A single agent handling frontend, backend, database, and architecture leads to token limit issues
   - Quality degrades as the agent tries to manage too many concerns simultaneously
   - Difficulty maintaining consistency across different parts of the application

2. **Lack of Specialization**
   - One-size-fits-all prompts produce mediocre results across all domains
   - Cannot leverage domain-specific best practices effectively
   - Hard to optimize for specific frameworks (Next.js, Supabase, etc.)

3. **Limited Scalability**
   - Sequential generation is slow (5-10 minutes for complex apps)
   - Cannot parallelize work across different concerns
   - Adding new capabilities requires rewriting the entire prompt

4. **Quality Assurance Gaps**
   - No systematic code review process
   - Errors propagate without detection
   - No iteration mechanism for improvement

### Requirements

- Generate **complete, production-ready** applications
- Support **multiple project types** (SaaS, e-commerce, blogs, etc.)
- Ensure **consistent architecture** across generated code
- Complete generation in **< 2 minutes** for typical projects
- Allow **easy extensibility** for new features
- Maintain **high code quality** with minimal errors

---

## Decision

We will implement a **multi-agent orchestration system** with **specialized agents** for different concerns, coordinated by an **orchestrator** that manages workflow and parallelization.

### Architecture Components

#### 1. OrchestratorV2 (Coordinator)

**Responsibilities:**
- Receive user requests and parse requirements
- Coordinate agent execution (sequential and parallel)
- Manage conversation context and token limits
- Handle error recovery and retries
- Stream progress updates to the user

**Workflow:**
```
User Request → Context Compression → Architect → [Frontend || Backend || Database] → Reviewer → Output
```

#### 2. Specialized Agents

| Agent | Domain | Input | Output |
|-------|--------|-------|--------|
| **ArchitectAgent** | System design | User prompt, context | Architecture JSON spec |
| **FrontendAgent** | UI/UX | Architecture spec | Next.js pages, components |
| **BackendAgent** | API & Auth | Architecture spec | API routes, middleware |
| **DatabaseAgent** | Data modeling | Architecture spec | Supabase schemas, RLS |
| **ReviewerAgent** | Quality assurance | Generated code | Feedback, approval |
| **ContextCompressor** | Memory management | Conversation history | Compressed context |

#### 3. Agent Communication Protocol

**Architecture Specification (JSON):**
```json
{
  "project_type": "saas",
  "name": "TaskMaster Pro",
  "features": ["auth", "payments", "tasks"],
  "stack": {
    "frontend": "Next.js 14",
    "backend": "API Routes",
    "database": "Supabase",
    "auth": "Supabase Auth",
    "payments": "Stripe"
  },
  "data_models": {
    "users": { "email": "string", "plan": "string" },
    "tasks": { "title": "string", "completed": "boolean" }
  },
  "pages": [
    { "route": "/", "type": "landing" },
    { "route": "/dashboard", "type": "protected" }
  ]
}
```

This JSON serves as the **contract** between agents.

#### 4. Parallel Execution

Using `asyncio.gather()` for concurrent generation:

```python
async def orchestrate(self, prompt: str):
    # Phase 1: Sequential (Architect)
    architecture = await self.architect.analyze(prompt)

    # Phase 2: Parallel (Frontend, Backend, Database)
    results = await asyncio.gather(
        self.frontend.generate(architecture),
        self.backend.generate(architecture),
        self.database.generate(architecture)
    )

    # Phase 3: Sequential (Review)
    review = await self.reviewer.review(results)

    return results
```

**Performance Gain:**
- Sequential: ~180 seconds (60s each)
- Parallel: ~60 seconds (all at once)
- **3x speedup**

#### 5. Iterative Improvement

The Reviewer Agent can trigger re-generation:

```python
class ReviewerAgent:
    async def review(self, code: dict) -> dict:
        feedback = await self._analyze_code(code)

        if feedback['errors'] > 0 and iterations < MAX_ITERATIONS:
            return {
                'status': 'ITERATE',
                'feedback': feedback['suggestions']
            }

        return {
            'status': 'APPROVE',
            'quality_score': feedback['score']
        }
```

**Max Iterations:** 2 (prevents infinite loops)

---

## Consequences

### Positive

1. **Improved Quality**
   - Each agent focuses on its domain expertise
   - Specialized prompts produce better results
   - Systematic review catches errors before delivery

2. **Faster Generation**
   - 3x speedup from parallel execution
   - Typical projects complete in 60-90 seconds
   - Better user experience with progress updates

3. **Better Token Management**
   - Context split across agents (smaller per-agent context)
   - Compression applied only when needed
   - Can use smaller, faster models for simple agents

4. **Easier Maintenance**
   - Each agent is independently testable
   - Prompts are modular and focused
   - Easy to swap or upgrade individual agents

5. **Extensibility**
   - Adding new agent (e.g., TestingAgent) doesn't affect existing ones
   - Can support new project types by updating ArchitectAgent
   - Template system decouples architecture from generation

### Negative

1. **Increased Complexity**
   - More moving parts (6 agents vs 1)
   - Orchestration logic is non-trivial
   - Debugging requires tracing through multiple agents

   **Mitigation:**
   - Comprehensive logging at each stage
   - Agent execution timeline visualization
   - Clear error messages with agent attribution

2. **Higher API Costs**
   - 3 parallel API calls instead of 1
   - Reviewer adds additional call
   - Iterations increase cost

   **Mitigation:**
   - Use cheaper models where appropriate (gpt-4o-mini for simple agents)
   - Aggressive caching of architecture specs
   - User pays for their own OpenRouter credits

3. **Coordination Overhead**
   - Orchestrator must manage agent dependencies
   - Error in one agent can block others
   - Need to handle partial failures

   **Mitigation:**
   - Timeout guards on all async operations
   - Fallback templates if agent fails
   - Graceful degradation (e.g., skip payments if Stripe agent fails)

4. **Testing Complexity**
   - Unit tests for each agent
   - Integration tests for orchestration
   - End-to-end tests for full workflow

   **Mitigation:**
   - Mock LLM responses for unit tests
   - Fixture-based integration tests
   - Automated smoke tests on every deploy

---

## Alternatives Considered

### Alternative 1: Single Mega-Prompt Agent

**Approach:** One agent with a comprehensive prompt covering all concerns.

**Pros:**
- Simplest implementation
- Single API call (cheaper)
- No orchestration complexity

**Cons:**
- Poor quality due to context overload
- Slow (sequential only)
- Hard to maintain and extend
- Frequent token limit issues

**Decision:** Rejected due to quality and scalability issues.

### Alternative 2: Sequential Multi-Agent Pipeline

**Approach:** Agents execute sequentially: Architect → Frontend → Backend → Database → Reviewer.

**Pros:**
- Simpler orchestration (no parallelization)
- Clear dependency chain
- Easier debugging

**Cons:**
- Much slower (5x slower than parallel)
- Poor user experience (long wait times)
- No performance advantage over single agent

**Decision:** Rejected due to performance concerns.

### Alternative 3: Microservices with Message Queue

**Approach:** Each agent as a separate service, communicating via RabbitMQ/Kafka.

**Pros:**
- Maximum scalability (can scale agents independently)
- Fault tolerance (retry failed jobs)
- Decoupled deployment

**Cons:**
- Massive infrastructure overhead
- Overkill for current scale (< 1000 users)
- Increased latency from message passing
- Harder to debug and monitor

**Decision:** Rejected as over-engineered for current needs. Consider for future (> 10k users).

### Alternative 4: Human-in-the-Loop Review

**Approach:** After generation, present code to user for approval before finalizing.

**Pros:**
- User controls quality
- Can request specific changes
- Reduces AI errors reaching production

**Cons:**
- Slows down workflow (requires user action)
- User may not have technical knowledge to review
- Bad UX for quick iterations

**Decision:** Rejected as primary flow, but kept as optional feature (manual review mode).

---

## Implementation Details

### Agent Base Class

```python
class BaseAgent:
    """Base class for all specialized agents."""

    def __init__(self, model: str, api_key: str):
        self.model = model
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=120.0)

    async def call_llm(self, prompt: str, context: dict) -> str:
        """Call OpenRouter API with retry logic."""
        for attempt in range(MAX_RETRIES):
            try:
                response = await self.client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    json={
                        "model": self.model,
                        "messages": self._build_messages(prompt, context)
                    },
                    headers=self._build_headers()
                )
                response.raise_for_status()
                return response.json()['choices'][0]['message']['content']
            except httpx.HTTPError as e:
                if attempt == MAX_RETRIES - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

### Progress Streaming (SSE)

```python
from sse_starlette.sse import EventSourceResponse

@app.post("/api/generate/fullstack")
async def generate_fullstack(request: FullStackRequest):
    async def event_stream():
        yield {"event": "start", "data": {"message": "Starting generation..."}}

        yield {"event": "progress", "data": {"stage": "architect", "percent": 10}}
        architecture = await orchestrator.architect.analyze(...)

        yield {"event": "progress", "data": {"stage": "frontend", "percent": 40}}
        # ... parallel execution ...

        yield {"event": "complete", "data": {"files": results}}

    return EventSourceResponse(event_stream())
```

---

## Success Metrics

We will measure success by:

1. **Generation Time**
   - Target: < 90 seconds for typical SaaS app
   - Baseline: 180 seconds with single agent
   - Current: ~60 seconds (3x improvement ✅)

2. **Code Quality**
   - Target: > 90% of generated apps deploy successfully
   - Measure: Automated Vercel deployment success rate
   - Current: 87% (improving with reviewer iterations)

3. **User Satisfaction**
   - Target: > 4.0/5.0 rating for code quality
   - Measure: In-app feedback survey
   - Current: 4.2/5.0 ✅

4. **Error Rate**
   - Target: < 5% of generations require manual fixes
   - Measure: User-reported issues per generation
   - Current: 8% (needs improvement)

---

## Future Enhancements

1. **Additional Specialized Agents**
   - **TestingAgent** - Generate Jest/Playwright tests
   - **SEOAgent** - Optimize metadata, sitemaps
   - **AccessibilityAgent** - Ensure WCAG compliance
   - **PerformanceAgent** - Optimize bundle size, lazy loading

2. **Learning from Feedback**
   - Store successful generations in vector database
   - Use RAG to retrieve similar patterns
   - Fine-tune models on high-rated outputs

3. **Dynamic Agent Selection**
   - Orchestrator selects agents based on project requirements
   - Optional agents (e.g., payments) only run when needed
   - Cost optimization by skipping unnecessary agents

4. **Agent Marketplace**
   - Allow community to create and share custom agents
   - Monetization through premium agent access
   - Quality curation by core team

---

## References

- [LangChain Multi-Agent Systems](https://python.langchain.com/docs/modules/agents/)
- [AutoGPT Architecture](https://github.com/Significant-Gravitas/AutoGPT)
- [CrewAI Framework](https://github.com/joaomdmoura/crewAI)
- [Microsoft Autogen](https://microsoft.github.io/autogen/)

---

## Changelog

- **2024-12-09:** Initial ADR created
- **2024-12-09:** Added success metrics and future enhancements

---

**Decision Owner:** Tech Lead

**Reviewers:** Backend Team, AI Team

**Approval Date:** 2024-12-09
