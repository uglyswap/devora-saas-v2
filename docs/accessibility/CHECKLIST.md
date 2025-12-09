# Accessibility Implementation Checklist

## Overview

This checklist provides a step-by-step guide to implement WCAG 2.1 AA compliance for the Devora platform. Each item includes implementation details and code examples.

**Goal:** Increase accessibility score from 78/100 to 97/100

---

## Phase 1: Critical Fixes (Week 1)

### 1.1 Color Contrast Fixes

**Status:** 🔴 Not Started | 🟡 In Progress | 🟢 Complete

- [ ] **Fix Button Contrast Issues**
  ```css
  /* Update: frontend/src/components/ui/button.jsx */
  .btn-secondary {
    background: #0066cc; /* Ensure 4.5:1 ratio */
    color: #ffffff;
  }

  .btn-disabled {
    background: #666666;
    color: #ffffff; /* 4.5:1 minimum */
  }
  ```

- [ ] **Fix Placeholder Text Contrast**
  ```css
  /* Update: frontend/src/styles/accessibility.css */
  input::placeholder,
  textarea::placeholder {
    color: #6b7280; /* Minimum 4.5:1 with white background */
    opacity: 1;
  }
  ```

- [ ] **Fix Navigation Link Hover States**
  ```css
  .nav-link:hover,
  .nav-link:focus {
    color: #0047b3; /* Darker blue for better contrast */
    background: #f0f4ff;
  }
  ```

- [ ] **Fix Card Subtitle Contrast**
  ```css
  .card-subtitle {
    color: #4b5563; /* Update from #6b7280 */
  }
  ```

- [ ] **Fix Footer Text Contrast**
  ```css
  footer {
    background: #1f2937;
    color: #f9fafb; /* Minimum 4.5:1 */
  }

  footer a {
    color: #60a5fa; /* Ensure link contrast */
  }
  ```

- [ ] **Fix Tag/Badge Backgrounds**
  ```css
  .badge {
    background: #2563eb;
    color: #ffffff;
  }
  ```

- [ ] **Fix Focus Outline Contrast**
  ```css
  *:focus-visible {
    outline: 3px solid #0066cc; /* 3:1 minimum */
    outline-offset: 2px;
  }
  ```

- [ ] **Run Contrast Checker on All Components**
  - Tool: WebAIM Contrast Checker
  - Verify all text: 4.5:1 minimum (3:1 for large text)
  - Verify all UI components: 3:1 minimum

---

### 1.2 Focus Indicators

- [ ] **Create Global Focus Styles**
  ```css
  /* Add to: frontend/src/styles/accessibility.css */

  /* Remove default focus styles */
  *:focus {
    outline: none;
  }

  /* Add visible focus for keyboard navigation */
  *:focus-visible {
    outline: 3px solid #0066cc;
    outline-offset: 2px;
    border-radius: 2px;
  }

  /* High contrast mode support */
  @media (prefers-contrast: high) {
    *:focus-visible {
      outline: 4px solid;
      outline-offset: 3px;
    }
  }

  /* Dark mode focus */
  .dark *:focus-visible {
    outline-color: #60a5fa;
  }
  ```

- [ ] **Add Focus Styles to Buttons**
  ```jsx
  // Update: frontend/src/components/ui/button.jsx
  const Button = React.forwardRef(({ className, variant, size, ...props }, ref) => {
    return (
      <button
        className={cn(
          "focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-blue-600",
          "focus-visible:ring-offset-2",
          buttonVariants({ variant, size, className })
        )}
        ref={ref}
        {...props}
      />
    )
  })
  ```

- [ ] **Add Focus Styles to Inputs**
  ```jsx
  // Update: frontend/src/components/ui/input.jsx
  const Input = React.forwardRef(({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          "focus-visible:ring-3 focus-visible:ring-blue-600",
          "focus-visible:ring-offset-2",
          className
        )}
        ref={ref}
        {...props}
      />
    )
  })
  ```

- [ ] **Add Focus Styles to Links**
  ```css
  a:focus-visible {
    outline: 3px solid #0066cc;
    outline-offset: 2px;
    border-radius: 2px;
  }
  ```

- [ ] **Test Focus Indicators**
  - Navigate entire app with Tab key
  - Verify all interactive elements have visible focus
  - Test in Chrome, Firefox, Safari

---

### 1.3 Keyboard Navigation

