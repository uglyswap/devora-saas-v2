"""
Performance Squad - Agents d'optimisation des performances

Ce module exporte tous les agents du Performance Squad:
- PerformanceEngineerAgent: Optimisation des Core Web Vitals et profiling JS
- BundleOptimizerAgent: Code splitting, tree shaking, asset optimization
- DatabaseOptimizerAgent: Optimisation SQL/NoSQL, indexing, caching
"""

from .performance_engineer import PerformanceEngineerAgent
from .bundle_optimizer import BundleOptimizerAgent
from .database_optimizer import DatabaseOptimizerAgent

__all__ = [
    "PerformanceEngineerAgent",
    "BundleOptimizerAgent",
    "DatabaseOptimizerAgent",
]

# Version du module
__version__ = "1.0.0"

# Metadata
__author__ = "Devora Transformation Team"
__description__ = "Performance optimization agents for web applications and databases"
