# Accessibility & i18n Integration Guide

## Quick Setup

This guide shows how to integrate the new accessibility features and internationalization into your existing Devora application.

---

## Step 1: Initialize i18n

### Update `frontend/src/index.js`

```javascript
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import './styles/accessibility.css'; // Import accessibility styles
import './i18n/config'; // Initialize i18n BEFORE App
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

### Update `frontend/public/index.html`

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="Devora - Build web applications visually" />
    <title>Devora</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
```

**Note:** The `lang` attribute will be automatically updated by i18n when language changes.

---

## Step 2: Update Navigation Component

### `frontend/src/components/Navigation.jsx`

```jsx
import React from 'react';
import { useTranslation } from 'react-i18next';
import { LanguageSwitcher } from './LanguageSwitcher';
import { useSkipLink } from '../hooks/useAccessibility';

export function Navigation() {
  const { t } = useTranslation();
  const { skipLinkProps } = useSkipLink();

  return (
    <>
      {/* Skip Navigation Link (WCAG 2.4.1) */}
      <a {...skipLinkProps}>
        {t('navigation.skipToMain')}
      </a>

      <header role="banner">
        <nav role="navigation" aria-label={t('navigation.menu')}>
          <div className="nav-container">
            <div className="nav-brand">
              <h1>{t('common.appName')}</h1>
            </div>

            <ul className="nav-links">
              <li>
                <a href="/dashboard">{t('navigation.dashboard')}</a>
              </li>
              <li>
                <a href="/editor">{t('navigation.editor')}</a>
              </li>
              <li>
                <a href="/templates">{t('navigation.templates')}</a>
              </li>
              <li>
                <a href="/settings">{t('navigation.settings')}</a>
              </li>
            </ul>

            <div className="nav-actions">
              {/* Language Switcher */}
              <LanguageSwitcher variant="ghost" size="sm" />

              {/* User Menu */}
              <button
                aria-label={t('navigation.profile')}
                aria-haspopup="menu"
              >
                Profile
              </button>
            </div>
          </div>
        </nav>
      </header>
    </>
  );
}
```

---

## Step 3: Update App.js

### `frontend/src/App.js`

```jsx
import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useKeyboardFocus } from './hooks/useAccessibility';

// Pages
import HomePage from './pages/HomePage';
import Dashboard from './pages/Dashboard';
import EditorPage from './pages/EditorPageUltimate';
import Login from './pages/Login';
import Register from './pages/Register';
import SettingsPage from './pages/SettingsPage';

// Components
import { Navigation } from './components/Navigation';

function App() {
  const { i18n } = useTranslation();

  // Enable keyboard focus detection
  useKeyboardFocus();

  // Update HTML lang attribute when language changes
  useEffect(() => {
    document.documentElement.lang = i18n.language;
  }, [i18n.language]);

  return (
    <Router>
      <div className="app">
        <Navigation />

        <main id="main-content" tabIndex={-1}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/editor" element={<EditorPage />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
```

---

## Step 4: Update Login Page (Example)

### `frontend/src/pages/Login.jsx`