- [ ] **Fix Modal Focus Trap**
  ```jsx
  // Update: frontend/src/components/ui/dialog.jsx
  import { useEffect, useRef } from 'react';
  import { useFocusTrap } from '@/hooks/useAccessibility';

  const Dialog = ({ open, onClose, children }) => {
    const dialogRef = useRef(null);
    useFocusTrap(dialogRef, open);

    useEffect(() => {
      const handleEscape = (e) => {
        if (e.key === 'Escape' && open) {
          onClose();
        }
      };

      document.addEventListener('keydown', handleEscape);
      return () => document.removeEventListener('keydown', handleEscape);
    }, [open, onClose]);

    return (
      <div ref={dialogRef} role="dialog" aria-modal="true">
        {children}
      </div>
    );
  };
  ```

- [ ] **Add Escape Key Support to All Modals**
  - Update: Dialog, AlertDialog, Sheet, Drawer components
  - Test: Press Esc to close each modal type

- [ ] **Fix Tab Order in Editor**
  ```jsx
  // Update: frontend/src/pages/EditorPageUltimate.jsx
  <div className="editor-container">
    <button tabIndex={1}>Save</button>
    <CodeEditor tabIndex={2} />
    <PreviewPanel tabIndex={3} />
  </div>
  ```

- [ ] **Add Arrow Key Navigation to Dropdowns**
  ```jsx
  // Update: frontend/src/components/ui/select.jsx
  const handleKeyDown = (e) => {
    switch(e.key) {
      case 'ArrowDown':
        e.preventDefault();
        focusNextItem();
        break;
      case 'ArrowUp':
        e.preventDefault();
        focusPreviousItem();
        break;
      case 'Enter':
      case ' ':
        e.preventDefault();
        selectCurrentItem();
        break;
      case 'Escape':
        closeDropdown();
        break;
    }
  };
  ```

- [ ] **Test Keyboard-Only Navigation**
  - Complete user flows without mouse
  - Check all forms can be submitted
  - Verify all buttons can be activated

---

### 1.4 Language Attributes

- [ ] **Add lang Attribute to HTML**
  ```html
  <!-- Update: frontend/public/index.html -->
  <!DOCTYPE html>
  <html lang="en">
    <head>
      <!-- ... -->
    </head>
    <body>
      <div id="root"></div>
    </body>
  </html>
  ```

- [ ] **Implement Dynamic Language Switching**
  ```jsx
  // Update: frontend/src/App.js
  import { useTranslation } from 'react-i18next';

  function App() {
    const { i18n } = useTranslation();

    useEffect(() => {
      document.documentElement.lang = i18n.language;
    }, [i18n.language]);

    return <Router>...</Router>;
  }
  ```

- [ ] **Add lang to Mixed-Language Content**
  ```jsx
  <div lang="fr">
    <p>Contenu en français</p>
  </div>
  <div lang="es">
    <p>Contenido en español</p>
  </div>
  ```

---

### 1.5 ARIA Live Regions

- [ ] **Add Aria-Live to Toast Notifications**
  ```jsx
  // Update: frontend/src/components/ui/toast.jsx
  const Toast = ({ title, description, variant }) => {
    return (
      <div
        role="status"
        aria-live="polite"
        aria-atomic="true"
        className="toast"
      >
        <div className="toast-title">{title}</div>
        {description && <div className="toast-description">{description}</div>}
      </div>
    );
  };
  ```

- [ ] **Add Status Messages to Forms**
  ```jsx
  // Example: Login form
  <form>
    <div>
      <label htmlFor="email">Email</label>
      <input
        id="email"
        type="email"
        aria-describedby="email-error"
        aria-invalid={!!errors.email}
      />
      {errors.email && (
        <span
          id="email-error"
          role="alert"
          aria-live="polite"
          className="error-message"
        >
          {errors.email}
        </span>
      )}
    </div>
  </form>
  ```

- [ ] **Add Live Region to Loading States**
  ```jsx
  const LoadingSpinner = ({ message = "Loading..." }) => {
    return (
      <div role="status" aria-live="polite" aria-busy="true">
        <span className="sr-only">{message}</span>
        <svg className="spinner" aria-hidden="true">...</svg>
      </div>
    );
  };
  ```

---

## Phase 2: High Priority Fixes (Week 2)

### 2.1 Form Accessibility

