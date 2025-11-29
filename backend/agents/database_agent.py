from .base_agent import BaseAgent
from typing import Dict, Any, List
import json
import re
import logging

logger = logging.getLogger(__name__)

class DatabaseAgent(BaseAgent):
    """Agent specialized in generating Supabase database schemas and configurations.
    
    Expertise:
    - PostgreSQL schema design
    - Supabase Row Level Security (RLS) policies
    - Database migrations
    - Indexes for performance
    - Foreign keys and relations
    - TypeScript types from schema
    - Supabase Edge Functions
    """
    
    def __init__(self, api_key: str, model: str = "openai/gpt-4o"):
        super().__init__("Database", api_key, model)
        
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate database schema and configurations"""
        architecture = task.get("architecture", {})
        data_models = task.get("data_models", [])
        features = task.get("features", [])
        
        system_prompt = """You are an expert Supabase/PostgreSQL database architect.
Your specialty is designing secure, scalable database schemas with proper RLS policies.

## Tech Stack:
- Supabase (PostgreSQL)
- Row Level Security (RLS)
- TypeScript type generation
- Database migrations

## Guidelines:

### Table Design:
```sql
-- Always include these columns
create table public.users (
  id uuid references auth.users primary key,
  email text unique not null,
  full_name text,
  avatar_url text,
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone default now()
);

-- Enable RLS
alter table public.users enable row level security;
```

### RLS Policies:
```sql
-- Users can read their own data
create policy "Users can view own data"
  on public.users for select
  using (auth.uid() = id);

-- Users can update their own data
create policy "Users can update own data"
  on public.users for update
  using (auth.uid() = id);
```

### Common Patterns:

1. **User-owned data**:
```sql
create table public.projects (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references public.users(id) on delete cascade not null,
  name text not null,
  created_at timestamp with time zone default now()
);

create policy "Users can CRUD own projects"
  on public.projects for all
  using (auth.uid() = user_id);
```

2. **Team/Organization data**:
```sql
create table public.team_members (
  team_id uuid references public.teams(id) on delete cascade,
  user_id uuid references public.users(id) on delete cascade,
  role text default 'member',
  primary key (team_id, user_id)
);
```

3. **Subscription/Billing**:
```sql
create table public.subscriptions (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references public.users(id) on delete cascade unique,
  stripe_customer_id text unique,
  stripe_subscription_id text unique,
  status text default 'inactive',
  plan text default 'free',
  current_period_end timestamp with time zone
);
```

### Indexes:
```sql
-- Add indexes for frequently queried columns
create index idx_projects_user_id on public.projects(user_id);
create index idx_projects_created_at on public.projects(created_at desc);
```

### Triggers:
```sql
-- Auto-update updated_at
create or replace function public.handle_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

create trigger on_update
  before update on public.users
  for each row execute function public.handle_updated_at();
```

## Output Format:

```sql
-- filepath: supabase/migrations/001_initial_schema.sql
[SQL code]
```

```typescript
// filepath: types/database.ts
[TypeScript types]
```

```sql
-- filepath: supabase/migrations/002_rls_policies.sql
[RLS policies]
```

Always include filepath comments."""

        context = f"""## Architecture:
{json.dumps(architecture, indent=2)}

## Data Models:
{json.dumps(data_models, indent=2)}

## Features Requiring Database:
{json.dumps(features, indent=2)}

---
Generate complete database schema including:
1. All tables with proper columns and types
2. Foreign key relationships
3. RLS policies for security
4. Indexes for performance
5. Triggers for automation
6. TypeScript types for the schema
"""
        
        messages = [{"role": "user", "content": context}]
        
        logger.info(f"[Database] Generating schema for {len(data_models)} models...")
        
        response = await self.call_llm(messages, system_prompt)
        
        files = self.parse_code_blocks(response)
        
        logger.info(f"[Database] Generated {len(files)} file(s)")
        
        return {
            "success": True,
            "files": files,
            "raw_response": response
        }
    
    async def generate_types(self, schema: str) -> Dict[str, Any]:
        """Generate TypeScript types from SQL schema"""
        system_prompt = """Generate TypeScript types from the SQL schema.

Create:
1. Table types (Row, Insert, Update)
2. Database type with all tables
3. Proper null handling
4. Relation types

Format:
```typescript
// filepath: types/database.ts
[code]
```"""
        
        messages = [{"role": "user", "content": f"Generate types from schema:\n\n{schema}"}]
        
        response = await self.call_llm(messages, system_prompt)
        files = self.parse_code_blocks(response)
        
        return {
            "success": True,
            "files": files
        }
    
    async def generate_rls_policies(self, table_name: str, access_pattern: str) -> Dict[str, Any]:
        """Generate RLS policies for a specific table"""
        system_prompt = f"""Generate RLS policies for table '{table_name}'.

Access pattern: {access_pattern}

Common patterns:
- 'user_owned': Users can only access their own data
- 'team_based': Team members can access team data
- 'public_read': Anyone can read, only owner can write
- 'admin_only': Only admins can access

Generate all necessary policies (select, insert, update, delete).

Format:
```sql
-- filepath: supabase/migrations/xxx_rls_{table_name}.sql
[code]
```"""
        
        messages = [{"role": "user", "content": f"Generate RLS for {table_name} with {access_pattern} pattern"}]
        
        response = await self.call_llm(messages, system_prompt)
        files = self.parse_code_blocks(response)
        
        return {
            "success": True,
            "files": files
        }
    
    def parse_code_blocks(self, response: str) -> List[Dict[str, str]]:
        """Parse code blocks with filepath comments"""
        files = []
        
        # Match both SQL and TypeScript blocks
        pattern = r'```(sql|typescript|ts)?\n(?:--\s*filepath:\s*(.+?)\n|\/\/\s*filepath:\s*(.+?)\n)?([\s\S]*?)```'
        
        matches = re.findall(pattern, response)
        
        for match in matches:
            language, sql_path, ts_path, code = match
            code = code.strip()
            
            if not code:
                continue
            
            filepath = sql_path or ts_path
            
            if filepath:
                filepath = filepath.strip()
            else:
                # Try to extract from first comment
                first_line = code.split('\n')[0] if code else ''
                if 'filepath:' in first_line.lower():
                    filepath = first_line.split('filepath:')[1].strip()
                else:
                    ext = 'sql' if language == 'sql' else 'ts'
                    filepath = f"schema.{ext}"
            
            if not language:
                language = 'sql' if filepath.endswith('.sql') else 'typescript'
            
            files.append({
                "name": filepath,
                "content": code,
                "language": language
            })
        
        return files
