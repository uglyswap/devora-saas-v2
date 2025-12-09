# Performance Squad - Quick Start Guide

Guide de démarrage rapide en 5 minutes.

## 1. Installation (30 secondes)

```bash
# Naviguer vers le dossier
cd C:/Users/quent/devora-transformation/orchestration/agents/performance_squad

# Vérifier Python
python --version  # Python 3.8+ requis

# Installer les dépendances (si nécessaire)
pip install requests python-dotenv
```

## 2. Configuration (1 minute)

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer .env et ajouter votre clé API OpenRouter
# OPENROUTER_API_KEY=sk-or-v1-xxxxx
```

Obtenir une clé API: https://openrouter.ai/keys

## 3. Vérification (30 secondes)

```bash
# Tester les imports
python -c "from performance_squad import PerformanceEngineerAgent, BundleOptimizerAgent, DatabaseOptimizerAgent; print('OK')"

# Exécuter les tests
python test_agents.py
```

## 4. Premier usage (2 minutes)

### Exemple 1: Analyser les Core Web Vitals

```python
import os
from dotenv import load_dotenv
from performance_engineer import PerformanceEngineerAgent
from base_agent import AgentConfig

load_dotenv()

config = AgentConfig(
    name="perf-test",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    model="anthropic/claude-3.5-sonnet"
)

agent = PerformanceEngineerAgent(config)

result = agent.analyze_core_web_vitals(
    url="https://example.com",
    metrics={
        "lcp": 3.5,   # Largest Contentful Paint (s)
        "fid": 120,   # First Input Delay (ms)
        "cls": 0.15   # Cumulative Layout Shift
    },
    context="Landing page e-commerce"
)

print(result["output"]["performance_analysis"]["analysis"])
```

### Exemple 2: Optimiser un bundle

```python
from bundle_optimizer import BundleOptimizerAgent

agent = BundleOptimizerAgent(config)

result = agent.analyze_dependencies(
    package_json="""
    {
      "dependencies": {
        "react": "^18.2.0",
        "lodash": "^4.17.21",
        "moment": "^2.29.4"
      }
    }
    """
)

print(result["output"]["bundle_optimization"]["recommendations"])
```

### Exemple 3: Optimiser une requête SQL

```python
from database_optimizer import DatabaseOptimizerAgent

agent = DatabaseOptimizerAgent(config)

result = agent.optimize_query(
    query="""
    SELECT * FROM users
    WHERE created_at > '2024-01-01'
    ORDER BY created_at DESC
    """,
    database="postgresql",
    execution_time=850  # 850ms
)

print(result["output"]["database_optimization"]["recommendations"])
```

## 5. Exemples complets

```bash
# Exécuter tous les exemples
python example_usage.py
```

Cela va:
1. Analyser des Core Web Vitals
2. Optimiser du code splitting
3. Optimiser une requête SQL
4. Faire un audit complet de performance

## Aide-mémoire

### Importer les agents

```python
from performance_squad import (
    PerformanceEngineerAgent,
    BundleOptimizerAgent,
    DatabaseOptimizerAgent
)
```

### Créer une configuration

```python
from base_agent import AgentConfig
import os

config = AgentConfig(
    name="mon-agent",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    model="anthropic/claude-3.5-sonnet",
    temperature=0.3,
    max_tokens=4096
)
```

### Utiliser un agent

```python
agent = PerformanceEngineerAgent(config)

# Méthode 1: Helper method (recommandé)
result = agent.analyze_core_web_vitals(url, metrics, context)

# Méthode 2: run() avec input_data complet
result = agent.run({
    "task_type": "core_web_vitals",
    "url": url,
    "metrics": metrics,
    "context": context
})

# Résultat
if result["status"] == "success":
    print(result["output"])
else:
    print(result["error"])
```

## Types de tâches

### Performance Engineer

- `core_web_vitals` - Analyse LCP, FID, CLS, TTFB
- `js_profiling` - Profile JavaScript, détecte bottlenecks
- `react_optimization` - Optimise rendering React
- `lighthouse_audit` - Analyse rapport Lighthouse
- `performance_budget` - Définit budgets de performance
- `bottleneck_analysis` - Identifie bottlenecks

### Bundle Optimizer

- `code_splitting` - Stratégie code splitting
- `tree_shaking` - Configuration tree shaking
- `asset_optimization` - Optimise images/fonts/SVG
- `dependency_analysis` - Analyse dépendances npm
- `compression_config` - Config Brotli/Gzip
- `bundle_analysis` - Analyse bundle complet

### Database Optimizer

- `query_optimization` - Optimise requête SQL/NoSQL
- `index_creation` - Stratégie indexing
- `connection_pooling` - Config connection pool
- `caching_strategy` - Stratégie Redis/Memcached
- `schema_optimization` - Optimise schema
- `query_plan_analysis` - Analyse EXPLAIN plan

## Métriques retournées

```python
result = agent.run(input_data)

# Status
result["status"]  # "success" ou "failed"

# Output
result["output"]  # Résultat formaté

# Métriques
result["metrics"]
# {
#     "total_tokens": 3847,
#     "prompt_tokens": 1234,
#     "completion_tokens": 2613,
#     "execution_time": 8.45,
#     "retry_count": 0,
#     "error_count": 0
# }

# Timestamp
result["timestamp"]  # "2024-01-01T12:00:00.000000"
```

## Troubleshooting

### Erreur: "OPENROUTER_API_KEY not found"

```bash
# Vérifier le .env
cat .env

# Vérifier la variable
echo $OPENROUTER_API_KEY

# Charger manuellement
export OPENROUTER_API_KEY=sk-or-v1-xxxxx
```

### Erreur: "ModuleNotFoundError"

```bash
# Vérifier l'installation
pip list | grep requests

# Installer si manquant
pip install requests python-dotenv
```

### Erreur: "Invalid task_type"

```python
# Vérifier les types valides dans la doc
agent.validate_input({
    "task_type": "invalid",  # Erreur
    "context": "..."
})
```

Voir SUMMARY.md pour la liste complète des task_types.

## Ressources

- **README.md** - Documentation complète
- **SUMMARY.md** - Récapitulatif et stats
- **example_usage.py** - Exemples concrets
- **test_agents.py** - Tests unitaires

## Support

Pour toute question:
1. Consulter README.md
2. Vérifier les exemples dans example_usage.py
3. Activer les logs DEBUG:

```python
config = AgentConfig(
    name="debug",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    log_level="DEBUG"  # Active logs détaillés
)
```

---

**Prêt à optimiser vos performances!** 🚀
