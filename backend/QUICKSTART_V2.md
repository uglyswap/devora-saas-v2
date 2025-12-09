# Devora Backend API V2 - Quick Start Guide

## 🚀 Démarrage en 5 Minutes

### Prérequis
- Python 3.10+
- MongoDB (local ou Atlas)
- Redis (optionnel mais recommandé)

---

## 📦 Installation

### 1. Installer les dépendances
```bash
cd backend
pip install -r requirements-v2.txt
```

### 2. Configuration Redis (Optionnel)

**Option A: Docker (Recommandé)**
```bash
docker run -d \
  --name devora-redis \
  -p 6379:6379 \
  redis:7-alpine \
  redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
```

**Option B: Installation locale**
```bash
# Ubuntu/Debian
sudo apt install redis-server

# macOS
brew install redis

# Windows
# Télécharger depuis: https://github.com/microsoftarchive/redis/releases
```

### 3. Variables d'environnement

Créer `.env` avec:
```env
# Existant
MONGO_URL=mongodb://localhost:27017
DB_NAME=devora_db
SECRET_KEY=your-super-secret-key-change-this-in-production
FRONTEND_URL=http://localhost:3000

# Nouveau - Redis
REDIS_URL=redis://localhost:6379/0

# Nouveau - OAuth2 Google (optionnel)
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/google/callback

# Nouveau - OAuth2 GitHub (optionnel)
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
GITHUB_REDIRECT_URI=http://localhost:3000/auth/github/callback
```

### 4. Intégration dans server.py

**Ajouter ces lignes dans `server.py`:**

```python
# Au début du fichier, après les imports existants
from api_v2 import api_v2_router
from api_v2.middleware import limiter, rate_limit_exceeded_handler
from api_v2.middleware.cache import init_redis_cache
from slowapi.errors import RateLimitExceeded
import os

# Après app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Initialiser Redis (avec fallback gracieux)
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
try:
    init_redis_cache(redis_url)
    logging.info(f"✅ Redis cache activated: {redis_url}")
except Exception as e:
    logging.warning(f"⚠️  Redis unavailable, running without cache: {e}")

# Avant les autres routers
app.include_router(api_v2_router, prefix="/api")
```

### 5. Démarrer le serveur

```bash
uvicorn server:app --reload --port 8000
```

---

## ✅ Vérification de l'Installation

### Test 1: Health Check API V2
```bash
curl http://localhost:8000/api/v2/
```

**Résultat attendu:**
```json
{
  "message": "Devora API v2",
  "version": "2.0.0",
  "status": "operational",
  "features": [
    "rate-limiting",
    "redis-caching",
    "openapi-spec",
    "type-safety",
    "enhanced-error-handling"
  ]
}
```

### Test 2: OpenAPI Documentation
Ouvrir dans le navigateur:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Vérifier que les endpoints `/v2/auth/*`, `/v2/projects/*` apparaissent.**

### Test 3: Rate Limiting
```bash
# Envoyer 6 requêtes rapidement
for i in {1..6}; do
  curl -X POST http://localhost:8000/api/v2/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@test.com","password":"test"}'
  echo ""
done
```

**La 6ème requête doit retourner:**
```json
{
  "error": "rate_limit_exceeded",
  "message": "Trop de requêtes. Veuillez patienter avant de réessayer.",
  "retry_after": 60
}
```

### Test 4: Redis Cache (si activé)
```bash
# Vérifier que Redis répond
redis-cli ping
# Doit retourner: PONG

# Vérifier les clés en cache
redis-cli KEYS "*"
```

---

## 🎨 Générer les Types TypeScript

### Pour le Frontend

```bash
# Générer les types
python generate_typescript_types.py

# Copier vers le frontend (ajuster le chemin)
cp devora-api-types.ts ../frontend/src/types/

# Ou créer un lien symbolique
ln -s $(pwd)/devora-api-types.ts ../frontend/src/types/
```

**Utilisation dans le frontend:**
```typescript
import { UserResponse, ProjectResponse } from '@/types/devora-api-types';

const user: UserResponse = await fetch('/api/v2/auth/me').then(r => r.json());
```

---

## 🔧 Configuration OAuth2 (Optionnel)

### Google OAuth

1. **Créer un projet Google Cloud:**
   - https://console.cloud.google.com/

2. **Activer Google OAuth API:**
   - APIs & Services → OAuth consent screen
   - Type: External
   - Scopes: email, profile, openid

3. **Créer des credentials:**
   - Credentials → Create Credentials → OAuth 2.0 Client ID
   - Application type: Web application
   - Authorized redirect URIs: `http://localhost:3000/auth/google/callback`

4. **Copier Client ID et Secret dans `.env`**

### GitHub OAuth

1. **Créer une OAuth App:**
   - https://github.com/settings/developers
   - New OAuth App

2. **Configuration:**
   - Application name: Devora (Dev)
   - Homepage URL: `http://localhost:3000`
   - Authorization callback URL: `http://localhost:3000/auth/github/callback`

