"""
Devora Orchestration - AI Engineer Agent
=========================================

Specialized agent for LLM integration, AI SDK implementation,
RAG pipelines, and prompt engineering.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import json

# Import from parent package
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.base_agent import BaseAgent, AgentConfig


@dataclass
class AIIntegrationSpec:
    """Specification for AI integration."""
    provider: str  # openai, anthropic, google, etc.
    model: str
    use_case: str  # chat, completion, embedding, etc.
    features: List[str]  # streaming, function_calling, vision, etc.
    rate_limits: Optional[Dict[str, int]] = None
    fallback_model: Optional[str] = None


class AIEngineer(BaseAgent):
    """
    AI Engineer Agent - Specialized in LLM integration and AI systems.

    Capabilities:
        - LLM provider integration (OpenAI, Anthropic, Google)
        - AI SDK implementation (Vercel AI SDK, LangChain)
        - RAG pipeline design and implementation
        - Prompt engineering and optimization
        - Embedding and vector search setup
        - AI-powered feature implementation
    """

    SYSTEM_PROMPT = """You are an expert AI Engineer specializing in LLM integration and AI systems.

Your expertise includes:
1. **LLM Integration**:
   - OpenAI API (GPT-4, GPT-4o, embeddings)
   - Anthropic API (Claude 3.5, Claude 4)
   - Google AI (Gemini 2.0)
   - OpenRouter for multi-provider access

2. **AI SDKs & Frameworks**:
   - Vercel AI SDK (useChat, useCompletion, StreamingTextResponse)
   - LangChain for complex chains
   - LlamaIndex for RAG
   - Vector databases (Pinecone, Supabase pgvector)

3. **RAG Pipelines**:
   - Document chunking strategies
   - Embedding generation
   - Semantic search implementation
   - Context retrieval optimization

4. **Prompt Engineering**:
   - System prompt design
   - Few-shot learning
   - Chain-of-thought prompting
   - Output formatting (JSON mode, structured output)

5. **Production Considerations**:
   - Rate limiting and retry logic
   - Token usage optimization
   - Cost management
   - Fallback strategies
   - Caching for embeddings

When implementing AI features:
- Use streaming for better UX
- Implement proper error handling for API failures
- Add retry logic with exponential backoff
- Consider token limits and context windows
- Optimize prompts for cost efficiency
- Cache embeddings when possible

Output code that is production-ready with proper TypeScript types."""

    def __init__(self, config: Optional[AgentConfig] = None):
        """Initialize AI Engineer agent."""
        super().__init__(
            name="ai_engineer",
            description="AI/ML integration specialist",
            config=config or AgentConfig()
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute AI engineering task.

        Args:
            context: Task context containing:
                - task: The AI task to perform
                - requirements: Specific requirements
                - existing_code: Current codebase context
                - provider: Preferred AI provider

        Returns:
            Dictionary with generated code and recommendations
        """
        task = context.get("task", "")
        requirements = context.get("requirements", [])
        provider = context.get("provider", "openrouter")

        prompt = f"""
Task: {task}

Requirements:
{json.dumps(requirements, indent=2)}

Provider: {provider}

Please provide:
1. Complete implementation code
2. Configuration setup
3. Environment variables needed
4. Usage examples
5. Error handling patterns
6. Cost optimization tips
"""

        result = await self.run(prompt)

        return {
            "success": True,
            "agent": self.name,
            "task": task,
            "implementation": result.get("content", ""),
            "provider": provider,
            "recommendations": self._extract_recommendations(result.get("content", ""))
        }

    def _extract_recommendations(self, content: str) -> List[str]:
        """Extract recommendations from generated content."""
        recommendations = []

        patterns = [
            "should consider",
            "recommend",
            "best practice",
            "important to",
            "don't forget"
        ]

        lines = content.split('\n')
        for line in lines:
            for pattern in patterns:
                if pattern.lower() in line.lower():
                    recommendations.append(line.strip())
                    break

        return recommendations[:5]  # Return top 5

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data."""
        return "task" in input_data

    def format_output(self, output: Dict[str, Any]) -> str:
        """Format output for display."""
        return json.dumps(output, indent=2)

    def generate_openrouter_client(self) -> str:
        """Generate OpenRouter client code."""
        return '''
import OpenAI from "openai";

const openrouter = new OpenAI({
  baseURL: "https://openrouter.ai/api/v1",
  apiKey: process.env.OPENROUTER_API_KEY,
  defaultHeaders: {
    "HTTP-Referer": process.env.APP_URL,
    "X-Title": "Devora App Builder",
  },
});

export async function generateWithAI(
  messages: { role: string; content: string }[],
  model: string = "anthropic/claude-3.5-sonnet"
) {
  const response = await openrouter.chat.completions.create({
    model,
    messages,
    temperature: 0.7,
    max_tokens: 4096,
  });

  return response.choices[0].message.content;
}

export async function streamWithAI(
  messages: { role: string; content: string }[],
  model: string = "anthropic/claude-3.5-sonnet"
) {
  const stream = await openrouter.chat.completions.create({
    model,
    messages,
    temperature: 0.7,
    max_tokens: 4096,
    stream: true,
  });

  return stream;
}
'''

    def generate_rag_pipeline(self) -> str:
        """Generate RAG pipeline code."""
        return '''
import { OpenAIEmbeddings } from "@langchain/openai";
import { SupabaseVectorStore } from "@langchain/community/vectorstores/supabase";
import { createClient } from "@supabase/supabase-js";

const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_ANON_KEY!
);

const embeddings = new OpenAIEmbeddings({
  openAIApiKey: process.env.OPENAI_API_KEY,
  modelName: "text-embedding-3-small",
});

export async function indexDocument(content: string, metadata: Record<string, any>) {
  const vectorStore = await SupabaseVectorStore.fromTexts(
    [content],
    [metadata],
    embeddings,
    {
      client: supabase,
      tableName: "documents",
      queryName: "match_documents",
    }
  );

  return vectorStore;
}

export async function searchSimilar(query: string, k: number = 5) {
  const vectorStore = new SupabaseVectorStore(embeddings, {
    client: supabase,
    tableName: "documents",
    queryName: "match_documents",
  });

  const results = await vectorStore.similaritySearch(query, k);
  return results;
}

export async function ragQuery(query: string) {
  // 1. Search for relevant documents
  const docs = await searchSimilar(query, 3);

  // 2. Build context from documents
  const context = docs.map(d => d.pageContent).join("\\n\\n");

  // 3. Generate response with context
  const response = await generateWithAI([
    {
      role: "system",
      content: `Use the following context to answer questions:\\n\\n${context}`
    },
    { role: "user", content: query }
  ]);

  return {
    answer: response,
    sources: docs.map(d => d.metadata),
  };
}
'''


__all__ = ["AIEngineer"]
