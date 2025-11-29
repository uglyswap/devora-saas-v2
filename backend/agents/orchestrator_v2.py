from .architect_agent import ArchitectAgent
from .frontend_agent import FrontendAgent
from .backend_agent import BackendAgent
from .database_agent import DatabaseAgent
from .reviewer import ReviewerAgent
from .context_compressor import compress_context_if_needed
from typing import Dict, Any, List, Callable, Optional
import asyncio
import logging

logger = logging.getLogger(__name__)

class OrchestratorV2:
    """Advanced orchestrator for full-stack project generation.
    
    Workflow:
    1. Architect analyzes requirements and defines architecture
    2. Parallel generation: Frontend + Backend + Database
    3. Reviewer validates and suggests improvements
    4. Iterate if needed
    
    ```
    User Request
         │
         ▼
    ┌─────────────┐
    │  ARCHITECT  │  ← Analyze & Design
    └──────┬──────┘
           │
     ┌─────┼─────┐
     │     │     │
     ▼     ▼     ▼
    ┌───┐ ┌───┐ ┌───┐
    │FE │ │BE │ │DB │  ← Parallel Generation
    └─┬─┘ └─┬─┘ └─┬─┘
      │     │     │
      └─────┼─────┘
            │
            ▼
    ┌─────────────┐
    │  REVIEWER   │  ← Validate & Iterate
    └─────────────┘
    ```
    """
    
    def __init__(self, api_key: str, model: str = "openai/gpt-4o"):
        self.api_key = api_key
        self.model = model
        
        # Initialize specialized agents
        self.architect = ArchitectAgent(api_key, model)
        self.frontend = FrontendAgent(api_key, model)
        self.backend = BackendAgent(api_key, model)
        self.database = DatabaseAgent(api_key, model)
        self.reviewer = ReviewerAgent(api_key, model)
        
        self.max_iterations = 2
        self.progress_callback: Optional[Callable] = None
        
    def set_progress_callback(self, callback: Callable):
        """Set callback for progress updates"""
        self.progress_callback = callback
        
    async def emit_progress(self, event: str, data: Dict[str, Any]):
        """Emit progress event"""
        if self.progress_callback:
            await self.progress_callback(event, data)
        logger.info(f"[OrchestratorV2] {event}: {data.get('message', '')}")
    
    async def execute(
        self, 
        user_request: str, 
        current_files: List[Dict] = None,
        conversation_history: List[Dict[str, str]] = None,
        project_type: str = None
    ) -> Dict[str, Any]:
        """Execute advanced agentic workflow for full-stack generation.
        
        Args:
            user_request: User's project description
            current_files: Existing project files
            conversation_history: Previous conversation context
            project_type: Optional hint (saas, ecommerce, blog, etc.)
            
        Returns:
            Dictionary with generated files and metadata
        """
        if current_files is None:
            current_files = []
        if conversation_history is None:
            conversation_history = []
        
        logger.info(f"[OrchestratorV2] Starting full-stack generation: {user_request[:100]}...")
        
        # Apply context compression if needed
        compressed_messages, compressed_files, compression_stats = compress_context_if_needed(
            conversation_history,
            files=[f if isinstance(f, dict) else {'name': f, 'content': ''} for f in current_files],
            keep_recent_messages=6,
            max_file_tokens=2000
        )
        
        if compression_stats.get('compressed'):
            logger.info(f"[OrchestratorV2] Context compressed: saved {compression_stats['total']['tokens_saved']} tokens")
        
        iteration = 0
        all_files = []
        
        try:
            # ═══════════════════════════════════════════════════════════════
            # STEP 1: ARCHITECTURE ANALYSIS
            # ═══════════════════════════════════════════════════════════════
            await self.emit_progress("analyzing", {
                "message": "Analyzing requirements and designing architecture...",
                "step": 1,
                "total_steps": 4
            })
            
            arch_result = await self.architect.execute({
                "request": user_request,
                "context": {
                    "current_files": [f.get('name', f) if isinstance(f, dict) else f for f in current_files],
                    "project_type_hint": project_type,
                    "conversation": compressed_messages[-3:] if compressed_messages else []
                }
            })
            
            if not arch_result["success"]:
                return {"success": False, "error": "Architecture analysis failed"}
            
            architecture = arch_result["architecture"]
            template = arch_result.get("template")
            
            await self.emit_progress("architecture_complete", {
                "message": f"Architecture defined: {architecture.get('project_type', 'custom')} project",
                "architecture": architecture,
                "template": template
            })
            
            # Iterative generation loop
            while iteration < self.max_iterations:
                iteration += 1
                
                await self.emit_progress("iteration_start", {
                    "message": f"Generation iteration {iteration}/{self.max_iterations}",
                    "iteration": iteration
                })
                
                # ═══════════════════════════════════════════════════════════
                # STEP 2: PARALLEL CODE GENERATION
                # ═══════════════════════════════════════════════════════════
                await self.emit_progress("generating", {
                    "message": "Generating Frontend, Backend, and Database in parallel...",
                    "step": 2,
                    "total_steps": 4
                })
                
                # Prepare tasks for each agent
                frontend_task = self.frontend.execute({
                    "architecture": architecture,
                    "pages": architecture.get("pages", []),
                    "components": [],
                    "current_files": compressed_files
                })
                
                backend_task = self.backend.execute({
                    "architecture": architecture,
                    "endpoints": self._extract_endpoints(architecture),
                    "integrations": architecture.get("integrations", []),
                    "data_models": architecture.get("data_models", [])
                })
                
                database_task = self.database.execute({
                    "architecture": architecture,
                    "data_models": architecture.get("data_models", []),
                    "features": architecture.get("features", [])
                })
                
                # Execute all three in parallel
                results = await asyncio.gather(
                    frontend_task,
                    backend_task,
                    database_task,
                    return_exceptions=True
                )
                
                frontend_result, backend_result, database_result = results
                
                # Collect all generated files
                all_files = []
                
                if isinstance(frontend_result, dict) and frontend_result.get("success"):
                    all_files.extend(frontend_result.get("files", []))
                    await self.emit_progress("frontend_complete", {
                        "message": f"Frontend: {len(frontend_result.get('files', []))} files generated"
                    })
                else:
                    logger.error(f"Frontend generation failed: {frontend_result}")
                
                if isinstance(backend_result, dict) and backend_result.get("success"):
                    all_files.extend(backend_result.get("files", []))
                    await self.emit_progress("backend_complete", {
                        "message": f"Backend: {len(backend_result.get('files', []))} files generated"
                    })
                else:
                    logger.error(f"Backend generation failed: {backend_result}")
                
                if isinstance(database_result, dict) and database_result.get("success"):
                    all_files.extend(database_result.get("files", []))
                    await self.emit_progress("database_complete", {
                        "message": f"Database: {len(database_result.get('files', []))} files generated"
                    })
                else:
                    logger.error(f"Database generation failed: {database_result}")
                
                # Add config files
                config_files = self._generate_config_files(architecture)
                all_files.extend(config_files)
                
                await self.emit_progress("generation_complete", {
                    "message": f"Generated {len(all_files)} total files",
                    "files": [f['name'] for f in all_files]
                })
                
                # ═══════════════════════════════════════════════════════════
                # STEP 3: REVIEW
                # ═══════════════════════════════════════════════════════════
                await self.emit_progress("reviewing", {
                    "message": "Reviewing generated code...",
                    "step": 3,
                    "total_steps": 4
                })
                
                review_result = await self.reviewer.execute({
                    "files": all_files,
                    "architecture": architecture,
                    "iteration": iteration,
                    "max_iterations": self.max_iterations
                })
                
                await self.emit_progress("review_complete", {
                    "message": review_result.get("message", "Review completed"),
                    "decision": review_result.get("decision"),
                    "requires_iteration": review_result.get("requires_iteration", False)
                })
                
                # Check if we need to iterate
                if not review_result.get("requires_iteration", False):
                    break
                
                # Update architecture with fix instructions for next iteration
                if review_result.get("fix_instructions"):
                    architecture["fix_instructions"] = review_result["fix_instructions"]
            
            # ═══════════════════════════════════════════════════════════════
            # STEP 4: FINALIZE
            # ═══════════════════════════════════════════════════════════════
            await self.emit_progress("complete", {
                "message": f"Full-stack generation completed! {len(all_files)} files ready.",
                "step": 4,
                "total_steps": 4,
                "iterations": iteration
            })
            
            return {
                "success": True,
                "files": all_files,
                "architecture": architecture,
                "template": template,
                "iterations": iteration,
                "compression_stats": compression_stats if compression_stats.get('compressed') else None,
                "message": f"Full-stack project generated with {len(all_files)} files in {iteration} iteration(s)"
            }
            
        except Exception as e:
            logger.error(f"[OrchestratorV2] Error: {str(e)}")
            await self.emit_progress("error", {
                "message": f"Error: {str(e)}"
            })
            return {
                "success": False,
                "error": str(e),
                "files": all_files  # Return partial results
            }
    
    def _extract_endpoints(self, architecture: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract API endpoints from architecture"""
        endpoints = []
        
        # Extract from pages
        for page in architecture.get("pages", []):
            if page.get("type") == "api":
                endpoints.append({
                    "path": page.get("path"),
                    "methods": ["GET", "POST"],
                    "description": page.get("name")
                })
        
        # Extract from features
        for feature in architecture.get("features", []):
            if "api" in feature.get("requires", []):
                endpoints.append({
                    "path": f"/api/{feature.get('name', 'resource').lower()}",
                    "methods": ["GET", "POST", "PUT", "DELETE"],
                    "description": feature.get("description", "")
                })
        
        # Add common endpoints based on integrations
        integrations = architecture.get("integrations", [])
        for integration in integrations:
            service = integration.get("service", "")
            if service == "stripe":
                endpoints.extend([
                    {"path": "/api/stripe/webhook", "methods": ["POST"], "description": "Stripe webhooks"},
                    {"path": "/api/stripe/checkout", "methods": ["POST"], "description": "Create checkout"},
                    {"path": "/api/stripe/portal", "methods": ["POST"], "description": "Customer portal"}
                ])
            elif service == "auth" or service == "supabase":
                endpoints.extend([
                    {"path": "/api/auth/callback", "methods": ["GET"], "description": "Auth callback"},
                    {"path": "/api/user", "methods": ["GET", "PUT"], "description": "User profile"}
                ])
        
        return endpoints
    
    def _generate_config_files(self, architecture: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate common config files"""
        files = []
        
        # package.json
        package_json = {
            "name": architecture.get("project_type", "my-app"),
            "version": "0.1.0",
            "private": True,
            "scripts": {
                "dev": "next dev",
                "build": "next build",
                "start": "next start",
                "lint": "next lint"
            },
            "dependencies": {
                "next": "14.2.0",
                "react": "^18",
                "react-dom": "^18",
                "@supabase/supabase-js": "^2.39.0",
                "@supabase/ssr": "^0.1.0",
                "tailwindcss": "^3.4.0",
                "typescript": "^5",
                "zod": "^3.22.0",
                "lucide-react": "^0.300.0"
            },
            "devDependencies": {
                "@types/node": "^20",
                "@types/react": "^18",
                "@types/react-dom": "^18",
                "autoprefixer": "^10.0.1",
                "postcss": "^8"
            }
        }
        
        # Add Stripe if needed
        for integration in architecture.get("integrations", []):
            if integration.get("service") == "stripe":
                package_json["dependencies"]["stripe"] = "^14.0.0"
                package_json["dependencies"]["@stripe/stripe-js"] = "^2.0.0"
        
        files.append({
            "name": "package.json",
            "content": __import__('json').dumps(package_json, indent=2),
            "language": "json"
        })
        
        # .env.local template
        env_content = """# Supabase
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# App
NEXT_PUBLIC_APP_URL=http://localhost:3000
"""
        
        for integration in architecture.get("integrations", []):
            if integration.get("service") == "stripe":
                env_content += """
# Stripe
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_xxx
"""
        
        files.append({
            "name": ".env.local.example",
            "content": env_content.strip(),
            "language": "plaintext"
        })
        
        # tailwind.config.ts
        tailwind_config = """import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: ['class'],
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
}
export default config
"""
        
        files.append({
            "name": "tailwind.config.ts",
            "content": tailwind_config,
            "language": "typescript"
        })
        
        # next.config.js
        next_config = """/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
  },
}

module.exports = nextConfig
"""
        
        files.append({
            "name": "next.config.js",
            "content": next_config,
            "language": "javascript"
        })
        
        return files
