"""
Devora Orchestration - ML Ops Engineer Agent
==============================================

Specialized agent for ML model deployment, monitoring,
caching, and cost management.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import json

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.base_agent import BaseAgent, AgentConfig


@dataclass
class ModelDeploymentConfig:
    """Configuration for model deployment."""
    model_id: str
    provider: str
    max_tokens: int
    temperature: float
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600
    rate_limit_rpm: int = 60
    fallback_model: Optional[str] = None


class MLOpsEngineer(BaseAgent):
    """
    ML Ops Engineer Agent - Specialized in ML operations and deployment.

    Capabilities:
        - Model deployment configuration
        - Inference monitoring and logging
        - Response caching strategies
        - Cost tracking and optimization
        - Rate limiting implementation
        - Fallback and retry strategies
        - A/B testing for models
    """

    SYSTEM_PROMPT = """You are an expert ML Operations Engineer specializing in LLM deployment and operations.

Your expertise includes:
1. **Model Deployment**:
   - API endpoint configuration
   - Load balancing across providers
   - Failover strategies
   - Version management

2. **Monitoring & Observability**:
   - Latency tracking
   - Token usage monitoring
   - Error rate tracking
   - Cost per request metrics
   - Quality metrics (hallucination detection)

3. **Caching Strategies**:
   - Semantic caching for similar queries
   - Embedding caching
   - Response caching with TTL
   - Cache invalidation patterns

4. **Cost Optimization**:
   - Model selection based on task complexity
   - Prompt optimization for token reduction
   - Batch processing where applicable
   - Usage quotas and alerts

5. **Reliability**:
   - Rate limiting implementation
   - Retry with exponential backoff
   - Circuit breaker patterns
   - Graceful degradation

When implementing ML ops:
- Always implement proper logging
- Track costs at request level
- Use caching aggressively
- Implement health checks
- Set up alerts for anomalies
- Plan for scale from day one

