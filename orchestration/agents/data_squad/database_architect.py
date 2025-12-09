"""
Database Architect Agent - Specialized in PostgreSQL/MongoDB schema design and optimization.

This agent is responsible for:
- Designing PostgreSQL schemas (Supabase)
- Creating and optimizing database migrations
- Implementing Row Level Security (RLS) policies
- Optimizing indexes and query performance
- Designing data models and relationships
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


class DatabaseArchitectAgent(BaseAgent):
    """
    Expert agent for database architecture and schema design.

    Specializations:
    - PostgreSQL schema design (Supabase)
    - MongoDB schema design (when needed)
    - Database migrations and versioning
    - Row Level Security (RLS) policies
    - Index optimization and query performance
    - Data modeling and normalization
    - Foreign key relationships and constraints
    - TypeScript type generation from schemas
    - Database triggers and functions
    """

    def __init__(self, api_key: str, model: str = "openai/gpt-4o"):
        super().__init__("DatabaseArchitect", api_key, model)

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute database architecture tasks.

        Args:
            task: Dictionary containing:
                - architecture: Overall system architecture
                - data_models: List of data models to create
                - features: Features requiring database support
                - optimization_target: Performance optimization goals

        Returns:
            Dictionary containing:
                - success: Boolean indicating success
                - files: List of generated migration files
                - types: TypeScript type definitions
                - indexes: Index recommendations
                - raw_response: Full LLM response
        """
        architecture = task.get("architecture", {})
        data_models = task.get("data_models", [])
        features = task.get("features", [])
        optimization_target = task.get("optimization_target", "balanced")

        system_prompt = self._get_system_prompt()
        context = self._build_context(architecture, data_models, features, optimization_target)

        messages = [{"role": "user", "content": context}]

        logger.info(f"[DatabaseArchitect] Designing schema for {len(data_models)} models...")

        response = await self.call_llm(messages, system_prompt)

        files = self._parse_code_blocks(response)

        logger.info(f"[DatabaseArchitect] Generated {len(files)} file(s)")

        return {
            "success": True,
            "files": files,
            "raw_response": response,
            "agent": self.name
        }

    async def generate_migration(self, changes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a database migration for schema changes.

        Args:
            changes: Dictionary describing the changes to make

        Returns:
            Migration SQL files (up and down)
        """
        system_prompt = """You are a database migration expert.

Generate safe, reversible migrations that:
1. Handle data preservation during schema changes
2. Include both UP and DOWN migrations
3. Use transactions where appropriate
4. Handle edge cases (NULL values, data type changes)
5. Include rollback strategies

Format:
```sql
-- filepath: migrations/{timestamp}_migration_name.up.sql
[UP migration]
```

```sql
-- filepath: migrations/{timestamp}_migration_name.down.sql
[DOWN migration]
```"""

        context = f"""Generate migration for these changes:

{json.dumps(changes, indent=2)}

Requirements:
- Preserve existing data
- Handle NULL values appropriately
- Use transactions
- Include rollback strategy
"""

        messages = [{"role": "user", "content": context}]
        response = await self.call_llm(messages, system_prompt)
        files = self._parse_code_blocks(response)

        return {
            "success": True,
            "files": files,
            "migration_type": changes.get("type", "schema_change")
        }

    async def optimize_indexes(self, queries: List[str], tables: List[str]) -> Dict[str, Any]:
        """
        Analyze queries and recommend index optimizations.

        Args:
            queries: List of SQL queries to optimize
            tables: List of table names to analyze

        Returns:
            Index recommendations and optimization strategies
        """
        system_prompt = """You are a database performance optimization expert.

Analyze queries and recommend:
1. Missing indexes
2. Composite indexes for multi-column queries
3. Partial indexes for filtered queries
4. Index removal recommendations (unused indexes)
5. EXPLAIN ANALYZE interpretation

Provide:
- Index creation SQL
- Performance impact estimation
- Trade-offs (write performance vs read performance)

Format:
```sql
-- filepath: migrations/optimize_indexes.sql
[Index creation statements with comments explaining why]
```"""

        context = f"""Analyze and optimize these queries:

## Queries:
{chr(10).join(f'{i+1}. {q}' for i, q in enumerate(queries))}

## Tables:
{', '.join(tables)}

Provide index recommendations with justification."""

        messages = [{"role": "user", "content": context}]
        response = await self.call_llm(messages, system_prompt)
        files = self._parse_code_blocks(response)

        return {
            "success": True,
            "files": files,
            "recommendations": response
        }

    async def design_rls_policies(self, table: str, access_pattern: str, roles: List[str]) -> Dict[str, Any]:
        """
        Design comprehensive Row Level Security policies.

        Args:
            table: Table name to secure
            access_pattern: Type of access pattern (user_owned, team_based, etc.)
            roles: List of user roles to consider

        Returns:
            Complete RLS policy definitions
        """
        system_prompt = """You are a database security expert specializing in Row Level Security.

Design comprehensive RLS policies that:
1. Follow principle of least privilege
2. Handle all CRUD operations appropriately
3. Consider role-based access control
4. Include policy for SELECT, INSERT, UPDATE, DELETE
5. Use efficient policy checks (avoid N+1 queries)

Common patterns:
- user_owned: auth.uid() = user_id
- team_based: Check team membership
- hierarchical: Parent-child relationships
- time_based: Valid date ranges
- status_based: Based on record status

Format:
```sql
-- filepath: migrations/rls_{table_name}.sql
[Complete RLS policies with explanatory comments]
```"""

        context = f"""Design RLS policies for:

Table: {table}
Access Pattern: {access_pattern}
Roles: {', '.join(roles)}

Include all necessary policies (SELECT, INSERT, UPDATE, DELETE) with proper security checks."""

        messages = [{"role": "user", "content": context}]
        response = await self.call_llm(messages, system_prompt)
        files = self._parse_code_blocks(response)

        return {
            "success": True,
            "files": files,
            "table": table,
            "access_pattern": access_pattern
        }

    async def generate_types(self, schema: str, language: str = "typescript") -> Dict[str, Any]:
        """
        Generate type definitions from database schema.

        Args:
            schema: SQL schema definition
            language: Target language (typescript, python, etc.)

        Returns:
            Type definition files
        """
        system_prompt = f"""Generate {language} types from SQL schema.

For TypeScript:
- Row types (complete record)
- Insert types (without auto-generated fields)
- Update types (all fields optional)
- Database interface with all tables
- Proper null handling
- Enums for text constraints

For Python:
- Pydantic models
- SQLAlchemy models
- Proper type hints

Format:
```{language}
// filepath: types/database.{language.split('script')[0]}
[Type definitions]
```"""

        messages = [{"role": "user", "content": f"Generate {language} types from:\n\n{schema}"}]
        response = await self.call_llm(messages, system_prompt)
        files = self._parse_code_blocks(response)

        return {
            "success": True,
            "files": files,
            "language": language
        }

    def _get_system_prompt(self) -> str:
        """Get the specialized system prompt for database architecture."""
        return """You are an expert Database Architect specializing in modern SaaS applications.

## Core Expertise:
- PostgreSQL (Supabase) with advanced features
- MongoDB for document storage when needed
- Database normalization and denormalization strategies
- Row Level Security (RLS) implementation
- Migration strategies and versioning
- Performance optimization and indexing
- Data modeling and relationships

## Technology Stack:
- **Primary**: Supabase (PostgreSQL)
- **Auth**: Supabase Auth with RLS
- **Storage**: Supabase Storage for files
- **Realtime**: Supabase Realtime subscriptions
- **Edge Functions**: Supabase Edge Functions for complex operations

## Database Design Principles:

### 1. Table Structure:
```sql
-- Standard table template
create table public.table_name (
  -- Primary key (prefer UUIDs for distributed systems)
  id uuid default gen_random_uuid() primary key,

  -- Foreign keys with proper cascade behavior
  user_id uuid references public.users(id) on delete cascade not null,

  -- Business columns with appropriate types
  name text not null,
  description text,
  metadata jsonb default '{}'::jsonb,

  -- Status/state management
  status text default 'active' check (status in ('active', 'archived', 'deleted')),

  -- Audit columns (always include)
  created_at timestamp with time zone default now() not null,
  updated_at timestamp with time zone default now() not null,
  created_by uuid references public.users(id),
  updated_by uuid references public.users(id)
);

-- Enable RLS (security first!)
alter table public.table_name enable row level security;

-- Indexes for common queries
create index idx_table_name_user_id on public.table_name(user_id);
create index idx_table_name_status on public.table_name(status) where status = 'active';
create index idx_table_name_created_at on public.table_name(created_at desc);
```

### 2. Row Level Security Patterns:

```sql
-- Pattern 1: User-owned data
create policy "Users manage own records"
  on public.table_name for all
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

-- Pattern 2: Team-based access
create policy "Team members can view"
  on public.table_name for select
  using (
    exists (
      select 1 from public.team_members
      where team_id = table_name.team_id
      and user_id = auth.uid()
    )
  );

-- Pattern 3: Role-based access
create policy "Admins have full access"
  on public.table_name for all
  using (
    exists (
      select 1 from public.user_roles
      where user_id = auth.uid()
      and role = 'admin'
    )
  );

-- Pattern 4: Public read, authenticated write
create policy "Public can read"
  on public.table_name for select
  using (true);

create policy "Authenticated can create"
  on public.table_name for insert
  with check (auth.uid() is not null);
```

### 3. Performance Optimization:

```sql
-- Composite indexes for multi-column queries
create index idx_composite on public.table_name(user_id, status, created_at desc);

-- Partial indexes for filtered queries
create index idx_active_only on public.table_name(user_id)
where status = 'active';

-- GIN indexes for JSONB columns
create index idx_metadata on public.table_name using gin(metadata);

-- Full-text search indexes
create index idx_search on public.table_name
using gin(to_tsvector('english', name || ' ' || coalesce(description, '')));
```

### 4. Triggers and Functions:

```sql
-- Auto-update updated_at timestamp
create or replace function public.handle_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql security definer;

create trigger on_table_update
  before update on public.table_name
  for each row execute function public.handle_updated_at();

-- Soft delete pattern
create or replace function public.soft_delete()
returns trigger as $$
begin
  update public.table_name
  set status = 'deleted', updated_at = now()
  where id = old.id;
  return null;
end;
$$ language plpgsql security definer;

create trigger on_table_delete
  before delete on public.table_name
  for each row execute function public.soft_delete();
```

### 5. Common SaaS Patterns:

```sql
-- Multi-tenancy (Team/Organization)
create table public.organizations (
  id uuid default gen_random_uuid() primary key,
  name text not null,
  slug text unique not null,
  plan text default 'free',
  created_at timestamp with time zone default now()
);

create table public.organization_members (
  organization_id uuid references public.organizations(id) on delete cascade,
  user_id uuid references public.users(id) on delete cascade,
  role text default 'member' check (role in ('owner', 'admin', 'member')),
  joined_at timestamp with time zone default now(),
  primary key (organization_id, user_id)
);

-- Subscription/Billing
create table public.subscriptions (
  id uuid default gen_random_uuid() primary key,
  organization_id uuid references public.organizations(id) on delete cascade unique,
  stripe_customer_id text unique,
  stripe_subscription_id text unique,
  plan text default 'free',
  status text default 'inactive',
  current_period_start timestamp with time zone,
  current_period_end timestamp with time zone,
  cancel_at timestamp with time zone
);

-- Usage/Metering
create table public.usage_records (
  id uuid default gen_random_uuid() primary key,
  organization_id uuid references public.organizations(id) on delete cascade,
  metric text not null,
  quantity integer not null default 1,
  recorded_at timestamp with time zone default now()
);

create index idx_usage_org_metric on public.usage_records(organization_id, metric, recorded_at desc);
```

## Output Format:

Always structure your response with clear file paths:

```sql
-- filepath: supabase/migrations/001_initial_schema.sql
[Table definitions and basic structure]
```

```sql
-- filepath: supabase/migrations/002_rls_policies.sql
[Row Level Security policies]
```

```sql
-- filepath: supabase/migrations/003_indexes.sql
[Index optimizations]
```

```sql
-- filepath: supabase/migrations/004_functions_triggers.sql
[Functions and triggers]
```

```typescript
// filepath: types/database.ts
[TypeScript type definitions]
```

## Best Practices:
1. **Security First**: Enable RLS on all tables, no exceptions
2. **Audit Trail**: Include created_at, updated_at, created_by, updated_by
3. **Soft Deletes**: Use status fields instead of hard deletes when possible
4. **JSONB for Flexibility**: Use JSONB for metadata and extensibility
5. **Proper Indexes**: Index foreign keys and frequently queried columns
6. **Constraints**: Use CHECK constraints for data validation
7. **Cascading**: Define proper ON DELETE behavior
8. **Naming**: Use snake_case for SQL, clear and descriptive names
9. **Comments**: Document complex logic and business rules
10. **Migrations**: Always provide reversible migrations

Generate production-ready, secure, and performant database schemas."""

    def _build_context(self, architecture: Dict[str, Any], data_models: List[Dict[str, Any]],
                      features: List[str], optimization_target: str) -> str:
        """Build the context message for the LLM."""
        return f"""Design a complete database architecture for this application.

## System Architecture:
{json.dumps(architecture, indent=2)}

## Data Models to Implement:
{json.dumps(data_models, indent=2)}

## Features Requiring Database Support:
{json.dumps(features, indent=2)}

## Optimization Target: {optimization_target}
- 'read_heavy': Optimize for read performance (more indexes, denormalization)
- 'write_heavy': Optimize for write performance (fewer indexes, normalization)
- 'balanced': Balance between read and write performance
- 'realtime': Optimize for realtime subscriptions and updates

## Deliverables Required:

1. **Complete Schema** (migrations/001_initial_schema.sql)
   - All tables with proper types
   - Foreign key relationships
   - Constraints and validations
   - Default values

2. **RLS Policies** (migrations/002_rls_policies.sql)
   - Comprehensive security policies
   - Role-based access control
   - User and team isolation

3. **Performance Indexes** (migrations/003_indexes.sql)
   - Indexes for common queries
   - Composite indexes where needed
   - Partial indexes for filtered queries
   - Full-text search if applicable

4. **Functions & Triggers** (migrations/004_functions_triggers.sql)
   - updated_at trigger
   - Soft delete logic
   - Custom business logic functions

5. **TypeScript Types** (types/database.ts)
   - Row types (complete records)
   - Insert types (without auto-generated fields)
   - Update types (all fields optional)
   - Database interface

6. **Documentation** (DATABASE.md)
   - Schema overview
   - Relationship diagram (as text/mermaid)
   - RLS policy explanations
   - Common queries examples

Generate a complete, production-ready database architecture."""

    def _parse_code_blocks(self, response: str) -> List[Dict[str, str]]:
        """Parse code blocks with filepath comments from LLM response."""
        files = []

        # Match code blocks with various languages
        pattern = r'```(\w+)?\n(?:--\s*filepath:\s*(.+?)\n|\/\/\s*filepath:\s*(.+?)\n|#\s*filepath:\s*(.+?)\n)?([\s\S]*?)```'

        matches = re.findall(pattern, response)

        for match in matches:
            language, sql_path, ts_path, py_path, code = match
            code = code.strip()

            if not code:
                continue

            # Determine filepath
            filepath = sql_path or ts_path or py_path

            if not filepath:
                # Try to extract from first line of code
                first_line = code.split('\n')[0] if code else ''
                if 'filepath:' in first_line.lower():
                    filepath = first_line.split('filepath:')[-1].strip()
                    # Remove the filepath line from code
                    code = '\n'.join(code.split('\n')[1:]).strip()

            if not filepath:
                # Determine from language
                ext_map = {
                    'sql': 'sql',
                    'typescript': 'ts',
                    'ts': 'ts',
                    'python': 'py',
                    'markdown': 'md'
                }
                ext = ext_map.get(language, 'txt')
                filepath = f"generated.{ext}"

            filepath = filepath.strip()

            # Determine language from filepath if not set
            if not language:
                if filepath.endswith('.sql'):
                    language = 'sql'
                elif filepath.endswith(('.ts', '.tsx')):
                    language = 'typescript'
                elif filepath.endswith('.py'):
                    language = 'python'
                elif filepath.endswith('.md'):
                    language = 'markdown'
                else:
                    language = 'text'

            files.append({
                "name": filepath,
                "content": code,
                "language": language,
                "type": "migration" if "migration" in filepath else "type" if "type" in filepath else "other"
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

        agent = DatabaseArchitectAgent(api_key)

        task = {
            "architecture": {
                "type": "SaaS",
                "multi_tenant": True,
                "auth": "supabase"
            },
            "data_models": [
                {
                    "name": "Project",
                    "fields": {
                        "name": "string",
                        "description": "text",
                        "status": "enum(draft,active,archived)"
                    },
                    "relations": ["user_id -> users.id"]
                },
                {
                    "name": "Task",
                    "fields": {
                        "title": "string",
                        "completed": "boolean",
                        "due_date": "timestamp"
                    },
                    "relations": [
                        "project_id -> projects.id",
                        "assigned_to -> users.id"
                    ]
                }
            ],
            "features": [
                "User authentication",
                "Project management",
                "Task tracking",
                "Team collaboration"
            ],
            "optimization_target": "balanced"
        }

        result = await agent.execute(task)

        print(f"\nSuccess: {result['success']}")
        print(f"\nGenerated {len(result['files'])} files:")
        for file in result['files']:
            print(f"\n--- {file['name']} ({file['language']}) ---")
            print(file['content'][:200] + "..." if len(file['content']) > 200 else file['content'])

    asyncio.run(test_agent())
