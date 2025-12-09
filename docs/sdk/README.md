# Devora SDK Documentation

Official client SDKs for integrating with the Devora AI Code Generator API.

## Available SDKs

- **[Python SDK](./python.md)** - For Python applications
- **[JavaScript/TypeScript SDK](./javascript.md)** - For Node.js and browser applications

## Quick Start

### Python

```bash
pip install devora-sdk
```

```python
from devora import DevoraClient

client = DevoraClient(
    api_key="your_openrouter_key",
    base_url="https://api.devora.ai"
)

# Generate a full-stack app
result = client.generate_fullstack(
    prompt="Build a SaaS for task management",
    project_type="saas"
)

print(f"Generated {len(result.files)} files")
```

### JavaScript/TypeScript

```bash
npm install devora-sdk
```

```typescript
import { DevoraClient } from 'devora-sdk';

const client = new DevoraClient({
  apiKey: 'your_openrouter_key',
  baseURL: 'https://api.devora.ai'
});

// Generate a full-stack app
const result = await client.generateFullstack({
  prompt: 'Build a SaaS for task management',
  projectType: 'saas'
});

console.log(`Generated ${result.files.length} files`);
```

## Authentication

All SDKs support two authentication methods:

### 1. OpenRouter API Key (Recommended for Code Generation)

```python
client = DevoraClient(api_key="sk-or-v1-...")
```

### 2. JWT Token (For User-Specific Operations)

```python
client = DevoraClient(
    auth_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
)
```

## Core Features

### Code Generation

Generate code using different modes:

- **Simple Generation** - HTML/CSS/JS only
- **Full-Stack Generation** - Complete Next.js apps with multi-agent orchestration
- **Streaming Progress** - Real-time updates via Server-Sent Events

### Project Management

- Create, read, update, delete projects
- Store conversation history
- Manage project files

### Integrations

- Export to GitHub
- Deploy to Vercel
- Manage billing with Stripe

## Examples

See the SDK-specific documentation for detailed examples:

- [Python SDK Examples](./python.md#examples)
- [JavaScript SDK Examples](./javascript.md#examples)

## Support

- **GitHub Issues:** [Report bugs and request features](https://github.com/yourusername/devora-transformation/issues)
- **Discord:** [Join our community](https://discord.gg/devora)
- **Email:** support@devora.ai

## License

MIT License - see [LICENSE](../../LICENSE) for details.
