"""
Copywriter Agent - Business Squad

Cet agent est responsable de:
- Rédiger le copy marketing (landing pages, ads, emails)
- Créer le contenu pour les campagnes
- Optimiser le microcopy UX (CTA, tooltips, messages d'erreur)
- Adapter le tone of voice selon la marque
"""

import sys
import os
from typing import Dict, Any, List
from datetime import datetime

# Ajouter le chemin du backend pour importer BaseAgent
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../backend'))

from agents.base_agent import BaseAgent


class CopywriterAgent(BaseAgent):
    """
    Agent Copywriter pour la création de contenu marketing et UX.

    Attributes:
        name (str): Nom de l'agent
        api_key (str): Clé API pour le LLM
        model (str): Modèle LLM à utiliser
        brand_voice (str): Tone of voice de la marque
    """

    def __init__(self, api_key: str, model: str = "openai/gpt-4o", brand_voice: str = "professionnel et accessible"):
        super().__init__(name="Copywriter", api_key=api_key, model=model)
        self.brand_voice = brand_voice
        self.system_prompt = f"""Tu es un Copywriter expert spécialisé en SaaS et produits digitaux.

Ton expertise:
- Copy marketing persuasif (landing pages, ads, emails)
- Microcopy UX (CTA, tooltips, messages d'erreur, onboarding)
- Storytelling et value proposition
- SEO copywriting
- A/B testing de messages

Tone of voice par défaut: {brand_voice}

Principes de copywriting:
- Clarity > Cleverness (clarté avant créativité)
- Focus sur les bénéfices, pas les features
- AIDA: Attention, Interest, Desire, Action
- Utiliser des power words et des déclencheurs émotionnels
- Court, percutant, actionnable

Format de sortie:
- Plusieurs variations pour A/B testing
- Longueur optimisée pour le canal (SMS, email, landing page)
- CTA clair et orienté action
- SEO-friendly quand applicable"""

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exécute une tâche de copywriting.

        Args:
            task (Dict[str, Any]): Tâche à exécuter avec les clés:
                - task_type: "landing_page" | "email" | "cta" | "microcopy" | "ad" | "seo"
                - context: Contexte du produit/service
                - target_audience: Audience cible
                - goal: Objectif (conversion, awareness, retention)
                - tone: Tone of voice spécifique (optionnel)
                - constraints: Contraintes (longueur, keywords)

        Returns:
            Dict[str, Any]: Résultat avec les clés:
                - status: "success" | "error"
                - output: Contenu généré
                - metadata: Informations complémentaires
        """
        task_type = task.get("task_type", "landing_page")
        context = task.get("context", "")
        target_audience = task.get("target_audience", "utilisateurs SaaS")
        goal = task.get("goal", "conversion")
        tone = task.get("tone", self.brand_voice)
        constraints = task.get("constraints", "")

        # Construire le prompt selon le type de tâche
        if task_type == "landing_page":
            user_prompt = self._build_landing_page_prompt(context, target_audience, goal, tone, constraints)
        elif task_type == "email":
            user_prompt = self._build_email_prompt(context, target_audience, goal, tone)
        elif task_type == "cta":
            user_prompt = self._build_cta_prompt(context, goal, tone)
        elif task_type == "microcopy":
            user_prompt = self._build_microcopy_prompt(context, constraints)
        elif task_type == "ad":
            user_prompt = self._build_ad_prompt(context, target_audience, goal, constraints)
        elif task_type == "seo":
            user_prompt = self._build_seo_prompt(context, constraints)
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
                "target_audience": target_audience,
                "tone": tone
            }
        }

    def _build_landing_page_prompt(self, context: str, audience: str, goal: str, tone: str, constraints: str) -> str:
        """Construit le prompt pour une landing page."""
        return f"""Rédige le copy complet d'une landing page pour:

CONTEXTE PRODUIT:
{context}

AUDIENCE CIBLE:
{audience}

OBJECTIF:
{goal}

TONE OF VOICE:
{tone}

CONTRAINTES:
{constraints if constraints else "Aucune contrainte spécifique"}

Structure de la landing page:
1. **Hero Section**
   - Headline (H1): Accrocheur, orienté bénéfice
   - Subheadline: Clarification de la value proposition
   - CTA primaire

