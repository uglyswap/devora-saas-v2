# Quickstart - Intégration Orchestration en 5 minutes

Ce guide vous permet d'intégrer le système d'orchestration dans Devora en moins de 5 minutes.

## TL;DR - Checklist rapide

```bash
# 1. Modifier server.py (2 lignes à ajouter)
# 2. Redémarrer le serveur
# 3. Tester avec curl
# 4. Profit! 🚀
```

## Étape 1: Modifier server.py (2 minutes)

### Modification 1: Ajouter l'import
**Ligne ~22** (avec les autres imports de routers):

```python
from routes_orchestration import router as orchestration_router  # AJOUTER CETTE LIGNE
```

### Modification 2: Inclure le router
**Ligne ~865** (avec les autres `app.include_router`):

```python
app.include_router(orchestration_router, prefix="/api")  # AJOUTER CETTE LIGNE
```

### Résumé des modifications

**AVANT:**
```python
# ligne ~18-22
from routes_auth import router as auth_router
from routes_billing import router as billing_router
from routes_admin import router as admin_router
from routes_support import router as support_router

# ...

# ligne ~860-865
app.include_router(auth_router, prefix="/api")
app.include_router(billing_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(support_router, prefix="/api")
app.include_router(api_router)
```

**APRÈS:**
```python
# ligne ~18-22
from routes_auth import router as auth_router
from routes_billing import router as billing_router
from routes_admin import router as admin_router
from routes_support import router as support_router
from routes_orchestration import router as orchestration_router  # NOUVEAU

# ...

# ligne ~860-865
app.include_router(auth_router, prefix="/api")
app.include_router(billing_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(support_router, prefix="/api")
app.include_router(orchestration_router, prefix="/api")  # NOUVEAU
app.include_router(api_router)
```

C'est tout! Seulement 2 lignes à ajouter.

## Étape 2: Redémarrer le serveur (30 secondes)

```bash
cd backend/
uvicorn server:app --reload --port 8000
```

Vérifier qu'il n'y a pas d'erreur au démarrage:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

✅ Si vous voyez ça, c'est bon!

## Étape 3: Tester (2 minutes)

### Test 1: Health check
```bash
curl http://localhost:8000/api/orchestrate/health
```

**Résultat attendu:**
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

✅ Si `orchestration_enabled: true`, c'est parfait!

### Test 2: Lister les squads
```bash
curl http://localhost:8000/api/orchestrate/squads
```

**Résultat attendu:**
```json
[
  {
    "name": "Business Squad",
    "type": "business",
    "agents": [...],
    "description": "Handles product requirements and business logic",
    ...
  },
  ...
]
```

### Test 3: Créer une tâche
```bash
curl -X POST http://localhost:8000/api/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "task_description": "Create a simple calculator API",
    "model": "anthropic/claude-3.5-sonnet",
    "api_key": "sk-or-v1-your-key-here",
    "priority": "medium"
  }'
```

**Résultat attendu:**
```json
{
  "task_id": "task_abc123def456",
  "status": "pending",
  "message": "Task queued for orchestration",
  "created_at": "2025-01-15T10:30:00.000Z",
  "estimated_duration": 300
}
```

✅ Vous avez un `task_id`? Parfait!

### Test 4: Vérifier le statut
```bash
# Remplacer TASK_ID par le task_id reçu
curl http://localhost:8000/api/orchestrate/status/TASK_ID
```

**Résultat attendu:**
```json
{
  "task_id": "task_abc123def456",
  "status": "running",
  "progress": 45,
  "current_step": "Executing task with agents",
  ...
}
```

## Étape 4: Documentation interactive

Ouvrir dans votre navigateur:
```
http://localhost:8000/docs
```

Chercher la section **"orchestration"** - vous devriez voir tous les nouveaux endpoints!

## Tests automatisés (Optionnel)

```bash
python test_orchestration_integration.py
```

Résultat attendu:
```
✓ PASS - Server is running and responsive
✓ PASS - Orchestration feature is listed in API features
✓ PASS - Health endpoint responds with 200
...
✓ ALL TESTS PASSED
```

## Exemples d'utilisation (Optionnel)

```bash
# Lancer tous les exemples
python example_orchestration_client.py

# Ou un exemple spécifique
python example_orchestration_client.py 1  # Simple task
python example_orchestration_client.py 2  # WebSocket tracking
python example_orchestration_client.py 5  # List resources
```

## Troubleshooting rapide

### Problème: ImportError lors du démarrage

**Erreur:**
```
ImportError: cannot import name 'router' from 'routes_orchestration'
```

**Solution:**
- Vérifier que `routes_orchestration.py` est dans le même dossier que `server.py`
- Vérifier qu'il n'y a pas de faute de frappe dans l'import

