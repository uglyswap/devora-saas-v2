"""
Search & RAG Specialist Agent - Specialized in search and retrieval-augmented generation.

This agent is responsible for:
- Full-text search implementation (PostgreSQL, ElasticSearch)
- Vector database setup (Pinecone, Supabase pgvector)
- RAG pipeline creation
- Embedding optimization
- Semantic search
- Hybrid search strategies
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


class SearchRAGSpecialistAgent(BaseAgent):
    """
    Expert agent for search implementation and RAG systems.

    Specializations:
    - Full-text search (PostgreSQL, ElasticSearch)
    - Vector databases (pgvector, Pinecone, Weaviate)
    - Semantic search with embeddings
    - RAG (Retrieval-Augmented Generation) pipelines
    - Hybrid search (keyword + semantic)
    - Search relevance tuning
    - Embedding models optimization
    - Document chunking strategies
    - Re-ranking algorithms
    """

    def __init__(self, api_key: str, model: str = "openai/gpt-4o"):
        super().__init__("SearchRAGSpecialist", api_key, model)

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute search and RAG implementation tasks.

        Args:
            task: Dictionary containing:
                - search_type: Type of search (full_text, semantic, hybrid)
                - data_sources: What to search (documents, products, etc.)
                - rag_enabled: Whether to implement RAG
                - vector_db: Vector database choice

        Returns:
            Dictionary containing:
                - success: Boolean indicating success
                - files: Implementation files
                - configuration: Search configuration
                - raw_response: Full LLM response
        """
        search_type = task.get("search_type", "hybrid")
        data_sources = task.get("data_sources", [])
        rag_enabled = task.get("rag_enabled", False)
        vector_db = task.get("vector_db", "pgvector")

        system_prompt = self._get_system_prompt(search_type, vector_db)
        context = self._build_context(search_type, data_sources, rag_enabled, vector_db)

        messages = [{"role": "user", "content": context}]

        logger.info(f"[SearchRAGSpecialist] Implementing {search_type} search with {vector_db}...")

        response = await self.call_llm(messages, system_prompt)

        files = self._parse_code_blocks(response)

        logger.info(f"[SearchRAGSpecialist] Generated {len(files)} files")

        return {
            "success": True,
            "files": files,
            "search_type": search_type,
            "vector_db": vector_db,
            "rag_enabled": rag_enabled,
            "raw_response": response,
            "agent": self.name
        }

    async def implement_fulltext_search(self, tables: List[str], columns: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Implement PostgreSQL full-text search.

        Args:
            tables: Tables to make searchable
            columns: Columns to search in each table

        Returns:
            Full-text search implementation
        """
        system_prompt = """You are a PostgreSQL full-text search expert.

Implement search using:
1. **tsvector** columns for indexed search
2. **GIN indexes** for performance
3. **ts_rank** for relevance scoring
4. **Search configuration** for language support
5. **Triggers** to keep tsvector updated

Features to include:
- Prefix matching
- Fuzzy search (similarity)
- Weighted columns (title > content)
- Highlighting results
- Search suggestions
"""

        context = f"""Implement full-text search for:

Tables: {', '.join(tables)}

Columns to search:
{json.dumps(columns, indent=2)}

Generate:
1. Migration to add tsvector columns
2. GIN indexes for performance
3. Triggers to update tsvector on changes
4. Search function with ranking
5. TypeScript/SQL query examples
"""

        messages = [{"role": "user", "content": context}]
        response = await self.call_llm(messages, system_prompt)
        files = self._parse_code_blocks(response)

        return {
            "success": True,
            "files": files,
            "search_method": "full_text"
        }

    async def implement_vector_search(self, documents: List[str], embedding_model: str = "openai") -> Dict[str, Any]:
        """
        Implement vector/semantic search.

        Args:
            documents: Types of documents to search
            embedding_model: Embedding model to use

        Returns:
            Vector search implementation
        """
        system_prompt = """You are a vector search and embeddings expert.

Implement semantic search using:
1. **pgvector** extension for PostgreSQL
2. **Embeddings** from OpenAI/Cohere/local models
3. **Cosine similarity** for relevance
4. **Chunking** strategies for large documents
5. **Metadata filtering** for hybrid search

Best practices:
- Chunk size: 500-1000 tokens
- Overlap: 100-200 tokens
- Store metadata with vectors
- Use HNSW index for speed
- Normalize vectors for cosine similarity
"""

        context = f"""Implement vector search for:

Document types: {', '.join(documents)}
Embedding model: {embedding_model}

Generate:
1. Database schema with vector columns
2. Embedding generation service
3. Document chunking logic
4. Vector similarity search queries
5. Integration with application code
"""

        messages = [{"role": "user", "content": context}]
        response = await self.call_llm(messages, system_prompt)
        files = self._parse_code_blocks(response)

        return {
            "success": True,
            "files": files,
            "search_method": "vector",
            "embedding_model": embedding_model
        }

    async def implement_rag_pipeline(self, knowledge_base: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implement RAG (Retrieval-Augmented Generation) pipeline.

        Args:
            knowledge_base: Description of knowledge base to use

        Returns:
            Complete RAG implementation
        """
        system_prompt = """You are a RAG (Retrieval-Augmented Generation) expert.

Design a RAG pipeline with:
1. **Document ingestion** - Parse and chunk documents
2. **Embedding generation** - Create vector embeddings
3. **Vector storage** - Store in vector database
4. **Retrieval** - Find relevant chunks
5. **Re-ranking** - Improve relevance (optional)
6. **Context assembly** - Prepare context for LLM
7. **Generation** - Generate response with LLM
8. **Citation tracking** - Link responses to sources

Pipeline stages:
```
Documents → Chunking → Embeddings → Vector DB
                ↓
User Query → Embedding → Similarity Search → Top-K Chunks
                ↓
        Context + Query → LLM → Response + Citations
```

Include:
- Efficient chunk retrieval
- Context window management
- Source attribution
- Caching for common queries
"""

        context = f"""Implement RAG pipeline for:

{json.dumps(knowledge_base, indent=2)}

Generate:
1. Document ingestion service
2. Embedding and storage logic
3. Retrieval service with re-ranking
4. RAG query handler
5. API endpoints for RAG
6. Frontend integration example
"""

        messages = [{"role": "user", "content": context}]
        response = await self.call_llm(messages, system_prompt)
        files = self._parse_code_blocks(response)

        return {
            "success": True,
            "files": files,
            "pipeline_type": "rag"
        }

    async def implement_hybrid_search(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implement hybrid search combining keyword and semantic search.

        Args:
            config: Configuration for hybrid search weights

        Returns:
            Hybrid search implementation
        """
        system_prompt = """You are a hybrid search expert.

Combine full-text and vector search using:
1. **Parallel queries** - Run both searches simultaneously
2. **Score normalization** - Normalize scores to 0-1 range
3. **Weighted fusion** - Combine scores (e.g., 0.7 * semantic + 0.3 * keyword)
4. **Re-ranking** - Use cross-encoder for final ranking
5. **Metadata filtering** - Apply filters to both methods

Hybrid search formula:
```
final_score = alpha * semantic_score + (1 - alpha) * keyword_score
```

Optimal alpha depends on:
- Query type (keyword-heavy vs conceptual)
- Data characteristics
- User behavior analysis
"""

        context = f"""Implement hybrid search with:

{json.dumps(config, indent=2)}

Generate:
1. Hybrid search service
2. Score normalization functions
3. Weighted fusion logic
4. Query router (choose method based on query)
5. Performance optimization
6. A/B testing setup for tuning weights
"""

        messages = [{"role": "user", "content": context}]
        response = await self.call_llm(messages, system_prompt)
        files = self._parse_code_blocks(response)

        return {
            "success": True,
            "files": files,
            "search_method": "hybrid"
        }

    async def optimize_embeddings(self, use_case: str, constraints: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize embedding model selection and configuration.

        Args:
            use_case: Type of search use case
            constraints: Budget, latency, accuracy constraints

        Returns:
            Embedding optimization recommendations
        """
        system_prompt = """You are an embedding optimization expert.

Analyze trade-offs:
1. **Model size** vs **accuracy** vs **cost**
2. **Latency** requirements
3. **Multilingual** support needed
4. **Domain-specific** vs general models

Popular options:
- OpenAI text-embedding-3-small (1536d, fast, good quality)
- OpenAI text-embedding-3-large (3072d, slower, best quality)
- Cohere embed-english-v3.0 (1024d, good for hybrid search)
- Local models (sentence-transformers, slower but free)

Recommendations should include:
- Model selection with justification
- Dimension reduction strategies
- Caching strategies
- Batch processing for cost
- Model serving architecture
"""

        context = f"""Optimize embeddings for:

Use case: {use_case}
Constraints: {json.dumps(constraints, indent=2)}

Provide:
1. Model recommendations
2. Configuration settings
3. Cost analysis
4. Performance benchmarks
5. Implementation code
"""

        messages = [{"role": "user", "content": context}]
        response = await self.call_llm(messages, system_prompt)

        return {
            "success": True,
            "recommendations": response
        }

    def _get_system_prompt(self, search_type: str, vector_db: str) -> str:
        """Get the specialized system prompt for search and RAG."""
        return f"""You are an expert Search & RAG Specialist.

## Core Expertise:
- Full-text search (PostgreSQL, ElasticSearch)
- Vector search and embeddings
- RAG (Retrieval-Augmented Generation)
- Hybrid search strategies
- Search relevance optimization
- Document processing and chunking
- Re-ranking algorithms

## Technology Stack:
- **Database**: PostgreSQL with pgvector extension
- **Vector DB**: {vector_db}
- **Embeddings**: OpenAI, Cohere, or local models
- **Search Type**: {search_type}
- **LLM**: OpenAI GPT-4 for RAG

## Search Implementation Patterns:

### 1. PostgreSQL Full-Text Search:

```sql
-- filepath: migrations/add_fulltext_search.sql

-- Add tsvector column for search
ALTER TABLE documents
ADD COLUMN search_vector tsvector
GENERATED ALWAYS AS (
  setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
  setweight(to_tsvector('english', coalesce(content, '')), 'B') ||
  setweight(to_tsvector('english', coalesce(tags, '')), 'C')
) STORED;

-- Create GIN index for fast search
CREATE INDEX idx_documents_search ON documents USING GIN(search_vector);

-- Search function with ranking
CREATE OR REPLACE FUNCTION search_documents(query_text TEXT)
RETURNS TABLE (
  id UUID,
  title TEXT,
  content TEXT,
  rank REAL
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    d.id,
    d.title,
    d.content,
    ts_rank(d.search_vector, websearch_to_tsquery('english', query_text)) AS rank
  FROM documents d
  WHERE d.search_vector @@ websearch_to_tsquery('english', query_text)
  ORDER BY rank DESC
  LIMIT 20;
END;
$$ LANGUAGE plpgsql;

-- Search with highlighting
CREATE OR REPLACE FUNCTION search_documents_highlighted(query_text TEXT)
RETURNS TABLE (
  id UUID,
  title TEXT,
  headline TEXT,
  rank REAL
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    d.id,
    d.title,
    ts_headline('english', d.content, websearch_to_tsquery('english', query_text),
      'MaxWords=50, MinWords=25, ShortWord=3, HighlightAll=FALSE') AS headline,
    ts_rank(d.search_vector, websearch_to_tsquery('english', query_text)) AS rank
  FROM documents d
  WHERE d.search_vector @@ websearch_to_tsquery('english', query_text)
  ORDER BY rank DESC
  LIMIT 20;
END;
$$ LANGUAGE plpgsql;
```

### 2. Vector Search with pgvector:

```sql
-- filepath: migrations/add_vector_search.sql

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Add vector column
ALTER TABLE documents
ADD COLUMN embedding vector(1536); -- OpenAI ada-002 dimensions

-- Create HNSW index for fast similarity search
CREATE INDEX idx_documents_embedding ON documents
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Vector similarity search function
CREATE OR REPLACE FUNCTION search_similar_documents(
  query_embedding vector(1536),
  match_threshold FLOAT DEFAULT 0.7,
  match_count INT DEFAULT 10
)
RETURNS TABLE (
  id UUID,
  title TEXT,
  content TEXT,
  similarity FLOAT
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    d.id,
    d.title,
    d.content,
    1 - (d.embedding <=> query_embedding) AS similarity
  FROM documents d
  WHERE 1 - (d.embedding <=> query_embedding) > match_threshold
  ORDER BY d.embedding <=> query_embedding
  LIMIT match_count;
END;
$$ LANGUAGE plpgsql;
```

### 3. Embedding Service:

```typescript
// filepath: lib/embeddings.ts
import OpenAI from 'openai';

const openai = new OpenAI({{
  apiKey: process.env.OPENAI_API_KEY
}});

export const embeddingService = {{
  /**
   * Generate embeddings for text
   */
  async generateEmbedding(text: string): Promise<number[]> {{
    const response = await openai.embeddings.create({{
      model: 'text-embedding-3-small',
      input: text,
      encoding_format: 'float'
    }});

    return response.data[0].embedding;
  }},

  /**
   * Generate embeddings in batch (more efficient)
   */
  async generateBatchEmbeddings(texts: string[]): Promise<number[][]> {{
    const response = await openai.embeddings.create({{
      model: 'text-embedding-3-small',
      input: texts,
      encoding_format: 'float'
    }});

    return response.data.map(d => d.embedding);
  }},

  /**
   * Chunk large text for embedding
   */
  chunkText(text: string, chunkSize: number = 1000, overlap: number = 200): string[] {{
    const chunks: string[] = [];
    let start = 0;

    while (start < text.length) {{
      const end = Math.min(start + chunkSize, text.length);
      chunks.push(text.slice(start, end));
      start += chunkSize - overlap;
    }}

    return chunks;
  }}
}};
```

### 4. RAG Implementation:

```typescript
// filepath: lib/rag.ts
import {{ embeddingService }} from './embeddings';
import {{ supabase }} from './supabase';
import OpenAI from 'openai';

const openai = new OpenAI();

export const ragService = {{
  /**
   * Ingest document into RAG system
   */
  async ingestDocument(document: {{
    title: string;
    content: string;
    metadata?: Record<string, any>;
  }}) {{
    // 1. Chunk the document
    const chunks = embeddingService.chunkText(document.content);

    // 2. Generate embeddings for each chunk
    const embeddings = await embeddingService.generateBatchEmbeddings(chunks);

    // 3. Store chunks with embeddings
    const chunkRecords = chunks.map((chunk, i) => ({{
      title: document.title,
      content: chunk,
      embedding: embeddings[i],
      metadata: document.metadata,
      chunk_index: i
    }}));

    const {{ data, error }} = await supabase
      .from('document_chunks')
      .insert(chunkRecords);

    if (error) throw error;
    return data;
  }},

  /**
   * Query RAG system
   */
  async query(question: string, options?: {{
    topK?: number;
    threshold?: number;
  }}) {{
    // 1. Generate embedding for question
    const queryEmbedding = await embeddingService.generateEmbedding(question);

    // 2. Find similar chunks
    const {{ data: chunks, error }} = await supabase.rpc('search_similar_documents', {{
      query_embedding: queryEmbedding,
      match_threshold: options?.threshold ?? 0.7,
      match_count: options?.topK ?? 5
    }});

    if (error) throw error;

    // 3. Prepare context from chunks
    const context = chunks
      .map(chunk => `[Source: ${{chunk.title}}]\\n${{chunk.content}}`)
      .join('\\n\\n---\\n\\n');

    // 4. Generate answer with LLM
    const response = await openai.chat.completions.create({{
      model: 'gpt-4',
      messages: [
        {{
          role: 'system',
          content: `You are a helpful assistant. Answer questions based on the provided context.
          If the context doesn't contain relevant information, say so.
          Always cite your sources using [Source: title].`
        }},
        {{
          role: 'user',
          content: `Context:\\n${{context}}\\n\\nQuestion: ${{question}}`
        }}
      ],
      temperature: 0.7
    }});

    return {{
      answer: response.choices[0].message.content,
      sources: chunks.map(c => ({{
        title: c.title,
        content: c.content,
        similarity: c.similarity
      }}))
    }};
  }}
}};
```

### 5. Hybrid Search:

```typescript
// filepath: lib/search/hybrid.ts
import {{ embeddingService }} from '../embeddings';
import {{ supabase }} from '../supabase';

export const hybridSearch = {{
  async search(query: string, options?: {{
    alpha?: number; // Weight for semantic search (0-1)
    limit?: number;
  }}) {{
    const alpha = options?.alpha ?? 0.7;
    const limit = options?.limit ?? 20;

    // 1. Run keyword search
    const {{ data: keywordResults }} = await supabase
      .rpc('search_documents', {{ query_text: query }});

    // 2. Run semantic search
    const queryEmbedding = await embeddingService.generateEmbedding(query);
    const {{ data: semanticResults }} = await supabase
      .rpc('search_similar_documents', {{
        query_embedding: queryEmbedding,
        match_count: limit
      }});

    // 3. Normalize scores
    const normalizedKeyword = this.normalizeScores(
      keywordResults.map(r => ({{ id: r.id, score: r.rank }}))
    );
    const normalizedSemantic = this.normalizeScores(
      semanticResults.map(r => ({{ id: r.id, score: r.similarity }}))
    );

    // 4. Combine scores
    const combinedScores = new Map<string, number>();

    normalizedKeyword.forEach(({{ id, score }}) => {{
      combinedScores.set(id, (1 - alpha) * score);
    }});

    normalizedSemantic.forEach(({{ id, score }}) => {{
      const current = combinedScores.get(id) ?? 0;
      combinedScores.set(id, current + alpha * score);
    }});

    // 5. Sort by combined score and return
    const rankedIds = Array.from(combinedScores.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, limit)
      .map(([id]) => id);

    // 6. Fetch full documents
    const {{ data: documents }} = await supabase
      .from('documents')
      .select('*')
      .in('id', rankedIds);

    return documents;
  }},

  normalizeScores(scores: {{ id: string; score: number }}[]) {{
    const max = Math.max(...scores.map(s => s.score));
    const min = Math.min(...scores.map(s => s.score));
    const range = max - min || 1;

    return scores.map(s => ({{
      id: s.id,
      score: (s.score - min) / range
    }}));
  }}
}};
```

## Output Format:

```sql
-- filepath: migrations/xxx_search_setup.sql
[Search infrastructure]
```

```typescript
// filepath: lib/search/index.ts
[Search service implementation]
```

```typescript
// filepath: lib/embeddings.ts
[Embedding generation service]
```

```typescript
// filepath: lib/rag.ts
[RAG pipeline implementation]
```

```markdown
# filepath: SEARCH.md
[Documentation and usage examples]
```

## Best Practices:
1. **Chunking**: 500-1000 tokens with 100-200 overlap
2. **Indexing**: Use HNSW for vectors, GIN for full-text
3. **Caching**: Cache embeddings and common queries
4. **Monitoring**: Track search quality and latency
5. **Relevance**: Tune weights based on user feedback
6. **Security**: RLS on search tables
7. **Cost**: Batch embeddings, cache aggressively
8. **Quality**: Implement re-ranking for top results
9. **UX**: Show sources and confidence scores
10. **Testing**: A/B test search algorithms

Generate production-ready search and RAG implementation."""

    def _build_context(self, search_type: str, data_sources: List[str],
                      rag_enabled: bool, vector_db: str) -> str:
        """Build the context message for the LLM."""
        return f"""Implement comprehensive search functionality.

## Search Type: {search_type}
- full_text: PostgreSQL full-text search only
- semantic: Vector/embedding search only
- hybrid: Combine keyword and semantic search

## Data Sources to Search:
{json.dumps(data_sources, indent=2)}

## RAG Enabled: {rag_enabled}

## Vector Database: {vector_db}

## Deliverables Required:

1. **Database Schema** (migrations/)
   - Search tables and indexes
   - Vector columns (if semantic/hybrid)
   - Full-text search vectors
   - Metadata for filtering

2. **Search Service** (lib/search/)
   - Search functions
   - Query parsing
   - Result ranking
   - Filters and facets

3. **Embedding Service** (lib/embeddings.ts)
   - Embedding generation
   - Batch processing
   - Chunking logic
   - Caching layer

4. **RAG Pipeline** (lib/rag.ts) - if enabled
   - Document ingestion
   - Chunk retrieval
   - Context assembly
   - LLM integration
   - Source attribution

5. **API Endpoints** (api/search/)
   - Search endpoint
   - Autocomplete/suggestions
   - Document upload (for RAG)
   - Analytics tracking

6. **Frontend Integration** (components/search/)
   - Search input component
   - Results display
   - Filters UI
   - Highlighting

7. **Documentation** (SEARCH.md)
   - Architecture overview
   - Usage examples
   - Performance tuning
   - Cost optimization

Generate complete, production-ready search implementation."""

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
                    'sql': 'sql', 'typescript': 'ts', 'ts': 'ts',
                    'javascript': 'js', 'python': 'py', 'markdown': 'md'
                }
                ext = ext_map.get(language, 'txt')
                filepath = f"search.{ext}"

            filepath = filepath.strip()

            if not language:
                ext_to_lang = {
                    '.sql': 'sql', '.ts': 'typescript', '.tsx': 'typescript',
                    '.js': 'javascript', '.py': 'python', '.md': 'markdown'
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
                "type": "search"
            })

        return files


if __name__ == "__main__":
    # Example usage
    import asyncio
    import os

    async def test_agent():
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            print("Error: OPENROUTER_API_KEY not set")
            return

        agent = SearchRAGSpecialistAgent(api_key)

        task = {
            "search_type": "hybrid",
            "data_sources": [
                "Documentation pages",
                "Blog posts",
                "Product descriptions",
                "User-generated content"
            ],
            "rag_enabled": True,
            "vector_db": "pgvector"
        }

        result = await agent.execute(task)

        print(f"\nSuccess: {result['success']}")
        print(f"Search Type: {result['search_type']}")
        print(f"Vector DB: {result['vector_db']}")
        print(f"RAG Enabled: {result['rag_enabled']}")
        print(f"\nGenerated {len(result['files'])} files:")
        for file in result['files']:
            print(f"\n--- {file['name']} ({file['language']}) ---")
            print(file['content'][:200] + "..." if len(file['content']) > 200 else file['content'])

    asyncio.run(test_agent())
