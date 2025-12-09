"""
Example Usage of AI/ML Infrastructure

This file demonstrates how to use the AI and ML Ops modules.
"""

import asyncio
import os
from datetime import timedelta

# AI Module imports
from ai.llm_service import LLMService, LLMConfig, LLMProvider
from ai.cache import ResponseCache
from ai.rag.embeddings import EmbeddingService
from ai.rag.vector_store import VectorStore, VectorStoreConfig, VectorStoreType
from ai.rag.retriever import ContextRetriever
from ai.prompts.template_manager import PromptTemplateManager

# ML Ops imports
from ml_ops.monitoring import MLMonitor, MetricType, MetricEvent
from ml_ops.cost_tracker import CostTracker, Budget
from ml_ops.ab_testing import ABTester, Experiment, Variant, ExperimentStatus
from ml_ops.dashboard import DashboardManager, DashboardConfig


# ═══════════════════════════════════════════════════════════════
# EXAMPLE 1: Basic LLM Usage with Caching
# ═══════════════════════════════════════════════════════════════

async def example_basic_llm():
    """Example: Basic LLM completion with caching"""
    print("\n=== Example 1: Basic LLM with Caching ===\n")

    # Initialize cache
    cache = ResponseCache(max_size=1000, default_ttl_seconds=3600)

    # Configure LLM
    config = LLMConfig(
        provider=LLMProvider.OPENROUTER,
        api_key=os.getenv("OPENROUTER_API_KEY", ""),
        model="openai/gpt-4o-mini",
        enable_cost_tracking=True,
    )

    async with LLMService(config) as llm:
        messages = [{"role": "user", "content": "Explain Python decorators in one sentence."}]

        # Check cache first
        cached = cache.get(messages, model=config.model)
        if cached:
            print(f"Cache HIT: {cached}")
            return

        # Call LLM
        response, stats = await llm.complete(messages)

        # Cache response
        cache.set(response, messages, model=config.model)

        print(f"Response: {response}")
        print(f"Stats: {stats.total_tokens} tokens, ${stats.estimated_cost:.4f}, {stats.latency_ms:.0f}ms")
        print(f"Cache metrics: {cache.get_metrics()}")


# ═══════════════════════════════════════════════════════════════
# EXAMPLE 2: RAG (Retrieval-Augmented Generation)
# ═══════════════════════════════════════════════════════════════

async def example_rag():
    """Example: RAG with vector store"""
    print("\n=== Example 2: RAG ===\n")

    # Initialize embedding service
    embedding_service = EmbeddingService(
        api_key=os.getenv("OPENAI_API_KEY", ""),
        model="text-embedding-3-small",
    )

    # Initialize vector store (in-memory)
    vector_config = VectorStoreConfig(
        store_type=VectorStoreType.MEMORY,
        dimension=1536,
    )
    vector_store = VectorStore(vector_config)

    # Initialize retriever
    retriever = ContextRetriever(
        embedding_service=embedding_service,
        vector_store=vector_store,
        score_threshold=0.7,
    )

    # Add documents to knowledge base
    documents = [
        {
            "id": "doc1",
            "text": "Next.js 14 uses the App Router with server components by default.",
            "category": "nextjs",
        },
        {
            "id": "doc2",
            "text": "Supabase provides Row Level Security (RLS) for fine-grained access control.",
            "category": "supabase",
        },
        {
            "id": "doc3",
            "text": "Stripe webhooks should be verified using the webhook secret.",
            "category": "stripe",
        },
    ]

    await retriever.add_documents(documents)

    # Query the knowledge base
    query = "How do I secure my Supabase database?"
    contexts = await retriever.retrieve(query, top_k=2)

    print(f"Query: {query}")
    print(f"Retrieved {len(contexts)} contexts:")
    for ctx in contexts:
        print(f"  - [{ctx.source}] (score: {ctx.score:.3f}): {ctx.text}")

    # Use in LLM prompt
    formatted_context = retriever.format_context(contexts)
    print(f"\nFormatted context for LLM:\n{formatted_context}")


# ═══════════════════════════════════════════════════════════════
# EXAMPLE 3: Prompt Templates
# ═══════════════════════════════════════════════════════════════

