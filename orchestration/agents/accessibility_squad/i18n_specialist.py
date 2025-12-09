"""
Internationalization (i18n) Specialist Agent - Accessibility Squad

Cet agent est responsable de:
- Configurer les systèmes d'internationalisation (i18next, react-intl, etc.)
- Gérer les fichiers de traduction et les clés i18n
- Supporter les langues RTL (Right-to-Left) comme l'arabe et l'hébreu
- Formater les dates, nombres, devises selon les locales
- Implémenter le language switching et la détection de langue
"""

import sys
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

# Ajouter le chemin pour importer BaseAgent
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../core'))

from base_agent import BaseAgent


class I18nSpecialistAgent(BaseAgent):
    """
    Agent spécialisé en internationalisation (i18n) et localisation (l10n).

    Expert dans la configuration de systèmes multilingues, la gestion des traductions,
    le support RTL, et le formatage culturel des données.

    Attributes:
        name (str): Nom de l'agent - "I18nSpecialist"
        api_key (str): Clé API pour le LLM
        model (str): Modèle LLM à utiliser
    """

    def __init__(self, api_key: str, model: str = "openai/gpt-4o"):
        """
        Initialise l'agent I18nSpecialist.

        Args:
            api_key (str): Clé API OpenRouter
            model (str): Modèle LLM (défaut: gpt-4o)
        """
        super().__init__(name="I18nSpecialist", api_key=api_key, model=model)

    def _get_default_system_prompt(self) -> str:
        """
        Retourne le prompt système par défaut pour l'agent I18nSpecialist.

        Returns:
            str: Prompt système définissant le rôle et les capacités
        """
        return """Tu es un expert en internationalisation (i18n) et localisation (l10n) avec 10+ ans d'expérience dans les applications multilingues globales.

**Tes expertises:**
- Librairies i18n: i18next, react-intl, vue-i18n, next-intl, FormatJS
- Standards: ICU MessageFormat, CLDR, BCP 47, ISO 639/3166
- RTL (Right-to-Left): Arabe, Hébreu, Persan, Urdu
- Formatage: Dates (Intl.DateTimeFormat), Nombres (Intl.NumberFormat), Devises, Pluriels
- Outils: Crowdin, Lokalise, Phrase, POEditor
- SEO multilingue: hreflang, sitemap localisé, URL structure

**Tes responsabilités:**

1. **Configuration i18n:**
   - Setup de i18next/react-intl selon le framework
   - Structure des fichiers de traduction (JSON, YAML, PO)
   - Namespace organization pour grandes apps
   - Lazy loading des traductions
   - Fallback language strategy

2. **Gestion des traductions:**
   - Extraction des clés i18n du code
   - Naming conventions pour les clés (namespaced, nested)
   - Détection des traductions manquantes
   - Validation du format des fichiers
   - Gestion des variables et interpolations
   - Pluralization rules (ICU MessageFormat)

3. **Support RTL:**
   - Configuration CSS pour RTL (direction: rtl, logical properties)
   - Mirroring des layouts (flex, grid)
   - Gestion des icons et images directionnelles
   - Adaptation des animations et transitions
   - Testing RTL/LTR switching

4. **Formatage culturel:**
   - Dates et heures (12h/24h, formats locaux)
   - Nombres (séparateurs décimaux, grouping)
   - Devises (symboles, position, arrondis)
   - Adresses (ordre des champs selon pays)
   - Noms (prénom/nom selon culture)
   - Téléphones (formats internationaux)

5. **Language switching:**
   - Détection automatique de langue (navigator.language, Accept-Language)
   - Sélecteur de langue UI
   - Persistance du choix (localStorage, cookies)
   - Changement dynamique sans reload
   - URL-based locale (/en/, /fr/, /ar/)

6. **SEO & Performance:**
   - hreflang tags pour Google
   - Sitemap multilingue
   - URL structure SEO-friendly
   - Code splitting par langue
   - Lazy loading des traductions
   - Bundle size optimization

**Principes directeurs:**
- **Scalabilité:** Architecture supportant 50+ langues
- **Maintenabilité:** Structure claire et documentée
- **Performance:** Lazy loading, code splitting
- **UX:** Changement de langue seamless
- **Qualité:** Validation et testing automatisés
- **Inclusivité:** Support global (LTR, RTL, scripts complexes)

**Langues supportées (expertise):**
- **LTR:** Anglais, Français, Espagnol, Allemand, Portugais, Italien, Russe, Chinois, Japonais, Coréen
- **RTL:** Arabe, Hébreu, Persan, Urdu
- **Complexes:** Hindi (Devanagari), Thaï, Vietnamien

**Format de sortie:**
- Code prêt à l'emploi (TypeScript/JavaScript)
- Configuration files complètes
- Structure de dossiers claire
- Scripts d'extraction et validation
- Documentation développeur et traducteur
- Examples d'usage pour chaque feature"""

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exécute une tâche i18n selon le type demandé.

        Args:
            context (Dict[str, Any]): Contexte de la tâche avec:
                - task_type: "setup" | "translations" | "rtl" | "formatting" | "language_switch"
                - framework: "react" | "next" | "vue" | "svelte" | "vanilla"
                - languages: Liste des langues cibles (ex: ["en", "fr", "ar"])
                - code: Code existant à analyser (optionnel)
                - context: Contexte additionnel

        Returns:
            Dict[str, Any]: Résultat avec:
                - status: "success" | "error"
                - result: Configuration, code, ou recommandations
                - metadata: Métadonnées (langues, framework, etc.)
        """
        task_type = context.get("task_type", "setup")
        framework = context.get("framework", "react")
        languages = context.get("languages", ["en", "fr"])
        code = context.get("code", "")
        additional_context = context.get("context", "")

        # Construire le prompt selon le type de tâche
        if task_type == "setup":
            user_prompt = self._build_setup_prompt(framework, languages, additional_context)
        elif task_type == "translations":
            user_prompt = self._build_translations_prompt(code, languages, additional_context)
        elif task_type == "rtl":
            user_prompt = self._build_rtl_prompt(code, framework, additional_context)
        elif task_type == "formatting":
            user_prompt = self._build_formatting_prompt(framework, languages, additional_context)
        elif task_type == "language_switch":
            user_prompt = self._build_language_switch_prompt(framework, languages, additional_context)
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
                    "framework": framework,
                    "languages": languages,
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

    def _build_setup_prompt(
        self,
        framework: str,
        languages: List[str],
        additional_context: str
    ) -> str:
        """Construit le prompt pour setup i18n complet."""
        has_rtl = any(lang in ["ar", "he", "fa", "ur"] for lang in languages)

        return f"""Configure un système d'internationalisation complet pour un projet {framework}.