```jsx
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  useAriaAnnouncement,
  useAutoId,
  useAriaDescribedBy
} from '../hooks/useAccessibility';

export function Login() {
  const { t } = useTranslation();
  const announce = useAriaAnnouncement('polite');

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  // Auto-generate IDs for accessibility
  const emailId = useAutoId('email');
  const passwordId = useAutoId('password');

  // Setup ARIA descriptions
  const emailAria = useAriaDescribedBy(emailId, {
    hasError: !!errors.email
  });
  const passwordAria = useAriaDescribedBy(passwordId, {
    hasHint: true,
    hasError: !!errors.password
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrors({});

    try {
      // Validation
      const newErrors = {};
      if (!email) {
        newErrors.email = t('auth.validation.emailRequired');
      } else if (!/\S+@\S+\.\S+/.test(email)) {
        newErrors.email = t('auth.validation.emailInvalid');
      }
      if (!password) {
        newErrors.password = t('auth.validation.passwordRequired');
      }

      if (Object.keys(newErrors).length > 0) {
        setErrors(newErrors);
        announce(t('common.error') + ': ' + Object.values(newErrors).join(', '));
        setLoading(false);
        return;
      }

      // Login logic here
      // await login(email, password);

      announce(t('common.success'));
    } catch (error) {
      setErrors({ general: t('auth.login.errorGeneric') });
      announce(t('auth.login.errorGeneric'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <h1>{t('auth.login.title')}</h1>
        <p className="text-muted">{t('auth.login.subtitle')}</p>

        <form onSubmit={handleSubmit}>
          {/* Email Field */}
          <div className="form-field">
            <label htmlFor={emailId}>
              {t('auth.login.email')}
              <span aria-label={t('accessibility.required')}>*</span>
            </label>
            <input
              id={emailId}
              type="email"
              name="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder={t('auth.login.emailPlaceholder')}
              autoComplete="email"
              aria-describedby={emailAria.ariaDescribedBy}
              aria-invalid={!!errors.email}
              required
            />
            {errors.email && (
              <span
                id={emailAria.errorId}
                role="alert"
                aria-live="polite"
                className="error-message"
              >
                {errors.email}
              </span>
            )}
          </div>

          {/* Password Field */}
          <div className="form-field">
            <label htmlFor={passwordId}>
              {t('auth.login.password')}
              <span aria-label={t('accessibility.required')}>*</span>
            </label>
            <input
              id={passwordId}
              type="password"
              name="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder={t('auth.login.passwordPlaceholder')}
              autoComplete="current-password"
              aria-describedby={passwordAria.ariaDescribedBy}
              aria-invalid={!!errors.password}
              required
            />
            <span id={passwordAria.hintId} className="hint">
              {t('auth.validation.passwordTooShort')}
            </span>
            {errors.password && (
              <span
                id={passwordAria.errorId}
                role="alert"
                aria-live="polite"
                className="error-message"
              >
                {errors.password}
              </span>
            )}
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            aria-busy={loading}
          >
            {loading ? t('common.loading') : t('auth.login.loginButton')}
          </button>

          {/* General Error */}
          {errors.general && (
            <div role="alert" aria-live="assertive" className="alert-error">
              {errors.general}
            </div>
          )}
        </form>

        <p className="text-center">
          {t('auth.login.noAccount')}{' '}
          <a href="/register">{t('auth.login.registerLink')}</a>
        </p>
      </div>
    </div>
  );
}

export default Login;
```

---

## Step 5: Update Settings Page

### `frontend/src/pages/SettingsPage.jsx`

Add language selection:

```jsx
import React from 'react';
import { useTranslation } from 'react-i18next';
import { InlineLanguageSelector } from '../components/LanguageSwitcher';
import { useReducedMotion } from '../hooks/useAccessibility';

export function SettingsPage() {
  const { t } = useTranslation();
  const prefersReducedMotion = useReducedMotion();

  return (
    <div className="settings-page">
      <h1>{t('settings.title')}</h1>
      <p className="text-muted">{t('settings.subtitle')}</p>

      {/* Preferences Section */}
      <section>
        <h2>{t('settings.preferences.title')}</h2>

        {/* Language Selector */}
        <div className="setting-group">
          <label>{t('settings.preferences.language')}</label>
          <InlineLanguageSelector />
        </div>

        {/* Reduced Motion Toggle */}
        <div className="setting-group">
          <label htmlFor="reduced-motion">
            {t('settings.preferences.reducedMotion')}
          </label>
          <input
            type="checkbox"
            id="reduced-motion"
            checked={prefersReducedMotion}
            onChange={(e) => {
              if (e.target.checked) {
                document.documentElement.classList.add('reduce-motion');
              } else {
                document.documentElement.classList.remove('reduce-motion');
              }
            }}
          />
          <p className="text-sm text-muted">
            {t('settings.preferences.reducedMotionHelp')}
          </p>
        </div>
      </section>
    </div>
  );
}

export default SettingsPage;
```

---

## Step 6: Update Dialog/Modal Components

### Example: Accessible Dialog

