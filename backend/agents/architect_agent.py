from .base_agent import BaseAgent
from typing import Dict, Any, List
import json
import logging

logger = logging.getLogger(__name__)

class ArchitectAgent(BaseAgent):
    """Agent responsible for analyzing requirements and defining architecture.
    
    This agent is the first to analyze user requirements and decides:
    - What type of project to create (SaaS, E-commerce, Blog, etc.)
    - Which template to use
    - What features are needed
    - What external services to integrate
    """
    
    def __init__(self, api_key: str, model: str = "openai/gpt-4o"):
        super().__init__("Architect", api_key, model)
        
        # Available project templates
        self.templates = {
            "saas_starter": {
                "name": "SaaS Starter",
                "description": "Full SaaS application with auth, billing, dashboard",
                "features": ["auth", "billing", "dashboard", "settings", "landing"],
                "stack": ["next.js", "supabase", "stripe", "tailwind"]
            },
            "ecommerce": {
                "name": "E-commerce",
                "description": "Online store with products, cart, checkout",
                "features": ["products", "cart", "checkout", "orders", "inventory"],
                "stack": ["next.js", "supabase", "stripe", "tailwind"]
            },
            "blog_cms": {
                "name": "Blog/CMS",
                "description": "Content management with MDX support",
                "features": ["posts", "categories", "comments", "seo"],
                "stack": ["next.js", "supabase", "mdx", "tailwind"]
            },
            "dashboard": {
                "name": "Admin Dashboard",
                "description": "Data visualization and management dashboard",
                "features": ["charts", "tables", "analytics", "reports"],
                "stack": ["next.js", "supabase", "recharts", "tailwind"]
            },
            "api_service": {
                "name": "API Service",
                "description": "REST/GraphQL API with documentation",
                "features": ["endpoints", "auth", "rate-limiting", "docs"],
                "stack": ["next.js", "supabase", "swagger", "zod"]
            }
        }
        
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze requirements and define project architecture"""
        user_request = task.get("request", "")
        context = task.get("context", {})
        
        system_prompt = f"""You are an expert software architect specializing in modern full-stack applications.
Your role is to analyze user requirements and define the optimal architecture.

## Available Templates
{json.dumps(self.templates, indent=2)}

## Your Tasks:
1. Analyze the user's requirements thoroughly
2. Select the most appropriate template (or suggest "custom" if none fit)
3. Identify required features and integrations
4. Define the data models needed
5. Specify external services (Stripe, Email, etc.)
6. Estimate complexity (simple, medium, complex)

## Return JSON format:
{{
  "analysis": "Brief analysis of requirements",
  "template": "template_key or custom",
  "project_type": "saas|ecommerce|blog|dashboard|api|custom",
  "features": [
    {{
      "name": "feature_name",
      "description": "what it does",
      "priority": "high|medium|low",
      "requires": ["list", "of", "dependencies"]
    }}
  ],
  "data_models": [
    {{
      "name": "ModelName",
      "fields": ["field1: type", "field2: type"],
      "relations": ["relation to other models"]
    }}
  ],
  "integrations": [
    {{
      "service": "stripe|supabase|email|etc",
      "purpose": "what it's used for",
      "required": true|false
    }}
  ],
  "pages": [
    {{
      "path": "/route",
      "name": "PageName",
      "type": "public|protected|admin",
      "components": ["list", "of", "components"]
    }}
  ],
  "complexity": "simple|medium|complex",
  "estimated_files": 10,
  "tech_stack": {{
    "frontend": ["next.js", "react", "tailwind"],
    "backend": ["api-routes", "server-actions"],
    "database": ["supabase", "postgresql"],
    "services": ["stripe", "resend"]
  }}
}}

Be thorough and specific. Consider edge cases and scalability."""
        
        messages = [
            {"role": "user", "content": f"User Request: {user_request}\n\nContext: {json.dumps(context)}"}
        ]
        
        logger.info(f"[Architect] Analyzing requirements: {user_request[:100]}...")
        
        response = await self.call_llm(messages, system_prompt)
        
        try:
            # Parse JSON response
            architecture = json.loads(response)
            
            # Validate required fields
            required_fields = ["template", "project_type", "features", "pages"]
            for field in required_fields:
                if field not in architecture:
                    architecture[field] = []
            
            logger.info(f"[Architect] Architecture defined: {architecture.get('project_type')} with {len(architecture.get('features', []))} features")
            
            return {
                "success": True,
                "architecture": architecture,
                "template": self.templates.get(architecture.get("template"), None),
                "raw_response": response
            }
            
        except json.JSONDecodeError:
            logger.warning("[Architect] Response not in JSON format")
            return {
                "success": True,
                "architecture": {
                    "analysis": response,
                    "template": "custom",
                    "project_type": "custom",
                    "features": [],
                    "pages": [],
                    "complexity": "medium"
                },
                "template": None,
                "raw_response": response
            }
    
    def get_template(self, template_key: str) -> Dict[str, Any]:
        """Get template configuration by key"""
        return self.templates.get(template_key)
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """List all available templates"""
        return [
            {"key": k, **v} for k, v in self.templates.items()
        ]