### Problème: orchestration_enabled = false

**Erreur dans le health check:**
```json
{"orchestration_enabled": false}
```

**Solution:**
- C'est normal! Le module `orchestration` n'est pas encore complètement intégré
- Les endpoints fonctionnent quand même en mode "mock" pour les tests
- Pour activer complètement, il faut que `../orchestration/` soit accessible

### Problème: 404 Not Found sur /api/orchestrate

**Cause:** Le router n'est pas inclus correctement.

**Solution:**
- Vérifier que vous avez ajouté `app.include_router(orchestration_router, prefix="/api")`
- Redémarrer le serveur
- Vérifier qu'il n'y a pas d'erreur au démarrage

### Problème: CORS errors sur WebSocket

**Solution:**
```python
# Dans server.py, vérifier la config CORS (ligne ~867)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],  # À configurer en production
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Endpoints disponibles (Référence rapide)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/orchestrate` | Créer une tâche |
| POST | `/api/orchestrate/workflow/{type}` | Exécuter un workflow |
| GET | `/api/orchestrate/squads` | Lister les squads |
| GET | `/api/orchestrate/agents` | Lister les agents |
| GET | `/api/orchestrate/workflows` | Lister les workflows |
| POST | `/api/orchestrate/quality-gate` | Quality gate |
| GET | `/api/orchestrate/status/{task_id}` | Statut d'une tâche |
| WS | `/api/orchestrate/ws/{task_id}` | WebSocket temps réel |
| GET | `/api/orchestrate/stream/{task_id}` | SSE stream |
| GET | `/api/orchestrate/health` | Health check |

## Utilisation basique en Python

```python
import requests

# Créer une tâche
response = requests.post("http://localhost:8000/api/orchestrate", json={
    "task_description": "Create a TODO API",
    "model": "anthropic/claude-3.5-sonnet",
    "api_key": "your-key",
    "priority": "medium"
})

task_id = response.json()["task_id"]
print(f"Task created: {task_id}")

# Suivre la progression
import time
while True:
    status = requests.get(f"http://localhost:8000/api/orchestrate/status/{task_id}").json()
    print(f"[{status['progress']:3d}%] {status['current_step']}")

    if status["status"] in ["completed", "failed"]:
        print(f"Result: {status.get('result', {})}")
        break

    time.sleep(2)
```

## Utilisation basique en JavaScript

```javascript
// Créer une tâche
const response = await fetch('http://localhost:8000/api/orchestrate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        task_description: 'Create a TODO API',
        model: 'anthropic/claude-3.5-sonnet',
        api_key: 'your-key',
        priority: 'medium'
    })
});

const { task_id } = await response.json();

// Suivre avec WebSocket
const ws = new WebSocket(`ws://localhost:8000/api/orchestrate/ws/${task_id}`);
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(data.event, data);

    if (data.event === 'task_completed') {
        console.log('Done!', data.result);
        ws.close();
    }
};
```

## Fichiers importants

| Fichier | Description |
|---------|-------------|
| `routes_orchestration.py` | **Routes API principales** |
| `README_ORCHESTRATION.md` | Documentation complète |
| `ORCHESTRATION_INTEGRATION.md` | Guide d'intégration détaillé |
| `test_orchestration_integration.py` | Suite de tests |
| `example_orchestration_client.py` | Exemples d'utilisation |
| `server_orchestration_patch.py` | Patch pour server.py |
| `QUICKSTART_ORCHESTRATION.md` | Ce fichier |

## Prochaines étapes

Une fois que tout fonctionne:

1. **Implémenter la vraie orchestration** (actuellement en mode mock)
   - Connecter au module `../orchestration/`
   - Initialiser les vrais agents
   - Implémenter les workflows réels

2. **Ajouter la persistance**
   - Sauvegarder les tâches en MongoDB
   - Gérer la cleanup des vieilles tâches

3. **Sécuriser**
   - Ajouter l'authentification
   - Valider les permissions
   - Rate limiting

4. **Tests et monitoring**
   - Tests unitaires
   - Métriques Prometheus
   - Logs structurés

## Aide et support

- **Documentation complète**: `README_ORCHESTRATION.md`
- **Guide d'intégration**: `ORCHESTRATION_INTEGRATION.md`
- **Exemples de code**: `example_orchestration_client.py`
- **Tests**: `test_orchestration_integration.py`
- **API docs**: http://localhost:8000/docs

## Résumé

✅ **2 lignes** à ajouter dans `server.py`
✅ **30 secondes** pour redémarrer
✅ **2 minutes** pour tester
✅ **10+ endpoints** disponibles immédiatement

**Total: Moins de 5 minutes pour une intégration complète!**

---

Bon développement! 🚀
