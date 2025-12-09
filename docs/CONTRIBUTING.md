# Contributing to Devora

Thank you for considering contributing to Devora! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Agent Development](#agent-development)
- [Documentation](#documentation)

---

## Code of Conduct

### Our Pledge

We are committed to making participation in this project a harassment-free experience for everyone, regardless of level of experience, gender, gender identity and expression, sexual orientation, disability, personal appearance, body size, race, ethnicity, age, religion, or nationality.

### Expected Behavior

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Trolling, insulting/derogatory comments, and personal or political attacks
- Public or private harassment
- Publishing others' private information without explicit permission
- Other conduct which could reasonably be considered inappropriate in a professional setting

---

## Getting Started

### Prerequisites

Before you start contributing, make sure you have:

- **Python 3.10+** installed
- **Node.js 18+** and npm/yarn
- **MongoDB 4.4+** running locally or accessible
- **Git** for version control
- A **GitHub account**
- A text editor or IDE (VS Code recommended)

### Understanding the Codebase

Familiarize yourself with:
- [README.md](../README.md) - Project overview
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture
- [ADRs](./adr/) - Architecture decisions

### Areas to Contribute

- **Bug Fixes** - Fix reported issues
- **New Features** - Implement planned features from roadmap
- **Agent Development** - Create new specialized agents
- **Documentation** - Improve docs, tutorials, examples
- **Testing** - Add unit tests, integration tests
- **Performance** - Optimize slow operations
- **UI/UX** - Improve frontend components

---

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/devora-transformation.git
cd devora-transformation
```

### 2. Set Up Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Unix/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your local configuration
```

### 3. Set Up Frontend

```bash
cd frontend

# Install dependencies
npm install
# or
yarn install

# Copy environment template
cp .env.example .env

# Edit .env with backend URL
```

### 4. Start Development Servers

**Terminal 1 (Backend):**
```bash
cd backend
uvicorn server:app --reload --port 8000
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm start
```

### 5. Verify Setup

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## How to Contribute

### Reporting Bugs

Before creating a bug report:
1. **Check existing issues** to avoid duplicates
2. **Verify** the bug exists in the latest version
3. **Gather information** about your environment

**Bug Report Template:**
```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g., Windows 11]
- Browser: [e.g., Chrome 120]
- Python Version: [e.g., 3.10]
- Node Version: [e.g., 18.17]

**Additional context**
Any other relevant information.
```

### Suggesting Enhancements

**Feature Request Template:**
```markdown
**Is your feature request related to a problem?**
A clear description of the problem.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Alternative solutions or features you've considered.

**Additional context**
Any other context, mockups, or examples.
```

### Your First Code Contribution

Look for issues labeled:
- `good first issue` - Simple tasks for newcomers
- `help wanted` - Tasks where maintainers need help
- `documentation` - Docs improvements

**Workflow:**
1. Comment on the issue to express interest
2. Wait for assignment/approval
3. Create a feature branch
4. Implement changes
5. Submit pull request

---

## Coding Standards

### Python (Backend)

**Style Guide:**
- Follow **PEP 8** style guide
- Use **type hints** for all functions
- Maximum line length: **100 characters**
- Use **async/await** for I/O operations

**Example:**
```python
from typing import List, Optional
from pydantic import BaseModel


class Project(BaseModel):
    """Represents a user project."""

    id: str
    name: str
    description: Optional[str] = None
    files: List[ProjectFile] = []


async def create_project(
    project: Project,
    user_id: str
) -> Project:
    """
    Create a new project in the database.

    Args:
        project: The project to create
        user_id: The ID of the user creating the project

    Returns:
        The created project with ID and timestamps

    Raises:
        HTTPException: If database operation fails
    """
    try:
        doc = project.model_dump()
        doc['user_id'] = user_id
        await db.projects.insert_one(doc)
        return project
    except Exception as e:
        raise HTTPException(500, f"Failed to create project: {str(e)}")
```

**Naming Conventions:**
- Functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_leading_underscore`

### JavaScript/React (Frontend)

**Style Guide:**
- Use **ES6+ syntax**
- Prefer **functional components** with hooks
- Use **prop-types** or TypeScript for type checking
- Maximum line length: **100 characters**

**Example:**
```javascript
import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';


/**
 * ProjectCard component displays a project summary.
 *
 * @param {Object} props - Component props
 * @param {Object} props.project - Project data
 * @param {Function} props.onSelect - Callback when project is selected
 */
function ProjectCard({ project, onSelect }) {
  const [loading, setLoading] = useState(false);

  const handleClick = async () => {
    setLoading(true);
    try {
      await onSelect(project.id);
    } catch (error) {
      console.error('Failed to select project:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader>
        <h3 className="text-xl font-semibold">{project.name}</h3>
      </CardHeader>
      <CardContent>
        <p className="text-gray-600">{project.description}</p>
        <Button onClick={handleClick} disabled={loading}>
          {loading ? 'Opening...' : 'Open Project'}
        </Button>
      </CardContent>
    </Card>
  );
}

ProjectCard.propTypes = {
  project: PropTypes.shape({
    id: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    description: PropTypes.string
  }).isRequired,
  onSelect: PropTypes.func.isRequired
};

export default ProjectCard;
```

**Naming Conventions:**
- Components: `PascalCase`
- Files: `PascalCase` for components, `camelCase` for utilities
- Functions: `camelCase`
- Constants: `UPPER_SNAKE_CASE`

### Commit Messages

Follow **Conventional Commits** specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
feat(agents): add TypeScript generation agent

- Implement TypeScriptAgent class
- Add type inference logic
- Include unit tests

Closes #123

---

fix(frontend): resolve Monaco editor crash on large files

The editor would freeze when loading files >1MB.
Added pagination and lazy loading.

Fixes #456

---

docs(api): update OpenAPI spec for /generate/fullstack endpoint

Added missing request/response schemas and examples.
```

---

## Testing Guidelines

### Backend Testing (pytest)

**Test Structure:**
```
backend/
  tests/
    __init__.py
    test_agents.py
    test_routes.py
    test_services.py
    test_integration.py
```

**Example Test:**
```python
import pytest
from fastapi.testclient import TestClient
from server import app


client = TestClient(app)


@pytest.fixture
def sample_project():
    """Fixture providing a sample project."""
    return {
        "name": "Test Project",
        "description": "A test project",
        "files": [
            {"name": "index.html", "content": "<html></html>", "language": "html"}
        ]
    }


def test_create_project(sample_project):
    """Test project creation endpoint."""
    response = client.post("/api/projects", json=sample_project)

    assert response.status_code == 200
    data = response.json()
    assert data['name'] == sample_project['name']
    assert 'id' in data
    assert 'created_at' in data


def test_get_project_not_found():
    """Test retrieving a non-existent project."""
    response = client.get("/api/projects/nonexistent-id")

    assert response.status_code == 404
    assert 'not found' in response.json()['detail'].lower()
```

**Running Tests:**
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_agents.py

# Run with coverage
pytest --cov=. --cov-report=html

# Run with verbose output
pytest -v
```

### Frontend Testing (Jest/React Testing Library)

**Example Test:**
```javascript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ProjectCard from '../components/ProjectCard';


describe('ProjectCard', () => {
  const mockProject = {
    id: '123',
    name: 'Test Project',
    description: 'Test description'
  };

  const mockOnSelect = jest.fn();

  it('renders project information', () => {
    render(<ProjectCard project={mockProject} onSelect={mockOnSelect} />);

    expect(screen.getByText('Test Project')).toBeInTheDocument();
    expect(screen.getByText('Test description')).toBeInTheDocument();
  });

  it('calls onSelect when button is clicked', async () => {
    render(<ProjectCard project={mockProject} onSelect={mockOnSelect} />);

    const button = screen.getByRole('button', { name: /open project/i });
    fireEvent.click(button);

    await waitFor(() => {
      expect(mockOnSelect).toHaveBeenCalledWith('123');
    });
  });
});
```

**Running Tests:**
```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch
```

### Integration Tests

Test the full stack interaction:

```python
import pytest
from agents.orchestrator_v2 import OrchestratorV2


@pytest.mark.asyncio
async def test_fullstack_generation():
    """Test complete fullstack generation workflow."""
    orchestrator = OrchestratorV2(
        model="gpt-4o",
        api_key=os.environ['OPENROUTER_API_KEY']
    )

    result = await orchestrator.orchestrate(
        prompt="Create a simple blog with authentication",
        context={"project_type": "blog"}
    )

    assert result['files'] is not None
    assert 'app/page.tsx' in [f['name'] for f in result['files']]
    assert result['review']['status'] == 'APPROVE'
```

---

## Pull Request Process

### 1. Create a Branch

```bash
# Update main branch
git checkout main
git pull origin main

# Create feature branch
git checkout -b feat/your-feature-name
```

### 2. Make Changes

- Write code following style guidelines
- Add/update tests
- Update documentation if needed
- Run linters and tests locally

### 3. Commit Changes

```bash
git add .
git commit -m "feat(scope): brief description"
```

### 4. Push to Your Fork

```bash
git push origin feat/your-feature-name
```

### 5. Create Pull Request

On GitHub:
1. Navigate to your fork
2. Click "New Pull Request"
3. Select your feature branch
4. Fill out the PR template

**PR Template:**
```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## How Has This Been Tested?
Describe the tests you ran to verify your changes.

## Checklist
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
```

### 6. Code Review

- Maintainers will review your PR
- Address any feedback
- Make requested changes
- Push updates to your branch (they will automatically update the PR)

### 7. Merge

Once approved:
- Maintainers will merge your PR
- Your branch will be deleted
- Changes will appear in the main branch

---

## Agent Development

### Creating a New Agent

**File Structure:**
```python
# backend/agents/your_new_agent.py

from .base_agent import BaseAgent
from typing import Dict, Any


class YourNewAgent(BaseAgent):
    """
    Agent responsible for [specific task].

    This agent handles [detailed description of responsibility].
    """

    SYSTEM_PROMPT = """
    You are an expert in [domain].

    Your task is to [specific instructions].

    Guidelines:
    - [Guideline 1]
    - [Guideline 2]
    - [Guideline 3]
    """

    async def generate(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate output based on input data.

        Args:
            input_data: Input specifications

        Returns:
            Generated output with metadata
        """
        prompt = self._build_prompt(input_data)
        response = await self.call_llm(prompt, input_data)
        return self._parse_response(response)

    def _build_prompt(self, input_data: Dict[str, Any]) -> str:
        """Build the generation prompt."""
        # Implementation
        pass

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response."""
        # Implementation
        pass
```

**Testing Your Agent:**
```python
# backend/tests/test_your_new_agent.py

import pytest
from agents.your_new_agent import YourNewAgent


@pytest.mark.asyncio
async def test_agent_generation():
    """Test agent generates expected output."""
    agent = YourNewAgent(model="gpt-4o", api_key="test-key")

    result = await agent.generate({
        "requirement": "Test requirement"
    })

    assert result is not None
    assert 'output' in result
```

### Integrating Agent into Orchestrator

```python
# backend/agents/orchestrator_v2.py

from .your_new_agent import YourNewAgent

class OrchestratorV2:
    def __init__(self, model: str, api_key: str):
        # Existing agents
        self.your_new_agent = YourNewAgent(model, api_key)

    async def orchestrate(self, ...):
        # Add to parallel execution
        your_task = self.your_new_agent.generate(data)

        results = await asyncio.gather(
            frontend_task,
            backend_task,
            database_task,
            your_task  # Add here
        )
```

---

## Documentation

### Updating Documentation

When making changes:
- Update relevant markdown files
- Add code examples
- Update API documentation (OpenAPI spec)
- Add/update architecture diagrams if needed

### Documentation Structure

```
docs/
├── ARCHITECTURE.md      # System architecture
├── CONTRIBUTING.md      # This file
├── api/
│   ├── openapi.yaml     # OpenAPI specification
│   └── examples/        # API usage examples
├── adr/                 # Architecture Decision Records
│   ├── ADR-001-multi-agent-architecture.md
│   ├── ADR-002-mongodb-choice.md
│   └── ADR-003-deployment-strategy.md
└── sdk/                 # SDK documentation
    ├── python.md
    └── javascript.md
```

### Writing Good Documentation

- **Be clear and concise**
- **Include examples**
- **Keep it up-to-date**
- **Use proper formatting** (headings, code blocks, lists)
- **Add diagrams** for complex concepts

---

## Questions?

If you have questions about contributing:

- **Check existing documentation** first
- **Search closed issues** for similar questions
- **Open a discussion** on GitHub Discussions
- **Ask in Discord** (if available)
- **Email maintainers** as last resort

---

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Recognized in the project README

Thank you for contributing to Devora!
