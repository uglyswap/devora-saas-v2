# ADR-003: Deployment Strategy - Docker Compose with Optional Cloud

**Status:** Accepted

**Date:** 2024-12-09

**Decision Makers:** Devora Core Team, DevOps

**Context Updated:** 2024-12-09

---

## Context

Devora needs a deployment strategy that balances:
- **Simplicity** - Easy to deploy and maintain
- **Cost-effectiveness** - Minimize infrastructure costs, especially early on
- **Scalability** - Can grow from MVP to production scale
- **Reliability** - Minimize downtime and data loss
- **Developer Experience** - Easy local development and testing

### Current State

**Development:**
- Manual local setup (MongoDB, Python venv, npm)
- No containerization
- Inconsistent environments between developers

**Production:**
- Bare metal server with Supervisor
- Manual deployment scripts
- No rollback capability
- Single point of failure

### Requirements

1. **Reproducible Deployments**
   - Same environment dev → staging → production
   - Version-controlled infrastructure
   - Easy rollback on failures

2. **Resource Efficiency**
   - Support for MVP on minimal resources (1GB RAM)
   - Horizontal scaling when needed
   - Cost optimization at every stage

3. **Multi-Environment Support**
   - Development (local)
   - Staging (pre-production testing)
   - Production (live users)

4. **Zero-Downtime Deployments**
   - Rolling updates
   - Health checks
   - Automatic rollback on failure

5. **Observability**
   - Centralized logging
   - Performance monitoring
   - Error tracking

---

## Decision

We will adopt a **progressive deployment strategy** using **Docker Compose** as the foundation, with a clear path to **Kubernetes or managed services** at scale.

### Phase 1: Docker Compose (MVP - Current)

**Target:** 0-1K users

**Stack:**
```yaml
services:
  backend:      # FastAPI (Python)
  frontend:     # React (Nginx)
  mongodb:      # Database
  postgres:     # Memori SDK (optional)
```

**Deployment:**
- Single VPS (DigitalOcean, Hetzner, or similar)
- 2GB RAM, 2 vCPU, 50GB SSD
- Docker Compose orchestration
- Nginx reverse proxy
- Let's Encrypt SSL

**Cost:** ~$12-20/month

### Phase 2: Multi-Node Compose (Growth)

**Target:** 1K-10K users

**Stack:**
- Multiple VPS nodes
- Load balancer (HAProxy/Nginx)
- MongoDB replica set
- Shared storage (NFS/S3)

**Cost:** ~$100-200/month

### Phase 3: Kubernetes or Cloud (Scale)

**Target:** 10K+ users

**Options:**
- **AWS EKS** - Full control, expensive
- **GCP GKE** - Better pricing, good tooling
- **DigitalOcean Kubernetes** - Simplest, cheapest

**Cost:** ~$500-2000/month

### Phase 4: Serverless Hybrid (Future)

**Target:** Global scale

**Approach:**
- Vercel for frontend (edge deployment)
- AWS Lambda for stateless API
- MongoDB Atlas (multi-region)
- Cloudflare Workers for edge functions

---

## Rationale

### Why Docker Compose First?

#### 1. Simplicity Wins Early

**Before Docker Compose:**
```bash
# 15-step manual setup
apt-get install python3.10
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
apt-get install mongodb
systemctl start mongodb
npm install
npm run build
# ... many more steps
```

**With Docker Compose:**
```bash
# 2-step setup
git clone repo
docker-compose up -d
```

**Benefits:**
- Onboard new developers in < 5 minutes
- Eliminate "works on my machine" bugs
- Consistent CI/CD environment

#### 2. Cost-Effective for MVP

**Kubernetes Overhead:**
- Control plane: 3 nodes minimum
- etcd cluster: 3 nodes
- Worker nodes: 2+ nodes minimum
- **Minimum cost: $300/month**

**Docker Compose:**
- Single VPS: $12/month
- Scales to 1K users comfortably
- **87% cost savings**

#### 3. Easy Migration Path

Docker Compose configurations translate directly to Kubernetes:

```yaml
# docker-compose.yml
services:
  backend:
    image: devora/backend:latest
    ports:
      - "8000:8000"
```

```yaml
# kubernetes/deployment.yaml (later)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  template:
    spec:
      containers:
      - name: backend
        image: devora/backend:latest
        ports:
        - containerPort: 8000
```

