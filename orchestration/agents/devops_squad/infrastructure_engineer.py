"""
Infrastructure Engineer Agent - DevOps Squad

Cet agent est responsable de:
- Configurer les déploiements sur Vercel/Cloudflare
- Générer les Dockerfiles et docker-compose.yml
- Créer les pipelines CI/CD (GitHub Actions, GitLab CI)
- Gérer les environnements (dev, staging, prod)
- Provisionner l'infrastructure as code (Terraform, Pulumi)
"""
from typing import Dict, Any, List
from datetime import datetime


from ..core.base_agent import BaseAgent


class InfrastructureEngineerAgent(BaseAgent):
    """
    Agent Infrastructure Engineer pour la configuration et le déploiement.

    Attributes:
        name (str): Nom de l'agent
        api_key (str): Clé API pour le LLM
        model (str): Modèle LLM à utiliser
    """

    def __init__(self, api_key: str, model: str = "openai/gpt-4o"):
        super().__init__(name="InfrastructureEngineer", api_key=api_key, model=model)

    def _get_default_system_prompt(self) -> str:
        """Retourne le system prompt par défaut pour l'Infrastructure Engineer."""
        return """Tu es un Infrastructure Engineer expert avec 10+ ans d'expérience en DevOps et Cloud.

Tes responsabilités:
- Concevoir et déployer des architectures cloud scalables (AWS, GCP, Azure, Vercel, Cloudflare)
- Créer des Dockerfiles optimisés et docker-compose.yml pour orchestration locale
- Implémenter des pipelines CI/CD robustes (GitHub Actions, GitLab CI, CircleCI)
- Gérer les environnements multiples (dev, staging, prod) avec isolation
- Écrire de l'Infrastructure as Code (Terraform, Pulumi, CloudFormation)
- Optimiser les coûts cloud et la performance

Principes:
- Infrastructure as Code: tout doit être versionné et reproductible
- Immutabilité: conteneurs immuables, pas de configuration manuelle
- Sécurité first: secrets gérés via vaults, least privilege
- Observabilité: monitoring et logging dès le début
- Cost-optimization: dimensionnement approprié, auto-scaling

Stacks supportées:
- **Frontend**: Next.js sur Vercel, React sur Cloudflare Pages
- **Backend**: Node.js, Python FastAPI, Go
- **Databases**: PostgreSQL (Supabase, RDS), Redis, MongoDB
- **CI/CD**: GitHub Actions (priorité), GitLab CI, CircleCI
- **Containers**: Docker, Docker Compose, Kubernetes (pour scale)
- **IaC**: Terraform (priorité), Pulumi, CDK

Format de sortie:
- Code infrastructure prêt à l'emploi
- Configuration commentée et documentée
- Best practices intégrées
- Scripts d'automatisation"""

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exécute une tâche d'infrastructure engineering.

        Args:
            task (Dict[str, Any]): Tâche à exécuter avec les clés:
                - task_type: "dockerfile" | "docker_compose" | "ci_cd" | "terraform" | "deployment"
                - stack: Stack technologique (ex: "nextjs", "fastapi", "nodejs")
                - platform: Plateforme cible (ex: "vercel", "cloudflare", "aws")
                - requirements: Requirements spécifiques (optionnel)
                - environment: Environnement cible (optionnel)

        Returns:
            Dict[str, Any]: Résultat avec les clés:
                - status: "success" | "error"
                - output: Configuration générée
                - files: Liste des fichiers à créer
                - metadata: Informations complémentaires
        """
        task_type = task.get("task_type", "deployment")
        stack = task.get("stack", "nodejs")
        platform = task.get("platform", "vercel")
        requirements = task.get("requirements", "")
        environment = task.get("environment", "production")

        # Construire le prompt selon le type de tâche
        if task_type == "dockerfile":
            user_prompt = self._build_dockerfile_prompt(stack, requirements)
        elif task_type == "docker_compose":
            user_prompt = self._build_docker_compose_prompt(stack, requirements)
        elif task_type == "ci_cd":
            user_prompt = self._build_ci_cd_prompt(stack, platform, requirements)
        elif task_type == "terraform":
            user_prompt = self._build_terraform_prompt(stack, platform, requirements)
        elif task_type == "deployment":
            user_prompt = self._build_deployment_prompt(stack, platform, environment, requirements)
        else:
            return {
                "status": "error",
                "output": f"Type de tâche inconnu: {task_type}",
                "files": [],
                "metadata": {}
            }

        # Appeler le LLM
        response = await self.call_llm(
            messages=[{"role": "user", "content": user_prompt}],
            system_prompt=self.system_prompt
        )

        # Ajouter à la mémoire
        self.add_to_memory("user", user_prompt)
        self.add_to_memory("assistant", response)

        # Extraire les fichiers générés
        files = self._extract_files_from_response(response, task_type)

        return {
            "status": "success",
            "output": response,
            "files": files,
            "metadata": {
                "task_type": task_type,
                "stack": stack,
                "platform": platform,
                "environment": environment,
                "timestamp": datetime.utcnow().isoformat()
            }
        }

    def _build_dockerfile_prompt(self, stack: str, requirements: str) -> str:
        """Construit le prompt pour générer un Dockerfile."""
        return f"""Génère un Dockerfile optimisé pour:

