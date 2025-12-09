# A/B Testing Strategy - Devora

**Version:** 1.0
**Last Updated:** December 9, 2025
**Platform:** PostHog (self-hosted)

---

## Overview

This document defines our A/B testing framework for data-driven product decisions.

**Goals:**
- Increase free-to-paid conversion rate (target: 5% → 8%)
- Improve feature adoption
- Optimize onboarding flow
- Maximize revenue per user

---

## Testing Framework

### PIE Scoring (Prioritization)

| Factor | Weight | Description |
|--------|--------|-------------|
| **P**otential | 40% | Expected impact on key metric |
| **I**mportance | 30% | Traffic volume affected |
| **E**ase | 30% | Implementation effort |

**Score = (P × 0.4) + (I × 0.3) + (E × 0.3)**

---

## 2025 Experiment Calendar

### Q1 2025 (Jan-Mar)

| Experiment | Hypothesis | Metric | Status |
|------------|------------|--------|--------|
| **EXP-001**: Pricing page layout | 3-column vs 2-column | Conversion | Planned |
| **EXP-002**: Free trial length | 7 vs 14 days | Activation | Planned |
| **EXP-003**: Onboarding flow | Wizard vs checklist | Day-7 retention | Planned |

### Q2-Q4: Additional experiments planned for CTA copy, feature discovery, upgrade prompts

---

## Statistical Requirements

- **Minimum sample size:** 1,000 visitors per variant
- **Confidence level:** 95%
- **Minimum detectable effect:** 10%
- **Test duration:** Minimum 14 days

---

## Tools & Implementation

**PostHog Feature Flags:**
```typescript
const variant = posthog.getFeatureFlag('pricing-page-layout');
if (variant === 'three-column') {
  return <ThreeColumnPricing />;
}
return <TwoColumnPricing />;
```

---

**Contact:** growth@devora.io | Slack: #growth-experiments