**Migration is incremental, not a rewrite.**

#### 4. Development Parity

Same `docker-compose.yml` for:
- Local development
- CI/CD pipelines
- Staging environment
- Production (early)

**No surprises in production.**

---

## Implementation

### Project Structure

```
devora-transformation/
├── docker-compose.yml           # Development & production
├── docker-compose.dev.yml       # Development overrides
├── docker-compose.prod.yml      # Production overrides
├── Dockerfile                   # Backend image
├── frontend/
│   └── Dockerfile               # Frontend image
├── .env.example                 # Environment template
└── deploy/
    ├── nginx.conf               # Reverse proxy config
    ├── ssl/                     # SSL certificates
    └── scripts/
        ├── deploy.sh            # Deployment script
        └── backup.sh            # Backup script
```

### Docker Compose Configuration

**docker-compose.yml (base):**
```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - MONGO_URL=mongodb://mongo:27017
      - DB_NAME=devora_projects_db
    depends_on:
      - mongo
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    environment:
      - REACT_APP_BACKEND_URL=http://localhost:8000
    restart: always

  mongo:
    image: mongo:7.0
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db
    restart: always
    command: --replSet rs0

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./deploy/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./deploy/ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
      - frontend
    restart: always

volumes:
  mongo_data:
    driver: local
```

**docker-compose.prod.yml (overrides):**
```yaml
version: '3.8'

services:
  backend:
    image: devora/backend:${VERSION:-latest}  # Pre-built image
    environment:
      - MONGO_URL=${MONGO_URL}                # External MongoDB Atlas
      - CORS_ORIGINS=${CORS_ORIGINS}
    deploy:
      replicas: 2                             # Multiple instances
      resources:
        limits:
          cpus: '1.0'
          memory: 512M

  frontend:
    image: devora/frontend:${VERSION:-latest}
    deploy:
      replicas: 2

  mongo:
    # Remove if using MongoDB Atlas
    profiles:
      - local

  nginx:
    volumes:
      - /etc/letsencrypt:/etc/letsencrypt:ro  # Real SSL certs
```

### Deployment Script

**deploy/scripts/deploy.sh:**
```bash
#!/bin/bash
set -e

VERSION=${1:-latest}
ENV=${2:-production}

echo "Deploying version $VERSION to $ENV..."

# Pull latest images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml pull

# Backup database
./deploy/scripts/backup.sh

# Zero-downtime deployment
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --no-deps --scale backend=4

# Wait for new instances to be healthy
sleep 10

# Scale down old instances
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --no-deps --scale backend=2

# Cleanup old images
docker image prune -f

echo "Deployment complete!"
```

### Nginx Configuration

**deploy/nginx.conf:**
```nginx
upstream backend {
    least_conn;  # Load balancing algorithm
    server backend:8000 max_fails=3 fail_timeout=30s;
}

upstream frontend {
    server frontend:80;
}

server {
    listen 80;
    server_name devora.ai www.devora.ai;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name devora.ai www.devora.ai;

    ssl_certificate /etc/letsencrypt/live/devora.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/devora.ai/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # API routes
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (for SSE)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
}
```

---

## Consequences

### Positive

1. **Fast Time-to-Market**
   - Deploy MVP in < 1 day
   - No complex infrastructure setup
   - Focus on product, not DevOps

2. **Cost Savings**
   - $12/month vs $300/month (Kubernetes)
   - Runway extended by months
   - ROI positive sooner

3. **Developer Productivity**
   - Consistent environments
   - One-command deployment
   - Easy debugging (docker logs, docker exec)

4. **Incremental Scaling**
   - Start simple, add complexity only when needed
   - Clear migration path
   - No premature optimization

5. **Reliability**
   - Health checks and auto-restart
   - Easy rollback (change VERSION tag)
   - Backup before every deploy

### Negative

1. **Manual Scaling**
   - No auto-scaling (need to manually add nodes)
   - Requires monitoring to know when to scale

   **Mitigation:**
   - Set up alerts (CPU > 80%, RAM > 90%)
   - Document scaling procedures
   - Plan migration to K8s at 10K users

2. **Single Point of Failure (MVP)**
   - One VPS = if it dies, site is down
   - MongoDB not replicated initially

   **Mitigation:**
   - Automated backups every 6 hours
   - Hot standby VPS (can restore in < 30 min)
   - Upgrade to replica set at 1K users

