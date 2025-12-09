# Data Squad - Expert Agents for Data, Analytics & Search

Le **Data Squad** regroupe 3 agents spécialisés dans la gestion des données, l'analytics et la recherche pour le système d'orchestration Devora.

## Agents Disponibles

### 1. Database Architect (`database_architect.py`)

**Expert en architecture de bases de données PostgreSQL/MongoDB**

#### Spécialités :
- Conception de schémas PostgreSQL (Supabase)
- Création et optimisation de migrations
- Implémentation de politiques RLS (Row Level Security)
- Optimisation des indexes et performances
- Modélisation de données et normalisation
- Génération de types TypeScript depuis le schéma
- Triggers et fonctions PostgreSQL

#### Méthodes principales :
```python
# Exécution générale (schéma complet)
await agent.execute({
    "architecture": {...},
    "data_models": [...],
    "features": [...],
    "optimization_target": "balanced"  # read_heavy, write_heavy, balanced, realtime
})

# Générer une migration
await agent.generate_migration({
    "type": "add_column",
    "table": "users",
    "changes": {...}
})

# Optimiser les indexes
await agent.optimize_indexes(
    queries=["SELECT * FROM users WHERE email = ?"],
    tables=["users", "projects"]
)

# Créer des politiques RLS
await agent.design_rls_policies(
    table="projects",
    access_pattern="user_owned",  # user_owned, team_based, hierarchical
    roles=["user", "admin"]
)

# Générer des types TypeScript
await agent.generate_types(schema_sql, language="typescript")
```

#### Fichiers générés :
- `migrations/001_initial_schema.sql` - Schéma complet
- `migrations/002_rls_policies.sql` - Politiques de sécurité
- `migrations/003_indexes.sql` - Optimisations
- `migrations/004_functions_triggers.sql` - Logique métier
- `types/database.ts` - Définitions TypeScript
- `DATABASE.md` - Documentation

---

### 2. Analytics Engineer (`analytics_engineer.py`)

**Expert en analytics, métriques et tracking d'événements**

#### Spécialités :
- Configuration PostHog/Mixpanel
- Tracking d'événements utilisateur
- Définition de métriques et KPIs
- Création de dashboards
- Configuration A/B testing
- Analyse de funnels de conversion
- Analytics temps réel
- Visualisation de données

#### Méthodes principales :
```python
# Exécution générale (setup analytics complet)
await agent.execute({
    "features": ["User auth", "Projects", "Billing"],
    "metrics": ["DAU", "Activation rate", "Conversion"],
    "platform": "posthog",  # posthog, mixpanel
    "tracking_plan": {...}
})

# Créer un tracking plan
await agent.create_tracking_plan([
    {"name": "User signup", "properties": ["method", "source"]},
    {"name": "Project created", "properties": ["template", "is_first"]}
])

# Créer un dashboard
await agent.create_dashboard(
    metrics=["DAU", "MAU", "Retention"],
    dashboard_type="product"  # product, marketing, executive
)

# Configurer un A/B test
await agent.setup_ab_test({
    "name": "checkout_button",
    "variants": ["control", "variant_a"],
    "success_metric": "conversion_rate"
})

# Analyser un funnel
await agent.analyze_funnel([
    "User_SignedUp",
    "Project_Created",
    "Payment_Completed"
])
```

#### Fichiers générés :
- `lib/analytics.ts` - Setup analytics
- `lib/analytics/events.ts` - Catalogue d'événements
- `hooks/useAnalytics.ts` - Hooks React
- `lib/analytics/server.ts` - Tracking serveur
- `analytics/queries/metrics.sql` - Requêtes métriques
- `analytics/dashboards/config.json` - Configuration dashboards
- `lib/experiments.ts` - A/B testing
- `ANALYTICS.md` - Documentation

---

### 3. Search & RAG Specialist (`search_rag_specialist.py`)

**Expert en recherche full-text, sémantique et systèmes RAG**

#### Spécialités :
- Recherche full-text (PostgreSQL, ElasticSearch)
- Vector databases (pgvector, Pinecone, Weaviate)
- Recherche sémantique avec embeddings
- Pipelines RAG (Retrieval-Augmented Generation)
- Recherche hybride (keyword + sémantique)
- Optimisation de pertinence
- Chunking de documents
- Re-ranking