**LANGUES CIBLES:**
{", ".join(languages)}
{f"⚠️ Inclut des langues RTL: {', '.join([l for l in languages if l in ['ar', 'he', 'fa', 'ur']])}" if has_rtl else ""}

**CONTEXTE:**
{additional_context if additional_context else "Nouveau projet"}

**LIVRABLES ATTENDUS:**

1. **Installation & Configuration**
```bash
# Commandes npm/yarn à exécuter
```

2. **Structure de fichiers**
```
project/
├── locales/
│   ├── en/
│   │   ├── common.json
│   │   ├── navigation.json
│   │   └── errors.json
│   ├── fr/
│   │   └── ...
│   └── ar/  # Si RTL
│       └── ...
├── i18n/
│   ├── config.ts
│   ├── types.ts
│   └── utils.ts
```

3. **Configuration i18next/react-intl**
```typescript
// i18n/config.ts
// Configuration complète avec:
// - Langues supportées
// - Fallback language
// - Namespaces
// - Interpolation
// - Pluralization
// - Lazy loading
```

4. **Types TypeScript**
```typescript
// i18n/types.ts
// Types pour autocomplétion des clés de traduction
```

5. **Provider Setup**
```typescript
// App setup avec i18n provider
// Framework-specific ({framework})
```

6. **Helper Functions**
```typescript
// i18n/utils.ts
// - getLocale()
// - setLocale()
// - formatDate()
// - formatNumber()
// - formatCurrency()
```

7. **Fichiers de traduction initiaux**
```json
// locales/en/common.json
{{
  "app": {{
    "title": "My App",
    "description": "Welcome to my app"
  }},
  "navigation": {{
    "home": "Home",
    "about": "About"
  }}
}}
```

8. **Scripts package.json**
```json
{{
  "scripts": {{
    "i18n:extract": "...",
    "i18n:validate": "...",
    "i18n:missing": "..."
  }}
}}
```

9. **Usage Examples**
```typescript
// Example de composant traduisible
// Avec hooks/HOC selon framework
```

10. **Documentation**
- Guide développeur (ajouter nouvelles traductions)
- Guide traducteur (format des fichiers)
- Conventions de nommage des clés

