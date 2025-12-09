# Business Squad - Capacités Détaillées

Ce document liste toutes les capacités de chaque agent du Business Squad.

---

## 1. ProductManagerAgent

### Task Types Supportés

#### `prd` - Product Requirement Document
**Input:**
```python
{
    "task_type": "prd",
    "context": "Description de la feature",
    "target_audience": "Audience cible",
    "constraints": "Contraintes techniques/business (optionnel)"
}
```

**Output:** PRD complet incluant:
- Executive Summary
- Problème à résoudre
- Objectifs et KPIs
- User personas et use cases
- Requirements fonctionnels et non-fonctionnels
- User flows
- Critères d'acceptation
- Timeline et phases

#### `user_story` - User Stories
**Input:**
```python
{
    "task_type": "user_story",
    "context": "Description de la feature",
    "target_audience": "Persona principal"
}
```

**Output:** 5+ user stories au format:
- En tant que [persona]
- Je veux [action]
- Afin de [bénéfice]
- Critères d'acceptation
- Estimation (story points)
- Priorité (P0-P3)

#### `roadmap` - Product Roadmap
**Input:**
```python
{
    "task_type": "roadmap",
    "context": "Vision produit",
    "constraints": "Timeline, ressources"
}
```

**Output:** Roadmap sur 12 mois:
- Phase 1 - MVP (Mois 1-2)
- Phase 2 - Growth (Mois 3-6)
- Phase 3 - Scale (Mois 7-12)
- Objectifs, features, KPIs par phase

#### `prioritization` - Priorisation RICE
**Input:**
```python
{
    "task_type": "prioritization",
    "context": "Liste de features à prioriser"
}
```

**Output:** Tableau avec scores RICE:
- Reach (0-10)
- Impact (0.25-3)
- Confidence (0-100%)
- Effort (1-10)
- Score RICE calculé
- Ordre d'implémentation recommandé

### Méthodes Helper
- `generate_prd(feature_description, target_audience)`
- `create_user_stories(feature_description, persona)`
- `build_roadmap(product_vision, timeline)`
- `prioritize_features(features_list)`

---

## 2. CopywriterAgent

### Task Types Supportés

#### `landing_page` - Copy de Landing Page
**Input:**
```python
{
    "task_type": "landing_page",
    "context": "Description produit",
    "target_audience": "Audience",
    "goal": "conversion" | "awareness" | "retention",
    "tone": "Tone of voice (optionnel)"
}
```

**Output:** Copy complet:
- Hero Section (headline + subheadline + CTA)
- Problem Section
- Solution Section
- Features Section
- Social Proof
- Pricing/CTA
- FAQ
- 2 variations de headline pour A/B test

#### `email` - Email Marketing
**Input:**
```python
{
    "task_type": "email",
    "context": "Contexte campagne",
    "target_audience": "Audience",
    "goal": "conversion" | "retention" | "activation"
}
```

**Output:** Email complet:
- 3 variations de subject line
- Preview text optimisé mobile
- Opening personnalisé
- Body (150-250 mots)
- CTA actionnable
- P.S.
- [MERGE_TAGS] pour personnalisation

#### `cta` - Call-to-Action Variations
**Input:**
```python
{
    "task_type": "cta",
    "context": "Contexte du CTA",
    "goal": "signup" | "purchase" | "demo"
}
```

**Output:** 10 variations de CTA:
- 3 CTA directs
- 3 CTA orientés bénéfice
- 2 CTA low-commitment
- 2 CTA urgents
- Contexte d'utilisation optimal pour chaque

#### `microcopy` - Microcopy UX
**Input:**
```python
{
    "task_type": "microcopy",
    "context": "Contexte interface",
    "constraints": "Longueur max (optionnel)"
}
```

**Output:** Set complet de microcopy:
- Messages d'erreur (5 variations)
- Messages de succès (3 variations)
- Tooltips (5 variations)
- Empty states (3 variations)
- Loading states (3 variations)
- Tous < 80 caractères pour mobile

#### `ad` - Copy Publicitaire
**Input:**
```python
{
    "task_type": "ad",
    "context": "Description produit",
    "target_audience": "Audience",
    "constraints": "Plateforme (Google, FB, LinkedIn)"
}
```

**Output:** Ads pour toutes plateformes:
- Google Ads (headlines + description)
- Facebook/Instagram Ads
- LinkedIn Ads
- Twitter/X Ads
- Multiples variations par plateforme

#### `seo` - Contenu SEO
**Input:**
```python
{
    "task_type": "seo",
    "context": "Page/contenu",
    "constraints": "Keywords cibles"
}
```

