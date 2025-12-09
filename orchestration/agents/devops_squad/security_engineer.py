"""
Security Engineer Agent - DevOps Squad

Cet agent est responsable de:
- Auditer le code pour les vulnérabilités OWASP Top 10
- Configurer la gestion sécurisée des secrets (Vault, AWS Secrets Manager)
- Implémenter le rate limiting et protection DDoS
- Vérifier et configurer les headers de sécurité HTTP
- Scanner les dépendances pour CVEs
"""
from typing import Dict, Any, List
from datetime import datetime

from ..core.base_agent import BaseAgent


class SecurityEngineerAgent(BaseAgent):
    """
    Agent Security Engineer pour l'audit et la sécurisation.

    Attributes:
        name (str): Nom de l'agent
        api_key (str): Clé API pour le LLM
        model (str): Modèle LLM à utiliser
    """

    def __init__(self, api_key: str, model: str = "openai/gpt-4o"):
        super().__init__(name="SecurityEngineer", api_key=api_key, model=model)

    def _get_default_system_prompt(self) -> str:
        """Retourne le system prompt par défaut pour le Security Engineer."""
        return """Tu es un Security Engineer expert avec 10+ ans d'expérience en cybersécurité et AppSec.

Tes responsabilités:
- Auditer le code pour les vulnérabilités OWASP Top 10 et CVEs
- Implémenter des stratégies de défense en profondeur (defense in depth)
- Configurer la gestion sécurisée des secrets et credentials
- Mettre en place rate limiting, WAF, et protection DDoS
- Vérifier les headers de sécurité HTTP et HTTPS
- Scanner les dépendances pour CVEs et updates critiques
- Implémenter l'authentification et autorisation robustes

OWASP Top 10 (2021):
1. Broken Access Control
2. Cryptographic Failures
3. Injection (SQL, XSS, Command)
4. Insecure Design
5. Security Misconfiguration
6. Vulnerable and Outdated Components
7. Identification and Authentication Failures
8. Software and Data Integrity Failures
9. Security Logging and Monitoring Failures
10. Server-Side Request Forgery (SSRF)

Principes de sécurité:
- **Zero Trust**: Ne jamais faire confiance, toujours vérifier
- **Least Privilege**: Permissions minimales nécessaires
- **Defense in Depth**: Multiples couches de sécurité
- **Secure by Default**: Configuration sécurisée par défaut
- **Fail Securely**: En cas d'erreur, refuser l'accès

Stacks de sécurité:
- **Secrets**: HashiCorp Vault, AWS Secrets Manager, Doppler
- **Auth**: OAuth2, JWT, SAML, Supabase Auth
- **Rate Limiting**: Redis-based, Cloudflare, Kong
- **WAF**: Cloudflare WAF, AWS WAF, ModSecurity
- **Scanning**: Snyk, Trivy, OWASP Dependency-Check
- **SAST**: SonarQube, Semgrep, CodeQL

Format de sortie:
- Rapport d'audit détaillé avec sévérité (Critical/High/Medium/Low)
- Code de correction ou configuration sécurisée
- Recommandations priorisées
- Proof of Concept (PoC) pour démonstration si nécessaire"""

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exécute une tâche de security engineering.

        Args:
            task (Dict[str, Any]): Tâche à exécuter avec les clés:
                - task_type: "audit" | "secrets" | "rate_limit" | "headers" | "dependencies" | "auth"
                - code: Code à auditer (optionnel)
                - stack: Stack technologique (optionnel)
                - requirements: Requirements spécifiques (optionnel)

        Returns:
            Dict[str, Any]: Résultat avec les clés:
                - status: "success" | "error"
                - output: Rapport ou configuration
                - vulnerabilities: Liste des vulnérabilités trouvées
                - severity: Niveau de sévérité global
                - metadata: Informations complémentaires
        """
        task_type = task.get("task_type", "audit")
        code = task.get("code", "")
        stack = task.get("stack", "nodejs")
        requirements = task.get("requirements", "")

        # Construire le prompt selon le type de tâche
        if task_type == "audit":
            user_prompt = self._build_audit_prompt(code, stack)
        elif task_type == "secrets":
            user_prompt = self._build_secrets_prompt(stack, requirements)
        elif task_type == "rate_limit":
            user_prompt = self._build_rate_limit_prompt(stack, requirements)
        elif task_type == "headers":
            user_prompt = self._build_headers_prompt(stack)
        elif task_type == "dependencies":
            user_prompt = self._build_dependencies_prompt(code, stack)
        elif task_type == "auth":
            user_prompt = self._build_auth_prompt(stack, requirements)
        else:
            return {
                "status": "error",
                "output": f"Type de tâche inconnu: {task_type}",
                "vulnerabilities": [],
                "severity": "unknown",
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

        # Extraire les vulnérabilités du rapport
        vulnerabilities = self._extract_vulnerabilities(response)
        severity = self._calculate_severity(vulnerabilities)

        return {
            "status": "success",
            "output": response,
            "vulnerabilities": vulnerabilities,
            "severity": severity,
            "metadata": {
                "task_type": task_type,
                "stack": stack,
                "total_issues": len(vulnerabilities),
                "timestamp": datetime.utcnow().isoformat()
            }
        }

    def _build_audit_prompt(self, code: str, stack: str) -> str:
        """Construit le prompt pour audit de sécurité."""
        return f"""Effectue un audit de sécurité complet pour le code suivant:

