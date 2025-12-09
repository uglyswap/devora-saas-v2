# Devora Internationalization (i18n) Guide

## Overview

Devora supports multiple languages using **react-i18next**, a powerful internationalization framework for React applications.

**Currently Supported Languages:**
- English (en) - Default
- French (fr)
- Spanish (es)

**Features:**
- Automatic language detection based on browser settings
- Language persistence in localStorage and cookies
- Dynamic language switching without page reload
- Pluralization support
- Date, number, and currency formatting
- Nested translation keys
- Interpolation and formatting

---

## Quick Start

### 1. Import and Use Translations

```jsx
import { useTranslation } from 'react-i18next';

function MyComponent() {
  const { t } = useTranslation();

  return (
    <div>
      <h1>{t('common.welcome')}</h1>
      <p>{t('dashboard.title')}</p>
    </div>
  );
}
```

### 2. Add Language Switcher

```jsx
import { LanguageSwitcher } from '../components/LanguageSwitcher';

function Navigation() {
  return (
    <nav>
      {/* Other nav items */}
      <LanguageSwitcher />
    </nav>
  );
}
```

---

## Configuration

### File Structure

```
frontend/src/
├── i18n/
│   └── config.js              # i18n configuration
├── locales/
│   ├── en.json               # English translations
│   ├── fr.json               # French translations
│   └── es.json               # Spanish translations
└── components/
    └── LanguageSwitcher.jsx  # Language switcher component
```

### Configuration File (`i18n/config.js`)

```javascript
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Import translations
import enTranslations from '../locales/en.json';
import frTranslations from '../locales/fr.json';
import esTranslations from '../locales/es.json';

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: enTranslations },
      fr: { translation: frTranslations },
      es: { translation: esTranslations }
    },
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false // React already escapes
    }
  });

export default i18n;
```

### Initialize in App

```jsx
// frontend/src/index.js
import React from 'react';
import ReactDOM from 'react-dom';
import './i18n/config'; // Initialize i18n
import App from './App';

ReactDOM.render(<App />, document.getElementById('root'));
```

---

## Translation Files

### JSON Structure

Translation files use nested keys for organization:

```json
{
  "common": {
    "welcome": "Welcome",
    "loading": "Loading...",
    "error": "Error"
  },
  "auth": {
    "login": {
      "title": "Login to Devora",
      "email": "Email Address",
      "password": "Password"
    }
  }
}
```

### Accessing Translations

```jsx
const { t } = useTranslation();

// Simple translation
t('common.welcome') // "Welcome"

// Nested translation
t('auth.login.title') // "Login to Devora"
```

---

## Advanced Features

### 1. Interpolation

Insert dynamic values into translations:

**Translation file:**
```json
{
  "dashboard": {
    "welcome": "Welcome back, {{name}}"
  }
}
```

**Usage:**
```jsx
t('dashboard.welcome', { name: 'John' })
// Output: "Welcome back, John"
```

### 2. Pluralization

Handle singular/plural forms:

**Translation file:**
```json
{
  "items": {
    "count_one": "{{count}} item",
    "count_other": "{{count}} items"
  }
}
```

**Usage:**
```jsx
t('items.count', { count: 1 })  // "1 item"
t('items.count', { count: 5 })  // "5 items"
```

### 3. Formatting

#### Date Formatting

```jsx
import { formatDate } from '../i18n/config';

// Automatic locale-aware formatting
formatDate(new Date(), { dateStyle: 'long' })
// EN: "December 9, 2025"
// FR: "9 décembre 2025"
// ES: "9 de diciembre de 2025"
```

#### Number Formatting

```jsx
import { formatNumber, formatCurrency } from '../i18n/config';

formatNumber(1234567.89)
// EN: "1,234,567.89"
// FR: "1 234 567,89"
// ES: "1.234.567,89"

formatCurrency(99.99, 'USD')
// EN: "$99.99"
// FR: "99,99 $US"
// ES: "99,99 US$"
```

#### Custom Formatting in Translations

**Translation file:**
```json
{
  "price": "Price: {{value, currency}}",
  "date": "Created on {{date, date}}"
}
```

**Usage:**
```jsx
t('price', { value: 99.99 })
t('date', { date: new Date() })
```

### 4. Context and Gender

Handle different contexts:

