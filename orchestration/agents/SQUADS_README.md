# Documentation des Squads - Devora Orchestration System

## Vue d'ensemble

Le système d'orchestration Devora est organisé en **squads spécialisées**, chacune contenant des agents experts dans leur domaine.

---

## Accessibility Squad

Squad dédiée à l'accessibilité web et l'internationalisation.

### Agents

#### 1. AccessibilityExpert
**Fichier:** `accessibility_squad/accessibility_expert.py`

**Responsabilités:**
- Auditer la conformité WCAG 2.1 (Levels A, AA, AAA)
- Vérifier les attributs ARIA et leur usage correct
- Tester la navigation clavier et les raccourcis
- Optimiser l'expérience pour les lecteurs d'écran (NVDA, JAWS, VoiceOver)
- Vérifier les contrastes de couleurs selon WCAG

**Capacités principales:**
- `audit_wcag()` - Audit WCAG complet avec rapport détaillé
- `review_aria()` - Revue des attributs ARIA
- `test_keyboard_navigation()` - Tests de navigation clavier
- `optimize_screen_reader()` - Optimisation pour lecteurs d'écran
- `check_contrast()` - Vérification des contrastes de couleurs

**Cas d'usage:**
```python
from accessibility_squad import AccessibilityExpertAgent

agent = AccessibilityExpertAgent(api_key="your_api_key")

# Audit WCAG complet
result = await agent.audit_wcag(
    code=html_code,
    level="AA"
)

# Revue ARIA
aria_review = await agent.review_aria(
    code=component_code,
    context="React modal component"
)

# Test navigation clavier
keyboard_test = await agent.test_keyboard_navigation(
    code=app_code
)
```

**Standards supportés:**
- WCAG 2.1 (A, AA, AAA)
- ARIA 1.2
- Section 508
- ADA Compliance

---

#### 2. I18nSpecialist
**Fichier:** `accessibility_squad/i18n_specialist.py`

**Responsabilités:**
- Configurer les systèmes d'internationalisation (i18next, react-intl, FormatJS)
- Gérer les fichiers de traduction et les clés i18n
- Supporter les langues RTL (Right-to-Left): Arabe, Hébreu, Persan, Urdu
- Formater les dates, nombres, devises selon les locales
- Implémenter le language switching et la détection de langue

**Capacités principales:**
- `setup_i18n()` - Configuration i18n complète
- `manage_translations()` - Gestion des fichiers de traduction
- `implement_rtl()` - Support RTL (Right-to-Left)
- `setup_formatting()` - Formatage culturel (dates, nombres, devises)
- `implement_language_switcher()` - Système de changement de langue

**Cas d'usage:**
```python
from accessibility_squad import I18nSpecialistAgent

agent = I18nSpecialistAgent(api_key="your_api_key")

# Setup i18n pour Next.js avec 3 langues
result = await agent.setup_i18n(
    framework="next",
    languages=["en", "fr", "ar"],
    context="E-commerce application"
)

# Implémenter RTL pour l'arabe
rtl_config = await agent.implement_rtl(
    code=current_css,
    framework="react"
)

# Gérer les traductions
translations = await agent.manage_translations(
    code=app_code,
    languages=["en", "fr", "es", "ar"]
)
```

**Frameworks supportés:**
- React (react-intl, i18next)
- Next.js (next-intl, next-i18next)
- Vue (vue-i18n)
- Svelte (svelte-i18n)
- Vanilla JS (i18next)

**Langues avec expertise:**
- **LTR:** Anglais, Français, Espagnol, Allemand, Portugais, Italien, Russe, Chinois, Japonais, Coréen
- **RTL:** Arabe, Hébreu, Persan, Urdu
- **Scripts complexes:** Hindi, Thaï, Vietnamien

---

## AI/ML Squad

Squad dédiée à l'intégration d'intelligence artificielle et au machine learning operations.

### Agents

#### 3. AIEngineer
**Fichier:** `ai_ml_squad/ai_engineer.py`

