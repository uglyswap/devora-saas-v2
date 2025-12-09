"""
Accessibility Squad - Agents pour l'accessibilité et l'internationalisation.

Ce module contient les agents spécialisés dans:
- Accessibilité web (WCAG, ARIA, navigation clavier)
- Internationalisation (i18n, traductions, RTL)
"""

from .accessibility_expert import AccessibilityExpertAgent
from .i18n_specialist import I18nSpecialistAgent

__all__ = [
    "AccessibilityExpertAgent",
    "I18nSpecialistAgent",
]
