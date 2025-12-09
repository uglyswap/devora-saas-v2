# Devora Python SDK

Official Python client library for the Devora AI Code Generator API.

## Installation

```bash
pip install devora-sdk
```

**Requirements:**
- Python 3.8+
- `requests` library (installed automatically)

## Quick Start

```python
from devora import DevoraClient

# Initialize client
client = DevoraClient(
    api_key="sk-or-v1-...",  # Your OpenRouter API key
    base_url="https://api.devora.ai"  # Optional, defaults to production
)

# Generate a full-stack SaaS app
result = client.generate_fullstack(
    prompt="Build a task management SaaS with authentication and payments",
    project_type="saas",
    model="openai/gpt-4o"
)

# Access generated files
for file in result.files:
    print(f"{file.name}: {len(file.content)} characters")

# Save to local filesystem
client.save_project(result, output_dir="./my-saas-app")
```

## Authentication

### OpenRouter API Key

```python
client = DevoraClient(api_key="sk-or-v1-...")
```

### JWT Token (for user-specific operations)

```python
# After login
response = client.auth.login("user@example.com", "password")
client.set_auth_token(response.access_token)

# Now all requests are authenticated
projects = client.projects.list()
```

## API Reference

### Client Initialization

```python
class DevoraClient:
    def __init__(
        self,
        api_key: str = None,
        auth_token: str = None,
        base_url: str = "https://api.devora.ai",
        timeout: int = 300  # 5 minutes for generation
    ):
        """
        Initialize the Devora client.

        Args:
            api_key: OpenRouter API key for code generation
            auth_token: JWT token for authenticated requests
            base_url: API base URL (default: production)
            timeout: Request timeout in seconds
        """
```

### Code Generation

#### Simple Generation

```python
def generate_code(
    self,
    prompt: str,
    model: str = "openai/gpt-4o",
    conversation_history: List[Dict] = None
) -> GeneratedCodeResponse:
    """
    Generate simple HTML/CSS/JS code.

    Args:
        prompt: Description of what to build
        model: AI model to use (default: gpt-4o)
        conversation_history: Previous messages for context

    Returns:
        GeneratedCodeResponse with files

    Example:
        >>> result = client.generate_code(
        ...     prompt="Create a landing page with pricing",
        ...     model="openai/gpt-4o"
        ... )
        >>> print(result.files[0].content)
    """
```

**Example:**
```python
result = client.generate_code(
    prompt="Create a modern portfolio website with dark mode",
    model="anthropic/claude-4-sonnet"
)

# Access generated files
html_content = next(f.content for f in result.files if f.name == "index.html")
print(html_content)
```

#### Full-Stack Generation

```python
def generate_fullstack(
    self,
    prompt: str,
    project_type: str = "saas",  # saas, ecommerce, blog, dashboard, api
    model: str = "openai/gpt-4o",
    conversation_history: List[Dict] = None,
    current_files: List[Dict] = None,
    stream: bool = False,
    on_progress: Callable[[ProgressEvent], None] = None
) -> FullStackResponse:
    """
    Generate a complete Next.js 14+ application.

    Args:
        prompt: Detailed description of the app
        project_type: Type of project (saas, ecommerce, blog, etc.)
        model: AI model to use
        conversation_history: Previous conversation for context
        current_files: Existing files to iterate on
        stream: Enable streaming progress updates
        on_progress: Callback for progress events (if stream=True)

    Returns:
        FullStackResponse with files, architecture, and review

    Example:
        >>> result = client.generate_fullstack(
        ...     prompt="Build a task manager with Stripe",
        ...     project_type="saas",
        ...     stream=True,
        ...     on_progress=lambda event: print(event.message)
        ... )
    """
```

**Example with Streaming:**
```python
def handle_progress(event):
    print(f"[{event.stage}] {event.percent}% - {event.message}")

result = client.generate_fullstack(
    prompt="""
    Build a SaaS for project management with:
    - User authentication (email/password)
    - Project CRUD operations
    - Task boards with drag-and-drop
    - Stripe subscription ($19/month Pro plan)
    - Dark mode support
    """,
    project_type="saas",
    model="openai/gpt-4o",
    stream=True,
    on_progress=handle_progress
)

# Output:
# [architect] 10% - Analyzing requirements...
# [architect] 20% - Selecting SaaS template...
# [frontend] 40% - Generating UI components...
# [backend] 60% - Creating API routes...
# [database] 80% - Defining Supabase schemas...
# [reviewer] 90% - Validating code quality...
# [complete] 100% - Generation complete!

print(f"\nGenerated {len(result.files)} files")
print(f"Architecture: {result.architecture.project_type}")
print(f"Quality Score: {result.review.quality_score}/100")
```