**Responsabilités:**
- Intégrer les LLMs (Claude, GPT, Gemini, Llama)
- Implémenter l'AI SDK (Vercel AI SDK, LangChain, LlamaIndex)
- Créer des pipelines RAG (Retrieval-Augmented Generation)
- Optimiser les prompts et le prompt engineering
- Gérer les embeddings et vector databases

**Capacités principales:**
- `integrate_llm()` - Intégration complète d'un LLM provider
- `create_rag_pipeline()` - Pipeline RAG end-to-end
- `optimize_prompt()` - Optimisation de prompts
- `implement_ai_sdk()` - Implémentation Vercel AI SDK
- `setup_vector_db()` - Configuration vector database

**Cas d'usage:**
```python
from ai_ml_squad import AIEngineer

agent = AIEngineer()

# Intégrer OpenAI dans Next.js
integration = await agent.execute({
    "task_type": "llm_integration",
    "framework": "next",
    "llm_provider": "openai",
    "requirements": "Chat interface with streaming"
})

# Créer pipeline RAG
rag = await agent.execute({
    "task_type": "rag_pipeline",
    "framework": "next",
    "llm_provider": "anthropic",
    "requirements": "Technical documentation search"
})

# Optimiser un prompt
optimized = await agent.execute({
    "task_type": "prompt_optimization",
    "code": current_prompt,
    "requirements": "Reduce cost by 30% while maintaining quality"
})
```

**LLM Providers supportés:**
- OpenAI (GPT-4, GPT-4o, GPT-4o-mini)
- Anthropic (Claude 3.5 Sonnet, Claude Opus 4.5)
- Google (Gemini 2.0 Flash, Gemini Pro)
- Meta (Llama 3)
- Mistral AI
- OpenRouter (multi-provider)

**AI SDKs supportés:**
- Vercel AI SDK
- LangChain
- LlamaIndex
- Semantic Kernel
- LangGraph

**Vector Databases:**
- Supabase pgvector
- Pinecone
- Weaviate
- Qdrant
- Chroma

---

#### 4. MLOpsEngineer
**Fichier:** `ai_ml_squad/ml_ops_engineer.py`

**Responsabilités:**
- Déployer les modèles en production
- Configurer le monitoring ML (latence, coûts, tokens)
- Gérer le caching des inférences (semantic caching)
- Optimiser les coûts API (model selection, token optimization)
- Implémenter rate limiting et retries

**Capacités principales:**
- Monitoring des requêtes LLM
- Caching sémantique
- Tracking des coûts par modèle
- Sélection optimale du modèle selon complexité
- Rate limiting et circuit breakers

**Cas d'usage:**
```python
from ai_ml_squad import MLOpsEngineer

agent = MLOpsEngineer()

# Setup monitoring complet
monitoring = await agent.execute({
    "task": "Setup LLM monitoring",
    "models": ["gpt-4o", "claude-3.5-sonnet"]
})

# Implémenter caching
caching = await agent.execute({
    "task": "Implement semantic caching",
    "models": ["gpt-4o"]
})
```

**Features:**
- **Monitoring:**
  - Latence par requête
  - Token usage (prompt + completion)
  - Coût par requête
  - Taux de succès/erreur
  - Tracking par modèle

- **Caching:**
  - Semantic caching (hash de prompts)
  - TTL configurable
  - Statistiques de cache (hit rate)
  - Invalidation par pattern

- **Cost Optimization:**
  - Calcul du coût par requête
  - Sélection du modèle optimal selon complexité
  - Budget checks
  - Alertes de dépassement

---

## Architecture des Agents

### Pattern BaseAgent

Tous les agents héritent de `BaseAgent` qui fournit:

```python
class BaseAgent(ABC):
    def __init__(self, name: str, api_key: str, model: str):
        self.name = name
        self.api_key = api_key
        self.model = model
        self.memory = []  # Conversation history

    @abstractmethod
    def _get_default_system_prompt(self) -> str:
        """Prompt système définissant le rôle de l'agent."""
        pass

    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Méthode principale d'exécution."""
        pass

    async def call_llm(self, messages: List[Dict], **kwargs) -> str:
        """Appel au LLM via OpenRouter."""
        pass
```

