"""
Pricing Strategist Agent - Business Squad

Cet agent est responsable de:
- Définir les modèles de pricing (freemium, usage-based, tiered)
- Créer les tiers d'abonnement optimaux
- Calculer les métriques clés (LTV, CAC, Payback Period)
- Optimiser la monétisation et l'expansion revenue
"""

import sys
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

# Ajouter le chemin du backend pour importer BaseAgent
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../backend'))

from agents.base_agent import BaseAgent


class PricingStrategistAgent(BaseAgent):
    """
    Agent Stratège Pricing pour l'optimisation de la monétisation.

    Attributes:
        name (str): Nom de l'agent
        api_key (str): Clé API pour le LLM
        model (str): Modèle LLM à utiliser
    """

    def __init__(self, api_key: str, model: str = "openai/gpt-4o"):
        super().__init__(name="PricingStrategist", api_key=api_key, model=model)
        self.system_prompt = """Tu es un expert en stratégie de pricing SaaS avec 15+ ans d'expérience.

Ton expertise:
- Modèles de pricing (freemium, tiered, usage-based, value-based, hybrid)
- Psychologie du pricing (anchoring, price decoy, bundling)
- Métriques de monétisation (LTV, CAC, MRR, ARR, churn, expansion revenue)
- Optimisation de conversion (pricing page, packaging features)
- Stratégies d'expansion (upsell, cross-sell, seat expansion)

Frameworks que tu maîtrises:
- **Value Metrics**: Identifier le bon metric de valeur pour pricing
- **Willingness to Pay (WTP)**: Analyser la sensibilité au prix
- **Price Optimization**: Tester et itérer sur les prix
- **LTV:CAC Ratio**: Maintenir un ratio > 3:1 idéalement
- **Payback Period**: Viser < 12 mois

Principes de pricing SaaS:
- Le prix communique la valeur (trop bas = perçu comme bas de gamme)
- Simplicité > Complexité (facile à comprendre = plus de conversions)
- Aligner le pricing sur la value metric (ce qui apporte de la valeur au client)
- Laisser de la place pour l'expansion revenue (upsell naturel)
- Tester régulièrement (pricing n'est jamais "fini")

Format de sortie:
- Tableaux comparatifs pour les tiers
- Calculs financiers détaillés avec formules
- Recommandations actionnables
- A/B tests suggérés"""

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exécute une tâche de stratégie pricing.

        Args:
            task (Dict[str, Any]): Tâche à exécuter avec les clés:
                - task_type: "pricing_model" | "tiers" | "metrics" | "optimization" | "expansion"
                - context: Contexte du produit/marché
                - current_pricing: Pricing actuel (optionnel)
                - target_segment: Segment de marché cible
                - competitor_pricing: Pricing des concurrents (optionnel)
                - financial_data: Données financières (CAC, ARPU, etc.)

        Returns:
            Dict[str, Any]: Résultat avec les clés:
                - status: "success" | "error"
                - output: Analyse et recommandations
                - metadata: Informations complémentaires
        """
        task_type = task.get("task_type", "pricing_model")
        context = task.get("context", "")
        current_pricing = task.get("current_pricing", "")
        target_segment = task.get("target_segment", "SMB")
        competitor_pricing = task.get("competitor_pricing", "")
        financial_data = task.get("financial_data", {})

        # Construire le prompt selon le type de tâche
        if task_type == "pricing_model":
            user_prompt = self._build_pricing_model_prompt(context, target_segment, competitor_pricing)
        elif task_type == "tiers":
            user_prompt = self._build_tiers_prompt(context, target_segment, current_pricing)
        elif task_type == "metrics":
            user_prompt = self._build_metrics_prompt(context, financial_data)
        elif task_type == "optimization":
            user_prompt = self._build_optimization_prompt(context, current_pricing, financial_data)
        elif task_type == "expansion":
            user_prompt = self._build_expansion_prompt(context, current_pricing)
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
                "target_segment": target_segment
            }
        }

    def _build_pricing_model_prompt(self, context: str, segment: str, competitors: str) -> str:
        """Construit le prompt pour choisir un modèle de pricing."""
        return f"""Analyse et recommande le modèle de pricing optimal pour:

