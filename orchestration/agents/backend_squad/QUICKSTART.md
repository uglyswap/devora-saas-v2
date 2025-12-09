# Backend Squad - Quick Start Guide

Guide de démarrage rapide pour utiliser les agents du Backend Squad.

---

## Installation Rapide

### 1. Vérifier les Prérequis

```bash
# Python 3.11+
python --version

# Node.js 18+ (optionnel, pour Next.js)
node --version
```

### 2. Installer les Dépendances

```bash
# Dépendances pour les agents
pip install httpx

# Dépendances backend (si génération FastAPI)
pip install fastapi uvicorn pydantic sqlalchemy
pip install python-jose passlib bcrypt

# Dépendances intégrations (selon besoins)
pip install stripe sendgrid boto3 authlib
```

### 3. Configurer l'API Key

```bash
# OpenRouter API Key (requis)
export OPENROUTER_API_KEY="sk-or-v1-your-key-here"

# Vérifier
echo $OPENROUTER_API_KEY
```

---

## Utilisation en 3 Minutes

### Exemple Minimal

```python
import asyncio
import os
from orchestration.agents.backend_squad import (
    APIArchitect,
    BackendDeveloper,
    IntegrationSpecialist
)

async def quick_example():
    api_key = os.environ["OPENROUTER_API_KEY"]

    # 1. Design API
    api_architect = APIArchitect(api_key=api_key)
    api_result = await api_architect.execute({
        "requirements": ["User CRUD", "Authentication"],
        "data_models": [
            {
                "name": "User",
                "fields": [
                    {"name": "email", "type": "string"},
                    {"name": "name", "type": "string"}
                ]
            }
        ],
        "api_type": "rest",
        "auth_type": "jwt"
    })

    print(f"✓ API designed with {len(api_result['endpoints'])} endpoints")

    # 2. Generate Backend Code
    backend_dev = BackendDeveloper(api_key=api_key)
    backend_result = await backend_dev.execute({
        "api_spec": api_result["api_spec"],
        "framework": "fastapi",
        "database": "postgresql",
        "auth_type": "jwt"
    })

    print(f"✓ Generated {len(backend_result['files'])} files")

    # 3. Add Integrations (optional)
    integration = IntegrationSpecialist(api_key=api_key)
    integration_result = await integration.execute({
        "integrations": ["stripe"],
        "framework": "fastapi"
    })

    print(f"✓ Integrated: {integration_result['integrations']}")

    # Save files
    for file in backend_result["files"]:
        print(f"  - {file['name']}")

if __name__ == "__main__":
    asyncio.run(quick_example())
```

### Exécuter

```bash
python quick_example.py
```

---

## Exemples de Cas d'Usage

### 1. API REST Simple

```python
api_architect = APIArchitect(api_key=key)
result = await api_architect.execute({
    "requirements": ["Blog posts CRUD"],
    "data_models": [
        {"name": "Post", "fields": [
            {"name": "title", "type": "string"},
            {"name": "content", "type": "text"}
        ]}
    ],
    "api_type": "rest",
    "auth_type": "jwt"
})
```

### 2. Backend FastAPI Complet

```python
backend_dev = BackendDeveloper(api_key=key)
result = await backend_dev.execute({
    "api_spec": api_spec,
    "framework": "fastapi",
    "database": "postgresql",
    "auth_type": "jwt",
    "features": ["crud", "auth", "rate_limiting"]
})
```

### 3. Intégration Stripe

```python
integration = IntegrationSpecialist(api_key=key)
result = await integration.generate_stripe_integration(
    features=["checkout", "subscriptions", "webhooks"],
    framework="fastapi"
)
```

### 4. OAuth Providers

```python
result = await integration.generate_oauth_integration(
    providers=["google", "github"],
    framework="nextjs"
)
```

---

## Factory Pattern (Recommandé)

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

## Workflow Complet (Production)

```python
async def generate_full_backend():
    """Generate complete production-ready backend."""

    api_key = os.environ["OPENROUTER_API_KEY"]

    # Step 1: API Architecture
    print("[1/3] Designing API...")
    api_architect = APIArchitect(api_key=api_key)
    api_design = await api_architect.execute({
        "requirements": [
            "User authentication",
            "Blog post management",
            "Comments system"
        ],
        "data_models": [...],
        "api_type": "rest",
        "auth_type": "jwt",
        "versioning": True
    })

    # Step 2: Backend Implementation
    print("[2/3] Implementing backend...")
    backend_dev = BackendDeveloper(api_key=api_key)
    backend_code = await backend_dev.execute({
        "api_spec": api_design["api_spec"],
        "framework": "fastapi",
        "database": "postgresql",
        "auth_type": "jwt",
        "features": [
            "crud_operations",
            "authentication",
            "pagination",
            "rate_limiting",
            "logging"
        ]
    })

    # Step 3: Third-party Integrations
    print("[3/3] Setting up integrations...")
    integration = IntegrationSpecialist(api_key=api_key)
    integrations = await integration.execute({
        "integrations": ["stripe", "sendgrid"],
        "framework": "fastapi",
        "requirements": {
            "stripe": {
                "features": ["checkout", "subscriptions", "webhooks"]
            },
            "sendgrid": {
                "features": ["transactional_emails"]
            }
        }
    })

    # Combine results
    all_files = (
        api_design["schemas"] +
        backend_code["files"] +
        integrations["files"]
    )

    # Save files
    for file in all_files:
        save_file(file["name"], file["content"])

    # Print summary
    print(f"\n✅ Generated {len(all_files)} files")
    print(f"📦 Dependencies: {backend_code['dependencies']}")
    print(f"🔐 Env vars needed: {list(integrations['env_vars'].keys())}")

    return {
        "files": all_files,
        "dependencies": backend_code["dependencies"],
        "env_vars": integrations["env_vars"],
        "setup": backend_code["setup_instructions"]
    }
```

