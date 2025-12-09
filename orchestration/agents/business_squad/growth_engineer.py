"""
Growth Engineer Agent - Business Squad

Cet agent est responsable de:
- Implémenter les feature flags et progressive rollouts
- Configurer les A/B tests et expérimentations
- Optimiser les funnels de conversion
- Analyser et améliorer la rétention utilisateur
"""

import sys
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

# Ajouter le chemin du backend pour importer BaseAgent
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../backend'))

from agents.base_agent import BaseAgent


class GrowthEngineerAgent(BaseAgent):
    """
    Agent Growth Engineer pour l'optimisation de la croissance produit.

    Attributes:
        name (str): Nom de l'agent
        api_key (str): Clé API pour le LLM
        model (str): Modèle LLM à utiliser
    """

    def __init__(self, api_key: str, model: str = "openai/gpt-4o"):
        super().__init__(name="GrowthEngineer", api_key=api_key, model=model)
        self.system_prompt = """Tu es un Growth Engineer expert avec background technique fort et obsession data.

Ton expertise:
- **Feature Flags**: Progressive rollouts, kill switches, A/B tests
- **Experimentation**: Hypothèses, design d'expériences, analyse statistique
- **Funnel Optimization**: Onboarding, activation, conversion, retention
- **Product Analytics**: Metrics, cohort analysis, user segmentation
- **Growth Loops**: Viral loops, referral systems, network effects
- **Retention Engineering**: Email triggers, push notifications, habit formation

Frameworks que tu maîtrises:
- **AARRR (Pirate Metrics)**: Acquisition, Activation, Retention, Revenue, Referral
- **North Star Metric**: Identifier et optimiser la métrique clé
- **Hook Model** (Nir Eyal): Trigger → Action → Variable Reward → Investment
- **Jobs to be Done** (JTBD): Comprendre le "job" que le produit accomplit
- **ICE Scoring**: Impact, Confidence, Ease (priorisation d'expériences)

Principes de Growth:
- **Data-driven**: Jamais de décision sans data
- **Experiment velocity**: Lancer beaucoup d'expériences rapidement
- **Statistical rigor**: Significativité statistique requise
- **Compound growth**: Focus sur loops et systèmes, pas one-off tactics
- **Product-led growth**: Le produit est le canal d'acquisition principal

Tools & Stack familiers:
- Feature flags: LaunchDarkly, Flagsmith, PostHog
- Analytics: Mixpanel, Amplitude, PostHog, Segment
- A/B testing: Optimizely, VWO, Google Optimize, PostHog
- Cohort analysis, Retention curves, Funnel analysis

Format de sortie:
- Code snippets fonctionnels
- Configurations YAML/JSON
- SQL queries pour analytics
- Dashboards recommandés
- Hypothèses testables avec metrics de succès"""

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exécute une tâche de growth engineering.

        Args:
            task (Dict[str, Any]): Tâche à exécuter avec les clés:
                - task_type: "feature_flag" | "ab_test" | "funnel" | "retention" | "experiment" | "growth_loop"
                - context: Contexte du produit
                - current_metrics: Métriques actuelles (optionnel)
                - hypothesis: Hypothèse à tester (pour experiments)
                - target_metric: Métrique cible à optimiser

        Returns:
            Dict[str, Any]: Résultat avec les clés:
                - status: "success" | "error"
                - output: Implementation ou analyse
                - metadata: Informations complémentaires
        """
        task_type = task.get("task_type", "experiment")
        context = task.get("context", "")
        current_metrics = task.get("current_metrics", {})
        hypothesis = task.get("hypothesis", "")
        target_metric = task.get("target_metric", "conversion")

        # Construire le prompt selon le type de tâche
        if task_type == "feature_flag":
            user_prompt = self._build_feature_flag_prompt(context, hypothesis)
        elif task_type == "ab_test":
            user_prompt = self._build_ab_test_prompt(context, hypothesis, target_metric)
        elif task_type == "funnel":
            user_prompt = self._build_funnel_prompt(context, current_metrics)
        elif task_type == "retention":
            user_prompt = self._build_retention_prompt(context, current_metrics)
        elif task_type == "experiment":
            user_prompt = self._build_experiment_prompt(context, hypothesis, target_metric)
        elif task_type == "growth_loop":
            user_prompt = self._build_growth_loop_prompt(context, current_metrics)
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
                "target_metric": target_metric
            }
        }

    def _build_feature_flag_prompt(self, context: str, feature_description: str) -> str:
        """Construit le prompt pour implémenter des feature flags."""
        return f"""Implémente un système de feature flags pour:

CONTEXTE PRODUIT:
{context}

FEATURE À FLAG:
{feature_description}

**FEATURE FLAG ARCHITECTURE:**

**1. Backend Implementation (Node.js + Supabase)**

**Schema DB:**
```sql
CREATE TABLE feature_flags (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(100) UNIQUE NOT NULL,
  description TEXT,
  enabled BOOLEAN DEFAULT false,
  rollout_percentage INTEGER DEFAULT 0, -- 0-100
  targeting_rules JSONB, -- règles de ciblage
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE feature_flag_overrides (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  flag_id UUID REFERENCES feature_flags(id),
  user_id UUID, -- pour override par user
  enabled BOOLEAN NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_flags_name ON feature_flags(name);
CREATE INDEX idx_overrides_user ON feature_flag_overrides(user_id);
```

