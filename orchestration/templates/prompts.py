"""
Templates de prompts pour tous les agents de l'orchestration Devora.

Fournit des prompts structurés et optimisés pour chaque type d'agent.
"""

from typing import Dict, List, Optional, Any


class SystemPrompts:
    """Prompts système de base pour tous les agents."""

    BASE = """Tu es un agent spécialisé dans le système d'orchestration Devora.

Principes fondamentaux:
- Tu communiques de manière claire et structurée
- Tu fournis des réponses au format attendu
- Tu restes dans ton domaine de spécialisation
- Tu demandes des clarifications si nécessaire
- Tu optimises pour la qualité et l'efficacité

Format de réponse: JSON structuré selon le schéma fourni."""

    REASONING = """Lors de ta réflexion:
1. Analyse le contexte et les contraintes
2. Identifie les options possibles
3. Évalue les avantages et inconvénients
4. Choisis la meilleure approche
5. Justifie ton raisonnement

Pense étape par étape et montre ton raisonnement."""


class RouterPrompts:
    """Prompts pour l'agent Router."""

    SYSTEM = f"""{SystemPrompts.BASE}

Tu es le Router Agent, responsable de l'analyse initiale et du routage des requêtes.

Ton rôle:
- Analyser la requête utilisateur pour comprendre l'intention
- Identifier les agents nécessaires pour traiter la requête
- Déterminer le workflow approprié
- Estimer la complexité et les ressources nécessaires

{SystemPrompts.REASONING}"""

    ANALYZE_REQUEST = """Analyse la requête suivante et détermine le meilleur workflow:

Requête: {query}

Contexte additionnel:
{context}

Fournis ton analyse au format JSON suivant:
{{
    "intent": "description de l'intention utilisateur",
    "complexity": "low|medium|high",
    "workflow": "nom_du_workflow",
    "required_agents": ["agent1", "agent2"],
    "estimated_steps": nombre_d_etapes,
    "reasoning": "explication de ton choix"
}}"""

    ROUTE_TO_AGENTS = """Basé sur cette analyse:
{analysis}

Détermine la séquence d'agents à exécuter:

Fournis un plan d'exécution au format JSON:
{{
    "execution_plan": [
        {{
            "agent": "nom_agent",
            "order": 1,
            "input_context": {{"clé": "valeur"}},
            "dependencies": ["agent_prérequis"]
        }}
    ],
    "parallel_groups": [[agent_ids]],
    "estimated_duration": "durée estimée"
}}"""


class PlannerPrompts:
    """Prompts pour l'agent Planner."""

    SYSTEM = f"""{SystemPrompts.BASE}

Tu es le Planner Agent, expert en décomposition de tâches et planification.

Ton rôle:
- Décomposer les objectifs complexes en tâches concrètes
- Identifier les dépendances entre tâches
- Optimiser l'ordre d'exécution
- Estimer la durée et les ressources

{SystemPrompts.REASONING}"""

    CREATE_PLAN = """Crée un plan d'action détaillé pour:

Objectif: {objective}

Contraintes:
{constraints}

Contexte:
{context}

Fournis un plan structuré au format JSON:
{{
    "tasks": [
        {{
            "id": "task_1",
            "description": "description de la tâche",
            "type": "research|analysis|implementation|validation",
            "priority": 1,
            "dependencies": ["task_id"],
            "estimated_duration": "durée",
            "resources_needed": ["ressource1"],
            "success_criteria": ["critère1"]
        }}
    ],
    "execution_order": ["task_1", "task_2"],
    "parallel_tasks": [["task_3", "task_4"]],
    "milestones": [
        {{
            "name": "milestone",
            "tasks": ["task_ids"],
            "deliverable": "livrable attendu"
        }}
    ]
}}"""

    OPTIMIZE_PLAN = """Optimise ce plan existant:

Plan actuel:
{current_plan}

Objectifs d'optimisation:
- {optimization_goals}

Fournis le plan optimisé avec les changements expliqués:
{{
    "optimized_plan": {{}},
    "changes": [
        {{
            "type": "addition|removal|reorder",
            "description": "description du changement",
            "reason": "justification"
        }}
    ],
    "improvements": {{
        "time_saved": "durée",
        "efficiency_gain": "pourcentage"
    }}
}}"""


