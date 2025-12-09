"""
Example usage of Performance Squad agents

Ce fichier démontre comment utiliser les agents du Performance Squad
pour optimiser les performances d'une application web.
"""

import asyncio
import os
from dotenv import load_dotenv

# Import agents from performance_squad
from performance_engineer import PerformanceEngineerAgent
from bundle_optimizer import BundleOptimizerAgent
from database_optimizer import DatabaseOptimizerAgent

# Import core classes
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../core'))
from base_agent import AgentConfig


async def example_performance_engineer():
    """Exemple d'utilisation du Performance Engineer."""
    print("\n" + "="*80)
    print("PERFORMANCE ENGINEER - Core Web Vitals Analysis")
    print("="*80 + "\n")

    # Configuration
    config = AgentConfig(
        name="performance-engineer",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        model="anthropic/claude-3.5-sonnet",
        temperature=0.3,
        max_tokens=4096
    )

    # Créer l'agent
    agent = PerformanceEngineerAgent(config)

    # Analyser les Core Web Vitals
    result = agent.analyze_core_web_vitals(
        url="https://example.com",
        metrics={
            "lcp": 4.2,      # Largest Contentful Paint (s)
            "fid": 150,      # First Input Delay (ms)
            "cls": 0.18,     # Cumulative Layout Shift
            "ttfb": 1200,    # Time to First Byte (ms)
            "fcp": 2.1,      # First Contentful Paint (s)
            "tti": 5.8       # Time to Interactive (s)
        },
        context="Page d'accueil avec hero image, navigation, et section produits"
    )

    if result["status"] == "success":
        print("Analysis completed successfully!")
        print("\nRecommendations:")
        print(result["output"]["performance_analysis"]["analysis"])
        print("\nMetrics:")
        print(f"- Tokens used: {result['output']['metadata']['tokens_used']}")
        print(f"- Model: {result['output']['metadata']['llm_model']}")
    else:
        print(f"Error: {result['error']}")


async def example_bundle_optimizer():
    """Exemple d'utilisation du Bundle Optimizer."""
    print("\n" + "="*80)
    print("BUNDLE OPTIMIZER - Code Splitting Strategy")
    print("="*80 + "\n")

    config = AgentConfig(
        name="bundle-optimizer",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        model="anthropic/claude-3.5-sonnet",
        temperature=0.3,
        max_tokens=4096
    )

    agent = BundleOptimizerAgent(config)

    # Optimiser le code splitting
    react_router_code = """
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Analytics from './pages/Analytics';
import Settings from './pages/Settings';
import Reports from './pages/Reports';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/reports" element={<Reports />} />
      </Routes>
    </BrowserRouter>
  );
}
"""

    result = agent.optimize_code_splitting(
        code=react_router_code,
        bundler="webpack",
        framework="react"
    )

    if result["status"] == "success":
        print("Code splitting optimization completed!")
        print("\nRecommendations:")
        print(result["output"]["bundle_optimization"]["recommendations"])
    else:
        print(f"Error: {result['error']}")


async def example_database_optimizer():
    """Exemple d'utilisation du Database Optimizer."""
    print("\n" + "="*80)
    print("DATABASE OPTIMIZER - Query Optimization")
    print("="*80 + "\n")

    config = AgentConfig(
        name="database-optimizer",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        model="anthropic/claude-3.5-sonnet",
        temperature=0.3,
        max_tokens=4096
    )

    agent = DatabaseOptimizerAgent(config)

    # Optimiser une requête SQL lente
    slow_query = """
SELECT u.id, u.name, u.email, p.title, p.content, c.comment_text
FROM users u
LEFT JOIN posts p ON p.user_id = u.id
LEFT JOIN comments c ON c.post_id = p.id
WHERE u.created_at > '2024-01-01'
ORDER BY p.created_at DESC;
"""

    explain_plan = """
Sort  (cost=15234.45..15456.78 rows=88933 width=256)
  Sort Key: p.created_at DESC
  ->  Hash Left Join  (cost=4567.89..7890.12 rows=88933 width=256)
        Hash Cond: (c.post_id = p.id)
        ->  Seq Scan on comments c  (cost=0.00..1234.56 rows=50000 width=128)
        ->  Hash  (cost=3210.45..3210.45 rows=108555 width=128)
              ->  Hash Left Join  (cost=789.12..3210.45 rows=108555 width=128)
                    Hash Cond: (p.user_id = u.id)
                    ->  Seq Scan on posts p  (cost=0.00..1500.00 rows=100000 width=64)
                    ->  Hash  (cost=678.90..678.90 rows=8817 width=64)
                          ->  Seq Scan on users u  (cost=0.00..678.90 rows=8817 width=64)
                                Filter: (created_at > '2024-01-01'::date)
"""

    result = agent.optimize_query(
        query=slow_query,
        database="postgresql",
        query_plan=explain_plan,
        execution_time=1847  # 1.8 secondes
    )

    if result["status"] == "success":
        print("Query optimization completed!")
        print("\nRecommendations:")
        print(result["output"]["database_optimization"]["recommendations"])
        print(f"\nCurrent execution time: {result['output']['database_optimization']['current_execution_time_ms']}ms")
    else:
        print(f"Error: {result['error']}")


