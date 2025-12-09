"""
Accessibility Expert Agent - Accessibility Squad

Cet agent est responsable de:
- Auditer la conformité WCAG 2.1 (AA et AAA)
- Vérifier les attributs ARIA et leur usage correct
- Tester la navigation clavier et les raccourcis
- Optimiser l'expérience pour les lecteurs d'écran
- Assurer la conformité aux standards d'accessibilité
"""

import sys
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

# Ajouter le chemin pour importer BaseAgent
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../core'))

from base_agent import BaseAgent


class AccessibilityExpertAgent(BaseAgent):
    """
    Agent expert en accessibilité web (WCAG 2.1, ARIA, navigation clavier).

    Spécialisé dans l'audit et l'amélioration de l'accessibilité des applications web,
    garantissant une expérience inclusive pour tous les utilisateurs.

    Attributes:
        name (str): Nom de l'agent - "AccessibilityExpert"
        api_key (str): Clé API pour le LLM
        model (str): Modèle LLM à utiliser
    """

    def __init__(self, api_key: str, model: str = "openai/gpt-4o"):
        """
        Initialise l'agent AccessibilityExpert.

        Args:
            api_key (str): Clé API OpenRouter
            model (str): Modèle LLM (défaut: gpt-4o)
        """
        super().__init__(name="AccessibilityExpert", api_key=api_key, model=model)

    def _get_default_system_prompt(self) -> str:
        """
        Retourne le prompt système par défaut pour l'agent AccessibilityExpert.

        Returns:
            str: Prompt système définissant le rôle et les capacités
        """
        return """Tu es un expert en accessibilité web avec certification IAAP (International Association of Accessibility Professionals).

**Tes expertises:**
- WCAG 2.1 Level AA et AAA (compréhension approfondie des 78 critères)
- ARIA 1.2 (rôles, propriétés, états, patterns)
- Section 508 et ADA compliance
- Tests avec lecteurs d'écran (NVDA, JAWS, VoiceOver, TalkBack)
- Navigation clavier et focus management
- Contraste des couleurs et perception visuelle
- Accessibilité mobile (iOS, Android)
- Tests automatisés (axe-core, Pa11y, Lighthouse)

**Tes responsabilités:**
1. **Audit WCAG 2.1:**
   - Évaluer chaque critère (A, AA, AAA)
   - Identifier les violations et leur sévérité
   - Fournir des recommandations actionnables
   - Prioriser les corrections (bloquantes → mineures)

2. **Vérification ARIA:**
   - Valider l'usage correct des rôles ARIA
   - Vérifier les propriétés (aria-label, aria-describedby, etc.)
   - Tester les états dynamiques (aria-expanded, aria-hidden)
   - Détecter les anti-patterns ARIA

3. **Navigation clavier:**
   - Tester l'accessibilité complète au clavier
   - Vérifier l'ordre de tabulation logique
   - Valider les indicateurs de focus visibles
   - Implémenter les raccourcis clavier standards
   - Gérer les focus traps et skip links

4. **Lecteurs d'écran:**
   - Optimiser les annonces vocales
   - Structurer le contenu sémantiquement
   - Tester avec NVDA, JAWS, VoiceOver
   - Valider les live regions (aria-live)

5. **Standards visuels:**
   - Vérifier les ratios de contraste (4.5:1 pour AA, 7:1 pour AAA)
   - Tester l'agrandissement de texte (200%)
   - Valider la lisibilité et la hiérarchie visuelle
   - Assurer l'indépendance de la couleur

**Principes directeurs:**
- **Inclusivité:** Accessible à tous, handicaps permanents, temporaires, ou situationnels
- **Standards-first:** Se conformer strictement aux WCAG 2.1
- **Sémantique HTML:** Utiliser HTML natif avant ARIA
- **Testabilité:** Proposer des tests automatisés + manuels
- **Documentation:** Expliquer clairement chaque problème et sa solution

**Format de sortie:**
- Rapports structurés en markdown
- Niveau de sévérité: CRITIQUE | ÉLEVÉ | MOYEN | FAIBLE
- Code examples avec avant/après
- Références aux critères WCAG spécifiques
- Priorisation des corrections avec effort estimé"""

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exécute une tâche d'accessibilité selon le type demandé.

        Args:
            context (Dict[str, Any]): Contexte de la tâche avec:
                - task_type: "wcag_audit" | "aria_review" | "keyboard_nav" | "screen_reader" | "contrast_check"
                - code: Code HTML/JSX/TSX à analyser (optionnel)
                - url: URL à auditer (optionnel)
                - level: Niveau WCAG visé ("A" | "AA" | "AAA", défaut: "AA")
                - context: Contexte additionnel

        Returns:
            Dict[str, Any]: Résultat avec:
                - status: "success" | "error"
                - result: Rapport d'audit ou recommandations
                - metadata: Métadonnées (sévérité, nombre d'issues, etc.)
        """
        task_type = context.get("task_type", "wcag_audit")
        code = context.get("code", "")
        url = context.get("url", "")
        level = context.get("level", "AA")
        additional_context = context.get("context", "")

        # Construire le prompt selon le type de tâche
        if task_type == "wcag_audit":
            user_prompt = self._build_wcag_audit_prompt(code, url, level, additional_context)
        elif task_type == "aria_review":
            user_prompt = self._build_aria_review_prompt(code, additional_context)
        elif task_type == "keyboard_nav":
            user_prompt = self._build_keyboard_nav_prompt(code, additional_context)
        elif task_type == "screen_reader":
            user_prompt = self._build_screen_reader_prompt(code, additional_context)
        elif task_type == "contrast_check":
            user_prompt = self._build_contrast_check_prompt(code, additional_context)
        else:
            return {
                "status": "error",
                "result": f"Type de tâche inconnu: {task_type}",
                "metadata": {"error": "invalid_task_type"}
            }

        try:
            # Appeler le LLM
            messages = [{"role": "user", "content": user_prompt}]
            response = await self.call_llm(messages=messages, temperature=0.3)

            # Ajouter à la mémoire
            self.add_to_memory("user", user_prompt)

            return {
                "status": "success",
                "result": response,
                "metadata": {
                    "task_type": task_type,
                    "wcag_level": level,
                    "timestamp": datetime.utcnow().isoformat(),
                    "agent": self.name
                }
            }

        except Exception as e:
            return {
                "status": "error",
                "result": f"Erreur lors de l'exécution: {str(e)}",
                "metadata": {"error": str(e)}
            }

    def _build_wcag_audit_prompt(
        self,
        code: str,
        url: str,
        level: str,
        additional_context: str
    ) -> str:
        """Construit le prompt pour un audit WCAG complet."""
        target = f"URL: {url}" if url else f"Code:\n```html\n{code}\n```"

        return f"""Effectue un audit d'accessibilité WCAG 2.1 Level {level} complet.

**CIBLE À AUDITER:**
{target}

**CONTEXTE ADDITIONNEL:**
{additional_context if additional_context else "Aucun contexte spécifique"}

**INSTRUCTIONS:**
Analyse selon les 4 principes WCAG (POUR):

1. **Perceptible** - L'information doit être présentée de manière perceptible
   - Alternatives textuelles (1.1)
   - Média temporel (1.2)
   - Adaptable (1.3)
   - Distinguable (1.4)

2. **Utilisable** - Les composants doivent être utilisables
   - Accessible au clavier (2.1)
   - Délai suffisant (2.2)
   - Crises et réactions physiques (2.3)
   - Navigable (2.4)
   - Modalités d'entrée (2.5)

3. **Compréhensible** - L'information doit être compréhensible
   - Lisible (3.1)
   - Prévisible (3.2)
   - Assistance à la saisie (3.3)

4. **Robuste** - Le contenu doit être robuste
   - Compatible (4.1)

**FORMAT DU RAPPORT:**

## Résumé Exécutif
- Score global: X/100
- Violations critiques: X
- Violations totales: X
- Niveau de conformité actuel: [A | AA | AAA | Non conforme]

## Violations par Sévérité

### 🔴 CRITIQUES (Bloquantes)
| Critère | Description | Élément | Impact | Solution |
|---------|-------------|---------|--------|----------|
| 1.1.1 | ... | ... | ... | ... |

### 🟠 ÉLEVÉES
[Même format]

### 🟡 MOYENNES
[Même format]

### 🔵 FAIBLES
[Même format]

## Exemples de Code

### Avant (Problématique)
```html
[Code avec problème]
```

### Après (Corrigé)
```html
[Code accessible]
```

## Plan de Remédiation Priorisé
1. [Tâche 1] - Effort: X jours - Impact: CRITIQUE
2. [Tâche 2] - Effort: X jours - Impact: ÉLEVÉ
...

## Tests Recommandés
- [ ] Tests automatisés (axe-core, Pa11y)
- [ ] Tests lecteurs d'écran (NVDA, JAWS, VoiceOver)
- [ ] Tests navigation clavier
- [ ] Tests utilisateurs en situation de handicap

Sois exhaustif et précis dans ton analyse."""

    def _build_aria_review_prompt(self, code: str, additional_context: str) -> str:
        """Construit le prompt pour une revue ARIA."""
        return f"""Effectue une revue approfondie de l'usage ARIA dans le code suivant.

**CODE À ANALYSER:**
```html
{code}
```

**CONTEXTE:**
{additional_context if additional_context else "Aucun contexte spécifique"}

**POINTS À VÉRIFIER:**

1. **Rôles ARIA:**
   - Les rôles sont-ils appropriés?
   - HTML natif pourrait-il remplacer ARIA? (règle #1 de ARIA)
   - Les rôles sont-ils utilisés correctement?

2. **Propriétés ARIA:**
   - aria-label, aria-labelledby, aria-describedby sont-ils corrects?
   - Les relations sont-elles valides?
   - Manque-t-il des labels obligatoires?

3. **États ARIA:**
   - aria-expanded, aria-selected, aria-checked sont-ils gérés?
   - Les états dynamiques sont-ils mis à jour via JavaScript?
   - aria-hidden est-il utilisé correctement (attention aux pièges)?

4. **Live Regions:**
   - aria-live, aria-atomic, aria-relevant sont-ils nécessaires?
   - Les annonces sont-elles pertinentes et non intrusives?

5. **Anti-patterns ARIA:**
   - Utilisation redondante avec HTML natif
   - Conflits entre rôles ARIA et éléments HTML
   - Mauvaise hiérarchie de landmarks

**FORMAT DE SORTIE:**

## Analyse ARIA

### ✅ Bonnes Pratiques Détectées
- [Liste des usages corrects]

### ❌ Problèmes Identifiés

#### Problème 1: [Titre]
- **Sévérité:** [CRITIQUE | ÉLEVÉ | MOYEN | FAIBLE]
- **Ligne:** [Numéro de ligne]
- **Code problématique:**
```html
[Code]
```
- **Problème:** [Explication détaillée]
- **Impact:** [Impact sur les utilisateurs]
- **Solution:**
```html
[Code corrigé]
```
- **Référence:** [Lien spec ARIA]

### 💡 Recommandations
- [Suggestions d'amélioration]

### 🧪 Tests à Effectuer
- [ ] Test avec NVDA
- [ ] Test avec VoiceOver
- [ ] Validation W3C ARIA
- [ ] Test avec axe DevTools

Fournis une analyse technique précise."""

    def _build_keyboard_nav_prompt(self, code: str, additional_context: str) -> str:
        """Construit le prompt pour tester la navigation clavier."""
        return f"""Analyse la navigation clavier et le focus management du code suivant.

**CODE À ANALYSER:**
```html
{code}
```

**CONTEXTE:**
{additional_context if additional_context else "Aucun contexte spécifique"}

**CRITÈRES D'ÉVALUATION:**

1. **Accessibilité clavier (WCAG 2.1.1):**
   - Toutes les fonctionnalités sont-elles accessibles au clavier?
   - Pas de piège au clavier (keyboard trap)?
   - Les raccourcis sont-ils standards?

2. **Ordre de tabulation (WCAG 2.4.3):**
   - L'ordre est-il logique et intuitif?
   - tabindex est-il utilisé correctement? (éviter > 0)
   - Les éléments interactifs sont-ils tous tabulables?

3. **Visibilité du focus (WCAG 2.4.7):**
   - L'indicateur de focus est-il toujours visible?
   - Le contraste est-il suffisant (3:1)?
   - outline:none est-il évité sans alternative?

4. **Skip links:**
   - Y a-t-il un "Skip to main content"?
   - Est-il fonctionnel et visible au focus?

5. **Focus management:**
   - Le focus est-il géré dans les modals/dialogs?
   - Le focus est-il restauré après fermeture?
   - autofocus est-il utilisé judicieusement?

6. **Raccourcis clavier:**
   - Les raccourcis suivent-ils les conventions (Esc, Enter, Space, Arrows)?
   - Y a-t-il des conflits avec les raccourcis navigateur?
   - Les raccourcis sont-ils documentés?

**FORMAT DE SORTIE:**

## Audit Navigation Clavier

### 📊 Score Global
- Accessibilité clavier: X/10
- Ordre de tabulation: X/10
- Visibilité du focus: X/10
- Focus management: X/10

### ✅ Points Forts
- [Liste]

### ❌ Problèmes Détectés

#### [Titre du problème]
- **Critère WCAG:** 2.1.X / 2.4.X
- **Sévérité:** [CRITIQUE | ÉLEVÉ | MOYEN | FAIBLE]
- **Description:** [Explication]
- **Test à effectuer:**
  1. [Étape 1]
  2. [Étape 2]
- **Comportement attendu:** [Ce qui devrait se passer]
- **Comportement actuel:** [Ce qui se passe]
- **Solution:**
```javascript
// Code de correction
```

### 🎯 Checklist de Tests Manuels
- [ ] Navigation Tab/Shift+Tab complète
- [ ] Tous les boutons activables avec Enter/Space
- [ ] Navigation dans les menus avec flèches
- [ ] Fermeture des modals avec Escape
- [ ] Focus visible sur tous les éléments
- [ ] Aucun piège au clavier
- [ ] Skip link fonctionnel

### 💡 Améliorations Suggérées
- [Suggestions pour UX clavier optimale]

Sois très précis sur les tests à effectuer."""

    def _build_screen_reader_prompt(self, code: str, additional_context: str) -> str:
        """Construit le prompt pour optimiser l'expérience lecteur d'écran."""
        return f"""Analyse l'expérience utilisateur pour les lecteurs d'écran.

**CODE À ANALYSER:**
```html
{code}
```

**CONTEXTE:**
{additional_context if additional_context else "Aucun contexte spécifique"}

**POINTS D'ANALYSE:**

1. **Structure sémantique:**
   - HTML sémantique (header, nav, main, aside, footer)
   - Hiérarchie des headings (h1 > h2 > h3...)
   - Landmarks ARIA si nécessaires

2. **Labels et descriptions:**
   - Tous les contrôles ont-ils des labels?
   - aria-label vs aria-labelledby: usage approprié?
   - aria-describedby pour infos complémentaires?

3. **Contenu masqué:**
   - Texte visible uniquement pour lecteurs d'écran (.sr-only)
   - aria-hidden utilisé correctement?
   - Contenu décoratif marqué comme tel?

4. **Navigation:**
   - Les landmarks sont-ils correctement définis?
   - Navigation par headings possible?
   - Listes utilisées pour les items répétés?

5. **Annonces dynamiques:**
   - aria-live pour les changements de contenu
   - aria-atomic et aria-relevant appropriés
   - Messages de status/erreur annoncés

6. **Formulaires:**
   - Labels associés aux champs (for + id)
   - Instructions claires
   - Erreurs annoncées et associées
   - Groupes de champs (fieldset/legend)

**FORMAT DE SORTIE:**

## Analyse Lecteur d'Écran

### 🎧 Expérience Simulée
**Ce qu'entendrait un utilisateur de NVDA:**
```
[Narration simulée ligne par ligne]
"Région principale"
"Titre niveau 1: Page d'accueil"
"Bouton: Se connecter"
...
```

### ❌ Problèmes d'Accessibilité

#### [Problème]
- **Impact:** [Ce que l'utilisateur ne peut pas faire]
- **Cause:** [Raison technique]
- **Code problématique:**
```html
[Code]
```
- **Solution:**
```html
[Code corrigé avec explications]
```
- **Test:** [Comment vérifier avec NVDA/JAWS/VoiceOver]

### ✅ Bonnes Pratiques Détectées
- [Liste]

### 🎯 Optimisations Recommandées

1. **Structure:**
   - [Suggestions]

2. **Labels:**
   - [Suggestions]

3. **Navigation:**
   - [Suggestions]

4. **Annonces:**
   - [Suggestions]

### 🧪 Plan de Test

#### Test NVDA (Windows)
1. [Étapes]

#### Test JAWS (Windows)
1. [Étapes]

#### Test VoiceOver (macOS/iOS)
1. [Étapes]

#### Test TalkBack (Android)
1. [Étapes]

### 📚 Ressources
- [Liens vers documentation pertinente]

Simule précisément l'expérience utilisateur."""

    def _build_contrast_check_prompt(self, code: str, additional_context: str) -> str:
        """Construit le prompt pour vérifier les contrastes de couleurs."""
        return f"""Analyse les contrastes de couleurs et la lisibilité visuelle.

**CODE À ANALYSER:**
```html
{code}
```

**CONTEXTE:**
{additional_context if additional_context else "Aucun contexte spécifique"}

**CRITÈRES WCAG:**

1. **Contraste du texte (1.4.3 - Level AA):**
   - Texte normal: ratio minimum 4.5:1
   - Texte large (18pt+ ou 14pt bold+): ratio minimum 3:1

2. **Contraste amélioré (1.4.6 - Level AAA):**
   - Texte normal: ratio minimum 7:1
   - Texte large: ratio minimum 4.5:1

3. **Contraste non-textuel (1.4.11):**
   - Composants UI: ratio minimum 3:1
   - États de focus: ratio minimum 3:1

4. **Redimensionnement du texte (1.4.4):**
   - Support du zoom 200% sans perte de contenu

5. **Indépendance de la couleur (1.4.1):**
   - L'information ne repose pas uniquement sur la couleur

**FORMAT DE SORTIE:**

## Audit Contraste & Lisibilité

### 📊 Résumé
- Paires de couleurs analysées: X
- Conformes AA: X
- Conformes AAA: X
- Non conformes: X

### ❌ Problèmes de Contraste

#### [Élément]
- **Couleur texte:** #XXXXXX
- **Couleur fond:** #XXXXXX
- **Ratio actuel:** X.XX:1
- **Ratio requis AA:** 4.5:1 (texte) / 3:1 (large)
- **Ratio requis AAA:** 7:1 (texte) / 4.5:1 (large)
- **Statut:** ❌ Non conforme AA | ⚠️ Conforme AA mais pas AAA | ✅ Conforme AAA
- **Impact:** [Utilisateurs affectés]
- **Suggestions de couleurs conformes:**
  - Option 1: Texte #XXXXXX / Fond #XXXXXX (ratio: X.XX:1)
  - Option 2: Texte #XXXXXX / Fond #XXXXXX (ratio: X.XX:1)

### ✅ Contrastes Conformes
- [Liste]

### 🎨 Recommandations Design

1. **Palette de couleurs:**
   - Couleur primaire: [Suggestion]
   - Couleur secondaire: [Suggestion]
   - Couleur texte: [Suggestion]
   - États (hover, focus, disabled): [Suggestions]

2. **Typographie:**
   - Taille minimum: 16px (14px pour large)
   - Line-height: 1.5 minimum
   - Letter-spacing: ajusté si nécessaire
   - Font-weight: considérer pour améliorer lisibilité

3. **Indépendance couleur:**
   - Ajouter des icônes aux états colorés (succès ✓, erreur ✗)
   - Utiliser des patterns/textures en complément
   - Souligner les liens (pas juste la couleur)

### 🧪 Outils de Test Recommandés
- WebAIM Contrast Checker
- Chrome DevTools (Lighthouse, Color Picker)
- Colour Contrast Analyser (CCA)
- axe DevTools
- WAVE browser extension

### 📋 Checklist
- [ ] Tous les textes ont ratio ≥ 4.5:1
- [ ] Titres/textes larges ont ratio ≥ 3:1
- [ ] Boutons/composants UI ont ratio ≥ 3:1
- [ ] Focus indicators ont ratio ≥ 3:1
- [ ] Information ne repose pas sur couleur seule
- [ ] Texte zoomable à 200% sans casse

Fournis des suggestions de couleurs précises avec hex codes."""

    async def audit_wcag(
        self,
        code: str = "",
        url: str = "",
        level: str = "AA"
    ) -> str:
        """
        Méthode helper pour effectuer un audit WCAG complet.

        Args:
            code (str): Code HTML/JSX/TSX à auditer
            url (str): URL à auditer (alternatif au code)
            level (str): Niveau WCAG ("A", "AA", "AAA")

        Returns:
            str: Rapport d'audit détaillé en markdown
        """
        result = await self.execute({
            "task_type": "wcag_audit",
            "code": code,
            "url": url,
            "level": level
        })
        return result["result"]

    async def review_aria(self, code: str, context: str = "") -> str:
        """
        Méthode helper pour effectuer une revue ARIA.

        Args:
            code (str): Code HTML/JSX/TSX à analyser
            context (str): Contexte additionnel

        Returns:
            str: Rapport de revue ARIA
        """
        result = await self.execute({
            "task_type": "aria_review",
            "code": code,
            "context": context
        })
        return result["result"]

    async def test_keyboard_navigation(self, code: str, context: str = "") -> str:
        """
        Méthode helper pour tester la navigation clavier.

        Args:
            code (str): Code à analyser
            context (str): Contexte additionnel

        Returns:
            str: Rapport de navigation clavier
        """
        result = await self.execute({
            "task_type": "keyboard_nav",
            "code": code,
            "context": context
        })
        return result["result"]

    async def optimize_screen_reader(self, code: str, context: str = "") -> str:
        """
        Méthode helper pour optimiser l'expérience lecteur d'écran.

        Args:
            code (str): Code à optimiser
            context (str): Contexte additionnel

        Returns:
            str: Recommandations pour lecteurs d'écran
        """
        result = await self.execute({
            "task_type": "screen_reader",
            "code": code,
            "context": context
        })
        return result["result"]

    async def check_contrast(self, code: str, context: str = "") -> str:
        """
        Méthode helper pour vérifier les contrastes de couleurs.

        Args:
            code (str): Code CSS/HTML à analyser
            context (str): Contexte additionnel

        Returns:
            str: Rapport de contraste des couleurs
        """
        result = await self.execute({
            "task_type": "contrast_check",
            "code": code,
            "context": context
        })
        return result["result"]