STACK: {stack}

CODE À AUDITER:
```
{code if code else "Pas de code fourni - effectue un audit générique des bonnes pratiques"}
```

Vérifie toutes les vulnérabilités OWASP Top 10 et fournis un rapport détaillé."""

    def _build_secrets_prompt(self, stack: str, requirements: str) -> str:
        """Construit le prompt pour configuration de secrets management."""
        return f"""Configure une solution de gestion des secrets pour:

STACK: {stack}
REQUIREMENTS: {requirements if requirements else "Standard setup"}

Fournis la configuration complète pour gérer les secrets de manière sécurisée."""

    def _build_rate_limit_prompt(self, stack: str, requirements: str) -> str:
        """Construit le prompt pour rate limiting."""
        return f"""Implémente du rate limiting pour:

STACK: {stack}
REQUIREMENTS: {requirements if requirements else "Standard API protection"}

Fournis le code et la configuration complète."""

    def _build_headers_prompt(self, stack: str) -> str:
        """Construit le prompt pour headers de sécurité."""
        return f"""Configure tous les headers de sécurité HTTP pour:

STACK: {stack}

Inclus: CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy"""

    def _build_dependencies_prompt(self, package_file: str, stack: str) -> str:
        """Construit le prompt pour scan des dépendances."""
        return f"""Scanne les dépendances pour vulnérabilités:

STACK: {stack}

PACKAGE FILE:
```
{package_file if package_file else "Pas de fichier fourni"}
```

Liste toutes les CVEs trouvées et recommande les mises à jour."""

    def _build_auth_prompt(self, stack: str, requirements: str) -> str:
        """Construit le prompt pour implémentation d'authentification."""
        return f"""Implémente un système d'authentification sécurisé:

STACK: {stack}
REQUIREMENTS: {requirements if requirements else "JWT + OAuth2"}

Fournis le code complet avec toutes les best practices."""

    def _extract_vulnerabilities(self, response: str) -> List[Dict[str, Any]]:
        """Extrait les vulnérabilités du rapport d'audit."""
        vulnerabilities = []
        # Parsing basique - à améliorer
        if "sql injection" in response.lower():
            vulnerabilities.append({"name": "SQL Injection", "severity": "critical"})
        if "xss" in response.lower():
            vulnerabilities.append({"name": "Cross-Site Scripting", "severity": "high"})
        return vulnerabilities

    def _calculate_severity(self, vulnerabilities: List[Dict[str, Any]]) -> str:
        """Calcule la sévérité globale."""
        if not vulnerabilities:
            return "none"
        severities = [v.get("severity", "low") for v in vulnerabilities]
        if "critical" in severities:
            return "critical"
        elif "high" in severities:
            return "high"
        elif "medium" in severities:
            return "medium"
        else:
            return "low"
