"""
Exemple d'utilisation des utilitaires Devora.

Cet exemple montre comment utiliser tous les composants ensemble
pour créer un workflow d'analyse simple.
"""

import asyncio
import json
import os
import sys
import io
from datetime import datetime
from pathlib import Path

# Fix encoding pour Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configuration de l'environnement (optionnel si .env existe)
# os.environ["OPENROUTER_API_KEY"] = "sk-or-v1-..."

from orchestration.utils import (
    create_llm_client,
    ModelType,
    get_logger,
    TokenManager,
    ProgressEmitter,
    EventType,
)
from orchestration.templates import (
    RouterPrompts,
    PlannerPrompts,
    create_messages,
    format_prompt,
    RouterResponse,
    PlannerResponse,
    Metadata,
    ResponseStatus,
    Task,
    TaskType,
)


async def analyze_request_example():
    """
    Exemple 1: Analyse d'une requête utilisateur avec le Router.
    """
    print("\n" + "=" * 60)
    print("EXEMPLE 1: Analyse de Requête")
    print("=" * 60)

    # Setup des composants
    logger = get_logger(__name__).with_context(example="router_analysis")
    emitter = ProgressEmitter(session_id="example_1")
    tm = TokenManager()

    # Callback pour logger tous les événements
    def log_events(event):
        logger.info(f"Event: {event.type.value}", **event.data)

    emitter.on_any(log_events)

    # Requête utilisateur
    user_query = """
    Je veux créer une application web de gestion de tâches collaborative.
    L'application doit permettre:
    - Créer/éditer/supprimer des tâches
    - Assigner des tâches à des utilisateurs
    - Suivre la progression en temps réel
    - Envoyer des notifications
    - Exporter des rapports
    """

    # Démarrage du workflow
    await emitter.workflow_start("router_analysis", {"query": user_query[:50] + "..."})

    # Créer le prompt
    prompt = format_prompt(
        RouterPrompts.ANALYZE_REQUEST,
        query=user_query,
        context="Startup tech, équipe de 3 devs, budget 2 mois"
    )

    messages = create_messages(
        system_prompt=RouterPrompts.SYSTEM,
        user_prompt=prompt
    )

    # Vérifier les tokens
    token_count = tm.count_messages_tokens(messages)
    logger.info("Prompt créé", tokens=token_count)

    print(f"\n📝 Requête utilisateur:")
    print(user_query)
    print(f"\n📊 Tokens du prompt: {token_count}")

    # Simuler l'appel LLM (commenté car nécessite une clé API)
    """
    async with await create_llm_client() as llm:
        await emitter.agent_start("router-001", "Router Agent")

        response = await llm.complete(
            messages,
            model=ModelType.SONNET,
            temperature=0.7,
            max_tokens=2048
        )

        logger.info("Réponse LLM reçue", tokens=response.tokens_used)

        # Parser la réponse JSON
        analysis = json.loads(response.content)

        # Créer la réponse structurée
        metadata = Metadata(
            agent_id="router-001",
            agent_type="router",
            execution_time=1.5,
            tokens_used=response.tokens_used,
            model_used=response.model
        )

        result = RouterResponse(
            status=ResponseStatus.SUCCESS,
            metadata=metadata,
            intent=analysis["intent"],
            complexity=analysis["complexity"],
            workflow=analysis["workflow"],
            required_agents=analysis["required_agents"],
            estimated_steps=analysis["estimated_steps"],
            reasoning=analysis["reasoning"]
        )

        print(f"\n✅ Analyse terminée:")
        print(f"  - Intention: {result.intent}")
        print(f"  - Complexité: {result.complexity}")
        print(f"  - Workflow: {result.workflow}")
        print(f"  - Agents requis: {', '.join(result.required_agents)}")
        print(f"  - Étapes estimées: {result.estimated_steps}")

        await emitter.agent_complete("router-001", result.to_dict())
    """

    # Simulation avec des données factices
    print("\n⚠️  Mode simulation (clé API non configurée)")
    simulation_result = {
        "intent": "Développement d'application web collaborative",
        "complexity": "high",
        "workflow": "full_stack_development",
        "required_agents": ["business_analyst", "frontend_dev", "backend_dev", "qa_engineer"],
        "estimated_steps": 8,
        "reasoning": "Projet complexe nécessitant frontend, backend, temps réel et notifications"
    }

    print(f"\n✅ Analyse simulée:")
    for key, value in simulation_result.items():
        print(f"  - {key}: {value}")

    await emitter.workflow_complete("router_analysis", simulation_result)

    # Stats finales
    stats = emitter.get_stats()
    print(f"\n📈 Statistiques:")
    print(f"  - Total événements: {stats['total_events']}")
    print(f"  - Événements par type: {stats['events_by_type']}")


