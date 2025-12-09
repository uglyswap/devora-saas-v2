# Architecture du Business Squad

## Vue d'Ensemble

```
┌─────────────────────────────────────────────────────────────────┐
│                    BUSINESS SQUAD AGENTS                        │
│                      (Orchestration Layer)                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ inherits from
                              ▼
                    ┌──────────────────┐
                    │   BaseAgent      │
                    │  (ABC)           │
                    ├──────────────────┤
                    │ - name           │
                    │ - api_key        │
                    │ - model          │
                    │ - memory[]       │
                    ├──────────────────┤
                    │ + execute()      │
                    │ + call_llm()     │
                    │ + add_to_memory()│
                    │ + get_memory()   │
                    │ + clear_memory() │
                    └──────────────────┘
                              │
            ┌─────────────────┼─────────────────┬──────────────────┬──────────────────┐
            │                 │                 │                  │                  │
            ▼                 ▼                 ▼                  ▼                  ▼
    ┌──────────────┐  ┌──────────────┐ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │  Product     │  │  Copywriter  │ │   Pricing    │  │ Compliance   │  │   Growth     │
    │  Manager     │  │    Agent     │ │  Strategist  │  │   Officer    │  │  Engineer    │
    └──────────────┘  └──────────────┘ └──────────────┘  └──────────────┘  └──────────────┘
```

## Agents et Responsabilités

### 1. ProductManagerAgent
```
Role: Product Management
├── PRD Generation
├── User Stories Creation
├── Roadmap Planning
└── Feature Prioritization (RICE)

Task Types:
├── prd
├── user_story
├── roadmap
└── prioritization

Output Format: Markdown
Expertise: Agile, RICE, User-centric design
```

### 2. CopywriterAgent
```
Role: Marketing & UX Copy
├── Landing Page Copy
├── Email Campaigns
├── CTA Variations
├── Microcopy UX
├── Ad Copy (Google, FB, LinkedIn)
└── SEO Content

Task Types:
├── landing_page
├── email
├── cta
├── microcopy
├── ad
└── seo

Output Format: Markdown with variations
Expertise: AIDA, Conversion optimization, Brand voice
```

### 3. PricingStrategistAgent
```
Role: Monetization Strategy
├── Pricing Model Selection
├── Pricing Tiers Design
├── Financial Metrics Analysis
├── Pricing Optimization
└── Expansion Revenue Strategy

Task Types:
├── pricing_model
├── tiers
├── metrics
├── optimization
└── expansion

Output Format: Markdown with tables & calculations
Expertise: LTV, CAC, SaaS metrics, Pricing psychology
```

### 4. ComplianceOfficerAgent
```
Role: Legal & Data Protection
├── Compliance Audits (GDPR, CCPA, LGPD)
├── Privacy Policy Generation
├── Data Flow Mapping
├── Consent Mechanisms
├── User Rights Implementation
└── DPIA Conduction

Task Types:
├── audit
├── policy
├── data_mapping
├── consent
├── rights
└── dpia

Output Format: Markdown with checklists & risk levels
Expertise: GDPR, CCPA, Privacy by Design, RLS
```

### 5. GrowthEngineerAgent
```
Role: Growth & Experimentation
├── Feature Flags Implementation
├── A/B Test Design
├── Funnel Optimization
├── Retention Improvement
├── Experiment Design
└── Growth Loops Creation

Task Types:
├── feature_flag
├── ab_test
├── funnel
├── retention
├── experiment
└── growth_loop

Output Format: Markdown + Code (TypeScript, SQL, React)
Expertise: A/B testing, Statistics, AARRR, Growth loops
```

## Data Flow

