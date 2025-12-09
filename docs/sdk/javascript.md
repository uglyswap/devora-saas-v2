# Devora JavaScript/TypeScript SDK

Official JavaScript/TypeScript client library for the Devora AI Code Generator API.

## Installation

```bash
npm install devora-sdk
# or
yarn add devora-sdk
# or
pnpm add devora-sdk
```

**Requirements:**
- Node.js 16+ or modern browser
- TypeScript 4.5+ (optional but recommended)

## Quick Start

### TypeScript

```typescript
import { DevoraClient } from 'devora-sdk';

// Initialize client
const client = new DevoraClient({
  apiKey: 'sk-or-v1-...', // Your OpenRouter API key
  baseURL: 'https://api.devora.ai' // Optional, defaults to production
});

// Generate a full-stack SaaS app
const result = await client.generateFullstack({
  prompt: 'Build a task management SaaS with authentication and payments',
  projectType: 'saas',
  model: 'openai/gpt-4o'
});

// Access generated files
result.files.forEach(file => {
  console.log(`${file.name}: ${file.content.length} characters`);
});

// Save to local filesystem (Node.js only)
await client.saveProject(result, './my-saas-app');
```

### JavaScript (ES6)

```javascript
const { DevoraClient } = require('devora-sdk');

const client = new DevoraClient({
  apiKey: 'sk-or-v1-...'
});

async function generateApp() {
  const result = await client.generateFullstack({
    prompt: 'Build a task management SaaS',
    projectType: 'saas'
  });

  console.log(`Generated ${result.files.length} files`);
}

generateApp();
```

### Browser

```html
<script type="module">
  import { DevoraClient } from 'https://cdn.jsdelivr.net/npm/devora-sdk@latest/dist/index.esm.js';

  const client = new DevoraClient({
    apiKey: 'sk-or-v1-...'
  });

  const result = await client.generateCode({
    prompt: 'Create a landing page'
  });

  console.log(result.files);
</script>
```

## Authentication

### OpenRouter API Key

```typescript
const client = new DevoraClient({
  apiKey: 'sk-or-v1-...'
});
```

### JWT Token (for user-specific operations)

```typescript
// After login
const authResponse = await client.auth.login('user@example.com', 'password');
client.setAuthToken(authResponse.accessToken);

// Now all requests are authenticated
const projects = await client.projects.list();
```

## API Reference

### Client Initialization

```typescript
interface DevoraClientConfig {
  apiKey?: string;
  authToken?: string;
  baseURL?: string;
  timeout?: number; // milliseconds, default: 300000 (5 minutes)
}

class DevoraClient {
  constructor(config: DevoraClientConfig);
}
```

**Example:**
```typescript
const client = new DevoraClient({
  apiKey: 'sk-or-v1-...',
  baseURL: 'http://localhost:8000', // For development
  timeout: 600000 // 10 minutes
});
```

### Code Generation

#### Simple Generation

```typescript
interface GenerateCodeOptions {
  prompt: string;
  model?: string; // default: 'openai/gpt-4o'
  conversationHistory?: ConversationMessage[];
}

interface GeneratedCodeResponse {
  files: ProjectFile[];
  message: string;
}

async generateCode(options: GenerateCodeOptions): Promise<GeneratedCodeResponse>;
```

**Example:**
```typescript
const result = await client.generateCode({
  prompt: 'Create a modern portfolio website with dark mode',
  model: 'anthropic/claude-4-sonnet'
});

// Access generated HTML
const htmlFile = result.files.find(f => f.name === 'index.html');
console.log(htmlFile.content);
```

#### Full-Stack Generation

```typescript
interface GenerateFullstackOptions {
  prompt: string;
  projectType?: 'saas' | 'ecommerce' | 'blog' | 'dashboard' | 'api';
  model?: string;
  conversationHistory?: ConversationMessage[];
  currentFiles?: ProjectFile[];
  stream?: boolean;
  onProgress?: (event: ProgressEvent) => void;
}

interface FullStackResponse {
  files: ProjectFile[];
  architecture: Architecture;
  review: Review;
}

async generateFullstack(options: GenerateFullstackOptions): Promise<FullStackResponse>;
```

