# 🚀 Devora SaaS V2 - Quick Start Guide

Déployez Devora sur votre serveur en **moins de 5 minutes** !

## Prérequis

- Docker & Docker Compose installés
- Git installé
- Un serveur avec au moins 2GB de RAM

## Déploiement Express

### 1. Cloner le projet

```bash
git clone https://github.com/uglyswap/devora-saas-v2.git
cd devora-saas-v2
```

### 2. Configuration automatique

```bash
# Rendre le script exécutable
chmod +x deploy.sh

# Lancer la configuration (génère les mots de passe sécurisés)
./deploy.sh setup
```

### 3. Ajouter vos clés API

Éditez le fichier `.env` et ajoutez au minimum :

```bash
# Ouvrir .env avec votre éditeur préféré
nano .env
```

**Clé requise pour l'IA :**
```env
OPENROUTER_API_KEY=sk-or-v1-votre-cle-ici
```

> 💡 Obtenez votre clé sur [openrouter.ai/keys](https://openrouter.ai/keys)

### 4. Lancer Devora

```bash
./deploy.sh start
```

### 5. Accéder à l'application

- **Frontend**: http://localhost:4522
- **API**: http://localhost:4521/api/

---

## Commandes Utiles

| Commande | Description |
|----------|-------------|
| `./deploy.sh start` | Démarrer tous les services |
| `./deploy.sh stop` | Arrêter tous les services |
| `./deploy.sh restart` | Redémarrer |
| `./deploy.sh status` | Vérifier l'état |
| `./deploy.sh logs` | Voir les logs |
| `./deploy.sh logs backend` | Logs du backend uniquement |
| `./deploy.sh build` | Reconstruire les containers |
| `./deploy.sh update` | Mettre à jour depuis Git |

---

## Configuration Production

### Avec un domaine personnalisé

1. Modifiez `.env` :

```env
FRONTEND_URL=https://devora.votredomaine.com
BACKEND_URL=https://api.devora.votredomaine.com
```

2. Configurez un reverse proxy (Nginx/Caddy/Traefik)

### Exemple Nginx

```nginx
# Frontend
server {
    listen 80;
    server_name devora.votredomaine.com;
    
    location / {
        proxy_pass http://localhost:4522;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
    }
}

# Backend API
server {
    listen 80;
    server_name api.devora.votredomaine.com;
    
    location / {
        proxy_pass http://localhost:4521;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Configuration Optionnelle

### Stripe (Paiements)

```env
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### GitHub (Export)

```env
GITHUB_TOKEN=ghp_...
```

### Vercel (Déploiement)

```env
VERCEL_TOKEN=...
```

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                     DEVORA                          │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────┐     ┌─────────────┐               │
│  │  Frontend   │────▶│   Backend   │               │
│  │  (React)    │     │  (FastAPI)  │               │
│  │  :4522      │     │   :4521     │               │
│  └─────────────┘     └──────┬──────┘               │
│                             │                       │
│              ┌──────────────┼──────────────┐       │
│              ▼              ▼              ▼       │
│       ┌──────────┐   ┌──────────┐   ┌──────────┐   │
│       │ MongoDB  │   │ Postgres │   │ OpenRouter│  │
│       │ (Data)   │   │ (Memory) │   │   (AI)    │  │
│       └──────────┘   └──────────┘   └──────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Services Docker

| Service | Port | Description |
|---------|------|-------------|
| frontend | 4522 | React SPA |
| backend | 4521 | FastAPI REST API |
| mongodb | 27017 (interne) | Base de données principale |
| postgres | 5432 (interne) | Memori - Mémoire persistante IA |

---

## Fonctionnalités IA

### Mode Agentique (HTML/CSS/JS)
- Génération de sites web simples
- Aperçu instantané dans l'éditeur
- Idéal pour les landing pages

### Mode Full-Stack (Next.js)
- Projets Next.js 14+ complets
- TypeScript + Tailwind + shadcn/ui
- Intégration Supabase/Stripe
- Preview via Vercel

### Mémoire Persistante (Memori)
- Apprentissage des préférences utilisateur
- Contexte cross-session
- Amélioration continue

---

## Dépannage

### Les containers ne démarrent pas

```bash
# Voir les logs détaillés
./deploy.sh logs

# Reconstruire depuis zéro
./deploy.sh build
./deploy.sh start
```

### Erreur de base de données

```bash
# Vérifier que PostgreSQL est prêt
docker compose exec postgres pg_isready

# Voir les logs PostgreSQL
./deploy.sh logs postgres
```

### Réinitialiser complètement

```bash
# ⚠️ ATTENTION: Supprime toutes les données!
./deploy.sh clean
./deploy.sh setup
./deploy.sh start
```

---

## Support

- 📖 [Documentation complète](./README.md)
- 🐛 [Signaler un bug](https://github.com/uglyswap/devora-saas-v2/issues)
- 💬 Questions: Ouvrez une issue sur GitHub

---

**Bon développement avec Devora!** 🎉
