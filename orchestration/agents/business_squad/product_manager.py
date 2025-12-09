"""
Product Manager Agent - Business Squad

Cet agent est responsable de:
- Générer des PRD (Product Requirement Documents)
- Créer des user stories détaillées
- Définir et maintenir la roadmap produit
- Prioriser les features selon le framework RICE
"""

import sys
import os
from typing import Dict, Any, List
from datetime import datetime

# Ajouter le chemin du backend pour importer BaseAgent
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../backend'))

from agents.base_agent import BaseAgent


class ProductManagerAgent(BaseAgent):
    """
    Agent Product Manager pour la définition et la gestion du produit.

    Attributes:
        name (str): Nom de l'agent
        api_key (str): Clé API pour le LLM
        model (str): Modèle LLM à utiliser
    """

    def __init__(self, api_key: str, model: str = "openai/gpt-4o"):
        super().__init__(name="ProductManager", api_key=api_key, model=model)
        self.system_prompt = """Tu es un Product Manager expert avec 10+ ans d'expérience.

Tes responsabilités:
- Créer des PRD (Product Requirement Documents) détaillés et actionnables
- Rédiger des user stories au format: "En tant que [persona], je veux [action] afin de [bénéfice]"
- Définir des roadmaps produit avec priorisation RICE (Reach, Impact, Confidence, Effort)
- Analyser les besoins utilisateurs et les transformer en specs techniques
- Définir les critères d'acceptation et les KPIs de succès

Principes:
- User-centric: toujours partir du besoin utilisateur
- Data-driven: baser les décisions sur des métriques
- Itératif: privilégier le MVP et l'amélioration continue
- Collaboratif: travailler en équipe avec Tech, Design, Business

Format de sortie:
- Structuré en markdown
- Sections claires et numérotées
- Critères mesurables
- Timeline réaliste"""

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exécute une tâche de product management.

        Args:
            task (Dict[str, Any]): Tâche à exécuter avec les clés:
                - task_type: "prd" | "user_story" | "roadmap" | "prioritization"
                - context: Contexte et requirements
                - target_audience: Audience cible (optionnel)
                - constraints: Contraintes techniques/business (optionnel)

        Returns:
            Dict[str, Any]: Résultat avec les clés:
                - status: "success" | "error"
                - output: Contenu généré
                - metadata: Informations complémentaires
        """
        task_type = task.get("task_type", "prd")
        context = task.get("context", "")
        target_audience = task.get("target_audience", "utilisateurs généraux")
        constraints = task.get("constraints", "")

        # Construire le prompt selon le type de tâche
        if task_type == "prd":
            user_prompt = self._build_prd_prompt(context, target_audience, constraints)
        elif task_type == "user_story":
            user_prompt = self._build_user_story_prompt(context, target_audience)
        elif task_type == "roadmap":
            user_prompt = self._build_roadmap_prompt(context, constraints)
        elif task_type == "prioritization":
            user_prompt = self._build_prioritization_prompt(context)
        else:
            return {
                "status": "error",
                "output": f"Type de tâche inconnu: {task_type}",
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

        return {
            "status": "success",
            "output": response,
            "metadata": {
                "task_type": task_type,
                "timestamp": datetime.utcnow().isoformat(),
                "target_audience": target_audience
            }
        }

    def _build_prd_prompt(self, context: str, target_audience: str, constraints: str) -> str:
        """Construit le prompt pour générer un PRD."""
        return f"""Génère un Product Requirement Document (PRD) complet pour:

CONTEXTE:
{context}

AUDIENCE CIBLE:
{target_audience}

CONTRAINTES:
{constraints if constraints else "Aucune contrainte spécifique"}

Le PRD doit inclure:
1. Executive Summary
2. Problème à résoudre
3. Objectifs et KPIs de succès
4. User personas et use cases
5. Requirements fonctionnels (must-have, nice-to-have)
6. Requirements non-fonctionnels (performance, sécurité, scalabilité)
7. User flows principaux
8. Critères d'acceptation
9. Dépendances et risques
10. Timeline et phases de déploiement