**Example with Streaming:**
```typescript
const result = await client.generateFullstack({
  prompt: `
    Build a SaaS for project management with:
    - User authentication (email/password)
    - Project CRUD operations
    - Task boards with drag-and-drop
    - Stripe subscription ($19/month Pro plan)
    - Dark mode support
  `,
  projectType: 'saas',
  model: 'openai/gpt-4o',
  stream: true,
  onProgress: (event) => {
    console.log(`[${event.stage}] ${event.percent}% - ${event.message}`);
  }
});

// Output:
// [architect] 10% - Analyzing requirements...
// [architect] 20% - Selecting SaaS template...
// [frontend] 40% - Generating UI components...
// [backend] 60% - Creating API routes...
// [database] 80% - Defining Supabase schemas...
// [reviewer] 90% - Validating code quality...
// [complete] 100% - Generation complete!

console.log(`\nGenerated ${result.files.length} files`);
console.log(`Quality Score: ${result.review.qualityScore}/100`);
```

### Project Management

```typescript
// List all projects
const projects = await client.projects.list();
projects.forEach(project => {
  console.log(`${project.name} - ${project.files.length} files`);
});

// Create a project
const project = await client.projects.create({
  name: 'My New Project',
  description: 'A test project',
  projectType: 'saas',
  files: [
    { name: 'index.html', content: '<html>...</html>', language: 'html' }
  ]
});

// Get a specific project
const project = await client.projects.get('project-uuid');

// Update a project
project.name = 'Updated Name';
project.files.push({
  name: 'new-file.js',
  content: "console.log('hello')",
  language: 'javascript'
});
const updated = await client.projects.update(project.id, project);

// Delete a project
await client.projects.delete('project-uuid');
```

### Settings Management

```typescript
// Get current settings
const settings = await client.settings.get();
console.log(settings.openrouterApiKey); // Encrypted value

// Update settings
await client.settings.update({
  openrouterApiKey: 'sk-or-v1-new-key',
  githubToken: 'ghp_...',
  vercelToken: '...'
});
```

### GitHub Integration

```typescript
// Export project to GitHub
const result = await client.github.export({
  projectId: 'project-uuid',
  repoName: 'my-awesome-project',
  githubToken: 'ghp_...',
  private: false // Public repository
});

console.log(`Repository created: ${result.repoUrl}`);
// https://github.com/username/my-awesome-project
```

### Vercel Deployment

```typescript
// Deploy to Vercel
const result = await client.vercel.deploy({
  projectId: 'project-uuid',
  projectName: 'my-app',
  vercelToken: '...'
});

console.log(`Deployed to: ${result.deploymentUrl}`);
// https://my-app-abc123.vercel.app
```

### Authentication

```typescript
// Register new user
const user = await client.auth.register({
  email: 'user@example.com',
  password: 'SecurePassword123!'
});

// Login
const authResponse = await client.auth.login({
  email: 'user@example.com',
  password: 'SecurePassword123!'
});

// Set token for subsequent requests
client.setAuthToken(authResponse.accessToken);

// Logout
await client.auth.logout();
```

### Billing (Stripe)

```typescript
// Create checkout session
const checkout = await client.billing.createCheckoutSession({ plan: 'pro' });

// Redirect user to Stripe
window.location.href = checkout.checkoutUrl;

// Check subscription status (after webhook)
const status = await client.billing.getSubscriptionStatus();
console.log(`Plan: ${status.plan}, Status: ${status.status}`);
```

## Examples

### Example 1: Generate and Deploy a Blog (Node.js)

```typescript
import { DevoraClient } from 'devora-sdk';
import fs from 'fs/promises';

const client = new DevoraClient({ apiKey: 'sk-or-v1-...' });

async function deployBlog() {
  // Step 1: Generate the blog
  console.log('Generating blog...');
  const result = await client.generateFullstack({
    prompt: `
      Create a tech blog with:
      - Markdown support for posts
      - Dark mode toggle
      - Comment system
      - RSS feed
      - SEO optimized
    `,
    projectType: 'blog',
    model: 'openai/gpt-4o',
    stream: true,
    onProgress: (e) => console.log(`${e.stage}: ${e.message}`)
  });

  // Step 2: Save to project
  const project = await client.projects.create({
    name: 'My Tech Blog',
    projectType: 'blog',
    files: result.files
  });

  // Step 3: Export to GitHub
  console.log('\nExporting to GitHub...');
  const githubResult = await client.github.export({
    projectId: project.id,
    repoName: 'my-tech-blog',
    githubToken: process.env.GITHUB_TOKEN!,
    private: false
  });

  // Step 4: Deploy to Vercel
  console.log('\nDeploying to Vercel...');
  const vercelResult = await client.vercel.deploy({
    projectId: project.id,
    projectName: 'my-blog',
    vercelToken: process.env.VERCEL_TOKEN!
  });

  console.log(`\n🎉 Blog live at: ${vercelResult.deploymentUrl}`);
}

deployBlog();
```

