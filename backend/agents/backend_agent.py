from .base_agent import BaseAgent
from typing import Dict, Any, List
import json
import re
import logging

logger = logging.getLogger(__name__)

class BackendAgent(BaseAgent):
    """Agent specialized in generating Next.js API routes and backend logic.
    
    Expertise:
    - Next.js API Routes (App Router)
    - Server Actions
    - Authentication (NextAuth, Supabase Auth)
    - Stripe integration (webhooks, checkout, billing)
    - Middleware for protected routes
    - Rate limiting
    - Error handling
    - TypeScript
    """
    
    def __init__(self, api_key: str, model: str = "openai/gpt-4o"):
        super().__init__("Backend", api_key, model)
        
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate backend code based on architecture"""
        architecture = task.get("architecture", {})
        endpoints = task.get("endpoints", [])
        integrations = task.get("integrations", [])
        data_models = task.get("data_models", [])
        
        system_prompt = """You are an expert Next.js backend developer.
Your specialty is creating secure, scalable API routes and server-side logic.

## Tech Stack:
- Next.js 14+ API Routes (App Router)
- TypeScript (strict mode)
- Supabase for database & auth
- Stripe for payments
- Zod for validation
- Server Actions for mutations

## API Routes Structure (App Router):
```
app/
  api/
    auth/
      [...nextauth]/route.ts   # NextAuth handler
      callback/route.ts        # Auth callbacks
    user/
      route.ts                 # GET, POST user
      [id]/route.ts            # GET, PUT, DELETE user by id
    stripe/
      webhook/route.ts         # Stripe webhooks
      checkout/route.ts        # Create checkout session
      portal/route.ts          # Customer portal
    [resource]/
      route.ts                 # CRUD operations
```

## Guidelines:

### Route Handlers:
```typescript
import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'

export async function GET(request: NextRequest) {
  try {
    const supabase = createClient()
    // ... logic
    return NextResponse.json({ data })
  } catch (error) {
    return NextResponse.json({ error: 'Error message' }, { status: 500 })
  }
}
```

### Server Actions:
```typescript
'use server'

import { revalidatePath } from 'next/cache'
import { createClient } from '@/lib/supabase/server'

export async function createItem(formData: FormData) {
  const supabase = createClient()
  // ... mutation logic
  revalidatePath('/items')
  return { success: true }
}
```

### Security:
1. Always validate input with Zod
2. Check authentication on protected routes
3. Use parameterized queries (Supabase handles this)
4. Validate webhook signatures (Stripe)
5. Rate limiting for public endpoints

### Error Handling:
- Use proper HTTP status codes
- Return consistent error format
- Log errors server-side
- Never expose internal errors to client

## Output Format:
```typescript
// filepath: app/api/[route]/route.ts
[complete code]
```

```typescript
// filepath: lib/actions/[name].ts
[complete code]
```

Always include the full filepath comment."""

        context = f"""## Architecture:
{json.dumps(architecture, indent=2)}

## Endpoints to Generate:
{json.dumps(endpoints, indent=2)}

## Integrations:
{json.dumps(integrations, indent=2)}

## Data Models:
{json.dumps(data_models, indent=2)}

---
Generate all backend code needed. Include:
1. API Routes for CRUD operations
2. Server Actions for mutations
3. Auth middleware/helpers
4. Stripe webhook handler (if billing needed)
5. Utility functions in lib/
"""
        
        messages = [{"role": "user", "content": context}]
        
        logger.info(f"[Backend] Generating API for {len(endpoints)} endpoints...")
        
        response = await self.call_llm(messages, system_prompt)
        
        files = self.parse_code_blocks(response)
        
        logger.info(f"[Backend] Generated {len(files)} file(s)")
        
        return {
            "success": True,
            "files": files,
            "raw_response": response
        }
    
    async def generate_stripe_integration(self) -> Dict[str, Any]:
        """Generate complete Stripe integration"""
        system_prompt = """Generate complete Stripe integration for Next.js 14:

1. lib/stripe.ts - Stripe client setup
2. app/api/stripe/webhook/route.ts - Webhook handler
3. app/api/stripe/checkout/route.ts - Create checkout session
4. app/api/stripe/portal/route.ts - Customer portal
5. lib/actions/billing.ts - Server actions for billing

Use TypeScript and proper error handling."""
        
        messages = [{"role": "user", "content": "Generate Stripe integration files"}]
        
        response = await self.call_llm(messages, system_prompt)
        files = self.parse_code_blocks(response)
        
        return {
            "success": True,
            "files": files
        }
    
    async def generate_auth_middleware(self, auth_type: str = "supabase") -> Dict[str, Any]:
        """Generate authentication middleware"""
        system_prompt = f"""Generate authentication middleware for Next.js 14 with {auth_type}.

Include:
1. middleware.ts - Route protection
2. lib/supabase/server.ts - Server client
3. lib/supabase/client.ts - Browser client
4. lib/supabase/middleware.ts - Auth middleware helper

Use App Router conventions and TypeScript."""
        
        messages = [{"role": "user", "content": f"Generate {auth_type} auth middleware"}]
        
        response = await self.call_llm(messages, system_prompt)
        files = self.parse_code_blocks(response)
        
        return {
            "success": True,
            "files": files
        }
    
    def parse_code_blocks(self, response: str) -> List[Dict[str, str]]:
        """Parse code blocks with filepath comments"""
        files = []
        
        pattern = r'```(\w+)?\n(?:\/\/\s*filepath:\s*(.+?)\n)?([\s\S]*?)```'
        
        matches = re.findall(pattern, response)
        
        for match in matches:
            language, filepath, code = match
            code = code.strip()
            
            if not code:
                continue
                
            if filepath:
                filepath = filepath.strip()
            else:
                first_line = code.split('\n')[0] if code else ''
                if 'filepath:' in first_line.lower():
                    filepath = first_line.split('filepath:')[1].strip()
                else:
                    filepath = f"api/route.ts"
            
            if not language:
                language = 'typescript'
            
            files.append({
                "name": filepath,
                "content": code,
                "language": language
            })
        
        return files