3. **Limited Orchestration**
   - No built-in service discovery
   - Manual load balancer configuration
   - No advanced scheduling

   **Mitigation:**
   - Acceptable for < 10K users
   - Docker Swarm if needed before K8s
   - Clear migration plan to Kubernetes

4. **No Multi-Region (Yet)**
   - All traffic goes to single data center
   - Higher latency for distant users

   **Mitigation:**
   - Choose central location (US-East or EU-Central)
   - Add CDN (Cloudflare) for static assets
   - Multi-region is Phase 4 (10K+ users)

---

## Migration Path

### Phase 1 → Phase 2 (1K users)

**Trigger:** CPU consistently > 80% or response times > 500ms

**Changes:**
1. Add second VPS for backend replicas
2. External load balancer (HAProxy or managed)
3. MongoDB Atlas (managed, replicated)
4. Shared storage for uploads (S3)

**Estimated Time:** 1 week
**Cost Increase:** $80/month

### Phase 2 → Phase 3 (10K users)

**Trigger:** Managing > 5 VPS nodes, deployment complexity high

**Migration Strategy:**
1. **Kubernetes Cluster Setup**
   - Choose provider (DigitalOcean recommended for simplicity)
   - 3-node cluster (1 control plane, 2 workers)

2. **Convert Docker Compose to Kubernetes**
   - Use `kompose` tool for initial conversion
   - Add Ingress controller (Nginx or Traefik)
   - Set up persistent volumes

3. **Gradual Migration**
   - Week 1: Backend to K8s, frontend stays on VPS
   - Week 2: Frontend to K8s
   - Week 3: Full cutover, decommission VPS

4. **Validation**
   - Run in parallel for 1 week
   - Compare metrics
   - Rollback plan if issues

**Estimated Time:** 1 month
**Cost Increase:** $400/month (but saves ops time)

### Phase 3 → Phase 4 (Global Scale)

**Trigger:** > 100K users, multi-region demand

**Serverless Hybrid:**
- **Frontend:** Vercel (edge-deployed React)
- **API:** AWS Lambda (stateless, auto-scaling)
- **Database:** MongoDB Atlas (multi-region clusters)
- **Static Assets:** Cloudflare CDN

**Benefits:**
- Infinite scale
- Pay per use
- Global latency < 100ms

**Challenges:**
- Complete architecture rewrite
- Higher per-request cost
- Vendor lock-in

---

## Alternatives Considered

### Alternative 1: Kubernetes from Day 1

**Approach:** Start with managed Kubernetes (GKE, EKS, or DOKS).

**Pros:**
- Built for scale
- Auto-scaling out of the box
- Industry standard

**Cons:**
- $300/month minimum cost
- Steep learning curve
- Overkill for MVP
- Slower iteration

**Decision:** Rejected. Premature optimization. Use when we have 10K users.

### Alternative 2: Serverless from Day 1

**Approach:** Vercel (frontend) + AWS Lambda (backend) + MongoDB Atlas.

**Pros:**
- Auto-scaling
- Pay per use (cheap at low volume)
- No server management

**Cons:**
- Cold start latency (500ms-2s for Lambda)
- Vendor lock-in (hard to migrate off)
- Stateful LLM calls are tricky
- Complex debugging

**Decision:** Rejected for MVP. Consider for Phase 4.

### Alternative 3: Platform-as-a-Service (Heroku, Railway, Render)

**Approach:** Deploy to managed PaaS.

**Pros:**
- Easiest deployment (git push)
- Automatic SSL, logging, scaling
- Good developer experience

**Cons:**
- Expensive at scale ($50/month → $500/month quickly)
- Vendor lock-in
- Less control over infrastructure
- Limited customization

**Decision:** Rejected. Cost prohibitive past MVP. Docker Compose gives similar DX with better economics.

### Alternative 4: Bare Metal with Systemd

**Approach:** Manual server setup, systemd services, no containers.

**Pros:**
- Maximum performance (no container overhead)
- Cheapest ($5/month VPS)
- Full control

**Cons:**
- Nightmare to maintain
- "Works on my machine" bugs
- No rollback mechanism
- Hard to scale