#### Méthodes principales :
```python
# Exécution générale (setup recherche complet)
await agent.execute({
    "search_type": "hybrid",  # full_text, semantic, hybrid
    "data_sources": ["Documentation", "Blog posts", "Products"],
    "rag_enabled": True,
    "vector_db": "pgvector"  # pgvector, pinecone, weaviate
})

# Implémenter recherche full-text
await agent.implement_fulltext_search(
    tables=["documents", "posts"],
    columns={"documents": ["title", "content"], "posts": ["title", "body"]}
)

# Implémenter recherche vectorielle
await agent.implement_vector_search(
    documents=["Documentation", "Blog"],
    embedding_model="openai"  # openai, cohere, local
)

# Implémenter pipeline RAG
await agent.implement_rag_pipeline({
    "knowledge_base": {
        "sources": ["docs", "faqs", "tutorials"],
        "chunk_size": 1000,
        "overlap": 200
    }
})

# Recherche hybride
await agent.implement_hybrid_search({
    "semantic_weight": 0.7,
    "keyword_weight": 0.3,
    "rerank": True
})

# Optimiser les embeddings
await agent.optimize_embeddings(
    use_case="product_search",
    constraints={"budget": "low", "latency": "<100ms"}
)
```

#### Fichiers générés :
- `migrations/xxx_search_setup.sql` - Infrastructure de recherche
- `lib/search/index.ts` - Service de recherche
- `lib/embeddings.ts` - Génération d'embeddings
- `lib/rag.ts` - Pipeline RAG
- `lib/search/hybrid.ts` - Recherche hybride
- `api/search/route.ts` - API endpoints
- `components/search/SearchBar.tsx` - Composants UI
- `SEARCH.md` - Documentation

---

## Utilisation

### Import des agents

```python
from orchestration.agents.data_squad import (
    DatabaseArchitectAgent,
    AnalyticsEngineerAgent,
    SearchRAGSpecialistAgent,
    get_agent,
    list_agents
)

# Créer un agent directement
agent = DatabaseArchitectAgent(api_key="your-key")

# Ou utiliser la factory
agent = get_agent('database_architect', api_key="your-key")

# Lister tous les agents disponibles
agents = list_agents()
```

### Exemple complet : Projet SaaS

```python
import asyncio
import os
from orchestration.agents.data_squad import (
    DatabaseArchitectAgent,
    AnalyticsEngineerAgent,
    SearchRAGSpecialistAgent
)

async def setup_saas_project():
    api_key = os.environ.get("OPENROUTER_API_KEY")

    # 1. Architecture de base de données
    db_agent = DatabaseArchitectAgent(api_key)
    db_result = await db_agent.execute({
        "architecture": {
            "type": "SaaS",
            "multi_tenant": True,
            "auth": "supabase"
        },
        "data_models": [
            {
                "name": "Organization",
                "fields": {"name": "string", "plan": "enum"},
                "relations": []
            },
            {
                "name": "Project",
                "fields": {"name": "string", "status": "enum"},
                "relations": ["organization_id -> organizations.id"]
            }
        ],
        "features": ["Multi-tenancy", "Subscriptions", "Projects"],
        "optimization_target": "balanced"
    })

    print(f"Database: {len(db_result['files'])} files generated")

    # 2. Analytics et tracking
    analytics_agent = AnalyticsEngineerAgent(api_key)
    analytics_result = await analytics_agent.execute({
        "features": [
            "User authentication",
            "Organization creation",
            "Project management",
            "Billing"
        ],
        "metrics": [
            "Daily Active Users",
            "Activation rate (signup to first project)",
            "Free to paid conversion",
            "Monthly Recurring Revenue"
        ],
        "platform": "posthog"
    })

    print(f"Analytics: {len(analytics_result['files'])} files generated")

    # 3. Recherche et RAG
    search_agent = SearchRAGSpecialistAgent(api_key)
    search_result = await search_agent.execute({
        "search_type": "hybrid",
        "data_sources": [
            "Project documentation",
            "Organization knowledge base",
            "Help center articles"
        ],
        "rag_enabled": True,
        "vector_db": "pgvector"
    })

    print(f"Search: {len(search_result['files'])} files generated")

    # Sauvegarder tous les fichiers
    all_files = (
        db_result['files'] +
        analytics_result['files'] +
        search_result['files']
    )

    for file in all_files:
        filepath = f"generated/{file['name']}"
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(file['content'])
        print(f"Created: {filepath}")

    print(f"\nTotal: {len(all_files)} files generated")

if __name__ == "__main__":
    asyncio.run(setup_saas_project())
```