**Output:** Contenu optimisé SEO:
- Meta Title (3 variations)
- Meta Description (2 variations)
- H1 Headline (2 variations)
- H2 Subheadings (5 suggestions)
- URL Slug (2 variations)
- Image Alt Text (5 exemples)

### Méthodes Helper
- `write_landing_page(product_description, audience)`
- `create_email_campaign(campaign_context, audience, objective)`
- `generate_cta_variations(context, objective)`
- `create_microcopy_set(ux_context, character_limit)`
- `set_brand_voice(tone)` - Change le tone of voice

---

## 3. PricingStrategistAgent

### Task Types Supportés

#### `pricing_model` - Choix du Modèle de Pricing
**Input:**
```python
{
    "task_type": "pricing_model",
    "context": "Description produit",
    "target_segment": "SMB" | "Mid-Market" | "Enterprise",
    "competitor_pricing": "Pricing concurrents (optionnel)"
}
```

**Output:** Analyse comparative:
- Freemium (avantages/inconvénients)
- Tiered Pricing
- Usage-Based Pricing
- Flat Rate
- Hybrid
- Recommandation finale avec justification
- Value metric recommandé

#### `tiers` - Création de Tiers de Pricing
**Input:**
```python
{
    "task_type": "tiers",
    "context": "Description produit",
    "target_segment": "Segment de marché",
    "current_pricing": "Pricing actuel (si refonte)"
}
```

**Output:** Structure de 3-4 tiers:
- Tableau comparatif complet
- Prix par tier
- Features et limites par tier
- Psychologie du pricing (anchoring, decoy)
- Feature packaging stratégique
- Recommandation du tier "sweet spot"

#### `metrics` - Analyse Métriques Financières
**Input:**
```python
{
    "task_type": "metrics",
    "context": "Description business",
    "financial_data": {
        "monthly_revenue": 50000,
        "cac": 150,
        "arpu": 50,
        "churn_rate": 5,
        "marketing_spend": 15000
        # etc.
    }
}
```

**Output:** Dashboard de métriques:
- LTV (Lifetime Value) calculé
- CAC (Customer Acquisition Cost)
- LTV:CAC Ratio avec interprétation
- Payback Period (mois)
- MRR & ARR
- Churn Rate
- Net Revenue Retention
- ARPU
- Comparaison aux benchmarks industrie
- Actions prioritaires pour améliorer

#### `optimization` - Optimisation du Pricing
**Input:**
```python
{
    "task_type": "optimization",
    "context": "Description produit",
    "current_pricing": "Structure actuelle",
    "financial_data": {...}
}
```

**Output:** Plan d'optimisation:
- Audit du pricing actuel
- Quick wins (impact rapide)
- Strategic changes (impact élevé)
- A/B tests recommandés (prix, packaging, anchoring)
- Roadmap d'optimisation (6 mois)
- KPIs de succès

#### `expansion` - Stratégie d'Expansion Revenue
**Input:**
```python
{
    "task_type": "expansion",
    "context": "Description produit",
    "current_pricing": "Structure actuelle"
}
```

**Output:** Playbook d'expansion:
- Seat Expansion strategy
- Feature Upsells
- Usage Upsells
- Service Upsells
- Cross-sells
- Triggers d'upsell automatiques
- Metrics d'expansion à tracker
- In-app upsell UX recommendations

### Méthodes Helper
- `design_pricing_model(product_context, target_market)`
- `create_pricing_tiers(product_context, target_market, current_pricing)`
- `analyze_metrics(product_context, financial_data)`
- `optimize_pricing(product_context, current_pricing, financial_data)`
- `build_expansion_strategy(product_context, current_pricing)`

---

## 4. ComplianceOfficerAgent

### Task Types Supportés

#### `audit` - Audit de Conformité
**Input:**
```python
{
    "task_type": "audit",
    "context": "Description système",
    "data_types": ["email", "nom", "IP", ...],
    "jurisdictions": ["GDPR", "CCPA", ...],
    "current_practices": "Pratiques actuelles (optionnel)"
}
```

**Output:** Audit complet:
- GDPR Compliance Checklist
- CCPA/CPRA Compliance Checklist
- Cookies & Consent
- Security Measures
- Vendor Management
- Score de risque (LOW/MEDIUM/HIGH/CRITICAL)
- Top 5 actions prioritaires avec deadlines

#### `policy` - Génération de Privacy Policy
**Input:**
```python
{
    "task_type": "policy",
    "context": "Description service",
    "data_types": ["données collectées"],
    "jurisdictions": ["EU", "US", ...]
}
```

**Output:** Privacy Policy complète:
- Introduction
- Informations collectées (par type)
- Utilisation des données
- Partage des données
- Droits des utilisateurs (GDPR + CCPA)
- Sécurité des données
- Cookies
- Modifications
- Contact & autorité de contrôle
- Langage clair et accessible