- [ ] **Add Proper Labels to Login Form**
  ```jsx
  // Update: frontend/src/pages/Login.jsx
  <form>
    <div className="form-group">
      <label htmlFor="login-email">Email Address</label>
      <input
        id="login-email"
        name="email"
        type="email"
        autoComplete="email"
        aria-describedby="email-hint"
        required
      />
      <span id="email-hint" className="hint">
        Enter your registered email
      </span>
    </div>

    <div className="form-group">
      <label htmlFor="login-password">Password</label>
      <input
        id="login-password"
        name="password"
        type="password"
        autoComplete="current-password"
        aria-describedby="password-hint"
        required
      />
      <span id="password-hint" className="hint">
        Your password is case-sensitive
      </span>
    </div>
  </form>
  ```

- [ ] **Add Autocomplete to Registration Form**
  ```jsx
  // Update: frontend/src/pages/Register.jsx
  <input
    id="reg-email"
    name="email"
    type="email"
    autoComplete="email"
  />
  <input
    id="reg-name"
    name="name"
    type="text"
    autoComplete="name"
  />
  <input
    id="reg-password"
    name="password"
    type="password"
    autoComplete="new-password"
  />
  ```

- [ ] **Add Field-Level Error Announcements**
  ```jsx
  const FormField = ({ id, label, error, ...props }) => {
    return (
      <div className="form-field">
        <label htmlFor={id}>{label}</label>
        <input
          id={id}
          aria-describedby={error ? `${id}-error` : undefined}
          aria-invalid={!!error}
          {...props}
        />
        {error && (
          <span
            id={`${id}-error`}
            role="alert"
            aria-live="polite"
            className="error"
          >
            {error}
          </span>
        )}
      </div>
    );
  };
  ```

- [ ] **Add Form-Level Success Messages**
  ```jsx
  const [submitStatus, setSubmitStatus] = useState(null);

  return (
    <form onSubmit={handleSubmit}>
      {submitStatus && (
        <div
          role="status"
          aria-live="polite"
          className={submitStatus.type}
        >
          {submitStatus.message}
        </div>
      )}
      {/* form fields */}
    </form>
  );
  ```

---

### 2.2 ARIA Labels and Attributes

- [ ] **Add ARIA Labels to Icon Buttons**
  ```jsx
  // Example: Navigation menu button
  <button
    aria-label="Open navigation menu"
    aria-expanded={isOpen}
    aria-controls="main-navigation"
  >
    <MenuIcon aria-hidden="true" />
  </button>
  ```

- [ ] **Fix Template Selector ARIA**
  ```jsx
  // Update: frontend/src/components/templates/TemplateSelector.jsx
  <div role="radiogroup" aria-labelledby="template-selector-label">
    <h2 id="template-selector-label">Choose a Template</h2>
    {templates.map((template) => (
      <div
        key={template.id}
        role="radio"
        aria-checked={selected === template.id}
        tabIndex={selected === template.id ? 0 : -1}
        onClick={() => setSelected(template.id)}
      >
        {template.name}
      </div>
    ))}
  </div>
  ```

- [ ] **Fix Editor Tabs ARIA**
  ```jsx
  // Update tab component
  <div role="tablist" aria-label="Editor views">
    <button
      role="tab"
      aria-selected={activeTab === 'code'}
      aria-controls="code-panel"
      id="code-tab"
      tabIndex={activeTab === 'code' ? 0 : -1}
    >
      Code
    </button>
    <button
      role="tab"
      aria-selected={activeTab === 'preview'}
      aria-controls="preview-panel"
      id="preview-tab"
      tabIndex={activeTab === 'preview' ? 0 : -1}
    >
      Preview
    </button>
  </div>

  <div
    role="tabpanel"
    id="code-panel"
    aria-labelledby="code-tab"
    hidden={activeTab !== 'code'}
  >
    {/* Code editor */}
  </div>
  ```

- [ ] **Add Alt Text to Images**
  ```jsx
  // Template thumbnails
  <img
    src={template.thumbnail}
    alt={`${template.name} - ${template.description}`}
  />

  // Decorative images
  <img src={decorative.svg} alt="" role="presentation" />
  ```

---

### 2.3 Skip Navigation

- [ ] **Add Skip to Main Content Link**
  ```jsx
  // Update: frontend/src/components/Navigation.jsx
  const Navigation = () => {
    return (
      <>
        <a href="#main-content" className="skip-link">
          Skip to main content
        </a>
        <nav>
          {/* navigation items */}
        </nav>
      </>
    );
  };
  ```

- [ ] **Add Skip Link Styles**
  ```css
  /* Add to: frontend/src/styles/accessibility.css */
  .skip-link {
    position: absolute;
    top: -40px;
    left: 0;
    background: #0066cc;
    color: white;
    padding: 8px 16px;
    text-decoration: none;
    font-weight: bold;
    z-index: 9999;
  }

  .skip-link:focus {
    top: 0;
  }
  ```

