# Devora - AI-Powered App Builder

<div align="center">
  <img src="./assets/devora-logo.svg" alt="Devora Logo" width="200" />

  **Build full-stack applications with AI in minutes, not hours.**

  [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
  [![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue)](https://typescriptlang.org)
  [![React](https://img.shields.io/badge/React-19-61dafb)](https://react.dev)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.100-009688)](https://fastapi.tiangolo.com)
  [![Tests](https://img.shields.io/badge/Coverage-85%25-green)]()

  [Live Demo](https://devora.app) | [Documentation](https://docs.devora.app) | [Discord](https://discord.gg/devora)
</div>

---

## Features

### AI-Powered Code Generation
- **Multi-Agent System**: Specialized AI agents (Architect, Frontend, Backend, Database, Reviewer) work together to build complete applications
- **Context-Aware**: Understands your existing codebase and generates consistent code
- **Quality Gates**: Automatic code review, linting, and security checks

### Browser-Native Preview (WebContainers)
- **Instant Feedback**: See your changes in real-time without any server setup
- **Full Node.js**: Run npm packages directly in your browser
- **Hot Reload**: Changes reflect immediately in the preview

### Visual Select & Edit
- **Click to Edit**: Select any element in the preview and modify it with AI
- **Quick Suggestions**: Context-aware styling and functionality suggestions
- **Non-Destructive**: All changes tracked with full undo/redo support

### One-Click Deployment
- **Vercel**: Deploy React, Next.js, and static sites
- **Netlify**: Deploy with automatic CI/CD
- **Cloudflare Pages**: Edge deployment for maximum performance

---

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.10+
- MongoDB (local or Atlas)
- OpenRouter API key

### Installation

```bash
# Clone the repository
git clone https://github.com/devora/devora-saas-v2.git
cd devora-saas-v2

# Install frontend dependencies
cd frontend
npm install

# Install backend dependencies
cd ../backend
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Running Locally

```bash
# Terminal 1: Start backend
cd backend
uvicorn server:app --reload --port 8000

# Terminal 2: Start frontend
cd frontend
npm run dev
```

Open http://localhost:3000 to start building!

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React 19)                      │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ Monaco Editor│  │ WebContainer │  │ Select & Edit Panel  │   │
│  │              │  │   Preview    │  │                      │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │  File Tree   │  │   AI Chat    │  │   Deploy Panel       │   │
│  │              │  │              │  │                      │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Backend API (FastAPI)                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ Orchestrator │  │   Quality    │  │   Deploy Service     │   │
│  │     V3       │  │    Gates     │  │                      │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │   Agents     │  │  LLM Client  │  │   Auth & Billing     │   │
│  │              │  │              │  │                      │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Data Layer                                │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │   MongoDB    │  │    Redis     │  │   File Storage       │   │
│  │  (Projects)  │  │   (Cache)    │  │   (S3/R2)            │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Documentation

| Section | Description |
|---------|-------------|
| [Getting Started](./getting-started.md) | First-time setup and configuration |
| [User Guide](./user-guide.md) | How to build apps with Devora |
| [API Reference](./api-reference.md) | Complete API documentation |
| [Architecture](./architecture.md) | Technical architecture details |
| [Agent System](./agent-system.md) | How AI agents work together |
| [Deployment](./deployment.md) | Deploying your Devora instance |
| [Contributing](./contributing.md) | How to contribute to Devora |
| [Marketplace](./marketplace.md) | Using and creating templates |

---

## Comparison

| Feature | Devora | Bolt.new | Lovable.dev | Windsurf |
|---------|--------|----------|-------------|----------|
| WebContainers Preview | ✅ | ✅ | ❌ | ❌ |
| Visual Select & Edit | ✅ | ❌ | ✅ | ❌ |
| Multi-Agent System | ✅ | ❌ | ❌ | ✅ |
| Quality Gates | ✅ | ❌ | ❌ | ❌ |
| One-Click Deploy | ✅ | ✅ | ✅ | ❌ |
| Open Source | ✅ | ❌ | ❌ | ❌ |
| Self-Hostable | ✅ | ❌ | ❌ | ❌ |
| Template Marketplace | ✅ | ✅ | ✅ | ❌ |
| Real-time Collaboration | 🔜 | ❌ | ❌ | ❌ |

---

## Roadmap

### Q1 2025
- [x] WebContainers integration
- [x] Visual Select & Edit
- [x] One-Click Deploy (Vercel, Netlify, Cloudflare)
- [x] Multi-agent orchestration v3
- [x] Quality gates system
- [x] 80%+ test coverage

### Q2 2025
- [ ] Real-time collaboration
- [ ] Mobile preview mode
- [ ] Custom AI model support
- [ ] Plugin system
- [ ] Template marketplace launch

### Q3 2025
- [ ] Enterprise features (SSO, audit logs)
- [ ] Team workspaces
- [ ] Advanced analytics
- [ ] GitHub/GitLab integration
- [ ] CI/CD pipelines

---

## Contributing

We welcome contributions! Please see our [Contributing Guide](./contributing.md) for details.

### Development Setup

```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/devora-saas-v2.git

# Install dependencies
npm install && pip install -r requirements.txt

# Run tests
npm test && pytest

# Start development servers
npm run dev & uvicorn server:app --reload
```

### Code Style
- TypeScript with strict mode
- ESLint + Prettier for frontend
- Black + isort for backend
- Conventional commits

---

## License

MIT License - see [LICENSE](../LICENSE) for details.

---

## Support

- 📚 [Documentation](https://docs.devora.app)
- 💬 [Discord Community](https://discord.gg/devora)
- 🐛 [GitHub Issues](https://github.com/devora/devora-saas-v2/issues)
- 📧 [Email Support](mailto:support@devora.app)

---

<div align="center">
  Built with ❤️ by the Devora Team
</div>
