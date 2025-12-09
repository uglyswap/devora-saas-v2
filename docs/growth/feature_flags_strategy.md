# Feature Flags Strategy - Devora

**Platform:** PostHog (self-hosted)
**Last Updated:** December 9, 2025

---

## Overview

Feature flags enable gradual rollouts, A/B testing, and instant rollbacks without deployments.

---

## Flag Types

| Type | Purpose | Example |
|------|---------|--------|
| **Release** | Gradual rollout | `release-vue-support` |
| **Experiment** | A/B testing | `exp-pricing-page-v2` |
| **Permission** | Feature access | `perm-enterprise-sso` |
| **Kill Switch** | Emergency disable | `kill-ai-generation` |
| **Ops** | Operational control | `ops-maintenance-mode` |

---

## Naming Convention

```
{category}-{feature-name}-{type}
```

**Examples:**
- `release-vue-support`
- `exp-onboarding-wizard`
- `perm-api-access`
- `kill-stripe-checkout`
- `ops-debug-logging`

---

## Rollout Strategy

**Standard Rollout (5 phases):**

| Phase | Percentage | Duration | Criteria to Proceed |
|-------|------------|----------|--------------------|
| 1 | 0% (internal) | 2 days | No bugs |
| 2 | 5% | 3 days | Error rate < 0.1% |
| 3 | 25% | 5 days | No performance impact |
| 4 | 50% | 7 days | Positive metrics |
| 5 | 100% | - | Stable |

---

## Implementation

**Backend (Python):**
```python
from posthog import Posthog

posthog = Posthog(project_api_key='phc_xxx')

def is_feature_enabled(flag_name: str, user_id: str) -> bool:
    return posthog.feature_enabled(flag_name, user_id)
```

**Frontend (React):**
```tsx
import { useFeatureFlag } from 'posthog-react';

function MyComponent() {
  const isVueEnabled = useFeatureFlag('release-vue-support');
  if (isVueEnabled) return <VueGenerator />;
  return <ReactGenerator />;
}
```

---

## Emergency Procedures

**Kill Switch Activation:**
1. Go to PostHog → Feature Flags
2. Find the kill switch flag
3. Set to 0% (disabled for all)
4. Notify #incidents Slack channel

---

**Contact:** devops@devora.io | Slack: #feature-flags