```jsx
import React, { useRef } from 'react';
import { useTranslation } from 'react-i18next';
import {
  useFocusTrap,
  useEscapeKey,
  useScrollLock
} from '../hooks/useAccessibility';

export function Dialog({ isOpen, onClose, title, children }) {
  const { t } = useTranslation();
  const dialogRef = useRef(null);

  // Trap focus inside dialog
  useFocusTrap(dialogRef, isOpen);

  // Close on Escape key
  useEscapeKey(onClose, isOpen);

  // Lock body scroll
  useScrollLock(isOpen);

  if (!isOpen) return null;

  return (
    <div className="dialog-backdrop" onClick={onClose}>
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="dialog-title"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="dialog-header">
          <h2 id="dialog-title">{title}</h2>
          <button
            onClick={onClose}
            aria-label={t('accessibility.closeDialog')}
          >
            ×
          </button>
        </div>

        <div className="dialog-content">
          {children}
        </div>
      </div>
    </div>
  );
}
```

---

## Step 7: Update Button Components

### `frontend/src/components/ui/button.jsx`

```jsx
import React from 'react';
import { useReducedMotion } from '../../hooks/useAccessibility';

export const Button = React.forwardRef(({
  children,
  variant = 'default',
  size = 'default',
  loading = false,
  className = '',
  ...props
}, ref) => {
  const prefersReducedMotion = useReducedMotion();

  return (
    <button
      ref={ref}
      className={`
        btn btn-${variant} btn-${size}
        ${loading ? 'btn-loading' : ''}
        ${prefersReducedMotion ? 'no-animation' : ''}
        ${className}
      `}
      aria-busy={loading}
      disabled={loading || props.disabled}
      {...props}
    >
      {loading && (
        <span className="loading-spinner" aria-hidden="true" />
      )}
      {children}
    </button>
  );
});

Button.displayName = 'Button';
```

---

## Step 8: Add Toast Notifications

### Example: Accessible Toast

```jsx
import React from 'react';
import { useTranslation } from 'react-i18next';

export function Toast({ title, description, variant = 'info' }) {
  const { t } = useTranslation();

  return (
    <div
      role="status"
      aria-live="polite"
      aria-atomic="true"
      className={`toast toast-${variant}`}
    >
      <div className="toast-icon" aria-hidden="true">
        {variant === 'success' && '✓'}
        {variant === 'error' && '✗'}
        {variant === 'info' && 'ℹ'}
      </div>
      <div className="toast-content">
        <div className="toast-title">{title}</div>
        {description && (
          <div className="toast-description">{description}</div>
        )}
      </div>
    </div>
  );
}

// Usage
function MyComponent() {
  const { t } = useTranslation();
  const announce = useAriaAnnouncement('polite');

  const showSuccessToast = () => {
    announce(t('editor.messages.projectSaved'));
    // Show toast UI
  };

  return <button onClick={showSuccessToast}>Save</button>;
}
```

---

## Testing Checklist

### Accessibility Testing

- [ ] Test keyboard navigation (Tab, Shift+Tab, Enter, Esc)
- [ ] Test with screen reader (NVDA, JAWS, VoiceOver)
- [ ] Test at 200% zoom
- [ ] Run Lighthouse accessibility audit (target: 97+)
- [ ] Run axe DevTools
- [ ] Test color contrast (all text 4.5:1+)
- [ ] Test focus indicators visibility
- [ ] Test with reduced motion enabled

### i18n Testing

- [ ] Switch to French and verify all text changes
- [ ] Switch to Spanish and verify all text changes
- [ ] Verify language persists after page reload
- [ ] Test pluralization (1 item vs 2 items)
- [ ] Test date/number formatting in each language
- [ ] Verify HTML lang attribute updates
- [ ] Test with browser language detection

---

## NPM Scripts

Add these to `frontend/package.json`:

```json
{
  "scripts": {
    "start": "craco start",
    "build": "craco build",
    "test": "craco test",
    "test:a11y": "pa11y-ci --sitemap http://localhost:3000/sitemap.xml",
    "typecheck": "tsc --noEmit"
  }
}
```

---

## Resources

- [WCAG 2.1 AA Audit Report](../docs/accessibility/WCAG_AUDIT.md)
- [Accessibility Checklist](../docs/accessibility/CHECKLIST.md)
- [i18n Guide](../docs/I18N_GUIDE.md)
- [Accessibility Hooks Documentation](../frontend/src/hooks/useAccessibility.js)

---

## Support

For questions or issues:
1. Check the documentation above
2. Review code examples in this guide
3. Contact the development team

**Last Updated:** December 9, 2025
