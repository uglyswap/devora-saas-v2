# Tests Documentation - Devora

## Vue d'Ensemble

Cette suite de tests complète assure la qualité et la fiabilité de la plateforme Devora SaaS.

### Statistiques
- **Total tests**: 115
- **Tests E2E**: 68
- **Tests unitaires**: 47
- **Coverage**: 84%
- **Temps d'exécution**: ~5 minutes

---

## Structure

```
tests/
├── e2e/                    # Tests End-to-End (Playwright)
│   ├── auth.spec.ts        # 24 tests - Authentication
│   ├── project-creation.spec.ts  # 22 tests - Projects & AI
│   ├── deployment.spec.ts  # 14 tests - Deployment
│   └── billing.spec.ts     # 8 tests - Stripe Billing
│
├── unit/                   # Tests Unitaires (Vitest)
│   ├── components/         # Tests composants React
│   ├── contexts/          # Tests contexts
│   └── hooks/             # Tests custom hooks
│
├── fixtures/              # Mock data & helpers
│   └── mockData.ts        # Données de test réutilisables
│
├── setup.ts               # Configuration globale tests
└── README.md              # Ce fichier
```

---

## Quick Start

### Installation

```bash
# Installer les dépendances
npm install

# Installer Playwright browsers
npx playwright install
```

### Lancer les Tests

```bash
# Tous les tests
npm test

# Tests unitaires seulement
npm run test:unit

# Tests E2E seulement
npm run test:e2e

# Tests avec UI interactive
npm run test:e2e:ui

# Tests en mode watch
npm run test:unit:watch

# Tests avec coverage
npm run test:unit:coverage
```

---

## Tests E2E (Playwright)

### Configuration

Le fichier `playwright.config.ts` configure:
- Multi-navigateurs: Chrome, Firefox, Safari
- Support mobile: iOS, Android
- Screenshots/vidéos automatiques sur échec
- Retry en CI
- Rapports HTML détaillés

### Auth Tests (auth.spec.ts)

**24 tests couvrant:**
- Registration flow
- Login flow
- Logout flow
- Session persistence
- Protected routes
- Password reset

**Exemple:**
```typescript
test('should successfully login', async ({ page }) => {
  await page.goto('/login');
  await page.fill('input[name="email"]', 'test@test.com');
  await page.fill('input[name="password"]', 'password');
  await page.click('button[type="submit"]');
  await page.waitForURL('/dashboard');
});
```

### Project Creation Tests (project-creation.spec.ts)

**22 tests couvrant:**
- Template selection
- AI code generation
- Code editor features
- Live preview
- Project management (save/load/delete)

### Deployment Tests (deployment.spec.ts)

**14 tests couvrant:**
- GitHub integration
- Repository configuration
- Deployment configuration
- Deploy process
- Deployment history
- Rollback

### Billing Tests (billing.spec.ts)

**8 tests couvrant:**
- Subscription plans
- Stripe checkout
- Subscription management
- Customer portal
- Cancellation flow
- Free trial

---

## Tests Unitaires (Vitest)

### Configuration

Le fichier `vitest.config.ts` configure:
- Environment jsdom pour React
- Coverage avec seuils à 84%
- Fast refresh
- Mocking automatique

### Component Tests

**ProtectedRoute.test.tsx**
- Authentication guards
- Subscription guards
- Admin guards
- Redirections

**Exemple:**
```typescript
it('should redirect to login if not authenticated', () => {
  const { result } = render(
    <ProtectedRoute>
      <div>Protected</div>
    </ProtectedRoute>
  );
  expect(mockNavigate).toHaveBeenCalledWith('/login');
});
```

### Context Tests

**AuthContext.test.tsx**
- Login/Logout
- Registration
- Session persistence
- Token refresh
- Error handling

### Hook Tests

**useProject.test.ts**
- CRUD operations
- Loading states
- Error handling

---

## Fixtures & Mocks

### Mock Data (`fixtures/mockData.ts`)

Données de test réutilisables:

```typescript
import {
  mockUser,
  mockProject,
  mockSubscription,
  mockInvoices,
  mockDeployment,
  mockPlans,
  mockTemplates
} from '@/tests/fixtures/mockData';

test('example', () => {
  const user = mockUser;
  // ...
});
```

**Disponible:**
- `mockUser` - Utilisateur test
- `mockAdminUser` - Admin test
- `mockProject` - Projet test
- `mockSubscription` - Abonnement
- `mockInvoices` - Factures
- `mockDeployment` - Déploiement
- `mockPlans` - Plans tarifaires
- `mockTemplates` - Templates
- `mockAuthTokens` - Tokens JWT
- `mockErrorResponses` - Erreurs API

---

## Best Practices

### Écrire un Test E2E

```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature Name', () => {
  test.beforeEach(async ({ page }) => {
    // Setup commun
    await page.goto('/');
  });

  test('should do something', async ({ page }) => {
    // Arrange
    await page.click('button#start');

    // Act
    await page.fill('input[name="field"]', 'value');
    await page.click('button[type="submit"]');

    // Assert
    await expect(page.locator('.success')).toBeVisible();
  });
});
```

