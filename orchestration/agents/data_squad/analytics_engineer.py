"""
Analytics Engineer Agent - Specialized in analytics implementation and event tracking.

This agent is responsible for:
- PostHog/Mixpanel analytics setup
- Event tracking implementation
- Metrics and KPI definitions
- Dashboard creation
- A/B testing configuration
- Conversion funnel analysis
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from backend.agents.base_agent import BaseAgent
from typing import Dict, Any, List
import json
import re
import logging

logger = logging.getLogger(__name__)


class AnalyticsEngineerAgent(BaseAgent):
    """
    Expert agent for analytics and metrics implementation.

    Specializations:
    - PostHog analytics configuration
    - Mixpanel event tracking
    - Custom analytics dashboards
    - A/B testing and feature flags
    - Conversion funnel optimization
    - User behavior analytics
    - Product metrics and KPIs
    - Data visualization
    - Real-time analytics
    """

    def __init__(self, api_key: str, model: str = "openai/gpt-4o"):
        super().__init__("AnalyticsEngineer", api_key, model)

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute analytics engineering tasks.

        Args:
            task: Dictionary containing:
                - features: List of features to track
                - metrics: KPIs and metrics to measure
                - platform: Analytics platform (posthog, mixpanel, etc.)
                - tracking_plan: Event tracking requirements

        Returns:
            Dictionary containing:
                - success: Boolean indicating success
                - files: Implementation files
                - tracking_events: Event definitions
                - dashboards: Dashboard configurations
                - raw_response: Full LLM response
        """
        features = task.get("features", [])
        metrics = task.get("metrics", [])
        platform = task.get("platform", "posthog")
        tracking_plan = task.get("tracking_plan", {})

        system_prompt = self._get_system_prompt(platform)
        context = self._build_context(features, metrics, platform, tracking_plan)

        messages = [{"role": "user", "content": context}]

        logger.info(f"[AnalyticsEngineer] Setting up {platform} analytics for {len(features)} features...")

        response = await self.call_llm(messages, system_prompt)

        files = self._parse_code_blocks(response)
        events = self._extract_events(response)

        logger.info(f"[AnalyticsEngineer] Generated {len(files)} files and {len(events)} event definitions")

        return {
            "success": True,
            "files": files,
            "tracking_events": events,
            "platform": platform,
            "raw_response": response,
            "agent": self.name
        }

    async def create_tracking_plan(self, features: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a comprehensive tracking plan for features.

        Args:
            features: List of features with user interactions

        Returns:
            Tracking plan with event definitions
        """
        system_prompt = """You are an analytics expert creating tracking plans.

A good tracking plan includes:
1. **Event naming convention**: Consistent, descriptive names
2. **Event properties**: All relevant context
3. **User properties**: User attributes to track
4. **Page views**: Critical pages to track
5. **Conversion events**: Key business metrics
6. **Frequency**: How often events fire

Use this format:
- Events: `Object_Action` (e.g., `Project_Created`, `User_SignedUp`)
- Properties: snake_case (e.g., `project_id`, `user_role`)
- Boolean properties: `is_` prefix (e.g., `is_premium`)

Output as JSON tracking plan."""

        context = f"""Create a tracking plan for these features:

{json.dumps(features, indent=2)}

Include:
1. All user interaction events
2. Required event properties
3. User properties to identify
4. Critical conversion events
5. Page view tracking
6. Event frequency expectations
"""

        messages = [{"role": "user", "content": context}]
        response = await self.call_llm(messages, system_prompt)

        return {
            "success": True,
            "tracking_plan": self._parse_json_response(response),
            "raw_response": response
        }

    async def create_dashboard(self, metrics: List[str], dashboard_type: str = "product") -> Dict[str, Any]:
        """
        Create analytics dashboard configuration.

        Args:
            metrics: List of metrics to visualize
            dashboard_type: Type of dashboard (product, marketing, executive)

        Returns:
            Dashboard configuration and queries
        """
        system_prompt = """You are a data visualization expert.

Create dashboards that:
1. Tell a story with data
2. Use appropriate chart types
3. Include filters and breakdowns
4. Show trends over time
5. Highlight important metrics

Dashboard types:
- **product**: User engagement, feature adoption, retention
- **marketing**: Acquisition, activation, referral
- **executive**: Revenue, growth, key business metrics

Output dashboard JSON config and SQL queries for metrics."""

        context = f"""Create a {dashboard_type} dashboard for these metrics:

{json.dumps(metrics, indent=2)}

Include:
1. Dashboard layout and sections
2. Visualizations (chart types)
3. SQL queries for each metric
4. Filters and date ranges
5. Drill-down capabilities
"""

        messages = [{"role": "user", "content": context}]
        response = await self.call_llm(messages, system_prompt)
        files = self._parse_code_blocks(response)

        return {
            "success": True,
            "files": files,
            "dashboard_type": dashboard_type,
            "raw_response": response
        }

    async def setup_ab_test(self, experiment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Set up A/B test configuration.

        Args:
            experiment: Experiment definition with variants and metrics

        Returns:
            A/B test implementation code
        """
        system_prompt = """You are an experimentation expert.

Design A/B tests that:
1. Have clear hypothesis and success metrics
2. Proper variant allocation (usually 50/50)
3. Statistical significance checks
4. Minimum sample size calculations
5. Implementation code for tracking
6. Analysis queries

Include:
- Feature flag configuration
- Event tracking for variants
- Success metric calculations
- Statistical significance tests
"""

        context = f"""Set up A/B test for this experiment:

{json.dumps(experiment, indent=2)}

Provide:
1. Feature flag configuration
2. Variant tracking implementation
3. Success metric queries
4. Sample size recommendations
5. Analysis dashboard
"""

        messages = [{"role": "user", "content": context}]
        response = await self.call_llm(messages, system_prompt)
        files = self._parse_code_blocks(response)

        return {
            "success": True,
            "files": files,
            "experiment": experiment.get("name"),
            "raw_response": response
        }

    async def analyze_funnel(self, funnel_steps: List[str]) -> Dict[str, Any]:
        """
        Create funnel analysis queries and visualizations.

        Args:
            funnel_steps: Ordered list of funnel steps

        Returns:
            Funnel analysis queries and drop-off insights
        """
        system_prompt = """You are a conversion optimization expert.

Analyze funnels to identify:
1. Drop-off points between steps
2. Conversion rates at each step
3. Time between steps
4. User segments with different behavior
5. Optimization opportunities

Provide:
- SQL queries for funnel analysis
- Drop-off rate calculations
- Cohort analysis
- Segment breakdowns
- Recommendations
"""

        context = f"""Analyze this conversion funnel:

Steps: {' → '.join(funnel_steps)}

Provide:
1. Overall funnel conversion query
2. Step-by-step drop-off analysis
3. Time-to-convert analysis
4. Segment comparison queries
5. Optimization recommendations
"""

        messages = [{"role": "user", "content": context}]
        response = await self.call_llm(messages, system_prompt)
        files = self._parse_code_blocks(response)

        return {
            "success": True,
            "files": files,
            "funnel_steps": funnel_steps,
            "raw_response": response
        }

    def _get_system_prompt(self, platform: str = "posthog") -> str:
        """Get the specialized system prompt for analytics engineering."""
        platform_configs = {
            "posthog": {
                "sdk": "@posthog/react",
                "init": "posthog.init(apiKey, { api_host: host })",
                "event": "posthog.capture('event_name', { properties })"
            },
            "mixpanel": {
                "sdk": "mixpanel-browser",
                "init": "mixpanel.init(token)",
                "event": "mixpanel.track('event_name', { properties })"
            }
        }

        config = platform_configs.get(platform, platform_configs["posthog"])

        return f"""You are an expert Analytics Engineer specializing in product analytics.

## Core Expertise:
- Product analytics implementation ({platform})
- Event tracking and instrumentation
- Metrics and KPI definitions
- A/B testing and experimentation
- User behavior analysis
- Conversion funnel optimization
- Dashboard design and data visualization
- Real-time analytics and monitoring

## Technology Stack:
- **Analytics Platform**: {platform}
- **Frontend SDK**: {config['sdk']}
- **Backend**: Server-side event tracking
- **Database**: PostgreSQL for custom analytics
- **Visualization**: Built-in dashboards + custom queries

## Analytics Implementation Patterns:

### 1. Event Tracking Setup:

```typescript
// filepath: lib/analytics.ts
import posthog from 'posthog-js';

export const analytics = {{
  init: () => {{
    if (typeof window !== 'undefined') {{
      posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY!, {{
        api_host: process.env.NEXT_PUBLIC_POSTHOG_HOST || 'https://app.posthog.com',
        loaded: (posthog) => {{
          if (process.env.NODE_ENV === 'development') posthog.debug();
        }}
      }});
    }}
  }},

  identify: (userId: string, traits?: Record<string, any>) => {{
    posthog.identify(userId, traits);
  }},

  track: (event: string, properties?: Record<string, any>) => {{
    posthog.capture(event, properties);
  }},

  page: (name?: string, properties?: Record<string, any>) => {{
    posthog.capture('$pageview', {{ page: name, ...properties }});
  }},

  reset: () => {{
    posthog.reset();
  }}
}};
```

### 2. Event Naming Convention:

```typescript
// filepath: lib/analytics/events.ts
/**
 * Analytics Event Catalog
 *
 * Naming: Object_Action (e.g., User_SignedUp, Project_Created)
 * Properties: snake_case (e.g., project_id, user_role)
 */

export const AnalyticsEvents = {{
  // Authentication
  USER_SIGNED_UP: 'User_SignedUp',
  USER_LOGGED_IN: 'User_LoggedIn',
  USER_LOGGED_OUT: 'User_LoggedOut',

  // Core Actions
  PROJECT_CREATED: 'Project_Created',
  PROJECT_UPDATED: 'Project_Updated',
  PROJECT_DELETED: 'Project_Deleted',
  PROJECT_SHARED: 'Project_Shared',

  // Conversion Events
  UPGRADE_CLICKED: 'Upgrade_Clicked',
  CHECKOUT_STARTED: 'Checkout_Started',
  PAYMENT_COMPLETED: 'Payment_Completed',

  // Feature Usage
  FEATURE_USED: 'Feature_Used',
  EXPORT_COMPLETED: 'Export_Completed',
}} as const;

export type AnalyticsEvent = typeof AnalyticsEvents[keyof typeof AnalyticsEvents];

// Event properties interfaces
export interface UserSignedUpProperties {{
  method: 'email' | 'google' | 'github';
  referral_source?: string;
  utm_campaign?: string;
}}

export interface ProjectCreatedProperties {{
  project_id: string;
  project_name: string;
  template_used?: string;
  is_first_project: boolean;
}}
```

### 3. React Hooks for Tracking:

```typescript
// filepath: hooks/useAnalytics.ts
import {{ useEffect }} from 'react';
import {{ analytics }} from '@/lib/analytics';
import {{ AnalyticsEvents }} from '@/lib/analytics/events';

export function usePageTracking() {{
  useEffect(() => {{
    analytics.page(window.location.pathname);
  }}, []);
}}

export function useEventTracking() {{
  return {{
    track: (event: string, properties?: Record<string, any>) => {{
      analytics.track(event, properties);
    }},

    trackProjectCreated: (project: any) => {{
      analytics.track(AnalyticsEvents.PROJECT_CREATED, {{
        project_id: project.id,
        project_name: project.name,
        is_first_project: !project.user.has_projects
      }});
    }},

    trackFeatureUsage: (feature: string) => {{
      analytics.track(AnalyticsEvents.FEATURE_USED, {{
        feature_name: feature,
        timestamp: new Date().toISOString()
      }});
    }}
  }};
}}
```

### 4. Server-Side Tracking:

```typescript
// filepath: lib/analytics/server.ts
import {{ PostHog }} from 'posthog-node';

const posthog = new PostHog(
  process.env.POSTHOG_API_KEY!,
  {{ host: process.env.POSTHOG_HOST }}
);

export const serverAnalytics = {{
  track: async (userId: string, event: string, properties?: Record<string, any>) => {{
    posthog.capture({{
      distinctId: userId,
      event,
      properties
    }});

    await posthog.shutdown(); // Flush events
  }},

  identify: async (userId: string, traits: Record<string, any>) => {{
    posthog.identify({{
      distinctId: userId,
      properties: traits
    }});
  }}
}};
```

### 5. Metrics Queries (SQL):

```sql
-- filepath: analytics/queries/metrics.sql

-- Daily Active Users (DAU)
SELECT
  date_trunc('day', timestamp) as date,
  count(DISTINCT user_id) as dau
FROM analytics_events
WHERE event_name = '$pageview'
  AND timestamp >= now() - interval '30 days'
GROUP BY date
ORDER BY date DESC;

-- Conversion Funnel
WITH funnel AS (
  SELECT
    user_id,
    MAX(CASE WHEN event_name = 'User_SignedUp' THEN 1 ELSE 0 END) as signed_up,
    MAX(CASE WHEN event_name = 'Project_Created' THEN 1 ELSE 0 END) as created_project,
    MAX(CASE WHEN event_name = 'Payment_Completed' THEN 1 ELSE 0 END) as converted
  FROM analytics_events
  WHERE timestamp >= now() - interval '30 days'
  GROUP BY user_id
)
SELECT
  COUNT(*) FILTER (WHERE signed_up = 1) as signups,
  COUNT(*) FILTER (WHERE created_project = 1) as created_projects,
  COUNT(*) FILTER (WHERE converted = 1) as conversions,
  ROUND(100.0 * COUNT(*) FILTER (WHERE created_project = 1) / NULLIF(COUNT(*) FILTER (WHERE signed_up = 1), 0), 2) as activation_rate,
  ROUND(100.0 * COUNT(*) FILTER (WHERE converted = 1) / NULLIF(COUNT(*) FILTER (WHERE signed_up = 1), 0), 2) as conversion_rate
FROM funnel;

-- Feature Adoption
SELECT
  properties->>'feature_name' as feature,
  COUNT(DISTINCT user_id) as unique_users,
  COUNT(*) as total_uses,
  ROUND(AVG(COUNT(*)) OVER (), 2) as avg_uses_per_feature
FROM analytics_events
WHERE event_name = 'Feature_Used'
  AND timestamp >= now() - interval '7 days'
GROUP BY feature
ORDER BY unique_users DESC;

-- Retention Cohorts
SELECT
  date_trunc('week', signup_date) as cohort_week,
  COUNT(DISTINCT user_id) as cohort_size,
  COUNT(DISTINCT CASE WHEN weeks_since_signup >= 1 THEN user_id END) as week_1,
  COUNT(DISTINCT CASE WHEN weeks_since_signup >= 2 THEN user_id END) as week_2,
  ROUND(100.0 * COUNT(DISTINCT CASE WHEN weeks_since_signup >= 1 THEN user_id END) / COUNT(DISTINCT user_id), 2) as week_1_retention
FROM (
  SELECT
    user_id,
    MIN(timestamp) as signup_date,
    EXTRACT(WEEK FROM AGE(timestamp, MIN(timestamp) OVER (PARTITION BY user_id))) as weeks_since_signup
  FROM analytics_events
  WHERE event_name = 'User_SignedUp'
  GROUP BY user_id, timestamp
) cohorts
GROUP BY cohort_week
ORDER BY cohort_week DESC;
```

### 6. A/B Testing:

```typescript
// filepath: lib/experiments.ts
import {{ posthog }} from '@/lib/analytics';

export function useExperiment(experimentKey: string) {{
  const variant = posthog.getFeatureFlag(experimentKey);

  useEffect(() => {{
    if (variant) {{
      posthog.capture('$experiment_started', {{
        experiment: experimentKey,
        variant
      }});
    }}
  }}, [experimentKey, variant]);

  return variant;
}}

// Usage
function CheckoutButton() {{
  const variant = useExperiment('checkout_button_test');

  return (
    <button className={{variant === 'control' ? 'btn-blue' : 'btn-green'}}>
      {{variant === 'control' ? 'Buy Now' : 'Get Started'}}
    </button>
  );
}}
```

## Dashboard Configuration:

```json
// filepath: analytics/dashboards/product_metrics.json
{{
  "name": "Product Metrics Dashboard",
  "sections": [
    {{
      "title": "Activation",
      "metrics": [
        {{
          "name": "Sign-ups",
          "query": "signup_count",
          "visualization": "line_chart",
          "timeframe": "30d"
        }},
        {{
          "name": "Activation Rate",
          "query": "activation_rate",
          "visualization": "percentage",
          "target": 40
        }}
      ]
    }},
    {{
      "title": "Engagement",
      "metrics": [
        {{
          "name": "DAU",
          "query": "daily_active_users",
          "visualization": "area_chart"
        }},
        {{
          "name": "Feature Usage",
          "query": "feature_adoption",
          "visualization": "bar_chart"
        }}
      ]
    }}
  ]
}}
```

## Output Format:

Provide files with clear paths:

```typescript
// filepath: lib/analytics.ts
[Analytics initialization and core functions]
```

```typescript
// filepath: lib/analytics/events.ts
[Event catalog and type definitions]
```

```typescript
// filepath: hooks/useAnalytics.ts
[React hooks for tracking]
```

```sql
-- filepath: analytics/queries/metrics.sql
[SQL queries for dashboards]
```

```json
// filepath: analytics/dashboards/config.json
[Dashboard configurations]
```

## Best Practices:
1. **Consistent Naming**: Use Object_Action pattern
2. **Type Safety**: Define event property interfaces
3. **Privacy**: Respect user privacy, allow opt-out
4. **Performance**: Batch events, async tracking
5. **Testing**: Test tracking in development mode
6. **Documentation**: Document all events in tracking plan
7. **Validation**: Validate event properties
8. **Monitoring**: Monitor event delivery and errors
9. **Compliance**: Follow GDPR/CCPA requirements
10. **Analysis**: Regular data quality checks

Generate production-ready analytics implementation with comprehensive tracking."""

    def _build_context(self, features: List[str], metrics: List[str],
                      platform: str, tracking_plan: Dict[str, Any]) -> str:
        """Build the context message for the LLM."""
        return f"""Implement comprehensive analytics for this application.

## Features to Track:
{json.dumps(features, indent=2)}

## Key Metrics & KPIs:
{json.dumps(metrics, indent=2)}

## Analytics Platform: {platform}

## Tracking Plan:
{json.dumps(tracking_plan, indent=2) if tracking_plan else "Create a comprehensive tracking plan"}

## Deliverables Required:

1. **Analytics Setup** (lib/analytics.ts)
   - Initialize {platform}
   - Core tracking functions
   - User identification
   - Page view tracking

2. **Event Catalog** (lib/analytics/events.ts)
   - All trackable events
   - Event property interfaces
   - Type-safe event tracking

3. **React Hooks** (hooks/useAnalytics.ts)
   - usePageTracking
   - useEventTracking
   - Custom tracking hooks

4. **Server-Side Tracking** (lib/analytics/server.ts)
   - Backend event tracking
   - Batch processing
   - Error handling

5. **Metrics Queries** (analytics/queries/)
   - DAU/MAU calculations
   - Conversion funnels
   - Retention cohorts
   - Feature adoption

6. **Dashboards** (analytics/dashboards/)
   - Product metrics dashboard
   - Business metrics dashboard
   - User engagement dashboard

7. **A/B Testing** (lib/experiments.ts)
   - Feature flag implementation
   - Experiment tracking
   - Variant allocation

8. **Tracking Plan Documentation** (ANALYTICS.md)
   - All events documented
   - Property definitions
   - Dashboard descriptions
   - Testing guidelines

Generate complete, production-ready analytics implementation."""

    def _parse_code_blocks(self, response: str) -> List[Dict[str, str]]:
        """Parse code blocks from LLM response."""
        files = []

        pattern = r'```(\w+)?\n(?:--\s*filepath:\s*(.+?)\n|\/\/\s*filepath:\s*(.+?)\n|#\s*filepath:\s*(.+?)\n)?([\s\S]*?)```'

        matches = re.findall(pattern, response)

        for match in matches:
            language, sql_path, ts_path, py_path, code = match
            code = code.strip()

            if not code:
                continue

            filepath = sql_path or ts_path or py_path

            if not filepath:
                first_line = code.split('\n')[0] if code else ''
                if 'filepath:' in first_line.lower():
                    filepath = first_line.split('filepath:')[-1].strip()
                    code = '\n'.join(code.split('\n')[1:]).strip()

            if not filepath:
                ext_map = {
                    'typescript': 'ts', 'ts': 'ts', 'javascript': 'js',
                    'sql': 'sql', 'json': 'json', 'markdown': 'md'
                }
                ext = ext_map.get(language, 'txt')
                filepath = f"analytics.{ext}"

            filepath = filepath.strip()

            if not language:
                ext_to_lang = {
                    '.ts': 'typescript', '.tsx': 'typescript', '.js': 'javascript',
                    '.sql': 'sql', '.json': 'json', '.md': 'markdown'
                }
                for ext, lang in ext_to_lang.items():
                    if filepath.endswith(ext):
                        language = lang
                        break
                if not language:
                    language = 'text'

            files.append({
                "name": filepath,
                "content": code,
                "language": language,
                "type": "analytics"
            })

        return files

    def _extract_events(self, response: str) -> List[Dict[str, Any]]:
        """Extract event definitions from response."""
        events = []

        # Look for event definitions in various formats
        event_patterns = [
            r'(\w+_\w+):\s*[\'"](.+?)[\'"]',  # CONSTANT: 'Event_Name'
            r'event:\s*[\'"](\w+_\w+)[\'"]',  # event: 'Event_Name'
            r'track\([\'"](\w+_\w+)[\'"]'     # track('Event_Name'
        ]

        for pattern in event_patterns:
            matches = re.findall(pattern, response)
            for match in matches:
                event_name = match if isinstance(match, str) else match[1] if len(match) > 1 else match[0]
                if '_' in event_name and event_name not in [e['name'] for e in events]:
                    events.append({
                        "name": event_name,
                        "category": event_name.split('_')[0],
                        "action": '_'.join(event_name.split('_')[1:])
                    })

        return events

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from response."""
        # Try to extract JSON block
        json_match = re.search(r'```json\n([\s\S]*?)```', response)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try to parse entire response
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"raw": response}


if __name__ == "__main__":
    # Example usage
    import asyncio
    import os

    async def test_agent():
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            print("Error: OPENROUTER_API_KEY not set")
            return

        agent = AnalyticsEngineerAgent(api_key)

        task = {
            "features": [
                "User authentication",
                "Project creation",
                "Task management",
                "Team collaboration",
                "Billing and subscriptions"
            ],
            "metrics": [
                "Daily Active Users (DAU)",
                "Sign-up to first project (activation)",
                "Free to paid conversion",
                "Feature adoption rates",
                "User retention (D1, D7, D30)"
            ],
            "platform": "posthog",
            "tracking_plan": {
                "core_events": ["User_SignedUp", "Project_Created", "Payment_Completed"],
                "page_views": ["/dashboard", "/projects", "/settings"],
                "properties": ["user_id", "project_id", "plan_type"]
            }
        }

        result = await agent.execute(task)

        print(f"\nSuccess: {result['success']}")
        print(f"Platform: {result['platform']}")
        print(f"\nGenerated {len(result['files'])} files:")
        for file in result['files']:
            print(f"\n--- {file['name']} ({file['language']}) ---")
            print(file['content'][:200] + "..." if len(file['content']) > 200 else file['content'])

        print(f"\n\nTracked Events ({len(result['tracking_events'])}):")
        for event in result['tracking_events'][:5]:
            print(f"  - {event['name']}")

    asyncio.run(test_agent())
