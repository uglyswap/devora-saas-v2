# Frontend Squad Architecture

## Vue d'ensemble

Le **Frontend Squad** est un ensemble de 3 agents spécialisés qui collaborent pour créer des interfaces utilisateur modernes, accessibles et performantes.

```
Frontend Squad
├── UI/UX Designer       → Design système, wireframes, accessibilité
├── Frontend Developer   → Code React/Next.js/TypeScript
└── Component Architect  → Architecture de composants, documentation
```

## Architecture des Agents

### Hiérarchie des Classes

```
BaseAgent (core/base_agent.py)
    ├── UIUXDesignerAgent
    ├── FrontendDeveloperAgent
    └── ComponentArchitectAgent
```

### BaseAgent (Classe Parente)

**Responsabilités:**
- Communication avec l'API LLM (OpenRouter)
- Gestion de la mémoire conversationnelle
- Méthodes abstraites pour l'exécution de tâches
- Validation des sorties

**Méthodes clés:**
```python
async def execute(context: Dict) -> Dict        # À implémenter par les sous-classes
async def call_llm(messages: List) -> str       # Appel API LLM
def add_to_memory(role: str, content: str)      # Gestion mémoire
def format_context(context: Dict) -> str        # Formatage contexte
```

## Agents Spécialisés

### 1. UI/UX Designer Agent

**Fichier:** `ui_ux_designer.py` (523 lignes)

**Expertise:**
- Design systems (tokens, couleurs, typographie)
- Wireframes et mockups
- User flows et parcours utilisateurs
- Accessibilité WCAG (A, AA, AAA)
- Design responsive

**Tâches supportées:**
```python
"wireframe"              # Créer des wireframes
"design_system"          # Créer système de design
"user_flow"              # Concevoir parcours utilisateurs
"component_spec"         # Spécifier composants
"accessibility_audit"    # Auditer accessibilité
```

**Méthodes de convenance:**
```python
async def generate_wireframe(feature, requirements)
async def create_design_system(brand, accessibility_level)
async def design_user_flow(feature, entry_point, goal)
```

**System Prompt:**
- Expert en principes de design (contraste, hiérarchie)
- Connaissance approfondie de shadcn/ui, Tailwind CSS
- Focus sur accessibilité (WCAG 2.1)
- Design responsive et mobile-first

### 2. Frontend Developer Agent

**Fichier:** `frontend_developer.py` (616 lignes)

**Expertise:**
- React 18+ (hooks, Server Components)
- Next.js 14+ (App Router, Server Actions)
- TypeScript strict mode
- State management (Context, Zustand, React Query)
- Performance optimization

**Tâches supportées:**
```python
"create_component"       # Créer composant React
"create_hook"            # Créer custom hook
"create_page"            # Créer page Next.js
"optimize_performance"   # Optimiser performances
"add_state_management"   # Ajouter gestion d'état
```

**Méthodes de convenance:**
```python
async def create_component(name, type, requirements, design_specs)
async def create_custom_hook(name, purpose, parameters)
async def create_page(name, route, requirements, api_endpoints)
```

**Capacités:**
- Extraction automatique de dépendances
- Parsing de blocs de code (TypeScript/TSX)
- Génération de code avec types stricts
- Gestion d'erreurs et loading states

**System Prompt:**
- Expert React/Next.js/TypeScript
- Patterns modernes (Server Components, Streaming)
- Optimisation performances (memoization, code splitting)
- Accessibilité et responsive design

### 3. Component Architect Agent

**Fichier:** `component_architect.py` (727 lignes)

**Expertise:**
- Architecture de bibliothèques de composants
- Atomic Design (atoms, molecules, organisms)
- Design patterns (compound components, polymorphic)
- shadcn/ui integration
- Documentation Storybook

**Tâches supportées:**
```python
"design_component_library"   # Concevoir bibliothèque
"create_component_spec"      # Créer spécifications
"design_compound_component"  # Concevoir compound component
"create_storybook_docs"      # Créer docs Storybook
"define_component_api"       # Définir API composant
```

**Méthodes de convenance:**
```python
async def design_component_library(components, design_system, framework)
async def create_component_spec(component_name, category, variants)
async def design_compound_component(component_name, sub_components)
async def create_storybook_docs(component_name, variants)
```

**Capacités:**
- Extraction de sections Markdown
- Parsing de blocs JSON/TypeScript
- Génération d'interfaces TypeScript complexes
- Architecture de bibliothèques scalables