class ResearcherPrompts:
    """Prompts pour l'agent Researcher."""

    SYSTEM = f"""{SystemPrompts.BASE}

Tu es le Researcher Agent, spécialisé dans la collecte et synthèse d'informations.

Ton rôle:
- Rechercher des informations pertinentes
- Analyser et synthétiser les données
- Valider les sources
- Identifier les insights clés

{SystemPrompts.REASONING}"""

    RESEARCH_TOPIC = """Recherche approfondie sur:

Sujet: {topic}

Questions spécifiques:
{questions}

Sources disponibles:
{sources}

Fournis ta recherche au format JSON:
{{
    "summary": "résumé exécutif",
    "findings": [
        {{
            "key_point": "point clé",
            "details": "détails",
            "source": "source",
            "confidence": 0.9,
            "supporting_evidence": ["preuve1"]
        }}
    ],
    "insights": ["insight1"],
    "gaps": ["information manquante"],
    "recommendations": ["recommandation1"]
}}"""

    SYNTHESIZE = """Synthétise ces informations:

Données brutes:
{raw_data}

Objectif de la synthèse:
{objective}

Fournis une synthèse structurée:
{{
    "executive_summary": "résumé",
    "key_themes": ["thème1"],
    "structured_data": {{}},
    "correlations": [
        {{
            "factor_a": "facteur",
            "factor_b": "facteur",
            "relationship": "relation",
            "strength": 0.8
        }}
    ],
    "actionable_insights": ["insight1"]
}}"""


class AnalystPrompts:
    """Prompts pour l'agent Analyst."""

    SYSTEM = f"""{SystemPrompts.BASE}

Tu es l'Analyst Agent, expert en analyse de données et évaluation.

Ton rôle:
- Analyser des données complexes
- Identifier patterns et anomalies
- Évaluer des options et alternatives
- Fournir des recommandations basées sur les données

{SystemPrompts.REASONING}"""

    ANALYZE_DATA = """Analyse ces données:

Données:
{data}

Questions d'analyse:
{questions}

Méthodologie souhaitée:
{methodology}

Fournis ton analyse au format JSON:
{{
    "analysis_summary": "résumé de l'analyse",
    "metrics": {{
        "metric_name": {{
            "value": 0.0,
            "unit": "unité",
            "trend": "up|down|stable",
            "significance": "high|medium|low"
        }}
    }},
    "patterns": [
        {{
            "pattern": "description",
            "frequency": 0.5,
            "significance": "high",
            "examples": ["exemple1"]
        }}
    ],
    "anomalies": [
        {{
            "description": "anomalie détectée",
            "severity": "high|medium|low",
            "potential_causes": ["cause1"]
        }}
    ],
    "recommendations": [
        {{
            "recommendation": "action recommandée",
            "priority": 1,
            "expected_impact": "impact",
            "confidence": 0.9
        }}
    ]
}}"""

    COMPARE_OPTIONS = """Compare ces options:

Options:
{options}

Critères d'évaluation:
{criteria}

Fournis une comparaison détaillée:
{{
    "comparison_matrix": {{
        "option_id": {{
            "criterion": {{
                "score": 0.8,
                "notes": "détails"
            }}
        }}
    }},
    "ranking": [
        {{
            "rank": 1,
            "option_id": "id",
            "total_score": 0.85,
            "strengths": ["force1"],
            "weaknesses": ["faiblesse1"]
        }}
    ],
    "recommendation": {{
        "selected_option": "option_id",
        "reasoning": "justification détaillée",
        "confidence": 0.9,
        "caveats": ["mise en garde"]
    }}
}}"""


class ImplementerPrompts:
    """Prompts pour l'agent Implementer."""

    SYSTEM = f"""{SystemPrompts.BASE}

Tu es l'Implementer Agent, responsable de l'exécution et de l'implémentation.

Ton rôle:
- Exécuter les tâches planifiées
- Générer du code, des configs, des documents
- Assurer la qualité de l'implémentation
- Documenter le travail effectué

{SystemPrompts.REASONING}"""

    IMPLEMENT_TASK = """Implémente cette tâche:

Description:
{task_description}

Spécifications:
{specifications}

Contraintes:
{constraints}

Fournis l'implémentation au format JSON:
{{
    "implementation": {{
        "type": "code|config|document|process",
        "content": "contenu de l'implémentation",
        "language": "langage si applicable",
        "files": [
            {{
                "path": "chemin/fichier",
                "content": "contenu",
                "description": "description"
            }}
        ]
    }},
    "testing": {{
        "test_cases": ["cas de test"],
        "validation_steps": ["étape de validation"],
        "expected_results": ["résultat attendu"]
    }},
    "documentation": {{
        "usage": "comment utiliser",
        "examples": ["exemple"],
        "notes": ["note importante"]
    }}
}}"""

    GENERATE_CODE = """Génère le code pour:

Fonctionnalité: {feature}

Exigences techniques:
{requirements}

Stack technique:
{tech_stack}

Fournis le code avec documentation:
{{
    "code_files": [
        {{
            "path": "src/module.py",
            "content": "code complet",
            "language": "python",
            "description": "description du fichier"
        }}
    ],
    "tests": [
        {{
            "path": "tests/test_module.py",
            "content": "tests unitaires",
            "coverage": 0.9
        }}
    ],
    "documentation": {{
        "api_reference": "documentation API",
        "usage_examples": ["exemple d'utilisation"],
        "dependencies": ["dépendance1"]
    }},
    "quality_checks": {{
        "linting": "passed",
        "type_checking": "passed",
        "security": ["vérification effectuée"]
    }}
}}"""


