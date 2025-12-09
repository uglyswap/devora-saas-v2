"""
Tests for AI/ML Infrastructure

Run with: pytest tests/test_ai_ml_infrastructure.py -v
"""

import pytest
import asyncio
import os
from datetime import datetime, timedelta

# AI Module
from ai.llm_service import LLMService, LLMConfig, LLMProvider
from ai.cache import ResponseCache
from ai.rag.embeddings import EmbeddingService
from ai.rag.vector_store import VectorStore, VectorStoreConfig, VectorStoreType
from ai.rag.retriever import ContextRetriever
from ai.prompts.template_manager import PromptTemplateManager

# ML Ops
from ml_ops.monitoring import MLMonitor, MetricType, MetricEvent
from ml_ops.cost_tracker import CostTracker, Budget
from ml_ops.ab_testing import ABTester, Experiment, Variant, ExperimentStatus
from ml_ops.dashboard import DashboardManager


# ═══════════════════════════════════════════════════════════════
# LLM Service Tests
# ═══════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_llm_service_initialization():
    """Test LLM service initialization"""
    config = LLMConfig(
        provider=LLMProvider.OPENROUTER,
        api_key="test_key",
        model="openai/gpt-4o-mini",
    )

    async with LLMService(config) as service:
        assert service.config.model == "openai/gpt-4o-mini"
        assert service.config.provider == LLMProvider.OPENROUTER


def test_llm_token_counting():
    """Test token counting"""
    config = LLMConfig(api_key="test_key")
    service = LLMService(config)

    text = "Hello, world! This is a test."
    tokens = service.count_tokens(text)

    assert tokens > 0
    assert isinstance(tokens, int)


def test_llm_cost_estimation():
    """Test cost estimation"""
    config = LLMConfig(api_key="test_key")
    service = LLMService(config)

    cost = service.estimate_cost(
        prompt_tokens=1000,
        completion_tokens=500,
        model="openai/gpt-4o-mini",
    )

    assert cost > 0
    assert isinstance(cost, float)


# ═══════════════════════════════════════════════════════════════
# Cache Tests
# ═══════════════════════════════════════════════════════════════

def test_cache_basic_operations():
    """Test cache set/get"""
    cache = ResponseCache(max_size=100)

    messages = [{"role": "user", "content": "Hello"}]
    response = "Hi there!"

    # Set
    cache.set(response, messages, model="test-model")

    # Get
    cached = cache.get(messages, model="test-model")

    assert cached == response


def test_cache_ttl():
    """Test cache TTL expiration"""
    cache = ResponseCache(max_size=100, default_ttl_seconds=1)

    messages = [{"role": "user", "content": "Hello"}]
    response = "Hi there!"

    cache.set(response, messages, model="test-model")

    # Should be cached
    assert cache.get(messages, model="test-model") == response

    # Wait for expiration
    import time
    time.sleep(2)

    # Should be expired
    assert cache.get(messages, model="test-model") is None


def test_cache_metrics():
    """Test cache metrics"""
    cache = ResponseCache(max_size=100)

    messages = [{"role": "user", "content": "Hello"}]
    response = "Hi there!"

    # Miss
    cache.get(messages, model="test-model")

    # Set
    cache.set(response, messages, model="test-model")

    # Hit
    cache.get(messages, model="test-model")

    metrics = cache.get_metrics()

    assert metrics["hits"] == 1
    assert metrics["misses"] == 1
    assert metrics["total_requests"] == 2
    assert metrics["hit_rate"] == 0.5


# ═══════════════════════════════════════════════════════════════
# Vector Store Tests
# ═══════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_vector_store_memory():
    """Test in-memory vector store"""
    config = VectorStoreConfig(
        store_type=VectorStoreType.MEMORY,
        dimension=3,
    )
    store = VectorStore(config)

    # Add vectors
    await store.add("vec1", "Hello world", [1.0, 0.0, 0.0], {"category": "greeting"})
    await store.add("vec2", "Goodbye", [0.0, 1.0, 0.0], {"category": "farewell"})

    # Search
    query_embedding = [1.0, 0.1, 0.0]
    results = await store.search(query_embedding, top_k=1)

    assert len(results) == 1
    assert results[0].id == "vec1"
    assert results[0].text == "Hello world"


