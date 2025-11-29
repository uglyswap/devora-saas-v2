# Changelog

All notable changes to Devora SaaS V2 are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - 2024-11-29

### Added

#### 🤖 Full-Stack Agentic Architecture
- **OrchestratorV2**: New parallel multi-agent orchestrator
  - Parallel execution of Frontend, Backend, and Database agents
  - Automatic context compression for long conversations
  - Progress streaming via SSE
  - Max 2 iterations with review feedback loop

- **ArchitectAgent**: Requirements analysis and architecture design
  - Template selection (SaaS, E-commerce, Blog, Dashboard, API)
  - Data model definition
  - Integration planning (Stripe, Supabase, etc.)

- **FrontendAgent**: Next.js 14+ code generation
  - App Router structure
  - React Server Components
  - Tailwind CSS + shadcn/ui
  - TypeScript strict mode

- **BackendAgent**: API and server-side code
  - Next.js API Routes
  - Server Actions
  - Stripe integration (webhooks, checkout, portal)
  - Authentication middleware

- **DatabaseAgent**: Supabase schema generation
  - PostgreSQL tables with proper types
  - Row Level Security (RLS) policies
  - Database migrations
  - TypeScript type generation

- **ContextCompressor**: Intelligent token management
  - Automatic context compression when approaching limits
  - Preserves recent messages and important code sections
  - Smart summarization of conversation history

#### 📦 Templates
- **SaaS Starter Template**: Complete SaaS boilerplate
  - Authentication (Supabase Auth)
  - Billing (Stripe subscriptions)
  - Dashboard with metrics
  - Settings & profile management
  - Marketing landing page

#### 🔌 New API Endpoint
- `POST /api/generate/fullstack`: Full-stack project generation
  - Uses OrchestratorV2 for multi-agent coordination
  - Streams progress via Server-Sent Events
  - Returns complete Next.js 14+ project

### Fixed

#### 🐛 Bug Fixes
- **BUG 1**: Fixed file tabs disappearing on re-render
  - Added `fileTabsKey` state for stable React key
  - Tabs now persist correctly during code updates

- **BUG 2**: Fixed ZIP download functionality
  - Integrated JSZip for proper file packaging
  - All project files now included in download

- **BUG 3**: Fixed admin dropdown readability
  - Added explicit option colors: `[&>option]:text-black [&>option]:bg-white`
  - Dropdowns now readable in both light and dark modes

- **BUG 4**: Fixed AI memory/context persistence
  - `conversation_history` now saved with projects
  - History synced between frontend and backend
  - Clear conversation button added

- **BUG 5**: Implemented context compression
  - `ContextCompressor` class for token management
  - `compress_context_if_needed()` utility function
  - Integrated in OrchestratorV2 workflow

### Changed
- Updated backend version to 3.0.0
- Improved error handling in all agents
- Enhanced logging throughout the system

### Technical Details

#### Dependencies Added
- Backend: No new dependencies (uses existing openai, pydantic)
- Frontend: JSZip (already in package.json)

#### Files Modified
- `backend/server.py`: Added `/api/generate/fullstack` endpoint
- `backend/agents/__init__.py`: Exported new agents
- `frontend/src/pages/EditorPage.jsx`: Bug fixes 1, 2, 4
- `frontend/src/pages/AdminPanel.jsx`: Bug fix 3

#### Files Added
- `backend/agents/orchestrator_v2.py`
- `backend/agents/architect_agent.py`
- `backend/agents/frontend_agent.py`
- `backend/agents/backend_agent.py`
- `backend/agents/database_agent.py`
- `backend/agents/context_compressor.py`
- `backend/templates/saas_starter.py`
- `backend/templates/__init__.py`

---

## [2.0.0] - 2024-11-15

### Added
- Multi-agent agentic mode
- Stripe billing integration
- GitHub export feature
- Vercel deployment feature
- Admin panel

### Changed
- Migrated to React 19
- Upgraded to Tailwind CSS v4
- New UI with shadcn/ui components

---

## [1.0.0] - 2024-10-01

### Added
- Initial release
- Basic code generation with OpenRouter
- Project management
- Monaco Editor integration
- Live preview
