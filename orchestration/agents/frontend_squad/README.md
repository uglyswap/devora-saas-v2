# Frontend Squad - Devora Orchestration System

Le **Frontend Squad** est un ensemble d'agents spécialisés dans le développement et le design frontend pour le système d'orchestration Devora.

## 🤖 Agents

### 1. UI/UX Designer Agent (`ui_ux_designer.py`)

Agent spécialisé en design d'interface utilisateur et expérience utilisateur.

**Capacités:**
- Génération de wireframes et mockups (descriptions conceptuelles)
- Définition de systèmes de design (couleurs, typographie, espacement)
- Création de user flows et journey maps
- Analyse d'accessibilité (conformité WCAG A/AA/AAA)
- Design de layouts responsifs
- Spécifications de composants

**Tâches supportées:**
- `wireframe` - Créer des wireframes détaillés
- `design_system` - Créer un système de design complet
- `user_flow` - Concevoir des parcours utilisateurs
- `component_spec` - Spécifier des composants UI
- `accessibility_audit` - Auditer l'accessibilité

**Exemple d'utilisation:**
```python
from orchestration.agents.frontend_squad import UIUXDesignerAgent

designer = UIUXDesignerAgent(api_key="your-openrouter-key")

# Créer un système de design
result = await designer.create_design_system(
    brand={
        "name": "Devora",
        "primary_color": "#3B82F6",
        "font": "Inter"
    },
    accessibility_level="WCAG AA"
)

# Générer des wireframes
result = await designer.generate_wireframe(
    feature="Dashboard",
    requirements="Stats cards, activity timeline, navigation"
)

# Créer un user flow
result = await designer.design_user_flow(
    feature="User Registration",
    entry_point="Landing page",
    goal="Complete account creation"
)
```

### 2. Frontend Developer Agent (`frontend_developer.py`)

Agent spécialisé en développement frontend avec React, Next.js et TypeScript.

**Capacités:**
- Génération de composants React/Next.js avec TypeScript
- Implémentation de state management (Context, Zustand, React Query)
- Création de custom hooks
- Optimisation des performances (memoization, code splitting)
- Layouts responsifs
- Gestion de données asynchrones
- Error boundaries et gestion d'erreurs

**Tâches supportées:**
- `create_component` - Créer un composant React
- `create_hook` - Créer un custom hook
- `create_page` - Créer une page Next.js
- `optimize_performance` - Optimiser les performances
- `add_state_management` - Implémenter la gestion d'état

**Exemple d'utilisation:**
```python
from orchestration.agents.frontend_squad import FrontendDeveloperAgent

developer = FrontendDeveloperAgent(api_key="your-openrouter-key")

# Créer un composant
result = await developer.create_component(
    name="UserProfileCard",
    component_type="ui",
    requirements="Display user info with avatar, stats, and actions",
    design_specs={"max_width": "400px"}
)

# Créer un custom hook
result = await developer.create_custom_hook(
    name="useLocalStorage",
    purpose="Sync state with localStorage",
    parameters={"key": "string", "initialValue": "T"}
)

# Créer une page Next.js
result = await developer.create_page(
    name="DashboardPage",
    route="/dashboard",
    requirements="Display user stats and activity",
    api_endpoints=["/api/stats", "/api/activity"]
)
```

### 3. Component Architect Agent (`component_architect.py`)

Agent spécialisé en architecture de composants et bibliothèques de composants.

**Capacités:**
- Design d'architecture de bibliothèque de composants
- Structuration d'intégration shadcn/ui
- Définition d'APIs de composants (props, interfaces)
- Création de définitions TypeScript
- Génération de documentation Storybook
- Établissement de conventions de nommage
- Design de compound components

**Tâches supportées:**
- `design_component_library` - Concevoir une bibliothèque de composants
- `create_component_spec` - Créer des spécifications de composants
- `design_compound_component` - Concevoir des compound components
- `create_storybook_docs` - Créer la documentation Storybook
- `define_component_api` - Définir l'API d'un composant