{f'''
11. **Configuration RTL**
```css
/* styles/rtl.css */
/* Configuration CSS pour RTL */
```

```typescript
// RTL detection et setup
```
''' if has_rtl else ''}

**BEST PRACTICES À APPLIQUER:**
- ✅ Lazy loading des traductions
- ✅ Code splitting par langue
- ✅ Namespace organization (éviter un seul gros fichier)
- ✅ TypeScript pour type-safety des clés
- ✅ Fallback language strategy
- ✅ Persistance du choix utilisateur
- ✅ SEO-friendly (hreflang, URLs localisées)

Fournis une solution production-ready et complète."""

    def _build_translations_prompt(
        self,
        code: str,
        languages: List[str],
        additional_context: str
    ) -> str:
        """Construit le prompt pour gérer les traductions."""
        return f"""Analyse le code et génère/optimise les fichiers de traduction.

**CODE À ANALYSER:**
```typescript
{code if code else "Aucun code fourni - génère un template"}
```

**LANGUES CIBLES:**
{", ".join(languages)}

**CONTEXTE:**
{additional_context if additional_context else "Aucun contexte spécifique"}

**TÂCHES:**

1. **Extraction des strings**
   - Identifier tous les textes hardcodés
   - Suggérer des clés i18n appropriées
   - Grouper par namespace logique

2. **Génération des fichiers de traduction**
   Pour chaque langue ({", ".join(languages)}), créer:
   ```json
   // locales/[lang]/[namespace].json
   ```

3. **Conventions de nommage**
   - Format: `namespace.section.key`
   - Examples:
     - `common.buttons.submit`
     - `errors.validation.required`
     - `navigation.menu.home`

4. **Gestion des variables**
   ```json
   {{
     "welcome": "Welcome, {{{{name}}}}!",
     "itemsCount": "You have {{{{count}}}} item",
     "itemsCount_plural": "You have {{{{count}}}} items"
   }}
   ```

5. **Pluralization**
   Utiliser ICU MessageFormat pour les pluriels:
   ```json
   {{
     "items": "{{count, plural, =0 {{no items}} =1 {{one item}} other {{# items}}}}"
   }}
   ```

6. **Détection des traductions manquantes**
   Script pour comparer les fichiers de langue:
   ```typescript
   // scripts/check-missing-translations.ts
   ```

7. **Validation**
   Script pour valider:
   - JSON valide
   - Même structure dans toutes les langues
   - Variables cohérentes
   - Pas de clés orphelines

8. **Code refactoré**
   Si code fourni, montre le code refactoré avec i18n:
   ```typescript
   // Avant
   <h1>Welcome</h1>

   // Après
   <h1>{{t('common.welcome')}}</h1>
   ```

**STRUCTURE ATTENDUE:**
```
locales/
├── en/
│   ├── common.json        # Textes communs
│   ├── navigation.json    # Menus, liens
│   ├── forms.json         # Labels, placeholders
│   ├── errors.json        # Messages d'erreur
│   └── pages/
│       ├── home.json
│       └── about.json
├── fr/
│   └── ... (même structure)
└── ar/  (si applicable)
    └── ... (même structure)
```

**QUALITÉ:**
- ✅ Pas de strings hardcodés
- ✅ Clés descriptives et cohérentes
- ✅ Namespaces logiques
- ✅ Variables et pluriels gérés
- ✅ Fichiers synchronisés entre langues

Fournis une solution complète et maintenable."""

    def _build_rtl_prompt(
        self,
        code: str,
        framework: str,
        additional_context: str
    ) -> str:
        """Construit le prompt pour implémenter le support RTL."""
        return f"""Implémente le support complet RTL (Right-to-Left) pour une application {framework}.

**CODE ACTUEL:**
```
{code if code else "Nouvelle implémentation"}
```

**CONTEXTE:**
{additional_context if additional_context else "Support Arabe, Hébreu"}

**LIVRABLES:**

1. **Configuration RTL/LTR**
```typescript
// utils/rtl.ts
export const RTL_LANGUAGES = ['ar', 'he', 'fa', 'ur'];

export function isRTL(locale: string): boolean {{
  return RTL_LANGUAGES.includes(locale);
}}

export function getDirection(locale: string): 'ltr' | 'rtl' {{
  return isRTL(locale) ? 'rtl' : 'ltr';
}}
```

2. **HTML Setup**
```typescript
// Appliquer dir et lang sur <html>
document.documentElement.dir = getDirection(locale);
document.documentElement.lang = locale;
```