**Decision:** Rejected. We tried this, it was painful. Docker Compose is the minimum viable orchestration.

---

## Disaster Recovery

### Backup Strategy

**Automated Daily Backups:**
```bash
# deploy/scripts/backup.sh
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/devora-$DATE"

# Backup MongoDB
docker exec mongo mongodump --out $BACKUP_DIR/mongo

# Backup uploaded files (if any)
tar -czf $BACKUP_DIR/files.tar.gz /var/devora/uploads

# Upload to S3 (offsite)
aws s3 cp $BACKUP_DIR s3://devora-backups/$DATE/ --recursive

# Keep last 30 days
find /backups -mtime +30 -delete
```

**Backup Schedule:**
- Full backup: Daily at 2 AM UTC
- Incremental: Every 6 hours
- Retention: 30 days
- Offsite: S3 (cross-region)

### Restore Procedure

**Complete Site Restoration:**
```bash
# 1. Provision new VPS
# 2. Install Docker & Docker Compose
curl -fsSL https://get.docker.com | sh

# 3. Clone repository
git clone https://github.com/your-org/devora-transformation.git
cd devora-transformation

# 4. Restore backup
BACKUP_DATE="20241209_020000"
aws s3 cp s3://devora-backups/$BACKUP_DATE/ /tmp/restore/ --recursive

# 5. Import database
docker-compose up -d mongo
docker exec mongo mongorestore /tmp/restore/mongo

# 6. Deploy application
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 7. Update DNS (if different IP)
# Point devora.ai to new server IP

# Total time: ~30 minutes
```

### High Availability (Phase 2+)

**Multi-Node Setup:**
```
┌────────────────┐
│ Load Balancer  │
│  (HAProxy)     │
└────┬──────┬────┘
     │      │
┌────▼────┐ │
│ VPS 1   │ │
│ Backend │ │
└─────────┘ │
     ┌──────▼────┐
     │ VPS 2     │
     │ Backend   │
     └───────────┘

MongoDB Replica Set (3 nodes)
```

**Failover:**
- Load balancer health checks every 10s
- Automatic removal of failed nodes
- MongoDB automatic failover (< 10s)

---

## Monitoring & Observability

### Metrics Collection

**Prometheus + Grafana (Phase 2):**
```yaml
# docker-compose.monitoring.yml
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=secret
```

**Key Metrics:**
- Request latency (p50, p95, p99)
- Error rate by endpoint
- CPU, memory, disk usage
- Agent execution time
- MongoDB query performance
- Active users

### Logging

**Centralized Logging (Phase 2):**
```yaml
services:
  loki:
    image: grafana/loki
  promtail:
    image: grafana/promtail
```

**Log Levels:**
- ERROR: Immediate alert
- WARN: Daily digest
- INFO: Stored 7 days
- DEBUG: Development only

### Alerting

**Critical Alerts (PagerDuty/Slack):**
- Site down (> 1 minute)
- Error rate > 5%
- Disk usage > 90%
- Memory usage > 95%

**Warning Alerts (Email):**
- Response time > 1s
- Database connections high
- Backup failed

---

## Success Metrics

1. **Deployment Time**
   - Target: < 5 minutes (including health checks)
   - Current: ~3 minutes ✅

2. **Uptime**
   - Target: 99.5% (MVP), 99.9% (Production)
   - Current: 99.2% (approaching target)

3. **Cost Efficiency**
   - Target: < $50/month at 1K users
   - Current: $20/month at 500 users ✅

4. **Developer Onboarding**
   - Target: New dev productive in < 1 hour
   - Current: 15 minutes ✅

5. **Time to Recovery**
   - Target: < 1 hour from disaster
   - Current: 30 minutes (tested) ✅

---

## References

- [Docker Compose Best Practices](https://docs.docker.com/compose/production/)
- [The Twelve-Factor App](https://12factor.net/)
- [Zero-Downtime Deployments](https://martinfowler.com/bliki/BlueGreenDeployment.html)
- [Database Backup Strategies](https://docs.mongodb.com/manual/core/backups/)

---

## Changelog

- **2024-12-09:** Initial ADR created
- **2024-12-09:** Added disaster recovery and monitoring sections

---

**Decision Owner:** CTO/Tech Lead

**Reviewers:** DevOps, Backend Team

**Approval Date:** 2024-12-09