class ValidatorPrompts:
    """Prompts pour l'agent Validator."""

    SYSTEM = f"""{SystemPrompts.BASE}

Tu es le Validator Agent, expert en vérification et assurance qualité.

Ton rôle:
- Valider les résultats produits
- Vérifier la conformité aux spécifications
- Identifier les erreurs et problèmes
- Suggérer des améliorations

{SystemPrompts.REASONING}"""

    VALIDATE_OUTPUT = """Valide ce résultat:

Résultat à valider:
{output}

Spécifications attendues:
{specifications}

Critères de qualité:
{quality_criteria}

Fournis ta validation au format JSON:
{{
    "validation_result": "passed|failed|warning",
    "overall_score": 0.85,
    "checks": [
        {{
            "check": "nom de la vérification",
            "status": "passed|failed|warning",
            "details": "détails",
            "severity": "critical|high|medium|low"
        }}
    ],
    "issues": [
        {{
            "issue": "description du problème",
            "severity": "critical",
            "location": "où",
            "suggestion": "comment corriger"
        }}
    ],
    "quality_metrics": {{
        "completeness": 0.9,
        "correctness": 0.95,
        "clarity": 0.85,
        "efficiency": 0.8
    }},
    "recommendations": ["amélioration suggérée"]
}}"""

    VERIFY_COMPLIANCE = """Vérifie la conformité:

Élément à vérifier:
{item}

Standards/Règles:
{standards}

Fournis un rapport de conformité:
{{
    "compliant": true,
    "compliance_score": 0.95,
    "standards_checked": [
        {{
            "standard": "nom du standard",
            "compliant": true,
            "details": "détails de vérification"
        }}
    ],
    "violations": [
        {{
            "rule": "règle violée",
            "severity": "high",
            "description": "description",
            "remediation": "action corrective"
        }}
    ],
    "certifications": ["certification applicable"]
}}"""


class OrchestratorPrompts:
    """Prompts pour l'agent Orchestrator."""

    SYSTEM = f"""{SystemPrompts.BASE}

Tu es l'Orchestrator Agent, coordinateur principal du système.

Ton rôle:
- Coordonner l'exécution des workflows
- Gérer les dépendances entre agents
- Optimiser l'utilisation des ressources
- Assurer la cohérence globale

{SystemPrompts.REASONING}"""

    COORDINATE_WORKFLOW = """Coordonne ce workflow:

Workflow: {workflow_name}

Plan d'exécution:
{execution_plan}

État actuel:
{current_state}

Fournis les prochaines actions:
{{
    "next_actions": [
        {{
            "agent": "nom_agent",
            "action": "action à effectuer",
            "priority": 1,
            "input": {{}},
            "timeout": "durée max"
        }}
    ],
    "resource_allocation": {{
        "agent": {{
            "cpu": "allocation",
            "memory": "allocation",
            "tokens": "budget tokens"
        }}
    }},
    "monitoring": {{
        "checkpoints": ["point de contrôle"],
        "success_criteria": ["critère"],
        "rollback_triggers": ["déclencheur de rollback"]
    }}
}}"""


def format_prompt(template: str, **kwargs) -> str:
    """
    Formate un template de prompt avec les variables fournies.

    Args:
        template: Template de prompt
        **kwargs: Variables à injecter

    Returns:
        Prompt formaté
    """
    return template.format(**kwargs)


def create_messages(
    system_prompt: str,
    user_prompt: str,
    history: Optional[List[Dict[str, str]]] = None,
) -> List[Dict[str, str]]:
    """
    Crée une liste de messages formatée pour l'API LLM.

    Args:
        system_prompt: Prompt système
        user_prompt: Prompt utilisateur
        history: Historique de conversation optionnel

    Returns:
        Liste de messages formatée
    """
    messages = [{"role": "system", "content": system_prompt}]

    if history:
        messages.extend(history)

    messages.append({"role": "user", "content": user_prompt})

    return messages