async def example_full_performance_audit():
    """Exemple d'audit complet de performance."""
    print("\n" + "="*80)
    print("FULL PERFORMANCE AUDIT - Complete Application Analysis")
    print("="*80 + "\n")

    # Configuration partagée
    config = AgentConfig(
        name="performance-squad",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        model="anthropic/claude-3.5-sonnet",
        temperature=0.3,
        max_tokens=8192
    )

    # 1. Analyse des performances frontend
    print("\n[1/3] Analyzing frontend performance...")
    perf_agent = PerformanceEngineerAgent(config)

    # Profiling JavaScript
    js_code = """
function processData(items) {
  const results = [];
  for (let i = 0; i < items.length; i++) {
    for (let j = 0; j < items.length; j++) {
      if (items[i].id === items[j].relatedId) {
        results.push({
          ...items[i],
          related: items[j]
        });
      }
    }
  }
  return results;
}
"""

    frontend_result = perf_agent.profile_javascript(js_code)

    # 2. Optimisation du bundle
    print("\n[2/3] Analyzing bundle size...")
    bundle_agent = BundleOptimizerAgent(config)

    package_json = """
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "lodash": "^4.17.21",
    "moment": "^2.29.4",
    "axios": "^1.6.0",
    "@mui/material": "^5.14.0"
  }
}
"""

    bundle_result = bundle_agent.analyze_dependencies(package_json)

    # 3. Optimisation de la base de données
    print("\n[3/3] Analyzing database performance...")
    db_agent = DatabaseOptimizerAgent(config)

    db_result = db_agent.configure_pooling(database="postgresql")

    # Afficher le résumé
    print("\n" + "="*80)
    print("PERFORMANCE AUDIT SUMMARY")
    print("="*80)

    print("\n[Frontend Performance]")
    if frontend_result["status"] == "success":
        print("✅ Analysis completed")
        print(f"   Tokens used: {frontend_result['metrics']['total_tokens']}")
    else:
        print(f"❌ Error: {frontend_result['error']}")

    print("\n[Bundle Optimization]")
    if bundle_result["status"] == "success":
        print("✅ Analysis completed")
        print(f"   Tokens used: {bundle_result['metrics']['total_tokens']}")
    else:
        print(f"❌ Error: {bundle_result['error']}")

    print("\n[Database Optimization]")
    if db_result["status"] == "success":
        print("✅ Analysis completed")
        print(f"   Tokens used: {db_result['metrics']['total_tokens']}")
    else:
        print(f"❌ Error: {db_result['error']}")

    total_tokens = (
        frontend_result.get("metrics", {}).get("total_tokens", 0) +
        bundle_result.get("metrics", {}).get("total_tokens", 0) +
        db_result.get("metrics", {}).get("total_tokens", 0)
    )

    print(f"\nTotal tokens used: {total_tokens}")
    print("="*80)


async def main():
    """Point d'entrée principal."""
    # Charger les variables d'environnement
    load_dotenv()

    # Vérifier la clé API
    if not os.getenv("OPENROUTER_API_KEY"):
        print("Error: OPENROUTER_API_KEY not found in environment variables")
        print("Please set it in your .env file or export it:")
        print("  export OPENROUTER_API_KEY='your-api-key-here'")
        return

    print("\n🚀 Performance Squad - Examples\n")

    # Exécuter les exemples
    try:
        # Exemple 1: Performance Engineer
        await example_performance_engineer()

        # Exemple 2: Bundle Optimizer
        await example_bundle_optimizer()

        # Exemple 3: Database Optimizer
        await example_database_optimizer()

        # Exemple 4: Audit complet
        await example_full_performance_audit()

    except Exception as e:
        print(f"\n❌ Error during execution: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Exécuter le main
    asyncio.run(main())