@pytest.mark.asyncio
async def test_vector_store_metadata_filter():
    """Test vector store metadata filtering"""
    config = VectorStoreConfig(store_type=VectorStoreType.MEMORY, dimension=3)
    store = VectorStore(config)

    await store.add("vec1", "Hello", [1.0, 0.0, 0.0], {"category": "greeting", "lang": "en"})
    await store.add("vec2", "Bonjour", [0.9, 0.1, 0.0], {"category": "greeting", "lang": "fr"})
    await store.add("vec3", "Goodbye", [0.0, 1.0, 0.0], {"category": "farewell", "lang": "en"})

    # Filter by category
    results = await store.search(
        [1.0, 0.0, 0.0],
        top_k=5,
        filter_metadata={"category": "greeting"}
    )

    assert len(results) == 2
    assert all(r.metadata["category"] == "greeting" for r in results)


# ═══════════════════════════════════════════════════════════════
# Prompt Template Tests
# ═══════════════════════════════════════════════════════════════

def test_template_manager():
    """Test template manager"""
    manager = PromptTemplateManager()

    # Get template
    template = manager.get_template("generate_component")

    assert template is not None
    assert template.name == "generate_component"
    assert "component_name" in template.variables


def test_template_rendering():
    """Test template rendering"""
    manager = PromptTemplateManager()

    rendered = manager.render(
        "generate_component",
        component_name="UserProfile",
        description="Display user info",
        props="{ userId: string }",
    )

    assert "UserProfile" in rendered
    assert "Display user info" in rendered


def test_template_categories():
    """Test template categories"""
    manager = PromptTemplateManager()

    categories = manager.get_categories()

    assert "architecture" in categories
    assert "code_generation" in categories
    assert "review" in categories


# ═══════════════════════════════════════════════════════════════
# Monitoring Tests
# ═══════════════════════════════════════════════════════════════

def test_monitoring_track_request():
    """Test monitoring request tracking"""
    monitor = MLMonitor()

    monitor.track_request(
        success=True,
        latency_ms=1500,
        cost=0.02,
        tokens=800,
        model="test-model",
        agent="test-agent",
    )

    stats = monitor.get_real_time_stats()

    assert stats["total_requests"] == 1
    assert stats["successful_requests"] == 1
    assert stats["total_cost"] == 0.02


def test_monitoring_aggregated_metrics():
    """Test aggregated metrics"""
    monitor = MLMonitor()

    # Track multiple requests
    for i in range(10):
        monitor.track_request(
            success=i % 10 != 0,  # 90% success
            latency_ms=1000 + i * 100,
            cost=0.01,
            tokens=500,
            model="test-model",
            agent="test-agent",
        )

    metrics = monitor.get_metrics()

    assert metrics.total_requests == 10
    assert metrics.success_rate == 0.9
    assert metrics.avg_latency_ms > 0
    assert metrics.total_cost == 0.1


def test_monitoring_error_breakdown():
    """Test error breakdown tracking"""
    monitor = MLMonitor()

    monitor.track_request(
        success=False,
        latency_ms=1000,
        model="test-model",
        agent="test-agent",
        error_type="timeout",
    )

    monitor.track_request(
        success=False,
        latency_ms=1000,
        model="test-model",
        agent="test-agent",
        error_type="rate_limit",
    )

    metrics = monitor.get_metrics()

    assert "timeout" in metrics.error_breakdown
    assert "rate_limit" in metrics.error_breakdown


# ═══════════════════════════════════════════════════════════════
# Cost Tracker Tests
# ═══════════════════════════════════════════════════════════════

def test_cost_tracker_basic():
    """Test basic cost tracking"""
    tracker = CostTracker()

    tracker.track_cost(
        amount=0.05,
        model="test-model",
        agent="test-agent",
        tokens_used=1000,
    )

    report = tracker.get_report()

    assert report.total_cost == 0.05
    assert report.total_requests == 1
    assert report.cost_by_model["test-model"] == 0.05


def test_cost_tracker_budget():
    """Test budget tracking"""
    tracker = CostTracker()

    budget = Budget(
        name="test_budget",
        limit=1.0,
        period="daily",
        scope="global",
    )

    tracker.add_budget(budget)

    # Track costs
    for _ in range(10):
        tracker.track_cost(
            amount=0.05,
            model="test-model",
            agent="test-agent",
            tokens_used=100,
        )

    status = tracker.get_budget_status("test_budget")

    assert status["spent"] == 0.5
    assert status["remaining"] == 0.5
    assert status["percentage"] == 50.0