**Translation file:**
```json
{
  "friend_male": "He is my friend",
  "friend_female": "She is my friend"
}
```

**Usage:**
```jsx
t('friend', { context: 'male' })   // "He is my friend"
t('friend', { context: 'female' }) // "She is my friend"
```

---

## Components

### LanguageSwitcher Component

#### Basic Usage

```jsx
import { LanguageSwitcher } from '../components/LanguageSwitcher';

<LanguageSwitcher />
```

#### Variants

```jsx
// Compact (icon only)
import { LanguageSwitcherCompact } from '../components/LanguageSwitcher';
<LanguageSwitcherCompact />

// With flags
import { LanguageSwitcherWithFlags } from '../components/LanguageSwitcher';
<LanguageSwitcherWithFlags />

// Inline (for settings pages)
import { InlineLanguageSelector } from '../components/LanguageSwitcher';
<InlineLanguageSelector />
```

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `variant` | string | `'outline'` | Button variant (default, outline, ghost) |
| `size` | string | `'default'` | Button size (default, sm, lg) |
| `showLabel` | boolean | `true` | Show language label |
| `showFlag` | boolean | `true` | Show flag emoji |
| `className` | string | `''` | Additional CSS classes |

---

## Hooks and Utilities

### useTranslation Hook

```jsx
import { useTranslation } from 'react-i18next';

function MyComponent() {
  const { t, i18n } = useTranslation();

  return (
    <div>
      <p>{t('common.welcome')}</p>
      <p>Current language: {i18n.language}</p>
      <button onClick={() => i18n.changeLanguage('fr')}>
        Switch to French
      </button>
    </div>
  );
}
```

### Helper Functions

```jsx
import {
  getCurrentLanguage,
  changeLanguage,
  formatNumber,
  formatCurrency,
  formatDate,
  formatRelativeTime
} from '../i18n/config';

// Get current language info
const lang = getCurrentLanguage();
// { code: 'en', name: 'English', nativeName: 'English', flag: '🇺🇸', dir: 'ltr' }

// Change language programmatically
await changeLanguage('fr');

// Format numbers
formatNumber(1234567.89); // "1,234,567.89"

// Format currency
formatCurrency(99.99, 'USD'); // "$99.99"

// Format dates
formatDate(new Date(), { dateStyle: 'medium' }); // "Dec 9, 2025"

// Relative time
formatRelativeTime(-1, 'day'); // "yesterday"
formatRelativeTime(2, 'hour'); // "in 2 hours"
```

---

## Translation Best Practices

### 1. Key Naming Conventions

- Use dot notation for nesting: `auth.login.title`
- Use descriptive keys: `errorInvalidEmail` instead of `error1`
- Group related translations: `dashboard.*`, `settings.*`

### 2. Avoid Hardcoded Strings

**Bad:**
```jsx
<h1>Welcome to Devora</h1>
```

**Good:**
```jsx
<h1>{t('common.welcome')}</h1>
```

### 3. Handle Missing Translations

i18next will fall back to English if a translation is missing:

```jsx
// If French translation is missing
t('some.missing.key') // Falls back to English
```

### 4. Keep Translations Synchronized

When adding a new key to `en.json`, add it to all other language files:

```bash
# Check for missing keys
npm run i18n:check
```

### 5. Use Interpolation for Dynamic Content

**Bad:**
```jsx
const message = 'Hello, ' + userName;
```

**Good:**
```json
{ "greeting": "Hello, {{name}}" }
```
```jsx
t('greeting', { name: userName })
```

---

## Adding a New Language

### Step 1: Create Translation File

Create `frontend/src/locales/de.json` (German):

```json
{
  "common": {
    "welcome": "Willkommen",
    "loading": "Laden..."
  }
}
```

### Step 2: Update Configuration

Update `frontend/src/i18n/config.js`:

```javascript
import deTranslations from '../locales/de.json';

export const SUPPORTED_LANGUAGES = [
  // ... existing languages
  {
    code: 'de',
    name: 'German',
    nativeName: 'Deutsch',
    flag: '🇩🇪',
    dir: 'ltr'
  }
];

i18n.init({
  resources: {
    // ... existing languages
    de: { translation: deTranslations }
  },
  supportedLngs: ['en', 'fr', 'es', 'de']
});
```

### Step 3: Test

The new language will automatically appear in the LanguageSwitcher.

