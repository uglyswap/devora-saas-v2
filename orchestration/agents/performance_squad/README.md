# Performance Squad

Le **Performance Squad** est un ensemble d'agents IA spécialisés dans l'optimisation des performances web et des bases de données. Ces agents utilisent Claude 3.5 Sonnet via OpenRouter pour analyser et optimiser différents aspects de vos applications.

## 🎯 Objectif

Fournir des analyses approfondies et des recommandations actionnables pour:
- Améliorer les Core Web Vitals (LCP, FID, CLS)
- Réduire la taille des bundles JavaScript
- Optimiser les requêtes et schemas de base de données
- Implémenter des stratégies de caching efficaces

## 📦 Agents

### 1. Performance Engineer (`performance_engineer.py`)

Agent expert en optimisation des performances frontend.

**Responsabilités:**
- ✅ Analyser les Core Web Vitals (LCP, FID, CLS, TTFB, FCP, TTI)
- ✅ Profiler le runtime JavaScript et identifier les bottlenecks
- ✅ Optimiser le rendering React (useMemo, useCallback, React.memo)
- ✅ Auditer les rapports Lighthouse
- ✅ Définir des performance budgets

**Seuils de performance:**
- LCP (Largest Contentful Paint): < 2.5s (Good), < 4.0s (Needs Improvement)
- FID (First Input Delay): < 100ms (Good), < 300ms (Needs Improvement)
- CLS (Cumulative Layout Shift): < 0.1 (Good), < 0.25 (Needs Improvement)
- TTFB (Time to First Byte): < 800ms (Good), < 1800ms (Needs Improvement)

**Exemple d'utilisation:**
```python
from performance_engineer import PerformanceEngineerAgent
from base_agent import AgentConfig

config = AgentConfig(
    name="perf-engineer",
    api_key="your-openrouter-key",
    model="anthropic/claude-3.5-sonnet"
)

agent = PerformanceEngineerAgent(config)

# Analyser les Core Web Vitals
result = agent.analyze_core_web_vitals(
    url="https://example.com",
    metrics={
        "lcp": 4.2,
        "fid": 150,
        "cls": 0.18,
        "ttfb": 1200
    },
    context="Page d'accueil e-commerce"
)

print(result["output"]["performance_analysis"]["analysis"])
```

---

### 2. Bundle Optimizer (`bundle_optimizer.py`)

Agent expert en optimisation de bundles JavaScript/CSS.

**Responsabilités:**
- ✅ Implémenter le code splitting (route-based, component-based)
- ✅ Configurer le tree shaking pour éliminer le dead code
- ✅ Optimiser les assets (images WebP/AVIF, fonts WOFF2, SVG)
- ✅ Analyser les dépendances npm et suggérer des alternatives légères
- ✅ Configurer la compression (Brotli, Gzip)

**Targets de bundle size:**
- Main bundle: < 100KB (gzipped)
- Vendor bundle: < 150KB (gzipped)
- Route chunk: < 50KB (gzipped)
- Total JS: < 250KB (gzipped)
- Total CSS: < 50KB (gzipped)

**Exemple d'utilisation:**
```python
from bundle_optimizer import BundleOptimizerAgent
from base_agent import AgentConfig

config = AgentConfig(
    name="bundle-optimizer",
    api_key="your-openrouter-key",
    model="anthropic/claude-3.5-sonnet"
)

agent = BundleOptimizerAgent(config)

# Optimiser le code splitting
result = agent.optimize_code_splitting(
    code="""
    import Dashboard from './pages/Dashboard';
    import Analytics from './pages/Analytics';
    """,
    bundler="webpack",
    framework="react"
)

print(result["output"]["bundle_optimization"]["recommendations"])
```

**Alternatives légères suggérées:**
| Package lourd | Taille | Alternative | Taille Alt | Gain |
|---------------|--------|-------------|------------|------|
| moment.js | 232KB | date-fns | 12KB | -220KB |
| lodash | 71KB | lodash-es | tree-shakable | ~50KB |
| axios | 13KB | ky / fetch | 4KB / 0KB | -9KB |

---

### 3. Database Optimizer (`database_optimizer.py`)

Agent expert en optimisation de bases de données SQL/NoSQL.

**Responsabilités:**
- ✅ Optimiser les requêtes SQL/MongoDB
- ✅ Créer les indexes appropriés (B-tree, Hash, GIN, GiST)
- ✅ Configurer le connection pooling (pg-pool, MySQL pool)
- ✅ Implémenter des stratégies de caching (Redis, Memcached)
- ✅ Optimiser les schemas (normalization, denormalization, partitioning)
- ✅ Analyser les query plans (EXPLAIN ANALYZE)

**Bases de données supportées:**
- PostgreSQL, MySQL, MariaDB, SQLite
- MongoDB, Cassandra, DynamoDB
- Redis (caching)