def test_cost_tracker_forecast():
    """Test cost forecasting"""
    tracker = CostTracker()

    # Track some costs
    for _ in range(30):
        tracker.track_cost(
            amount=1.0,
            model="test-model",
            agent="test-agent",
            tokens_used=1000,
        )

    forecast = tracker.forecast_costs(days_ahead=30)

    assert forecast["estimated_cost"] > 0
    assert forecast["daily_average"] == 1.0


# ═══════════════════════════════════════════════════════════════
# A/B Testing Tests
# ═══════════════════════════════════════════════════════════════

def test_ab_testing_create_experiment():
    """Test experiment creation"""
    tester = ABTester()

    experiment = Experiment(
        name="test_experiment",
        description="Test experiment",
        variants=[
            Variant(name="control", model="model-a"),
            Variant(name="treatment", model="model-b"),
        ],
    )

    tester.create_experiment(experiment)

    assert "test_experiment" in tester.list_experiments()


def test_ab_testing_variant_selection():
    """Test variant selection"""
    tester = ABTester()

    experiment = Experiment(
        name="test_experiment",
        description="Test",
        variants=[
            Variant(name="v1", weight=1.0),
            Variant(name="v2", weight=1.0),
        ],
    )

    tester.create_experiment(experiment)
    tester.start_experiment("test_experiment")

    # Get variant
    variant = tester.get_variant("test_experiment")

    assert variant is not None
    assert variant.name in ["v1", "v2"]


def test_ab_testing_results():
    """Test result tracking"""
    tester = ABTester()

    experiment = Experiment(
        name="test_experiment",
        description="Test",
        variants=[
            Variant(name="v1"),
            Variant(name="v2"),
        ],
        min_sample_size=10,
    )

    tester.create_experiment(experiment)
    tester.start_experiment("test_experiment")

    # Track results
    for i in range(20):
        variant_name = "v1" if i % 2 == 0 else "v2"
        success = i % 5 != 0  # 80% success

        tester.track_result(
            experiment_name="test_experiment",
            variant_name=variant_name,
            success=success,
            latency_ms=1000,
            cost=0.01,
        )

    summary = tester.get_experiment_summary("test_experiment")

    assert summary["total_impressions"] == 20
    assert len(summary["variants"]) == 2


# ═══════════════════════════════════════════════════════════════
# Dashboard Tests
# ═══════════════════════════════════════════════════════════════

def test_dashboard_overview():
    """Test dashboard overview"""
    monitor = MLMonitor()
    tracker = CostTracker()
    ab_tester = ABTester()

    dashboard = DashboardManager(monitor, tracker, ab_tester)

    # Track some data
    for i in range(10):
        monitor.track_request(
            success=True,
            latency_ms=1000,
            cost=0.01,
            tokens=500,
            model="test-model",
            agent="test-agent",
        )

        tracker.track_cost(
            amount=0.01,
            model="test-model",
            agent="test-agent",
            tokens_used=500,
        )

    overview = dashboard.get_overview()

    assert "overview" in overview
    assert "last_24h" in overview
    assert "cost_summary" in overview
    assert overview["overview"]["total_requests"] == 10


def test_dashboard_health_check():
    """Test health check"""
    monitor = MLMonitor()
    tracker = CostTracker()
    ab_tester = ABTester()

    dashboard = DashboardManager(monitor, tracker, ab_tester)

    # Track some successful requests
    for _ in range(10):
        monitor.track_request(
            success=True,
            latency_ms=1000,
            cost=0.01,
            tokens=500,
            model="test-model",
            agent="test-agent",
        )

    health = dashboard.get_health_check()

    assert health["overall_status"] in ["healthy", "degraded", "critical"]
    assert "checks" in health


# ═══════════════════════════════════════════════════════════════
# Integration Tests
# ═══════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_full_workflow():
    """Test complete workflow: RAG + LLM + Monitoring"""
    # Skip if no API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("No OPENAI_API_KEY found")

    # Setup
    cache = ResponseCache()
    monitor = MLMonitor()
    tracker = CostTracker()

    # Add knowledge
    embeddings = EmbeddingService(api_key=api_key)
    vector_store = VectorStore(VectorStoreConfig(store_type=VectorStoreType.MEMORY, dimension=1536))
    retriever = ContextRetriever(embeddings, vector_store)

    docs = [
        {"id": "1", "text": "Python is a programming language"},
    ]
    await retriever.add_documents(docs)

    # Retrieve context
    context = await retriever.retrieve_and_format("programming language", top_k=1)

    assert "Python" in context

    # Check monitoring
    stats = monitor.get_real_time_stats()
    assert stats is not None


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
