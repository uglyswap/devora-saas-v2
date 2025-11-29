# 🚀 Guide de Déploiement Devora SaaS V2

## Prérequis

- Node.js 18+
- Python 3.11+
- Compte MongoDB Atlas
- Compte Stripe
- Compte GitHub (pour l'export)
- Compte Vercel (pour le déploiement)

## Variables d'Environnement

Créer un fichier `.env` dans le dossier `backend/`:

```env
# MongoDB
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/devora

# OpenRouter API (LLM)
OPENROUTER_API_KEY=sk-or-v1-xxx

# Stripe
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
STRIPE_PRICE_ID_MONTHLY=price_xxx
STRIPE_PRICE_ID_YEARLY=price_xxx

# GitHub (pour export)
GITHUB_TOKEN=ghp_xxx

# Vercel (pour déploiement)
VERCEL_TOKEN=xxx
VERCEL_TEAM_ID=team_xxx

# Frontend URL
FRONTEND_URL=https://devora.app
```

Créer un fichier `.env` dans le dossier `frontend/`:

```env
REACT_APP_BACKEND_URL=https://api.devora.app
REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_live_xxx
```

## Déploiement Backend (Railway)

### 1. Créer un projet Railway

```bash
# Installer Railway CLI
npm install -g @railway/cli

# Login
railway login

# Créer projet
railway init
```

### 2. Configurer le service

```bash
cd backend

# Lier au projet Railway
railway link

# Ajouter les variables d'environnement
railway variables set MONGODB_URI="mongodb+srv://..."
railway variables set OPENROUTER_API_KEY="sk-or-v1-..."
railway variables set STRIPE_SECRET_KEY="sk_live_..."
# ... autres variables

# Déployer
railway up
```

### 3. Configuration Procfile

Créer `backend/Procfile`:
```
web: uvicorn server:app --host 0.0.0.0 --port $PORT
```

### 4. Configuration railway.json

```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn server:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/api/health"
  }
}
```

## Déploiement Frontend (Vercel)

### 1. Connecter le repository GitHub

1. Aller sur [vercel.com](https://vercel.com)
2. "Add New Project"
3. Importer depuis GitHub
4. Sélectionner le dossier `frontend/` comme Root Directory

### 2. Configuration Build

```
Build Command: npm run build
Output Directory: build
Install Command: npm install
```

### 3. Variables d'environnement Vercel

Dans les settings du projet Vercel:

```
REACT_APP_BACKEND_URL = https://api.devora.app
REACT_APP_STRIPE_PUBLISHABLE_KEY = pk_live_xxx
```

### 4. Domaine personnalisé

1. Settings → Domains
2. Ajouter `devora.app`
3. Configurer DNS chez votre registrar

## Configuration Stripe

### 1. Créer les produits

Dans le Dashboard Stripe:

1. Products → Add Product
2. Créer "Devora Pro Monthly" - €29/mois
3. Créer "Devora Pro Yearly" - €290/an
4. Noter les `price_id` pour chaque produit

### 2. Configurer les Webhooks

1. Developers → Webhooks
2. Add endpoint: `https://api.devora.app/api/stripe/webhook`
3. Événements à écouter:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`

### 3. Mode Test vs Live

- **Test**: Utiliser `sk_test_xxx` et `pk_test_xxx`
- **Live**: Utiliser `sk_live_xxx` et `pk_live_xxx`

## Configuration MongoDB Atlas

### 1. Créer un cluster

1. [mongodb.com/atlas](https://mongodb.com/atlas)
2. Create Cluster → M10 ou supérieur pour production
3. Région: Europe (Paris) ou US East

### 2. Configuration réseau

1. Network Access → Add IP Address
2. Pour Railway/Vercel: "Allow Access from Anywhere" (0.0.0.0/0)
3. Ou configurer les IPs spécifiques

### 3. Créer un utilisateur

1. Database Access → Add New Database User
2. Authentication: Password
3. Rôle: `readWriteAnyDatabase`

### 4. Obtenir la connection string

```
mongodb+srv://username:password@cluster.mongodb.net/devora?retryWrites=true&w=majority
```

## Vérification Post-Déploiement

### Checklist

- [ ] Backend `/api/health` retourne 200
- [ ] Frontend charge correctement
- [ ] Login/Register fonctionnel
- [ ] Stripe checkout fonctionne
- [ ] Génération de code fonctionne
- [ ] Export GitHub fonctionne
- [ ] Déploiement Vercel fonctionne
- [ ] Webhooks Stripe reçus

### Commandes de test

```bash
# Test API health
curl https://api.devora.app/api/health

# Test génération
curl -X POST https://api.devora.app/api/generate/openrouter \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a hello world page"}'
```

## Monitoring

### Railway
- Logs: `railway logs`
- Métriques: Dashboard Railway

### Vercel
- Analytics: Vercel Dashboard
- Logs: Functions tab

### MongoDB Atlas
- Performance Advisor
- Real-time metrics

## Troubleshooting

### Erreur CORS
```python
# Vérifier les origines autorisées dans server.py
origins = [
    "https://devora.app",
    "https://www.devora.app",
    "http://localhost:3000"  # Dev only
]
```

### Erreur MongoDB Connection
```
# Vérifier:
1. IP whitelistée dans Atlas
2. Username/password corrects
3. Cluster actif
```

### Erreur Stripe Webhook
```
# Vérifier:
1. Endpoint URL correct
2. Webhook secret correct
3. Événements sélectionnés
```