**Seuils de performance:**
- Excellent: < 10ms
- Good: < 50ms
- Acceptable: < 100ms
- Slow: < 500ms
- Critical: > 1000ms (⚠️ problème majeur)

**Exemple d'utilisation:**
```python
from database_optimizer import DatabaseOptimizerAgent
from base_agent import AgentConfig

config = AgentConfig(
    name="db-optimizer",
    api_key="your-openrouter-key",
    model="anthropic/claude-3.5-sonnet"
)

agent = DatabaseOptimizerAgent(config)

# Optimiser une requête SQL
result = agent.optimize_query(
    query="""
    SELECT u.id, u.name, p.title
    FROM users u
    LEFT JOIN posts p ON p.user_id = u.id
    WHERE u.created_at > '2024-01-01'
    ORDER BY p.created_at DESC;
    """,
    database="postgresql",
    execution_time=1847  # 1.8 secondes
)

print(result["output"]["database_optimization"]["recommendations"])
```

---

## 🚀 Installation

### 1. Prérequis

```bash
# Python 3.8+
python --version

# Installer les dépendances
pip install requests python-dotenv
```

### 2. Configuration

Créer un fichier `.env` à la racine:

```bash
OPENROUTER_API_KEY=your-openrouter-api-key-here
```

Obtenir une clé API OpenRouter: https://openrouter.ai/keys

### 3. Structure

```
orchestration/agents/performance_squad/
├── __init__.py                  # Exports des agents
├── performance_engineer.py      # Agent Performance Engineer
├── bundle_optimizer.py          # Agent Bundle Optimizer
├── database_optimizer.py        # Agent Database Optimizer
├── example_usage.py             # Exemples d'utilisation
└── README.md                    # Documentation
```

---

## 📖 Utilisation

### Exemple simple

```python
import os
from dotenv import load_dotenv
from performance_engineer import PerformanceEngineerAgent
from base_agent import AgentConfig

# Charger les variables d'environnement
load_dotenv()

# Configuration
config = AgentConfig(
    name="perf-agent",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    model="anthropic/claude-3.5-sonnet",
    temperature=0.3,
    max_tokens=4096
)

# Créer l'agent
agent = PerformanceEngineerAgent(config)

# Exécuter une analyse
result = agent.run({
    "task_type": "core_web_vitals",
    "url": "https://example.com",
    "metrics": {
        "lcp": 3.5,
        "fid": 120,
        "cls": 0.15
    },
    "context": "Landing page with hero image"
})

# Afficher les résultats
if result["status"] == "success":
    print(result["output"]["performance_analysis"]["analysis"])
else:
    print(f"Error: {result['error']}")
```

### Exemple d'audit complet

```bash
# Exécuter les exemples
python example_usage.py
```

Cela exécutera:
1. Analyse des Core Web Vitals
2. Optimisation du code splitting
3. Optimisation d'une requête SQL
4. Audit complet de performance

---

## 🎨 Types de tâches

### Performance Engineer

| Task Type | Description | Input |
|-----------|-------------|-------|
| `core_web_vitals` | Analyse LCP, FID, CLS, TTFB | Métriques mesurées |
| `js_profiling` | Profile JavaScript, détecte bottlenecks | Code ou profiling data |
| `react_optimization` | Optimise rendering React | Code React |
| `lighthouse_audit` | Analyse rapport Lighthouse | Rapport JSON |
| `performance_budget` | Définit performance budgets | Contexte app |
| `bottleneck_analysis` | Identifie bottlenecks généraux | Métriques et contexte |

### Bundle Optimizer

| Task Type | Description | Input |
|-----------|-------------|-------|
| `code_splitting` | Stratégie de code splitting | Code routing |
| `tree_shaking` | Configuration tree shaking | package.json |
| `asset_optimization` | Optimise images, fonts, SVG | Config assets |
| `dependency_analysis` | Analyse dépendances npm | package.json + stats |
| `compression_config` | Config Brotli/Gzip | Bundler |
| `bundle_analysis` | Analyse bundle complet | Bundle stats |

### Database Optimizer

| Task Type | Description | Input |
|-----------|-------------|-------|
| `query_optimization` | Optimise requête SQL/NoSQL | Query + EXPLAIN |
| `index_creation` | Stratégie d'indexing | Schema + queries |
| `connection_pooling` | Config connection pool | Database type |
| `caching_strategy` | Stratégie Redis/Memcached | Use case |
| `schema_optimization` | Optimise schema DB | Schema actuel |
| `query_plan_analysis` | Analyse EXPLAIN plan | Query + plan |

---

## 📊 Métriques et Monitoring

Chaque agent retourne des métriques détaillées:

