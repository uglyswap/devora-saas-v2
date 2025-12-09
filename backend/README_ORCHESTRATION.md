# Intégration du Système d'Orchestration dans Devora Backend

Ce dossier contient l'intégration complète du nouveau système d'orchestration multi-agents dans le backend FastAPI de Devora.

## Fichiers créés

### 1. `routes_orchestration.py` (Principal)
Routes API FastAPI pour exposer le système d'orchestration.

**Fonctionnalités:**
- Exécution de tâches orchestrées avec squads spécialisées
- Workflows prédéfinis (code review, architecture, testing, etc.)
- Quality gate automatique
- Progression en temps réel via WebSocket et SSE
- Gestion des tâches avec statuts et métriques

**Endpoints créés:**
- `POST /api/orchestrate` - Exécuter une tâche
- `POST /api/orchestrate/workflow/{workflow_name}` - Exécuter un workflow
- `GET /api/orchestrate/squads` - Lister les squads
- `GET /api/orchestrate/agents` - Lister les agents
- `GET /api/orchestrate/workflows` - Lister les workflows
- `POST /api/orchestrate/quality-gate` - Quality gate
- `GET /api/orchestrate/status/{task_id}` - Statut d'une tâche
- `WebSocket /api/orchestrate/ws/{task_id}` - Progression temps réel
- `GET /api/orchestrate/stream/{task_id}` - SSE stream
- `GET /api/orchestrate/health` - Health check

### 2. `ORCHESTRATION_INTEGRATION.md`
Documentation complète de l'intégration avec exemples d'utilisation.

**Contient:**
- Instructions de modification de server.py
- Exemples d'utilisation Python et JavaScript
- Guide de test des endpoints
- Documentation des modèles de données
- Notes de sécurité et prochaines étapes

### 3. `server_orchestration_patch.py`
Patch montrant exactement les modifications à apporter à `server.py`.

**Modifications:**
1. Ajouter l'import du router d'orchestration
2. Inclure le router dans l'application
3. Mettre à jour le version et features (optionnel)

### 4. `test_orchestration_integration.py`
Suite de tests automatisés pour valider l'intégration.

**Tests:**
- Connectivité serveur
- Health check orchestration
- Liste des squads, agents, workflows
- Création de tâche
- Récupération de statut
- Quality gate
- Gestion d'erreurs (404, etc.)

**Usage:**
```bash
python test_orchestration_integration.py
```

### 5. `example_orchestration_client.py`
Exemples complets d'utilisation du client Python.

**Exemples:**
1. Tâche simple avec polling
2. Tâche avec WebSocket tracking
3. Workflow de code review
4. Exécution du quality gate
5. Liste des ressources disponibles

**Usage:**
```bash
# Tous les exemples
python example_orchestration_client.py

# Exemple spécifique
python example_orchestration_client.py 1
```

## Installation

### Prérequis
- Python 3.9+
- FastAPI installé
- Module orchestration dans `../orchestration/`
- MongoDB (pour persistance des tâches)
- OpenRouter API key

### Étapes d'installation

1. **Copier les fichiers**
   ```bash
   # Les fichiers sont déjà dans backend/
   ls -la routes_orchestration.py
   ```

2. **Modifier server.py**
   ```python
   # Ajouter l'import (ligne ~22)
   from routes_orchestration import router as orchestration_router

   # Inclure le router (ligne ~865)
   app.include_router(orchestration_router, prefix="/api")
   ```

3. **Vérifier les dépendances**
   ```bash
   pip install fastapi uvicorn websockets pydantic
   ```

4. **Vérifier le module orchestration**
   ```bash
   # Doit contenir:
   # orchestration/core/__init__.py
   # orchestration/core/base_agent.py
   # orchestration/utils/llm_client.py
   ls -la ../orchestration/
   ```

5. **Configurer les variables d'environnement**
   ```bash
   export OPENROUTER_API_KEY="sk-or-v1-..."
   export MONGO_URL="mongodb://localhost:27017"
   ```

6. **Lancer le serveur**
   ```bash
   cd backend/
   uvicorn server:app --reload --port 8000
   ```

## Test de l'intégration

### Test rapide
```bash
# 1. Health check
curl http://localhost:8000/api/orchestrate/health

# 2. Lister les squads
curl http://localhost:8000/api/orchestrate/squads

# 3. Créer une tâche
curl -X POST http://localhost:8000/api/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "task_description": "Create a TODO API",
    "model": "anthropic/claude-3.5-sonnet",
    "api_key": "sk-or-v1-xxx",
    "priority": "medium"
  }'
```

