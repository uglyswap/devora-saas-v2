# Intégration du Système d'Orchestration dans server.py

## Modifications à apporter à server.py

### 1. Ajouter l'import du nouveau router

Ajouter cette ligne avec les autres imports de routers (autour de la ligne 18-22):

```python
from routes_orchestration import router as orchestration_router
```

### 2. Inclure le router dans l'application

Ajouter cette ligne avec les autres `app.include_router()` (autour de la ligne 860-865):

```python
app.include_router(orchestration_router, prefix="/api")
```

### Exemple de modification complète

```python
# ... autres imports ...
from routes_auth import router as auth_router
from routes_billing import router as billing_router
from routes_admin import router as admin_router
from routes_support import router as support_router
from routes_orchestration import router as orchestration_router  # NOUVEAU

# ... reste du code ...

# Include routers (ligne ~860)
app.include_router(auth_router, prefix="/api")
app.include_router(billing_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(support_router, prefix="/api")
app.include_router(orchestration_router, prefix="/api")  # NOUVEAU
app.include_router(api_router)
```

## Routes API disponibles après intégration

Une fois intégré, les nouvelles routes seront disponibles:

### Routes principales

- **POST /api/orchestrate**
  Exécute une tâche avec orchestration complète

- **POST /api/orchestrate/workflow/{workflow_name}**
  Exécute un workflow prédéfini (code_review, architecture_design, etc.)

- **GET /api/orchestrate/squads**
  Liste les squads disponibles (Business, Engineering, QA, Full-Stack)

- **GET /api/orchestrate/agents**
  Liste tous les agents disponibles

- **GET /api/orchestrate/workflows**
  Liste les workflows prédéfinis

- **POST /api/orchestrate/quality-gate**
  Exécute le quality gate sur des artefacts

- **GET /api/orchestrate/status/{task_id}**
  Récupère le statut d'une tâche

- **GET /api/orchestrate/health**
  Health check du système d'orchestration

### Routes temps réel

- **WebSocket /api/orchestrate/ws/{task_id}**
  Connexion WebSocket pour progression en temps réel

- **GET /api/orchestrate/stream/{task_id}**
  Server-Sent Events (SSE) pour progression

## Exemple d'utilisation

### Exécuter une tâche orchestrée

```python
import requests

response = requests.post("http://localhost:8000/api/orchestrate", json={
    "task_description": "Create a REST API for user management with CRUD operations",
    "context": {
        "tech_stack": ["FastAPI", "SQLAlchemy", "PostgreSQL"],
        "requirements": ["Authentication", "Role-based access"]
    },
    "model": "anthropic/claude-3.5-sonnet",
    "api_key": "your_openrouter_api_key",
    "priority": "high",
    "max_iterations": 3,
    "enable_quality_gate": true
})

task_id = response.json()["task_id"]
print(f"Task created: {task_id}")
```

### Suivre la progression (polling)

```python
import time

while True:
    status = requests.get(f"http://localhost:8000/api/orchestrate/status/{task_id}")
    data = status.json()

    print(f"Status: {data['status']}, Progress: {data['progress']}%")

    if data["status"] in ["completed", "failed"]:
        print(f"Result: {data['result']}")
        break

    time.sleep(2)
```

### Suivre la progression (WebSocket)

```javascript
// Frontend JavaScript
const ws = new WebSocket(`ws://localhost:8000/api/orchestrate/ws/${taskId}`);

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    switch(data.event) {
        case 'progress_update':
            console.log(`Progress: ${data.progress}%`);
            break;
        case 'task_completed':
            console.log('Task completed:', data.result);
            ws.close();
            break;
        case 'task_failed':
            console.error('Task failed:', data.error);
            ws.close();
            break;
    }
};
```

### Suivre la progression (SSE)

```javascript
// Frontend JavaScript avec EventSource
const eventSource = new EventSource(`http://localhost:8000/api/orchestrate/stream/${taskId}`);

eventSource.addEventListener('progress', (event) => {
    const data = JSON.parse(event.data);
    console.log(`Progress: ${data.progress}% - ${data.step}`);
});

eventSource.addEventListener('completed', (event) => {
    const data = JSON.parse(event.data);
    console.log('Completed:', data);
    eventSource.close();
});

