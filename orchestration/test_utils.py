"""
Script de test pour vérifier les utilitaires Devora.

Usage:
    python orchestration/test_utils.py
"""

import asyncio
import sys
import io
from pathlib import Path

# Fix encoding pour Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))


async def test_llm_client():
    """Test du LLMClient."""
    print("\n=== Test LLMClient ===")

    from orchestration.utils import create_llm_client, ModelType

    try:
        async with await create_llm_client() as client:
            print("✓ Client LLM créé")

            # Test de comptage de tokens
            text = "Ceci est un test simple."
            tokens = client.count_tokens(text)
            print(f"✓ Comptage tokens: {tokens} tokens pour '{text}'")

            # Test de complétion (nécessite OPENROUTER_API_KEY)
            try:
                response = await client.complete(
                    messages=[{"role": "user", "content": "Dis bonjour en 5 mots"}],
                    model=ModelType.HAIKU,  # Plus rapide
                    max_tokens=50,
                )
                print(f"✓ Complétion réussie: {response.content[:50]}...")
                print(f"  Tokens utilisés: {response.tokens_used}")
                print(f"  Modèle: {response.model}")
            except Exception as e:
                print(f"⚠ Complétion ignorée (clé API requise): {e}")

    except Exception as e:
        print(f"✗ Erreur LLMClient: {e}")
        return False

    return True


def test_logger():
    """Test du Logger."""
    print("\n=== Test Logger ===")

    from orchestration.utils import get_logger

    try:
        logger = get_logger(__name__)
        print("✓ Logger créé")

        # Test logging simple
        logger.debug("Message de debug")
        logger.info("Message d'information")
        logger.warning("Message d'avertissement")
        print("✓ Logging simple OK")

        # Test logging structuré
        logger.info("Événement", user_id=123, action="test", status="success")
        print("✓ Logging structuré OK")

        # Test contexte
        context_logger = logger.with_context(module="test", session="test_123")
        context_logger.info("Message avec contexte")
        print("✓ Logging avec contexte OK")

    except Exception as e:
        print(f"✗ Erreur Logger: {e}")
        return False

    return True


def test_token_manager():
    """Test du TokenManager."""
    print("\n=== Test TokenManager ===")

    from orchestration.utils import TokenManager, count_tokens

    try:
        tm = TokenManager()
        print("✓ TokenManager créé")

        # Test comptage
        text = "Ceci est un exemple de texte à analyser pour compter les tokens."
        tokens = tm.count_tokens(text, model="claude")
        print(f"✓ Comptage: {tokens} tokens pour {len(text)} caractères")

        # Test avec fonction utilitaire
        tokens2 = count_tokens(text)
        assert tokens == tokens2, "Les deux méthodes doivent donner le même résultat"
        print("✓ Fonction utilitaire OK")

        # Test messages
        messages = [
            {"role": "system", "content": "Tu es un assistant."},
            {"role": "user", "content": "Bonjour!"},
        ]
        msg_tokens = tm.count_messages_tokens(messages)
        print(f"✓ Messages: {msg_tokens} tokens pour {len(messages)} messages")

        # Test limites
        limit = tm.get_model_limit("anthropic/claude-3.5-sonnet")
        print(f"✓ Limite Claude Sonnet: {limit:,} tokens")

        # Test vérification de capacité
        fits, used, available = tm.check_context_fit(
            messages,
            model="anthropic/claude-3.5-sonnet",
            max_completion_tokens=4096,
        )
        print(f"✓ Vérification: {'OK' if fits else 'Trop grand'} ({used} utilisés, {available} disponibles)")

        # Test compression
        long_text = "test " * 1000
        result = tm.compress_context(
            text=long_text,
            target_tokens=100,
            strategy="truncate",
        )
        print(f"✓ Compression: {result.original_tokens} → {result.compressed_tokens} tokens (ratio: {result.compression_ratio:.2%})")

    except Exception as e:
        print(f"✗ Erreur TokenManager: {e}")
        return False

    return True


async def test_progress_emitter():
    """Test du ProgressEmitter."""
    print("\n=== Test ProgressEmitter ===")

    from orchestration.utils import ProgressEmitter, EventType

    try:
        emitter = ProgressEmitter(session_id="test_session")
        print(f"✓ ProgressEmitter créé (session: {emitter.session_id})")

        # Test callback
        events_received = []

        def callback(event):
            events_received.append(event.type.value)

        emitter.on_any(callback)
        print("✓ Callback enregistré")

        # Test émission
        await emitter.workflow_start("test_workflow", {"type": "test"})
        await emitter.agent_start("test_agent", "Test Agent")
        await emitter.task_progress("task_1", 0.5, "En cours...")
        await emitter.agent_complete("test_agent", {"status": "success"})
        await emitter.workflow_complete("test_workflow", {"result": "ok"})

        print(f"✓ {len(events_received)} événements émis")

        # Test récupération
        all_events = emitter.get_events(limit=10)
        print(f"✓ {len(all_events)} événements dans le buffer")

        # Test statistiques
        stats = emitter.get_stats()
        print(f"✓ Stats: {stats['total_events']} événements totaux")

        # Test SSE
        queue = await emitter.create_sse_stream()
        print("✓ Queue SSE créée")

        # Émettre un événement de test
        await emitter.log("info", "Test SSE")

        # Vérifier que l'événement est dans la queue
        event = await asyncio.wait_for(queue.get(), timeout=1.0)
        sse_format = event.to_sse()
        print(f"✓ Format SSE OK: {sse_format[:50]}...")

        emitter.remove_sse_stream(queue)

    except Exception as e:
        print(f"✗ Erreur ProgressEmitter: {e}")
        return False

    return True