### Suite de tests complète
```bash
python test_orchestration_integration.py
```

Résultat attendu:
```
Starting Orchestration Integration Tests
Base URL: http://localhost:8000

✓ PASS - Server is running and responsive
✓ PASS - Orchestration feature is listed in API features
✓ PASS - Health endpoint responds with 200
✓ PASS - Squads endpoint responds with 200
...

✓ ALL TESTS PASSED
```

## Utilisation

### Exemple Python simple

```python
import requests

# Créer une tâche
response = requests.post("http://localhost:8000/api/orchestrate", json={
    "task_description": "Create a REST API for user management",
    "model": "anthropic/claude-3.5-sonnet",
    "api_key": "your-key",
    "enable_quality_gate": true
})

task_id = response.json()["task_id"]

# Suivre la progression
import time
while True:
    status = requests.get(f"http://localhost:8000/api/orchestrate/status/{task_id}").json()
    print(f"Progress: {status['progress']}%")

    if status["status"] in ["completed", "failed"]:
        print(f"Result: {status['result']}")
        break

    time.sleep(2)
```

### Exemple JavaScript (Frontend)

```javascript
// Créer une tâche
const response = await fetch('http://localhost:8000/api/orchestrate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        task_description: 'Create a TODO app',
        model: 'anthropic/claude-3.5-sonnet',
        api_key: 'your-key',
        priority: 'high'
    })
});

const { task_id } = await response.json();

// Suivre avec WebSocket
const ws = new WebSocket(`ws://localhost:8000/api/orchestrate/ws/${task_id}`);

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.event === 'progress_update') {
        console.log(`Progress: ${data.progress}%`);
    } else if (data.event === 'task_completed') {
        console.log('Completed:', data.result);
        ws.close();
    }
};
```

### Exemple avec le client Python

```python
from example_orchestration_client import DevoraOrchestrationClient

# Initialiser le client
client = DevoraOrchestrationClient(api_url="http://localhost:8000")

# Créer et suivre une tâche
response = client.create_task(
    task_description="Design a microservices architecture",
    context={"services": ["User", "Product", "Order"]},
    enable_quality_gate=True
)

task_id = response["task_id"]
final_status = client.wait_for_completion(task_id, verbose=True)

print(f"Result: {final_status['result']}")
```

## Architecture

### Flux de données

```
Client Request
    ↓
FastAPI Router (routes_orchestration.py)
    ↓
Task Creation & Storage (in-memory/MongoDB)
    ↓
Async Execution (execute_orchestrated_task)
    ↓
Orchestration System (../orchestration/)
    ↓
Squads & Agents (Business, Engineering, QA)
    ↓
LLM Calls (OpenRouter API)
    ↓
Quality Gate (if enabled)
    ↓
Results Storage & Broadcast
    ↓
WebSocket/SSE Notifications
    ↓
Client receives updates
```

### Modèles de données

**OrchestrationRequest:**
- task_description: str
- context: dict
- model: str
- api_key: str
- priority: TaskPriority
- max_iterations: int
- enable_quality_gate: bool
- squad_type: SquadType (optionnel)

**TaskResponse:**
- task_id: str
- status: TaskStatus
- message: str
- created_at: datetime
- estimated_duration: int

**TaskStatusResponse:**
- task_id: str
- status: TaskStatus
- progress: float (0-100)
- current_step: str
- agents_involved: list
- metrics: dict
- result: dict
- error: str
- created_at: datetime
- updated_at: datetime
- completed_at: datetime

## Squads et Agents

### Business Squad
**Agents:**
- Product Manager
- Business Analyst

**Workflows:**
- Feature development
- Requirements analysis
- User story creation

### Engineering Squad
**Agents:**
- Architect
- Frontend Developer
- Backend Developer
- DevOps Engineer

**Workflows:**
- Architecture design
- Code implementation
- Refactoring
- Code review

### QA Squad
**Agents:**
- QA Tester
- Quality Analyst
- Security Auditor

**Workflows:**
- Testing
- Code review
- Quality assurance
- Security audit

### Full-Stack Squad
Combinaison de toutes les squads pour des projets complexes.

## Workflows prédéfinis

1. **code_review** - Review de code complet
2. **architecture_design** - Design d'architecture système
3. **feature_development** - Développement de feature
4. **bug_fix** - Analyse et fix de bug
5. **testing** - Génération et exécution de tests
6. **refactoring** - Refactoring de code
7. **documentation** - Génération de documentation
8. **optimization** - Optimisation de performance

## Quality Gate

Le quality gate vérifie automatiquement:
- ✓ Couverture de tests (min 80%)
- ✓ Qualité du code (score 85+)
- ✓ Standards de sécurité
- ✓ Documentation complète
- ✓ Performance acceptable

**Utilisation:**
```python
result = client.run_quality_gate(
    artifacts=[...],
    requirements={
        "min_test_coverage": 80,
        "code_quality_score": 85,
        "security_scan": True
    }
)