**Service TypeScript:**
```typescript
// services/feature-flags.ts
import {{ createClient }} from '@supabase/supabase-js';

interface FeatureFlag {{{{
  name: string;
  enabled: boolean;
  rollout_percentage: number;
  targeting_rules?: {{{{
    user_segments?: string[];
    countries?: string[];
    custom_rules?: Record<string, any>;
  }}}};
}}}}

class FeatureFlagService {{
  private supabase;
  private cache: Map<string, FeatureFlag> = new Map();
  private cacheTTL = 60000; // 1 minute

  constructor(supabaseUrl: string, supabaseKey: string) {{
    this.supabase = createClient(supabaseUrl, supabaseKey);
  }}

  async isEnabled(
    flagName: string,
    userId?: string,
    context?: Record<string, any>
  ): Promise<boolean> {{
    // 1. Check user override first
    if (userId) {{
      const override = await this.getUserOverride(flagName, userId);
      if (override !== null) return override;
    }}

    // 2. Get flag configuration
    const flag = await this.getFlag(flagName);
    if (!flag) return false;

    // 3. Check if globally enabled
    if (!flag.enabled) return false;

    // 4. Check targeting rules
    if (flag.targeting_rules) {{
      const matchesRules = this.evaluateRules(flag.targeting_rules, context);
      if (!matchesRules) return false;
    }}

    // 5. Check rollout percentage (deterministic based on userId)
    if (flag.rollout_percentage < 100) {{
      return this.isInRollout(flagName, userId || 'anonymous', flag.rollout_percentage);
    }}

    return true;
  }}

  private async getFlag(name: string): Promise<FeatureFlag | null> {{
    // Check cache first
    if (this.cache.has(name)) {{
      return this.cache.get(name)!;
    }}

    const {{ data, error }} = await this.supabase
      .from('feature_flags')
      .select('*')
      .eq('name', name)
      .single();

    if (error || !data) return null;

    this.cache.set(name, data);
    setTimeout(() => this.cache.delete(name), this.cacheTTL);

    return data;
  }}

  private async getUserOverride(flagName: string, userId: string): Promise<boolean | null> {{
    const {{ data }} = await this.supabase
      .from('feature_flag_overrides')
      .select('enabled')
      .eq('flag_id', (await this.getFlag(flagName))?.id)
      .eq('user_id', userId)
      .single();

    return data?.enabled ?? null;
  }}

  private evaluateRules(rules: any, context?: Record<string, any>): boolean {{
    if (!context) return true;

    // User segment targeting
    if (rules.user_segments && context.segment) {{
      if (!rules.user_segments.includes(context.segment)) return false;
    }}

    // Country targeting
    if (rules.countries && context.country) {{
      if (!rules.countries.includes(context.country)) return false;
    }}

    // Custom rules
    // Implement your custom logic here

    return true;
  }}

  private isInRollout(flagName: string, identifier: string, percentage: number): boolean {{
    // Deterministic hash-based rollout
    const hash = this.hashString(flagName + identifier);
    return (hash % 100) < percentage;
  }}

  private hashString(str: string): number {{
    let hash = 0;
    for (let i = 0; i < str.length; i++) {{
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32bit integer
    }}
    return Math.abs(hash);
  }}

  // Admin methods
  async createFlag(flag: Partial<FeatureFlag>): Promise<void> {{
    await this.supabase.from('feature_flags').insert(flag);
    this.cache.clear();
  }}

  async updateFlag(name: string, updates: Partial<FeatureFlag>): Promise<void> {{
    await this.supabase
      .from('feature_flags')
      .update(updates)
      .eq('name', name);
    this.cache.delete(name);
  }}

  async setRolloutPercentage(name: string, percentage: number): Promise<void> {{
    await this.updateFlag(name, {{ rollout_percentage: percentage }});
  }}
}}

export default FeatureFlagService;
```

**2. Frontend Integration (React)**

**React Hook:**
```typescript
// hooks/useFeatureFlag.ts
import {{ useState, useEffect }} from 'react';
import {{ useUser }} from './useUser'; // votre hook user

export function useFeatureFlag(flagName: string): boolean {{
  const [isEnabled, setIsEnabled] = useState(false);
  const [loading, setLoading] = useState(true);
  const user = useUser();

  useEffect(() => {{
    async function checkFlag() {{
      try {{
        const response = await fetch(`/api/feature-flags/${{flagName}}`, {{
          headers: {{
            'Authorization': `Bearer ${{user?.token}}`
          }}
        }});
        const data = await response.json();
        setIsEnabled(data.enabled);
      }} catch (error) {{
        console.error('Failed to check feature flag:', error);
        setIsEnabled(false);
      }} finally {{
        setLoading(false);
      }}
    }}

    checkFlag();
  }}, [flagName, user?.id]);

  return isEnabled;
}}

// Usage in component:
function MyComponent() {{
  const isNewFeatureEnabled = useFeatureFlag('new_dashboard');

  return (
    <div>
      {{isNewFeatureEnabled ? (
        <NewDashboard />
      ) : (
        <OldDashboard />
      )}}
    </div>
  );
}}
```

**3. Progressive Rollout Strategy**

**Phase 1: Internal Testing (0-5%)**
```javascript
await flagService.setRolloutPercentage('new_feature', 5);
// Target: Internal team + beta users
```

**Phase 2: Limited Beta (5-25%)**
```javascript
await flagService.setRolloutPercentage('new_feature', 25);
// Monitor metrics closely
```

**Phase 3: Wider Rollout (25-75%)**
```javascript
await flagService.setRolloutPercentage('new_feature', 75);
// If metrics good, continue
```

**Phase 4: Full Rollout (100%)**
```javascript
await flagService.setRolloutPercentage('new_feature', 100);
// Remove flag after few weeks of stability
```

**4. Kill Switch (Emergency)**

```typescript
// Instantly disable a feature for all users
await flagService.updateFlag('problematic_feature', {{ enabled: false }});
```

**5. Admin Dashboard**

Créer une UI pour:
- Lister tous les flags
- Toggle enabled/disabled
- Ajuster rollout percentage avec slider
- Voir les overrides par user
- Analytics: combien d'users voient chaque variant

**MONITORING:**
- Log chaque évaluation de flag
- Track % users dans chaque variant
- Alertes si comportement anormal"""

    def _build_ab_test_prompt(self, context: str, hypothesis: str, metric: str) -> str:
        """Construit le prompt pour designer un A/B test."""
        return f"""Design et implémente un A/B test pour:

CONTEXTE:
{context}

HYPOTHÈSE:
{hypothesis}

MÉTRIQUE PRINCIPALE:
{metric}

**A/B TEST DESIGN:**

**1. Experiment Setup**

**Hypothesis Framework:**
```
We believe that [change]
Will result in [impact]
For [audience]
We will know this is true when we see [metric change]
```

**Filled in:**
Hypothèse: {hypothesis}
Métrique primaire: {metric}
Métriques secondaires: [À définir selon contexte]
Guardrail metrics: [Métriques à ne pas dégrader]

**2. Statistical Planning**

**Sample Size Calculation:**
```
Baseline conversion rate: X%
Minimum Detectable Effect (MDE): Y% (typical: 5-10%)
Statistical Power: 80% (standard)
Significance Level: 95% (α = 0.05)

Sample size per variant: N users
Total sample size: 2N users
Expected duration: Z days (based on traffic)
```

