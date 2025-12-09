# Devora - AI-Powered Code Generator SaaS

**Transform ideas into production-ready applications using AI multi-agent orchestration.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.1-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19.0.0-61DAFB.svg)](https://reactjs.org)
[![MongoDB](https://img.shields.io/badge/MongoDB-4.5.0-47A248.svg)](https://www.mongodb.com)

---

## 🌟 Overview

Devora is a **next-generation SaaS platform** that leverages AI multi-agent orchestration to generate complete, production-ready web applications. From simple landing pages to full-stack SaaS products with authentication, payments, and database integration.

### Key Features

- **🤖 Multi-Agent AI Orchestration** - Specialized agents for architecture, frontend, backend, and database
- **⚡ Full-Stack Generation** - Next.js 14+ applications with App Router, Server Actions, and Supabase
- **🎨 Modern UI Components** - Built with Tailwind CSS and shadcn/ui
- **🔐 Authentication Ready** - Supabase Auth with RLS policies
- **💳 Payment Integration** - Stripe subscriptions and webhooks
- **📦 Export & Deploy** - One-click GitHub export and Vercel deployment
- **💾 Persistent Memory** - Context-aware conversations using Memori SDK
- **🔄 Real-time Streaming** - SSE for live generation progress

---

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ and npm/yarn
- **Python** 3.10+
- **MongoDB** 4.4+
- **OpenRouter API Key** (for AI models)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/devora-transformation.git
cd devora-transformation
```

2. **Install Backend Dependencies**
```bash
cd backend
pip install -r requirements.txt
```

3. **Configure Environment Variables**
```bash
# Backend .env
cp .env.example .env
# Edit .env with your MongoDB URL and other settings
```

4. **Install Frontend Dependencies**
```bash
cd ../frontend
npm install
# or
yarn install
```

5. **Start the Services**

**Backend (Terminal 1):**
```bash
cd backend
uvicorn server:app --reload --port 8000
```

**Frontend (Terminal 2):**
```bash
cd frontend
npm start
```

6. **Access the Application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 📖 Documentation

- **[Architecture Guide](./docs/ARCHITECTURE.md)** - System architecture and design patterns
- **[Contributing Guide](./docs/CONTRIBUTING.md)** - How to contribute to the project
- **[API Documentation](./docs/api/openapi.yaml)** - Complete OpenAPI specification
- **[SDK Documentation](./docs/sdk/)** - Client SDKs and integration guides
- **[ADRs](./docs/adr/)** - Architecture Decision Records

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│              USER REQUEST                        │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│         CONTEXT COMPRESSOR                       │
│  • Token management (128K limit)                │
│  • Intelligent compression                       │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│         ARCHITECT AGENT                          │
│  • Analyzes requirements                         │
│  • Selects template (SaaS, E-commerce, etc.)    │
│  • Defines architecture                          │
└────────────────────┬────────────────────────────┘
                     │
     ┌───────────────┼───────────────┐
     │               │               │
     ▼               ▼               ▼
┌─────────┐   ┌─────────┐   ┌──────────┐
│FRONTEND │   │BACKEND  │   │DATABASE  │
│ AGENT   │   │ AGENT   │   │ AGENT    │
│         │   │         │   │          │
│Next.js  │   │API      │   │Supabase  │
│Tailwind │   │Routes   │   │Schemas   │
│shadcn/ui│   │Auth     │   │RLS       │
└────┬────┘   └────┬────┘   └────┬─────┘
     │             │             │
     └─────────────┼─────────────┘
                   │ (Parallel Execution)
                   ▼
┌─────────────────────────────────────────────────┐
│         REVIEWER AGENT                           │
│  • Code validation                               │
│  • Error detection                               │
│  • Iterative improvement (max 2)                │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│              OUTPUT                              │
│  • Production-ready Next.js app                 │
│  • Supabase schemas with RLS                    │
│  • .env.local.example                           │
└─────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

### Backend
- **FastAPI 0.110.1** - Modern Python web framework
- **MongoDB 4.5.0** - Document database for projects and users
- **Motor 3.3.1** - Async MongoDB driver
- **OpenAI SDK** - AI model integration
- **LiteLLM 1.80.0** - Unified LLM interface
- **Stripe 14.0.1** - Payment processing
- **PyGithub 2.8.1** - GitHub API integration
- **Memori SDK 2.0.0** - Persistent memory management

### Frontend
- **React 19.0.0** - Modern UI framework
- **React Router 7.5.1** - Client-side routing
- **Monaco Editor** - VS Code-powered code editor
- **Tailwind CSS 3.4.17** - Utility-first CSS
- **shadcn/ui** - High-quality React components
- **Axios 1.8.4** - HTTP client
- **Lucide React** - Icon library

### AI & Orchestration
- **OrchestratorV2** - Parallel multi-agent execution
- **ArchitectAgent** - Requirements analysis and planning
- **FrontendAgent** - Next.js UI generation
- **BackendAgent** - API and authentication
- **DatabaseAgent** - Supabase schemas and RLS
- **ReviewerAgent** - Code quality assurance

---

## 💡 Usage

### 1. Configure API Keys

Navigate to **Settings** and add:
- **OpenRouter API Key** - Get from [openrouter.ai/keys](https://openrouter.ai/keys)
- **GitHub Token** (optional) - For repo export
- **Vercel Token** (optional) - For deployment

### 2. Create a Project

Click **"New Project"** or **"Get Started"** to open the editor with default files.

### 3. Generate Code with AI

In the **AI Assistant** panel:
1. Select your preferred model (GPT-4o, Claude 4, Gemini 2.5, etc.)
2. Describe what you want to build
3. Click send and watch the AI generate code in real-time

**Example prompts:**
- "Create a modern landing page with hero section and pricing"
- "Build a SaaS dashboard with user authentication"
- "Generate a blog with dark mode and comment system"

### 4. Full-Stack Project Generation

For complete applications:
```
Use the /api/generate/fullstack endpoint with:
- Project type: saas | ecommerce | blog | dashboard | api
- Description: Detailed requirements
- Model: Your preferred AI model
```

The system will generate:
- ✅ Next.js 14+ App Router structure
- ✅ Tailwind + shadcn/ui components
- ✅ API routes with authentication
- ✅ Supabase schemas with RLS policies
- ✅ Stripe integration (for SaaS)
- ✅ Email templates
- ✅ Environment configuration

### 5. Export & Deploy

- **💾 Save** - Auto-saves to MongoDB
- **📥 Download** - Export all files as ZIP
- **🔗 GitHub Export** - Create a new repository
- **🚀 Vercel Deploy** - Deploy to production

---

## 🔌 API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/` | GET | Health check |
| `/api/settings` | GET/PUT | User settings management |
| `/api/projects` | GET/POST | Project CRUD operations |
| `/api/projects/{id}` | GET/PUT/DELETE | Single project operations |
| `/api/openrouter/models` | GET | List available AI models |

### Generation Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/generate/openrouter` | POST | Simple code generation (HTML/CSS/JS) |
| `/api/generate/agentic` | POST | Multi-agent code generation |
| `/api/generate/fullstack` | POST | **Full-stack Next.js app generation** |
| `/api/templates` | GET | List available templates |

### Integration Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/github/export` | POST | Export project to GitHub |
| `/api/vercel/deploy` | POST | Deploy to Vercel |
| `/api/stripe/checkout` | POST | Create Stripe checkout session |
| `/api/stripe/webhook` | POST | Handle Stripe webhooks |

### Authentication & Admin

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | POST | User registration |
| `/api/auth/login` | POST | User login |
| `/api/auth/logout` | POST | User logout |
| `/api/admin/*` | Various | Admin panel operations |

Full API documentation available at `/docs` (Swagger UI) when running the server.

---

## 🗄️ Database Schema

### MongoDB Collections

**projects**
```javascript
{
  id: String (UUID),
  name: String,
  description: String,
  files: [
    { name: String, content: String, language: String }
  ],
  conversation_history: [
    { role: "user"|"assistant", content: String }
  ],
  project_type: String, // saas, ecommerce, blog, etc.
  github_repo_url: String,
  vercel_url: String,
  user_id: String,
  created_at: DateTime,
  updated_at: DateTime
}
```

**users**
```javascript
{
  id: String (UUID),
  email: String,
  hashed_password: String,
  stripe_customer_id: String,
  subscription_status: String,
  plan: String, // free, pro, enterprise
  created_at: DateTime,
  updated_at: DateTime
}
```

**settings**
```javascript
{
  id: String (UUID),
  openrouter_api_key: String (encrypted),
  github_token: String (encrypted),
  vercel_token: String (encrypted),
  created_at: DateTime,
  updated_at: DateTime
}
```

---

## 🔒 Security

- **🔐 API Key Encryption** - All API keys stored encrypted in MongoDB
- **🛡️ CORS Protection** - Configured allowed origins
- **⚡ Rate Limiting** - Prevents API abuse
- **🔑 JWT Authentication** - Secure session management
- **✅ Input Validation** - Pydantic models for all requests
- **🔍 Stripe Webhook Verification** - Signature validation

---

## 🌐 Environment Variables

### Backend (.env)

```env
# Database
MONGO_URL=mongodb://localhost:27017
DB_NAME=devora_projects_db

# CORS
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Email (Resend)
RESEND_API_KEY=re_...

# Frontend URL
FRONTEND_URL=http://localhost:3000

# Memori SDK (Optional)
MEMORI_API_KEY=your-memori-key
MEMORI_DATABASE_URL=postgresql://...
```

### Frontend (.env)

```env
REACT_APP_BACKEND_URL=http://localhost:8000
```

---

## 📊 Features by Plan

| Feature | Free | Pro | Enterprise |
|---------|------|-----|------------|
| AI Code Generation | ✅ | ✅ | ✅ |
| Monaco Editor | ✅ | ✅ | ✅ |
| Projects Limit | 5 | Unlimited | Unlimited |
| GitHub Export | ❌ | ✅ | ✅ |
| Vercel Deploy | ❌ | ✅ | ✅ |
| Full-Stack Generation | ❌ | ✅ | ✅ |
| Custom Templates | ❌ | ❌ | ✅ |
| Priority Support | ❌ | ❌ | ✅ |
| Team Collaboration | ❌ | ❌ | ✅ |

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](./docs/CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Integration Tests
```bash
python backend/test_orchestration_integration.py
```

---

## 📦 Deployment

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Production build
docker-compose -f docker-compose.prod.yml up -d
```

### Manual Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment instructions.

---

## 🗺️ Roadmap

- [ ] **TypeScript Agent** - Dedicated TypeScript code generation
- [ ] **Testing Agent** - Automatic test generation (Jest, Playwright)
- [ ] **SEO Agent** - Metadata and optimization
- [ ] **Multi-language Support** - i18n integration
- [ ] **Figma Integration** - Design-to-code conversion
- [ ] **Real-time Collaboration** - Multi-user editing
- [ ] **Custom Model Training** - Fine-tuned models for specific stacks
- [ ] **Kubernetes Support** - Advanced deployment options

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **OpenRouter** - Unified access to multiple AI models
- **Anthropic, OpenAI, Google** - Powerful language models
- **Supabase** - Backend-as-a-Service platform
- **Vercel** - Deployment and hosting
- **shadcn/ui** - Beautiful UI components
- **FastAPI** - Modern Python web framework

---

## 💬 Support

- **📧 Email:** support@devora.ai
- **💬 Discord:** [Join our community](https://discord.gg/devora)
- **🐛 Issues:** [GitHub Issues](https://github.com/yourusername/devora-transformation/issues)
- **📖 Docs:** [Full Documentation](https://docs.devora.ai)

---

**Built with ❤️ by the Devora Team**

*Transform your ideas into reality with AI-powered development.*