**System Prompt:**
- Expert Atomic Design et patterns de composants
- Connaissance approfondie shadcn/ui et Radix UI
- TypeScript avancé (generics, utility types)
- Documentation et Storybook

## Workflows Prédéfinis

### 1. Design to Code
```
[Designer: Design system]
    ↓
[Architect: Component architecture]
    ↓
[Developer: Implementation]
```

### 2. Component Creation
```
[Designer: UI/interactions]
    ↓
[Architect: API/variants]
    ↓
[Developer: Code]
    ↓
[Architect: Storybook docs]
```

### 3. Design System Creation
```
[Designer: Design tokens]
    ↓
[Architect: Component library structure]
    ↓
[Developer: Base components]
```

## Formats de Données

### Format de Contexte (Input)

```typescript
interface Context {
  // Général
  task: string;
  feature?: string;
  requirements?: string;

  // Design
  brand?: {
    name?: string;
    primary_color?: string;
    secondary_color?: string;
    font?: string;
  };
  design_system?: object;
  target_audience?: string;
  accessibility_level?: 'WCAG A' | 'WCAG AA' | 'WCAG AAA';

  // Development
  component_name?: string;
  component_type?: 'page' | 'layout' | 'ui' | 'compound';
  api_endpoints?: string[];
  state_management?: 'local' | 'context' | 'zustand' | 'react-query';

  // Architecture
  components?: string[];
  framework?: 'shadcn/ui' | 'custom';
  patterns?: object;
}
```

### Format de Résultat (Output)

```typescript
interface Result {
  status: 'success' | 'error';
  result: {
    // Designer
    wireframes?: object[];
    design_system?: object;
    user_flows?: object[];
    accessibility_notes?: string[];

    // Developer
    code?: string;
    file_path?: string;
    dependencies?: string[];
    additional_files?: object[];

    // Architect
    architecture?: object;
    specifications?: object[];
    code_blocks?: object[];
    sections?: Record<string, string>;
  };
  task_type: string;
  component_name?: string;
  feature?: string;
  recommendations?: string[];
  error?: string;
}
```

## Stack Technique

### Frontend Technologies
- **React 18+** - Library UI avec concurrent features
- **Next.js 14+** - Framework avec App Router
- **TypeScript** - Typage strict, pas de 'any'
- **Tailwind CSS** - Utility-first CSS
- **shadcn/ui** - Bibliothèque de composants (Radix UI)

### State Management
- **React Context** - State local/global simple
- **Zustand** - State management léger
- **React Query / TanStack Query** - Server state
- **React Hook Form + Zod** - Gestion de formulaires

### Developer Tools
- **Storybook** - Documentation composants
- **ESLint** - Linting
- **TypeScript Compiler** - Type checking

### LLM Integration
- **OpenRouter API** - Accès multi-modèles
- **Default Model:** `openai/gpt-4o`
- **Temperature:** 0.3-0.7 (selon la tâche)

## Métriques

### Taille du Code
```
Total: 3,350 lignes

ui_ux_designer.py      : 523 lignes (15.6%)
frontend_developer.py  : 616 lignes (18.4%)
component_architect.py : 727 lignes (21.7%)
__init__.py           : 236 lignes (7.0%)
example_usage.py      : 342 lignes (10.2%)
test_frontend_squad.py: 380 lignes (11.3%)
README.md             : 526 lignes (15.7%)
```

### Complexité
- **Prompts système:** ~500-700 lignes par agent
- **Méthodes publiques:** 5-8 par agent
- **Méthodes privées:** 8-12 par agent
- **Tests unitaires:** 30+ tests

## Patterns de Design

### 1. Template Method Pattern
```python
class BaseAgent:
    async def execute(context):  # Template
        # Défini par les sous-classes
        pass
```

### 2. Strategy Pattern
```python
def _build_task_prompt(context):
    task = context["task"]
    if task == "wireframe":
        return self._get_wireframe_prompt()
    elif task == "design_system":
        return self._get_design_system_prompt()
    # ... autres stratégies
```

### 3. Builder Pattern
```python
def _build_task_prompt(context):
    base = self._get_base_context(context)
    task_specific = self._get_task_prompt(context["task"])
    return base + task_specific
```

### 4. Factory Pattern
```python
def create_frontend_squad(api_key, model):
    return {
        "ui_ux_designer": UIUXDesignerAgent(api_key, model),
        "frontend_developer": FrontendDeveloperAgent(api_key, model),
        "component_architect": ComponentArchitectAgent(api_key, model),
    }
```