---

## Commandes Utiles

### Tests

```bash
# Tester les agents (sans appel API)
python orchestration/agents/backend_squad/test_backend_squad.py

# Avec pytest
pytest orchestration/agents/backend_squad/test_backend_squad.py -v
```

### Exemples

```bash
# Exemples complets avec mocks
python orchestration/agents/backend_squad/example_usage.py
```

### Debugging

```python
# Activer logging détaillé
import logging
logging.basicConfig(level=logging.DEBUG)

# Voir les prompts envoyés au LLM
agent = APIArchitect(api_key=key)
agent.logger.setLevel(logging.DEBUG)
```

---

## Structure des Fichiers Générés

### FastAPI

```
app/
├── main.py                     # Application FastAPI
├── api/
│   └── v1/
│       ├── api.py              # Router principal
│       └── endpoints/
│           ├── auth.py         # Auth endpoints
│           ├── users.py        # User CRUD
│           └── [resource].py   # Resource endpoints
├── core/
│   ├── config.py               # Configuration
│   ├── database.py             # Database connection
│   └── security.py             # JWT, password hashing
├── middleware/
│   ├── logging.py              # Request logging
│   ├── cors.py                 # CORS config
│   └── rate_limit.py           # Rate limiting
├── models/
│   ├── user.py                 # SQLAlchemy models
│   └── [resource].py
├── schemas/
│   ├── user.py                 # Pydantic schemas
│   └── [resource].py
├── services/
│   └── user_service.py         # Business logic
├── integrations/
│   ├── stripe.py               # Stripe integration
│   └── sendgrid.py             # Email integration
└── background/
    └── tasks.py                # Celery tasks
```

### Next.js

```
app/
├── api/
│   ├── auth/
│   │   └── [...nextauth]/route.ts
│   ├── users/
│   │   ├── route.ts            # GET, POST
│   │   └── [id]/route.ts       # GET, PUT, DELETE
│   └── stripe/
│       └── webhook/route.ts
├── lib/
│   ├── auth.ts                 # Auth utilities
│   ├── db.ts                   # Database client
│   └── stripe.ts               # Stripe client
├── middleware.ts               # Global middleware
└── actions/
    └── users.ts                # Server Actions
```

---

## Environment Variables

### Exemple .env

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Auth
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Stripe (if using)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# SendGrid (if using)
SENDGRID_API_KEY=SG.xxx
SENDGRID_FROM_EMAIL=noreply@example.com

# OAuth (if using)
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxx
GITHUB_CLIENT_ID=xxx
GITHUB_CLIENT_SECRET=xxx

# Redis (optional, for caching)
REDIS_URL=redis://localhost:6379
```

---

## Dépannage

### Erreur: BaseAgent not found

```python
# Assurez-vous que le path est correct
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../backend'))
from agents.base_agent import BaseAgent
```

### Erreur: OpenRouter API

```bash
# Vérifier la clé API
echo $OPENROUTER_API_KEY

# Tester la connexion
curl https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer $OPENROUTER_API_KEY"
```

### Erreur: Module not found

```bash
# Installer les dépendances manquantes
pip install httpx fastapi pydantic
```

---

## Prochaines Étapes

Après avoir généré votre backend :

1. **Configurer l'environnement**
   ```bash
   cp .env.example .env
   # Éditer .env avec vos valeurs
   ```

2. **Installer les dépendances**
   ```bash
   # FastAPI
   pip install -r requirements.txt

   # Next.js
   npm install
   ```

3. **Initialiser la database**
   ```bash
   # Avec Alembic (FastAPI)
   alembic upgrade head

   # Avec Prisma (Next.js)
   npx prisma migrate dev
   ```

4. **Lancer le serveur**
   ```bash
   # FastAPI
   uvicorn app.main:app --reload

   # Next.js
   npm run dev
   ```

5. **Tester l'API**
   - FastAPI: http://localhost:8000/docs
   - Next.js: http://localhost:3000/api

---

## Ressources

- **Documentation complète:** [README.md](./README.md)
- **Exemples détaillés:** [example_usage.py](./example_usage.py)
- **Tests:** [test_backend_squad.py](./test_backend_squad.py)
- **Spécifications:** [DELIVERABLE.md](./DELIVERABLE.md)

---

## Support

Pour des questions ou problèmes :
1. Consulter le README.md pour la doc complète
2. Vérifier example_usage.py pour des exemples
3. Exécuter les tests pour validation

---

**Prêt en 3 minutes - Production-ready en 30 minutes** ⚡