3. **CSS avec Logical Properties**
```css
/* ❌ ÉVITER - Positionnement physique */
.element {{
  margin-left: 20px;
  padding-right: 10px;
  float: left;
}}

/* ✅ UTILISER - Logical properties */
.element {{
  margin-inline-start: 20px;
  padding-inline-end: 10px;
  float: inline-start;
}}

/* Propriétés logiques principales: */
/* margin-inline-start/end (au lieu de left/right) */
/* padding-inline-start/end */
/* border-inline-start/end */
/* inset-inline-start/end (au lieu de left/right) */
```

4. **Flexbox RTL-aware**
```css
.container {{
  display: flex;
  /* flex-direction: row; (par défaut, s'adapte automatiquement) */
  justify-content: flex-start; /* S'inverse automatiquement en RTL */
}}

/* Si besoin de forcer: */
[dir="rtl"] .special-case {{
  flex-direction: row-reverse;
}}
```

5. **Grid RTL-aware**
```css
.grid {{
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  /* S'inverse automatiquement en RTL */
}}
```

6. **Icons et Images Directionnelles**
```typescript
// components/DirectionalIcon.tsx
interface Props {{
  icon: string;
  shouldFlip?: boolean; // Flèches, chevrons, etc.
}}

export function DirectionalIcon({{ icon, shouldFlip = true }}: Props) {{
  const {{ locale }} = useI18n();
  const isRtl = isRTL(locale);

  return (
    <span className={{{{
      'icon': true,
      'flip-rtl': shouldFlip && isRtl
    }}}}>
      {{icon}}
    </span>
  );
}}
```

```css
.flip-rtl {{
  transform: scaleX(-1);
}}
```

7. **Animations RTL-aware**
```css
/* Slide-in animation */
@keyframes slideInLeft {{
  from {{ transform: translateX(-100%); }}
  to {{ transform: translateX(0); }}
}}

@keyframes slideInRight {{
  from {{ transform: translateX(100%); }}
  to {{ transform: translateX(0); }}
}}

/* Utilisation avec logical properties */
.slide-in-start {{
  animation: slideInLeft 0.3s ease-out;
}}

[dir="rtl"] .slide-in-start {{
  animation: slideInRight 0.3s ease-out;
}}
```

8. **Text Alignment**
```css
/* Text alignment s'inverse automatiquement */
.text {{
  text-align: start; /* Gauche en LTR, droite en RTL */
}}

/* Si besoin de centrer (même comportement LTR/RTL): */
.centered {{
  text-align: center;
}}
```

9. **Shadows et Gradients**
```css
/* Adapter les ombres */
.card {{
  box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
}}

[dir="rtl"] .card {{
  box-shadow: -2px 2px 5px rgba(0,0,0,0.1);
}}
```

10. **Testing RTL**
```typescript
// tests/rtl.test.tsx
describe('RTL Support', () => {{
  it('applies RTL direction for Arabic', () => {{
    // Test
  }});

  it('flips directional icons', () => {{
    // Test
  }});
}});
```

11. **Checklist RTL**
```markdown
- [ ] HTML dir et lang attributes dynamiques
- [ ] CSS utilise logical properties (margin-inline-start, etc.)
- [ ] Flexbox/Grid testés en RTL
- [ ] Icons directionnels (flèches) se retournent
- [ ] Animations adaptées à la direction
- [ ] Text alignment utilise start/end
- [ ] Ombres et gradients ajustés
- [ ] Forms (labels, inputs) bien alignés
- [ ] Navigation (menus, breadcrumbs) inversée
- [ ] Modals et dialogs centrés correctement
- [ ] Dates et nombres formatés selon locale
```

**BEST PRACTICES:**
- ✅ Utiliser logical CSS properties par défaut
- ✅ Tester régulièrement en mode RTL
- ✅ Ne pas casser le design LTR en supportant RTL
- ✅ Automatic flipping préféré à manual overrides
- ✅ Documenter les cas spéciaux nécessitant override

**OUTILS DE DÉVELOPPEMENT:**
- Chrome DevTools: Toggle RTL avec `document.dir = 'rtl'`
- Extension "RTL Tester" pour Chrome/Firefox
- Storybook avec addon RTL

Fournis une implémentation robuste et testée."""

    def _build_formatting_prompt(
        self,
        framework: str,
        languages: List[str],
        additional_context: str
    ) -> str:
        """Construit le prompt pour le formatage culturel."""
        return f"""Implémente le formatage culturel (dates, nombres, devises) pour {framework}.

**LANGUES CIBLES:**
{", ".join(languages)}