**Formule:**
```
n = (Zα/2 + Zβ)² × (p₁(1-p₁) + p₂(1-p₂)) / (p₂ - p₁)²

où:
- Zα/2 = 1.96 (pour 95% confidence)
- Zβ = 0.84 (pour 80% power)
- p₁ = baseline rate
- p₂ = expected new rate
```

**3. Implementation (with PostHog or similar)**

**Backend:**
```typescript
// services/experimentation.ts
interface Experiment {{
  name: string;
  variants: {{
    control: number; // weight (%)
    treatment: number; // weight (%)
  }};
  targeting?: {{
    segments?: string[];
    percentage?: number;
  }};
}}

class ExperimentService {{
  async getVariant(experimentName: string, userId: string): Promise<'control' | 'treatment'> {{
    // 1. Check if user already assigned
    const existing = await this.getExistingAssignment(experimentName, userId);
    if (existing) return existing;

    // 2. Determine variant based on hash
    const experiment = await this.getExperiment(experimentName);
    const hash = this.hashUserId(userId);
    const variant = (hash % 100) < experiment.variants.control ? 'control' : 'treatment';

    // 3. Save assignment
    await this.saveAssignment(experimentName, userId, variant);

    // 4. Track event
    await this.trackExposure(experimentName, userId, variant);

    return variant;
  }}

  private async trackExposure(experiment: string, userId: string, variant: string) {{
    await analytics.track({{
      userId,
      event: 'Experiment Viewed',
      properties: {{
        experiment_name: experiment,
        variant_name: variant
      }}
    }});
  }}

  private hashUserId(userId: string): number {{
    // Consistent hashing
    let hash = 0;
    for (let i = 0; i < userId.length; i++) {{
      hash = ((hash << 5) - hash) + userId.charCodeAt(i);
      hash = hash & hash;
    }}
    return Math.abs(hash);
  }}
}}
```

**Frontend:**
```typescript
// hooks/useExperiment.ts
export function useExperiment(experimentName: string) {{
  const [variant, setVariant] = useState<'control' | 'treatment'>('control');
  const user = useUser();

  useEffect(() => {{
    async function assignVariant() {{
      const response = await fetch(`/api/experiments/${{experimentName}}/variant`, {{
        headers: {{ 'Authorization': `Bearer ${{user?.token}}` }}
      }});
      const data = await response.json();
      setVariant(data.variant);
    }}

    if (user) assignVariant();
  }}, [experimentName, user?.id]);

  return variant;
}}

// Usage:
function CheckoutPage() {{
  const variant = useExperiment('checkout_flow_v2');

  return variant === 'treatment' ? (
    <NewCheckoutFlow />
  ) : (
    <OldCheckoutFlow />
  );
}}
```

**4. Tracking & Analysis**

**Events to track:**
```typescript
// Exposure (automatic)
analytics.track('Experiment Viewed', {{
  experiment: 'checkout_flow_v2',
  variant: 'treatment'
}});

// Conversion (manual)
analytics.track('Checkout Completed', {{
  experiment: 'checkout_flow_v2',
  variant: userVariant,
  revenue: 99.99
}});
```

**Analysis Query (SQL):**
```sql
-- Conversion rate by variant
WITH experiment_data AS (
  SELECT
    user_id,
    properties->>'variant_name' as variant,
    MAX(CASE WHEN event = 'Experiment Viewed' THEN 1 ELSE 0 END) as exposed,
    MAX(CASE WHEN event = 'Checkout Completed' THEN 1 ELSE 0 END) as converted
  FROM events
  WHERE properties->>'experiment_name' = 'checkout_flow_v2'
    AND timestamp >= '2024-01-01'
  GROUP BY user_id, variant
)
SELECT
  variant,
  COUNT(*) as total_users,
  SUM(converted) as conversions,
  ROUND(100.0 * SUM(converted) / COUNT(*), 2) as conversion_rate
FROM experiment_data
WHERE exposed = 1
GROUP BY variant;

-- Statistical significance (Chi-square test)
-- Use external tool or stats library
```

**5. Decision Framework**