3. **Copier Client ID et Secret dans `.env`**

---

## 🧪 Tester l'API

### Option 1: cURL

**Inscription:**
```bash
curl -X POST http://localhost:8000/api/v2/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123",
    "full_name": "John Doe"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/v2/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123"
  }'
```

**Lister les projets (avec token):**
```bash
TOKEN="your-jwt-token-here"
curl http://localhost:8000/api/v2/projects \
  -H "Authorization: Bearer $TOKEN"
```

### Option 2: Postman/Insomnia

Importer la spec OpenAPI:
```
http://localhost:8000/openapi.json
```

Toutes les routes et schémas seront auto-importés.

### Option 3: Python Requests

```python
import requests

# Register
response = requests.post(
    "http://localhost:8000/api/v2/auth/register",
    json={
        "email": "test@example.com",
        "password": "SecurePass123",
        "full_name": "Test User"
    }
)
user = response.json()
print(user)

# Login
response = requests.post(
    "http://localhost:8000/api/v2/auth/login",
    json={
        "email": "test@example.com",
        "password": "SecurePass123"
    }
)
token = response.json()["access_token"]

# Get projects
response = requests.get(
    "http://localhost:8000/api/v2/projects",
    headers={"Authorization": f"Bearer {token}"}
)
projects = response.json()
print(projects)
```

---

## 📊 Monitoring

### Vérifier les Logs

```bash
# Logs en temps réel
tail -f logs/devora.log

# Filtrer les erreurs
grep "ERROR" logs/devora.log

# Voir les rate limits hits
grep "Rate limit exceeded" logs/devora.log
```

### Monitorer Redis

```bash
# Monitor en temps réel
redis-cli MONITOR

# Statistiques
redis-cli INFO stats

# Nombre de clés en cache
redis-cli DBSIZE

# Voir toutes les clés
redis-cli KEYS "*"

# Vider le cache (attention en production !)
redis-cli FLUSHDB
```

---

## 🐛 Troubleshooting

### Problème: "Stripe not configured"
**Solution:**
```bash
# Vérifier les variables d'environnement
echo $STRIPE_API_KEY

# Ou configurer via admin panel
# http://localhost:3000/admin/settings
```

### Problème: "Redis connection failed"
**Solution:**
```bash
# Vérifier que Redis tourne
redis-cli ping

# Si pas de réponse, démarrer Redis
# Docker: docker start devora-redis
# Local: sudo service redis-server start
```

### Problème: "Rate limit too strict"
**Solution:**
Modifier dans `api_v2/middleware/rate_limiter.py`:
```python
class RateLimits:
    AUTH_LOGIN = "10/minute"  # Au lieu de 5/minute
```

### Problème: "OAuth redirect mismatch"
**Solution:**
Vérifier que les redirect URIs dans Google/GitHub matchent exactement:
```
Google Console: http://localhost:3000/auth/google/callback
GitHub OAuth: http://localhost:3000/auth/github/callback
.env: GOOGLE_REDIRECT_URI=http://localhost:3000/auth/google/callback
```

---

## 📈 Next Steps

### Court terme
1. ✅ Tester tous les endpoints via Swagger UI
2. ✅ Créer un compte de test et des projets
3. ✅ Configurer OAuth2 (au moins Google OU GitHub)
4. ✅ Générer les types TypeScript pour le frontend

### Moyen terme
1. Activer Redis en production
2. Configurer monitoring (Sentry, Datadog, etc.)
3. Ajouter tests d'intégration
4. Load testing avec Locust

### Long terme
1. Migration complète vers V2
2. Dépréciation progressive de V1
3. WebSocket pour génération temps réel
4. GraphQL endpoint (optionnel)

---

## 📚 Ressources

- **Documentation API:** http://localhost:8000/docs
- **Spec OpenAPI:** `backend/openapi.yaml`
- **Guide complet:** `backend/API_V2_README.md`
- **Rapport delivery:** `backend/BACKEND_SQUAD_DELIVERY.md`
- **Exemples frontend:** `backend/example-frontend-client.ts`

---

## 💡 Tips & Best Practices

### Performance
```python
# Toujours utiliser le cache pour les lectures fréquentes
@cached(ttl=CacheConfig.PROJECT_LIST, key_prefix="projects")
async def get_projects(user_id: str):
    return await db.projects.find({"user_id": user_id}).to_list(1000)
```

### Sécurité
```python
# Toujours valider les inputs
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        # Validation custom
        if not re.search(r'[A-Z]', v):
            raise ValueError('Must contain uppercase')
        return v
```

### Rate Limiting
```python
# Adapter les limites selon le type d'opération
@router.post("/expensive-operation")
@limiter.limit("5/minute")  # Opération coûteuse
async def expensive_operation():
    pass

@router.get("/cheap-operation")
@limiter.limit("100/minute")  # Lecture simple
async def cheap_operation():
    pass
```

---

**Prêt à coder ! 🚀**

Questions ? Consultez `API_V2_README.md` ou ouvrez une issue.