async def example_prompt_templates():
    """Example: Using prompt templates"""
    print("\n=== Example 3: Prompt Templates ===\n")

    # Initialize template manager
    template_manager = PromptTemplateManager()

    # Get a template
    template = template_manager.get_template("generate_component")

    if template:
        # Render template
        prompt = template.render(
            component_name="UserProfile",
            description="A component that displays user information",
            props="{ userId: string, showAvatar: boolean }",
        )

        print(f"Template: {template.name}")
        print(f"Rendered prompt:\n{prompt}")

    # List all templates
    print(f"\nAvailable templates ({len(template_manager.list_templates())}):")
    for t in template_manager.list_templates()[:5]:
        print(f"  - {t.name} ({t.category}): {t.description}")


# ═══════════════════════════════════════════════════════════════
# EXAMPLE 4: ML Monitoring
# ═══════════════════════════════════════════════════════════════

async def example_monitoring():
    """Example: ML monitoring"""
    print("\n=== Example 4: ML Monitoring ===\n")

    # Initialize monitor
    monitor = MLMonitor(retention_days=30)

    # Simulate some requests
    for i in range(100):
        success = i % 10 != 0  # 90% success rate
        latency_ms = 1000 + (i % 50) * 100
        cost = 0.01 if success else 0
        tokens = 500 if success else 0

        monitor.track_request(
            success=success,
            latency_ms=latency_ms,
            cost=cost,
            tokens=tokens,
            model="openai/gpt-4o-mini",
            agent="coder",
            error_type="timeout" if not success else None,
        )

    # Get real-time stats
    stats = monitor.get_real_time_stats()
    print(f"Real-time stats:")
    print(f"  Total requests: {stats['total_requests']}")
    print(f"  Success rate: {stats['success_rate']:.2%}")
    print(f"  Avg latency: {stats['avg_latency_ms']:.0f}ms")
    print(f"  Total cost: ${stats['total_cost']:.4f}")

    # Get aggregated metrics
    metrics = monitor.get_metrics()
    print(f"\nAggregated metrics:")
    print(f"  P95 latency: {metrics.p95_latency_ms:.0f}ms")
    print(f"  Error breakdown: {metrics.error_breakdown}")


# ═══════════════════════════════════════════════════════════════
# EXAMPLE 5: Cost Tracking and Budgets
# ═══════════════════════════════════════════════════════════════

async def example_cost_tracking():
    """Example: Cost tracking with budgets"""
    print("\n=== Example 5: Cost Tracking ===\n")

    # Initialize cost tracker
    cost_tracker = CostTracker(retention_days=90)

    # Add budgets
    cost_tracker.add_budget(Budget(
        name="daily_budget",
        limit=10.0,
        period="daily",
        scope="global",
        alert_threshold=0.8,
    ))

    cost_tracker.add_budget(Budget(
        name="gpt4_monthly",
        limit=100.0,
        period="monthly",
        scope="model",
        scope_value="openai/gpt-4o",
    ))

    # Track some costs
    for i in range(50):
        cost_tracker.track_cost(
            amount=0.05,
            model="openai/gpt-4o-mini" if i % 2 == 0 else "openai/gpt-4o",
            agent="coder",
            tokens_used=1000,
        )

    # Get cost report
    report = cost_tracker.get_report()
    print(f"Cost Report:")
    print(f"  Total cost: ${report.total_cost:.2f}")
    print(f"  Avg per request: ${report.avg_cost_per_request:.4f}")
    print(f"  Cost by model: {report.cost_by_model}")

    # Check budget status
    for budget_name in ["daily_budget", "gpt4_monthly"]:
        status = cost_tracker.get_budget_status(budget_name)
        if status:
            print(f"\nBudget '{budget_name}':")
            print(f"  Spent: ${status['spent']:.2f} / ${status['limit']:.2f}")
            print(f"  Usage: {status['percentage']:.1f}%")

    # Get forecast
    forecast = cost_tracker.forecast_costs(days_ahead=30)
    print(f"\n30-day forecast: ${forecast['estimated_cost']:.2f}")


# ═══════════════════════════════════════════════════════════════
# EXAMPLE 6: A/B Testing
# ═══════════════════════════════════════════════════════════════

