"""
Prompt Template Manager

Manages reusable prompt templates with variable interpolation
and versioning for A/B testing.
"""

import logging
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class PromptTemplate:
    """A prompt template with metadata"""
    name: str
    template: str
    variables: List[str] = field(default_factory=list)
    version: str = "1.0"
    description: str = ""
    category: str = "general"
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def render(self, **kwargs) -> str:
        """Render template with provided variables"""
        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required variable: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "template": self.template,
            "variables": self.variables,
            "version": self.version,
            "description": self.description,
            "category": self.category,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PromptTemplate":
        """Create from dictionary"""
        data = data.copy()
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        return cls(**data)


class PromptTemplateManager:
    """Manage prompt templates"""

    def __init__(self, templates_dir: Optional[Path] = None):
        self.templates_dir = templates_dir
        self._templates: Dict[str, PromptTemplate] = {}
        self._load_default_templates()

        # Load from disk if directory provided
        if templates_dir and templates_dir.exists():
            self._load_from_disk()

    def _load_default_templates(self):
        """Load default templates for code generation"""

        # ============================================================
        # ARCHITECTURE TEMPLATES
        # ============================================================
        self.add_template(PromptTemplate(
            name="architecture_analysis",
            category="architecture",
            description="Analyze requirements and design architecture",
            variables=["user_request", "context"],
            template="""You are an expert software architect. Analyze the following requirements and design a complete architecture.

User Request:
{user_request}

Context:
{context}

Provide a comprehensive architecture including:
1. Project type and tech stack
2. File structure
3. Data models
4. API endpoints
5. Frontend pages/components
6. Third-party integrations
7. Security considerations

Format your response as a structured JSON."""
        ))

        # ============================================================
        # CODE GENERATION TEMPLATES
        # ============================================================
        self.add_template(PromptTemplate(
            name="generate_component",
            category="code_generation",
            description="Generate a React/Next.js component",
            variables=["component_name", "description", "props"],
            template="""Generate a Next.js 14 component with the following specifications:

Component Name: {component_name}
Description: {description}
Props: {props}

Requirements:
- Use TypeScript with proper typing
- Use Tailwind CSS for styling
- Follow Next.js 14 App Router conventions
- Include proper error handling
- Add helpful comments

Provide the complete component code."""
        ))

        self.add_template(PromptTemplate(
            name="generate_api_route",
            category="code_generation",
            description="Generate a Next.js API route",
            variables=["route_path", "method", "description", "auth_required"],
            template="""Generate a Next.js 14 API route with the following specifications:

Route: {route_path}
HTTP Method: {method}
Description: {description}
Authentication Required: {auth_required}

Requirements:
- Use TypeScript
- Implement proper error handling
- Add input validation with Zod
- Return appropriate status codes
- Include rate limiting if needed
- Add security headers

Provide the complete route handler code."""
        ))

        self.add_template(PromptTemplate(
            name="generate_database_schema",
            category="code_generation",
            description="Generate database schema",
            variables=["table_name", "fields", "database_type"],
            template="""Generate a database schema with the following specifications:

Table Name: {table_name}
Fields: {fields}
Database Type: {database_type}

Requirements:
- Include proper indexes
- Add foreign key constraints where appropriate
- Use appropriate data types
- Add created_at and updated_at timestamps
- Include security policies (RLS for Supabase)

Provide the complete schema definition."""
        ))

        # ============================================================
        # CODE REVIEW TEMPLATES
        # ============================================================
        self.add_template(PromptTemplate(
            name="code_review",
            category="review",
            description="Review generated code",
            variables=["code", "context"],
            template="""Review the following code and provide detailed feedback:

Code:
{code}

Context:
{context}

Analyze:
1. Code quality and best practices
2. Security vulnerabilities
3. Performance issues
4. Error handling
5. Type safety
6. Accessibility (for UI code)
7. Test coverage needs

Provide:
- Issues found (categorized by severity: critical, high, medium, low)
- Specific suggestions for improvement
- Overall quality score (1-10)
- Recommendation: APPROVE / REQUEST_CHANGES / REJECT"""
        ))

        # ============================================================
        # RAG TEMPLATES
        # ============================================================
        self.add_template(PromptTemplate(
            name="rag_augmented_generation",
            category="rag",
            description="Generate code with RAG context",
            variables=["user_request", "retrieved_context"],
            template="""Generate code based on the user request and relevant context from the knowledge base.

User Request:
{user_request}

Relevant Documentation/Examples:
{retrieved_context}

Use the provided context to inform your implementation. Follow the patterns and best practices shown in the context.

Provide the complete implementation with explanations."""
        ))

        # ============================================================
        # TESTING TEMPLATES
        # ============================================================
        self.add_template(PromptTemplate(
            name="generate_tests",
            category="testing",
            description="Generate unit tests for code",
            variables=["code", "test_framework"],
            template="""Generate comprehensive unit tests for the following code:

Code:
{code}

Test Framework: {test_framework}

Requirements:
- Test happy paths
- Test edge cases
- Test error conditions
- Mock external dependencies
- Aim for >80% code coverage
- Include setup/teardown as needed

Provide the complete test suite."""
        ))

        # ============================================================
        # BUG FIX TEMPLATES
        # ============================================================
        self.add_template(PromptTemplate(
            name="fix_bug",
            category="debugging",
            description="Analyze and fix a bug",
            variables=["bug_description", "code", "error_message"],
            template="""Analyze and fix the following bug:

Bug Description:
{bug_description}

Error Message:
{error_message}

Current Code:
{code}

Provide:
1. Root cause analysis
2. Fixed code
3. Explanation of the fix
4. How to prevent similar bugs in the future
5. Suggested tests to verify the fix"""
        ))

        # ============================================================
        # OPTIMIZATION TEMPLATES
        # ============================================================
        self.add_template(PromptTemplate(
            name="optimize_code",
            category="optimization",
            description="Optimize code for performance",
            variables=["code", "performance_issue"],
            template="""Optimize the following code for better performance:

Performance Issue:
{performance_issue}

Current Code:
{code}

Analyze:
1. Performance bottlenecks
2. Time complexity
3. Space complexity
4. Database query efficiency
5. Caching opportunities

Provide:
- Optimized code
- Performance comparison (before/after)
- Explanation of optimizations
- Trade-offs (if any)"""
        ))

        # ============================================================
        # REFACTORING TEMPLATES
        # ============================================================
        self.add_template(PromptTemplate(
            name="refactor_code",
            category="refactoring",
            description="Refactor code for better maintainability",
            variables=["code", "refactoring_goal"],
            template="""Refactor the following code:

Refactoring Goal:
{refactoring_goal}

Current Code:
{code}

Apply:
1. DRY (Don't Repeat Yourself)
2. SOLID principles
3. Clean code practices
4. Design patterns where appropriate
5. Improved naming and structure

Provide:
- Refactored code
- List of changes made
- Explanation of improvements
- Any breaking changes (if applicable)"""
        ))

        logger.info(f"[PromptManager] Loaded {len(self._templates)} default templates")

    def add_template(self, template: PromptTemplate):
        """Add a template"""
        self._templates[template.name] = template

    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """Get a template by name"""
        return self._templates.get(name)

    def list_templates(self, category: Optional[str] = None) -> List[PromptTemplate]:
        """List all templates, optionally filtered by category"""
        templates = list(self._templates.values())

        if category:
            templates = [t for t in templates if t.category == category]

        return templates

    def render(self, template_name: str, **kwargs) -> str:
        """Render a template by name"""
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template not found: {template_name}")

        return template.render(**kwargs)

    def delete_template(self, name: str):
        """Delete a template"""
        if name in self._templates:
            del self._templates[name]
            logger.info(f"[PromptManager] Deleted template: {name}")

    def _load_from_disk(self):
        """Load templates from disk"""
        if not self.templates_dir:
            return

        try:
            for file_path in self.templates_dir.glob("*.json"):
                with open(file_path, "r") as f:
                    data = json.load(f)
                    template = PromptTemplate.from_dict(data)
                    self.add_template(template)

            logger.info(f"[PromptManager] Loaded templates from {self.templates_dir}")

        except Exception as e:
            logger.error(f"[PromptManager] Failed to load templates from disk: {e}")

    def save_to_disk(self):
        """Save all templates to disk"""
        if not self.templates_dir:
            logger.warning("[PromptManager] No templates directory configured")
            return

        try:
            self.templates_dir.mkdir(parents=True, exist_ok=True)

            for template in self._templates.values():
                file_path = self.templates_dir / f"{template.name}.json"
                with open(file_path, "w") as f:
                    json.dump(template.to_dict(), f, indent=2)

            logger.info(f"[PromptManager] Saved {len(self._templates)} templates to disk")

        except Exception as e:
            logger.error(f"[PromptManager] Failed to save templates to disk: {e}")

    def export_templates(self) -> Dict[str, Any]:
        """Export all templates as dictionary"""
        return {
            name: template.to_dict()
            for name, template in self._templates.items()
        }

    def import_templates(self, templates_data: Dict[str, Any]):
        """Import templates from dictionary"""
        for name, data in templates_data.items():
            template = PromptTemplate.from_dict(data)
            self.add_template(template)

        logger.info(f"[PromptManager] Imported {len(templates_data)} templates")

    def get_categories(self) -> List[str]:
        """Get list of all template categories"""
        categories = set(t.category for t in self._templates.values())
        return sorted(categories)

    def search_templates(self, query: str) -> List[PromptTemplate]:
        """Search templates by name or description"""
        query = query.lower()
        results = []

        for template in self._templates.values():
            if (query in template.name.lower() or
                query in template.description.lower() or
                query in template.category.lower()):
                results.append(template)

        return results
