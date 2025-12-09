# Backend Squad - Devora Orchestration System

Équipe d'agents spécialisés dans le développement backend, la conception d'API et les intégrations tierces.

## Agents

### 1. API Architect (`api_architect.py`)

**Responsabilités :**
- Conception d'architectures API REST et GraphQL
- Génération de documentation OpenAPI/Swagger
- Définition de schémas de validation (Pydantic pour Python, Zod pour TypeScript)
- Planification de stratégies de versioning d'API
- Conception de flux d'authentification et d'autorisation

**Capacités :**
- Design patterns API (REST, GraphQL, RPC)
- Spécification OpenAPI 3.1 complète
- Stratégies de versioning (URI, Header, Content negotiation)
- Authentification (JWT, OAuth2, API Keys)
- Rate limiting et caching
- Pagination, filtrage, tri
- Documentation complète

**Utilisation :**
```python
from orchestration.agents.backend_squad import APIArchitect

api_architect = APIArchitect(api_key="your-openrouter-key")

result = await api_architect.execute({
    "requirements": [
        "User management CRUD",
        "Authentication with JWT",
        "Blog post management"
    ],
    "data_models": [
        {"name": "User", "fields": ["email", "password", "name"]},
        {"name": "Post", "fields": ["title", "content", "author_id"]}
    ],
    "api_type": "rest",
    "auth_type": "jwt",
    "versioning": True
})

# Output:
# - api_spec: OpenAPI specification
# - schemas: Pydantic/Zod validation schemas
# - endpoints: Endpoint definitions
# - documentation: API documentation
```

**Méthodes principales :**
- `execute(task)` - Conception complète de l'API
- `generate_openapi_spec(endpoints, schemas)` - Génération OpenAPI 3.1
- `generate_validation_schemas(data_models, language)` - Schémas Pydantic/Zod
- `design_versioning_strategy(api_spec)` - Stratégie de versioning

---

### 2. Backend Developer (`backend_developer.py`)

**Responsabilités :**
- Implémentation de code backend (FastAPI ou Next.js API Routes)
- Création de systèmes d'authentification (JWT, OAuth2, Session)
- Développement de middleware (logging, CORS, rate limiting, auth)
- Implémentation de background jobs (Celery, Bull)
- Optimisation de requêtes database
- Gestion d'erreurs et logging

**Tech Stack supporté :**
- **Python:** FastAPI, SQLAlchemy, Celery, Redis
- **TypeScript:** Next.js API Routes, Prisma, Bull, NextAuth
- **Databases:** PostgreSQL, MongoDB, Supabase
- **Auth:** JWT, OAuth2, NextAuth, Supabase Auth

**Utilisation :**
```python
from orchestration.agents.backend_squad import BackendDeveloper

backend_dev = BackendDeveloper(api_key="your-key")

result = await backend_dev.execute({
    "api_spec": api_spec_from_architect,  # From APIArchitect
    "framework": "fastapi",  # or "nextjs"
    "database": "postgresql",
    "auth_type": "jwt",
    "features": ["crud", "auth", "background_jobs"]
})

# Output:
# - files: Liste de fichiers de code générés
# - dependencies: Packages requis (requirements.txt ou package.json)
# - setup_instructions: Guide d'installation et de démarrage
```

**Méthodes principales :**
- `execute(task)` - Implémentation backend complète
- `generate_authentication(auth_type, framework)` - Système d'auth
- `generate_middleware(types, framework)` - Middlewares
- `generate_background_jobs(jobs, framework)` - Background jobs

**Structure de code générée (FastAPI) :**
```
app/
  main.py                    # Application FastAPI
  api/v1/endpoints/          # Routes API
  core/                      # Configuration, sécurité, database
  middleware/                # Logging, CORS, rate limiting
  models/                    # SQLAlchemy models
  schemas/                   # Pydantic schemas
  services/                  # Logique métier
  background/tasks.py        # Celery tasks
```

**Structure de code générée (Next.js) :**
```
app/
  api/                       # API Routes
    auth/[...nextauth]/route.ts
    [resource]/route.ts
  lib/                       # Utilities
    auth.ts
    db.ts
  middleware.ts              # Middleware global
  actions/                   # Server Actions
```

---

### 3. Integration Specialist (`integration_specialist.py`)

**Responsabilités :**
- Intégration Stripe (paiements, subscriptions, webhooks)
- Configuration OAuth providers (Google, GitHub, Microsoft, etc.)
- Implémentation de webhooks (entrants et sortants)
- Intégration d'APIs tierces (SendGrid, Twilio, AWS S3, etc.)
- Systèmes event-driven
- Vérification de signatures webhook
- Gestion de rate limits et retries

**Intégrations supportées :**
- **Paiements:** Stripe, PayPal, Square
- **Auth:** Google OAuth, GitHub, Microsoft, Auth0
- **Email:** SendGrid, Mailgun, AWS SES, Resend
- **SMS:** Twilio, Vonage
- **Storage:** AWS S3, Cloudflare R2, Supabase Storage
- **Analytics:** Google Analytics, Mixpanel, Segment
- **Communication:** Slack, Discord, Telegram

**Utilisation :**
```python
from orchestration.agents.backend_squad import IntegrationSpecialist

integration_specialist = IntegrationSpecialist(api_key="your-key")

result = await integration_specialist.execute({
    "integrations": ["stripe", "google_oauth", "sendgrid"],
    "framework": "fastapi",  # or "nextjs"
    "requirements": {
        "stripe": ["checkout", "subscriptions", "webhooks"],
        "sendgrid": ["transactional_emails", "templates"]
    }
})

# Output:
# - files: Fichiers d'intégration
# - env_vars: Variables d'environnement requises
# - setup_instructions: Guide de configuration
```