async def example_ab_testing():
    """Example: A/B testing prompts"""
    print("\n=== Example 6: A/B Testing ===\n")

    # Initialize A/B tester
    ab_tester = ABTester()

    # Create experiment
    experiment = Experiment(
        name="prompt_optimization",
        description="Test different prompt styles for code generation",
        variants=[
            Variant(
                name="concise",
                prompt_template="Generate {component_name}: {description}",
                model="openai/gpt-4o-mini",
                weight=1.0,
            ),
            Variant(
                name="detailed",
                prompt_template="Create a production-ready {component_name} that {description}. Include TypeScript types and error handling.",
                model="openai/gpt-4o-mini",
                weight=1.0,
            ),
        ],
        primary_metric="success_rate",
        min_sample_size=50,
    )

    ab_tester.create_experiment(experiment)
    ab_tester.start_experiment("prompt_optimization")

    # Simulate experiment results
    for i in range(100):
        variant = ab_tester.get_variant("prompt_optimization")
        if variant:
            # Simulate: detailed variant performs better
            success = (variant.name == "detailed" and i % 10 != 0) or (variant.name == "concise" and i % 5 != 0)
            latency_ms = 2000 + (i % 10) * 100

            ab_tester.track_result(
                experiment_name="prompt_optimization",
                variant_name=variant.name,
                success=success,
                latency_ms=latency_ms,
                cost=0.01,
                tokens=500,
            )

    # Get results
    summary = ab_tester.get_experiment_summary("prompt_optimization")
    if summary:
        print(f"Experiment: {summary['name']}")
        print(f"Status: {summary['status']}")
        print(f"Total impressions: {summary['total_impressions']}")
        print(f"Current leader: {summary['current_leader']}")
        print(f"\nVariants:")
        for variant in summary['variants']:
            print(f"  {variant['name']}:")
            print(f"    Success rate: {variant['success_rate']:.2%}")
            print(f"    Avg latency: {variant['avg_latency_ms']:.0f}ms")


# ═══════════════════════════════════════════════════════════════
# EXAMPLE 7: Complete Dashboard
# ═══════════════════════════════════════════════════════════════

async def example_dashboard():
    """Example: ML Ops dashboard"""
    print("\n=== Example 7: ML Ops Dashboard ===\n")

    # Initialize components
    monitor = MLMonitor()
    cost_tracker = CostTracker()
    ab_tester = ABTester()

    # Create dashboard
    dashboard = DashboardManager(
        monitor=monitor,
        cost_tracker=cost_tracker,
        ab_tester=ab_tester,
        config=DashboardConfig(refresh_interval_seconds=60),
    )

    # Simulate some activity
    for i in range(50):
        monitor.track_request(
            success=i % 10 != 0,
            latency_ms=1500 + (i % 20) * 100,
            cost=0.02,
            tokens=800,
            model="openai/gpt-4o-mini",
            agent="coder",
        )

        cost_tracker.track_cost(
            amount=0.02,
            model="openai/gpt-4o-mini",
            agent="coder",
            tokens_used=800,
        )

    # Get overview
    overview = dashboard.get_overview()
    print(f"Dashboard Overview:")
    print(f"  Total requests: {overview['overview']['total_requests']}")
    print(f"  Success rate: {overview['overview']['success_rate']:.2%}")
    print(f"  Avg latency: {overview['overview']['avg_latency_ms']:.0f}ms")
    print(f"  Total cost: ${overview['overview']['total_cost']:.4f}")

    # Get health check
    health = dashboard.get_health_check()
    print(f"\nHealth Status: {health['overall_status']}")
    print(f"  Error rate: {health['checks']['error_rate']['status']}")
    print(f"  Latency: {health['checks']['latency']['status']}")


# ═══════════════════════════════════════════════════════════════
# RUN ALL EXAMPLES
# ═══════════════════════════════════════════════════════════════

async def main():
    """Run all examples"""
    print("=" * 70)
    print("AI/ML Infrastructure Examples")
    print("=" * 70)

    # Note: Some examples require API keys
    # Set environment variables before running:
    # - OPENROUTER_API_KEY
    # - OPENAI_API_KEY

    try:
        # await example_basic_llm()
        # await example_rag()
        await example_prompt_templates()
        await example_monitoring()
        await example_cost_tracking()
        await example_ab_testing()
        await example_dashboard()

    except Exception as e:
        print(f"\nError running examples: {e}")
        print("Make sure to set required API keys in environment variables.")


if __name__ == "__main__":
    asyncio.run(main())