STACK: {stack}

REQUIREMENTS:
{requirements if requirements else "Standard production setup"}

Le Dockerfile doit:
1. Utiliser multi-stage build pour optimiser la taille
2. Implémenter layer caching efficace
3. Tourner en non-root user pour la sécurité
4. Inclure les health checks
5. Optimiser pour la production (minification, tree-shaking)
6. Gérer correctement les node_modules / dépendances
7. Exposer les ports nécessaires
8. Définir les variables d'environnement

Bonnes pratiques:
- Base images officielles et versionnées (alpine quand possible)
- .dockerignore inclus
- Build args pour la flexibilité
- Labels pour la traçabilité

Fournis aussi:
- Le Dockerfile commenté
- Le fichier .dockerignore associé
- Commandes docker build et run pour tester"""

    def _build_docker_compose_prompt(self, stack: str, requirements: str) -> str:
        """Construit le prompt pour générer docker-compose.yml."""
        return f"""Génère un docker-compose.yml complet pour:

STACK: {stack}

REQUIREMENTS:
{requirements if requirements else "Dev environment standard avec DB et cache"}

Le docker-compose.yml doit inclure:
1. Service application principale
2. Base de données (PostgreSQL par défaut)
3. Cache (Redis si applicable)
4. Networks pour isolation
5. Volumes pour persistance
6. Health checks pour tous les services
7. Variables d'environnement via .env
8. Restart policies appropriées

Services typiques:
- app: Application principale
- db: PostgreSQL 15+ avec volumes
- redis: Cache (optionnel)
- nginx: Reverse proxy (si multi-services)

Fournis aussi:
- docker-compose.yml commenté
- Fichier .env.example avec toutes les variables
- Scripts Makefile pour commandes courantes (up, down, logs, etc.)
- Instructions de démarrage rapide"""

    def _build_ci_cd_prompt(self, stack: str, platform: str, requirements: str) -> str:
        """Construit le prompt pour générer pipeline CI/CD."""
        return f"""Génère un pipeline CI/CD GitHub Actions pour:

STACK: {stack}
PLATFORM: {platform}

REQUIREMENTS:
{requirements if requirements else "Pipeline standard: lint, test, build, deploy"}

Le pipeline doit inclure:
1. **CI Pipeline** (Pull Requests):
   - Linting (ESLint, Prettier)
   - Tests unitaires et d'intégration
   - Type checking (TypeScript)
   - Security scanning (npm audit, Snyk)
   - Build verification