eventSource.addEventListener('error', (event) => {
    console.error('Error:', event);
    eventSource.close();
});
```

### Exécuter un workflow prédéfini

```python
response = requests.post(
    "http://localhost:8000/api/orchestrate/workflow/code_review",
    json={
        "workflow_type": "code_review",
        "input_data": {
            "repository_url": "https://github.com/user/repo",
            "branch": "feature/new-api",
            "files": ["src/api/users.py", "tests/test_users.py"]
        },
        "model": "anthropic/claude-3.5-sonnet",
        "api_key": "your_openrouter_api_key",
        "priority": "medium"
    }
)
```

### Lister les squads et agents

```python
# Lister les squads
squads = requests.get("http://localhost:8000/api/orchestrate/squads")
print(squads.json())

# Lister les agents
agents = requests.get("http://localhost:8000/api/orchestrate/agents")
print(agents.json())

# Lister les workflows
workflows = requests.get("http://localhost:8000/api/orchestrate/workflows")
print(workflows.json())
```

### Exécuter le quality gate

```python
response = requests.post("http://localhost:8000/api/orchestrate/quality-gate", json={
    "artifacts": [
        {
            "type": "code",
            "path": "src/api/users.py",
            "content": "..."
        },
        {
            "type": "tests",
            "path": "tests/test_users.py",
            "coverage": 85
        }
    ],
    "requirements": {
        "min_test_coverage": 80,
        "code_quality_score": 85,
        "security_scan": true
    },
    "model": "anthropic/claude-3.5-sonnet",
    "api_key": "your_openrouter_api_key"
})

result = response.json()
print(f"Quality Gate: {'PASSED' if result['passed'] else 'FAILED'}")
print(f"Score: {result['score']}/100")
print(f"Recommendations: {result['recommendations']}")
```

## Tests

### Test du health check

```bash
curl http://localhost:8000/api/orchestrate/health
```

Réponse attendue:
```json
{
    "status": "healthy",
    "orchestration_enabled": true,
    "active_tasks": 0,
    "total_tasks": 0,
    "websocket_connections": 0,
    "timestamp": "2025-01-15T10:30:00.000Z"
}
```

### Test de création de tâche

```bash
curl -X POST http://localhost:8000/api/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "task_description": "Create a simple TODO API",
    "model": "anthropic/claude-3.5-sonnet",
    "api_key": "sk-or-v1-xxx",
    "priority": "medium",
    "enable_quality_gate": true
  }'
```

## Documentation interactive

Une fois le serveur lancé, accédez à:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Toutes les nouvelles routes d'orchestration seront automatiquement documentées avec leurs schémas, exemples, et descriptions.

## Prochaines étapes

1. **Implémenter la vraie logique d'orchestration**
   Actuellement, les endpoints retournent des données mockées. Il faut:
   - Connecter au vrai système d'orchestration dans `../orchestration/`
   - Initialiser les agents et squads
   - Implémenter les workflows réels
   - Implémenter le quality gate réel

2. **Ajouter la persistance**
   Les tâches sont actuellement stockées en mémoire. Pour la production:
   - Utiliser MongoDB pour persister les tâches
   - Créer des modèles de données appropriés
   - Gérer la cleanup des vieilles tâches

3. **Améliorer le WebSocket**
   - Gérer la reconnexion automatique
   - Implémenter les commandes client (pause, cancel)
   - Ajouter l'authentification WebSocket

4. **Monitoring et métriques**
   - Logs structurés
   - Métriques Prometheus
   - Tracing avec OpenTelemetry

5. **Tests**
   - Tests unitaires pour chaque endpoint
   - Tests d'intégration
   - Tests de charge pour le WebSocket

## Notes de sécurité

- Les clés API sont actuellement passées dans les requêtes. En production, utilisez l'authentification existante de Devora.
- Validez les permissions avant d'exécuter des tâches
- Limitez le nombre de tâches concurrentes par utilisateur
- Implémentez un timeout pour les tâches longues
- Sanitizez toutes les entrées utilisateur

## Support

Pour toute question ou problème, consultez:
- Documentation du système d'orchestration: `../orchestration/README.md`
- Code source: `routes_orchestration.py`
- Exemples: Ce fichier