### Écrire un Test Unitaire

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';

describe('Component', () => {
  it('should render correctly', () => {
    // Arrange
    render(<Component prop="value" />);

    // Assert
    expect(screen.getByText('value')).toBeInTheDocument();
  });

  it('should handle clicks', async () => {
    // Arrange
    const onClick = vi.fn();
    render(<Component onClick={onClick} />);

    // Act
    await userEvent.click(screen.getByRole('button'));

    // Assert
    expect(onClick).toHaveBeenCalledTimes(1);
  });
});
```

### Conventions de Nommage

**Fichiers:**
- E2E: `*.spec.ts`
- Unit: `*.test.ts` ou `*.test.tsx`

**Tests:**
```typescript
// ✅ Bon
test('should display error message when login fails')

// ❌ Mauvais
test('login error')
```

**Describe blocks:**
```typescript
// ✅ Bon
describe('AuthContext', () => {
  describe('Login', () => {
    it('should login successfully with valid credentials')
  })
})

// ❌ Mauvais
describe('tests', () => {
  it('test1')
})
```

---

## Debugging

### Playwright

```bash
# Mode debug interactif
npm run test:e2e:debug

# Run avec navigateur visible
npm run test:e2e:headed

# UI mode (recommandé)
npm run test:e2e:ui
```

**Dans le code:**
```typescript
// Pause et inspecter
await page.pause();

// Screenshots
await page.screenshot({ path: 'debug.png' });

// Console logs
page.on('console', msg => console.log(msg.text()));
```

### Vitest

```bash
# Watch mode
npm run test:unit:watch

# Debug avec VS Code
# Ajouter breakpoint et Run > Debug Test
```

**Dans le code:**
```typescript
// Console logs visibles
console.log('Debug:', value);

// Debugger breakpoint
debugger;
```

---

## CI/CD

### GitHub Actions

Le workflow `.github/workflows/ci.yml` exécute:
1. Lint & Format
2. TypeScript check
3. Unit tests avec coverage
4. Build
5. E2E tests
6. Security scans
7. Performance audit (Lighthouse)

**Status checks requis:**
- ✅ All tests pass
- ✅ Coverage ≥ 80%
- ✅ No linting errors
- ✅ Build succeeds

### Hooks Git

**Pre-commit:**
- Lint staged files
- Run tests sur fichiers modifiés

**Commit-msg:**
- Validate format: `type(scope): message`

---

## Coverage

### Objectifs

- **Global**: ≥ 84%
- **Statements**: ≥ 84%
- **Branches**: ≥ 84%
- **Functions**: ≥ 84%
- **Lines**: ≥ 84%

### Voir le Coverage

```bash
# Générer rapport
npm run test:unit:coverage

# Ouvrir rapport HTML
open coverage/index.html
```

### Fichiers Critiques

Doivent avoir ≥ 90% coverage:
- `AuthContext.jsx`
- `ProtectedRoute.jsx`
- `Billing.jsx`
- `stripe_service.py`
- `auth.py`

---

## Troubleshooting

### Problèmes Communs

**Tests E2E timeout:**
```bash
# Augmenter timeout dans playwright.config.ts
timeout: 60 * 1000, // 60 secondes
```

**Tests unitaires échouent:**
```bash
# Clear cache
npm run test:unit -- --clearCache

# Update snapshots
npm run test:unit -- -u
```

**Playwright browsers manquants:**
```bash
npx playwright install
```

**Port déjà utilisé:**
```bash
# Changer port dans playwright.config.ts
webServer: {
  url: 'http://localhost:3001'
}
```

---

## Ressources

### Documentation
- [Playwright Docs](https://playwright.dev)
- [Vitest Docs](https://vitest.dev)
- [Testing Library](https://testing-library.com)

### Guides Internes
- [CODE_REVIEW_GUIDE.md](../docs/CODE_REVIEW_GUIDE.md)
- [QA_SQUAD_DELIVERY.md](../docs/QA_SQUAD_DELIVERY.md)

### Support
- Issues: GitHub Issues
- Questions: Slack #qa-squad
- Reviews: Pull Requests

---

## Maintenance

### Ajouter un Nouveau Test

1. Créer le fichier dans le bon dossier
2. Suivre les conventions de nommage
3. Utiliser les fixtures existantes
4. Vérifier le coverage
5. Documenter si complexe

### Mettre à Jour les Tests

- Tests cassés après refactoring: Normal, mettre à jour
- Snapshots obsolètes: `npm run test:unit -- -u`
- Fixtures changées: Modifier `mockData.ts`

### Review Checklist

- [ ] Nouveaux tests pour nouvelles features
- [ ] Tests passent tous localement
- [ ] Coverage maintenu ≥ 84%
- [ ] Pas de tests flaky (intermittents)
- [ ] Temps d'exécution raisonnable

---

**Version**: 1.0
**Dernière mise à jour**: 2024-01-15
**Maintenu par**: QA Squad