**Exemple d'utilisation:**
```python
from orchestration.agents.frontend_squad import ComponentArchitectAgent

architect = ComponentArchitectAgent(api_key="your-openrouter-key")

# Concevoir une bibliothèque de composants
result = await architect.design_component_library(
    components=["Button", "Input", "Card", "Modal"],
    design_system={"colors": {...}, "spacing": [...]},
    framework="shadcn/ui"
)

# Créer une spécification de composant
result = await architect.create_component_spec(
    component_name="Button",
    category="atom",
    variants=["size", "variant", "color"]
)

# Concevoir un compound component
result = await architect.design_compound_component(
    component_name="Form",
    sub_components=["FormField", "FormLabel", "FormInput"]
)

# Créer la documentation Storybook
result = await architect.create_storybook_docs(
    component_name="Button",
    variants={
        "variant": ["primary", "secondary", "outline"],
        "size": ["sm", "md", "lg"]
    }
)
```

## 🔄 Workflows Prédéfinis

Le Frontend Squad propose plusieurs workflows qui orchestrent les agents pour accomplir des tâches complexes:

### 1. Design to Code Workflow

Processus complet du design à l'implémentation.

```python
from orchestration.agents.frontend_squad import create_frontend_squad, execute_workflow

squad = create_frontend_squad(api_key="your-key")

results = await execute_workflow(
    workflow_name="design_to_code",
    agents=squad,
    context={
        "feature": "User Dashboard",
        "requirements": "Display user stats and activity"
    }
)
```

**Étapes:**
1. UI/UX Designer: Créer le système de design et les wireframes
2. Component Architect: Concevoir l'architecture des composants et les APIs
3. Frontend Developer: Implémenter les composants avec TypeScript

### 2. Component Creation Workflow

Créer un nouveau composant de A à Z.

```python
results = await execute_workflow(
    workflow_name="component_creation",
    agents=squad,
    context={
        "component_name": "SearchBar",
        "requirements": "Auto-complete, search history, keyboard nav"
    }
)
```

**Étapes:**
1. UI/UX Designer: Concevoir l'UI et les interactions du composant
2. Component Architect: Définir l'API du composant et les variants
3. Frontend Developer: Implémenter le code du composant
4. Component Architect: Créer la documentation Storybook

### 3. Design System Creation Workflow

Créer un système de design complet.

```python
results = await execute_workflow(
    workflow_name="design_system_creation",
    agents=squad,
    context={
        "brand": {"primary_color": "#3B82F6", "font": "Inter"}
    }
)
```

**Étapes:**
1. UI/UX Designer: Définir les design tokens et le langage visuel
2. Component Architect: Structurer la bibliothèque de composants
3. Frontend Developer: Implémenter les composants de base

## 🛠️ Utilisation Rapide

### Installation et Configuration

```bash
# Installer les dépendances
pip install httpx python-dotenv

# Configurer la clé API
echo "OPENROUTER_API_KEY=your-key-here" >> .env
```

### Créer l'Ensemble du Squad

```python
from orchestration.agents.frontend_squad import create_frontend_squad

# Créer tous les agents en une fois
squad = create_frontend_squad(api_key="your-key")

# Accéder aux agents individuels
designer = squad["ui_ux_designer"]
developer = squad["frontend_developer"]
architect = squad["component_architect"]

# Utiliser les agents
result = await designer.execute({
    "task": "design_system",
    "feature": "app",
    "brand": {"primary_color": "#3B82F6"}
})
```

### Obtenir les Informations du Squad

```python
from orchestration.agents.frontend_squad import get_squad_info

info = get_squad_info()
print(f"Squad: {info['name']}")
print(f"Agents: {list(info['agents'].keys())}")
print(f"Workflows: {list(info['workflows'].keys())}")
```

## 📚 Structure des Données

### Format de Contexte (Input)

