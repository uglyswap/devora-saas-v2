# Guide des Utilitaires Devora

Documentation complète des utilitaires d'orchestration (utils/) et templates.

## Table des Matières

- [Vue d'Ensemble](#vue-densemble)
- [LLMClient](#llmclient)
- [Logger](#logger)
- [TokenManager](#tokenmanager)
- [ProgressEmitter](#progressemitter)
- [Templates de Prompts](#templates-de-prompts)
- [Templates de Réponses](#templates-de-réponses)
- [Exemples Complets](#exemples-complets)

---

## Vue d'Ensemble

Les utilitaires fournissent les composants de base pour l'orchestration:

- **LLMClient** - Communication avec l'API OpenRouter
- **Logger** - Logging structuré avec couleurs
- **TokenManager** - Gestion des tokens et contexte
- **ProgressEmitter** - Événements de progression SSE
- **Templates** - Prompts et schémas de réponses

---

## LLMClient

Client unifié pour les appels à l'API OpenRouter avec retry automatique et rate limiting.

### Configuration

```python
from orchestration.utils import LLMClient, LLMConfig, ModelType

# Configuration personnalisée
config = LLMConfig(
    api_key="sk-or-v1-...",
    base_url="https://openrouter.ai/api/v1",  # Défaut
    timeout=300,  # 5 minutes
    max_retries=3,
    rate_limit_delay=1.0,  # 1 seconde entre requêtes
)

client = LLMClient(config)
```

### Utilisation Basique

```python
# Avec context manager (recommandé)
async with LLMClient() as client:
    response = await client.complete(
        messages=[
            {"role": "user", "content": "Explique-moi les websockets"}
        ],
        model=ModelType.SONNET,
        temperature=0.7,
        max_tokens=2048,
    )

    print(response.content)
    print(f"Tokens: {response.tokens_used}")
    print(f"Modèle: {response.model}")
```

### Streaming

```python
async with LLMClient() as client:
    async for chunk in client.stream(
        messages=[{"role": "user", "content": "Écris un poème"}],
        model=ModelType.HAIKU,  # Plus rapide pour streaming
    ):
        print(chunk, end="", flush=True)
```

### Modèles Disponibles

```python
from orchestration.utils import ModelType

ModelType.SONNET       # anthropic/claude-3.5-sonnet
ModelType.HAIKU        # anthropic/claude-3.5-haiku
ModelType.OPUS         # anthropic/claude-opus-4
ModelType.GPT4         # openai/gpt-4-turbo
ModelType.DEEPSEEK     # deepseek/deepseek-chat
```

### Gestion d'Erreurs

```python
from orchestration.utils import RateLimitError
import httpx

try:
    response = await client.complete(messages)
except RateLimitError as e:
    print("Rate limit dépassé, attente...")
    await asyncio.sleep(5)
except httpx.HTTPError as e:
    print(f"Erreur HTTP: {e}")
```

### Factory Function

```python
from orchestration.utils import create_llm_client

# Utilise la variable d'environnement OPENROUTER_API_KEY
client = await create_llm_client()

# Ou avec clé explicite
client = await create_llm_client(api_key="sk-or-v1-...")
```

---

## Logger

Logger structuré avec support couleurs (dev) et JSON (prod).

### Configuration

```python
from orchestration.utils import setup_logger, get_logger

# Logger simple
logger = get_logger(__name__)

# Logger avec configuration personnalisée
logger = setup_logger(
    name="mon_module",
    level="DEBUG",  # DEBUG, INFO, WARN, ERROR, CRITICAL
    use_json=False,  # True pour production
    log_file="logs/app.log",  # Optionnel
)
```

### Utilisation

```python
# Logging simple
logger.info("Application démarrée")
logger.warning("Paramètre manquant, utilisation de la valeur par défaut")
logger.error("Erreur de connexion à la base de données", exc_info=True)

# Logging structuré
logger.info(
    "Requête traitée",
    user_id="user_123",
    duration_ms=245,
    status="success"
)
```

### Contexte Persistant

```python
# Créer un logger avec contexte
agent_logger = logger.with_context(
    agent_id="router-001",
    workflow="analysis",
    session_id="sess_abc123"
)

# Tous les logs incluront le contexte
agent_logger.info("Démarrage de l'agent")
# Output: ... | agent_id=router-001 | workflow=analysis | Démarrage de l'agent

agent_logger.error("Erreur détectée", error_code="ERR_001")
# Ajoute error_code au contexte existant
```

### Niveaux de Log

```python
logger.debug("Information de debug détaillée")
logger.info("Information générale")
logger.warning("Avertissement, pas bloquant")
logger.error("Erreur récupérable")
logger.critical("Erreur critique, arrêt probable")
logger.exception("Erreur avec traceback automatique")
```

### Output Couleurs

Les couleurs sont automatiques en mode terminal:
- **DEBUG**: Gris clair
- **INFO**: Bleu
- **WARN**: Jaune
- **ERROR**: Rouge vif
- **CRITICAL**: Rouge gras

### Format JSON (Production)

```python
logger = setup_logger("app", use_json=True)
logger.info("Événement", user_id=123, action="login")

# Output JSON:
# {"timestamp":"2024-12-09T10:30:45","level":"INFO","message":"Événement","extra":{"user_id":123,"action":"login"}}
```

---

## TokenManager

Gestionnaire de tokens pour optimiser l'utilisation du contexte LLM.

### Comptage de Tokens

```python
from orchestration.utils import TokenManager, count_tokens

tm = TokenManager()

# Compter tokens dans un texte
text = "Ceci est un exemple de texte assez long..."
token_count = tm.count_tokens(text, model="claude")

# Fonction utilitaire
token_count = count_tokens(text)  # Utilise l'instance globale
```

### Comptage de Messages

```python
messages = [
    {"role": "system", "content": "Tu es un assistant utile."},
    {"role": "user", "content": "Explique-moi la physique quantique."},
    {"role": "assistant", "content": "La physique quantique est..."},
]

total_tokens = tm.count_messages_tokens(messages, model="claude")
print(f"Total: {total_tokens} tokens")
```

### Vérification de Capacité

```python
fits, used, available = tm.check_context_fit(
    messages=messages,
    model="anthropic/claude-3.5-sonnet",
    max_completion_tokens=4096,
    safety_margin=0.1,  # 10% de marge
)

if fits:
    print(f"OK - {used} tokens utilisés, {available} disponibles")
else:
    print(f"Trop grand - {used} tokens > limite")
```

### Compression de Contexte

```python
from orchestration.utils import CompressionResult

# Compression de texte
long_text = "..." * 10000
result = tm.compress_context(
    text=long_text,
    target_tokens=1000,
    model="claude",
    strategy="truncate",  # ou "truncate_end", "sliding_window"
)

print(f"Original: {result.original_tokens} tokens")
print(f"Compressé: {result.compressed_tokens} tokens")
print(f"Ratio: {result.compression_ratio:.2%}")
print(f"Stratégie: {result.strategy_used}")
```

### Compression de Messages

```python
# Comprimer une conversation
compressed_messages = tm.compress_messages(
    messages=long_conversation,
    target_tokens=8000,
    model="claude",
    preserve_system=True,  # Garder les messages système
    preserve_recent=3,     # Garder les 3 derniers messages
)

# Les messages du milieu sont supprimés pour respecter la limite
```

### Limites par Modèle

```python
from orchestration.utils import ModelTokenLimits

# Récupérer la limite
limit = tm.get_model_limit("anthropic/claude-3.5-sonnet")
print(f"Limite: {limit:,} tokens")  # 200,000 tokens

# Limites disponibles
ModelTokenLimits.CLAUDE_SONNET.value  # 200,000
ModelTokenLimits.CLAUDE_HAIKU.value   # 200,000
ModelTokenLimits.GPT4_TURBO.value     # 128,000
ModelTokenLimits.DEEPSEEK.value       # 64,000
```

---

## ProgressEmitter

Émetteur d'événements de progression pour intégration frontend via SSE.

### Configuration

```python
from orchestration.utils import ProgressEmitter, EventType, EventPriority

# Créer un émetteur
emitter = ProgressEmitter(
    session_id="session_abc123",  # Optionnel, généré auto
    buffer_size=1000,  # Taille du buffer
)
```

### Émission d'Événements

```python
# Événement workflow
await emitter.workflow_start("workflow_1", {"type": "analysis"})

# Événement agent
await emitter.agent_start("router-001", "Router Agent")
await emitter.agent_thinking("router-001", "Analyse de la requête...")
await emitter.agent_complete("router-001", {"status": "success"})

# Événement task
await emitter.task_progress(
    task_id="task_1",
    progress=0.5,  # 0.0 à 1.0
    message="Traitement en cours...",
    agent_id="analyzer-001"
)

# Événement LLM streaming
await emitter.llm_stream_chunk("Voici", agent_id="writer-001")
await emitter.llm_stream_chunk(" le résultat", agent_id="writer-001")

# Log
await emitter.log("info", "Opération réussie", duration_ms=125)

# Métrique
await emitter.metric("response_time", 0.245, unit="seconds", endpoint="/api/analyze")
```

### Événement Générique

```python
await emitter.emit(
    event_type=EventType.AGENT_START,
    data={"agent_name": "CustomAgent", "version": "1.0"},
    priority=EventPriority.HIGH,
    agent_id="custom-001",
    task_id="task_42",
)
```

### Callbacks

```python
# Callback pour un type d'événement
async def on_agent_complete(event):
    print(f"Agent {event.agent_id} terminé!")

emitter.on(EventType.AGENT_COMPLETE, on_agent_complete)

# Callback global (tous les événements)
def log_all_events(event):
    print(f"[{event.type.value}] {event.data}")

emitter.on_any(log_all_events)

# Les callbacks peuvent être sync ou async
```

### Streaming SSE

```python
# Créer une queue pour SSE
queue = await emitter.create_sse_stream()

# Dans un endpoint FastAPI
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

@app.get("/events")
async def stream_events():
    async def event_generator():
        queue = await emitter.create_sse_stream()
        try:
            while True:
                event = await queue.get()
                yield event.to_sse()
        finally:
            emitter.remove_sse_stream(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

### Récupération d'Événements

```python
# Tous les événements récents
events = emitter.get_events(limit=100)

# Filtrer par type
agent_events = emitter.get_events(
    event_type=EventType.AGENT_COMPLETE,
    limit=50
)

# Statistiques
stats = emitter.get_stats()
print(stats)
# {
#     "total_events": 1523,
#     "events_by_type": {"workflow.start": 10, "agent.complete": 45, ...},
#     "start_time": "2024-12-09T10:00:00",
#     "active_sse_streams": 3,
#     "buffer_size": 1000
# }
```

### Types d'Événements

```python
from orchestration.utils import EventType

# Workflow
EventType.WORKFLOW_START
EventType.WORKFLOW_COMPLETE
EventType.WORKFLOW_ERROR

# Agent
EventType.AGENT_START
EventType.AGENT_THINKING
EventType.AGENT_COMPLETE
EventType.AGENT_ERROR

# Task
EventType.TASK_START
EventType.TASK_PROGRESS
EventType.TASK_COMPLETE
EventType.TASK_ERROR

# LLM
EventType.LLM_REQUEST
EventType.LLM_RESPONSE
EventType.LLM_STREAM_CHUNK
EventType.LLM_ERROR

# Général
EventType.LOG
EventType.METRIC
EventType.DEBUG
```

---

## Templates de Prompts

Templates optimisés pour chaque agent avec variables dynamiques.

### Utilisation Basique

```python
from orchestration.templates import RouterPrompts, format_prompt, create_messages

# Formater un template
prompt = format_prompt(
    RouterPrompts.ANALYZE_REQUEST,
    query="Analyse les ventes du Q4",
    context="E-commerce B2B, 1000 transactions/jour"
)

# Créer des messages pour l'API
messages = create_messages(
    system_prompt=RouterPrompts.SYSTEM,
    user_prompt=prompt,
    history=[  # Optionnel
        {"role": "user", "content": "Question précédente"},
        {"role": "assistant", "content": "Réponse précédente"}
    ]
)

# Envoyer au LLM
response = await llm_client.complete(messages)
```

### Prompts Disponibles

```python
from orchestration.templates import (
    RouterPrompts,
    PlannerPrompts,
    ResearcherPrompts,
    AnalystPrompts,
    ImplementerPrompts,
    ValidatorPrompts,
    OrchestratorPrompts,
)

# Router
RouterPrompts.SYSTEM              # Prompt système
RouterPrompts.ANALYZE_REQUEST     # Analyser une requête
RouterPrompts.ROUTE_TO_AGENTS     # Router vers des agents

# Planner
PlannerPrompts.SYSTEM
PlannerPrompts.CREATE_PLAN        # Créer un plan de tâches
PlannerPrompts.OPTIMIZE_PLAN      # Optimiser un plan

# Researcher
ResearcherPrompts.SYSTEM
ResearcherPrompts.RESEARCH_TOPIC  # Rechercher un sujet
ResearcherPrompts.SYNTHESIZE      # Synthétiser des données

# Analyst
AnalystPrompts.SYSTEM
AnalystPrompts.ANALYZE_DATA       # Analyser des données
AnalystPrompts.COMPARE_OPTIONS    # Comparer des options

# Implementer
ImplementerPrompts.SYSTEM
ImplementerPrompts.IMPLEMENT_TASK # Implémenter une tâche
ImplementerPrompts.GENERATE_CODE  # Générer du code

# Validator
ValidatorPrompts.SYSTEM
ValidatorPrompts.VALIDATE_OUTPUT  # Valider un résultat
ValidatorPrompts.VERIFY_COMPLIANCE # Vérifier la conformité

# Orchestrator
OrchestratorPrompts.SYSTEM
OrchestratorPrompts.COORDINATE_WORKFLOW # Coordonner un workflow
```

### Exemple Complet

```python
# Créer un plan avec le Planner
plan_prompt = format_prompt(
    PlannerPrompts.CREATE_PLAN,
    objective="Développer une API REST pour gestion de tâches",
    constraints="- Budget: 2 semaines\n- Stack: FastAPI + PostgreSQL\n- MVP seulement",
    context="Équipe de 2 développeurs, infrastructure AWS existante"
)

messages = create_messages(
    system_prompt=PlannerPrompts.SYSTEM,
    user_prompt=plan_prompt
)

response = await llm_client.complete(messages, model=ModelType.SONNET)
plan_data = json.loads(response.content)
```

---

## Templates de Réponses

Schémas structurés pour les réponses des agents avec validation.

### Types de Réponses

```python
from orchestration.templates import (
    RouterResponse,
    PlannerResponse,
    ResearcherResponse,
    AnalystResponse,
    ImplementerResponse,
    ValidatorResponse,
    OrchestratorResponse,
    ErrorResponse,
)
```

### Création de Réponses

```python
from orchestration.templates import (
    Metadata,
    ResponseStatus,
    RouterResponse,
    create_success_response,
)

# Métadonnées communes
metadata = Metadata(
    agent_id="router-001",
    agent_type="router",
    execution_time=1.23,
    tokens_used=456,
    model_used="anthropic/claude-3.5-sonnet"
)

# Réponse spécifique
response = RouterResponse(
    status=ResponseStatus.SUCCESS,
    metadata=metadata,
    intent="Analyse de données de ventes",
    complexity="high",
    workflow="data_analysis",
    required_agents=["researcher", "analyst"],
    estimated_steps=5,
    reasoning="Requête complexe nécessitant recherche approfondie"
)

# Convertir en dict
response_dict = response.to_dict()
```

### Helper Functions

```python
from orchestration.templates import create_success_response, create_error_response

# Réponse de succès simple
success = create_success_response(
    agent_id="test-001",
    agent_type="test",
    data={"result": "success", "value": 42},
    execution_time=0.5,
    tokens_used=120
)

# Réponse d'erreur
error = create_error_response(
    agent_id="agent-001",
    agent_type="planner",
    error_message="Requête mal formée",
    error_type="ValidationError",
    error_code="ERR_INVALID_INPUT",
    traceback="...",  # Optionnel
    recovery_suggestions=[
        "Vérifier le format de la requête",
        "Fournir plus de contexte"
    ]
)
```

### Structures de Données

```python
from orchestration.templates import (
    Task,
    Finding,
    Metric,
    Pattern,
    Recommendation,
    FileOutput,
    ValidationCheck,
    QualityMetrics,
)

# Tâche
task = Task(
    id="task_1",
    description="Créer le modèle de données",
    type=TaskType.IMPLEMENTATION,
    priority=1,
    dependencies=["task_0"],
    estimated_duration="2 heures",
    resources_needed=["database_access"],
    success_criteria=["Tests passent", "Migration réussie"]
)

# Finding (recherche)
finding = Finding(
    key_point="Performance critique pour les requêtes complexes",
    details="Les index composites améliorent la performance de 10x",
    source="PostgreSQL Documentation",
    confidence=0.95,
    supporting_evidence=["Benchmark test", "Case study Acme Corp"]
)

# Metric (analyse)
metric = Metric(
    value=245.3,
    unit="ms",
    trend="up",
    significance="high"
)

# Recommendation
rec = Recommendation(
    recommendation="Implémenter un cache Redis",
    priority=1,
    expected_impact="Réduction de 50% du temps de réponse",
    confidence=0.9,
    implementation_steps=[
        "Installer Redis",
        "Configurer le client",
        "Implémenter la logique de cache"
    ]
)
```

### Validation de Schéma

```python
from orchestration.templates import validate_response_schema

response_dict = {
    "status": "success",
    "metadata": {...},
    "data": {
        "result": "ok",
        "nested": {"value": 42}
    }
}

# Vérifier les champs requis
missing = validate_response_schema(
    response_dict,
    expected_fields=["status", "metadata", "data.result", "data.nested.value"]
)

if missing:
    print(f"Champs manquants: {missing}")
```

---

## Exemples Complets

### Exemple 1: Agent Simple avec Tous les Utils

```python
import asyncio
from orchestration.utils import (
    create_llm_client,
    get_logger,
    TokenManager,
    ProgressEmitter,
    EventType,
)
from orchestration.templates import (
    PlannerPrompts,
    create_messages,
    format_prompt,
    PlannerResponse,
    Metadata,
    ResponseStatus,
)

async def create_project_plan(objective: str):
    # Setup
    logger = get_logger(__name__)
    emitter = ProgressEmitter()
    tm = TokenManager()

    # Logging avec contexte
    logger = logger.with_context(agent="planner", session="demo")

    # Callback pour progression
    def log_event(event):
        logger.info(f"Event: {event.type.value}", **event.data)

    emitter.on_any(log_event)

    # Démarrage
    await emitter.workflow_start("planning", {"objective": objective})
    logger.info("Démarrage de la planification", objective=objective)

    # Créer le prompt
    prompt = format_prompt(
        PlannerPrompts.CREATE_PLAN,
        objective=objective,
        constraints="Budget: 2 semaines\nÉquipe: 2 personnes",
        context="Stack: Python, FastAPI, PostgreSQL"
    )

    messages = create_messages(
        system_prompt=PlannerPrompts.SYSTEM,
        user_prompt=prompt
    )

    # Vérifier les tokens
    token_count = tm.count_messages_tokens(messages)
    logger.info("Messages préparés", tokens=token_count)

    # Appel LLM
    async with await create_llm_client() as llm:
        await emitter.agent_start("planner-001", "Planner Agent")

        response = await llm.complete(
            messages,
            model=ModelType.SONNET,
            temperature=0.7,
            max_tokens=4096
        )

        logger.info(
            "Réponse reçue",
            tokens=response.tokens_used,
            model=response.model
        )

        # Créer la réponse structurée
        import json
        plan_data = json.loads(response.content)

        metadata = Metadata(
            agent_id="planner-001",
            agent_type="planner",
            execution_time=1.5,
            tokens_used=response.tokens_used,
            model_used=response.model
        )

        result = PlannerResponse(
            status=ResponseStatus.SUCCESS,
            metadata=metadata,
            tasks=[Task(**t) for t in plan_data.get("tasks", [])],
            execution_order=plan_data.get("execution_order", []),
            parallel_tasks=plan_data.get("parallel_tasks", []),
            milestones=plan_data.get("milestones", [])
        )

        await emitter.agent_complete("planner-001", result.to_dict())
        await emitter.workflow_complete("planning", {"status": "success"})

        return result

# Exécution
if __name__ == "__main__":
    result = asyncio.run(create_project_plan("Développer une API de gestion de tâches"))
    print(result.to_dict())
```

### Exemple 2: Streaming avec Progression

```python
async def stream_with_progress():
    emitter = ProgressEmitter()
    logger = get_logger(__name__)

    async with await create_llm_client() as llm:
        await emitter.agent_start("writer-001", "Writer Agent")

        full_response = ""
        chunk_count = 0

        async for chunk in llm.stream(
            messages=[{"role": "user", "content": "Écris un article sur l'IA"}],
            model=ModelType.HAIKU
        ):
            full_response += chunk
            chunk_count += 1

            # Émettre le chunk
            await emitter.llm_stream_chunk(chunk, agent_id="writer-001")

            # Progression estimée (basée sur tokens estimés)
            estimated_total = 2000
            current_tokens = len(full_response) // 4
            progress = min(current_tokens / estimated_total, 1.0)

            await emitter.task_progress(
                "writing",
                progress,
                f"{current_tokens} tokens générés",
                agent_id="writer-001"
            )

        logger.info("Streaming terminé", chunks=chunk_count, total_chars=len(full_response))
        await emitter.agent_complete("writer-001", {"word_count": len(full_response.split())})

asyncio.run(stream_with_progress())
```

### Exemple 3: Compression Intelligente

```python
async def smart_compression_example():
    tm = TokenManager()
    logger = get_logger(__name__)

    # Longue conversation
    messages = [
        {"role": "system", "content": "Tu es un assistant expert."},
        *[
            {
                "role": "user" if i % 2 == 0 else "assistant",
                "content": f"Message {i}: " + "texte " * 100
            }
            for i in range(100)
        ]
    ]

    # Vérifier si ça tient
    fits, used, available = tm.check_context_fit(
        messages,
        model="anthropic/claude-3.5-sonnet",
        max_completion_tokens=4096
    )

    logger.info("Vérification initiale", fits=fits, used=used, available=available)

    if not fits:
        # Compression nécessaire
        logger.warning("Compression nécessaire", overflow_tokens=used - available)

        compressed = tm.compress_messages(
            messages,
            target_tokens=available,
            preserve_recent=5,  # Garder les 5 derniers messages
            preserve_system=True
        )

        logger.info(
            "Compression effectuée",
            original_count=len(messages),
            compressed_count=len(compressed),
            ratio=len(compressed) / len(messages)
        )

        messages = compressed

    # Utiliser les messages (compressés ou non)
    async with await create_llm_client() as llm:
        response = await llm.complete(messages)
        logger.info("Réponse obtenue", tokens=response.tokens_used)

asyncio.run(smart_compression_example())
```

---

## Installation des Dépendances

```bash
# Dépendances requises
pip install httpx tenacity

# Optionnel (pour token counting précis)
pip install tiktoken
```

## Variables d'Environnement

```bash
# Fichier .env
OPENROUTER_API_KEY=sk-or-v1-...
LOG_LEVEL=INFO
DEFAULT_MODEL=anthropic/claude-3.5-sonnet
```

---

## Tests

```python
# Tester les imports
python -c "from orchestration.utils import *; print('Utils OK')"
python -c "from orchestration.templates import *; print('Templates OK')"

# Tests unitaires (si disponibles)
pytest orchestration/tests/utils/
```

---

## Support

Pour plus d'informations:
- **README principal**: [README.md](./README.md)
- **Documentation agents**: [AGENTS.md](./AGENTS.md)
- **GitHub Issues**: [Issues](https://github.com/votre-org/devora-transformation/issues)