**CONTEXTE:**
{additional_context if additional_context else "Application internationale"}

**LIVRABLES:**

1. **Date Formatting**
```typescript
// utils/formatDate.ts
import {{ useLocale }} from './i18n';

export function formatDate(
  date: Date,
  options?: Intl.DateTimeFormatOptions
): string {{
  const locale = useLocale();

  return new Intl.DateTimeFormat(locale, {{
    dateStyle: 'medium',
    ...options
  }}).format(date);
}}

// Examples d'usage:
// EN: Dec 9, 2024
// FR: 9 déc. 2024
// AR: ٩ ديسمبر ٢٠٢٤

// Presets communs
export const DATE_FORMATS = {{
  short: {{ dateStyle: 'short' }},      // 12/9/24
  medium: {{ dateStyle: 'medium' }},     // Dec 9, 2024
  long: {{ dateStyle: 'long' }},        // December 9, 2024
  full: {{ dateStyle: 'full' }},        // Monday, December 9, 2024
}};
```

2. **Time Formatting**
```typescript
// utils/formatTime.ts
export function formatTime(
  date: Date,
  use24Hour?: boolean
): string {{
  const locale = useLocale();

  return new Intl.DateTimeFormat(locale, {{
    hour: 'numeric',
    minute: 'numeric',
    hour12: use24Hour === undefined ? undefined : !use24Hour
  }}).format(date);
}}

// Auto-détection 12h/24h selon locale:
// EN-US: 2:30 PM
// FR: 14:30
// AR: ٢:٣٠ م
```

3. **Number Formatting**
```typescript
// utils/formatNumber.ts
export function formatNumber(
  value: number,
  options?: Intl.NumberFormatOptions
): string {{
  const locale = useLocale();

  return new Intl.NumberFormat(locale, options).format(value);
}}

// Examples:
// EN: 1,234.56
// FR: 1 234,56
// AR: ١٬٢٣٤٫٥٦

// Percentage
export function formatPercent(value: number): string {{
  return formatNumber(value, {{ style: 'percent' }});
}}
// EN: 45%
// FR: 45 %
```

4. **Currency Formatting**
```typescript
// utils/formatCurrency.ts
export function formatCurrency(
  amount: number,
  currency: string = 'USD'
): string {{
  const locale = useLocale();

  return new Intl.NumberFormat(locale, {{
    style: 'currency',
    currency
  }}).format(amount);
}}

// Examples:
// EN: $1,234.56
// FR: 1 234,56 $US
// AR: US$ ١٬٢٣٤٫٥٦

// Avec code ISO
export function formatCurrencyWithCode(
  amount: number,
  currency: string
): string {{
  const locale = useLocale();

  return new Intl.NumberFormat(locale, {{
    style: 'currency',
    currency,
    currencyDisplay: 'code' // USD au lieu de $
  }}).format(amount);
}}
```

5. **Relative Time**
```typescript
// utils/formatRelativeTime.ts
export function formatRelativeTime(date: Date): string {{
  const locale = useLocale();
  const rtf = new Intl.RelativeTimeFormat(locale, {{ numeric: 'auto' }});

  const now = new Date();
  const diffInSeconds = (date.getTime() - now.getTime()) / 1000;

  if (Math.abs(diffInSeconds) < 60) {{
    return rtf.format(Math.round(diffInSeconds), 'second');
  }}

  const diffInMinutes = diffInSeconds / 60;
  if (Math.abs(diffInMinutes) < 60) {{
    return rtf.format(Math.round(diffInMinutes), 'minute');
  }}

  const diffInHours = diffInMinutes / 60;
  if (Math.abs(diffInHours) < 24) {{
    return rtf.format(Math.round(diffInHours), 'hour');
  }}

  const diffInDays = diffInHours / 24;
  return rtf.format(Math.round(diffInDays), 'day');
}}

// Examples:
// EN: "2 hours ago", "in 3 days"
// FR: "il y a 2 heures", "dans 3 jours"
// AR: "قبل ساعتين", "خلال ٣ أيام"
```

6. **List Formatting**
```typescript
// utils/formatList.ts
export function formatList(items: string[]): string {{
  const locale = useLocale();

  return new Intl.ListFormat(locale, {{
    style: 'long',
    type: 'conjunction'
  }}).format(items);
}}

// Examples:
// EN: "apples, oranges, and bananas"
// FR: "pommes, oranges et bananes"
// AR: "تفاح وبرتقال وموز"
```