#### `data_mapping` - Cartographie des Données
**Input:**
```python
{
    "task_type": "data_mapping",
    "context": "Description système",
    "data_types": ["types de données"]
}
```

**Output:** Data mapping complet:
- Tableau de flux de données (source → stockage → partage → transferts)
- Catégorisation (PII, Special Category, Technical, Usage, Payment)
- Niveau de risque par type
- Systèmes et third parties impliqués
- Data lifecycle (collection → deletion)
- Recommandations (pseudonymisation, encryption, rétention)

#### `consent` - Mécanisme de Consentement
**Input:**
```python
{
    "task_type": "consent",
    "context": "Description service",
    "data_types": ["données nécessitant consentement"]
}
```

**Output:** Spécifications de consent management:
- Cookie consent banner (design + catégories)
- Email marketing consent (double opt-in)
- Data processing consent
- Consent records (schema DB)
- Consent refresh strategy
- UI/UX pour gérer le consentement
- Implementation checklist

#### `rights` - Implémentation Droits Utilisateurs
**Input:**
```python
{
    "task_type": "rights",
    "context": "Description service",
    "jurisdictions": ["GDPR", "CCPA"]
}
```

**Output:** Guide d'implémentation:
- Right to Access (export données)
- Right to Rectification (modifier)
- Right to Erasure (supprimer)
- Right to Data Portability
- Right to Object
- Right to Restriction
- Process workflow complet
- Automation vs intervention manuelle
- SLA (< 30 jours GDPR)
- Metrics à tracker

#### `dpia` - Data Protection Impact Assessment
**Input:**
```python
{
    "task_type": "dpia",
    "context": "Description traitement",
    "data_types": ["données traitées"]
}
```

**Output:** DPIA complète:
- Description du traitement
- Necessity & Proportionality
- Risk Assessment (Likelihood × Severity)
- Risques identifiés (Data Breach, Unauthorized Access, etc.)
- Mitigation Measures
- Consultation (DPO, data subjects, autorité)
- Risk Matrix
- Overall Risk Level
- Decision (Proceed / Mitigate / Consult)
- Action Plan avec deadlines

### Méthodes Helper
- `audit_compliance(product_context, data_types, jurisdictions)`
- `generate_privacy_policy(product_context, data_types, jurisdictions)`
- `map_data_flows(product_context, data_types)`
- `design_consent_mechanism(product_context, data_types)`
- `implement_user_rights(product_context, jurisdictions)`
- `conduct_dpia(product_context, data_types)`
- `add_regulation(regulation)` - Ajouter une réglementation
- `remove_regulation(regulation)` - Retirer une réglementation

---

## 5. GrowthEngineerAgent

### Task Types Supportés

#### `feature_flag` - Implémentation Feature Flags
**Input:**
```python
{
    "task_type": "feature_flag",
    "context": "Description produit",
    "hypothesis": "Description de la feature à flag"
}
```

**Output:** Implémentation complète:
- Schema DB (Supabase SQL)
- Service TypeScript (FeatureFlagService complet)
- React Hook (useFeatureFlag)
- Progressive rollout strategy (5% → 25% → 100%)
- Kill switch (emergency disable)
- Admin dashboard specs
- Monitoring recommendations

#### `ab_test` - Design d'A/B Test
**Input:**
```python
{
    "task_type": "ab_test",
    "context": "Description produit",
    "hypothesis": "Hypothèse à tester",
    "target_metric": "Métrique principale"
}
```

**Output:** A/B test complet:
- Hypothesis framework rempli
- Statistical planning (sample size, duration)
- Implementation (backend + frontend code)
- Tracking & analysis (events, SQL queries)
- Decision framework (when to ship)
- Common pitfalls to avoid
- Reporting template

#### `funnel` - Optimisation de Funnel
**Input:**
```python
{
    "task_type": "funnel",
    "context": "Description du funnel",
    "current_metrics": {
        "landing_to_signup": 0.40,
        "signup_to_verify": 0.80,
        # etc.
    }
}
```

**Output:** Analyse et optimisation:
- Définition du funnel avec conversions
- Drop-off analysis (SQL queries)
- Identification du plus gros drop-off
- Hypothèses d'optimisation par step
- Quick wins (low-effort, high-impact)
- Advanced tactics (segmentation, cohort analysis)
- Monitoring dashboard
- Experiment roadmap
- Expected impact calculation

#### `retention` - Amélioration Rétention
**Input:**
```python
{
    "task_type": "retention",
    "context": "Description produit",
    "current_metrics": {
        "d1_retention": 0.45,
        "d7_retention": 0.28,
        "d30_retention": 0.15,
        # etc.
    }
}
```