### Project Management

```python
# List all projects
projects = client.projects.list()
for project in projects:
    print(f"{project.name} - {len(project.files)} files")

# Create a project
project = client.projects.create(
    name="My New Project",
    description="A test project",
    project_type="saas",
    files=[
        {"name": "index.html", "content": "<html>...</html>", "language": "html"}
    ]
)

# Get a specific project
project = client.projects.get(project_id="uuid-here")

# Update a project
project.name = "Updated Name"
project.files.append({
    "name": "new-file.js",
    "content": "console.log('hello')",
    "language": "javascript"
})
updated = client.projects.update(project.id, project)

# Delete a project
client.projects.delete(project_id="uuid-here")
```

### Settings Management

```python
# Get current settings
settings = client.settings.get()
print(settings.openrouter_api_key)  # Encrypted value

# Update settings
client.settings.update(
    openrouter_api_key="sk-or-v1-new-key",
    github_token="ghp_...",
    vercel_token="..."
)
```

### GitHub Integration

```python
# Export project to GitHub
result = client.github.export(
    project_id="uuid-here",
    repo_name="my-awesome-project",
    github_token="ghp_...",
    private=False  # Public repository
)

print(f"Repository created: {result.repo_url}")
# https://github.com/username/my-awesome-project
```

### Vercel Deployment

```python
# Deploy to Vercel
result = client.vercel.deploy(
    project_id="uuid-here",
    project_name="my-app",
    vercel_token="..."
)

print(f"Deployed to: {result.deployment_url}")
# https://my-app-abc123.vercel.app
```

### Authentication

```python
# Register new user
user = client.auth.register(
    email="user@example.com",
    password="SecurePassword123!"
)

# Login
auth_response = client.auth.login(
    email="user@example.com",
    password="SecurePassword123!"
)

# Set token for subsequent requests
client.set_auth_token(auth_response.access_token)

# Logout
client.auth.logout()
```

### Billing (Stripe)

```python
# Create checkout session
checkout = client.billing.create_checkout_session(plan="pro")

# Redirect user to Stripe
print(f"Pay here: {checkout.checkout_url}")

# Check subscription status (after webhook)
status = client.billing.get_subscription_status()
print(f"Plan: {status.plan}, Status: {status.status}")
```

## Examples

### Example 1: Generate and Deploy a Blog

```python
from devora import DevoraClient

client = DevoraClient(api_key="sk-or-v1-...")

# Step 1: Generate the blog
print("Generating blog...")
result = client.generate_fullstack(
    prompt="""
    Create a tech blog with:
    - Markdown support for posts
    - Dark mode toggle
    - Comment system
    - RSS feed
    - SEO optimized
    """,
    project_type="blog",
    model="openai/gpt-4o",
    stream=True,
    on_progress=lambda e: print(f"{e.stage}: {e.message}")
)

# Step 2: Save to project
project = client.projects.create(
    name="My Tech Blog",
    project_type="blog",
    files=result.files
)

# Step 3: Export to GitHub
print("\nExporting to GitHub...")
github_result = client.github.export(
    project_id=project.id,
    repo_name="my-tech-blog",
    github_token="ghp_...",
    private=False
)

# Step 4: Deploy to Vercel
print("\nDeploying to Vercel...")
vercel_result = client.vercel.deploy(
    project_id=project.id,
    project_name="my-blog",
    vercel_token="..."
)

print(f"\n🎉 Blog live at: {vercel_result.deployment_url}")
```

### Example 2: Iterative Development

```python
from devora import DevoraClient

client = DevoraClient(api_key="sk-or-v1-...")

# Initial generation
print("Creating initial app...")
result = client.generate_fullstack(
    prompt="Build a simple todo app with authentication",
    project_type="saas"
)

project = client.projects.create(
    name="Todo App",
    files=result.files,
    conversation_history=[
        {"role": "user", "content": "Build a simple todo app with authentication"},
        {"role": "assistant", "content": "Generated todo app"}
    ]
)

# Iterate: Add a feature
print("\nAdding feature...")
updated_result = client.generate_fullstack(
    prompt="Add a priority field to tasks (low, medium, high) and ability to filter by priority",
    current_files=[f.__dict__ for f in result.files],
    conversation_history=project.conversation_history
)

# Update project
project.files = updated_result.files
project.conversation_history.extend([
    {"role": "user", "content": "Add priority filtering"},
    {"role": "assistant", "content": "Added priority feature"}
])

client.projects.update(project.id, project)
print("✅ Feature added!")
```

### Example 3: Batch Processing

