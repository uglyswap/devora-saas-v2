# Devora SaaS v2 - Deployment Guide

## Dokploy Deployment

### Services Required

1. **MongoDB** (Docker image: `mongo:7`)
   - Environment variables:
     - `MONGO_INITDB_ROOT_USERNAME=devora`
     - `MONGO_INITDB_ROOT_PASSWORD=devora2024secure`
     - `MONGO_INITDB_DATABASE=devora`

2. **Backend** (Docker image: `ghcr.io/uglyswap/devora-saas-v2/backend:latest`)
   - Port: 4521
   - Domain: api.devora.fun
   - Environment variables:
     ```
     MONGO_URL=mongodb://devora:devora2024secure@<mongodb-app-name>:27017/devora?authSource=admin
     DB_NAME=devora
     SECRET_KEY=<your-secret-key-min-32-chars>
     FRONTEND_URL=https://devora.fun
     ALGORITHM=HS256
     ACCESS_TOKEN_EXPIRE_MINUTES=1440
     ```

3. **Frontend** (Docker image: `ghcr.io/uglyswap/devora-saas-v2/frontend:latest`)
   - Port: 4522
   - Domain: devora.fun
   - Build args (already baked in image):
     - `REACT_APP_BACKEND_URL=https://api.devora.fun`

### Important Notes

- Replace `<mongodb-app-name>` with the actual Dokploy app name for MongoDB
- The SECRET_KEY must be at least 32 characters
- Make sure GHCR packages are public before deploying
- If domains conflict, delete old domains from other projects first

### GitHub Actions

Images are automatically built and pushed to GHCR on every push to main branch.