2. **CD Pipeline** (main branch):
   - Deploy vers {platform}
   - Migration de base de données (si applicable)
   - Smoke tests post-déploiement
   - Rollback automatique en cas d'échec

3. **Environnements**:
   - dev: Auto-deploy sur chaque commit
   - staging: Auto-deploy sur merge vers main
   - production: Manual approval + deploy

Bonnes pratiques:
- Caching des dépendances (npm, pip, etc.)
- Matrix builds pour tester multiple versions
- Secrets via GitHub Secrets
- Notifications (Slack, Discord)
- Artifact uploads pour debugging

Fournis:
- .github/workflows/ci.yml
- .github/workflows/cd.yml
- Documentation du workflow
- Badge status pour README.md"""

    def _build_terraform_prompt(self, stack: str, platform: str, requirements: str) -> str:
        """Construit le prompt pour générer configuration Terraform."""
        return f"""Génère une configuration Terraform pour:

STACK: {stack}
PLATFORM: {platform}

REQUIREMENTS:
{requirements if requirements else "Infrastructure de base pour production"}

La configuration Terraform doit inclure:
1. **Provider Configuration**:
   - Versioning strict des providers
   - Backend remote (S3 + DynamoDB lock)
   - Workspaces pour multi-env

2. **Core Infrastructure**:
   - Networking (VPC, Subnets, Security Groups)
   - Compute (EC2, ECS, Lambda selon stack)
   - Database (RDS PostgreSQL avec backups)
   - Cache (ElastiCache Redis)
   - Storage (S3 buckets avec encryption)

3. **Security**:
   - IAM roles et policies (least privilege)
   - Security groups restrictifs
   - Encryption at rest et in transit
   - Secrets Manager pour credentials

4. **Observability**:
   - CloudWatch logs et metrics
   - Alarms pour incidents
   - Auto-scaling policies

Structure de fichiers:
```
terraform/
├── main.tf              # Resources principales
├── variables.tf         # Input variables
├── outputs.tf          # Outputs
├── versions.tf         # Providers versions
├── backend.tf          # Remote state
├── environments/
│   ├── dev.tfvars
│   ├── staging.tfvars
│   └── prod.tfvars
└── modules/
    ├── networking/
    ├── compute/
    └── database/
```

