# Devora Documentation Index

Welcome to the complete documentation for **Devora** - the AI-powered code generation SaaS platform.

---

## 🚀 Getting Started

- **[README](../README.md)** - Project overview, installation, and quick start
- **[QUICKSTART](../QUICKSTART.md)** - Get up and running in 5 minutes
- **[DEPLOYMENT](../DEPLOYMENT.md)** - Production deployment guide

---

## 📚 Core Documentation

### Architecture & Design

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Complete system architecture documentation
  - System overview and high-level design
  - Multi-agent orchestration system
  - Data flow and component interactions
  - Security architecture
  - Deployment architecture
  - Scalability and performance strategies

### Contributing

- **[CONTRIBUTING.md](./CONTRIBUTING.md)** - Contribution guidelines
  - Code of conduct
  - Development setup
  - Coding standards (Python & JavaScript)
  - Testing guidelines
  - Pull request process
  - Agent development guide

---

## 📖 Architecture Decision Records (ADRs)

Documentation of key architectural decisions and their rationale:

- **[ADR-001: Multi-Agent Architecture](./adr/ADR-001-multi-agent-architecture.md)**
  - Why we chose a multi-agent system over single-agent approach
  - Agent specialization and coordination
  - Performance benefits (3x speedup)
  - Iterative improvement workflow

- **[ADR-002: MongoDB vs PostgreSQL](./adr/ADR-002-mongodb-vs-postgresql.md)**
  - Database selection rationale
  - MongoDB for operational data
  - PostgreSQL for persistent memory (Memori SDK)
  - Hybrid approach benefits

- **[ADR-003: Deployment Strategy](./adr/ADR-003-deployment-strategy.md)**
  - Docker Compose for MVP and growth phases
  - Migration path to Kubernetes at scale
  - Disaster recovery and backup strategies
  - Cost optimization at each phase

---

## 🔌 API Documentation

### OpenAPI Specification

- **[openapi.yaml](./api/openapi.yaml)** - Complete OpenAPI 3.0 specification
  - All endpoints documented with request/response schemas
  - Authentication methods
  - Rate limiting information
  - Examples for every endpoint
  - **Interactive docs:** Visit `/docs` when running the server

### Postman Collection

- **[postman_collection.json](./api/postman_collection.json)** - Ready-to-use Postman collection
  - Pre-configured requests for all endpoints
  - Environment variables for easy configuration
  - Test scripts for automated workflows
  - **Import into Postman:** File → Import → Select this file

---

## 🛠️ SDK Documentation

Official client SDKs for integrating with Devora:

### Python SDK

- **[Python SDK Guide](./sdk/python.md)** - Complete Python client documentation
  - Installation and quick start
  - API reference with type hints
  - Code generation examples
  - Project management
  - GitHub and Vercel integrations
  - Error handling and best practices

### JavaScript/TypeScript SDK

- **[JavaScript SDK Guide](./sdk/javascript.md)** - Complete JavaScript/TypeScript client documentation
  - Installation (npm, yarn, pnpm)
  - TypeScript type definitions
  - React hooks examples
  - Browser and Node.js usage
  - Streaming progress with SSE
  - Error handling

### SDK Overview

- **[SDK Overview](./sdk/README.md)** - SDK comparison and quick links

---

## 🎨 Specialized Guides

### Quality Assurance

- **[QA_SQUAD_DELIVERY.md](./QA_SQUAD_DELIVERY.md)** - Quality assurance processes
  - Testing strategy (unit, integration, E2E)
  - Code review workflow
  - Performance testing
  - Security auditing

### Code Quality

- **[CODE_REVIEW_GUIDE.md](./CODE_REVIEW_GUIDE.md)** - Code review best practices
  - Review checklist
  - Common pitfalls to avoid
  - Security considerations
  - Performance optimization

### Internationalization

- **[I18N_GUIDE.md](./I18N_GUIDE.md)** - Multi-language support
  - Setting up i18n in Next.js
  - Translation workflow
  - Language detection
  - RTL language support

### Accessibility

- **[accessibility/](./accessibility/)** - Web accessibility guidelines
  - WCAG 2.1 compliance
  - Screen reader compatibility
  - Keyboard navigation
  - Color contrast standards

### Performance

- **[performance/](./performance/)** - Performance optimization
  - Frontend optimization (code splitting, lazy loading)
  - Backend optimization (caching, database indexes)
  - Monitoring and profiling
  - Load testing strategies

---

## 📊 Project Insights

### Status & Roadmap

- **[STATUS_ACTUEL.md](../STATUS_ACTUEL.md)** - Current project status
- **[ROADMAP.md](../ROADMAP.md)** - Feature roadmap and upcoming releases
- **[CHANGELOG.md](../CHANGELOG.md)** - Version history and release notes

### Reports & Analysis

- **[TRANSFORMATION_REPORT.md](../TRANSFORMATION_REPORT.md)** - Project transformation summary
- **[DATA_SQUAD_SUMMARY.md](../DATA_SQUAD_SUMMARY.md)** - Data architecture insights
- **[AUDIT_FINAL.md](../AUDIT_FINAL.md)** - Final audit report
- **[RECOMMENDED_IMPROVEMENTS.md](../RECOMMENDED_IMPROVEMENTS.md)** - Future improvements