if result["passed"]:
    print("✓ Quality gate passed!")
else:
    print("✗ Quality gate failed:", result["blockers"])
```

## Progression en temps réel

### Option 1: Polling (Simple)
```python
while True:
    status = get_task_status(task_id)
    if status["status"] in ["completed", "failed"]:
        break
    time.sleep(2)
```

### Option 2: WebSocket (Recommandé)
```javascript
const ws = new WebSocket(`ws://localhost:8000/api/orchestrate/ws/${task_id}`);
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(data.event, data);
};
```

### Option 3: Server-Sent Events (Alternative)
```javascript
const eventSource = new EventSource(`http://localhost:8000/api/orchestrate/stream/${task_id}`);
eventSource.addEventListener('progress', (e) => {
    const data = JSON.parse(e.data);
    console.log(`Progress: ${data.progress}%`);
});
```

## Documentation API

Une fois le serveur lancé, la documentation interactive est disponible:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Cherchez la section **"orchestration"** pour voir tous les endpoints.

## Troubleshooting

### Erreur: Module 'orchestration' not found
**Cause:** Le module orchestration n'est pas accessible.

**Solution:**
```bash
# Vérifier que le dossier existe
ls -la ../orchestration/

# Vérifier que __init__.py existe
ls -la ../orchestration/core/__init__.py

# Ajouter au PYTHONPATH si nécessaire
export PYTHONPATH="${PYTHONPATH}:/path/to/devora-transformation"
```

### Erreur: orchestration_enabled = false
**Cause:** Import du module orchestration a échoué.

**Solution:**
- Vérifier les logs au démarrage du serveur
- Vérifier que toutes les dépendances sont installées
- Vérifier la structure du module orchestration

### Erreur: WebSocket connection refused
**Cause:** WebSocket non supporté par le serveur.

**Solution:**
```bash
# Lancer avec support WebSocket
uvicorn server:app --reload --ws-ping-interval 20
```

### Erreur: 503 Service Unavailable
**Cause:** ORCHESTRATION_ENABLED = False dans routes_orchestration.py.

**Solution:**
- Corriger les imports du module orchestration
- Redémarrer le serveur

### Erreur: Task not found (404)
**Cause:** Task_id invalide ou tâche expirée.

**Solution:**
- Vérifier que le task_id est correct
- Implémenter la persistance en DB (actuellement en mémoire)

## Prochaines étapes

### Phase 1: Implémentation de base (Actuel)
- ✅ Routes API créées
- ✅ Modèles de données définis
- ✅ WebSocket support
- ✅ Documentation complète
- ⏳ Intégration avec le vrai système d'orchestration

### Phase 2: Intégration complète
- [ ] Connecter au système d'orchestration réel
- [ ] Implémenter les workflows réels
- [ ] Implémenter le quality gate réel
- [ ] Persistance MongoDB des tâches
- [ ] Authentification et autorisation

### Phase 3: Production-ready
- [ ] Rate limiting
- [ ] Monitoring et métriques
- [ ] Logs structurés
- [ ] Tests unitaires et d'intégration
- [ ] Documentation déployée
- [ ] CI/CD pipeline

### Phase 4: Features avancées
- [ ] Tâches récurrentes
- [ ] Workflows custom
- [ ] Multi-tenant support
- [ ] API versioning
- [ ] GraphQL API alternative

## Support et contribution

### Rapporter un bug
Créer une issue avec:
- Description du problème
- Étapes pour reproduire
- Logs pertinents
- Version de Python, FastAPI, etc.

### Proposer une amélioration
Créer une PR avec:
- Description de la feature
- Tests ajoutés
- Documentation mise à jour

### Questions
Consulter:
- Cette documentation
- `ORCHESTRATION_INTEGRATION.md`
- Code source de `routes_orchestration.py`
- Exemples dans `example_orchestration_client.py`

## Licence

Même licence que le projet Devora principal.

---

**Créé le:** 2025-01-15
**Version:** 1.0.0
**Auteur:** Devora Team
**Statut:** En développement actif