```python
context = {
    # Général
    "task": str,              # Type de tâche
    "feature": str,           # Nom de la feature
    "requirements": str,      # Requirements détaillés

    # Design
    "brand": dict,            # Guidelines de marque
    "design_system": dict,    # Système de design
    "target_audience": str,   # Audience cible
    "accessibility_level": str, # WCAG A/AA/AAA

    # Development
    "component_name": str,    # Nom du composant
    "component_type": str,    # Type de composant
    "api_endpoints": list,    # Endpoints API
    "state_management": str,  # Approche de state management

    # Architecture
    "components": list,       # Liste de composants
    "framework": str,         # Framework (shadcn/ui, etc.)
    "patterns": dict,         # Patterns désirés
}
```

### Format de Résultat (Output)

```python
result = {
    "status": "success" | "error",
    "result": {
        # Varie selon le type de tâche
        # Peut contenir: code, design_specs, architecture, etc.
    },
    "task_type": str,
    "recommendations": list,  # Optional
    "error": str,            # Si status == "error"
}
```

## 🎯 Exemples Complets

Voir le fichier `example_usage.py` pour des exemples détaillés de chaque agent et workflow.

### Exécuter les Exemples

```bash
# Configurer la clé API
export OPENROUTER_API_KEY="your-key"

# Exécuter les exemples
python orchestration/agents/frontend_squad/example_usage.py
```

## 🧪 Tests

```python
# Test rapide d'un agent
import asyncio
from orchestration.agents.frontend_squad import UIUXDesignerAgent

async def test():
    designer = UIUXDesignerAgent(api_key="your-key")
    result = await designer.execute({
        "task": "wireframe",
        "feature": "Login Page",
        "requirements": "Email, password, remember me, forgot password"
    })
    print(result)

asyncio.run(test())
```

## 🔧 Configuration Avancée

### Modifier le Modèle LLM

```python
# Utiliser un modèle différent
designer = UIUXDesignerAgent(
    api_key="your-key",
    model="anthropic/claude-3.5-sonnet"  # Au lieu de gpt-4o
)
```

### Personnaliser le System Prompt

```python
# Créer un agent avec un prompt personnalisé
designer = UIUXDesignerAgent(api_key="your-key")
designer._system_prompt = """
Your custom system prompt here...
"""
```

## 📝 Conventions

### Nommage des Composants
- **PascalCase** pour les noms de composants: `UserProfileCard`, `SearchBar`
- **camelCase** pour les hooks: `useLocalStorage`, `useFetchData`
- **kebab-case** pour les fichiers: `user-profile-card.tsx`, `use-local-storage.ts`

### Structure de Fichiers
```
src/
  components/
    ui/              # shadcn/ui components
    compound/        # Compound components
    layouts/         # Layout components
  hooks/            # Custom hooks
  lib/              # Utilities
  types/            # TypeScript types
```

## 🚀 Bonnes Pratiques

1. **Toujours typer avec TypeScript** - Pas de `any`
2. **Suivre les conventions shadcn/ui** - Pour la cohérence
3. **Prioriser l'accessibilité** - WCAG AA minimum
4. **Optimiser les performances** - Memoization, code splitting
5. **Documenter les composants** - JSDoc et Storybook
6. **Tester les edge cases** - Loading, error, empty states
7. **Design responsive-first** - Mobile, tablet, desktop
8. **Supporter le dark mode** - Via design tokens

## 🐛 Debugging

### Activer les Logs

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

### Inspecter les Résultats

```python
result = await agent.execute(context)

# Vérifier le statut
if result["status"] == "error":
    print(f"Error: {result['error']}")
else:
    # Inspecter le résultat
    import json
    print(json.dumps(result, indent=2))
```

## 📖 Ressources

- [shadcn/ui Documentation](https://ui.shadcn.com)
- [Next.js 14 Documentation](https://nextjs.org/docs)
- [React TypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Storybook Documentation](https://storybook.js.org/docs)

## 🤝 Contribution

Pour ajouter de nouvelles fonctionnalités au Frontend Squad:

1. Créer une nouvelle méthode dans l'agent approprié
2. Ajouter le prompt correspondant
3. Mettre à jour la documentation
4. Ajouter un exemple dans `example_usage.py`
5. Tester avec différents contextes

## 📄 License

Partie du projet Devora - Voir LICENSE à la racine du projet.