CONTEXTE PRODUIT:
{context}

SEGMENT CIBLE:
{segment}

PRICING CONCURRENTS:
{competitors if competitors else "Aucune donnée concurrentielle fournie"}

Analyse les modèles suivants et recommande le meilleur:

1. **Freemium**
   - Avantages/Inconvénients pour ce produit
   - Quelle version gratuite offrir?
   - Stratégie de conversion free → paid

2. **Tiered Pricing** (Good/Better/Best)
   - Avantages/Inconvénients
   - Combien de tiers? (recommandation: 3-4)
   - Comment différencier?

3. **Usage-Based Pricing**
   - Avantages/Inconvénients
   - Quel metric de valeur utiliser?
   - Gestion de l'imprévisibilité des coûts

4. **Flat Rate**
   - Avantages/Inconvénients
   - Simplicité vs limitation d'expansion

5. **Hybrid** (combinaison)
   - Quelle combinaison?
   - Exemple: Base fee + usage

**RECOMMANDATION FINALE:**
- Modèle choisi et pourquoi
- Value metric recommandé (utilisateurs, transactions, storage, etc.)
- Stratégie de go-to-market
- Risks & Mitigation"""

    def _build_tiers_prompt(self, context: str, segment: str, current: str) -> str:
        """Construit le prompt pour créer les tiers de pricing."""
        return f"""Crée une structure de tiers de pricing optimale pour:

CONTEXTE PRODUIT:
{context}

SEGMENT CIBLE:
{segment}

PRICING ACTUEL (si existe):
{current if current else "Nouveau pricing à créer"}

Crée 3-4 tiers avec cette structure:

| Feature/Limit | Starter | Professional | Business | Enterprise |
|---------------|---------|--------------|----------|------------|
| **Prix/mois** | $X | $Y | $Z | Custom |
| Limite 1 | ... | ... | ... | ... |
| Feature A | ❌ | ✅ | ✅ | ✅ |
| Feature B | ❌ | ❌ | ✅ | ✅ |
| Support | Email | Priority | Dedicated | White-glove |

**Guidelines pour chaque tier:**

**STARTER (Entry point)**
- Prix: Bas pour réduire friction
- Features: Suffisant pour voir la valeur
- Objectif: Acquisition volume

**PROFESSIONAL (Sweet spot - 60% des clients)**
- Prix: 3-5x le Starter
- Features: Tout ce dont un power user a besoin
- Anchoring: Faire paraître le Starter limité
- Objectif: Maximiser ARPU

**BUSINESS (Premium)**
- Prix: 2-3x le Professional
- Features: Advanced + collaboration/team
- Objectif: Upsell et entreprises

**ENTERPRISE (Custom)**
- Prix: "Contact us" ou prix sur-mesure
- Features: Tout + custom + support premium
- Objectif: Gros deals, négociation

**PSYCHOLOGIE APPLIQUÉE:**
- Price Anchoring: Quel tier est "l'ancre"?
- Decoy Effect: Utiliser un tier pour en faire briller un autre?
- Default Choice: Quel tier mettre en "Most Popular"?