---

## Right-to-Left (RTL) Support

For RTL languages like Arabic:

### Step 1: Add RTL Language

```javascript
export const SUPPORTED_LANGUAGES = [
  // ... existing languages
  {
    code: 'ar',
    name: 'Arabic',
    nativeName: 'العربية',
    flag: '🇸🇦',
    dir: 'rtl' // Right-to-left
  }
];
```

### Step 2: Update HTML Direction

The configuration automatically updates the `dir` attribute:

```javascript
i18n.on('languageChanged', (lng) => {
  const language = SUPPORTED_LANGUAGES.find(l => l.code === lng);
  if (language) {
    document.documentElement.dir = language.dir; // 'ltr' or 'rtl'
  }
});
```

### Step 3: Add RTL Styles

```css
/* frontend/src/index.css */
[dir="rtl"] {
  direction: rtl;
  text-align: right;
}

[dir="rtl"] .ml-2 {
  margin-left: 0;
  margin-right: 0.5rem;
}
```

---

## Testing Translations

### Manual Testing

1. Open the application
2. Click the language switcher
3. Select a language
4. Verify all text changes correctly
5. Check pluralization with different counts
6. Test date/number formatting

### Automated Testing

```jsx
// __tests__/i18n.test.js
import i18n from '../i18n/config';

describe('i18n', () => {
  it('should translate common keys', () => {
    i18n.changeLanguage('en');
    expect(i18n.t('common.welcome')).toBe('Welcome');

    i18n.changeLanguage('fr');
    expect(i18n.t('common.welcome')).toBe('Bienvenue');
  });

  it('should handle interpolation', () => {
    i18n.changeLanguage('en');
    expect(i18n.t('dashboard.welcome', { name: 'John' }))
      .toBe('Welcome back, John');
  });
});
```

---

## Troubleshooting

### Translations Not Loading

**Issue:** Translations don't appear, showing keys instead.

**Solution:**
1. Check that i18n is initialized before App renders:
   ```jsx
   import './i18n/config'; // BEFORE importing App
   import App from './App';
   ```

2. Verify JSON syntax in translation files (no trailing commas)

3. Check console for errors

### Language Not Persisting

**Issue:** Language resets on page reload.

**Solution:**
Check that cookies/localStorage are enabled:

```javascript
// i18n/config.js
detection: {
  caches: ['localStorage', 'cookie']
}
```

### Missing Translation Warnings

**Issue:** Console shows "Missing translation" warnings.

**Solution:**
1. Add missing keys to translation files
2. Or disable warnings in production:
   ```javascript
   i18n.init({
     saveMissing: process.env.NODE_ENV === 'development'
   });
   ```

---

## Performance Optimization

### 1. Lazy Load Translations

For large applications, load translations on demand:

```javascript
import HttpBackend from 'i18next-http-backend';

i18n
  .use(HttpBackend)
  .init({
    backend: {
      loadPath: '/locales/{{lng}}.json'
    }
  });
```

### 2. Split Namespaces

Organize translations by feature:

```
locales/
├── en/
│   ├── common.json
│   ├── dashboard.json
│   └── editor.json
```

```jsx
const { t } = useTranslation('dashboard');
t('title'); // Loads only dashboard namespace
```

---

## Accessibility Considerations

### 1. Language Attribute

The configuration automatically sets the `lang` attribute:

```html
<html lang="en">
```

This helps screen readers pronounce text correctly.

### 2. Announce Language Changes

The LanguageSwitcher component announces changes to screen readers:

```jsx
const announcement = `Language changed to ${language.name}`;
announceToScreenReader(announcement);
```

### 3. ARIA Labels

Ensure ARIA labels are translated:

```jsx
<button aria-label={t('accessibility.closeDialog')}>
  <CloseIcon />
</button>
```

---

## Resources

- [react-i18next Documentation](https://react.i18next.com/)
- [i18next Documentation](https://www.i18next.com/)
- [Pluralization Rules](https://www.i18next.com/translation-function/plurals)
- [Formatting](https://www.i18next.com/translation-function/formatting)

---

## Support

For questions or issues:
- Check this documentation first
- Review the [WCAG 2.1 Accessibility Audit](./accessibility/WCAG_AUDIT.md)
- Contact the development team

---

**Last Updated:** December 9, 2025