### Utilisation

#### 1. Initialisation
```python
agent = AccessibilityExpertAgent(
    api_key=os.environ["OPENROUTER_API_KEY"],
    model="openai/gpt-4o"  # Optionnel, défaut: gpt-4o
)
```

#### 2. Exécution
```python
result = await agent.execute({
    "task_type": "wcag_audit",
    "code": html_code,
    "level": "AA"
})

print(result["status"])  # "success" ou "error"
print(result["result"])  # Rapport généré
```

#### 3. Méthodes helper
```python
# Au lieu de execute() avec config, utiliser les helpers:
audit = await agent.audit_wcag(code=html, level="AA")
aria_review = await agent.review_aria(code=component)
```

---

## Best Practices

### 1. Accessibility Expert

**Pour un audit complet:**
```python
# 1. Audit WCAG global
wcag_audit = await agent.audit_wcag(code=app_code, level="AA")

# 2. Revue ARIA spécifique
aria_review = await agent.review_aria(code=component_code)

# 3. Tests clavier
keyboard_tests = await agent.test_keyboard_navigation(code=app_code)

# 4. Optimisation lecteur d'écran
sr_optimization = await agent.optimize_screen_reader(code=component_code)

# 5. Vérification contrastes
contrast_check = await agent.check_contrast(code=css_code)
```

**Priorisation des corrections:**
1. CRITIQUES (bloquantes): Navigation clavier cassée, contrastes < 3:1
2. ÉLEVÉES: ARIA incorrect, labels manquants
3. MOYENNES: Ordre de tabulation sous-optimal
4. FAIBLES: Améliorations UX

### 2. I18n Specialist

**Setup progressif:**
```python
# 1. Configuration initiale (2 langues)
setup = await agent.setup_i18n(
    framework="next",
    languages=["en", "fr"]
)

# 2. Ajouter RTL quand nécessaire
if "ar" in future_languages:
    rtl_config = await agent.implement_rtl(framework="next")

# 3. Formatage culturel
formatting = await agent.setup_formatting(
    framework="next",
    languages=["en", "fr", "ar"]
)
```

**Organisation des traductions:**
```
locales/
  en/
    common.json      # Textes communs (header, footer)
    navigation.json  # Menus, liens
    forms.json       # Labels, placeholders
    errors.json      # Messages d'erreur
    pages/
      home.json
      about.json
```

### 3. AI Engineer

**Pipeline RAG optimal:**
```python
# 1. Setup vector database
vector_db = await agent.execute({
    "task_type": "vector_db",
    "framework": "next",
    "requirements": "Supabase pgvector for documentation"
})

# 2. Create RAG pipeline
rag = await agent.execute({
    "task_type": "rag_pipeline",
    "framework": "next",
    "llm_provider": "anthropic",
    "requirements": "Documentation search with Claude 3.5"
})

# 3. Optimize prompts
optimized_prompts = await agent.execute({
    "task_type": "prompt_optimization",
    "code": current_rag_prompt
})
```

**Choix du modèle:**
- **Simple tasks:** GPT-4o-mini, Gemini Flash (rapide, pas cher)
- **Medium tasks:** GPT-4o, Claude 3.5 Sonnet (équilibré)
- **Complex tasks:** Claude Opus 4.5 (meilleure qualité)

### 4. ML Ops Engineer

**Monitoring complet:**
```python
# Tracker chaque requête LLM
from ml_ops_engineer import llmMonitor

await llmMonitor.trackRequest({
    "requestId": "req_123",
    "model": "gpt-4o",
    "provider": "openai",
    "promptTokens": 150,
    "completionTokens": 300,
    "totalTokens": 450,
    "latencyMs": 1200,
    "cost": 0.0045,
    "success": True,
    "timestamp": datetime.now()
})

# Obtenir les stats
stats = await llmMonitor.getUsageStats(period="week")
costs = await llmMonitor.getCostByModel(start_date, end_date)
```