async def planning_example():
    """
    Exemple 2: Création d'un plan de projet avec le Planner.
    """
    print("\n" + "=" * 60)
    print("EXEMPLE 2: Planification de Projet")
    print("=" * 60)

    logger = get_logger(__name__).with_context(example="planning")
    emitter = ProgressEmitter(session_id="example_2")
    tm = TokenManager()

    # Objectif du projet
    objective = "Développer une API REST pour la gestion de tâches avec authentification JWT"

    # Contraintes
    constraints = """
    - Budget: 2 semaines
    - Stack: FastAPI + PostgreSQL
    - MVP seulement
    - Déploiement sur AWS
    """

    # Contexte
    context = """
    - Équipe de 2 développeurs backend
    - Infrastructure AWS existante
    - Base de code existante à étendre
    """

    await emitter.workflow_start("planning", {"objective": objective})

    # Créer le prompt
    prompt = format_prompt(
        PlannerPrompts.CREATE_PLAN,
        objective=objective,
        constraints=constraints,
        context=context
    )

    messages = create_messages(
        system_prompt=PlannerPrompts.SYSTEM,
        user_prompt=prompt
    )

    token_count = tm.count_messages_tokens(messages)
    logger.info("Plan prompt créé", tokens=token_count)

    print(f"\n🎯 Objectif: {objective}")
    print(f"\n📊 Tokens: {token_count}")

    # Simulation du plan
    print("\n⚠️  Mode simulation (clé API non configurée)")

    simulated_plan = {
        "tasks": [
            {
                "id": "task_1",
                "description": "Définir les schémas de données et endpoints API",
                "type": "planning",
                "priority": 1,
                "dependencies": [],
                "estimated_duration": "4 heures",
                "resources_needed": ["OpenAPI spec"],
                "success_criteria": ["Schémas Pydantic définis", "Routes documentées"]
            },
            {
                "id": "task_2",
                "description": "Implémenter l'authentification JWT",
                "type": "implementation",
                "priority": 1,
                "dependencies": ["task_1"],
                "estimated_duration": "8 heures",
                "resources_needed": ["JWT library", "database access"],
                "success_criteria": ["Login/register fonctionnels", "Tests passent"]
            },
            {
                "id": "task_3",
                "description": "Créer les endpoints CRUD pour les tâches",
                "type": "implementation",
                "priority": 2,
                "dependencies": ["task_1", "task_2"],
                "estimated_duration": "12 heures",
                "resources_needed": ["database", "auth middleware"],
                "success_criteria": ["CRUD complet", "Validation des données", "Tests unitaires"]
            },
            {
                "id": "task_4",
                "description": "Tests d'intégration et documentation",
                "type": "validation",
                "priority": 3,
                "dependencies": ["task_3"],
                "estimated_duration": "6 heures",
                "resources_needed": ["Pytest", "OpenAPI generator"],
                "success_criteria": ["Couverture > 80%", "Docs complètes"]
            }
        ],
        "execution_order": ["task_1", "task_2", "task_3", "task_4"],
        "parallel_tasks": [],
        "milestones": [
            {
                "name": "API définie",
                "tasks": ["task_1"],
                "deliverable": "Spécification OpenAPI"
            },
            {
                "name": "Auth implémentée",
                "tasks": ["task_2"],
                "deliverable": "Endpoints login/register"
            },
            {
                "name": "MVP ready",
                "tasks": ["task_3", "task_4"],
                "deliverable": "API fonctionnelle testée"
            }
        ]
    }

    # Afficher le plan
    print("\n✅ Plan généré:")
    print(f"\n📋 Tâches ({len(simulated_plan['tasks'])}):")
    for task in simulated_plan["tasks"]:
        deps = f" (dépend de: {', '.join(task['dependencies'])})" if task['dependencies'] else ""
        print(f"\n  {task['id']} - {task['description']}{deps}")
        print(f"    Type: {task['type']}")
        print(f"    Durée estimée: {task['estimated_duration']}")
        print(f"    Critères de succès: {', '.join(task['success_criteria'])}")

    print(f"\n🎯 Milestones ({len(simulated_plan['milestones'])}):")
    for milestone in simulated_plan["milestones"]:
        print(f"  - {milestone['name']}: {milestone['deliverable']}")

    await emitter.workflow_complete("planning", {"tasks_count": len(simulated_plan["tasks"])})