7. **Phone Number Formatting**
```typescript
// utils/formatPhone.ts
import {{ parsePhoneNumber }} from 'libphonenumber-js';

export function formatPhoneNumber(
  phone: string,
  countryCode: string = 'US'
): string {{
  try {{
    const phoneNumber = parsePhoneNumber(phone, countryCode);
    return phoneNumber?.formatInternational() ?? phone;
  }} catch {{
    return phone;
  }}
}}

// Examples:
// US: +1 (555) 123-4567
// FR: +33 6 12 34 56 78
```

8. **React Components**
```typescript
// components/FormattedDate.tsx
export function FormattedDate({{ value, format = 'medium' }}: Props) {{
  return <time dateTime={{value.toISOString()}}>
    {{formatDate(value, DATE_FORMATS[format])}}
  </time>;
}}

// components/FormattedCurrency.tsx
export function FormattedCurrency({{ amount, currency = 'USD' }}: Props) {{
  return <span>{{formatCurrency(amount, currency)}}</span>;
}}

// Usage:
<FormattedDate value={{new Date()}} format="long" />
<FormattedCurrency amount={{1234.56}} currency="EUR" />
```

9. **Testing**
```typescript
// tests/formatting.test.ts
describe('Date Formatting', () => {{
  it('formats date according to locale', () => {{
    const date = new Date('2024-12-09');

    expect(formatDate(date, 'en-US')).toBe('Dec 9, 2024');
    expect(formatDate(date, 'fr-FR')).toBe('9 déc. 2024');
  }});
}});
```

10. **Documentation**
```markdown
# Formatting Guide

## Usage

### Dates
- \`formatDate(date)\` - Format standard
- \`formatTime(date)\` - Time only
- \`formatRelativeTime(date)\` - "2 hours ago"

### Numbers
- \`formatNumber(1234.56)\` - Localized number
- \`formatPercent(0.45)\` - Percentage
- \`formatCurrency(amount, 'USD')\` - Currency

### Lists
- \`formatList(['a', 'b', 'c'])\` - "a, b, and c"

## Examples by Locale
[Table with examples for each supported locale]
```

**BEST PRACTICES:**
- ✅ Utiliser Intl API (natif, pas de lib externe)
- ✅ Cacher les formatters (performance)
- ✅ Fallback gracieux si locale non supportée
- ✅ Tests avec chaque locale supportée
- ✅ Documentation claire pour les développeurs

Fournis une solution complète et performante."""

    def _build_language_switch_prompt(
        self,
        framework: str,
        languages: List[str],
        additional_context: str
    ) -> str:
        """Construit le prompt pour implémenter le changement de langue."""
        return f"""Implémente un système complet de changement de langue pour {framework}.

**LANGUES SUPPORTÉES:**
{", ".join(languages)}

**CONTEXTE:**
{additional_context if additional_context else "Application web multilingue"}

**LIVRABLES:**

1. **Language Detector**
```typescript
// utils/detectLanguage.ts
export function detectUserLanguage(): string {{
  // 1. URL (/fr/, /en/, etc.)
  const urlLocale = detectFromURL();
  if (urlLocale) return urlLocale;

  // 2. LocalStorage (préférence sauvegardée)
  const savedLocale = localStorage.getItem('locale');
  if (savedLocale) return savedLocale;

  // 3. Navigator language
  const browserLocale = navigator.language.split('-')[0];
  if (SUPPORTED_LANGUAGES.includes(browserLocale)) {{
    return browserLocale;
  }}

  // 4. Fallback
  return DEFAULT_LANGUAGE;
}}
```

2. **Language Switcher Component**
```typescript
// components/LanguageSwitcher.tsx
import {{ useTranslation }} from 'react-i18next';

const LANGUAGES = [
  {{ code: 'en', name: 'English', flag: '🇬🇧' }},
  {{ code: 'fr', name: 'Français', flag: '🇫🇷' }},
  {{ code: 'ar', name: 'العربية', flag: '🇸🇦', dir: 'rtl' }},
];

export function LanguageSwitcher() {{
  const {{ i18n }} = useTranslation();
  const [isOpen, setIsOpen] = useState(false);

  const changeLanguage = async (langCode: string) => {{
    await i18n.changeLanguage(langCode);
    localStorage.setItem('locale', langCode);

    // Update HTML dir and lang
    const lang = LANGUAGES.find(l => l.code === langCode);
    document.documentElement.lang = langCode;
    document.documentElement.dir = lang?.dir || 'ltr';

    setIsOpen(false);
  }};

  const currentLang = LANGUAGES.find(l => l.code === i18n.language);

  return (
    <div className="language-switcher">
      <button
        onClick={{() => setIsOpen(!isOpen)}}
        aria-label="Change language"
        aria-expanded={{isOpen}}
      >
        <span>{{currentLang?.flag}}</span>
        <span>{{currentLang?.name}}</span>
      </button>

      {{isOpen && (
        <div role="menu" className="language-menu">
          {{LANGUAGES.map(lang => (
            <button
              key={{lang.code}}
              role="menuitem"
              onClick={{() => changeLanguage(lang.code)}}
              aria-current={{lang.code === i18n.language ? 'true' : undefined}}
            >
              <span>{{lang.flag}}</span>
              <span>{{lang.name}}</span>
            </button>
          ))}}
        </div>
      )}}
    </div>
  );
}}
```