def test_prompts():
    """Test des templates de prompts."""
    print("\n=== Test Templates Prompts ===")

    from orchestration.templates import (
        RouterPrompts,
        PlannerPrompts,
        format_prompt,
        create_messages,
    )

    try:
        # Test format_prompt
        prompt = format_prompt(
            RouterPrompts.ANALYZE_REQUEST,
            query="Test query",
            context="Test context",
        )
        assert "Test query" in prompt
        assert "Test context" in prompt
        print("✓ format_prompt OK")

        # Test create_messages
        messages = create_messages(
            system_prompt=RouterPrompts.SYSTEM,
            user_prompt=prompt,
        )
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        print("✓ create_messages OK")

        # Test avec historique
        messages_with_history = create_messages(
            system_prompt=PlannerPrompts.SYSTEM,
            user_prompt="New prompt",
            history=[
                {"role": "user", "content": "Previous question"},
                {"role": "assistant", "content": "Previous answer"},
            ],
        )
        assert len(messages_with_history) == 4
        print("✓ create_messages avec historique OK")

        # Vérifier que tous les prompts sont accessibles
        assert hasattr(RouterPrompts, "SYSTEM")
        assert hasattr(PlannerPrompts, "CREATE_PLAN")
        print("✓ Tous les prompts accessibles")

    except Exception as e:
        print(f"✗ Erreur Templates Prompts: {e}")
        return False

    return True


def test_responses():
    """Test des templates de réponses."""
    print("\n=== Test Templates Réponses ===")

    from orchestration.templates import (
        Metadata,
        ResponseStatus,
        RouterResponse,
        Task,
        TaskType,
        create_success_response,
        create_error_response,
    )

    try:
        # Test Metadata
        metadata = Metadata(
            agent_id="test_agent",
            agent_type="test",
            execution_time=1.23,
            tokens_used=456,
        )
        print("✓ Metadata créé")

        # Test RouterResponse
        response = RouterResponse(
            status=ResponseStatus.SUCCESS,
            metadata=metadata,
            intent="Test intent",
            complexity="medium",
            workflow="test_workflow",
            required_agents=["agent1", "agent2"],
            estimated_steps=3,
        )
        print("✓ RouterResponse créé")

        # Test to_dict
        response_dict = response.to_dict()
        assert "status" in response_dict
        assert "metadata" in response_dict
        assert response_dict["data"]["intent"] == "Test intent"
        print("✓ to_dict() OK")

        # Test Task
        task = Task(
            id="task_1",
            description="Test task",
            type=TaskType.IMPLEMENTATION,
            priority=1,
        )
        task_dict = task.to_dict()
        assert task_dict["type"] == "implementation"
        print("✓ Task OK")

        # Test create_success_response
        success = create_success_response(
            agent_id="test",
            agent_type="test",
            data={"result": "ok"},
        )
        assert success.is_success()
        print("✓ create_success_response OK")

        # Test create_error_response
        error = create_error_response(
            agent_id="test",
            agent_type="test",
            error_message="Test error",
            error_code="ERR_TEST",
        )
        assert not error.is_success()
        assert error.status == ResponseStatus.ERROR
        print("✓ create_error_response OK")

    except Exception as e:
        import traceback
        print(f"✗ Erreur Templates Réponses: {e}")
        traceback.print_exc()
        return False

    return True


async def main():
    """Exécute tous les tests."""
    print("=" * 60)
    print("TESTS DES UTILITAIRES DEVORA")
    print("=" * 60)

    results = []

    # Tests synchrones
    results.append(("Logger", test_logger()))
    results.append(("TokenManager", test_token_manager()))
    results.append(("Prompts", test_prompts()))
    results.append(("Responses", test_responses()))

    # Tests asynchrones
    results.append(("LLMClient", await test_llm_client()))
    results.append(("ProgressEmitter", await test_progress_emitter()))

    # Résumé
    print("\n" + "=" * 60)
    print("RÉSUMÉ DES TESTS")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")

    print(f"\n{passed}/{total} tests réussis")

    if passed == total:
        print("\n🎉 Tous les tests sont passés!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) échoué(s)")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