### Request Flow
```
User/System Request
        │
        ▼
┌──────────────────┐
│  Agent.execute() │
│  (async)         │
└──────────────────┘
        │
        ├─── 1. Parse task_type
        │
        ├─── 2. Build prompt (specific to task)
        │
        ├─── 3. Call LLM via OpenRouter
        │         │
        │         ▼
        │    ┌──────────────────┐
        │    │ OpenRouter API   │
        │    │ (LLM: GPT-4o)    │
        │    └──────────────────┘
        │         │
        ├─── 4. Receive response
        │
        ├─── 5. Add to memory
        │
        └─── 6. Return formatted result
                │
                ▼
        ┌──────────────────┐
        │   Result Dict    │
        │ {                │
        │   status: "...", │
        │   output: "...", │
        │   metadata: {...}│
        │ }                │
        └──────────────────┘
```

### Memory Management
```
Agent Memory (per instance)
├── Conversation History
│   ├── {"role": "user", "content": "..."}
│   ├── {"role": "assistant", "content": "..."}
│   └── ... (chronological)
│
├── Operations
│   ├── add_to_memory(role, content)
│   ├── get_memory() → List[Dict]
│   └── clear_memory()
│
└── Persistence: In-memory only (cleared on restart)
```

## LLM Integration

### OpenRouter Integration
```
BaseAgent.call_llm()
        │
        ▼
┌─────────────────────────────────┐
│  OpenRouter API                 │
│  https://openrouter.ai/api/v1/  │
│  /chat/completions              │
└─────────────────────────────────┘
        │
        ├─── Headers:
        │    ├── Authorization: Bearer {api_key}
        │    ├── HTTP-Referer: {frontend_url}
        │    ├── X-Title: "Devora"
        │    └── Content-Type: application/json
        │
        ├─── Payload:
        │    ├── model: "openai/gpt-4o" (default)
        │    └── messages: [
        │         {role: "system", content: "..."},
        │         {role: "user", content: "..."}
        │        ]
        │
        └─── Response:
             └── choices[0].message.content
```

### Supported Models
- Default: `openai/gpt-4o`
- Alternative: `anthropic/claude-3.5-sonnet`
- Premium: `anthropic/claude-opus-4.5`
- Reasoning: `openai/o1`
- Any OpenRouter model

## System Prompts

Chaque agent a un `system_prompt` unique qui définit:
- Son expertise
- Ses responsabilités
- Ses principes de travail
- Le format de sortie attendu

```python
# Exemple: ProductManagerAgent
system_prompt = """
Tu es un Product Manager expert avec 10+ ans d'expérience.

Responsabilités:
- Créer des PRD détaillés et actionnables
- Rédiger des user stories au format Agile
- Définir des roadmaps avec priorisation RICE
...

Principes:
- User-centric: partir du besoin utilisateur
- Data-driven: baser sur des métriques
- Itératif: privilégier MVP
...

Format de sortie:
- Structuré en markdown
- Sections claires et numérotées
- Critères mesurables
...
"""
```

## Workflows Multi-Agents

### Exemple: Lancement Feature
```
Séquence:
1. ProductManager.execute({task_type: "prd"})
        │
        ▼
   PRD Generated
        │
        ▼
2. ComplianceOfficer.execute({task_type: "audit"})
        │
        ▼
   Compliance Check (OK/Issues)
        │
        ▼
3. Copywriter.execute({task_type: "microcopy"})
        │
        ▼
   Copy Created
        │
        ▼
4. GrowthEngineer.execute({task_type: "feature_flag"})
        │
        ▼
   Feature Flag Setup
        │
        ▼
   FEATURE READY TO SHIP
```

### Exemple: Optimisation Pricing
```
Séquence:
1. PricingStrategist.execute({task_type: "metrics"})
        │
        ▼
   Current Metrics Analyzed
        │
        ▼
2. PricingStrategist.execute({task_type: "tiers"})
        │
        ▼
   New Tiers Designed
        │
        ▼
3. Copywriter.execute({task_type: "landing_page"})
        │
        ▼
   Pricing Page Copy
        │
        ▼
4. GrowthEngineer.execute({task_type: "ab_test"})
        │
        ▼
   A/B Test Setup
        │
        ▼
   PRICING OPTIMIZATION LIVE
```

## Error Handling