Format: Markdown structuré avec numérotation claire."""

    def _build_user_story_prompt(self, context: str, target_audience: str) -> str:
        """Construit le prompt pour générer des user stories."""
        return f"""Génère des user stories détaillées pour:

CONTEXTE:
{context}

AUDIENCE CIBLE:
{target_audience}

Pour chaque user story, utilise le format:
**En tant que** [persona]
**Je veux** [action/feature]
**Afin de** [bénéfice/valeur]

**Critères d'acceptation:**
- [ ] Critère 1
- [ ] Critère 2
- [ ] Critère 3

**Estimation:** [Points de story - XS/S/M/L/XL]
**Priorité:** [P0/P1/P2/P3]
**Dépendances:** [User stories liées]

Génère au minimum 5 user stories couvrant les flows principaux."""

    def _build_roadmap_prompt(self, context: str, constraints: str) -> str:
        """Construit le prompt pour générer une roadmap."""
        return f"""Génère une roadmap produit pour:

CONTEXTE:
{context}

CONTRAINTES:
{constraints if constraints else "Aucune contrainte spécifique"}

Structure la roadmap en phases:
- **Phase 1 - MVP** (Mois 1-2): Features essentielles
- **Phase 2 - Growth** (Mois 3-6): Features de croissance
- **Phase 3 - Scale** (Mois 7-12): Optimisation et scale

Pour chaque phase, indique:
1. Objectifs clés
2. Features principales
3. KPIs de succès
4. Ressources nécessaires
5. Risques identifiés

Utilise une vision 12 mois avec checkpoints trimestriels."""

    def _build_prioritization_prompt(self, context: str) -> str:
        """Construit le prompt pour prioriser des features."""
        return f"""Analyse et priorise les features suivantes selon le framework RICE:

FEATURES À PRIORISER:
{context}

Pour chaque feature, calcule le score RICE:
- **Reach** (0-10): Combien d'utilisateurs impactés par trimestre?
- **Impact** (0.25/0.5/1/2/3): Quel impact sur l'objectif clé?
- **Confidence** (0-100%): Niveau de certitude des estimations
- **Effort** (1-10): Combien de personnes-mois requis?

**Score RICE = (Reach × Impact × Confidence) / Effort**

Présente les résultats sous forme de tableau:
| Feature | Reach | Impact | Confidence | Effort | Score RICE | Priorité |
|---------|-------|--------|------------|--------|------------|----------|
| ...     | ...   | ...    | ...        | ...    | ...        | P0/P1/P2 |

Recommande ensuite l'ordre d'implémentation optimal."""

    async def generate_prd(self, feature_description: str, target_audience: str = "utilisateurs généraux") -> str:
        """
        Méthode helper pour générer rapidement un PRD.

        Args:
            feature_description (str): Description de la feature
            target_audience (str): Audience cible

        Returns:
            str: PRD généré en markdown
        """
        result = await self.execute({
            "task_type": "prd",
            "context": feature_description,
            "target_audience": target_audience
        })
        return result["output"]

    async def create_user_stories(self, feature_description: str, persona: str = "utilisateur") -> str:
        """
        Méthode helper pour générer des user stories.

        Args:
            feature_description (str): Description de la feature
            persona (str): Persona principal

        Returns:
            str: User stories en markdown
        """
        result = await self.execute({
            "task_type": "user_story",
            "context": feature_description,
            "target_audience": persona
        })
        return result["output"]

    async def build_roadmap(self, product_vision: str, timeline: str = "12 mois") -> str:
        """
        Méthode helper pour créer une roadmap.

        Args:
            product_vision (str): Vision produit
            timeline (str): Horizon temporel

        Returns:
            str: Roadmap en markdown
        """
        result = await self.execute({
            "task_type": "roadmap",
            "context": product_vision,
            "constraints": f"Timeline: {timeline}"
        })
        return result["output"]

    async def prioritize_features(self, features: List[str]) -> str:
        """
        Méthode helper pour prioriser des features avec RICE.

        Args:
            features (List[str]): Liste des features à prioriser

        Returns:
            str: Priorisation avec scores RICE
        """
        features_context = "\n".join([f"- {f}" for f in features])
        result = await self.execute({
            "task_type": "prioritization",
            "context": features_context
        })
        return result["output"]
