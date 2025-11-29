"""Project templates for full-stack generation."""

from .saas_starter import SAAS_STARTER_TEMPLATE

TEMPLATES = {
    "saas_starter": SAAS_STARTER_TEMPLATE,
}

def get_template(name: str):
    """Get template by name"""
    return TEMPLATES.get(name)

def list_templates():
    """List all available templates"""
    return list(TEMPLATES.keys())