2. **Problem Section**
   - Décrire le pain point
   - Empathie avec l'audience

3. **Solution Section**
   - Comment le produit résout le problème
   - 3-4 bénéfices clés avec icônes

4. **Features Section**
   - Features principales avec descriptions courtes
   - Focus sur "Pourquoi ça compte" pas juste "Qu'est-ce que c'est"

5. **Social Proof**
   - Témoignages (structure vide à remplir)
   - Logos de clients
   - Métriques (utilisateurs, satisfaction)

6. **Pricing/CTA Section**
   - CTA secondaire
   - Proposition de valeur finale

7. **FAQ** (3-5 questions)

Fournis 2 variations de headline pour A/B testing."""

    def _build_email_prompt(self, context: str, audience: str, goal: str, tone: str) -> str:
        """Construit le prompt pour un email."""
        return f"""Rédige un email marketing pour:

CONTEXTE:
{context}

AUDIENCE:
{audience}

OBJECTIF:
{goal}

TONE OF VOICE:
{tone}

L'email doit inclure:
- **Subject line** (3 variations pour A/B test)
- **Preview text** (optimisé pour mobile)
- **Opening** (personnalisé et engageant)
- **Body** (value proposition claire)
- **CTA** (clair et actionnable)
- **P.S.** (pour renforcer l'urgence ou ajouter de la valeur)

Longueur: 150-250 mots (optimal pour l'engagement)
Format: Plain text ou HTML simple selon l'objectif

Ajoute des [MERGE_TAGS] pour la personnalisation (prénom, entreprise, etc.)"""

    def _build_cta_prompt(self, context: str, goal: str, tone: str) -> str:
        """Construit le prompt pour des CTA."""
        return f"""Génère des Call-to-Action (CTA) pour:

CONTEXTE:
{context}

OBJECTIF:
{goal}

TONE OF VOICE:
{tone}

Génère 10 variations de CTA:
- 3 CTA directs (ex: "Commencer gratuitement")
- 3 CTA orientés bénéfice (ex: "Augmenter mes conversions")
- 2 CTA low-commitment (ex: "Voir une démo")
- 2 CTA urgents (ex: "Profiter de l'offre limitée")

Pour chaque CTA, indique:
- Le texte du bouton
- Le contexte d'utilisation optimal
- Le niveau de conversion attendu (estimé)

Format:
**CTA 1:** "Texte du CTA"
- Contexte: Où l'utiliser
- Type: Direct/Bénéfice/Low-commitment/Urgent"""

    def _build_microcopy_prompt(self, context: str, constraints: str) -> str:
        """Construit le prompt pour du microcopy UX."""
        return f"""Rédige du microcopy UX pour:

CONTEXTE:
{context}

CONTRAINTES:
{constraints if constraints else "Aucune contrainte spécifique"}

Génère le microcopy pour:

1. **Messages d'erreur** (5 variations)
   - Erreur de formulaire (email invalide, mot de passe faible, etc.)
   - Erreur serveur (500, timeout)
   - Erreur de permissions
   - Ton: Empathique, pas accusateur, avec solution

2. **Messages de succès** (3 variations)
   - Action complétée
   - Ton: Positif, encourageant

3. **Tooltips** (5 variations)
   - Aide contextuelle
   - Maximum 1-2 phrases
   - Ton: Utile, pas condescendant

4. **Empty states** (3 variations)
   - Quand pas de données
   - Ton: Encourageant à l'action

5. **Loading states** (3 variations)
   - Pendant le chargement
   - Ton: Rassurant, anticipe l'attente

Chaque message doit être:
- Court (< 80 caractères pour mobile)
- Actionnable (dire quoi faire ensuite)
- Human, pas robotique"""

    def _build_ad_prompt(self, context: str, audience: str, goal: str, constraints: str) -> str:
        """Construit le prompt pour une publicité."""
        return f"""Crée du copy publicitaire pour:

CONTEXTE PRODUIT:
{context}

AUDIENCE CIBLE:
{audience}

OBJECTIF:
{goal}

CONTRAINTES (plateforme, longueur):
{constraints if constraints else "Générique - tous canaux"}

Génère des ads pour:

1. **Google Ads**
   - Headline 1 (30 caractères max) - 3 variations
   - Headline 2 (30 caractères max) - 3 variations
   - Description (90 caractères max) - 2 variations

2. **Facebook/Instagram Ads**
   - Primary text (125 caractères optimal) - 2 variations
   - Headline (40 caractères max) - 3 variations
   - Description (30 caractères max)

3. **LinkedIn Ads**
   - Intro text (150 caractères) - 2 variations
   - Headline (70 caractères max) - 2 variations

4. **Twitter/X Ads**
   - Tweet copy (280 caractères max) - 3 variations

Pour chaque ad:
- Utiliser des power words
- Inclure une proposition de valeur claire
- CTA spécifique
- Urgence/Scarcity si pertinent"""

    def _build_seo_prompt(self, context: str, constraints: str) -> str:
        """Construit le prompt pour du contenu SEO."""
        return f"""Optimise le contenu SEO pour:

CONTEXTE:
{context}

KEYWORDS CIBLES:
{constraints}

Génère:

1. **Meta Title** (50-60 caractères)
   - Inclure keyword principal
   - Catchy et orienté clic
   - 3 variations

2. **Meta Description** (150-160 caractères)
   - Inclure keyword principal et secondaires
   - Value proposition claire
   - CTA implicite
   - 2 variations

3. **H1 Headline** (optimisé SEO + UX)
   - Keyword principal inclus naturellement
   - 2 variations

4. **H2 Subheadings** (5 suggestions)
   - Keywords secondaires
   - Structure logique du contenu

5. **URL Slug**
   - Court, descriptif
   - Keyword-rich
   - 2 variations

6. **Image Alt Text** (5 exemples)
   - Descriptif + keywords naturels

Format: Markdown avec annotations SEO"""

    async def write_landing_page(self, product_description: str, audience: str = "utilisateurs SaaS") -> str:
        """
        Méthode helper pour générer le copy d'une landing page.

        Args:
            product_description (str): Description du produit
            audience (str): Audience cible

        Returns:
            str: Copy de la landing page
        """
        result = await self.execute({
            "task_type": "landing_page",
            "context": product_description,
            "target_audience": audience,
            "goal": "conversion"
        })
        return result["output"]

    async def create_email_campaign(self, campaign_context: str, audience: str, objective: str = "conversion") -> str:
        """
        Méthode helper pour créer un email marketing.

        Args:
            campaign_context (str): Contexte de la campagne
            audience (str): Audience cible
            objective (str): Objectif (conversion, retention, awareness)

        Returns:
            str: Email complet avec variations
        """
        result = await self.execute({
            "task_type": "email",
            "context": campaign_context,
            "target_audience": audience,
            "goal": objective
        })
        return result["output"]

    async def generate_cta_variations(self, context: str, objective: str = "signup") -> str:
        """
        Méthode helper pour générer des variations de CTA.

        Args:
            context (str): Contexte du CTA
            objective (str): Objectif du CTA

        Returns:
            str: Liste de CTA avec recommandations
        """
        result = await self.execute({
            "task_type": "cta",
            "context": context,
            "goal": objective
        })
        return result["output"]

    async def create_microcopy_set(self, ux_context: str, character_limit: int = None) -> str:
        """
        Méthode helper pour créer un set de microcopy UX.

        Args:
            ux_context (str): Contexte de l'interface
            character_limit (int): Limite de caractères (optionnel)

        Returns:
            str: Set complet de microcopy
        """
        constraints = f"Limite: {character_limit} caractères" if character_limit else ""
        result = await self.execute({
            "task_type": "microcopy",
            "context": ux_context,
            "constraints": constraints
        })
        return result["output"]

    def set_brand_voice(self, tone: str):
        """
        Change le tone of voice de la marque.

        Args:
            tone (str): Nouveau tone (ex: "friendly and casual", "professional and authoritative")
        """
        self.brand_voice = tone
        self.system_prompt = self.system_prompt.replace(
            f"Tone of voice par défaut: {self.brand_voice}",
            f"Tone of voice par défaut: {tone}"
        )