**Caching stratégique:**
```python
from ml_ops_engineer import LLMCache

cache = LLMCache(config={
    "ttlSeconds": 3600,  # 1 heure
    "semanticThreshold": 0.95
})

# Wrapper automatique
cached_response = await cache.get(prompt, model)
if not cached_response:
    response = await call_llm(prompt, model)
    await cache.set(prompt, model, response)
```

---

## Exemples d'Intégration

### Workflow complet: Application accessible multilingue avec AI

```python
# 1. Setup i18n
i18n_agent = I18nSpecialistAgent(api_key=api_key)
i18n_setup = await i18n_agent.setup_i18n(
    framework="next",
    languages=["en", "fr", "ar", "es"]
)

# 2. Implémenter RTL
rtl_config = await i18n_agent.implement_rtl(
    code=app_css,
    framework="next"
)

# 3. Intégrer AI
ai_agent = AIEngineer()
ai_integration = await ai_agent.integrate_llm(
    framework="next",
    llm_provider="anthropic",
    requirements="Multilingual chat with translation"
)

# 4. Setup monitoring
mlops_agent = MLOpsEngineer()
monitoring = await mlops_agent.execute({
    "task": "Setup monitoring",
    "models": ["claude-3.5-sonnet"]
})

# 5. Audit accessibilité
a11y_agent = AccessibilityExpertAgent(api_key=api_key)
audit = await a11y_agent.audit_wcag(
    code=final_app_code,
    level="AA"
)
```

---

## Variables d'Environnement

```env
# OpenRouter API (pour les agents)
OPENROUTER_API_KEY=your_openrouter_key

# Pour AI/ML Squad
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Vector Database (Supabase)
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_key

# Caching (Upstash Redis)
UPSTASH_REDIS_URL=your_redis_url
UPSTASH_REDIS_TOKEN=your_redis_token

# Frontend URL (pour OpenRouter referer)
FRONTEND_URL=http://localhost:3000
```

---

## Maintenance et Évolution

### Ajouter un nouvel agent

1. Créer le fichier dans la squad appropriée:
```python
# accessibility_squad/new_agent.py
from ..core.base_agent import BaseAgent

class NewAgent(BaseAgent):
    def _get_default_system_prompt(self) -> str:
        return "System prompt..."

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Implementation
        pass
```

2. Ajouter au `__init__.py`:
```python
from .new_agent import NewAgent

__all__ = [
    "AccessibilityExpertAgent",
    "I18nSpecialistAgent",
    "NewAgent"  # Ajout
]
```

### Tester un agent

```python
# Test basique
agent = AccessibilityExpertAgent(api_key=test_api_key)
result = await agent.execute({
    "task_type": "wcag_audit",
    "code": "<button>Click me</button>",  # Simple test
    "level": "AA"
})

assert result["status"] == "success"
assert "WCAG" in result["result"]
```

---

## Support et Documentation

- **Code source:** `C:/Users/quent/devora-transformation/orchestration/agents/`
- **Documentation API:** Voir docstrings dans chaque fichier
- **Examples:** Voir sections "Cas d'usage" ci-dessus

---

## Roadmap

### Court terme
- [ ] Tests unitaires pour chaque agent
- [ ] Documentation OpenAPI pour l'API REST
- [ ] Dashboard de monitoring ML

### Moyen terme
- [ ] Agent de sécurité (Security Engineer)
- [ ] Agent de performance (Performance Engineer)
- [ ] Intégration continue des audits

### Long terme
- [ ] Multi-agent orchestration automatique
- [ ] Self-healing capabilities
- [ ] Apprentissage continu des agents

---

**Dernière mise à jour:** 2025-12-09
**Version:** 1.0.0
**Auteur:** Devora Orchestration Team