**Output:** Stratégie de rétention:
- Retention cohort table (SQL query)
- Key retention metrics (D1, D7, D30)
- Churn analysis (who, when, why)
- 5 stratégies principales:
  1. Improve onboarding
  2. Build habits (Hook Model)
  3. Re-engagement campaigns (triggered emails)
  4. Feature adoption
  5. Community & social
- Retention loops
- Metrics dashboard
- Experimentation roadmap

#### `experiment` - Design d'Expérimentation
**Input:**
```python
{
    "task_type": "experiment",
    "context": "Description produit",
    "hypothesis": "Hypothèse",
    "target_metric": "Métrique"
}
```

**Output:** Expérimentation complète:
- Hypothesis formulation (framework rempli)
- ICE Prioritization (Impact, Confidence, Ease)
- Experiment design (type, variants)
- Sample size & duration calculation
- Success criteria (primary, secondary, guardrails)
- Implementation plan (timeline)
- Tracking implementation (code)
- Analysis plan (statistical tests, SQL)
- Risks & mitigation
- Learnings documentation template

#### `growth_loop` - Création de Growth Loops
**Input:**
```python
{
    "task_type": "growth_loop",
    "context": "Description produit",
    "current_metrics": {
        "k_factor": 0.8,
        "viral_coefficient": 0.5
    }
}
```

**Output:** Growth loops design:
- Types de loops (Viral, Content, Paid, Sales)
- Design YOUR loop (components: input → action → output → incentive → feedback)
- Loop efficiency metrics (cycle time, amplification, retention)
- Implementations:
  - Viral Loop (referral program code complet)
  - Content Loop (UGC + SEO)
  - Paid Loop (unit economics)
- Compounding loops & network effects
- Loop metrics dashboard
- Optimization tactics par type
- Experiment ideas
- Case studies (Dropbox, Pinterest, Stripe)

### Méthodes Helper
- `implement_feature_flag(feature_description, context)`
- `design_ab_test(hypothesis, metric, context)`
- `optimize_funnel(context, current_metrics)`
- `improve_retention(context, current_metrics)`
- `create_experiment(hypothesis, metric, context)`
- `build_growth_loop(context, current_metrics)`

---

## Utilisation Combinée des Agents

Les agents sont conçus pour travailler ensemble dans des workflows:

### Exemple: Lancement d'une Feature
```
1. ProductManager → Génère PRD
2. ComplianceOfficer → Audit conformité
3. Copywriter → Crée messaging
4. GrowthEngineer → Configure feature flag & A/B test
5. PricingStrategist → Défini pricing si nouvelle feature premium
```

### Exemple: Refonte Pricing
```
1. PricingStrategist → Analyse metrics actuelles
2. PricingStrategist → Design nouveaux tiers
3. Copywriter → Crée copy pricing page
4. GrowthEngineer → Setup A/B test ancien vs nouveau pricing
5. ComplianceOfficer → Vérifie transparence des prix (GDPR)
```

### Exemple: Optimisation Onboarding
```
1. ProductManager → User stories onboarding amélioré
2. Copywriter → Microcopy pour chaque step
3. GrowthEngineer → Analyse funnel actuel
4. GrowthEngineer → Design A/B test nouveau flow
5. ComplianceOfficer → Consent mechanism dans l'onboarding
```

---

## Modèles LLM Supportés

Tous les agents supportent n'importe quel modèle disponible via OpenRouter:

**Recommandés:**
- `openai/gpt-4o` (par défaut) - Meilleur rapport qualité/prix
- `anthropic/claude-3.5-sonnet` - Excellent pour raisonnement complexe
- `anthropic/claude-opus-4.5` - Premium, meilleure qualité
- `openai/o1` - Pour tâches complexes nécessitant deep reasoning

**Configuration:**
```python
agent = ProductManagerAgent(
    api_key="your-key",
    model="anthropic/claude-3.5-sonnet"  # ou autre
)
```

---

## Limitations Actuelles

1. **Pas de retry logic** - Si l'appel LLM échoue, pas de retry automatique
2. **Pas de streaming** - Réponses complètes uniquement
3. **Timeout fixe** - 120 secondes max par appel
4. **Mémoire simple** - Liste de messages, pas de RAG ou vector search
5. **Pas de validation** - Les outputs ne sont pas validés structurellement
6. **Pas de caching** - Chaque appel refait l'inférence

## Roadmap

- [ ] Ajouter retry avec exponential backoff
- [ ] Support streaming responses
- [ ] Validation Pydantic des outputs
- [ ] Caching des résultats (Redis)
- [ ] Métriques (latency, token usage, coût)
- [ ] Templates de prompts customizables
- [ ] Multi-agent workflows automatiques
- [ ] Integration avec orchestrateur central