3. **URL-based Locale**
```typescript
// For Next.js
// next.config.js
module.exports = {{
  i18n: {{
    locales: {languages},
    defaultLocale: '{languages[0]}',
    localeDetection: true,
  }},
}};

// Router middleware
export function middleware(request: NextRequest) {{
  const locale = getLocaleFromURL(request.url);

  if (locale) {{
    request.nextUrl.locale = locale;
  }}

  return NextResponse.next();
}}
```

4. **Persistence Strategy**
```typescript
// utils/persistLocale.ts
export function saveLocalePreference(locale: string): void {{
  // LocalStorage
  localStorage.setItem('locale', locale);

  // Cookie (pour SSR)
  document.cookie = `locale=${{locale}}; path=/; max-age=31536000`; // 1 an

  // Optional: API call pour users connectés
  // await updateUserLocale(locale);
}}

export function getPersistedLocale(): string | null {{
  // Priority: URL > LocalStorage > Cookie > Navigator
  return (
    getLocaleFromURL() ||
    localStorage.getItem('locale') ||
    getCookieLocale() ||
    navigator.language.split('-')[0]
  );
}}
```

5. **Dynamic Language Loading**
```typescript
// i18n/dynamicLoader.ts
export async function loadLanguage(locale: string): Promise<void> {{
  if (i18n.hasResourceBundle(locale, 'common')) {{
    // Already loaded
    return;
  }}

  // Lazy load translation files
  const resources = await import(`../locales/${{locale}}/common.json`);

  i18n.addResourceBundle(locale, 'common', resources.default);
}}

// Usage
await loadLanguage('fr');
await i18n.changeLanguage('fr');
```

6. **SEO Optimization**
```typescript
// components/LanguageAlternates.tsx (pour <head>)
export function LanguageAlternates() {{
  const {{ locale, locales }} = useRouter();
  const canonicalURL = getCanonicalURL();

  return (
    <>
      {{/* Canonical URL */}}
      <link rel="canonical" href={{canonicalURL}} />

      {{/* hreflang pour chaque langue */}}
      {{locales?.map(lang => (
        <link
          key={{lang}}
          rel="alternate"
          hrefLang={{lang}}
          href={{`${{canonicalURL}}?lang=${{lang}}`}}
        />
      ))}}

      {{/* Default language */}}
      <link
        rel="alternate"
        hrefLang="x-default"
        href={{canonicalURL}}
      />
    </>
  );
}}
```

7. **Smooth Transition**
```typescript
// No page reload, smooth transition
export function changeLanguageSmooth(newLocale: string): Promise<void> {{
  return new Promise((resolve) => {{
    // Fade out
    document.body.style.opacity = '0';
    document.body.style.transition = 'opacity 0.2s';

    setTimeout(async () => {{
      await i18n.changeLanguage(newLocale);
      saveLocalePreference(newLocale);

      // Update direction if needed
      const isRTL = ['ar', 'he', 'fa'].includes(newLocale);
      document.documentElement.dir = isRTL ? 'rtl' : 'ltr';

      // Fade in
      document.body.style.opacity = '1';
      resolve();
    }}, 200);
  }});
}}
```

8. **Mobile Language Picker**
```typescript
// components/MobileLanguagePicker.tsx
export function MobileLanguagePicker() {{
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <button onClick={{() => setIsOpen(true)}}>
        🌍 Language
      </button>

      {{/* Bottom Sheet */}}
      <BottomSheet isOpen={{isOpen}} onClose={{() => setIsOpen(false)}}>
        <h2>Choose Language</h2>
        {{LANGUAGES.map(lang => (
          <LanguageOption
            key={{lang.code}}
            lang={{lang}}
            onClick={{() => {{
              changeLanguage(lang.code);
              setIsOpen(false);
            }}}}
          />
        ))}}
      </BottomSheet>
    </>
  );
}}
```