```python
from devora import DevoraClient
from concurrent.futures import ThreadPoolExecutor

client = DevoraClient(api_key="sk-or-v1-...")

# Generate multiple landing pages in parallel
prompts = [
    "Create a landing page for a fitness app",
    "Create a landing page for a food delivery service",
    "Create a landing page for a meditation app"
]

def generate_landing_page(prompt):
    result = client.generate_code(prompt=prompt)
    return result

# Parallel execution
with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(generate_landing_page, prompts))

for i, result in enumerate(results, 1):
    print(f"Landing page {i}: {len(result.files)} files generated")
```

### Example 4: Error Handling

```python
from devora import DevoraClient, DevoraAPIError, AuthenticationError

client = DevoraClient(api_key="sk-or-v1-...")

try:
    result = client.generate_fullstack(
        prompt="Build a SaaS",
        project_type="saas"
    )
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
    print("Check your API key")
except DevoraAPIError as e:
    print(f"API error: {e.status_code} - {e.message}")
    if e.status_code == 429:
        print("Rate limit exceeded. Retry in 60 seconds.")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Response Types

### GeneratedCodeResponse

```python
@dataclass
class ProjectFile:
    name: str
    content: str
    language: str

@dataclass
class GeneratedCodeResponse:
    files: List[ProjectFile]
    message: str
```

### FullStackResponse

```python
@dataclass
class FullStackResponse:
    files: List[ProjectFile]
    architecture: dict  # Architecture spec from ArchitectAgent
    review: dict        # Review from ReviewerAgent
    quality_score: int  # 0-100

    def save(self, output_dir: str):
        """Save all files to local directory."""
        pass
```

### ProgressEvent (Streaming)

```python
@dataclass
class ProgressEvent:
    event: str       # "start", "progress", "agent_start", "complete", "error"
    stage: str       # "architect", "frontend", "backend", "database", "reviewer"
    percent: int     # 0-100
    message: str
    data: dict       # Additional event data
```

## Configuration

### Environment Variables

```bash
# .env file
DEVORA_API_KEY=sk-or-v1-...
DEVORA_BASE_URL=https://api.devora.ai
DEVORA_TIMEOUT=300
```

```python
import os
from devora import DevoraClient

client = DevoraClient(
    api_key=os.getenv("DEVORA_API_KEY"),
    base_url=os.getenv("DEVORA_BASE_URL"),
    timeout=int(os.getenv("DEVORA_TIMEOUT", 300))
)
```

### Custom Timeout

```python
# Long-running generation
client = DevoraClient(
    api_key="sk-or-v1-...",
    timeout=600  # 10 minutes
)
```

### Retry Configuration

```python
from devora import DevoraClient
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

client = DevoraClient(api_key="sk-or-v1-...")

# Custom retry strategy
retry_strategy = Retry(
    total=3,
    backoff_factor=2,
    status_forcelist=[429, 500, 502, 503, 504]
)

adapter = HTTPAdapter(max_retries=retry_strategy)
client.session.mount("https://", adapter)
```

## Testing

### Mock Client for Testing

```python
from devora.testing import MockDevoraClient

# In your tests
def test_my_app():
    client = MockDevoraClient()

    # Mock response
    client.mock_generate_fullstack(
        files=[
            {"name": "app/page.tsx", "content": "...", "language": "typescript"}
        ]
    )

    result = client.generate_fullstack(prompt="Build a SaaS")
    assert len(result.files) == 1
```

## Advanced Usage

### Custom Headers

```python
client = DevoraClient(api_key="sk-or-v1-...")
client.session.headers.update({
    "X-Custom-Header": "value"
})
```

### Logging

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

client = DevoraClient(api_key="sk-or-v1-...")
# Now all HTTP requests are logged
```

## Troubleshooting

### Common Issues

**1. Timeout Errors**
```python
# Increase timeout for complex generations
client = DevoraClient(api_key="...", timeout=600)
```

**2. Rate Limit Errors**
```python
# Implement exponential backoff
import time

for attempt in range(3):
    try:
        result = client.generate_fullstack(prompt="...")
        break
    except DevoraAPIError as e:
        if e.status_code == 429:
            wait = 2 ** attempt
            print(f"Rate limited. Retrying in {wait}s...")
            time.sleep(wait)
```

**3. Authentication Errors**
```python
# Verify API key
settings = client.settings.get()
print(f"API Key configured: {bool(settings.openrouter_api_key)}")
```

## Support

- **Documentation:** https://docs.devora.ai
- **GitHub:** https://github.com/yourusername/devora-sdk-python
- **Issues:** https://github.com/yourusername/devora-sdk-python/issues
- **Email:** support@devora.ai

## License

MIT License - see [LICENSE](https://github.com/yourusername/devora-sdk-python/blob/main/LICENSE)
