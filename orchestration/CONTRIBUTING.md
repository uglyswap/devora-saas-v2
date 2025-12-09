# Contributing to Devora Orchestration

Merci de votre intérêt pour contribuer au système d'orchestration Devora! Ce guide vous aidera à démarrer.

---

## Table des Matières

- [Code of Conduct](#code-of-conduct)
- [Comment Contribuer](#comment-contribuer)
- [Développement Local](#développement-local)
- [Architecture](#architecture)
- [Créer un Nouvel Agent](#créer-un-nouvel-agent)
- [Créer un Workflow](#créer-un-workflow)
- [Standards de Code](#standards-de-code)
- [Tests](#tests)
- [Documentation](#documentation)
- [Process de Pull Request](#process-de-pull-request)

---

## Code of Conduct

Ce projet adhère au [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). En participant, vous acceptez de respecter ces règles.

---

## Comment Contribuer

### Signaler un Bug

1. Vérifiez que le bug n'a pas déjà été signalé dans [Issues](https://github.com/devora-ai/orchestration/issues)
2. Créez une nouvelle issue avec le template "Bug Report"
3. Incluez:
   - Description détaillée du problème
   - Steps pour reproduire
   - Comportement attendu vs actuel
   - Environnement (Python version, OS, etc.)
   - Logs/erreurs si disponibles

### Proposer une Feature

1. Créez une issue avec le template "Feature Request"
2. Décrivez:
   - Le problème que la feature résout
   - La solution proposée
   - Alternatives considérées
   - Impact sur l'architecture existante

### Contribuer du Code

1. Fork le repository
2. Créez une branche (`git checkout -b feature/AmazingFeature`)
3. Commitez vos changements (`git commit -m 'Add AmazingFeature'`)
4. Pushez vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

---

## Développement Local

### Prérequis

- Python 3.11+
- pip ou uv
- Git
- OpenRouter API key

### Installation

```bash
# Clone le repository
git clone https://github.com/devora-ai/orchestration.git
cd orchestration

# Créer environnement virtuel
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Installer dépendances
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Dev dependencies

# Configurer variables d'environnement
cp .env.example .env
# Éditer .env avec votre API key
```

### Structure du Projet

```
orchestration/
├── core/                   # Core components
│   ├── base_agent.py      # BaseAgent class
│   └── __init__.py
├── agents/                 # Agent implementations
│   ├── business_squad/
│   ├── frontend_squad/
│   ├── backend_squad/
│   ├── data_squad/
│   ├── devops_squad/
│   ├── qa_squad/
│   ├── performance_squad/
│   ├── accessibility_squad/
│   ├── ai_ml_squad/
│   └── documentation_squad/
├── workflows/              # Workflow implementations
│   ├── base.py
│   ├── full_stack.py
│   └── ...
├── utils/                  # Utility functions
│   ├── llm_client.py
│   └── logger.py
├── tests/                  # Tests
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docs/                   # Documentation
├── examples/               # Usage examples
└── scripts/                # Utility scripts
```

---

## Architecture

### BaseAgent

Tous les agents héritent de `BaseAgent`:

```python
from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseAgent(ABC):
    """Base class for all agents."""

    @abstractmethod
    def validate_input(self, input_data: Any) -> bool:
        """Validate input data."""
        pass

    @abstractmethod
    def execute(self, input_data: Any, **kwargs) -> Any:
        """Execute the agent's task."""
        pass

    @abstractmethod
    def format_output(self, raw_output: Any) -> Dict[str, Any]:
        """Format output data."""
        pass

    def run(self, input_data: Any, **kwargs) -> Dict[str, Any]:
        """Main entry point."""
        # Orchestrates: validate → execute → format
        pass
```

### Principes de Design

1. **Single Responsibility**: Un agent = une responsabilité claire
2. **Configuration via AgentConfig**: Tous les paramètres dans la config
3. **Métriques Automatiques**: Tracking automatique des tokens, temps, erreurs
4. **Error Handling Robuste**: Retry automatique, logging détaillé
5. **Callbacks pour Progression**: Support de callbacks pour UI/monitoring

---

## Créer un Nouvel Agent

### Template de Base

```python
"""
[Agent Name] - [Squad Name]

Description de l'agent et ses responsabilités.
"""

from typing import Any, Dict, List, Optional
import sys
import os

# Import BaseAgent
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))
from core.base_agent import BaseAgent, AgentConfig

class MyNewAgent(BaseAgent):
    """
    Description de l'agent.

    Capabilities:
    - Capability 1
    - Capability 2
    - Capability 3

    Example input:
        {
            "field1": value1,
            "field2": value2
        }

    Example output:
        {
            "status": "success",
            "result": {...}
        }
    """

    SYSTEM_PROMPT = """You are an expert [ROLE] with expertise in:

- Expertise 1
- Expertise 2
- Expertise 3

Your responsibilities:
- Responsibility 1
- Responsibility 2

Principles:
- Principle 1
- Principle 2

Output format:
- Format specification
"""

    def __init__(self, config: AgentConfig, callbacks: Optional[List] = None):
        """Initialize the agent."""
        super().__init__(config, callbacks)

    def validate_input(self, input_data: Any) -> bool:
        """Validate input data."""
        if not isinstance(input_data, dict):
            raise ValueError("Input must be a dictionary")

        # Vérifier champs requis
        required_fields = ["field1", "field2"]
        for field in required_fields:
            if field not in input_data:
                raise ValueError(f"Missing required field: {field}")

        return True

    def execute(self, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Execute the agent's task."""
        # Extraire inputs
        field1 = input_data.get("field1")
        field2 = input_data.get("field2")

        # Construire le prompt
        prompt = self._build_prompt(field1, field2)

        self.logger.info(f"Executing {self.config.name}")

        # Appeler le LLM
        response = self._call_llm(
            prompt=prompt,
            system_message=self.SYSTEM_PROMPT
        )

        return {
            "result": response["content"],
            "metadata": {
                "field1": field1,
                "timestamp": datetime.now().isoformat()
            }
        }

    def format_output(self, raw_output: Dict[str, Any]) -> Dict[str, Any]:
        """Format output data."""
        return {
            "content": raw_output["result"],
            "metadata": raw_output["metadata"]
        }

    def _build_prompt(self, field1: str, field2: str) -> str:
        """Build the prompt for the LLM."""
        return f"""Task: [DESCRIPTION]

Input 1: {field1}
Input 2: {field2}

Please:
1. Step 1
2. Step 2
3. Step 3

Output format: [FORMAT]
"""

    # Helper methods
    async def helper_method(self, param: str) -> Dict[str, Any]:
        """Convenience method for common task."""
        return self.run({
            "field1": param,
            "field2": "default"
        })
```

### Checklist pour Nouvel Agent

- [ ] Hérite de `BaseAgent`
- [ ] Implémente `validate_input()`, `execute()`, `format_output()`
- [ ] Docstring complète avec exemples
- [ ] System prompt bien défini
- [ ] Gestion d'erreurs appropriée
- [ ] Logging aux points clés
- [ ] Type hints pour tous les paramètres
- [ ] Tests unitaires (au moins 80% coverage)
- [ ] Documentation dans `AGENTS.md`
- [ ] Exemple d'utilisation dans `examples/`

---

## Créer un Workflow

### Template de Workflow

```python
"""
[Workflow Name]

Description du workflow et de son objectif.
"""

from typing import Dict, Any, List
import time
from datetime import datetime

from .base import BaseWorkflow
from ..agents.business_squad.product_manager import ProductManagerAgent
from ..agents.frontend_squad.ui_ux_designer import UIUXDesignerAgent

class MyWorkflow(BaseWorkflow):
    """
    Description du workflow.

    Squads impliquées:
    - Business Squad
    - Frontend Squad

    Steps:
    1. Step 1 description
    2. Step 2 description
    3. Step 3 description
    """

    def __init__(self, api_key: str, model: str = "anthropic/claude-3.5-sonnet"):
        super().__init__(api_key, model)

        # Initialize agents
        self.pm = ProductManagerAgent(self._create_config("pm"))
        self.designer = UIUXDesignerAgent(self._create_config("designer"))

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the workflow."""
        # Initialize context
        context = self._init_context(input_data)

        try:
            # Step 1: Product Management
            self.logger.info("Step 1: Product Management")
            pm_result = await self._run_step(
                agent=self.pm,
                input_data={
                    "task_type": "prd",
                    "context": input_data["description"]
                },
                context=context,
                step_name="product_management"
            )

            # Step 2: Design
            self.logger.info("Step 2: UI/UX Design")
            design_result = await self._run_step(
                agent=self.designer,
                input_data={
                    "task": "design_system",
                    "requirements": pm_result["output"]
                },
                context=context,
                step_name="design"
            )

            # Format final output
            return self._format_output(context)

        except Exception as e:
            return self._handle_error(e, context)

    def _init_context(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize workflow context."""
        return {
            "workflow": "my_workflow",
            "project_name": input_data.get("project_name", "Unnamed"),
            "start_time": time.time(),
            "steps_completed": [],
            "outputs": {},
            "metrics": {
                "total_tokens": 0,
                "total_time": 0.0,
                "agents_executed": 0
            }
        }

    async def _run_step(
        self,
        agent,
        input_data: Dict[str, Any],
        context: Dict[str, Any],
        step_name: str
    ) -> Dict[str, Any]:
        """Run a workflow step."""
        step_start = time.time()

        try:
            # Execute agent
            result = await agent.execute(input_data)

            # Update context
            context["outputs"][step_name] = result
            context["steps_completed"].append(step_name)

            # Update metrics
            if "metadata" in result:
                context["metrics"]["total_tokens"] += result["metadata"].get("total_tokens", 0)

            context["metrics"]["agents_executed"] += 1

            step_time = time.time() - step_start
            self.logger.info(f"Step {step_name} completed in {step_time:.2f}s")

            return result

        except Exception as e:
            self.logger.error(f"Step {step_name} failed: {str(e)}")
            raise

    def _format_output(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Format final workflow output."""
        context["metrics"]["total_time"] = time.time() - context["start_time"]

        return {
            "status": "success",
            "workflow": context["workflow"],
            "project_name": context["project_name"],
            "deliverables": context["outputs"],
            "metrics": context["metrics"],
            "steps_completed": context["steps_completed"],
            "timestamp": datetime.utcnow().isoformat()
        }

    def _handle_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle workflow error."""
        return {
            "status": "failed",
            "workflow": context["workflow"],
            "error": str(error),
            "steps_completed": context["steps_completed"],
            "metrics": context["metrics"],
            "timestamp": datetime.utcnow().isoformat()
        }
```

### Checklist pour Nouveau Workflow

- [ ] Hérite de `BaseWorkflow`
- [ ] Steps clairement définis et documentés
- [ ] Context management approprié
- [ ] Error handling à chaque step
- [ ] Métriques agrégées correctement
- [ ] Logging détaillé
- [ ] Tests d'intégration
- [ ] Documentation dans `WORKFLOWS.md`
- [ ] Exemple d'utilisation

---

## Standards de Code

### Python Style Guide

Nous suivons [PEP 8](https://peps.python.org/pep-0008/) avec quelques ajustements:

```python
# ✅ BON

class MyAgent(BaseAgent):
    """Agent description.

    Args:
        config: Agent configuration
        callbacks: Optional callbacks

    Attributes:
        name: Agent name
    """

    def execute(self, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Execute agent task.

        Args:
            input_data: Input dictionary
            **kwargs: Additional parameters

        Returns:
            Dictionary with result

        Raises:
            ValueError: If input is invalid
        """
        pass


# ❌ MAUVAIS

class myagent(BaseAgent):  # Mauvais naming
    def execute(self, input_data, **kwargs):  # Pas de type hints
        pass  # Pas de docstring
```

### Type Hints

```python
# ✅ BON: Type hints partout
from typing import Dict, Any, List, Optional

def process_data(
    data: Dict[str, Any],
    options: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Process data with options."""
    pass


# ❌ MAUVAIS: Pas de type hints
def process_data(data, options=None):
    pass
```

### Docstrings

Utiliser le format Google style:

```python
def complex_function(param1: str, param2: int) -> Dict[str, Any]:
    """Short description.

    Longer description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Dictionary containing:
            - key1: Description
            - key2: Description

    Raises:
        ValueError: If param1 is empty
        TypeError: If param2 is not int

    Example:
        >>> result = complex_function("test", 42)
        >>> print(result["key1"])
        'value1'
    """
    pass
```

### Formatage

```bash
# Install formatters
pip install black isort flake8 mypy

# Format code
black .
isort .

# Check style
flake8 .

# Type checking
mypy .
```

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

`.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/isort
    rev: 5.13.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=100]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

---

## Tests

### Structure des Tests

```
tests/
├── unit/                   # Tests unitaires
│   ├── agents/
│   │   ├── test_product_manager.py
│   │   └── test_ui_ux_designer.py
│   └── core/
│       └── test_base_agent.py
├── integration/            # Tests d'intégration
│   ├── test_workflows.py
│   └── test_agent_collaboration.py
├── e2e/                    # Tests end-to-end
│   └── test_full_stack_workflow.py
└── conftest.py             # Fixtures pytest
```

### Exemple de Test Unitaire

```python
# tests/unit/agents/test_product_manager.py

import pytest
from orchestration.agents.business_squad.product_manager import ProductManagerAgent
from orchestration.core.base_agent import AgentConfig

@pytest.fixture
def pm_agent():
    """Create ProductManager agent for testing."""
    config = AgentConfig(
        name="test_pm",
        api_key="test_key",
        model="test_model"
    )
    return ProductManagerAgent(config)

def test_validate_input_valid(pm_agent):
    """Test input validation with valid data."""
    input_data = {
        "task_type": "prd",
        "context": "Test context"
    }

    assert pm_agent.validate_input(input_data) is True

def test_validate_input_missing_field(pm_agent):
    """Test input validation with missing field."""
    input_data = {
        "context": "Test context"
        # Missing task_type
    }

    with pytest.raises(ValueError, match="Missing required field: task_type"):
        pm_agent.validate_input(input_data)

@pytest.mark.asyncio
async def test_execute_prd(pm_agent, mocker):
    """Test PRD generation."""
    # Mock LLM call
    mock_llm = mocker.patch.object(pm_agent, '_call_llm')
    mock_llm.return_value = {
        "content": "# PRD\n\n...",
        "usage": {"total_tokens": 1000}
    }

    input_data = {
        "task_type": "prd",
        "context": "Test app"
    }

    result = await pm_agent.execute(input_data)

    assert result["status"] == "success"
    assert "PRD" in result["output"]
    mock_llm.assert_called_once()
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-mock pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=orchestration --cov-report=html

# Run specific test file
pytest tests/unit/agents/test_product_manager.py

# Run specific test
pytest tests/unit/agents/test_product_manager.py::test_validate_input_valid

# Run with verbose output
pytest -v

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/
```

### Coverage Requirements

- **Minimum**: 80% coverage
- **Target**: 90%+ coverage
- **Critical paths**: 100% coverage (core, base_agent)

---

## Documentation

### Documenter un Agent

Ajouter une section dans `AGENTS.md`:

```markdown
### X. Agent Name

**Responsabilités**: Brief description

#### Capacités

- Capability 1
- Capability 2

#### Input Format

\`\`\`python
{
    "field1": type,
    "field2": type
}
\`\`\`

#### Output Format

\`\`\`python
{
    "status": "success" | "error",
    "result": {...}
}
\`\`\`

#### Exemples

\`\`\`python
# Example code
\`\`\`
```

### Documenter un Workflow

Ajouter dans `WORKFLOWS.md`:

```markdown
### X. Workflow Name

**Objectif**: Description

**Squads Impliquées**:
\`\`\`
Squad A → Squad B → Squad C
\`\`\`

**Étapes**: ...

**Input Format**: ...

**Output Format**: ...

**Exemple**: ...
```

---

## Process de Pull Request

### Avant de Soumettre

- [ ] Code formaté (black, isort)
- [ ] Pas d'erreurs flake8
- [ ] Type checking passe (mypy)
- [ ] Tests passent (pytest)
- [ ] Coverage >= 80%
- [ ] Documentation mise à jour
- [ ] CHANGELOG.md mis à jour
- [ ] Commits bien structurés

### Convention de Commits

Utiliser [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: Nouvelle feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Refactoring
- `test`: Tests
- `chore`: Maintenance

**Exemples**:
```
feat(agents): add SEO specialist agent

Implement new agent for SEO optimization with capabilities:
- Meta tags generation
- Schema markup
- Sitemap creation

Closes #123

---

fix(workflows): handle timeout in full stack workflow

Add timeout handling to prevent infinite wait on agent failure.

Fixes #456

---

docs(readme): update installation instructions

Add instructions for Windows users.
```

### Template de PR

```markdown
## Description

Brief description of changes.

## Type of Change

- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature breaking existing functionality)
- [ ] Documentation update

## Testing

Describe how you tested your changes.

## Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review performed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added/updated
- [ ] All tests pass locally
- [ ] Dependent changes merged

## Screenshots (if applicable)

Add screenshots here.
```

### Review Process

1. **Automated Checks**: CI runs tests, linting, coverage
2. **Code Review**: Au moins 1 approval requis
3. **Reviewer Feedback**: Adresser tous les commentaires
4. **Final Approval**: Merge autorisé

---

## Questions?

- **Documentation**: Lire [README.md](./README.md), [AGENTS.md](./AGENTS.md)
- **Discussions**: [GitHub Discussions](https://github.com/devora-ai/orchestration/discussions)
- **Chat**: [Discord](https://discord.gg/devora)
- **Email**: dev@devora.ai

---

**Merci de contribuer à Devora Orchestration!** 🚀
