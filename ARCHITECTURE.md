# 🏗️ Architecture Devora SaaS V2

## Vue d'ensemble

Devora SaaS V2 est un générateur de code agentic basé sur l'IA, utilisant une architecture multi-agents pour produire des applications full-stack Next.js 14+.

## Stack Technologique

### Backend (Python/FastAPI)
```
backend/
├── server.py              # API FastAPI principale (v3.0.0)
├── agents/                # Système multi-agents
│   ├── orchestrator_v2.py # Orchestrateur parallèle
│   ├── architect_agent.py # Analyse & design
│   ├── frontend_agent.py  # Génération UI Next.js
│   ├── backend_agent.py   # API Routes & Auth
│   ├── database_agent.py  # Supabase schemas
│   ├── context_compressor.py # Gestion tokens
│   ├── reviewer.py        # Validation code
│   ├── planner.py         # Planification tâches
│   ├── coder.py           # Génération HTML/CSS/JS
│   └── tester.py          # Tests automatisés
├── templates/             # Templates de projets
│   └── saas_starter.py    # Template SaaS complet
└── requirements.txt       # Dépendances Python
```

### Frontend (React 19)
```
frontend/
├── src/
│   ├── App.js             # Routes principales
│   ├── pages/             # 11 pages
│   │   ├── HomePage.jsx   # Landing page
│   │   ├── Dashboard.jsx  # Liste projets
│   │   ├── EditorPage.jsx # Éditeur principal
│   │   ├── AdminPanel.jsx # Administration
│   │   ├── Billing.jsx    # Gestion abonnements
│   │   └── ...
│   ├── components/        # Composants UI
│   │   ├── ui/            # shadcn/ui
│   │   └── ...
│   └── contexts/          # React Context
│       └── AuthContext.jsx
└── package.json
```

## Architecture Multi-Agents

### Workflow OrchestratorV2

```
┌─────────────────────────────────────────────────────────────┐
│                      USER REQUEST                            │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   CONTEXT COMPRESSOR                         │
│  • Analyse tokens disponibles                                │
│  • Compression conversation si nécessaire                    │
│  • Préserve contexte récent (6 messages)                    │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   ARCHITECT AGENT                            │
│  • Analyse requirements                                      │
│  • Sélection template (SaaS, E-commerce, Blog, etc.)        │
│  • Définition data models & intégrations                    │
│  • Output: Architecture JSON                                 │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  FRONTEND   │  │   BACKEND   │  │  DATABASE   │
│   AGENT     │  │    AGENT    │  │    AGENT    │
│             │  │             │  │             │
│ • Pages     │  │ • API Routes│  │ • Schemas   │
│ • Components│  │ • Auth      │  │ • RLS       │
│ • Layouts   │  │ • Stripe    │  │ • Types     │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │
       └────────────────┼────────────────┘
                        │ (asyncio.gather - PARALLEL)
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    REVIEWER AGENT                            │
│  • Validation code généré                                    │
│  • Détection erreurs & suggestions                          │
│  • Décision: APPROVE ou ITERATE (max 2 iterations)          │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      OUTPUT                                  │
│  • Fichiers générés (Next.js 14+ App Router)                │
│  • package.json, tailwind.config.ts                         │
│  • .env.local.example                                        │
│  • Schemas Supabase avec RLS                                │
└─────────────────────────────────────────────────────────────┘
```

### Agents Spécialisés

| Agent | Responsabilité | Tech Output |
|-------|---------------|-------------|
| **ArchitectAgent** | Analyse requirements, sélection template | Architecture JSON |
| **FrontendAgent** | UI/UX, pages, composants | Next.js 14+, Tailwind, shadcn/ui |
| **BackendAgent** | API, Auth, Paiements | API Routes, Server Actions, Stripe |
| **DatabaseAgent** | Data modeling, sécurité | Supabase, PostgreSQL, RLS |
| **ReviewerAgent** | Validation, QA | Feedback, fix instructions |
| **ContextCompressor** | Gestion mémoire | Compression intelligente |

## API Endpoints

### Génération de Code

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/generate/openrouter` | POST | Génération simple (HTML/CSS/JS) |
| `/api/generate/agentic` | POST | Génération multi-agents classique |
| `/api/generate/fullstack` | POST | **Génération Full-Stack Next.js** |
| `/api/templates` | GET | Liste templates disponibles |

### Projets

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/projects` | GET | Liste tous les projets |
| `/api/projects` | POST | Créer un projet |
| `/api/projects/{id}` | GET | Détails d'un projet |
| `/api/projects/{id}` | PUT | Mettre à jour un projet |
| `/api/projects/{id}` | DELETE | Supprimer un projet |

### Export & Déploiement

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/github/export` | POST | Push vers GitHub |
| `/api/vercel/deploy` | POST | Déploiement Vercel |

### Paiements (Stripe)

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/stripe/checkout` | POST | Créer session checkout |
| `/api/stripe/webhook` | POST | Webhooks Stripe |

## Base de Données

### MongoDB Collections

```javascript
// Collection: projects
{
  _id: ObjectId,
  name: String,
  description: String,
  files: [
    { name: String, content: String, language: String }
  ],
  conversation_history: [
    { role: "user"|"assistant", content: String }
  ],
  github_repo_url: String,
  vercel_url: String,
  created_at: Date,
  updated_at: Date
}

// Collection: users (via Stripe)
{
  _id: ObjectId,
  email: String,
  stripe_customer_id: String,
  subscription_status: String,
  plan: String,
  created_at: Date
}
```

## Compression de Contexte

Le `ContextCompressor` gère intelligemment les limites de tokens:

```python
# Stratégie de compression
1. Estimation tokens (4 chars = 1 token)
2. Seuil: 85% de 128K tokens (GPT-4o)
3. Si dépassement:
   - Garde premier message (intent original)
   - Résume messages intermédiaires
   - Garde 6 derniers messages (contexte récent)
   - Tronque fichiers volumineux (garde imports, exports, fonctions)
```

## Sécurité

- **Auth**: Session-based avec cookies sécurisés
- **CORS**: Configuré pour domaines autorisés
- **Rate Limiting**: Protection API endpoints
- **Stripe Webhooks**: Signature validation
- **Environment Variables**: Secrets non exposés

## Performance

- **Génération parallèle**: Frontend/Backend/Database simultanés
- **SSE Streaming**: Progress en temps réel
- **Compression contexte**: Optimisation tokens LLM
- **MongoDB async**: motor driver pour non-blocking I/O