- [ ] **Add ID to Main Content**
  ```jsx
  // Update: All page components
  <main id="main-content" tabIndex={-1}>
    {/* page content */}
  </main>
  ```

---

### 2.4 Semantic HTML

- [ ] **Add Heading Hierarchy to Dashboard**
  ```jsx
  // Update: frontend/src/pages/Dashboard.jsx
  <main id="main-content">
    <h1>Dashboard</h1>

    <section>
      <h2>Recent Projects</h2>
      {/* projects list */}
    </section>

    <section>
      <h2>Quick Actions</h2>
      {/* actions */}
    </section>
  </main>
  ```

- [ ] **Add Landmark Roles**
  ```jsx
  <header role="banner">
    <nav role="navigation" aria-label="Main navigation">
      {/* nav items */}
    </nav>
  </header>

  <main role="main" id="main-content">
    {/* main content */}
  </main>

  <aside role="complementary" aria-label="Sidebar">
    {/* sidebar content */}
  </aside>

  <footer role="contentinfo">
    {/* footer content */}
  </footer>
  ```

- [ ] **Fix Heading Order in Editor**
  ```jsx
  // Update: frontend/src/pages/EditorPageUltimate.jsx
  <main>
    <h1 className="sr-only">Web Application Editor</h1>

    <section>
      <h2>Code Editor</h2>
      {/* editor */}
    </section>

    <section>
      <h2>Live Preview</h2>
      {/* preview */}
    </section>
  </main>
  ```

---

## Phase 3: Medium Priority (Week 3)

### 3.1 Reduced Motion Support

- [ ] **Add prefers-reduced-motion Styles**
  ```css
  /* Add to: frontend/src/styles/accessibility.css */

  @media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
      animation-duration: 0.01ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: 0.01ms !important;
      scroll-behavior: auto !important;
    }
  }
  ```

- [ ] **Update Component Animations**
  ```css
  .fade-in {
    animation: fadeIn 0.3s ease-in-out;
  }

  @media (prefers-reduced-motion: reduce) {
    .fade-in {
      animation: none;
      opacity: 1;
    }
  }
  ```

- [ ] **Add Reduced Motion Toggle**
  ```jsx
  // Add to: frontend/src/pages/SettingsPage.jsx
  const [reducedMotion, setReducedMotion] = useState(
    window.matchMedia('(prefers-reduced-motion: reduce)').matches
  );

  useEffect(() => {
    if (reducedMotion) {
      document.documentElement.classList.add('reduce-motion');
    } else {
      document.documentElement.classList.remove('reduce-motion');
    }
  }, [reducedMotion]);
  ```

---

### 3.2 Enhanced Error Handling

- [ ] **Add Specific Error Suggestions**
  ```jsx
  const getErrorMessage = (error) => {
    switch(error.code) {
      case 'INVALID_EMAIL':
        return 'Please enter a valid email address (e.g., user@example.com)';
      case 'WEAK_PASSWORD':
        return 'Password must contain at least 8 characters, 1 uppercase letter, and 1 number';
      case 'USER_NOT_FOUND':
        return 'No account found with this email. Try registering instead.';
      default:
        return error.message;
    }
  };
  ```

- [ ] **Add Confirmation Dialogs for Destructive Actions**
  ```jsx
  const DeleteProjectDialog = ({ project, onConfirm }) => {
    return (
      <AlertDialog>
        <AlertDialogContent role="alertdialog">
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Project?</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete "{project.name}"?
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={onConfirm}>
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    );
  };
  ```

- [ ] **Add Inline Validation Feedback**
  ```jsx
  const [emailValid, setEmailValid] = useState(null);

  const validateEmail = (email) => {
    const isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    setEmailValid(isValid);
  };

  return (
    <input
      type="email"
      onChange={(e) => validateEmail(e.target.value)}
      aria-describedby="email-validation"
      aria-invalid={emailValid === false}
    />
    {emailValid !== null && (
      <span
        id="email-validation"
        role="status"
        aria-live="polite"
      >
        {emailValid ? '✓ Valid email' : '✗ Invalid email format'}
      </span>
    )}
  );
  ```

---

### 3.3 Tooltip Improvements