```python
result = agent.run(input_data)

# Métriques d'exécution
print(result["metrics"])
# {
#     "total_tokens": 3847,
#     "prompt_tokens": 1234,
#     "completion_tokens": 2613,
#     "execution_time": 8.45,  # secondes
#     "retry_count": 0,
#     "error_count": 0
# }

# Status de l'agent
print(result["status"])  # "success" ou "failed"

# Timestamp
print(result["timestamp"])  # ISO 8601
```

---

## 🔧 Configuration avancée

### Personnaliser le modèle LLM

```python
config = AgentConfig(
    name="custom-agent",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    model="anthropic/claude-opus-4.5",  # Modèle plus puissant
    temperature=0.2,                     # Plus déterministe
    max_tokens=8192,                     # Réponses plus longues
    timeout=120,                         # 2 minutes timeout
    max_retries=5,                       # Plus de retries
    log_level="DEBUG"                    # Logs détaillés
)
```

### Callbacks pour le monitoring

```python
def on_agent_event(event: str, data: dict):
    if event == "agent_started":
        print(f"Agent {data['agent']} started")
    elif event == "execution_complete":
        print(f"Execution took {data['time']:.2f}s")
    elif event == "agent_completed":
        print(f"Total tokens: {data['metrics']['total_tokens']}")

# Ajouter le callback
agent.add_callback(on_agent_event)

# Exécuter
result = agent.run(input_data)
```

---

## 🧪 Tests

```bash
# Tester un agent spécifique
python -c "from performance_engineer import PerformanceEngineerAgent; print('✅ Import OK')"

# Exécuter les exemples
python example_usage.py
```

---

## 📝 Best Practices

### 1. Analyse des Core Web Vitals

```python
# ✅ BON: Inclure le contexte et les métriques
result = agent.analyze_core_web_vitals(
    url="https://example.com/product/123",
    metrics={"lcp": 3.2, "fid": 85, "cls": 0.12},
    context="Page produit avec galerie d'images, reviews, et related products"
)

# ❌ MAUVAIS: Métriques sans contexte
result = agent.analyze_core_web_vitals(
    url="https://example.com",
    metrics={"lcp": 3.2}
)
```

### 2. Optimisation de bundle

```python
# ✅ BON: Inclure les stats du bundle
result = agent.analyze_dependencies(
    package_json=package_json_content,
    bundle_stats={
        "total_size": 450000,
        "vendor_size": 320000,
        "app_size": 130000
    }
)

# ❌ MAUVAIS: Sans stats
result = agent.analyze_dependencies(package_json_content)
```

### 3. Optimisation de requêtes

```python
# ✅ BON: Inclure le query plan et le temps d'exécution
result = agent.optimize_query(
    query=sql_query,
    database="postgresql",
    query_plan=explain_output,
    execution_time=1234  # ms
)

# ❌ MAUVAIS: Query seule sans contexte
result = agent.optimize_query(query=sql_query)
```

---

## 🎓 Ressources

### Outils recommandés

**Performance monitoring:**
- [Lighthouse](https://developers.google.com/web/tools/lighthouse)
- [WebPageTest](https://www.webpagetest.org/)
- [Chrome DevTools](https://developer.chrome.com/docs/devtools/)

**Bundle analysis:**
- [Webpack Bundle Analyzer](https://github.com/webpack-contrib/webpack-bundle-analyzer)
- [source-map-explorer](https://github.com/danvk/source-map-explorer)
- [bundlephobia.com](https://bundlephobia.com/)

**Database profiling:**
- [pg_stat_statements](https://www.postgresql.org/docs/current/pgstatstatements.html) (PostgreSQL)
- [MySQL Performance Schema](https://dev.mysql.com/doc/refman/8.0/en/performance-schema.html)
- [MongoDB Profiler](https://www.mongodb.com/docs/manual/tutorial/manage-the-database-profiler/)

### Références

- [Web Vitals](https://web.dev/vitals/)
- [Core Web Vitals](https://web.dev/articles/vitals)
- [Webpack Optimization](https://webpack.js.org/guides/production/)
- [PostgreSQL Performance Tips](https://wiki.postgresql.org/wiki/Performance_Optimization)

---

## 🤝 Contribution

Pour ajouter un nouvel agent au Performance Squad:

1. Créer un nouveau fichier `new_agent.py`
2. Hériter de `BaseAgent`
3. Implémenter les méthodes abstraites:
   - `validate_input()`
   - `execute()`
   - `format_output()`
4. Ajouter l'export dans `__init__.py`
5. Documenter dans ce README

---

## 📄 License

MIT License - Devora Transformation Team

---

## 🆘 Support

Pour toute question ou problème:
- Consulter la documentation de `BaseAgent` dans `orchestration/core/base_agent.py`
- Vérifier les exemples dans `example_usage.py`
- Activer les logs DEBUG pour plus de détails

```python
config = AgentConfig(
    name="debug-agent",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    log_level="DEBUG"  # Active les logs détaillés
)
```