---

## Architecture des Agents

Tous les agents du Data Squad héritent de `BaseAgent` et suivent cette structure :

```python
class DataSquadAgent(BaseAgent):
    def __init__(self, api_key: str, model: str = "openai/gpt-4o"):
        super().__init__("AgentName", api_key, model)

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Méthode principale d'exécution"""
        # Prépare le prompt système
        system_prompt = self._get_system_prompt()

        # Construit le contexte
        context = self._build_context(task)

        # Appelle le LLM
        response = await self.call_llm([{"role": "user", "content": context}], system_prompt)

        # Parse la réponse
        files = self._parse_code_blocks(response)

        return {
            "success": True,
            "files": files,
            "raw_response": response
        }
```

### Méthodes communes :

- `execute(task)` - Exécution principale
- `_get_system_prompt()` - Prompt système spécialisé
- `_build_context(task)` - Construction du contexte
- `_parse_code_blocks(response)` - Extraction des fichiers générés
- `call_llm(messages, system_prompt)` - Appel au LLM (hérité de BaseAgent)

---

## Capabilities par Agent

### Database Architect
- `schema_design` - Conception de schémas
- `migrations` - Gestion de migrations
- `rls_policies` - Politiques de sécurité
- `index_optimization` - Optimisation performances
- `type_generation` - Génération de types
- `data_modeling` - Modélisation de données

### Analytics Engineer
- `event_tracking` - Tracking d'événements
- `metrics_definition` - Définition de métriques
- `dashboard_creation` - Création de dashboards
- `ab_testing` - Tests A/B
- `funnel_analysis` - Analyse de funnels
- `posthog_setup` - Configuration PostHog
- `mixpanel_setup` - Configuration Mixpanel

### Search & RAG Specialist
- `fulltext_search` - Recherche full-text
- `vector_search` - Recherche vectorielle
- `hybrid_search` - Recherche hybride
- `rag_pipeline` - Pipeline RAG
- `embeddings` - Gestion d'embeddings
- `semantic_search` - Recherche sémantique

---

## Tags pour Recherche

Chaque agent est taggé pour faciliter la découverte :

- **Database Architect**: `database`, `postgresql`, `supabase`, `schema`, `sql`
- **Analytics Engineer**: `analytics`, `metrics`, `tracking`, `posthog`, `mixpanel`, `kpi`
- **Search & RAG Specialist**: `search`, `rag`, `embeddings`, `vector`, `semantic`, `pgvector`

---

## Tests

Exécuter les tests :

```bash
# Test d'imports et création d'agents
python test_data_squad.py

# Test individuel d'un agent
python -m orchestration.agents.data_squad.database_architect
python -m orchestration.agents.data_squad.analytics_engineer
python -m orchestration.agents.data_squad.search_rag_specialist
```

---

## Statistiques

- **Total lignes de code** : ~2,645 lignes
- **Agents** : 3
- **Capabilities totales** : 19
- **Méthodes publiques** : ~15 par agent
- **Patterns implémentés** :
  - PostgreSQL Full-text Search
  - pgvector Semantic Search
  - RLS Policies
  - PostHog/Mixpanel Integration
  - RAG Pipeline
  - Hybrid Search
  - A/B Testing
  - Dashboard Configuration

---

## Roadmap

### Améliorations futures :
- [ ] Support MongoDB schema design
- [ ] ElasticSearch integration
- [ ] Pinecone vector database
- [ ] Advanced re-ranking algorithms
- [ ] Real-time analytics streaming
- [ ] Custom embedding models
- [ ] Multi-language search
- [ ] Graph database patterns
- [ ] Time-series optimizations
- [ ] Data warehouse integrations

---

## Contribution

Pour ajouter un nouvel agent au Data Squad :

1. Créer `new_agent.py` dans ce répertoire
2. Hériter de `BaseAgent`
3. Implémenter `execute()` et méthodes spécialisées
4. Ajouter l'agent dans `__init__.py`
5. Mettre à jour `AGENTS_METADATA`
6. Ajouter les tests
7. Documenter dans ce README

---

## Support

Pour toute question sur les agents du Data Squad :
- Consulter la documentation de chaque agent (docstrings)
- Lancer les exemples d'utilisation dans chaque fichier
- Voir les tests dans `test_data_squad.py`

**Créé pour Devora Transformation** 🚀