```python
try:
    result = await agent.execute(task)
    if result["status"] == "success":
        # Process result
        output = result["output"]
    else:
        # Handle error
        error = result["output"]
except Exception as e:
    # LLM call failed
    logger.error(f"Agent execution failed: {e}")
```

## Performance Considerations

### Async Architecture
- All LLM calls are asynchronous (`async/await`)
- Agents can be called in parallel for independent tasks
- Timeout: 120 seconds per LLM call

### Memory
- In-memory conversation history (per agent instance)
- No automatic cleanup (call `clear_memory()` if needed)
- No persistence (lost on restart)

### Caching
- No built-in caching (roadmap item)
- Every call makes a fresh LLM request

## Security

### API Key Management
```python
# ✅ GOOD: Environment variable
api_key = os.environ.get("OPENROUTER_API_KEY")

# ✅ GOOD: Secret manager
api_key = get_secret("OPENROUTER_API_KEY")

# ❌ BAD: Hardcoded
api_key = "sk-or-v1-..."  # NEVER DO THIS
```

### Data Handling
- Agents don't persist sensitive data
- Conversation memory is ephemeral
- All data sent to LLM via HTTPS
- No local file storage

## Testing

### Unit Tests (Recommended)
```python
import pytest
from business_squad import ProductManagerAgent

@pytest.mark.asyncio
async def test_product_manager_prd():
    pm = ProductManagerAgent(api_key="test-key")
    result = await pm.execute({
        "task_type": "prd",
        "context": "Test feature"
    })
    assert result["status"] == "success"
    assert "PRD" in result["output"]
```

### Integration Tests
```python
@pytest.mark.asyncio
async def test_multi_agent_workflow():
    api_key = os.environ.get("OPENROUTER_API_KEY")

    pm = ProductManagerAgent(api_key=api_key)
    compliance = ComplianceOfficerAgent(api_key=api_key)

    # 1. Generate PRD
    prd_result = await pm.generate_prd("New feature")

    # 2. Check compliance
    audit_result = await compliance.audit_compliance(
        product_context=prd_result,
        data_types=["email"]
    )

    assert audit_result["risk_level"] in ["low", "medium", "high"]
```

## Monitoring (Roadmap)

### Metrics to Track
```
Agent Performance
├── Latency (ms)
│   ├── p50
│   ├── p95
│   └── p99
├── Token Usage
│   ├── Input tokens
│   ├── Output tokens
│   └── Cost ($)
├── Success Rate (%)
└── Error Rate (%)

Usage Stats
├── Calls per agent
├── Most used task_types
└── Average response length
```

## Extensibility

### Adding a New Agent
```python
# 1. Create new file: new_agent.py
from base_agent import BaseAgent

class NewAgent(BaseAgent):
    def __init__(self, api_key, model="openai/gpt-4o"):
        super().__init__(name="NewAgent", api_key=api_key, model=model)
        self.system_prompt = "Your system prompt..."

    async def execute(self, task):
        # Your implementation
        pass

# 2. Add to __init__.py
from .new_agent import NewAgent
__all__ = [..., "NewAgent"]
```

### Adding a New Task Type
```python
# In existing agent
async def execute(self, task):
    task_type = task.get("task_type")

    if task_type == "new_task_type":
        user_prompt = self._build_new_task_prompt(...)
        # ... rest of implementation

def _build_new_task_prompt(self, ...):
    return f"""..."""
```

## Deployment

### Environment Variables
```bash
export OPENROUTER_API_KEY="sk-or-v1-..."
export FRONTEND_URL="https://devora.app"  # for OpenRouter HTTP-Referer
```

### Docker (Example)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY orchestration/ /app/orchestration/
COPY backend/agents/base_agent.py /app/backend/agents/

RUN pip install httpx

ENV OPENROUTER_API_KEY=""
ENV FRONTEND_URL="http://localhost:3000"

CMD ["python", "-m", "orchestration.agents.business_squad.example_usage"]
```

## License

Propriétaire - Devora Team