Fournis aussi:
- Scripts d'initialisation (terraform init, plan, apply)
- Documentation de l'architecture
- Diagrammes d'infrastructure (Mermaid)"""

    def _build_deployment_prompt(self, stack: str, platform: str, environment: str, requirements: str) -> str:
        """Construit le prompt pour configuration de déploiement."""
        return f"""Configure le déploiement pour:

STACK: {stack}
PLATFORM: {platform}
ENVIRONMENT: {environment}

REQUIREMENTS:
{requirements if requirements else "Configuration standard"}

Configuration nécessaire:

**Pour Vercel:**
- vercel.json avec routes et headers
- Environment variables par environnement
- Build settings optimisés
- Redirects et rewrites
- Edge config si nécessaire

**Pour Cloudflare:**
- wrangler.toml pour Workers/Pages
- KV namespaces et R2 buckets
- Routes et Workers placement
- DNS et SSL configuration
- Analytics et Web Vitals

**Pour AWS/GCP/Azure:**
- Configuration du load balancer
- Auto-scaling policies
- Health checks endpoints
- Blue-green deployment strategy
- Rollback procedures

Inclure:
1. Fichiers de configuration pour {platform}
2. Scripts de déploiement automatisés
3. Validation pre-deploy (smoke tests)
4. Monitoring post-deploy
5. Documentation de rollback

Variables d'environnement requises:
- DATABASE_URL
- REDIS_URL
- API_KEYS
- Feature flags
- Logging configuration

Fournis:
- Configuration complète commentée
- Scripts de déploiement (.sh ou .js)
- Checklist de déploiement
- Procédures de rollback"""

    def _extract_files_from_response(self, response: str, task_type: str) -> List[Dict[str, str]]:
        """
        Extrait les fichiers à créer depuis la réponse du LLM.

        Args:
            response (str): Réponse du LLM
            task_type (str): Type de tâche exécutée

        Returns:
            List[Dict[str, str]]: Liste de fichiers avec path et content
        """
        files = []
        # Parsing basique des blocs de code markdown
        # Format attendu: ```filename\ncode\n```

        import re
        pattern = r'```(\w+)?\n(.*?)\n```'
        matches = re.findall(pattern, response, re.DOTALL)

        for lang, content in matches:
            # Déterminer le nom de fichier selon le contexte
            if task_type == "dockerfile":
                if "dockerignore" in content.lower():
                    filename = ".dockerignore"
                else:
                    filename = "Dockerfile"
            elif task_type == "docker_compose":
                if ".env" in content or "EXAMPLE" in content:
                    filename = ".env.example"
                elif "makefile" in lang.lower():
                    filename = "Makefile"
                else:
                    filename = "docker-compose.yml"
            elif task_type == "ci_cd":
                if "ci.yml" in response[:response.find(content)]:
                    filename = ".github/workflows/ci.yml"
                else:
                    filename = ".github/workflows/cd.yml"
            else:
                filename = f"config.{lang if lang else 'txt'}"

            files.append({
                "path": filename,
                "content": content.strip()
            })

        return files

    async def generate_dockerfile(self, stack: str, requirements: str = "") -> Dict[str, Any]:
        """
        Méthode helper pour générer un Dockerfile.

        Args:
            stack (str): Stack technologique
            requirements (str): Requirements spécifiques

        Returns:
            Dict[str, Any]: Résultat avec Dockerfile et .dockerignore
        """
        return await self.execute({
            "task_type": "dockerfile",
            "stack": stack,
            "requirements": requirements
        })

    async def generate_docker_compose(self, stack: str, requirements: str = "") -> Dict[str, Any]:
        """
        Méthode helper pour générer docker-compose.yml.

        Args:
            stack (str): Stack technologique
            requirements (str): Services additionnels requis

        Returns:
            Dict[str, Any]: Résultat avec docker-compose.yml et .env.example
        """
        return await self.execute({
            "task_type": "docker_compose",
            "stack": stack,
            "requirements": requirements
        })

    async def setup_ci_cd(self, stack: str, platform: str, requirements: str = "") -> Dict[str, Any]:
        """
        Méthode helper pour setup CI/CD pipeline.

        Args:
            stack (str): Stack technologique
            platform (str): Plateforme de déploiement
            requirements (str): Requirements pipeline spécifiques

        Returns:
            Dict[str, Any]: Résultat avec workflows GitHub Actions
        """
        return await self.execute({
            "task_type": "ci_cd",
            "stack": stack,
            "platform": platform,
            "requirements": requirements
        })

    async def provision_infrastructure(self, stack: str, platform: str, requirements: str = "") -> Dict[str, Any]:
        """
        Méthode helper pour provisionner infrastructure avec Terraform.

        Args:
            stack (str): Stack technologique
            platform (str): Cloud provider
            requirements (str): Requirements infrastructure

        Returns:
            Dict[str, Any]: Résultat avec configuration Terraform
        """
        return await self.execute({
            "task_type": "terraform",
            "stack": stack,
            "platform": platform,
            "requirements": requirements
        })

    async def configure_deployment(
        self,
        stack: str,
        platform: str,
        environment: str = "production",
        requirements: str = ""
    ) -> Dict[str, Any]:
        """
        Méthode helper pour configurer le déploiement.

        Args:
            stack (str): Stack technologique
            platform (str): Plateforme cible
            environment (str): Environnement (dev/staging/prod)
            requirements (str): Requirements déploiement

        Returns:
            Dict[str, Any]: Résultat avec configuration déploiement
        """
        return await self.execute({
            "task_type": "deployment",
            "stack": stack,
            "platform": platform,
            "environment": environment,
            "requirements": requirements
        })