### Example 2: Iterative Development

```typescript
import { DevoraClient } from 'devora-sdk';

const client = new DevoraClient({ apiKey: 'sk-or-v1-...' });

async function iterativeDevelopment() {
  // Initial generation
  console.log('Creating initial app...');
  let result = await client.generateFullstack({
    prompt: 'Build a simple todo app with authentication',
    projectType: 'saas'
  });

  const project = await client.projects.create({
    name: 'Todo App',
    files: result.files,
    conversationHistory: [
      { role: 'user', content: 'Build a simple todo app with authentication' },
      { role: 'assistant', content: 'Generated todo app' }
    ]
  });

  // Iterate: Add a feature
  console.log('\nAdding feature...');
  result = await client.generateFullstack({
    prompt: 'Add a priority field to tasks (low, medium, high) and ability to filter by priority',
    currentFiles: result.files,
    conversationHistory: project.conversationHistory
  });

  // Update project
  project.files = result.files;
  project.conversationHistory.push(
    { role: 'user', content: 'Add priority filtering' },
    { role: 'assistant', content: 'Added priority feature' }
  );

  await client.projects.update(project.id, project);
  console.log('✅ Feature added!');
}

iterativeDevelopment();
```

### Example 3: React Hook

```typescript
import { useState, useEffect } from 'react';
import { DevoraClient } from 'devora-sdk';

function useDevora(apiKey: string) {
  const [client, setClient] = useState<DevoraClient | null>(null);

  useEffect(() => {
    setClient(new DevoraClient({ apiKey }));
  }, [apiKey]);

  return client;
}

// Usage in component
function MyComponent() {
  const client = useDevora(process.env.REACT_APP_DEVORA_API_KEY!);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const generateApp = async () => {
    if (!client) return;

    setLoading(true);
    try {
      const result = await client.generateFullstack({
        prompt: 'Build a landing page',
        projectType: 'landing'
      });
      setResult(result);
    } catch (error) {
      console.error('Generation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button onClick={generateApp} disabled={loading}>
        {loading ? 'Generating...' : 'Generate App'}
      </button>
      {result && <div>Generated {result.files.length} files</div>}
    </div>
  );
}
```

### Example 4: Error Handling

```typescript
import { DevoraClient, DevoraAPIError, AuthenticationError } from 'devora-sdk';

const client = new DevoraClient({ apiKey: 'sk-or-v1-...' });

async function generateWithErrorHandling() {
  try {
    const result = await client.generateFullstack({
      prompt: 'Build a SaaS',
      projectType: 'saas'
    });
    console.log('Success!', result);
  } catch (error) {
    if (error instanceof AuthenticationError) {
      console.error('Authentication failed:', error.message);
      console.error('Check your API key');
    } else if (error instanceof DevoraAPIError) {
      console.error(`API error: ${error.statusCode} - ${error.message}`);
      if (error.statusCode === 429) {
        console.error('Rate limit exceeded. Retry in 60 seconds.');
      }
    } else {
      console.error('Unexpected error:', error);
    }
  }
}
```

## TypeScript Types

### Core Types

