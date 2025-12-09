# Devora - SaaS AppBuilder Context

## Project Overview

**Nom**: Devora Ultimate v12
**Type**: SaaS AppBuilder with AI Code Generation
**Status**: Development

## Tech Stack

### Frontend
- React 18
- React Router DOM
- Tailwind CSS + shadcn/ui
- Axios for HTTP
- Monaco Editor (code editing)
- WebContainer API (live preview)

### Backend
- FastAPI (Python)
- Motor (async MongoDB driver)
- MongoDB (database)
- OpenRouter API (AI code generation)

### Integrations
- Stripe (payments & subscriptions)
- GitHub (repo management, deployment)
- Vercel (deployment)

## Key Features

1. **AI Code Generation**: Multi-agent system (Orchestrator, Planner, Coder, Tester, Reviewer)
2. **Live Preview**: WebContainer-based preview in browser
3. **Template System**: Pre-built templates (Landing Page, Dashboard, E-commerce)
4. **Deployment**: One-click deploy to GitHub + Vercel
5. **SuperAdmin Dashboard**: Analytics, user management, Stripe config

## Directory Structure

```
saasdevora-ultimatev12/
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── pages/          # Page components
│   │   ├── contexts/       # React contexts (Auth)
│   │   └── styles/         # CSS files
│   └── public/
│
├── backend/                # FastAPI backend
│   ├── agents/             # AI generation agents
│   │   ├── orchestrator.py
│   │   ├── orchestrator_v2.py
│   │   ├── planner.py
│   │   ├── coder.py
│   │   ├── frontend_agent.py
│   │   ├── backend_agent.py
│   │   └── ...
│   ├── routes_*.py         # API route modules
│   └── server.py           # Main FastAPI app
│
└── docs/                   # Documentation
```

## Current Users

- **test@devora.com**: Test admin account (password: Test123!)

## Environment Variables

### Backend (.env)
- MONGO_URL
- JWT_SECRET
- STRIPE_SECRET_KEY
- STRIPE_WEBHOOK_SECRET

### Frontend
- REACT_APP_API_URL (default: http://localhost:8000)

## Recent Changes (Session 2024-12-09)

1. Fixed `'list' object has no attribute 'get'` error in code generation
2. Added starter files for new projects (index.html, style.css, script.js)
3. Improved Navigation with user dropdown and admin access
4. Created password reset utility script