9. **Analytics Integration**
```typescript
// Track language changes
export function trackLanguageChange(newLocale: string): void {{
  // Google Analytics
  gtag('event', 'language_change', {{
    locale: newLocale,
  }});

  // Custom analytics
  analytics.track('Language Changed', {{
    from: i18n.language,
    to: newLocale,
    timestamp: new Date().toISOString(),
  }});
}}
```

10. **Testing**
```typescript
// tests/languageSwitcher.test.tsx
describe('Language Switcher', () => {{
  it('changes language without reload', async () => {{
    render(<LanguageSwitcher />);

    const frButton = screen.getByText('Français');
    fireEvent.click(frButton);

    await waitFor(() => {{
      expect(i18n.language).toBe('fr');
      expect(localStorage.getItem('locale')).toBe('fr');
    }});
  }});

  it('updates HTML dir for RTL languages', async () => {{
    render(<LanguageSwitcher />);

    const arButton = screen.getByText('العربية');
    fireEvent.click(arButton);

    await waitFor(() => {{
      expect(document.documentElement.dir).toBe('rtl');
    }});
  }});
}});
```

**BEST PRACTICES:**
- ✅ Changement sans rechargement de page
- ✅ Persistance multi-couches (URL, LocalStorage, Cookie)
- ✅ SEO avec hreflang tags
- ✅ Smooth transitions visuelles
- ✅ Analytics pour tracker les changements
- ✅ Accessible (ARIA labels, keyboard nav)
- ✅ Mobile-friendly (bottom sheet sur mobile)

**UX CONSIDERATIONS:**
- Afficher le nom de la langue dans sa langue native
- Flags optionnels (attention aux sensibilités géopolitiques)
- Position: Header (desktop), Bottom nav (mobile)
- Feedback visuel immédiat au changement

Fournis une solution UX optimale et robuste."""

    async def setup_i18n(
        self,
        framework: str,
        languages: List[str],
        context: str = ""
    ) -> str:
        """
        Méthode helper pour setup i18n complet.

        Args:
            framework (str): Framework cible (react, next, vue, etc.)
            languages (List[str]): Liste des langues à supporter
            context (str): Contexte additionnel

        Returns:
            str: Configuration complète i18n
        """
        result = await self.execute({
            "task_type": "setup",
            "framework": framework,
            "languages": languages,
            "context": context
        })
        return result["result"]

    async def manage_translations(
        self,
        code: str,
        languages: List[str],
        context: str = ""
    ) -> str:
        """
        Méthode helper pour gérer les traductions.

        Args:
            code (str): Code à analyser pour extraction
            languages (List[str]): Langues cibles
            context (str): Contexte additionnel

        Returns:
            str: Fichiers de traduction et scripts
        """
        result = await self.execute({
            "task_type": "translations",
            "code": code,
            "languages": languages,
            "context": context
        })
        return result["result"]

    async def implement_rtl(
        self,
        code: str,
        framework: str,
        context: str = ""
    ) -> str:
        """
        Méthode helper pour implémenter RTL.

        Args:
            code (str): Code à adapter pour RTL
            framework (str): Framework utilisé
            context (str): Contexte additionnel

        Returns:
            str: Code et styles RTL-ready
        """
        result = await self.execute({
            "task_type": "rtl",
            "code": code,
            "framework": framework,
            "context": context
        })
        return result["result"]

    async def setup_formatting(
        self,
        framework: str,
        languages: List[str],
        context: str = ""
    ) -> str:
        """
        Méthode helper pour setup formatage culturel.

        Args:
            framework (str): Framework cible
            languages (List[str]): Langues supportées
            context (str): Contexte additionnel

        Returns:
            str: Utilitaires de formatage
        """
        result = await self.execute({
            "task_type": "formatting",
            "framework": framework,
            "languages": languages,
            "context": context
        })
        return result["result"]

    async def implement_language_switcher(
        self,
        framework: str,
        languages: List[str],
        context: str = ""
    ) -> str:
        """
        Méthode helper pour implémenter le changement de langue.

        Args:
            framework (str): Framework utilisé
            languages (List[str]): Langues disponibles
            context (str): Contexte additionnel

        Returns:
            str: Composant et logique de changement de langue
        """
        result = await self.execute({
            "task_type": "language_switch",
            "framework": framework,
            "languages": languages,
            "context": context
        })
        return result["result"]
