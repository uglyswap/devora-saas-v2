# Installation et Configuration - Devora Orchestration Core

## Prerequisites

- Python 3.8+
- Node.js 16+ (pour quality gate)
- npm 8+ (pour quality gate)
- OpenRouter API Key

## Installation Rapide

### 1. Verifier Python

```bash
python --version
# Doit afficher Python 3.8 ou superieur
```

### 2. Installer les dependances Python

```bash
pip install requests
```

### 3. Obtenir une API Key OpenRouter

1. Aller sur https://openrouter.ai
2. Creer un compte
3. Generer une API key
4. Copier la key

### 4. Configuration

Creer un fichier `.env` ou configurer les variables:

```bash
OPENROUTER_API_KEY=your-api-key-here
```

## Utilisation

### Test de base

```bash
cd C:/Users/quent/devora-transformation/orchestration/core
python test_orchestration.py
```

Resultat attendu: `5/5 tests passed`

### Exemple d'utilisation

```python
from orchestrator_ultimate import OrchestratorUltimate, OrchestratorRequest

# Initialisation
orchestrator = OrchestratorUltimate(
    api_key="your-openrouter-api-key",
    enable_quality_gate=True
)

# Creation de la requete
request = OrchestratorRequest(
    task="Build a REST API for user management",
    workflow="api_development"
)

# Execution
import asyncio
result = asyncio.run(orchestrator.execute(request))

# Affichage des resultats
print(f"Status: {result.status}")
print(f"Squads: {result.metrics['squads_executed']}")
print(f"Agents: {result.metrics['agents_executed']}")
```

## Configuration du Quality Gate

Le quality gate necessite Node.js et npm installes.

### Verifier Node.js

```bash
node --version
npm --version
```

### Installer les dependances (dans votre projet)

```bash
npm install --save-dev typescript eslint prettier jest
```

### Configurer ESLint

```bash
npm init @eslint/config
```

### Configurer TypeScript

Creer `tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "strict": true,
    "esModuleInterop": true
  }
}
```

## Desactiver le Quality Gate (temporaire)

Si vous voulez tester sans quality gate:

```python
orchestrator = OrchestratorUltimate(
    api_key="your-api-key",
    enable_quality_gate=False  # Desactive
)

# Ou par requete
request = OrchestratorRequest(
    task="...",
    quality_gate=False  # Desactive pour cette requete
)
```

## Workflows Disponibles

```python
# Lister tous les workflows
workflows = orchestrator.get_available_workflows()
print(workflows)

# Obtenir info sur un workflow
info = orchestrator.workflow_engine.get_workflow_info("full_stack_feature")
print(info)
```

## Squads Disponibles

```python
# Lister tous les squads
squads = orchestrator.get_available_squads()
print(squads)

# Obtenir info sur un squad
info = orchestrator.squad_manager.get_squad_info("architecture")
print(info)
```

## Callbacks pour SSE

```python
def my_callback(event, data):
    print(f"Event: {event}")
    print(f"Data: {data}")
    # Envoyer via SSE au frontend

orchestrator.callbacks.append(my_callback)
```

## Troubleshooting

### Erreur: "ImportError: No module named 'requests'"

```bash
pip install requests
```

### Erreur: "Quality gate failed: command not found"

Node.js/npm non installe. Installer depuis https://nodejs.org
ou desactiver quality gate.

### Erreur: "API key invalid"

Verifier votre API key OpenRouter.

### Tests echouent

Verifier que tous les fichiers sont presents:

```bash
ls -la
# Doit contenir:
# - orchestrator_ultimate.py
# - squad_manager.py
# - workflow_engine.py
# - quality_gate_engine.py
# - base_agent.py
```

## Performance

### Execution Parallele

Pour accelerer l'execution:

```python
request = OrchestratorRequest(
    task="...",
    mode=ExecutionMode.PARALLEL,  # Tous en parallele
    max_parallel=8  # Max 8 agents en meme temps
)
```

### Desactiver le Logging

```python
orchestrator = OrchestratorUltimate(
    api_key="...",
    log_level="ERROR"  # Seulement les erreurs
)
```

## Support

Pour les bugs ou questions:
- Voir README.md pour la documentation
- Voir ARCHITECTURE.md pour les details techniques
- Voir example_usage.py pour des exemples

## Next Steps

1. Tester avec `python test_orchestration.py`
2. Essayer les exemples dans `example_usage.py`
3. Creer votre premiere requete
4. Integrer avec votre application

Bon developpement avec Devora!