**Méthodes principales :**
- `execute(task)` - Implémentation de toutes les intégrations
- `generate_stripe_integration(features, framework)` - Stripe complet
- `generate_oauth_integration(providers, framework)` - OAuth providers
- `generate_webhook_system(events, framework)` - Système webhook
- `generate_email_integration(provider, framework)` - Service email
- `generate_storage_integration(provider, framework)` - Cloud storage

**Exemple de webhook Stripe :**
```python
# FastAPI
@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig, STRIPE_WEBHOOK_SECRET
        )

        if event.type == "checkout.session.completed":
            await handle_checkout_completed(event.data.object)
        elif event.type == "customer.subscription.updated":
            await handle_subscription_updated(event.data.object)

        return {"status": "success"}
    except Exception as e:
        raise HTTPException(400, detail=str(e))
```

---

## Utilisation en Orchestration

### Workflow complet Backend Squad

```python
from orchestration.agents.backend_squad import (
    APIArchitect,
    BackendDeveloper,
    IntegrationSpecialist
)

# 1. Conception API
api_architect = APIArchitect(api_key=api_key)
api_design = await api_architect.execute({
    "requirements": user_requirements,
    "data_models": data_models,
    "api_type": "rest",
    "auth_type": "jwt"
})

# 2. Implémentation Backend
backend_dev = BackendDeveloper(api_key=api_key)
backend_code = await backend_dev.execute({
    "api_spec": api_design["api_spec"],
    "framework": "fastapi",
    "database": "postgresql",
    "auth_type": "jwt"
})

# 3. Intégrations
integration_specialist = IntegrationSpecialist(api_key=api_key)
integrations = await integration_specialist.execute({
    "integrations": ["stripe", "sendgrid"],
    "framework": "fastapi"
})

# 4. Combiner tous les fichiers
all_files = (
    api_design["schemas"] +
    backend_code["files"] +
    integrations["files"]
)

# 5. Générer instructions complètes
setup_instructions = f"""
{backend_code["setup_instructions"]}

## Intégrations
{integrations["setup_instructions"]}

## Environment Variables
{format_env_vars(integrations["env_vars"])}
"""
```

### Factory Pattern

```python
from orchestration.agents.backend_squad import get_agent, list_agents

# Lister les agents disponibles
agents = list_agents()
for name, info in agents.items():
    print(f"{name}: {info['description']}")

# Créer un agent dynamiquement
agent = get_agent("api_architect", api_key="your-key")
result = await agent.execute(task)
```

---

## Installation

### Dépendances

Les agents du Backend Squad dépendent de `BaseAgent` du backend principal :

```python
# Path setup dans chaque agent
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../backend'))
from agents.base_agent import BaseAgent
```

### Packages Python requis

```bash
# Installation des dépendances backend
pip install fastapi uvicorn pydantic sqlalchemy
pip install python-jose passlib bcrypt
pip install stripe sendgrid boto3 authlib
pip install httpx  # Pour appels LLM via OpenRouter
```

---

## Tests

Exécuter les tests :

```bash
# Avec pytest
pytest orchestration/agents/backend_squad/test_backend_squad.py -v

# Test manuel
python orchestration/agents/backend_squad/test_backend_squad.py
```

---

## Architecture

```
orchestration/agents/backend_squad/
├── __init__.py                   # Exports & factory functions
├── api_architect.py              # API design agent
├── backend_developer.py          # Backend implementation agent
├── integration_specialist.py     # Integrations agent
├── test_backend_squad.py         # Tests
└── README.md                     # Cette documentation
```

---

## Best Practices

### 1. Sécurité
- Toujours valider les signatures webhook
- Ne jamais committer les clés API
- Utiliser des environnements séparés (dev/prod)
- Implémenter rate limiting
- Hasher les passwords avec bcrypt
- Utiliser HTTPS uniquement en production

### 2. Performance
- Utiliser async/await pour I/O
- Implémenter du caching (Redis)
- Paginer les résultats
- Indexer les colonnes database
- Utiliser background jobs pour tâches lourdes

### 3. Qualité du Code
- Types stricts (Pydantic, TypeScript)
- Docstrings complètes
- Gestion d'erreurs exhaustive
- Logging approprié
- Tests unitaires et d'intégration

---

## Roadmap

- [ ] Support GraphQL avec Strawberry/Pothos
- [ ] Génération de tests automatiques
- [ ] Monitoring et observabilité (Sentry, DataDog)
- [ ] Rate limiting distribué (Redis)
- [ ] Circuit breaker pour intégrations tierces
- [ ] Support WebSockets avancé
- [ ] Génération de documentation interactive
- [ ] CI/CD pipeline templates

---

## Contribution

Pour ajouter un nouvel agent au Backend Squad :

1. Créer un fichier `new_agent.py` héritant de `BaseAgent`
2. Implémenter la méthode `async def execute(task)`
3. Ajouter des méthodes auxiliaires si nécessaire
4. Mettre à jour `__init__.py` avec le nouvel agent
5. Ajouter tests dans `test_backend_squad.py`
6. Documenter dans ce README

---

**Backend Squad - Production-Ready Backend Code Generation** 🚀