## Extensibilité

### Ajouter une Nouvelle Tâche

1. **Ajouter le type de tâche:**
```python
# Dans _build_task_prompt()
elif task_type == "nouvelle_tache":
    return base_context + self._get_nouvelle_tache_prompt()
```

2. **Créer le prompt:**
```python
def _get_nouvelle_tache_prompt(self) -> str:
    return """
    ## Task: Nouvelle Tâche
    ...
    """
```

3. **Ajouter méthode de convenance (optionnel):**
```python
async def execute_nouvelle_tache(self, param1, param2):
    return await self.execute({
        "task": "nouvelle_tache",
        "param1": param1,
        "param2": param2
    })
```

### Ajouter un Nouvel Agent

1. **Créer la classe:**
```python
from ..core.base_agent import BaseAgent

class NouvelAgent(BaseAgent):
    def __init__(self, api_key, model="openai/gpt-4o"):
        super().__init__(name="nouvel_agent", api_key=api_key, model=model)

    def _get_default_system_prompt(self):
        return "..."

    async def execute(self, context):
        # Implémentation
        pass
```

2. **Ajouter à `__init__.py`:**
```python
from .nouvel_agent import NouvelAgent

__all__ = [..., "NouvelAgent"]
```

3. **Mettre à jour `create_frontend_squad()`:**
```python
def create_frontend_squad(api_key, model):
    return {
        ...,
        "nouvel_agent": NouvelAgent(api_key, model)
    }
```

### Ajouter un Workflow

```python
SQUAD_INFO = {
    "workflows": {
        "nouveau_workflow": {
            "description": "Description du workflow",
            "steps": [
                {"agent": "ui_ux_designer", "task": "Tâche 1"},
                {"agent": "frontend_developer", "task": "Tâche 2"}
            ]
        }
    }
}
```

## Bonnes Pratiques

### Code Quality
- ✅ TypeScript strict (pas de 'any')
- ✅ Docstrings sur toutes les méthodes publiques
- ✅ Type hints Python
- ✅ Error handling systématique
- ✅ Logging des opérations importantes

### Testing
- ✅ Tests unitaires pour chaque agent
- ✅ Mocking des appels LLM
- ✅ Tests d'intégration des workflows
- ✅ Tests avec vraie API (optionnels)

### Documentation
- ✅ README détaillé
- ✅ Examples d'utilisation
- ✅ Architecture documentée
- ✅ Formats de données définis

### Performance
- ✅ Appels LLM async
- ✅ Temperature adaptée (0.3 pour code, 0.7 pour design)
- ✅ Timeout configurables
- ✅ Gestion de la mémoire conversationnelle

## Dépendances

```python
# Core
httpx         # Async HTTP client
asyncio       # Async/await support
logging       # Logging
json          # JSON parsing
re            # Regex

# Testing
pytest        # Testing framework
pytest-asyncio # Async test support
unittest.mock # Mocking
```

## Sécurité

### API Keys
- ✅ Jamais hardcodées dans le code
- ✅ Variables d'environnement (.env)
- ✅ Non incluses dans les logs

### Validation
- ✅ Validation des inputs
- ✅ Validation des outputs
- ✅ Error handling pour les API failures
- ✅ Timeout sur les requêtes HTTP

### Code Safety
- ✅ Pas d'eval() ou exec()
- ✅ Sanitization des inputs utilisateur
- ✅ Pas d'exécution de code généré

## Roadmap

### Phase 1 (Actuel) ✅
- [x] Structure de base des 3 agents
- [x] Workflows prédéfinis
- [x] Documentation complète
- [x] Tests unitaires

### Phase 2 (Futur)
- [ ] Intégration avec Figma API
- [ ] Génération d'images de wireframes
- [ ] Support Playwright pour screenshots
- [ ] Cache des résultats LLM
- [ ] Metrics et analytics

### Phase 3 (Futur)
- [ ] Fine-tuning de modèles spécialisés
- [ ] Multi-agent collaboration avancée
- [ ] Auto-amélioration via feedback
- [ ] Integration continue (CI/CD)

## Support et Contribution

### Obtenir de l'aide
- Consulter le README.md
- Examiner example_usage.py
- Lancer les tests pour voir des exemples

### Contribuer
1. Suivre les conventions de code existantes
2. Ajouter des tests pour les nouvelles fonctionnalités
3. Documenter les changements
4. Respecter les types Python et TypeScript

## License

Partie du projet Devora - Voir LICENSE à la racine.