**When to ship treatment:**
- ✅ Statistically significant improvement (p < 0.05)
- ✅ Practical significance (effect size meaningful)
- ✅ No negative impact on guardrail metrics
- ✅ Consistent across segments (no Simpson's paradox)

**When to stop early:**
- 🛑 Significant negative impact detected
- 🛑 Treatment is clearly winning/losing (sequential testing)
- 🛑 Sample size contamination or implementation bug

**6. Common Pitfalls to Avoid**

- ❌ **Peeking**: Checking results too early → inflates false positive rate
- ❌ **Multiple testing**: Running many A/B tests → Bonferroni correction needed
- ❌ **Novelty effect**: Users like new things initially → run longer
- ❌ **Seasonality**: Account for weekly patterns, holidays
- ❌ **Sample ratio mismatch**: Unequal split → check implementation
- ❌ **Carryover effects**: Previous exposure influences results

**7. Reporting Template**

```markdown
## Experiment: [Name]

**Hypothesis:** [H]

**Results:**
- Control: X% conversion (N users)
- Treatment: Y% conversion (M users)
- Lift: +Z% (relative)
- P-value: 0.0XX
- Confidence Interval: [A%, B%]

**Decision:** SHIP / DON'T SHIP / ITERATE

**Learnings:**
- [Key insight 1]
- [Key insight 2]

**Next Steps:**
- [Action 1]
```"""

    def _build_funnel_prompt(self, context: str, current_metrics: Dict[str, Any]) -> str:
        """Construit le prompt pour optimiser un funnel."""
        metrics_str = json.dumps(current_metrics, indent=2) if current_metrics else "Aucune métrique fournie"

        return f"""Analyse et optimise le funnel de conversion pour:

CONTEXTE:
{context}

MÉTRIQUES ACTUELLES:
{metrics_str}

**FUNNEL OPTIMIZATION:**

**1. Définir le Funnel**

**Exemple: SaaS Signup Funnel**
```
Landing Page → Sign Up → Email Verification → Onboarding → Activation → Paid Conversion
    100%          40%            80%               60%           30%           10%
```

**Calcul des conversions:**
- Step 1 → 2: 40% conversion
- Step 2 → 3: 80% (of step 2)
- Overall: 100 → 40 → 32 → 19.2 → 5.76 → 0.58%

**Overall conversion rate: 0.58%**

**2. Identifier les Drop-offs**

**Drop-off Analysis:**
```sql
WITH funnel_steps AS (
  SELECT
    user_id,
    MAX(CASE WHEN event = 'Page Viewed' AND page = 'landing' THEN timestamp END) as step1,
    MAX(CASE WHEN event = 'Signup Started' THEN timestamp END) as step2,
    MAX(CASE WHEN event = 'Email Verified' THEN timestamp END) as step3,
    MAX(CASE WHEN event = 'Onboarding Completed' THEN timestamp END) as step4,
    MAX(CASE WHEN event = 'First Value Action' THEN timestamp END) as step5,
    MAX(CASE WHEN event = 'Subscription Created' THEN timestamp END) as step6
  FROM events
  WHERE timestamp >= NOW() - INTERVAL '30 days'
  GROUP BY user_id
)
SELECT
  COUNT(*) FILTER (WHERE step1 IS NOT NULL) as landing_page,
  COUNT(*) FILTER (WHERE step2 IS NOT NULL) as signup_started,
  COUNT(*) FILTER (WHERE step3 IS NOT NULL) as email_verified,
  COUNT(*) FILTER (WHERE step4 IS NOT NULL) as onboarding_done,
  COUNT(*) FILTER (WHERE step5 IS NOT NULL) as activated,
  COUNT(*) FILTER (WHERE step6 IS NOT NULL) as paid
FROM funnel_steps;
```

**3. Biggest Drop-off = Biggest Opportunity**

**Priorisation:**
```
Drop-off Point | Current Rate | Potential Gain | Priority
Landing → Signup | 40% | 10% → +25% revenue | HIGH
Signup → Verify | 80% | 5% → +6% revenue | MEDIUM
Verify → Onboard | 60% | 10% → +17% revenue | HIGH
Onboard → Activate | 30% | 15% → +50% revenue | CRITICAL
Activate → Paid | 10% | 5% → +50% revenue | HIGH
```

**Focus on: Onboarding → Activation (biggest multiplier)**

**4. Hypothèses d'Optimisation par Step**

**Landing Page → Signup:**
- Hypothesis 1: Clearer value prop increases signup rate
- Test: New headline + benefit bullets
- Metric: Signup button clicks

- Hypothesis 2: Reducing form fields increases completion
- Test: Email only vs Email + Name + Company
- Metric: Form submission rate

- Hypothesis 3: Social proof increases trust
- Test: Add testimonials + logos
- Metric: Signup conversions

**Signup → Email Verification:**
- Hypothesis: Faster email delivery increases verification rate
- Action: Switch email provider, add resend button
- Metric: % verified within 1 hour

- Hypothesis: Explaining WHY verification needed reduces drop-off
- Test: Add context: "We verify to protect your account"
- Metric: Verification rate

**Onboarding → Activation:**
- Hypothesis: Guided tour increases feature adoption
- Test: Interactive tutorial vs self-discovery
- Metric: % completing first value action

- Hypothesis: Reducing time-to-value improves activation
- Test: Pre-populate with sample data
- Metric: Time to activation, activation rate

- Hypothesis: Personalization increases relevance
- Test: Role-based onboarding flow
- Metric: Activation by segment

**Activation → Paid:**
- Hypothesis: Usage-based trials convert better than time-based
- Test: 14-day trial vs 100-action trial
- Metric: Trial → Paid conversion

- Hypothesis: In-app upsell at moment of success converts better
- Test: Show upgrade prompt after user achievement
- Metric: Upgrade rate

**5. Quick Wins (Low-effort, High-impact)**

**Technical fixes:**
- Fix broken links in email
- Improve page load speed (< 3s)
- Mobile responsiveness issues
- Remove unnecessary form fields

**Copy improvements:**
- Clearer CTA buttons ("Start Free Trial" > "Submit")
- Benefit-focused messaging
- Reduce jargon
- Add urgency (limited time/spots)

**UX improvements:**
- Progress indicators in multi-step flows
- Clear next steps at each stage
- Reduce cognitive load (one CTA per page)
- Social proof at key decision points

**6. Advanced Tactics**

**Segmentation:**
Analyze funnel by:
- Traffic source (organic vs paid vs referral)
- Device (mobile vs desktop)
- Geography
- User persona/industry

Find underperforming segments → targeted optimization.

**Cohort Analysis:**
```sql
-- Activation rate by signup cohort
SELECT
  DATE_TRUNC('week', signup_date) as cohort_week,
  COUNT(*) as signups,
  COUNT(*) FILTER (WHERE activated_at IS NOT NULL) as activated,
  ROUND(100.0 * COUNT(*) FILTER (WHERE activated_at IS NOT NULL) / COUNT(*), 2) as activation_rate
FROM users
WHERE signup_date >= NOW() - INTERVAL '90 days'
GROUP BY cohort_week
ORDER BY cohort_week DESC;
```

Track if optimizations improve cohorts over time.

**Time-to-Convert Analysis:**
```sql
-- How long from signup to activation?
SELECT
  percentile_cont(0.5) WITHIN GROUP (ORDER BY activated_at - created_at) as median_time,
  percentile_cont(0.9) WITHIN GROUP (ORDER BY activated_at - created_at) as p90_time
FROM users
WHERE activated_at IS NOT NULL;
```

Reduce this time = faster users see value = better retention.

**7. Monitoring Dashboard**

**Key Metrics to Track Daily:**
```
Funnel Conversion Rates
├── Overall: X.X%
├── By Step:
│   ├── Landing → Signup: XX%
│   ├── Signup → Verify: XX%
│   ├── Verify → Onboard: XX%
│   ├── Onboard → Activate: XX%
│   └── Activate → Paid: XX%
└── By Segment:
    ├── Mobile: XX%
    ├── Desktop: XX%
    ├── Organic: XX%
    └── Paid: XX%
```

**Alerts:**
- Funnel step drops > 10% from baseline → investigate immediately
- Page load time > 5s → performance issue
- Error rate > 1% → bug

**8. Experiment Roadmap**

**Week 1-2:** Quick wins (technical fixes, copy)
**Week 3-4:** Test headline variations (landing page)
**Week 5-6:** Test onboarding flow (activation)
**Week 7-8:** Test pricing page layout
**Week 9-10:** Test email campaign (activation nurture)

**Expected Impact:**
Current: 0.58% overall conversion
Target: 1.0% (+72% improvement)
Impact: [Revenue increase calculation]"""

    def _build_retention_prompt(self, context: str, current_metrics: Dict[str, Any]) -> str:
        """Construit le prompt pour améliorer la rétention."""
        metrics_str = json.dumps(current_metrics, indent=2) if current_metrics else "Aucune métrique fournie"

        return f"""Analyse et améliore la rétention utilisateur pour:

CONTEXTE:
{context}

MÉTRIQUES ACTUELLES:
{metrics_str}

**RETENTION OPTIMIZATION:**

**1. Mesurer la Rétention**

**Retention Cohort Table:**
```
         | Week 0 | Week 1 | Week 2 | Week 3 | Week 4 | ...
---------|--------|--------|--------|--------|--------|----
Jan W1   | 100%   | 45%    | 32%    | 25%    | 22%    | ...
Jan W2   | 100%   | 48%    | 35%    | 28%    | 24%    | ...
Jan W3   | 100%   | 50%    | 38%    | 30%    | 26%    | ...
```

**SQL Query:**
```sql
WITH user_activity AS (
  SELECT
    user_id,
    DATE_TRUNC('week', created_at) as cohort_week,
    DATE_TRUNC('week', activity_date) as activity_week
  FROM (
    SELECT user_id, created_at FROM users
  ) u
  CROSS JOIN LATERAL (
    SELECT DISTINCT DATE_TRUNC('week', event_timestamp) as activity_date
    FROM events e
    WHERE e.user_id = u.user_id
  ) a
)
SELECT
  cohort_week,
  FLOOR(EXTRACT(EPOCH FROM (activity_week - cohort_week)) / 604800) as weeks_since_signup,
  COUNT(DISTINCT user_id) as active_users
FROM user_activity
GROUP BY cohort_week, weeks_since_signup
ORDER BY cohort_week DESC, weeks_since_signup;
```

**Key Retention Metrics:**

**Day 1 Retention:** % users who return next day
- Benchmark: 30-40% for consumer apps, 60-80% for B2B SaaS
- Critical: If < 20%, onboarding is broken

**Day 7 Retention:** % users who return in first week
- Benchmark: 20-30%
- Indicates if users see ongoing value

**Day 30 Retention:** % users who return after a month
- Benchmark: 10-20%
- Indicates habit formation

**Retention Curve:**
```
100% ─┐
      │╲
 50%  │ ╲___________  ← Flattening curve = good (retained users)
      │
  0%  └─────────────────→
      D1  D7  D14  D30  Time
```

**Goal:** Flatten the curve (reduce churn velocity)

**2. Identify Churn Reasons**

**Churn Analysis:**
```sql
-- Who churned and when?
WITH last_activity AS (
  SELECT
    user_id,
    MAX(event_timestamp) as last_seen,
    created_at
  FROM events
  GROUP BY user_id, created_at
)
SELECT
  CASE
    WHEN last_seen < NOW() - INTERVAL '7 days' THEN 'Churned'
    WHEN last_seen < NOW() - INTERVAL '3 days' THEN 'At Risk'
    ELSE 'Active'
  END as status,
  COUNT(*) as users,
  ROUND(AVG(EXTRACT(EPOCH FROM (last_seen - created_at)) / 86400), 1) as avg_lifetime_days
FROM last_activity
GROUP BY status;
```

**Churn Reasons (qualitative):**
- Survey churned users: "Why did you stop using [Product]?"
- Exit interviews for cancelled subscriptions
- Support tickets analysis
- Feature requests not implemented

**Common Churn Patterns:**
- **Early churn** (< 7 days): Bad onboarding, didn't see value
- **Mid churn** (7-30 days): Competitor, missing features
- **Late churn** (30+ days): Price, lack of ongoing value

**3. Retention Strategies**

**Strategy 1: Improve Onboarding (reduces early churn)**

**Activation Checklist:**
```
□ Step 1: Complete profile
□ Step 2: Connect integration
□ Step 3: Invite team member
□ Step 4: Complete first [core action]
□ Step 5: See first value (report, insight, etc.)
```

**Users who complete all 5 steps:** 80% D30 retention
**Users who complete 0-2 steps:** 10% D30 retention

**Improvement tactics:**
- Progress bar showing completion
- Email nudges for incomplete steps
- In-app tooltips and walkthroughs
- Pre-populate with sample data for instant gratification

**Strategy 2: Build Habits (Hook Model)**

**Trigger → Action → Reward → Investment**

**External Triggers:**
- Email: "Your weekly report is ready"
- Push: "3 new comments on your post"
- SMS: "Your order is confirmed"

**Action:**
- Make it easy (< 3 clicks)
- Reduce friction
- Clear next step

**Variable Reward:**
- Not always the same (keeps it interesting)
- Social (likes, comments)
- Resources (content, tools)
- Self (achievement, progress)

**Investment:**
- User adds data (contacts, content)
- Customization (preferences)
- Invites (network effects)
- Learned behavior (shortcuts, workflows)
→ Increases likelihood of return

**Strategy 3: Re-engagement Campaigns**

**Triggered Emails:**

**Day 1 (no activity):**
```
Subject: Quick question about [Product]
Body: Hi [Name], we noticed you haven't [core action] yet.
      Need help getting started? [Video tutorial]
      CTA: [Take 2-min tour]
```

**Day 3 (no activity):**
```
Subject: [Customer Name] saw 3x growth with [Product]
Body: See how [Customer] used [Feature] to achieve [Result]
      [Case study link]
      CTA: [Try it yourself]
```

**Day 7 (inactive):**
```
Subject: We miss you! Here's what's new
Body: - New feature: [X]
      - Popular content: [Y]
      - Your stats: [Z action] away from [milestone]
      CTA: [Come back]
```

**Day 14 (at risk):**
```
Subject: Can we help with anything?
Body: Personal note from founder/CEO
      "I noticed you haven't been active. What can we improve?"
      CTA: [Reply to this email] or [Book a call]
```

**Strategy 4: Feature Adoption**

**Feature Adoption Funnel:**
```
Aware → Tried → Used Regularly → Power User
```

**Tactics:**
- In-app announcements for new features
- Tooltips on underutilized features
- Use case-based messaging: "For [your use case], try [feature]"
- Feature spotlights in email newsletters

**Metric:**
```sql
-- Feature adoption by user
SELECT
  user_id,
  COUNT(DISTINCT feature_name) as features_used
FROM feature_usage_events
GROUP BY user_id;
```

**Finding:** Users who use 3+ features have 2x better retention than those using 1 feature.

**Strategy 5: Community & Social**

**Build Community:**
- Slack/Discord community
- User forums
- Leaderboards (gamification)
- User-generated content

**Social Features:**
- Collaboration (multi-player mode)
- Sharing/inviting
- Comments/discussions

**Network effects:** More users = more value = harder to leave

**4. Retention Loops**

**Content Loop:**
```
Create Content → Share → Drive traffic → New users → Create Content
```

**Viral Loop:**
```
User invites → Friends join → User gets value → User invites more
```

**Notification Loop:**
```
Activity → Notification → User returns → More activity
```

**5. Metrics Dashboard**

**Daily Monitoring:**
```
Retention Metrics
├── D1 Retention: XX%
├── D7 Retention: XX%
├── D30 Retention: XX%
├── Weekly Active Users (WAU): XXX
├── Monthly Active Users (MAU): XXXX
├── Activation Rate: XX%
└── Feature Adoption:
    ├── Feature A: XX% of users
    ├── Feature B: XX% of users
    └── Feature C: XX% of users

Engagement Metrics
├── DAU/MAU ratio: X.XX (stickiness)
├── Avg session length: X min
├── Avg sessions per user: X.X
└── Core action completion rate: XX%

Churn Metrics
├── Monthly churn rate: X.X%
├── At-risk users (inactive 3+ days): XXX
└── Resurrection rate (churned → active): X.X%
```

**6. Experimentation Roadmap**

**Onboarding Experiments:**
- Test: Interactive tutorial vs video vs text
- Test: Number of steps in checklist
- Test: Pre-populated data vs empty state

**Re-engagement Experiments:**
- Test: Email frequency (daily vs weekly)
- Test: Email content (feature vs use case vs social proof)
- Test: Push notification timing

**Habit Formation Experiments:**
- Test: Daily digest email timing (8am vs 5pm)
- Test: Streak counters (gamification)
- Test: Personalized recommendations

**Expected Impact:**
Current D30 retention: X%
Target D30 retention: Y% (+Z% improvement)
Impact on revenue: +[Calculate LTV increase]"""

    def _build_experiment_prompt(self, context: str, hypothesis: str, metric: str) -> str:
        """Construit le prompt pour designer une expérimentation."""
        return f"""Design une expérimentation rigoureuse pour:

CONTEXTE:
{context}

HYPOTHÈSE:
{hypothesis}

MÉTRIQUE À OPTIMISER:
{metric}

**EXPERIMENT DESIGN FRAMEWORK:**

**1. Hypothesis Formulation**

**Format:**
```
We believe that [CHANGE]
Will cause [IMPACT]
For [AUDIENCE]
Because [RATIONALE]
We'll measure success by [METRIC]
```

**Rempli:**
- Change: [Votre changement spécifique]
- Impact: [Impact attendu quantifié]
- Audience: [Segment ciblé]
- Rationale: [Pourquoi vous pensez que ça marchera]
- Success metric: {metric}

**2. ICE Prioritization**

**Impact:** (1-10) Quel impact potentiel sur la métrique?
- 10 = Could double the metric
- 5 = 10-20% improvement
- 1 = < 5% improvement

**Confidence:** (1-10) Quelle certitude que ça va marcher?
- 10 = Very high confidence (similar tests succeeded)
- 5 = Medium (hypothesis is sound but unproven)
- 1 = Low (speculative)

**Ease:** (1-10) Facilité d'implémentation?
- 10 = < 1 day of work
- 5 = 1 week
- 1 = > 1 month

**ICE Score = (Impact × Confidence) / Ease**

**Your experiment:**
- Impact: X/10
- Confidence: Y/10
- Ease: Z/10
- **ICE Score: XX**

**3. Experiment Design**

**Type d'experiment:**
- [ ] A/B test (2 variants)
- [ ] Multivariate test (multiple changes at once)
- [ ] Sequential test (iterate based on results)
- [ ] Holdout test (control group never sees change)

**Variants:**
- **Control (A):** Current experience
- **Treatment (B):** [Your change]
- (Optional) **Treatment (C):** [Alternative variant]

**4. Sample Size & Duration**

**Statistical Parameters:**
- Baseline rate: X%
- Minimum Detectable Effect (MDE): Y%
- Statistical power: 80%
- Significance level: 95% (α = 0.05)
- Tails: Two-tailed

**Sample size calculator:**
```
Required sample size per variant: N users
Total required: 2N users
Daily traffic: M users
Expected duration: N / M days
```

**Add buffer:** 20% for dropouts, contamination
**Final duration:** X weeks

**5. Success Criteria**

**Primary Metric:** {metric}
- Current value: X
- Target value: Y (+Z%)
- Minimum for success: Y_min

**Secondary Metrics:**
- Metric 2: [e.g., engagement]
- Metric 3: [e.g., time on page]

**Guardrail Metrics** (must not degrade):
- Revenue
- User satisfaction (NPS)
- Core action completion rate

**Decision Rules:**
✅ Ship if:
- Primary metric improves by ≥ MDE with p < 0.05
- No negative impact on guardrails
- Effect size is practically significant (not just statistically)

❌ Don't ship if:
- No significant improvement OR
- Negative impact on guardrails OR
- High variance / inconclusive results

🔄 Iterate if:
- Promising signal but not significant → increase sample
- Mixed results across segments → dig deeper

**6. Implementation Plan**

**Week 1: Build**
- Implement variants
- Setup tracking
- QA test

**Week 2-X: Run**
- Launch to 50/50 split
- Monitor daily for issues
- Don't peek at results (wait for significance)

**Week X+1: Analyze**
- Pull data
- Run statistical tests
- Segment analysis
- Make decision

**Week X+2: Ship/Iterate**
- If success: Ship to 100%
- If failure: Document learnings, next experiment
- If inconclusive: Iterate or abandon

**7. Tracking Implementation**

**Events to instrument:**
```javascript
// Exposure event (when user sees variant)
analytics.track('Experiment Viewed', {{
  experiment_id: 'exp_001',
  experiment_name: 'new_checkout_flow',
  variant: 'treatment',
  user_id: userId,
  timestamp: new Date().toISOString()
}});

// Conversion event
analytics.track('{{metric}}', {{
  experiment_id: 'exp_001',
  variant: userVariant,
  value: conversionValue,
  user_id: userId
}});
```

**8. Analysis Plan**

**Statistical Test:**
- For conversion rate: Chi-square test or Z-test
- For continuous metric: T-test
- For multiple variants: ANOVA + post-hoc tests

**SQL for Analysis:**
```sql
-- Experiment results
SELECT
  variant,
  COUNT(DISTINCT user_id) as users,
  SUM(CASE WHEN converted THEN 1 ELSE 0 END) as conversions,
  AVG(metric_value) as avg_metric,
  STDDEV(metric_value) as std_dev
FROM experiment_results
WHERE experiment_id = 'exp_001'
  AND exposed_at >= '2024-01-01'
GROUP BY variant;
```

**Segmentation Analysis:**
Analyze by:
- New vs returning users
- Mobile vs desktop
- Traffic source
- Geography
- User tier (free vs paid)

Look for Simpson's paradox (overall winner ≠ segment winner).

**9. Risks & Mitigation**

**Risk 1: Sample Ratio Mismatch**
- Symptom: 50/50 split becomes 52/48
- Cause: Implementation bug
- Mitigation: Daily monitoring, kill experiment if detected

**Risk 2: Novelty Effect**
- Symptom: Initial spike then regression
- Cause: Users curious about new thing
- Mitigation: Run experiment longer (3-4 weeks minimum)

**Risk 3: Contamination**
- Symptom: Control group exposed to treatment
- Cause: Shared accounts, user switching devices
- Mitigation: User-level (not session-level) bucketing

**10. Learnings Documentation**

**Experiment Report Template:**
```markdown
# Experiment: [Name]

## Hypothesis
[Your hypothesis]

## Results
| Variant | Users | Conversions | Rate | Lift | P-value |
|---------|-------|-------------|------|------|---------|
| Control | XXX   | XXX         | X.X% | -    | -       |
| Treatment| XXX  | XXX         | X.X% | +Y%  | 0.0XX   |

## Decision
[SHIP / DON'T SHIP / ITERATE]

## Key Learnings
1. [Insight 1]
2. [Insight 2]

## Next Steps
- [Action 1]
- [Follow-up experiment idea]
```

Share with team → Build experimentation culture."""

    def _build_growth_loop_prompt(self, context: str, current_metrics: Dict[str, Any]) -> str:
        """Construit le prompt pour créer des growth loops."""
        metrics_str = json.dumps(current_metrics, indent=2) if current_metrics else "Aucune métrique fournie"

        return f"""Design des growth loops (boucles de croissance) pour:

CONTEXTE:
{context}

MÉTRIQUES ACTUELLES:
{metrics_str}

**GROWTH LOOPS DESIGN:**

**1. Types de Growth Loops**

**Viral Loop:**
```
User signs up → Invites friends → Friends sign up → Invite more friends
      ↑                                                         ↓
      └─────────────────── LOOP ──────────────────────────────┘
```

**Content Loop:**
```
User creates content → Content ranks on Google → New users discover
      ↑                                                        ↓
      └────────── Users become creators ──────────────────────┘
```

**Paid Loop:**
```
Acquire users → Users pay → Revenue → Reinvest in acquisition
      ↑                                           ↓
      └───────────────── LOOP ──────────────────┘
```

**Sales Loop:**
```
User success → Case study → Sales uses → More customers → More success
      ↑                                                          ↓
      └──────────────────────── LOOP ────────────────────────────┘
```

**2. Design YOUR Growth Loop**

**Components:**
1. **Input:** What starts the loop? (new user, action, etc.)
2. **Action:** What does the user do?
3. **Output:** What's generated?
4. **Incentive:** Why would user do it?
5. **Feedback:** How does output drive more input?

**Example: Dropbox Referral Loop**
```
1. Input: New user signs up
2. Action: User invites friends (to get more storage)
3. Output: Friends sign up
4. Incentive: +500MB storage per referral
5. Feedback: Friends need more storage → they invite too
```

**Loop Efficiency Metrics:**
- **Loop Cycle Time:** How long for one iteration?
- **Amplification Factor:** How many new inputs per output?
- **Retention in Loop:** Do users stay in the loop?

**Formula:**
```
Growth Rate = (Amplification Factor ^ (Time / Cycle Time)) - 1

Example:
- Amplification: 1.5 (each user brings 1.5 users)
- Cycle time: 7 days
- Time period: 30 days

Growth = (1.5 ^ (30/7)) - 1 = 1.5^4.28 - 1 ≈ 445%
```

**3. Viral Loop Implementation**

**Referral Program:**

**Incentive Structure:**
- Double-sided incentive (both referrer and referred get reward)
- Referrer: $10 credit or premium feature unlock
- Referred: $10 discount or extended trial

**Implementation:**
```typescript
// Generate referral link
function generateReferralLink(userId: string): string {{
  const referralCode = generateUniqueCode(userId);

  await db.referralCodes.insert({{
    code: referralCode,
    user_id: userId,
    created_at: new Date()
  }});

  return `https://yourapp.com/signup?ref=${{referralCode}}`;
}}