---

## 🔐 Security & Operations

### Security

- **Security considerations** documented in:
  - [ARCHITECTURE.md](./ARCHITECTURE.md#security-architecture) - Security architecture
  - [ADR-002](./adr/ADR-002-mongodb-vs-postgresql.md) - Data security
  - [ADR-003](./adr/ADR-003-deployment-strategy.md) - Deployment security

### Operations

- **[DEPLOYMENT.md](../DEPLOYMENT.md)** - Deployment procedures
- **[deploy.sh](../deploy.sh)** - Automated deployment script
- **[docker-compose.yml](../docker-compose.yml)** - Development environment
- **[docker-compose.prod.yml](../docker-compose.prod.yml)** - Production environment

---

## 🧪 Testing

### Test Documentation

- **[tests/](../tests/)** - Test suite
- **[test_reports/](../test_reports/)** - Test execution reports
- **[backend/test_orchestration_integration.py](../backend/test_orchestration_integration.py)** - Integration tests

---

## 💼 Business Documentation

### SaaS Setup

- **[SAAS_SETUP.md](../SAAS_SETUP.md)** - SaaS configuration guide
  - Stripe integration
  - Subscription plans
  - User management
  - Admin panel

### Admin Management

- **[ADMIN_MANAGEMENT.md](../ADMIN_MANAGEMENT.md)** - Admin features
- **[ADMIN_SETUP.md](../ADMIN_SETUP.md)** - Admin panel setup

### User Guide

- **[USER_GUIDE.md](../USER_GUIDE.md)** - End-user documentation
  - How to use the platform
  - AI code generation tips
  - Project management
  - Export and deployment

---

## 📝 Additional Resources

### Marketing & Copywriting

- **[COPYWRITING_AIDA.md](../COPYWRITING_AIDA.md)** - Marketing copy framework
- **[MISSION_RECAP.md](../MISSION_RECAP.md)** - Project mission statement

### Development Guides

- **[AGENTIC_SYSTEM.md](../AGENTIC_SYSTEM.md)** - Agentic system deep dive
- **[IMPROVEMENTS_AND_FEATURES.md](../IMPROVEMENTS_AND_FEATURES.md)** - Feature proposals
- **[MODIFICATIONS_UX.md](../MODIFICATIONS_UX.md)** - UX improvements

### Backend Specific

- **[backend/INDEX_ORCHESTRATION.md](../backend/INDEX_ORCHESTRATION.md)** - Orchestration system index
- **[backend/ORCHESTRATION_INTEGRATION.md](../backend/ORCHESTRATION_INTEGRATION.md)** - Integration guide
- **[backend/QUICKSTART_ORCHESTRATION.md](../backend/QUICKSTART_ORCHESTRATION.md)** - Orchestration quick start
- **[backend/README_ORCHESTRATION.md](../backend/README_ORCHESTRATION.md)** - Orchestration readme

---

## 🔗 Quick Links

### For Developers

1. **Setting up dev environment:** [CONTRIBUTING.md](./CONTRIBUTING.md#development-setup)
2. **Understanding the architecture:** [ARCHITECTURE.md](./ARCHITECTURE.md)
3. **Creating a new agent:** [CONTRIBUTING.md](./CONTRIBUTING.md#agent-development)
4. **Running tests:** [CONTRIBUTING.md](./CONTRIBUTING.md#testing-guidelines)

### For API Users

1. **API reference:** [openapi.yaml](./api/openapi.yaml)
2. **Python SDK:** [sdk/python.md](./sdk/python.md)
3. **JavaScript SDK:** [sdk/javascript.md](./sdk/javascript.md)
4. **Postman collection:** [postman_collection.json](./api/postman_collection.json)

### For DevOps

1. **Deployment guide:** [DEPLOYMENT.md](../DEPLOYMENT.md)
2. **Docker setup:** [ADR-003](./adr/ADR-003-deployment-strategy.md)
3. **Monitoring:** [ARCHITECTURE.md](./ARCHITECTURE.md#monitoring--observability)
4. **Backup & recovery:** [ADR-003](./adr/ADR-003-deployment-strategy.md#disaster-recovery)

### For Product/Business

1. **SaaS setup:** [SAAS_SETUP.md](../SAAS_SETUP.md)
2. **Roadmap:** [ROADMAP.md](../ROADMAP.md)
3. **User guide:** [USER_GUIDE.md](../USER_GUIDE.md)
4. **Copywriting:** [COPYWRITING_AIDA.md](../COPYWRITING_AIDA.md)

---

## 🆘 Getting Help

If you can't find what you're looking for:

1. **Search the docs:** Use Ctrl+F or your editor's search
2. **Check the ADRs:** Many "why" questions are answered there
3. **API docs:** Interactive Swagger UI at `/docs` endpoint
4. **Community:**
   - GitHub Issues: [Report bugs or request features](https://github.com/yourusername/devora-transformation/issues)
   - Discord: [Join our community](https://discord.gg/devora)
   - Email: support@devora.ai

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](../LICENSE) file for details.

---

**Last Updated:** 2024-12-09

**Documentation Version:** 3.0.0

**Maintained by:** Devora Documentation Team
