from .base_agent import BaseAgent
from typing import Dict, Any, List
import json
import re
import logging

logger = logging.getLogger(__name__)

class FrontendAgent(BaseAgent):
    """Agent specialized in generating Next.js 14+ frontend code.
    
    Expertise:
    - Next.js App Router (app/ directory)
    - React Server Components & Client Components
    - Tailwind CSS + shadcn/ui
    - TypeScript strict mode
    - Responsive design
    - Accessibility (ARIA)
    - React Hook Form + Zod validation
    """
    
    def __init__(self, api_key: str, model: str = "openai/gpt-4o"):
        super().__init__("Frontend", api_key, model)
        
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate frontend code based on architecture"""
        architecture = task.get("architecture", {})
        pages = task.get("pages", [])
        components = task.get("components", [])
        current_files = task.get("current_files", [])
        
        system_prompt = """You are an expert Next.js 14+ frontend developer.
Your specialty is creating beautiful, production-ready UI with modern best practices.

## Tech Stack:
- Next.js 14+ with App Router
- TypeScript (strict mode)
- Tailwind CSS for styling
- shadcn/ui components
- React Hook Form + Zod for forms
- Lucide React for icons

## Guidelines:

### File Structure:
```
app/
  (auth)/
    login/page.tsx
    register/page.tsx
    layout.tsx
  (dashboard)/
    dashboard/page.tsx
    settings/page.tsx
    layout.tsx
  api/
    route.ts
  layout.tsx
  page.tsx
components/
  ui/           # shadcn/ui components
  forms/        # Form components
  layout/       # Layout components (Header, Footer, Sidebar)
  features/     # Feature-specific components
lib/
  utils.ts
  validations.ts
types/
  index.ts
```

### Component Patterns:
1. Use 'use client' directive only when necessary
2. Server Components by default
3. Proper TypeScript interfaces
4. Error boundaries for error handling
5. Loading states with Suspense
6. Mobile-first responsive design

### Code Quality:
- Clean, readable code
- Proper prop types
- Meaningful variable names
- Comments only for complex logic
- No inline styles (use Tailwind)

## Output Format:
Generate complete files with clear separators:

```tsx
// filepath: app/page.tsx
[complete code here]
```

```tsx
// filepath: components/ui/button.tsx
[complete code here]
```

Always include the full filepath comment."""

        # Build context message
        context = f"""## Architecture:
{json.dumps(architecture, indent=2)}

## Pages to Generate:
{json.dumps(pages, indent=2)}

## Components to Generate:
{json.dumps(components, indent=2)}

## Existing Files:
{json.dumps([f.get('name', f) if isinstance(f, dict) else f for f in current_files])}

---
Generate all the frontend code needed. Be complete and production-ready.
"""
        
        messages = [{"role": "user", "content": context}]
        
        logger.info(f"[Frontend] Generating UI for {len(pages)} pages...")
        
        response = await self.call_llm(messages, system_prompt)
        
        # Parse code blocks
        files = self.parse_code_blocks(response)
        
        logger.info(f"[Frontend] Generated {len(files)} file(s)")
        
        return {
            "success": True,
            "files": files,
            "raw_response": response
        }
    
    async def generate_page(self, page_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a single page"""
        system_prompt = """Generate a complete Next.js 14 page component.
Use TypeScript, Tailwind CSS, and follow App Router conventions.
Include proper metadata export for SEO.

Output format:
```tsx
// filepath: [path]
[code]
```"""
        
        messages = [{
            "role": "user", 
            "content": f"Generate page:\n{json.dumps(page_spec, indent=2)}"
        }]
        
        response = await self.call_llm(messages, system_prompt)
        files = self.parse_code_blocks(response)
        
        return {
            "success": True,
            "files": files
        }
    
    async def generate_component(self, component_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a single component"""
        system_prompt = """Generate a complete React component for Next.js 14.
Use TypeScript with proper interfaces.
Use Tailwind CSS for styling.
Use shadcn/ui as base when applicable.
Include proper prop types and default values.

Output format:
```tsx
// filepath: components/[path]
[code]
```"""
        
        messages = [{
            "role": "user",
            "content": f"Generate component:\n{json.dumps(component_spec, indent=2)}"
        }]
        
        response = await self.call_llm(messages, system_prompt)
        files = self.parse_code_blocks(response)
        
        return {
            "success": True,
            "files": files
        }
    
    def parse_code_blocks(self, response: str) -> List[Dict[str, str]]:
        """Parse code blocks with filepath comments"""
        files = []
        
        # Pattern: ```lang\n// filepath: path\ncode```
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
                # Try to extract from first comment
                first_line = code.split('\n')[0] if code else ''
                if 'filepath:' in first_line.lower():
                    filepath = first_line.split('filepath:')[1].strip().strip('/')
                else:
                    ext = self._get_extension(language)
                    filepath = f"file.{ext}"
            
            # Determine language from extension if not set
            if not language:
                language = self._get_language_from_path(filepath)
            
            files.append({
                "name": filepath,
                "content": code,
                "language": language or "typescript"
            })
        
        return files
    
    def _get_extension(self, language: str) -> str:
        """Get file extension from language"""
        mapping = {
            'typescript': 'ts',
            'tsx': 'tsx',
            'javascript': 'js',
            'jsx': 'jsx',
            'css': 'css',
            'json': 'json',
            'html': 'html'
        }
        return mapping.get(language, language or 'tsx')
    
    def _get_language_from_path(self, filepath: str) -> str:
        """Get language from file path"""
        ext = filepath.split('.')[-1] if '.' in filepath else ''
        mapping = {
            'ts': 'typescript',
            'tsx': 'tsx',
            'js': 'javascript',
            'jsx': 'jsx',
            'css': 'css',
            'json': 'json'
        }
        return mapping.get(ext, 'typescript')