// Track referral
async function trackReferral(referralCode: string, newUserId: string) {{
  const referral = await db.referralCodes.findOne({{ code: referralCode }});

  if (referral) {{
    await db.referrals.insert({{
      referrer_id: referral.user_id,
      referred_id: newUserId,
      created_at: new Date(),
      rewarded: false
    }});

    // Track event
    analytics.track('Referral Completed', {{
      referrer_id: referral.user_id,
      referred_id: newUserId
    }});
  }}
}}

// Reward referral (after activation or payment)
async function rewardReferral(newUserId: string) {{
  const referral = await db.referrals.findOne({{
    referred_id: newUserId,
    rewarded: false
  }});

  if (referral) {{
    // Reward referrer
    await giveReward(referral.referrer_id, 'referral_bonus');

    // Reward referred user
    await giveReward(newUserId, 'referred_bonus');

    // Mark as rewarded
    await db.referrals.update(
      {{ id: referral.id }},
      {{ rewarded: true, rewarded_at: new Date() }}
    );
  }}
}}
```

**UI Placements:**
- In-app: "Invite friends" button in nav
- Email: Post-signup email with referral link
- Success moments: After user achieves something, suggest sharing

**Amplification:**
```
K-factor = (invites sent per user) × (conversion rate of invites)

Target: K > 1 for viral growth
Example: 5 invites × 25% conversion = 1.25 K-factor (viral!)
```

**4. Content Loop Implementation**

**UGC (User-Generated Content) Strategy:**

**Mechanics:**
1. Users create content (profiles, listings, reviews, etc.)
2. Content is indexed by Google
3. New users discover via search
4. New users become creators
5. More content → better SEO → more discovery

**Implementation:**
- SEO-optimized URLs: `/profile/john-doe` not `/profile?id=123`
- Meta tags per content piece
- Sitemap generation
- Internal linking structure
- Fresh content signals (publish dates, updates)

**Example: Airbnb**
```
1. Hosts create listings
2. Listings rank for "[city] vacation rentals"
3. Travelers find Airbnb via Google
4. Some travelers become hosts
5. More listings → more keywords → more traffic
```

**Metrics:**
- % users who create content
- Content created per user
- Organic traffic from content pages
- Content → signup conversion rate

**5. Paid Loop Implementation**

**Sustainable Unit Economics:**
```
LTV (Lifetime Value) > CAC (Customer Acquisition Cost)