async def streaming_example():
    """
    Exemple 3: Streaming avec progression en temps réel.
    """
    print("\n" + "=" * 60)
    print("EXEMPLE 3: Streaming avec Progression")
    print("=" * 60)

    logger = get_logger(__name__).with_context(example="streaming")
    emitter = ProgressEmitter(session_id="example_3")

    await emitter.workflow_start("streaming", {"type": "content_generation"})
    await emitter.agent_start("writer-001", "Writer Agent")

    # Simuler un streaming
    print("\n📝 Génération de contenu (simulé):\n")

    simulated_chunks = [
        "L'orchestration multi-agents est un paradigme puissant ",
        "qui permet de décomposer des tâches complexes ",
        "en sous-tâches spécialisées. ",
        "\n\nChaque agent se concentre sur son domaine d'expertise, ",
        "assurant ainsi une meilleure qualité ",
        "et une plus grande efficacité. ",
        "\n\nLes agents peuvent travailler en parallèle ",
        "ou de manière séquentielle selon les dépendances."
    ]

    full_text = ""
    for i, chunk in enumerate(simulated_chunks):
        # Simuler un délai
        await asyncio.sleep(0.2)

        # Afficher le chunk
        print(chunk, end="", flush=True)
        full_text += chunk

        # Émettre l'événement
        await emitter.llm_stream_chunk(chunk, agent_id="writer-001")

        # Progression
        progress = (i + 1) / len(simulated_chunks)
        await emitter.task_progress(
            "content_generation",
            progress,
            f"{len(full_text)} caractères générés",
            agent_id="writer-001"
        )

    print("\n\n✅ Génération terminée!")
    print(f"  - Total: {len(full_text)} caractères")
    print(f"  - Chunks: {len(simulated_chunks)}")

    await emitter.agent_complete("writer-001", {"char_count": len(full_text)})
    await emitter.workflow_complete("streaming", {"status": "success"})


async def token_management_example():
    """
    Exemple 4: Gestion avancée des tokens.
    """
    print("\n" + "=" * 60)
    print("EXEMPLE 4: Gestion des Tokens")
    print("=" * 60)

    tm = TokenManager()
    logger = get_logger(__name__).with_context(example="tokens")

    # Créer une longue conversation
    conversation = [
        {"role": "system", "content": "Tu es un assistant expert en développement."},
    ]

    # Ajouter beaucoup de messages
    for i in range(50):
        conversation.append({
            "role": "user",
            "content": f"Question {i}: " + "comment faire " * 20
        })
        conversation.append({
            "role": "assistant",
            "content": f"Réponse {i}: " + "tu peux utiliser " * 30
        })

    # Compter les tokens
    total_tokens = tm.count_messages_tokens(conversation)
    logger.info("Conversation créée", messages=len(conversation), tokens=total_tokens)

    print(f"\n📊 Conversation:")
    print(f"  - Messages: {len(conversation)}")
    print(f"  - Tokens: {total_tokens:,}")

    # Vérifier si ça tient dans le contexte
    model = "anthropic/claude-3.5-sonnet"
    fits, used, available = tm.check_context_fit(
        conversation,
        model=model,
        max_completion_tokens=4096,
        safety_margin=0.1
    )

    print(f"\n🔍 Vérification de capacité ({model}):")
    print(f"  - Utilisé: {used:,} tokens")
    print(f"  - Disponible pour complétion: {available:,} tokens")
    print(f"  - Status: {'✅ OK' if fits else '❌ Trop grand'}")

    if not fits:
        # Compression nécessaire
        print(f"\n⚠️  Compression requise!")

        compressed = tm.compress_messages(
            conversation,
            target_tokens=available,
            preserve_system=True,
            preserve_recent=10  # Garder les 10 derniers messages
        )

        compressed_tokens = tm.count_messages_tokens(compressed)

        print(f"\n✅ Compression effectuée:")
        print(f"  - Messages originaux: {len(conversation)}")
        print(f"  - Messages compressés: {len(compressed)}")
        print(f"  - Ratio: {len(compressed)/len(conversation):.1%}")
        print(f"  - Tokens économisés: {total_tokens - compressed_tokens:,}")


async def main():
    """Exécute tous les exemples."""
    print("\n" + "=" * 60)
    print("EXEMPLES D'UTILISATION - UTILITAIRES DEVORA")
    print("=" * 60)
    print(f"\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Vérifier la clé API
    if not os.getenv("OPENROUTER_API_KEY"):
        print("\n⚠️  OPENROUTER_API_KEY non configurée")
        print("Les exemples s'exécuteront en mode simulation.\n")

    try:
        await analyze_request_example()
        await planning_example()
        await streaming_example()
        await token_management_example()

        print("\n" + "=" * 60)
        print("✅ Tous les exemples terminés avec succès!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