Output infrastructure code that is production-ready."""

    def __init__(self, config: Optional[AgentConfig] = None):
        """Initialize ML Ops Engineer agent."""
        super().__init__(
            name="ml_ops_engineer",
            description="ML Operations specialist",
            config=config or AgentConfig()
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute ML ops task.

        Args:
            context: Task context containing:
                - task: The ML ops task to perform
                - models: Models to deploy/manage
                - infrastructure: Current infrastructure context

        Returns:
            Dictionary with configuration and implementation
        """
        task = context.get("task", "")
        models = context.get("models", [])

        prompt = f"""
Task: {task}

Models to manage:
{json.dumps(models, indent=2)}

Please provide:
1. Infrastructure configuration
2. Monitoring setup
3. Caching implementation
4. Cost tracking setup
5. Alerting rules
"""

        result = await self.run(prompt)

        return {
            "success": True,
            "agent": self.name,
            "task": task,
            "implementation": result.get("content", ""),
            "configurations": self._extract_configurations(result.get("content", ""))
        }

    def _extract_configurations(self, content: str) -> Dict[str, Any]:
        """Extract configurations from content."""
        return {
            "monitoring": True,
            "caching": True,
            "rate_limiting": True
        }

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data."""
        return "task" in input_data

    def format_output(self, output: Dict[str, Any]) -> str:
        """Format output for display."""
        return json.dumps(output, indent=2)

    def generate_monitoring_setup(self) -> str:
        """Generate monitoring setup code."""
        return '''
// ML Monitoring Service
import { createClient } from "@supabase/supabase-js";

interface LLMMetrics {
  requestId: string;
  model: string;
  provider: string;
  promptTokens: number;
  completionTokens: number;
  totalTokens: number;
  latencyMs: number;
  cost: number;
  success: boolean;
  errorType?: string;
  timestamp: Date;
}

class LLMMonitor {
  private supabase;
  private metricsBuffer: LLMMetrics[] = [];
  private flushInterval: number = 5000; // 5 seconds

  constructor() {
    this.supabase = createClient(
      process.env.SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_KEY!
    );

    // Flush metrics periodically
    setInterval(() => this.flush(), this.flushInterval);
  }

  async trackRequest(metrics: LLMMetrics) {
    this.metricsBuffer.push(metrics);

    // Immediate flush for errors
    if (!metrics.success) {
      await this.flush();
    }
  }

  async flush() {
    if (this.metricsBuffer.length === 0) return;

    const batch = [...this.metricsBuffer];
    this.metricsBuffer = [];

    try {
      await this.supabase.from("llm_metrics").insert(batch);
    } catch (error) {
      console.error("Failed to flush metrics:", error);
      // Re-add to buffer for retry
      this.metricsBuffer.unshift(...batch);
    }
  }

  async getUsageStats(period: "day" | "week" | "month") {
    const { data, error } = await this.supabase
      .rpc("get_llm_usage_stats", { period });

    if (error) throw error;
    return data;
  }

  async getCostByModel(startDate: Date, endDate: Date) {
    const { data, error } = await this.supabase
      .from("llm_metrics")
      .select("model, cost")
      .gte("timestamp", startDate.toISOString())
      .lte("timestamp", endDate.toISOString());

    if (error) throw error;

    // Aggregate by model
    const costByModel: Record<string, number> = {};
    data.forEach((row) => {
      costByModel[row.model] = (costByModel[row.model] || 0) + row.cost;
    });

    return costByModel;
  }
}

export const llmMonitor = new LLMMonitor();
'''

    def generate_caching_layer(self) -> str:
        """Generate caching layer code."""
        return '''
// Semantic Caching for LLM Responses
import { Redis } from "@upstash/redis";
import { createHash } from "crypto";

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_URL!,
  token: process.env.UPSTASH_REDIS_TOKEN!,
});

interface CacheConfig {
  ttlSeconds: number;
  semanticThreshold: number; // 0-1, similarity threshold
}

const DEFAULT_CONFIG: CacheConfig = {
  ttlSeconds: 3600, // 1 hour
  semanticThreshold: 0.95,
};

export class LLMCache {
  private config: CacheConfig;

  constructor(config: Partial<CacheConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
  }

  private hashPrompt(prompt: string): string {
    return createHash("sha256").update(prompt).digest("hex");
  }

  async get(prompt: string, model: string): Promise<string | null> {
    const key = `llm:${model}:${this.hashPrompt(prompt)}`;
    const cached = await redis.get<string>(key);
    return cached;
  }

  async set(prompt: string, model: string, response: string): Promise<void> {
    const key = `llm:${model}:${this.hashPrompt(prompt)}`;
    await redis.setex(key, this.config.ttlSeconds, response);
  }

  async invalidate(pattern: string): Promise<void> {
    const keys = await redis.keys(`llm:*${pattern}*`);
    if (keys.length > 0) {
      await redis.del(...keys);
    }
  }

  async getStats(): Promise<{ hits: number; misses: number; hitRate: number }> {
    const hits = (await redis.get<number>("llm:stats:hits")) || 0;
    const misses = (await redis.get<number>("llm:stats:misses")) || 0;
    const total = hits + misses;
    return {
      hits,
      misses,
      hitRate: total > 0 ? hits / total : 0,
    };
  }
}

// Middleware for automatic caching
export function withCache(cache: LLMCache) {
  return async function cachedLLMCall(
    fn: (prompt: string, model: string) => Promise<string>,
    prompt: string,
    model: string
  ): Promise<string> {
    // Check cache first
    const cached = await cache.get(prompt, model);
    if (cached) {
      await redis.incr("llm:stats:hits");
      return cached;
    }

    await redis.incr("llm:stats:misses");

    // Call LLM
    const response = await fn(prompt, model);

    // Cache response
    await cache.set(prompt, model, response);

    return response;
  };
}
'''

    def generate_cost_tracker(self) -> str:
        """Generate cost tracking code."""
        return '''
// LLM Cost Tracking Service

// Cost per 1K tokens (approximate, check provider pricing)
const MODEL_COSTS: Record<string, { input: number; output: number }> = {
  "gpt-4o": { input: 0.005, output: 0.015 },
  "gpt-4o-mini": { input: 0.00015, output: 0.0006 },
  "claude-3.5-sonnet": { input: 0.003, output: 0.015 },
  "claude-opus-4.5": { input: 0.015, output: 0.075 },
  "gemini-2.0-flash": { input: 0.0001, output: 0.0004 },
};

export function calculateCost(
  model: string,
  promptTokens: number,
  completionTokens: number
): number {
  const costs = MODEL_COSTS[model] || MODEL_COSTS["gpt-4o-mini"];

  const inputCost = (promptTokens / 1000) * costs.input;
  const outputCost = (completionTokens / 1000) * costs.output;

  return inputCost + outputCost;
}

export function selectOptimalModel(
  taskComplexity: "simple" | "medium" | "complex",
  budget: number
): string {
  if (taskComplexity === "simple" && budget < 0.001) {
    return "gpt-4o-mini";
  }

  if (taskComplexity === "medium") {
    return "claude-3.5-sonnet";
  }

  if (taskComplexity === "complex") {
    return "claude-opus-4.5";
  }

  return "gpt-4o";
}

export async function checkBudget(
  userId: string,
  estimatedCost: number
): Promise<{ allowed: boolean; remaining: number }> {
  // Implementation would check user's budget in database
  const monthlyBudget = 100; // $100/month default
  const currentSpend = 50; // Would come from database

  const remaining = monthlyBudget - currentSpend;

  return {
    allowed: estimatedCost <= remaining,
    remaining,
  };
}
'''


__all__ = ["MLOpsEngineer"]