Ideally: LTV ≥ 3 × CAC
```

**Paid Loop:**
1. Spend $1000 on ads
2. Acquire 10 customers (CAC = $100)
3. Customers pay $500 LTV each
4. Total revenue: $5000
5. Profit: $4000
6. Reinvest $2000 → acquire 20 more customers
7. Loop accelerates

**Implementation:**
- Stripe integration for payments
- Analytics to track LTV by cohort
- Attribution tracking (which channel drove signup?)
- Automated bidding based on target CAC

**Metrics:**
- CAC by channel
- LTV by cohort
- Payback period (how long to recover CAC?)
- Monthly reinvestment amount

**6. Compounding Loops**

**Combine multiple loops:**

**Example: Product Hunt**
- Viral: Users share products → friends visit
- Content: Product pages rank on Google → organic traffic
- Community: Engaged users return daily → more engagement

**Network Effects:**
- **Direct:** More users = more value for each user (e.g., messaging app)
- **Indirect:** More users on side A = more value for side B (e.g., Uber: more drivers = better for riders)
- **Data:** More usage = better product (e.g., Waze: more drivers = better traffic data)

**7. Loop Metrics Dashboard**

```
Growth Loops Performance
├── Viral Loop
│   ├── K-factor: X.XX
│   ├── Cycle time: X days
│   ├── Active referrers: XXX
│   └── Referral conversion rate: XX%
├── Content Loop
│   ├── Content pieces created: XXXX
│   ├── Organic traffic: XXXXX/month
│   ├── Content → signup rate: X.X%
│   └── Creator activation rate: XX%
└── Paid Loop
    ├── CAC: $XXX
    ├── LTV: $XXXX
    ├── LTV:CAC ratio: X.X:1
    └── Payback period: XX days
