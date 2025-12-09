"""
Test Engineer Agent - QA Squad

Agent spécialisé dans la génération et la gestion de tests automatisés.
Génère des tests E2E (Playwright), unitaires (Jest/Vitest), d'intégration,
calcule la couverture de code et crée des fixtures/mocks.

Author: Devora Orchestration System
Version: 1.0.0
"""

from typing import Dict, Any, List, Optional
import json
import re
from datetime import datetime

from orchestration.core.base_agent import BaseAgent, AgentConfig


class TestEngineerAgent(BaseAgent):
    """
    Agent Test Engineer pour la génération complète de tests automatisés.

    Cet agent est un expert en:
    - Génération de tests E2E avec Playwright (Page Object Model, fixtures, assertions robustes)
    - Création de tests unitaires Jest/Vitest (AAA pattern, mocking, snapshots)
    - Implémentation de tests d'intégration (MSW, contrats API, flows multi-composants)
    - Génération de fixtures et mocks réalistes et maintenables
    - Calcul et analyse de la couverture de code (statement, branch, function, line)
    - Stratégies de test (Test Pyramid, TDD, BDD)
    - Tests de régression pour prévenir les bugs récurrents

    Architecture:
        - Hérite de BaseAgent pour l'intégration LLM via OpenRouter
        - Implémente validate_input() pour valider les contextes de test
        - Implémente execute() pour générer les tests selon le type demandé
        - Implémente format_output() pour structurer les résultats

    Capabilities:
        - generate_e2e_tests(): Tests Playwright avec POM et best practices
        - generate_unit_tests(): Tests unitaires complets avec mocks
        - generate_integration_tests(): Tests d'intégration avec MSW
        - generate_fixtures(): Données de test réalistes et factories
        - calculate_coverage(): Analyse de couverture et gaps
        - create_test_strategy(): Stratégie de test complète (pyramid, CI/CD)
        - generate_regression_tests(): Tests pour bugs connus

    Attributes:
        config (AgentConfig): Configuration de l'agent (model, temperature, etc.)

    Example:
        >>> config = AgentConfig(
        ...     name="test_engineer",
        ...     model="anthropic/claude-3.5-sonnet",
        ...     api_key="your-key",
        ...     temperature=0.3  # Basse pour tests déterministes
        ... )
        >>> agent = TestEngineerAgent(config)
        >>> result = agent.run({
        ...     "type": "e2e",
        ...     "code": "...",
        ...     "user_flow": "Login → Dashboard → Logout"
        ... })
        >>> print(result["output"]["tests"])
    """

    # Prompt système ultra-détaillé (~550 lignes) définissant l'expertise complète
    SYSTEM_PROMPT = """Tu es un Test Engineer senior avec 15+ ans d'expérience en Quality Assurance et Test Automation.

## EXPERTISE PRINCIPALE

Tu es un expert reconnu internationalement en:

### 1. Testing Strategies & Philosophies

- **Test Pyramid**: 70% unit tests, 20% integration, 10% E2E - tu sais exactement comment équilibrer
- **TDD (Test-Driven Development)**: Red-Green-Refactor cycle, tests avant code
- **BDD (Behavior-Driven Development)**: Given-When-Then scenarios, Gherkin syntax
- **AAA Pattern**: Arrange-Act-Assert pour tests clairs et maintenables
- **Testing Trophy**: Alternative moderne à la pyramide, focus sur integration tests
- **Property-Based Testing**: Tests avec Hypothesis/fast-check pour edge cases automatiques
- **Mutation Testing**: Tester la qualité des tests eux-mêmes (Stryker)
- **Contract Testing**: Pact pour valider les contrats entre services

### 2. Test Frameworks & Tools - Expertise Approfondie

**Playwright (E2E Testing)**:
- Page Object Model (POM) pour maintenabilité maximale
- Auto-wait et auto-retry pour stabilité (pas de sleeps!)
- Cross-browser testing (Chromium, Firefox, WebKit)
- Mobile emulation et responsive testing
- Network interception et mocking
- Visual regression testing avec screenshots
- Parallel execution et sharding pour vitesse
- Trace viewer pour debugging
- Test generator et codegen
- CI/CD integration (GitHub Actions, GitLab CI)

**Jest/Vitest (Unit Testing)**:
- Mocking avancé (jest.fn, jest.mock, vi.mock)
- Snapshot testing intelligent (éviter over-snapshotting)
- Coverage reports détaillés (v8, istanbul)
- Custom matchers pour assertions métier
- Test suites organisées (describe, it, test.each)
- beforeEach/afterEach hooks pour setup/teardown
- Timer mocking (fake timers, advance time)
- Module mocking et dependency injection

**Testing Library (Component Testing)**:
- User-centric testing (queries par role, label, text)
- Accessibility-first approach (getByRole, getByLabelText)
- Async utilities (waitFor, findBy)
- User event simulation (userEvent.click, type, etc.)
- Custom render avec providers (Redux, Context, Router)

**MSW - Mock Service Worker (API Mocking)**:
- REST API handlers pour tests isolation
- GraphQL mocking
- Network delay simulation
- Error response testing
- Request intercepting et logging

**Cypress (Alternative E2E)**:
- Custom commands et chains
- Network stubbing et fixtures
- Time travel debugging
- Real-time reloading

### 3. Code Coverage Analysis - Expertise Métrique

**Coverage Types**:
- **Statement Coverage**: Chaque ligne exécutée au moins une fois
- **Branch Coverage**: Tous les if/else paths testés
- **Function Coverage**: Toutes les fonctions appelées
- **Line Coverage**: Toutes les lignes logiques couvertes
- **Path Coverage**: Toutes les combinaisons de branches (complexe mais idéal)

**Coverage Goals par Type de Code**:
- **Business Logic Critique**: 100% coverage OBLIGATOIRE
- **Utilities & Helpers**: 95%+ coverage
- **UI Components**: 80%+ coverage (focus sur logic, pas styling)
- **Config Files**: 50%+ coverage (souvent statiques)
- **Generated Code**: Peut être exclu
- **Types/Interfaces**: N/A (pas de runtime logic)

**Coverage Tools**:
- Istanbul/NYC: Standard industry pour coverage JS/TS
- v8 Coverage: Plus rapide, moins précis
- Codecov/Coveralls: Reporting et tracking dans le temps
- SonarQube: Quality gates avec coverage minimums

**Coverage Anti-Patterns à Éviter**:
- "Coverage pour coverage": Tests qui passent mais n'assertent rien
- Over-mocking: Mocker tellement qu'on ne teste plus rien de réel
- Snapshot overkill: Snapshots de gros objets qui cassent souvent
- Ignoring edge cases: 100% coverage mais sans tester les erreurs

### 4. Test Design Patterns - Architecture de Tests

**Page Object Model (POM)**:
```typescript
class LoginPage {
  constructor(private page: Page) {}

  async goto() { await this.page.goto('/login'); }
  async fillEmail(email: string) { await this.page.fill('[name="email"]', email); }
  async fillPassword(pwd: string) { await this.page.fill('[name="password"]', pwd); }
  async submit() { await this.page.click('button[type="submit"]'); }
  async login(email: string, pwd: string) {
    await this.fillEmail(email);
    await this.fillPassword(pwd);
    await this.submit();
  }
}
```

**Factory Pattern pour Fixtures**:
```typescript
const userFactory = (overrides = {}) => ({
  id: faker.datatype.uuid(),
  email: faker.internet.email(),
  name: faker.name.fullName(),
  createdAt: new Date(),
  ...overrides
});
```

**Builder Pattern pour Test Data**:
```typescript
class UserBuilder {
  private user = { name: '', email: '', role: 'user' };
  withName(name: string) { this.user.name = name; return this; }
  withEmail(email: string) { this.user.email = email; return this; }
  asAdmin() { this.user.role = 'admin'; return this; }
  build() { return this.user; }
}
```

**Custom Matchers**:
```typescript
expect.extend({
  toBeValidEmail(received) {
    const pass = /^[^@]+@[^@]+\\.[^@]+$/.test(received);
    return { pass, message: () => `Expected ${received} to be a valid email` };
  }
});
```

### 5. Test Maintenance & Anti-Flakiness

**Causes de Flaky Tests**:
- Race conditions (async non attendu)
- Dépendances externes (APIs, DB)
- Test order dependency
- Shared state entre tests
- Timing issues (sleeps, timeouts)
- Non-deterministic data (random, dates)

**Solutions Anti-Flaky**:
- **Auto-wait**: Utiliser Playwright auto-wait au lieu de sleeps
- **Isolation**: Chaque test doit être indépendant
- **Fixtures**: Données de test déterministes
- **Mocking**: Mocker les APIs externes avec MSW
- **Retry Logic**: Retry automatique pour tests E2E (max 3x)
- **Parallel Safe**: Tests qui peuvent runner en parallèle
- **Cleanup**: Proper teardown après chaque test

**Test Smells à Détecter**:
- Tests qui passent/échouent aléatoirement
- Tests qui dépendent de l'ordre d'exécution
- Tests avec des sleeps/waits arbitraires
- Tests de 200+ lignes (trop long)
- Duplication entre tests (manque de setup commun)
- Assertions faibles (expect(true).toBe(true))

### 6. CI/CD Integration & Performance

**Optimisation de Suite de Tests**:
- **Parallelization**: Runner tests en parallèle (jest --maxWorkers)
- **Sharding**: Distribuer tests sur plusieurs machines
- **Test Selection**: Runner seulement tests affectés (--changedSince)
- **Fail Fast**: Arrêter au premier échec en dev
- **Caching**: Cache node_modules, build artifacts
- **Incremental Testing**: Tester seulement ce qui a changé

**CI/CD Best Practices**:
```yaml
# GitHub Actions example
- name: Run Tests
  run: |
    npm run test:unit -- --coverage
    npm run test:integration
    npm run test:e2e -- --shard=${{ matrix.shardIndex }}/${{ matrix.shardTotal }}
  env:
    CI: true
```

**Coverage Gates**:
- Bloquer PR si coverage < threshold (ex: 80%)
- Alerter si coverage diminue vs base branch
- Exceptions pour legacy code (progressive improvement)

### 7. Test Data Management

**Fixtures Best Practices**:
- **Minimal Data**: Juste ce qui est nécessaire pour le test
- **Realistic Data**: Utiliser Faker.js pour données réalistes
- **Immutable**: Ne jamais modifier les fixtures partagées
- **Version Control**: Fixtures en JSON dans repo
- **Factories**: Fonctions pour générer fixtures avec overrides

**Database Testing**:
- **Test DB**: DB dédiée pour tests (SQLite in-memory pour vitesse)
- **Migrations**: Tester les migrations aussi
- **Seeding**: Seeds déterministes pour tests
- **Cleanup**: Reset DB après chaque test
- **Transactions**: Wrapper tests en transactions (auto-rollback)

### 8. Accessibility & Security Testing

**Accessibility Testing**:
- **axe-core**: Automated a11y testing dans tests E2E
- **WCAG Compliance**: Vérifier conformité WCAG 2.1 AA
- **Screen Reader Testing**: Tester navigation clavier et screen readers
- **Color Contrast**: Valider ratios de contraste

**Security Testing**:
- **OWASP Top 10**: Tester injections, XSS, CSRF
- **Authentication**: Tester flows auth, session management
- **Authorization**: Tester permissions, RBAC
- **Input Validation**: Tester avec inputs malicieux

### 9. Regression Testing Strategy

**Quand Créer Regression Tests**:
- Après CHAQUE bug fix (prévenir réintroduction)
- Pour features critiques (payment, auth, data integrity)
- Bugs de production (haute priorité)
- Edge cases découverts en production

**Structure Regression Test**:
```typescript
/**
 * REGRESSION TEST for Bug #1234
 *
 * BUG: User could checkout with empty cart
 * ROOT CAUSE: Missing validation in checkout flow
 * FIX: Added cart.items.length > 0 check
 * IMPACT: Payment errors, customer complaints
 * FIXED: 2024-01-15 by @developer
 */
test('should NOT allow checkout with empty cart', async () => {
  // Reproduce original bug scenario
  await cart.clear();
  const checkoutBtn = page.locator('[data-testid="checkout"]');

  // Assert bug is fixed
  await expect(checkoutBtn).toBeDisabled();

  // Try to force checkout via API
  const response = await request.post('/api/checkout');
  expect(response.status).toBe(400);
  expect(response.body.error).toContain('Cart is empty');
});
```

### 10. Advanced Testing Techniques

**Property-Based Testing**:
```typescript
// Au lieu de tester des cas spécifiques, tester des propriétés
fc.assert(
  fc.property(fc.integer(), fc.integer(), (a, b) => {
    return add(a, b) === add(b, a); // Commutativité
  })
);
```

**Mutation Testing**:
- Modifier le code source (mutations)
- Si tests passent encore, ils sont faibles
- Stryker pour JS/TS

**Visual Regression Testing**:
- Screenshot comparison (Percy, Chromatic)
- Détecter changements UI non intentionnels
- Cross-browser visual diffs

**Performance Testing**:
- Lighthouse CI dans tests E2E
- Bundle size testing
- Runtime performance benchmarks

## TON ROLE ET RESPONSABILITÉS

Quand on te demande de générer des tests, tu dois:

1. **Analyser le Code Profondément**:
   - Identifier TOUS les chemins d'exécution
   - Lister TOUS les edge cases possibles
   - Détecter les dépendances externes à mocker
   - Évaluer la complexité et les risques

2. **Concevoir la Stratégie de Test**:
   - Quel type de tests (unit, integration, E2E)?
   - Combien de tests (suivre la pyramide)?
   - Quelles données de test (fixtures)?
   - Quel niveau de coverage viser?

3. **Générer des Tests de Qualité Production**:
   - Code complet et exécutable immédiatement
   - Tous les imports nécessaires
   - Configuration si nécessaire
   - Commentaires pour logique complexe uniquement
   - Nommage descriptif (test names = documentation)
   - Assertions robustes et significatives

4. **Assurer la Maintenabilité**:
   - DRY: Extraire setup commun en beforeEach
   - POM pour E2E tests
   - Factories pour fixtures
   - Clear test organization

5. **Prévenir la Flakiness**:
   - Pas de sleeps/waits arbitraires
   - Auto-wait Playwright
   - Mocking des APIs externes
   - Données déterministes
   - Isolation complète

6. **Documenter les Tests**:
   - Docstrings pour test suites complexes
   - Commentaires pour business logic non évidente
   - README pour setup de test environment

## FORMAT DE SORTIE

Tes tests doivent TOUJOURS:
- Être du code 100% valide et exécutable
- Inclure tous les imports
- Suivre les conventions du framework (Jest/Vitest/Playwright)
- Avoir des noms de test descriptifs (pas de "test1", "test2")
- Utiliser les assertions appropriées
- Gérer les erreurs et edge cases
- Être performants (pas de timeouts excessifs)

## EXEMPLE DE QUALITÉ ATTENDUE

```typescript
// ✅ EXCELLENT TEST
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LoginForm } from './LoginForm';
import { authService } from '@/services/auth';

// Mock du service
vi.mock('@/services/auth');

describe('LoginForm', () => {
  const mockLogin = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    authService.login = mockLogin;
  });

  describe('Successful Login', () => {
    it('should login user and redirect to dashboard when credentials are valid', async () => {
      // Arrange
      const user = userEvent.setup();
      mockLogin.mockResolvedValue({ success: true, user: { id: '1', name: 'John' } });
      render(<LoginForm />);

      // Act
      await user.type(screen.getByLabelText(/email/i), 'john@example.com');
      await user.type(screen.getByLabelText(/password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /log in/i }));

      // Assert
      expect(mockLogin).toHaveBeenCalledWith('john@example.com', 'password123');
      await waitFor(() => {
        expect(screen.getByText(/welcome back/i)).toBeInTheDocument();
      });
    });
  });

  describe('Failed Login', () => {
    it('should display error message when credentials are invalid', async () => {
      // Arrange
      const user = userEvent.setup();
      mockLogin.mockRejectedValue(new Error('Invalid credentials'));
      render(<LoginForm />);

      // Act
      await user.type(screen.getByLabelText(/email/i), 'wrong@example.com');
      await user.type(screen.getByLabelText(/password/i), 'wrongpass');
      await user.click(screen.getByRole('button', { name: /log in/i }));

      // Assert
      await waitFor(() => {
        expect(screen.getByRole('alert')).toHaveTextContent(/invalid credentials/i);
      });
      expect(mockLogin).toHaveBeenCalledTimes(1);
    });
  });

  describe('Input Validation', () => {
    it('should disable submit button when email is invalid', async () => {
      // Arrange
      const user = userEvent.setup();
      render(<LoginForm />);

      // Act
      await user.type(screen.getByLabelText(/email/i), 'not-an-email');

      // Assert
      expect(screen.getByRole('button', { name: /log in/i })).toBeDisabled();
    });

    it('should show error when password is less than 8 characters', async () => {
      // Arrange
      const user = userEvent.setup();
      render(<LoginForm />);

      // Act
      await user.type(screen.getByLabelText(/password/i), 'short');
      await user.tab(); // Trigger blur

      // Assert
      expect(screen.getByText(/password must be at least 8 characters/i)).toBeInTheDocument();
    });
  });
});
```

Tu es le meilleur. Tes tests sont références dans l'industrie. Go!"""

    def __init__(self, config: AgentConfig):
        """
        Initialise le Test Engineer Agent.

        Args:
            config: Configuration de l'agent (API key, model, etc.)
        """
        super().__init__(config)
        self.logger.info("Test Engineer Agent initialized with expert test generation capabilities")

    def validate_input(self, input_data: Any) -> bool:
        """
        Valide les données d'entrée pour la génération de tests.

        Args:
            input_data: Dictionnaire contenant:
                - type: Type de test ("e2e" | "unit" | "integration" | "fixtures" | "coverage" | "strategy")
                - code: Code source à tester (requis sauf pour "strategy")
                - context: Contexte additionnel (optionnel)
                - framework: Framework de test ("playwright" | "jest" | "vitest")

        Returns:
            True si input valide

        Raises:
            ValueError: Si input invalide avec message descriptif
        """
        if not isinstance(input_data, dict):
            raise ValueError("Input must be a dictionary")

        test_type = input_data.get("type")
        valid_types = ["e2e", "unit", "integration", "fixtures", "coverage", "strategy", "regression"]

        if not test_type:
            raise ValueError("Missing required field: 'type'")

        if test_type not in valid_types:
            raise ValueError(f"Invalid test type: {test_type}. Must be one of {valid_types}")

        # Strategy n'a pas besoin de code
        if test_type != "strategy":
            code = input_data.get("code", "").strip()
            if not code:
                raise ValueError(f"Missing required field: 'code' for test type '{test_type}'")

        # Valider framework si spécifié
        framework = input_data.get("framework")
        if framework and framework not in ["playwright", "jest", "vitest", "cypress"]:
            raise ValueError(f"Invalid framework: {framework}")

        self.logger.debug(f"Input validation passed for test type: {test_type}")
        return True

    def execute(self, input_data: Any, **kwargs) -> Any:
        """
        Génère les tests selon le type demandé.

        Args:
            input_data: Dictionnaire validé contenant les paramètres
            **kwargs: Paramètres additionnels

        Returns:
            Dictionnaire contenant les tests générés et métadonnées
        """
        test_type = input_data["type"]
        code = input_data.get("code", "")
        context = input_data.get("context", "")
        framework = input_data.get("framework", "vitest")

        self.logger.info(f"Generating {test_type} tests with framework {framework}")

        # Construire le prompt utilisateur selon le type
        if test_type == "e2e":
            user_prompt = self._build_e2e_prompt(code, context)
        elif test_type == "unit":
            user_prompt = self._build_unit_prompt(code, framework, context)
        elif test_type == "integration":
            user_prompt = self._build_integration_prompt(code, context)
        elif test_type == "fixtures":
            user_prompt = self._build_fixtures_prompt(code, context)
        elif test_type == "coverage":
            user_prompt = self._build_coverage_prompt(code, context)
        elif test_type == "strategy":
            user_prompt = self._build_strategy_prompt(context)
        elif test_type == "regression":
            bug_description = input_data.get("bug_description", "")
            user_prompt = self._build_regression_prompt(code, bug_description, context)

        # Appeler le LLM
        response = self._call_llm(
            prompt=user_prompt,
            system_message=self.SYSTEM_PROMPT,
            temperature=kwargs.get("temperature", 0.3)  # Basse pour tests déterministes
        )

        return {
            "tests": response["content"],
            "test_type": test_type,
            "framework": framework,
            "model_used": response.get("model"),
            "tokens_used": response.get("usage", {})
        }

    def format_output(self, raw_output: Any) -> Dict[str, Any]:
        """
        Formate la sortie brute en structure standardisée.

        Args:
            raw_output: Sortie brute de execute()

        Returns:
            Dictionnaire formaté avec tests et métadonnées
        """
        return {
            "tests": raw_output["tests"],
            "metadata": {
                "test_type": raw_output["test_type"],
                "framework": raw_output["framework"],
                "model": raw_output.get("model_used"),
                "tokens": raw_output.get("tokens_used"),
                "generated_at": datetime.now().isoformat()
            },
            "recommendations": self._extract_recommendations(raw_output["tests"]),
            "coverage_analysis": self._analyze_coverage_from_tests(raw_output["tests"])
        }

    # ==================== PROMPT BUILDERS ====================

    def _build_e2e_prompt(self, code: str, context: str) -> str:
        """Construit le prompt pour tests E2E Playwright."""
        return f"""Génère une suite complète de tests E2E avec Playwright pour le code suivant.

CONTEXTE:
{context if context else "Application web moderne nécessitant des tests end-to-end complets"}

CODE À TESTER:
```
{code}
```

REQUIREMENTS:

1. **Utilise le Page Object Model (POM)** pour maximiser la maintenabilité
2. **Tests complets** couvrant:
   - Happy path (scénario nominal)
   - Edge cases (cas limites)
   - Error scenarios (gestion d'erreurs)
   - User flows critiques
3. **Assertions robustes** avec expect() et locators précis
4. **Auto-wait Playwright** - JAMAIS de page.waitForTimeout() ou sleeps
5. **Cross-browser compatible** (Chromium, Firefox, WebKit)
6. **Screenshots** on failure pour debugging
7. **Fixtures** pour données de test

STRUCTURE ATTENDUE:

```typescript
// pages/LoginPage.ts - Page Object Model
import {{ Page, Locator }} from '@playwright/test';

export class LoginPage {{
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;

  constructor(page: Page) {{
    this.page = page;
    this.emailInput = page.locator('[data-testid="email"]');
    // ... autres locators
  }}

  async goto() {{
    await this.page.goto('/login');
  }}

  async login(email: string, password: string) {{
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }}
}}

// tests/login.spec.ts - Tests E2E
import {{ test, expect }} from '@playwright/test';
import {{ LoginPage }} from '../pages/LoginPage';

test.describe('Login Flow', () => {{
  let loginPage: LoginPage;

  test.beforeEach(async ({{ page }}) => {{
    loginPage = new LoginPage(page);
    await loginPage.goto();
  }});

  test('should login successfully with valid credentials', async ({{ page }}) => {{
    // Test implementation
  }});

  test('should show error with invalid credentials', async ({{ page }}) => {{
    // Test implementation
  }});
}});
```

IMPORTANT:
- Code production-ready, exécutable immédiatement
- Tous les imports nécessaires
- Type annotations TypeScript
- Data-testid attributes pour locators robustes
- Pas de code TODO ou placeholder"""

    def _build_unit_prompt(self, code: str, framework: str, context: str) -> str:
        """Construit le prompt pour tests unitaires."""
        return f"""Génère des tests unitaires complets avec {framework.upper()} pour le code suivant.

CONTEXTE:
{context if context else "Tests unitaires pour fonctions/composants isolés"}

CODE À TESTER:
```
{code}
```

REQUIREMENTS:

1. **Coverage 100%** pour ce code:
   - Toutes les fonctions testées
   - Tous les if/else branches
   - Tous les edge cases
   - Toutes les erreurs possibles

2. **AAA Pattern** (Arrange-Act-Assert) strict:
   ```typescript
   it('should do X when Y', () => {{
     // Arrange: Setup
     const input = createTestData();
     const mock = vi.fn();

     // Act: Execute
     const result = functionToTest(input);

     // Assert: Verify
     expect(result).toBe(expected);
     expect(mock).toHaveBeenCalledWith(args);
   }});
   ```

3. **Mocking Approprié**:
   - Mock external dependencies (APIs, DB, modules)
   - Spy on functions pour vérifier appels
   - Stub timers si date/time logic
   - Mock fetch/axios pour HTTP requests

4. **Test Organization**:
   ```typescript
   describe('ModuleName', () => {{
     describe('functionName', () => {{
       it('should handle normal case', () => {{}});
       it('should handle edge case: empty input', () => {{}});
       it('should throw error when invalid', () => {{}});
     }});
   }});
   ```

5. **Best Practices**:
   - beforeEach pour reset mocks
   - Descriptive test names (no "test1", "test2")
   - One assertion per test (ou related assertions)
   - Fast tests (< 100ms each)

FRAMEWORK: {framework}

Génère:
- Tests complets avec tous les imports
- Configuration si nécessaire ({framework}.config.ts)
- Custom matchers si pertinent
- Test factories pour données complexes

CODE PRODUCTION-READY UNIQUEMENT."""

    def _build_integration_prompt(self, code: str, context: str) -> str:
        """Construit le prompt pour tests d'intégration."""
        return f"""Génère des tests d'intégration complets pour valider l'interaction entre composants/modules.

CONTEXTE:
{context if context else "Tests d'intégration pour valider les interactions entre modules"}

CODE À TESTER:
```
{code}
```

REQUIREMENTS:

1. **Test Real Interactions**:
   - Ne pas tout mocker (seulement external APIs)
   - Tester les vrais flows entre modules
   - Valider les contrats entre composants
   - Tester les side effects

2. **MSW pour API Mocking**:
   ```typescript
   import {{ setupServer }} from 'msw/node';
   import {{ rest }} from 'msw';

   const server = setupServer(
     rest.get('/api/users', (req, res, ctx) => {{
       return res(ctx.json({{ users: [...] }}));
     }})
   );

   beforeAll(() => server.listen());
   afterEach(() => server.resetHandlers());
   afterAll(() => server.close());
   ```

3. **Database Integration** (si applicable):
   - Test database ou in-memory DB
   - Migrations
   - Seeding avec données de test
   - Cleanup après chaque test

4. **Test Scenarios**:
   - User flows complets (multi-step)
   - Data persistence across operations
   - Error propagation entre layers
   - Transaction rollback scenarios

5. **Performance Considerations**:
   - Tests plus lents que unit tests (acceptable)
   - Mais < 5 secondes par test
   - Parallel execution safe

Génère des tests qui valident:
- API → Service → Repository flows
- Component → Hook → Context interactions
- Authentication → Authorization chains
- Event emission et handling

CODE COMPLET ET EXÉCUTABLE."""

    def _build_fixtures_prompt(self, code: str, context: str) -> str:
        """Construit le prompt pour génération de fixtures."""
        return f"""Génère des fixtures et factories pour les tests du code suivant.

CONTEXTE:
{context if context else "Génération de données de test réalistes et maintenables"}

CODE À TESTER:
```
{code}
```

REQUIREMENTS:

1. **Factory Pattern**:
   ```typescript
   import {{ faker }} from '@faker-js/faker';

   export const createUser = (overrides = {{}}) => ({{
     id: faker.datatype.uuid(),
     email: faker.internet.email(),
     name: faker.name.fullName(),
     createdAt: faker.date.past(),
     role: 'user',
     ...overrides
   }});

   // Usage
   const admin = createUser({{ role: 'admin' }});
   const specificUser = createUser({{ email: 'test@example.com' }});
   ```

2. **Builder Pattern** (pour objets complexes):
   ```typescript
   class UserBuilder {{
     private user = {{ name: '', email: '', preferences: {{}} }};

     withName(name: string) {{ this.user.name = name; return this; }}
     withEmail(email: string) {{ this.user.email = email; return this; }}
     withPreferences(prefs: any) {{ this.user.preferences = prefs; return this; }}

     build() {{ return this.user; }}
   }}

   // Usage
   const user = new UserBuilder()
     .withName('John')
     .withEmail('john@example.com')
     .build();
   ```

3. **Static Fixtures** (pour cas spécifiques):
   ```typescript
   // fixtures/users.json
   {{
     "validUser": {{ "id": "1", "email": "test@example.com" }},
     "adminUser": {{ "id": "2", "email": "admin@example.com", "role": "admin" }},
     "deletedUser": {{ "id": "3", "deletedAt": "2024-01-01" }}
   }}
   ```

4. **MSW Handlers**:
   ```typescript
   export const userHandlers = [
     rest.get('/api/users/:id', (req, res, ctx) => {{
       const {{ id }} = req.params;
       return res(ctx.json(createUser({{ id }})));
     }}),
     rest.post('/api/users', async (req, res, ctx) => {{
       const body = await req.json();
       return res(ctx.json(createUser(body)));
     }})
   ];
   ```

5. **Best Practices**:
   - Données réalistes (Faker.js)
   - Immutable factories (return new object)
   - Type-safe (TypeScript)
   - Documented (JSDoc comments)
   - Reusable across tests

Génère:
- Factories pour tous les types de données
- Builders pour objets complexes
- Static fixtures pour edge cases
- MSW handlers pour APIs
- Index file exportant tout

PRODUCTION-READY CODE."""

    def _build_coverage_prompt(self, code: str, context: str) -> str:
        """Construit le prompt pour analyse de coverage."""
        return f"""Analyse la couverture de code et identifie les gaps de testing.

CONTEXTE:
{context if context else "Analyse de coverage pour identifier les parties non testées"}

CODE À ANALYSER:
```
{code}
```

TÂCHES:

1. **Identifier Uncovered Lines**:
   - Lister toutes les lignes non couvertes
   - Prioriser par criticité (business logic > utilities > config)
   - Expliquer pourquoi elles ne sont pas testées

2. **Branch Coverage Analysis**:
   - Identifier les branches if/else non testées
   - Lister les edge cases manquants
   - Proposer les scénarios de test nécessaires

3. **Function Coverage**:
   - Fonctions jamais appelées dans les tests
   - Fonctions partiellement testées
   - Fonctions avec mocks uniquement (pas de vraie execution)

4. **Coverage Goals**:
   Définir les objectifs réalistes:
   - Business logic: 100%
   - Utilities: 95%
   - UI Components: 80%
   - Config: 50%

5. **Generate Missing Tests**:
   Pour chaque gap identifié, générer le test manquant:
   ```typescript
   // COVERAGE GAP: Line 45 - Error handling for invalid input
   it('should throw error when input is null', () => {{
     expect(() => myFunction(null)).toThrow('Input cannot be null');
   }});
   ```

FORMAT DE SORTIE:

```markdown
## Coverage Analysis Report

### Summary
- **Overall Coverage**: X%
- **Statements**: X/Y (Z%)
- **Branches**: X/Y (Z%)
- **Functions**: X/Y (Z%)
- **Lines**: X/Y (Z%)

### Critical Gaps (Business Logic)
1. **Line 45-50**: Error handling for payment processing
   - **Risk**: HIGH - Could lead to failed transactions
   - **Test Required**: Test with invalid payment method

### Missing Tests

\`\`\`typescript
// Generated tests to fill coverage gaps
describe('Coverage Gap Tests', () => {{
  // Tests here
}});
\`\`\`

### Recommendations
- [ ] Add integration tests for payment flow
- [ ] Test error scenarios in checkout
- [ ] Add E2E test for complete user journey
```

ANALYSE COMPLÈTE ET ACTIONNABLE."""

    def _build_strategy_prompt(self, context: str) -> str:
        """Construit le prompt pour stratégie de test."""
        return f"""Crée une stratégie de test complète et détaillée pour le projet.

CONTEXTE DU PROJET:
{context}

CRÉER UNE STRATÉGIE INCLUANT:

## 1. Test Pyramid Distribution

Définir la répartition optimale:
- **Unit Tests (70%)**: Quels composants/fonctions
- **Integration Tests (20%)**: Quelles intégrations
- **E2E Tests (10%)**: Quels user flows

Justifier chaque choix.

## 2. Coverage Goals

Par type de code:
- Business Logic: X% (justifier)
- API Endpoints: X%
- UI Components: X%
- Utilities: X%
- Config Files: X%

## 3. Test Types & Priorities

### Functional Tests
- Features critiques à tester
- Acceptance criteria
- User scenarios

### Regression Tests
- Bugs historiques à prévenir
- Critical paths

### Performance Tests
- Benchmarks à maintenir
- Load testing strategy
- Lighthouse CI thresholds

### Security Tests
- OWASP Top 10 checks
- Authentication flows
- Authorization rules
- Input validation

### Accessibility Tests
- WCAG 2.1 AA compliance
- Screen reader compatibility
- Keyboard navigation

## 4. CI/CD Integration

### Pre-commit
```bash
# Hooks à installer
npm run lint
npm run test:unit:changed
npm run typecheck
```

### Pull Request
```yaml
# GitHub Actions
- run: npm run test:unit -- --coverage
- run: npm run test:integration
- coverage threshold: 80%
```

### Staging
```yaml
- run: npm run test:e2e
- run: npm run test:accessibility
- run: lighthouse-ci
```

### Production
- Smoke tests
- Monitoring & alerting

## 5. Test Maintenance

### Anti-Flakiness
- Isolation strategies
- Mocking strategies
- Retry policies

### Organization
```
tests/
  unit/
    components/
    services/
    utils/
  integration/
    api/
    flows/
  e2e/
    pages/
    specs/
  fixtures/
  helpers/
```

### Conventions
- Naming: `*.spec.ts` ou `*.test.ts`
- Location: Co-located ou separate `tests/` folder
- Factories: `factories/*.ts`

## 6. Tools & Configuration

### Recommended Stack
- **Unit/Integration**: Vitest (faster) ou Jest
- **E2E**: Playwright (modern) ou Cypress
- **Mocking**: MSW pour APIs
- **Coverage**: v8 ou Istanbul
- **CI**: GitHub Actions

### Configuration Files
```typescript
// vitest.config.ts
export default defineConfig({{
  test: {{
    coverage: {{
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      lines: 80,
      branches: 75,
      functions: 80,
      statements: 80,
    }},
  }},
}});
```

## 7. Roadmap & Milestones

### Phase 1 (Week 1-2)
- [ ] Setup test infrastructure
- [ ] Unit tests for critical logic
- [ ] 50% coverage goal

### Phase 2 (Week 3-4)
- [ ] Integration tests
- [ ] E2E tests for main flows
- [ ] 70% coverage goal

### Phase 3 (Week 5-6)
- [ ] Full coverage (80%+)
- [ ] Performance tests
- [ ] Security tests
- [ ] CI/CD integration

### Phase 4 (Ongoing)
- [ ] Maintenance
- [ ] Regression tests for new bugs
- [ ] Refactoring

STRATÉGIE COMPLÈTE, ACTIONNABLE ET RÉALISTE."""

    def _build_regression_prompt(self, code: str, bug_description: str, context: str) -> str:
        """Construit le prompt pour tests de régression."""
        return f"""Génère des tests de régression pour prévenir la réintroduction d'un bug.

BUG DESCRIPTION:
{bug_description}

CONTEXTE:
{context if context else "Test de régression pour bug fix"}

CODE CONCERNÉ:
```
{code}
```

REQUIREMENTS:

1. **Documentation Complète**:
   ```typescript
   /**
    * REGRESSION TEST - Bug #ID
    *
    * BUG: [Description courte du bug original]
    * SEVERITY: CRITICAL | HIGH | MEDIUM | LOW
    * REPORTED: [Date] by [Reporter]
    * ROOT CAUSE: [Cause technique du bug]
    * FIX: [Comment le bug a été corrigé]
    * IMPACT: [Impact business/utilisateur]
    * RELATED ISSUES: [Liens vers issues/tickets]
    */
   ```

2. **Reproduire le Bug**:
   Le test doit:
   - Reproduire exactement le scénario du bug original
   - Utiliser les mêmes données qui ont causé le bug
   - Tester le chemin d'exécution problématique

3. **Valider le Fix**:
   ```typescript
   test('REGRESSION: should not [bug behavior]', async () => {{
     // Arrange: Setup qui causait le bug
     const problematicData = {{ ... }};

     // Act: Exécuter le code qui bugait
     const result = await functionThatWasBuggy(problematicData);

     // Assert: Vérifier que le bug ne se reproduit PAS
     expect(result).not.toBe(buggyBehavior);
     expect(result).toBe(expectedBehavior);

     // Assert: Vérifier les side effects
     expect(noUnwantedSideEffect).toBe(true);
   }});
   ```

4. **Edge Cases Liés**:
   Tester les variations du bug:
   - Conditions similaires qui pourraient causer le même bug
   - Edge cases découverts pendant l'investigation
   - Scenarios "presque identiques" au bug

5. **Assertions Robustes**:
   - Vérifier le comportement attendu
   - Vérifier qu'aucun effet secondaire indésirable
   - Vérifier les logs/événements si applicable

EXEMPLE:

```typescript
/**
 * REGRESSION TEST - Bug #1234
 *
 * BUG: Users could checkout with negative quantities
 * SEVERITY: CRITICAL
 * REPORTED: 2024-01-10 by Customer Support
 * ROOT CAUSE: Missing validation in cart.addItem()
 * FIX: Added quantity >= 1 check in validation
 * IMPACT: Revenue loss, inventory issues
 * RELATED ISSUES: #1235 (similar in wishlist)
 */
describe('REGRESSION: Cart Negative Quantity Bug #1234', () => {{
  it('should reject negative quantities in cart', () => {{
    // Arrange: Data that caused the original bug
    const cart = new Cart();
    const product = {{ id: '1', price: 10 }};

    // Act & Assert: Should throw error
    expect(() => {{
      cart.addItem(product, -5); // Original bug: this was allowed
    }}).toThrow('Quantity must be at least 1');
  }});

  it('should reject zero quantities', () => {{
    const cart = new Cart();
    expect(() => cart.addItem(product, 0)).toThrow();
  }});

  it('should accept positive quantities', () => {{
    const cart = new Cart();
    expect(() => cart.addItem(product, 1)).not.toThrow();
  }});
}});
```

Génère des tests de régression complets, documentés, et qui garantissent que ce bug ne reviendra JAMAIS."""

    # ==================== HELPER METHODS ====================

    def _extract_recommendations(self, tests: str) -> List[str]:
        """Extrait les recommandations depuis les tests générés."""
        recommendations = []

        # Chercher des patterns de recommandations dans les commentaires
        comment_pattern = r'//.*(?:TODO|FIXME|NOTE|RECOMMENDATION):\s*(.+)'
        matches = re.findall(comment_pattern, tests, re.IGNORECASE)
        recommendations.extend(matches)

        # Recommandations génériques basées sur le contenu
        if "faker" in tests.lower():
            recommendations.append("Install @faker-js/faker for realistic test data generation")
        if "msw" in tests.lower():
            recommendations.append("Install msw (Mock Service Worker) for API mocking")
        if "playwright" in tests.lower():
            recommendations.append("Install @playwright/test and configure browsers")
        if "testing-library" in tests.lower():
            recommendations.append("Install @testing-library/react and @testing-library/user-event")

        return recommendations[:5]  # Top 5 recommendations

    def _analyze_coverage_from_tests(self, tests: str) -> Dict[str, Any]:
        """Analyse basique de coverage depuis les tests générés."""
        # Compter les tests
        test_count = len(re.findall(r'\b(?:test|it)\s*\(', tests))
        describe_count = len(re.findall(r'\bdescribe\s*\(', tests))

        # Détecter les types de tests
        has_unit_tests = bool(re.search(r'from\s+[\'"]vitest[\'"]|from\s+[\'"]jest[\'"]', tests))
        has_e2e_tests = bool(re.search(r'from\s+[\'"]@playwright/test[\'"]', tests))
        has_mocks = bool(re.search(r'\bvi\.mock\(|\bjest\.mock\(|\bvi\.fn\(', tests))

        return {
            "test_count": test_count,
            "test_suites": describe_count,
            "estimated_coverage": "Unknown (run tests to get actual coverage)",
            "test_types": {
                "unit": has_unit_tests,
                "e2e": has_e2e_tests,
                "has_mocking": has_mocks
            },
            "quality_indicators": {
                "has_AAA_pattern": bool(re.search(r'// Arrange|// Act|// Assert', tests, re.IGNORECASE)),
                "has_descriptive_names": test_count > 0 and not bool(re.search(r'test[0-9]|it\([\'"]test', tests)),
                "uses_beforeEach": bool(re.search(r'\bbeforeEach\s*\(', tests))
            }
        }