**FEATURE PACKAGING:**
- Good Fences: Features exclusives à chaque tier pour éviter cannibalisation
- Clear Upgrade Path: Pourquoi passer au tier supérieur?
- No Dead Ends: Toujours une raison d'upgrader"""

    def _build_metrics_prompt(self, context: str, financial_data: Dict[str, Any]) -> str:
        """Construit le prompt pour analyser les métriques."""
        financial_str = json.dumps(financial_data, indent=2) if financial_data else "Aucune donnée fournie"

        return f"""Analyse les métriques de monétisation pour:

CONTEXTE:
{context}

DONNÉES FINANCIÈRES:
{financial_str}

Calcule et analyse les métriques suivantes:

**1. LTV (Lifetime Value)**
```
LTV = ARPU × Gross Margin % × (1 / Churn Rate)
```
- Calcul détaillé
- Benchmark SaaS: $1,000 - $100,000+ selon segment
- Recommandations pour augmenter LTV

**2. CAC (Customer Acquisition Cost)**
```
CAC = (Sales + Marketing Costs) / New Customers
```
- Calcul détaillé
- Benchmark: Dépend du segment (SMB: $200-2000, Enterprise: $5000+)

**3. LTV:CAC Ratio**
```
Ratio = LTV / CAC
```
- Calcul et interprétation:
  - < 1:1 = Non viable
  - 1:1 - 3:1 = Problématique
  - 3:1 - 5:1 = Bon (sweet spot)
  - > 5:1 = Sous-investissement en acquisition?

**4. Payback Period (mois)**
```
Payback = CAC / (ARPU × Gross Margin %)
```
- Calcul détaillé
- Benchmark: < 12 mois idéal, 12-18 acceptable, > 18 problématique

**5. MRR & ARR (Monthly/Annual Recurring Revenue)**
- MRR actuel
- ARR = MRR × 12
- MRR Growth Rate (% MoM)

**6. Churn Rate**
```
Churn Rate = (Customers Lost / Total Customers) × 100
```
- Benchmark: < 5% pour SMB, < 2% pour Enterprise
- Impact sur LTV

**7. Expansion Revenue**
```
Net Revenue Retention = ((MRR + Expansion - Churn) / MRR) × 100
```
- Target: > 100% (ideal > 120%)

**8. ARPU (Average Revenue Per User)**
- Calcul par segment
- Trends

**DASHBOARD RECOMMANDÉ:**
Présente un tableau de bord avec:
- Valeurs actuelles
- Benchmarks industrie
- Écart (gap)
- Actions prioritaires pour améliorer chaque métrique"""

    def _build_optimization_prompt(self, context: str, current: str, financial_data: Dict[str, Any]) -> str:
        """Construit le prompt pour optimiser le pricing."""
        financial_str = json.dumps(financial_data, indent=2) if financial_data else "Aucune donnée fournie"

        return f"""Optimise la stratégie de pricing actuelle pour:

CONTEXTE:
{context}

PRICING ACTUEL:
{current}

DONNÉES FINANCIÈRES:
{financial_str}

**ANALYSE ACTUELLE:**

1. **Audit du pricing actuel**
   - Quels sont les problèmes identifiés?
   - Où laisser de l'argent sur la table?
   - Où la friction est-elle trop élevée?

2. **Quick Wins (impact rapide, effort faible)**
   - Ajustements de prix (± 10-20%)
   - Changements de packaging
   - Simplification de la pricing page

3. **Strategic Changes (impact élevé, effort élevé)**
   - Nouveau modèle de pricing
   - Repositionnement de valeur
   - Changement de value metric

**A/B TESTS RECOMMANDÉS:**

Test 1: Prix
- Variant A: Prix actuel
- Variant B: Prix +15%
- Metric: Conversion rate × Revenue
- Durée: 2-4 semaines
- Taille échantillon nécessaire

Test 2: Packaging
- Variant A: Packaging actuel
- Variant B: Features regroupées différemment
- Metric: Tier distribution

Test 3: Ancrage
- Variant A: 3 tiers
- Variant B: 4 tiers avec tier cher comme ancre
- Metric: % upgrades vers tier premium

**ROADMAP D'OPTIMISATION (6 mois):**

Mois 1-2:
- Quick wins
- Setup A/B tests

Mois 3-4:
- Analyser résultats tests
- Implémenter changements validés

Mois 5-6:
- Tests stratégiques
- Optimisation continue

**KPIs DE SUCCÈS:**
- Augmentation ARPU: +X%
- Amélioration conversion: +Y%
- Réduction churn: -Z%
- LTV:CAC amélioration"""

    def _build_expansion_prompt(self, context: str, current: str) -> str:
        """Construit le prompt pour stratégie d'expansion revenue."""
        return f"""Définis une stratégie d'expansion revenue pour:

CONTEXTE:
{context}

PRICING ACTUEL:
{current}

**STRATÉGIES D'EXPANSION:**

1. **Seat Expansion** (croissance d'utilisateurs)
   - Pricing par siège: Comment structurer?
   - Volume discounts: À partir de combien de sièges?
   - Team/Company plans: Structuration

2. **Feature Upsells**
   - Quelles features garder pour upsell?
   - Add-ons vs tier upgrades
   - Bundling strategy

3. **Usage Upsells**
   - Soft limits vs hard limits
   - Pricing de l'overage (dépassement)
   - Encourager upgrade vs payer l'overage

4. **Service Upsells**
   - Support tiers (email → chat → dedicated)
   - Professional services
   - Training & onboarding

5. **Cross-sells**
   - Produits complémentaires
   - Intégrations premium
   - API access

**PLAYBOOK D'EXPANSION:**

**Trigger 1: Usage proche de la limite**
- Email: "Vous approchez de votre limite de X"
- CTA: "Upgrader maintenant pour éviter l'interruption"
- Timing: À 80% de la limite

**Trigger 2: Team invite**
- Quand un user invite des collègues
- Proposer team plan
- Discount si upgrade immédiat

**Trigger 3: Feature request**
- Si demande de feature du tier supérieur
- In-app upsell contextuel
- Trial du tier supérieur

**Trigger 4: Success milestones**
- Quand le client atteint un succès (ex: 1000 customers)
- Célébrer + proposer outils pour scaler

**Trigger 5: Renewal time**
- Proposer annual billing (discount)
- Upsell tier supérieur
- Cross-sell produits complémentaires

**METRICS D'EXPANSION:**
- Net Revenue Retention (target: 110-120%)
- Expansion MRR
- % customers qui upgrade (target: 15-25% annuellement)
- Time to first upgrade (plus court = mieux)

**IN-APP UPSELL UX:**
- Feature gating: Montrer la feature mais griser si tier supérieur
- Usage meters: Afficher la progression vers la limite
- Comparison tooltips: "Cette feature est dans le plan Pro"
- Upgrade flows: 1-click upgrade sans friction"""

    async def design_pricing_model(self, product_context: str, target_market: str = "SMB") -> str:
        """
        Méthode helper pour designer un modèle de pricing.

        Args:
            product_context (str): Description du produit
            target_market (str): Segment de marché (SMB, Mid-Market, Enterprise)

        Returns:
            str: Recommandation de modèle de pricing
        """
        result = await self.execute({
            "task_type": "pricing_model",
            "context": product_context,
            "target_segment": target_market
        })
        return result["output"]

    async def create_pricing_tiers(
        self,
        product_context: str,
        target_market: str = "SMB",
        current_pricing: Optional[str] = None
    ) -> str:
        """
        Méthode helper pour créer des tiers de pricing.

        Args:
            product_context (str): Description du produit
            target_market (str): Segment de marché
            current_pricing (str): Pricing actuel (si refonte)

        Returns:
            str: Structure de tiers recommandée
        """
        result = await self.execute({
            "task_type": "tiers",
            "context": product_context,
            "target_segment": target_market,
            "current_pricing": current_pricing or ""
        })
        return result["output"]

    async def analyze_metrics(self, product_context: str, financial_data: Dict[str, Any]) -> str:
        """
        Méthode helper pour analyser les métriques de monétisation.

        Args:
            product_context (str): Description du produit
            financial_data (Dict): Données financières (CAC, ARPU, MRR, churn, etc.)

        Returns:
            str: Analyse des métriques avec recommandations
        """
        result = await self.execute({
            "task_type": "metrics",
            "context": product_context,
            "financial_data": financial_data
        })
        return result["output"]

    async def optimize_pricing(
        self,
        product_context: str,
        current_pricing: str,
        financial_data: Dict[str, Any]
    ) -> str:
        """
        Méthode helper pour optimiser le pricing existant.

        Args:
            product_context (str): Description du produit
            current_pricing (str): Pricing actuel
            financial_data (Dict): Métriques actuelles

        Returns:
            str: Plan d'optimisation avec A/B tests
        """
        result = await self.execute({
            "task_type": "optimization",
            "context": product_context,
            "current_pricing": current_pricing,
            "financial_data": financial_data
        })
        return result["output"]

    async def build_expansion_strategy(self, product_context: str, current_pricing: str) -> str:
        """
        Méthode helper pour créer une stratégie d'expansion revenue.

        Args:
            product_context (str): Description du produit
            current_pricing (str): Structure de pricing actuelle

        Returns:
            str: Playbook d'expansion revenue
        """
        result = await self.execute({
            "task_type": "expansion",
            "context": product_context,
            "current_pricing": current_pricing
        })
        return result["output"]