- [ ] **Make Tooltips Keyboard Accessible**
  ```jsx
  // Update: frontend/src/components/ui/tooltip.jsx
  const Tooltip = ({ content, children }) => {
    const [isOpen, setIsOpen] = useState(false);

    return (
      <div className="tooltip-wrapper">
        <button
          onMouseEnter={() => setIsOpen(true)}
          onMouseLeave={() => setIsOpen(false)}
          onFocus={() => setIsOpen(true)}
          onBlur={() => setIsOpen(false)}
          aria-describedby="tooltip"
        >
          {children}
        </button>
        {isOpen && (
          <div
            id="tooltip"
            role="tooltip"
            className="tooltip-content"
          >
            {content}
          </div>
        )}
      </div>
    );
  };
  ```

- [ ] **Add Escape Key to Dismiss**
  ```jsx
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      return () => document.removeEventListener('keydown', handleEscape);
    }
  }, [isOpen]);
  ```

- [ ] **Ensure Tooltips Don't Disappear on Hover**
  ```jsx
  <div
    className="tooltip-content"
    onMouseEnter={() => setIsOpen(true)}
    onMouseLeave={() => setIsOpen(false)}
  >
    {content}
  </div>
  ```

---

## Testing Checklist

### Automated Testing

- [ ] **Run axe DevTools on All Pages**
  - Homepage
  - Dashboard
  - Editor
  - Login/Register
  - Settings
  - Admin Panel

- [ ] **Run Lighthouse Accessibility Audit**
  - Target score: 97+
  - Fix all flagged issues

- [ ] **Run WAVE Evaluation**
  - Verify ARIA implementation
  - Check heading structure

- [ ] **Run pa11y CI in Pipeline**
  ```json
  // Add to package.json
  "scripts": {
    "test:a11y": "pa11y-ci --sitemap http://localhost:3000/sitemap.xml"
  }
  ```

### Manual Testing

- [ ] **Keyboard Navigation Test**
  - Navigate entire app with Tab/Shift+Tab only
  - Activate all buttons with Enter/Space
  - Close all modals with Escape
  - Navigate dropdowns with arrow keys

- [ ] **Screen Reader Test (NVDA)**
  - Login flow
  - Create new project
  - Edit existing project
  - Navigate dashboard

- [ ] **Screen Reader Test (JAWS)**
  - Verify all content is announced
  - Check form labels are read correctly

- [ ] **Screen Reader Test (VoiceOver)**
  - Test on macOS/iOS
  - Verify gesture support

- [ ] **Zoom Test**
  - Zoom to 200% in browser
  - Verify no horizontal scrolling
  - Check text doesn't overlap
  - Ensure buttons remain clickable

- [ ] **Color Blindness Test**
  - Use Chrome DevTools vision deficiency simulation
  - Test: Protanopia, Deuteranopia, Tritanopia
  - Verify error states are distinguishable

- [ ] **High Contrast Mode Test**
  - Enable Windows High Contrast
  - Verify all content is visible
  - Check focus indicators are clear

---

## Documentation

- [ ] **Create Developer Guidelines**
  - File: `docs/ACCESSIBILITY_GUIDELINES.md`
  - Include code examples
  - Add to onboarding docs

- [ ] **Update Component Documentation**
  - Add accessibility notes to each component
  - Document required ARIA attributes
  - Include keyboard interaction patterns

- [ ] **Create Testing Guide**
  - How to test with screen readers
  - Keyboard testing checklist
  - Automated testing setup

---

## Success Criteria

### Quantitative Metrics

- ✅ Lighthouse Accessibility Score: 97+
- ✅ WCAG 2.1 AA Compliance: 100%
- ✅ Zero Critical Issues in axe DevTools
- ✅ All Pages Pass WAVE Evaluation
- ✅ Color Contrast: All text 4.5:1+, UI 3:1+

### Qualitative Metrics

- ✅ All user flows completable with keyboard only
- ✅ All content accessible to screen readers
- ✅ All forms have proper labels and error messages
- ✅ All images have appropriate alt text
- ✅ Focus indicators visible on all interactive elements

---

## Timeline

| Phase | Duration | Completion Date |
|-------|----------|-----------------|
| Phase 1: Critical Fixes | Week 1 | [Date] |
| Phase 2: High Priority | Week 2 | [Date] |
| Phase 3: Medium Priority | Week 3 | [Date] |
| Testing & QA | Week 4 | [Date] |
| Final Review | Week 5 | [Date] |

---

## Notes

- Update this checklist as you complete items
- Add any new issues discovered during implementation
- Document any deviations from the plan
- Share progress in team standups

**Last Updated:** December 9, 2025
