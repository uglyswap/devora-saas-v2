"""
Business Squad - Agents d'orchestration business

Ce module contient tous les agents du Business Squad responsables de:
- Product Management (PRD, user stories, roadmap)
- Copywriting (marketing, UX microcopy)
- Pricing Strategy (modèles de pricing, métriques financières)
- Compliance (GDPR, CCPA, politiques de confidentialité)
- Growth Engineering (A/B tests, feature flags, rétention)
"""

from .product_manager import ProductManagerAgent
from .copywriter import CopywriterAgent
from .pricing_strategist import PricingStrategistAgent
from .compliance_officer import ComplianceOfficerAgent
from .growth_engineer import GrowthEngineerAgent

__all__ = [
    "ProductManagerAgent",
    "CopywriterAgent",
    "PricingStrategistAgent",
    "ComplianceOfficerAgent",
    "GrowthEngineerAgent",
]

__version__ = "1.0.0"
__author__ = "Devora Team"
__description__ = "Business Squad - AI Agents pour l'orchestration business"
