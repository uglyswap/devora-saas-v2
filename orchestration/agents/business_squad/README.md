# Business Squad - Agents d'Orchestration Business

Ce module contient tous les agents du Business Squad pour Devora, responsables de la gestion produit, marketing, pricing, conformité et growth.

## Agents Disponibles

### 1. ProductManagerAgent
**Responsabilités:**
- Générer des PRD (Product Requirement Documents)
- Créer des user stories au format Agile
- Définir la roadmap produit
- Prioriser les features avec le framework RICE

**Utilisation:**
```python
from orchestration.agents.business_squad import ProductManagerAgent

# Initialiser l'agent
pm = ProductManagerAgent(api_key="your-openrouter-api-key")

# Générer un PRD
prd = await pm.generate_prd(
    feature_description="Système de notifications push en temps réel",
    target_audience="utilisateurs actifs de l'application mobile"
)

# Créer des user stories
stories = await pm.create_user_stories(
    feature_description="Dashboard analytics pour les admins",
    persona="Product Manager"
)

# Prioriser des features avec RICE
prioritization = await pm.prioritize_features([
    "Authentification SSO",
    "Export PDF des rapports",
    "Mode dark",
    "Intégration Slack"
])
```

### 2. CopywriterAgent
**Responsabilités:**
- Rédiger le copy marketing (landing pages, emails, ads)
- Créer le microcopy UX (CTA, tooltips, messages d'erreur)
- Optimiser le contenu pour la conversion
- Adapter le tone of voice selon la marque

**Utilisation:**
```python
from orchestration.agents.business_squad import CopywriterAgent

# Initialiser l'agent
copywriter = CopywriterAgent(
    api_key="your-openrouter-api-key",
    brand_voice="professionnel et accessible"
)

# Générer le copy d'une landing page
landing_copy = await copywriter.write_landing_page(
    product_description="Plateforme SaaS d'orchestration d'agents AI",
    audience="développeurs et product teams"
)

# Créer une campagne email
email = await copywriter.create_email_campaign(
    campaign_context="Lancement nouvelle feature: AI Agents collaboration",
    audience="utilisateurs actifs",
    objective="conversion"
)

# Générer des variations de CTA
ctas = await copywriter.generate_cta_variations(
    context="Page de pricing, objectif signup trial",
    objective="signup"
)

# Créer du microcopy UX
microcopy = await copywriter.create_microcopy_set(
    ux_context="Formulaire d'inscription avec validation",
    character_limit=80
)
```

### 3. PricingStrategistAgent
**Responsabilités:**
- Définir les modèles de pricing (freemium, tiered, usage-based)
- Créer les tiers d'abonnement optimaux
- Calculer les métriques (LTV, CAC, Payback Period)
- Optimiser la monétisation et l'expansion revenue

**Utilisation:**
```python
from orchestration.agents.business_squad import PricingStrategistAgent

# Initialiser l'agent
pricing = PricingStrategistAgent(api_key="your-openrouter-api-key")

# Designer un modèle de pricing
model = await pricing.design_pricing_model(
    product_context="Plateforme d'orchestration d'agents AI avec usage-based billing",
    target_market="SMB"
)

# Créer des tiers de pricing
tiers = await pricing.create_pricing_tiers(
    product_context="SaaS B2B avec freemium",
    target_market="Mid-Market"
)

# Analyser les métriques financières
metrics_analysis = await pricing.analyze_metrics(
    product_context="SaaS avec 1000 utilisateurs actifs",
    financial_data={
        "monthly_revenue": 50000,
        "cac": 150,
        "arpu": 50,
        "churn_rate": 5,
        "marketing_spend": 15000
    }
)

# Optimiser le pricing existant
optimization = await pricing.optimize_pricing(
    product_context="SaaS B2B établi",
    current_pricing="3 tiers: Starter $29, Pro $99, Business $299",
    financial_data={
        "arpu": 85,
        "ltv": 1200,
        "cac": 300
    }
)
```

### 4. ComplianceOfficerAgent
**Responsabilités:**
- Vérifier la conformité GDPR, CCPA, LGPD
- Générer les politiques de confidentialité et CGU
- Auditer les pratiques de données
- Implémenter les droits des utilisateurs

**Utilisation:**
```python
from orchestration.agents.business_squad import ComplianceOfficerAgent

# Initialiser l'agent
compliance = ComplianceOfficerAgent(
    api_key="your-openrouter-api-key",
    regulations=["GDPR", "CCPA"]
)

# Auditer la conformité
audit = await compliance.audit_compliance(
    product_context="SaaS B2B avec stockage de données personnelles",
    data_types=["email", "nom", "prénom", "adresse IP", "usage data"],
    jurisdictions=["EU", "US"]
)

# Générer une privacy policy
privacy_policy = await compliance.generate_privacy_policy(
    product_context="Application SaaS",
    data_types=["email", "nom", "données d'utilisation"],
    jurisdictions=["EU", "US", "CA"]
)

# Mapper les flux de données
data_mapping = await compliance.map_data_flows(
    product_context="SaaS avec intégrations tierces",
    data_types=["PII", "usage data", "payment data"]
)

# Designer le mécanisme de consentement
consent = await compliance.design_consent_mechanism(
    product_context="Application web avec cookies analytics",
    data_types=["cookies", "email marketing"]
)

# Conduire une DPIA
dpia = await compliance.conduct_dpia(
    product_context="Nouveau système de tracking comportemental",
    data_types=["behavioral data", "device fingerprinting"]
)
```

### 5. GrowthEngineerAgent
**Responsabilités:**
- Implémenter les feature flags et progressive rollouts
- Configurer les A/B tests
- Optimiser les funnels de conversion
- Améliorer la rétention utilisateur

**Utilisation:**
```python
from orchestration.agents.business_squad import GrowthEngineerAgent

# Initialiser l'agent
growth = GrowthEngineerAgent(api_key="your-openrouter-api-key")

# Implémenter un feature flag
feature_flag = await growth.implement_feature_flag(
    feature_description="Nouveau dashboard avec AI insights",
    context="SaaS B2B, rollout progressif sur 4 semaines"
)

# Designer un A/B test
ab_test = await growth.design_ab_test(
    hypothesis="Un onboarding interactif augmente l'activation de 20%",
    metric="activation_rate",
    context="Funnel signup pour SaaS"
)

# Optimiser un funnel
funnel_optimization = await growth.optimize_funnel(
    context="Funnel signup SaaS: Landing → Signup → Email Verify → Onboarding → Activation",
    current_metrics={
        "landing_to_signup": 0.40,
        "signup_to_verify": 0.80,
        "verify_to_onboarding": 0.60,
        "onboarding_to_activation": 0.30
    }
)

# Améliorer la rétention
retention_strategy = await growth.improve_retention(
    context="SaaS B2B avec churn problématique",
    current_metrics={
        "d1_retention": 0.45,
        "d7_retention": 0.28,
        "d30_retention": 0.15,
        "monthly_churn": 8.5
    }
)

# Créer des growth loops
growth_loops = await growth.build_growth_loop(
    context="SaaS avec potentiel viral (collaboration features)",
    current_metrics={
        "k_factor": 0.8,
        "viral_coefficient": 0.5
    }
)
```

## Installation

### Prérequis
```bash
pip install httpx
```

### Configuration

Tous les agents nécessitent une clé API OpenRouter:

```python
import os
os.environ['OPENROUTER_API_KEY'] = "your-api-key"

# Ou passer directement au constructeur
agent = ProductManagerAgent(api_key="your-api-key")
```

## Architecture

Tous les agents héritent de `BaseAgent` qui fournit:
- Gestion de la mémoire conversationnelle
- Appels LLM via OpenRouter
- Interface asynchrone commune

```python
class BaseAgent(ABC):
    def __init__(self, name: str, api_key: str, model: str = "openai/gpt-4o")
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]
    async def call_llm(self, messages: List[Dict], system_prompt: str) -> str
    def add_to_memory(self, role: str, content: str)
    def get_memory() -> List[Dict[str, Any]]
    def clear_memory()
```

## Modèles LLM Supportés

Par défaut, tous les agents utilisent `openai/gpt-4o` via OpenRouter, mais vous pouvez spécifier n'importe quel modèle:

```python
agent = ProductManagerAgent(
    api_key="your-key",
    model="anthropic/claude-3.5-sonnet"  # ou autre
)
```

## Exemples Complets

### Workflow Complet: Lancement d'une Feature

```python
import asyncio
from orchestration.agents.business_squad import (
    ProductManagerAgent,
    CopywriterAgent,
    GrowthEngineerAgent,
    ComplianceOfficerAgent
)

async def launch_feature():
    api_key = "your-openrouter-api-key"

    # 1. Product Manager crée le PRD
    pm = ProductManagerAgent(api_key=api_key)
    prd = await pm.generate_prd(
        feature_description="Système de notifications push personnalisées",
        target_audience="utilisateurs actifs"
    )
    print("PRD généré:", prd)

    # 2. Compliance vérifie la conformité
    compliance = ComplianceOfficerAgent(api_key=api_key)
    audit = await compliance.audit_compliance(
        product_context="Feature de notifications push",
        data_types=["device tokens", "preferences", "usage patterns"]
    )
    print("Audit conformité:", audit['risk_level'])

    # 3. Copywriter crée le messaging
    copywriter = CopywriterAgent(api_key=api_key)
    microcopy = await copywriter.create_microcopy_set(
        ux_context="Settings de notifications avec toggles",
        character_limit=60
    )
    print("Microcopy créé:", microcopy)

    # 4. Growth Engineer prépare le rollout
    growth = GrowthEngineerAgent(api_key=api_key)
    feature_flag = await growth.implement_feature_flag(
        feature_description="Notifications push v2",
        context="Rollout progressif: 5% → 25% → 100% sur 3 semaines"
    )
    print("Feature flag configuré:", feature_flag)

asyncio.run(launch_feature())
```

### Workflow: Optimisation Pricing

```python
async def optimize_saas_pricing():
    api_key = "your-key"

    pricing = PricingStrategistAgent(api_key=api_key)

    # Analyser les métriques actuelles
    analysis = await pricing.analyze_metrics(
        product_context="SaaS B2B établi",
        financial_data={
            "mrr": 150000,
            "arr": 1800000,
            "cac": 450,
            "arpu": 125,
            "ltv": 2500,
            "churn_rate": 6.5,
            "payback_months": 8
        }
    )

    # Optimiser le pricing
    optimization = await pricing.optimize_pricing(
        product_context="SaaS B2B",
        current_pricing="Starter $49, Pro $149, Business $399",
        financial_data=analysis
    )

    # Créer stratégie d'expansion
    expansion = await pricing.build_expansion_strategy(
        product_context="SaaS avec seat-based pricing",
        current_pricing=optimization
    )

    return {
        "analysis": analysis,
        "optimization": optimization,
        "expansion": expansion
    }

asyncio.run(optimize_saas_pricing())
```

## Tests

Pour tester les agents:

```bash
cd orchestration/agents/business_squad
python -m pytest tests/
```

## Performance

- Tous les appels LLM sont asynchrones
- Timeout par défaut: 120 secondes
- Cache de mémoire conversationnelle par agent
- Retry automatique non implémenté (à ajouter si besoin)

## Sécurité

- ⚠️ **Ne jamais commiter les clés API**
- Utiliser des variables d'environnement
- Les agents ne stockent pas les données sensibles
- Audit logs recommandés pour la production

## Roadmap

- [ ] Ajouter retry logic avec backoff exponentiel
- [ ] Implémenter le caching des résultats
- [ ] Ajouter support pour streaming responses
- [ ] Créer des templates de prompts customizables
- [ ] Ajouter métriques de performance (latency, token usage)
- [ ] Intégration avec orchestrateur central

## Support

Pour questions ou bugs, ouvrir une issue sur le repo Devora.

## License

Propriétaire - Devora Team