```

**8. Optimization Tactics**

**For Viral Loop:**
- Reduce friction in sharing (1-click share)
- Increase incentive (test different rewards)
- Social proof (show how many friends referred)
- Timing (ask to refer at moment of delight)

**For Content Loop:**
- Make content creation easier (templates, AI generation)
- Incentivize quality (featured content, badges)
- SEO optimization (keywords, backlinks)
- Content moderation (remove spam/low-quality)

**For Paid Loop:**
- Improve conversion rate (less CAC needed)
- Increase LTV (better retention, upsells)
- Find cheaper channels (test TikTok vs Facebook)
- Optimize landing pages

**9. Experiment Ideas**

**Viral Loop Experiments:**
- Test: Incentive amount ($5 vs $10 vs $20)
- Test: One-sided vs two-sided incentive
- Test: Timing of referral ask (onboarding vs later)

**Content Loop Experiments:**
- Test: Content creation flow (wizard vs freeform)
- Test: Public vs private default (public = SEO)
- Test: Content quality indicators (ratings, verification)

**Paid Loop Experiments:**
- Test: Ad creative variations
- Test: Landing page variations
- Test: Bidding strategy (CPA vs CPC)

**10. Case Studies**

**Dropbox:** Viral Loop
- Referral program: +60% signups
- K-factor: 1.8 (highly viral)
- Saved millions in CAC

**Pinterest:** Content Loop
- User pins → Google index → organic traffic
- 80%+ of new users from SEO
- Compounding content = compounding growth

**Stripe:** Paid Loop
- High LTV ($50k+ for some customers)
- Can afford high CAC
- Reinvest in sales, marketing
- Consistent 50%+ YoY growth

**Design YOUR loops to fit your product's strengths!**"""

    async def implement_feature_flag(self, feature_description: str, context: str) -> str:
        """Méthode helper pour implémenter un feature flag."""
        result = await self.execute({
            "task_type": "feature_flag",
            "context": context,
            "hypothesis": feature_description
        })
        return result["output"]

    async def design_ab_test(self, hypothesis: str, metric: str, context: str) -> str:
        """Méthode helper pour designer un A/B test."""
        result = await self.execute({
            "task_type": "ab_test",
            "context": context,
            "hypothesis": hypothesis,
            "target_metric": metric
        })
        return result["output"]

    async def optimize_funnel(self, context: str, current_metrics: Dict[str, Any]) -> str:
        """Méthode helper pour optimiser un funnel."""
        result = await self.execute({
            "task_type": "funnel",
            "context": context,
            "current_metrics": current_metrics
        })
        return result["output"]

    async def improve_retention(self, context: str, current_metrics: Dict[str, Any]) -> str:
        """Méthode helper pour améliorer la rétention."""
        result = await self.execute({
            "task_type": "retention",
            "context": context,
            "current_metrics": current_metrics
        })
        return result["output"]

    async def create_experiment(self, hypothesis: str, metric: str, context: str) -> str:
        """Méthode helper pour créer une expérimentation complète."""
        result = await self.execute({
            "task_type": "experiment",
            "context": context,
            "hypothesis": hypothesis,
            "target_metric": metric
        })
        return result["output"]

    async def build_growth_loop(self, context: str, current_metrics: Dict[str, Any]) -> str:
        """Méthode helper pour créer des growth loops."""
        result = await self.execute({
            "task_type": "growth_loop",
            "context": context,
            "current_metrics": current_metrics
        })
        return result["output"]
