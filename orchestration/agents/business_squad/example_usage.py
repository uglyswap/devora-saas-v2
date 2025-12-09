#!/usr/bin/env python3
"""
Exemple d'utilisation des agents du Business Squad.

Ce script démontre comment utiliser chaque agent individuellement.
Pour exécuter: python example_usage.py
"""

import asyncio
import os
from product_manager import ProductManagerAgent
from copywriter import CopywriterAgent
from pricing_strategist import PricingStrategistAgent
from compliance_officer import ComplianceOfficerAgent
from growth_engineer import GrowthEngineerAgent


async def example_product_manager():
    """Exemple d'utilisation du Product Manager Agent."""
    print("\n" + "="*80)
    print("PRODUCT MANAGER AGENT - Exemple")
    print("="*80)

    # NOTE: Remplacer par votre vraie clé API
    api_key = os.environ.get("OPENROUTER_API_KEY", "sk-or-v1-dummy-key")

    pm = ProductManagerAgent(api_key=api_key)

    # Exemple: Créer des user stories
    print("\n[1/2] Génération de user stories...")
    result = await pm.execute({
        "task_type": "user_story",
        "context": "Feature de dashboard analytics temps réel pour SaaS B2B",
        "target_audience": "Product Managers et Data Analysts"
    })

    if result["status"] == "success":
        print("\n✓ User stories générées:")
        print(result["output"][:500] + "...")  # Afficher les 500 premiers caractères
    else:
        print(f"\n✗ Erreur: {result['output']}")

    # Exemple: Priorisation RICE
    print("\n[2/2] Priorisation de features avec RICE...")
    features_to_prioritize = """
    - Authentification SSO (Google, Microsoft)
    - Export PDF des rapports
    - Mode dark pour l'interface
    - Intégration Slack pour notifications
    - API publique avec webhooks
    """

    result = await pm.execute({
        "task_type": "prioritization",
        "context": features_to_prioritize
    })

    if result["status"] == "success":
        print("\n✓ Priorisation RICE:")
        print(result["output"][:500] + "...")
    else:
        print(f"\n✗ Erreur: {result['output']}")


async def example_copywriter():
    """Exemple d'utilisation du Copywriter Agent."""
    print("\n" + "="*80)
    print("COPYWRITER AGENT - Exemple")
    print("="*80)

    api_key = os.environ.get("OPENROUTER_API_KEY", "sk-or-v1-dummy-key")
    copywriter = CopywriterAgent(api_key=api_key)

    # Exemple: Générer des CTA
    print("\n[1/1] Génération de variations de CTA...")
    result = await copywriter.execute({
        "task_type": "cta",
        "context": "Page de pricing pour SaaS d'orchestration d'agents AI",
        "goal": "signup_trial"
    })

    if result["status"] == "success":
        print("\n✓ Variations de CTA générées:")
        print(result["output"][:600] + "...")
    else:
        print(f"\n✗ Erreur: {result['output']}")


async def example_pricing_strategist():
    """Exemple d'utilisation du Pricing Strategist Agent."""
    print("\n" + "="*80)
    print("PRICING STRATEGIST AGENT - Exemple")
    print("="*80)

    api_key = os.environ.get("OPENROUTER_API_KEY", "sk-or-v1-dummy-key")
    pricing = PricingStrategistAgent(api_key=api_key)

    # Exemple: Créer des tiers de pricing
    print("\n[1/1] Création de tiers de pricing...")
    result = await pricing.execute({
        "task_type": "tiers",
        "context": "SaaS d'orchestration d'agents AI, usage-based billing sur nombre d'agents",
        "target_segment": "SMB et Mid-Market"
    })

    if result["status"] == "success":
        print("\n✓ Tiers de pricing créés:")
        print(result["output"][:700] + "...")
    else:
        print(f"\n✗ Erreur: {result['output']}")


async def example_compliance_officer():
    """Exemple d'utilisation du Compliance Officer Agent."""
    print("\n" + "="*80)
    print("COMPLIANCE OFFICER AGENT - Exemple")
    print("="*80)

    api_key = os.environ.get("OPENROUTER_API_KEY", "sk-or-v1-dummy-key")
    compliance = ComplianceOfficerAgent(api_key=api_key, regulations=["GDPR", "CCPA"])

    # Exemple: Audit de conformité
    print("\n[1/1] Audit de conformité GDPR/CCPA...")
    result = await compliance.execute({
        "task_type": "audit",
        "context": "SaaS avec stockage cloud, agents AI traitant des données clients",
        "data_types": ["email", "nom", "entreprise", "données d'utilisation", "logs d'agents"],
        "jurisdictions": ["EU", "US"]
    })

    if result["status"] == "success":
        print(f"\n✓ Audit complété - Niveau de risque: {result['risk_level'].upper()}")
        print(result["output"][:600] + "...")
    else:
        print(f"\n✗ Erreur: {result['output']}")


async def example_growth_engineer():
    """Exemple d'utilisation du Growth Engineer Agent."""
    print("\n" + "="*80)
    print("GROWTH ENGINEER AGENT - Exemple")
    print("="*80)

    api_key = os.environ.get("OPENROUTER_API_KEY", "sk-or-v1-dummy-key")
    growth = GrowthEngineerAgent(api_key=api_key)

    # Exemple: Design d'un A/B test
    print("\n[1/1] Design d'un A/B test...")
    result = await growth.execute({
        "task_type": "ab_test",
        "context": "SaaS onboarding flow",
        "hypothesis": "Un onboarding interactif avec tutoriel augmente l'activation de 25%",
        "target_metric": "activation_rate"
    })

    if result["status"] == "success":
        print("\n✓ A/B test designé:")
        print(result["output"][:700] + "...")
    else:
        print(f"\n✗ Erreur: {result['output']}")


async def run_all_examples():
    """Exécute tous les exemples séquentiellement."""
    print("\n" + "🚀 "*20)
    print("BUSINESS SQUAD - Démonstration des Agents")
    print("🚀 "*20)

    # Vérifier la clé API
    if not os.environ.get("OPENROUTER_API_KEY"):
        print("\n⚠️  WARNING: OPENROUTER_API_KEY n'est pas définie.")
        print("Les exemples utiliseront une clé dummy et échoueront.")
        print("\nPour tester avec une vraie clé:")
        print("export OPENROUTER_API_KEY='votre-clé'")
        print("python example_usage.py")
        print("\nExécution des exemples avec dummy key...\n")

    try:
        await example_product_manager()
        await example_copywriter()
        await example_pricing_strategist()
        await example_compliance_officer()
        await example_growth_engineer()

        print("\n" + "="*80)
        print("✓ Tous les exemples ont été exécutés!")
        print("="*80)

    except Exception as e:
        print(f"\n✗ Erreur lors de l'exécution: {e}")
        print("\nSi vous voyez une erreur d'authentification, définissez OPENROUTER_API_KEY")


if __name__ == "__main__":
    # Exécuter tous les exemples
    asyncio.run(run_all_examples())