```typescript
interface ProjectFile {
  name: string;
  content: string;
  language: 'typescript' | 'javascript' | 'html' | 'css' | 'markdown' | 'json';
}

interface ConversationMessage {
  role: 'user' | 'assistant';
  content: string;
}

interface Project {
  id: string;
  name: string;
  description?: string;
  files: ProjectFile[];
  conversationHistory: ConversationMessage[];
  projectType?: 'saas' | 'ecommerce' | 'blog' | 'dashboard' | 'api' | 'landing';
  githubRepoUrl?: string;
  vercelUrl?: string;
  createdAt: Date;
  updatedAt: Date;
}

interface Architecture {
  projectType: string;
  name: string;
  features: string[];
  stack: {
    frontend: string;
    backend: string;
    database: string;
    auth: string;
    payments?: string;
  };
  dataModels: Record<string, any>;
  pages: Array<{ route: string; type: string }>;
}

interface Review {
  status: 'APPROVE' | 'ITERATE';
  feedback?: string[];
  qualityScore: number; // 0-100
}

interface ProgressEvent {
  event: 'start' | 'progress' | 'agent_start' | 'agent_complete' | 'error' | 'complete';
  stage?: 'architect' | 'frontend' | 'backend' | 'database' | 'reviewer';
  percent: number; // 0-100
  message: string;
  data?: any;
}
```

## Configuration

### Environment Variables

```bash
# .env file
DEVORA_API_KEY=sk-or-v1-...
DEVORA_BASE_URL=https://api.devora.ai
DEVORA_TIMEOUT=300000
```

```typescript
import { DevoraClient } from 'devora-sdk';

const client = new DevoraClient({
  apiKey: process.env.DEVORA_API_KEY,
  baseURL: process.env.DEVORA_BASE_URL,
  timeout: parseInt(process.env.DEVORA_TIMEOUT || '300000')
});
```

### Custom Timeout

```typescript
// Long-running generation
const client = new DevoraClient({
  apiKey: 'sk-or-v1-...',
  timeout: 600000 // 10 minutes
});
```

### Custom Fetch (Advanced)

```typescript
import fetch from 'node-fetch';

const client = new DevoraClient({
  apiKey: 'sk-or-v1-...',
  fetch: fetch as any // Custom fetch implementation
});
```

## Testing

### Mock Client for Testing

```typescript
import { MockDevoraClient } from 'devora-sdk/testing';

// In your tests
describe('MyApp', () => {
  it('should generate a project', async () => {
    const client = new MockDevoraClient();

    // Mock response
    client.mockGenerateFullstack({
      files: [
        { name: 'app/page.tsx', content: '...', language: 'typescript' }
      ]
    });

    const result = await client.generateFullstack({ prompt: 'Build a SaaS' });
    expect(result.files).toHaveLength(1);
  });
});
```

## Advanced Usage

### Custom Headers

```typescript
const client = new DevoraClient({
  apiKey: 'sk-or-v1-...',
  headers: {
    'X-Custom-Header': 'value'
  }
});
```

### Interceptors

```typescript
client.interceptors.request.use((config) => {
  console.log('Sending request:', config.url);
  return config;
});

client.interceptors.response.use((response) => {
  console.log('Received response:', response.status);
  return response;
});
```

### Retry Logic

```typescript
import { DevoraClient } from 'devora-sdk';

const client = new DevoraClient({
  apiKey: 'sk-or-v1-...',
  retry: {
    maxRetries: 3,
    retryDelay: (attempt) => Math.pow(2, attempt) * 1000, // Exponential backoff
    retryOn: [429, 500, 502, 503, 504]
  }
});
```

## Troubleshooting

### Common Issues

**1. Timeout Errors**
```typescript
// Increase timeout for complex generations
const client = new DevoraClient({
  apiKey: '...',
  timeout: 600000 // 10 minutes
});
```

**2. CORS Errors (Browser)**
```typescript
// Ensure backend has CORS enabled
// Or use a proxy in development

// vite.config.ts
export default {
  server: {
    proxy: {
      '/api': 'http://localhost:8000'
    }
  }
}
```

**3. Module Resolution (TypeScript)**
```json
// tsconfig.json
{
  "compilerOptions": {
    "moduleResolution": "node",
    "esModuleInterop": true
  }
}
```

## Support

- **Documentation:** https://docs.devora.ai
- **GitHub:** https://github.com/yourusername/devora-sdk-js
- **Issues:** https://github.com/yourusername/devora-sdk-js/issues
- **Email:** support@devora.ai

## License

MIT License - see [LICENSE](https://github.com/yourusername/devora-sdk-js/blob/main/LICENSE)
