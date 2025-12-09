"""
Prompt Template Management

Provides:
- Template storage and versioning
- Variable interpolation
- Common prompt patterns for code generation
"""

from .template_manager import PromptTemplateManager, PromptTemplate

__all__ = ["PromptTemplateManager", "PromptTemplate"]
