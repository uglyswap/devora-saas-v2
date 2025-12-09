"""
QA Squad - Quality Assurance Agents

Ce module regroupe tous les agents spécialisés en Quality Assurance pour le système
d'orchestration Devora.

Agents disponibles:
    - TestEngineerAgent: Génération de tests (E2E, unitaires, intégration, fixtures)
    - CodeReviewerAgent: Review de code et détection de problèmes (sécurité, performance, qualité)

Usage:
    from orchestration.agents.qa_squad import TestEngineerAgent, CodeReviewerAgent
    from orchestration.core.base_agent import AgentConfig

    # Test Engineer - Génération de tests
    config = AgentConfig(
        name="test_engineer",
        model="anthropic/claude-3.5-sonnet",
        api_key="your-api-key",
        temperature=0.3  # Basse pour tests déterministes
    )
    test_engineer = TestEngineerAgent(config)

    # Générer des tests E2E
    result = test_engineer.run({
        "type": "e2e",
        "code": "...",
        "context": "User login flow"
    })
    print(result["output"]["tests"])

    # Code Reviewer - Review automatique
    config = AgentConfig(
        name="code_reviewer",
        model="anthropic/claude-3.5-sonnet",
        api_key="your-api-key",
        temperature=0.4  # Modérée pour review équilibrée
    )
    code_reviewer = CodeReviewerAgent(config)

    # Review complète du code
    result = code_reviewer.run({
        "code": "...",
        "language": "typescript",
        "focus": "security"  # ou "performance", "quality", "all"
    })
    print(result["output"]["review"])

Fonctionnalités clés:

    TestEngineerAgent:
        - Tests E2E avec Playwright (Page Object Model, auto-wait)
        - Tests unitaires Jest/Vitest (AAA pattern, mocking)
        - Tests d'intégration (MSW, contrats API)
        - Génération de fixtures et factories
        - Analyse de couverture de code
        - Stratégies de test (Test Pyramid, CI/CD)
        - Tests de régression pour bugs connus

    CodeReviewerAgent:
        - Review complète (qualité, sécurité, performance)
        - Audit de sécurité OWASP Top 10
        - Analyse de performance (complexité, bottlenecks)
        - Détection d'anti-patterns et code smells
        - Vérification SOLID, DRY, KISS, YAGNI
        - Analyse architecturale (design patterns)
        - Suggestions de refactoring avec exemples

Version: 1.0.0
Author: Devora Orchestration System
"""

from .test_engineer import TestEngineerAgent
from .code_reviewer import CodeReviewerAgent

__all__ = [
    "TestEngineerAgent",
    "CodeReviewerAgent",
]

__version__ = "1.0.0"
