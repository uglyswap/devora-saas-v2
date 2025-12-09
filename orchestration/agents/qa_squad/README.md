# QA Squad - Quality Assurance Agents

Squad d'agents spécialisés en Quality Assurance pour le système d'orchestration Devora.

## Vue d'ensemble

Le QA Squad fournit deux agents experts pour automatiser et améliorer la qualité du code:

### 1. **TestEngineerAgent** - Expert en Test Automation

Agent spécialisé dans la génération complète de tests automatisés de haute qualité.

**Capabilities**:
- ✅ Tests E2E avec Playwright (Page Object Model, auto-wait, cross-browser)
- ✅ Tests unitaires Jest/Vitest (AAA pattern, mocking avancé, coverage)
- ✅ Tests d'intégration (MSW pour API mocking, contrats)
- ✅ Génération de fixtures et factories (Factory pattern, Builder pattern)
- ✅ Analyse de couverture de code (statement, branch, function, line)
- ✅ Stratégies de test (Test Pyramid, TDD, BDD, CI/CD integration)
- ✅ Tests de régression (prévention de bugs récurrents)

**Expertise**:
- Test Pyramid et Testing Trophy
- Page Object Model (POM) pour E2E tests
- Mocking strategies (MSW, jest.mock, vi.mock)
- Coverage analysis et gap identification
- Anti-flaky test patterns
- Performance testing et benchmarks

### 2. **CodeReviewerAgent** - Expert en Code Quality

Agent spécialisé dans la review automatique de code et l'analyse de qualité.

**Capabilities**:
- 🔍 Review complète (lisibilité, maintenabilité, performance)
- 🔒 Audit de sécurité OWASP Top 10
- ⚡ Analyse de performance (complexité, bottlenecks, optimisations)
- 🏗️ Analyse architecturale (design patterns, anti-patterns)
- 🧼 Détection de code smells (duplication, complexité, etc.)
- ✨ Vérification best practices (SOLID, DRY, KISS, YAGNI)
- 🔧 Suggestions de refactoring avec exemples concrets

**Expertise**:
- SOLID principles
- OWASP Top 10 security vulnerabilities
- Code smells et anti-patterns (Bloaters, Couplers, etc.)
- Design patterns (Factory, Repository, Observer, etc.)
- Performance optimization (Big O, caching, indexing)
- Complexité cyclomatique et cognitive

## Installation

```bash
# Les agents sont déjà inclus dans orchestration/agents/qa_squad/
# Assurez-vous d'avoir les dépendances core installées:
pip install -r requirements.txt
```

## Configuration

Les deux agents utilisent `AgentConfig` du core:

```python
from orchestration.core.base_agent import AgentConfig

config = AgentConfig(
    name="agent_name",
    model="anthropic/claude-3.5-sonnet",  # ou autre modèle OpenRouter
    api_key="your-openrouter-api-key",
    temperature=0.3,  # 0.3 pour tests, 0.4 pour review
    max_tokens=4096,
    timeout=60,
    log_level="INFO"
)
```

## Usage

### TestEngineerAgent

#### Tests E2E (Playwright)

```python
from orchestration.agents.qa_squad import TestEngineerAgent
from orchestration.core.base_agent import AgentConfig

# Configuration
config = AgentConfig(
    name="test_engineer",
    model="anthropic/claude-3.5-sonnet",
    api_key="your-key",
    temperature=0.3  # Basse pour tests déterministes
)

# Initialiser l'agent
agent = TestEngineerAgent(config)

# Générer tests E2E
result = agent.run({
    "type": "e2e",
    "code": """
    // Code de votre application
    export function LoginPage() {
      // ...
    }
    """,
    "context": "User login flow avec email/password",
    "framework": "playwright"
})

# Récupérer les tests générés
tests = result["output"]["tests"]
print(tests)

# Métadonnées
print(f"Framework: {result['output']['metadata']['framework']}")
print(f"Test count: {result['output']['coverage_analysis']['test_count']}")
```

**Output exemple**:
```typescript
// pages/LoginPage.ts
import { Page, Locator } from '@playwright/test';

export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.locator('[data-testid="email"]');
    this.passwordInput = page.locator('[data-testid="password"]');
    this.submitButton = page.getByRole('button', { name: /log in/i });
    this.errorMessage = page.locator('[role="alert"]');
  }

  async goto() {
    await this.page.goto('/login');
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }
}

// tests/login.spec.ts
import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';

test.describe('Login Flow', () => {
  let loginPage: LoginPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    await loginPage.goto();
  });

  test('should login successfully with valid credentials', async ({ page }) => {
    // Arrange
    const validEmail = 'user@example.com';
    const validPassword = 'SecurePass123!';

    // Act
    await loginPage.login(validEmail, validPassword);

    // Assert
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
  });

  test('should show error with invalid credentials', async ({ page }) => {
    // Arrange
    const invalidEmail = 'wrong@example.com';
    const invalidPassword = 'wrongpass';

    // Act
    await loginPage.login(invalidEmail, invalidPassword);

    // Assert
    await expect(loginPage.errorMessage).toBeVisible();
    await expect(loginPage.errorMessage).toHaveText(/invalid credentials/i);
  });

  test('should disable submit button when fields are empty', async () => {
    // Assert
    await expect(loginPage.submitButton).toBeDisabled();
  });
});
```

#### Tests Unitaires (Vitest/Jest)

```python
result = agent.run({
    "type": "unit",
    "code": """
    export function calculateDiscount(price: number, discountPercent: number): number {
      if (price < 0 || discountPercent < 0 || discountPercent > 100) {
        throw new Error('Invalid input');
      }
      return price * (1 - discountPercent / 100);
    }
    """,
    "framework": "vitest",
    "context": "E-commerce discount calculation"
})

tests = result["output"]["tests"]
```

**Output exemple**:
```typescript
import { describe, it, expect } from 'vitest';
import { calculateDiscount } from './discount';

describe('calculateDiscount', () => {
  describe('Valid Inputs', () => {
    it('should calculate 10% discount correctly', () => {
      // Arrange
      const price = 100;
      const discount = 10;

      // Act
      const result = calculateDiscount(price, discount);

      // Assert
      expect(result).toBe(90);
    });

    it('should return original price with 0% discount', () => {
      expect(calculateDiscount(100, 0)).toBe(100);
    });

    it('should return 0 with 100% discount', () => {
      expect(calculateDiscount(100, 100)).toBe(0);
    });

    it('should handle decimal prices', () => {
      expect(calculateDiscount(99.99, 15)).toBeCloseTo(84.99, 2);
    });
  });

  describe('Invalid Inputs', () => {
    it('should throw error when price is negative', () => {
      expect(() => calculateDiscount(-10, 10)).toThrow('Invalid input');
    });

    it('should throw error when discount is negative', () => {
      expect(() => calculateDiscount(100, -5)).toThrow('Invalid input');
    });

    it('should throw error when discount > 100', () => {
      expect(() => calculateDiscount(100, 101)).toThrow('Invalid input');
    });
  });

  describe('Edge Cases', () => {
    it('should handle price = 0', () => {
      expect(calculateDiscount(0, 50)).toBe(0);
    });

    it('should handle very large prices', () => {
      const result = calculateDiscount(999999, 25);
      expect(result).toBe(749999.25);
    });
  });
});
```

#### Génération de Fixtures

```python
result = agent.run({
    "type": "fixtures",
    "code": """
    interface User {
      id: string;
      email: string;
      name: string;
      role: 'user' | 'admin';
      createdAt: Date;
    }
    """,
    "context": "User fixtures pour tests"
})
```

**Output exemple**:
```typescript
import { faker } from '@faker-js/faker';

// Factory Pattern pour génération flexible
export const createUser = (overrides = {}) => ({
  id: faker.datatype.uuid(),
  email: faker.internet.email(),
  name: faker.name.fullName(),
  role: 'user' as const,
  createdAt: faker.date.past(),
  ...overrides
});

// Builder Pattern pour objets complexes
export class UserBuilder {
  private user: Partial<User> = {
    id: faker.datatype.uuid(),
    email: faker.internet.email(),
    name: faker.name.fullName(),
    role: 'user',
    createdAt: new Date()
  };

  withId(id: string): UserBuilder {
    this.user.id = id;
    return this;
  }

  withEmail(email: string): UserBuilder {
    this.user.email = email;
    return this;
  }

  withName(name: string): UserBuilder {
    this.user.name = name;
    return this;
  }

  asAdmin(): UserBuilder {
    this.user.role = 'admin';
    return this;
  }

  build(): User {
    return this.user as User;
  }
}

// Static Fixtures pour cas spécifiques
export const fixtures = {
  validUser: {
    id: '1',
    email: 'user@example.com',
    name: 'John Doe',
    role: 'user' as const,
    createdAt: new Date('2024-01-01')
  },
  adminUser: {
    id: '2',
    email: 'admin@example.com',
    name: 'Admin User',
    role: 'admin' as const,
    createdAt: new Date('2023-01-01')
  }
};

// Usage Examples
const randomUser = createUser();
const specificUser = createUser({ email: 'test@example.com' });
const adminUser = new UserBuilder().withEmail('admin@test.com').asAdmin().build();
```

#### Analyse de Coverage

```python
result = agent.run({
    "type": "coverage",
    "code": """/* Votre code avec gaps de coverage */""",
    "context": "Identifier les parties non testées"
})

coverage = result["output"]["coverage_analysis"]
print(f"Gaps identifiés: {len(coverage.get('gaps', []))}")
```

#### Stratégie de Test

```python
result = agent.run({
    "type": "strategy",
    "context": """
    Projet: E-commerce platform
    Stack: Next.js, TypeScript, Supabase
    Features: Auth, Payments, Cart, Admin
    Team: 5 developers
    Timeline: 3 months
    """
})

strategy = result["output"]["tests"]
print(strategy)  # Document markdown complet avec roadmap
```

### CodeReviewerAgent

#### Review Complète

```python
from orchestration.agents.qa_squad import CodeReviewerAgent
from orchestration.core.base_agent import AgentConfig

# Configuration
config = AgentConfig(
    name="code_reviewer",
    model="anthropic/claude-3.5-sonnet",
    api_key="your-key",
    temperature=0.4  # Modérée pour review équilibrée
)

# Initialiser l'agent
agent = CodeReviewerAgent(config)

# Review complète
result = agent.run({
    "code": """
    async function getUserData(userId) {
      const query = `SELECT * FROM users WHERE id = ${userId}`;
      const result = await db.query(query);
      return result.rows[0];
    }
    """,
    "language": "javascript",
    "focus": "all"  # ou "security", "performance", "quality", "architecture"
})

# Récupérer la review
review = result["output"]["review"]
print(review)

# Résumé des issues
summary = result["output"]["summary"]
print(f"Total issues: {summary['total_issues']}")
print(f"Critical: {summary['critical']}")
print(f"Major: {summary['major']}")
print(f"Minor: {summary['minor']}")

# Issues détaillées
for issue in result["output"]["issues"]:
    print(f"{issue['severity'].upper()}: {issue['title']}")
    print(f"Location: {issue['location']}")
```

**Output exemple**:
```markdown
## Code Review Summary

**Overall Quality**: Poor
**Total Issues**: 5 (🔴 2 | 🟠 2 | 🟡 1 | 🟢 0)
**Complexity**: Low

---

## 🔴 CRITICAL Issues

### 1. SQL Injection Vulnerability
**Location**: line 2
**Severity**: CRITICAL
**OWASP Category**: A03:2021 – Injection
**Issue**: User input `userId` is directly concatenated into SQL query without sanitization
**Why**: An attacker can inject malicious SQL code to:
- Access unauthorized data
- Modify or delete database records
- Execute admin operations
- Compromise entire database

**Exploit Scenario**:
```javascript
// Attacker sends: userId = "1 OR 1=1"
// Resulting query: SELECT * FROM users WHERE id = 1 OR 1=1
// Returns ALL users instead of one!

// Worse: userId = "1; DROP TABLE users; --"
// Could delete entire users table!
```

**Fix**:
```javascript
// ❌ DANGEROUS - Current code
async function getUserData(userId) {
  const query = `SELECT * FROM users WHERE id = ${userId}`;
  const result = await db.query(query);
  return result.rows[0];
}

// ✅ SECURE - Parameterized query
async function getUserData(userId: string) {
  const query = 'SELECT * FROM users WHERE id = $1';
  const result = await db.query(query, [userId]);
  return result.rows[0];
}

// Even better with type safety and validation
async function getUserData(userId: string): Promise<User | null> {
  // Validate input
  if (!userId || typeof userId !== 'string') {
    throw new Error('Invalid userId');
  }

  // Parameterized query
  const query = 'SELECT id, email, name FROM users WHERE id = $1';
  const result = await db.query<User>(query, [userId]);

  return result.rows[0] || null;
}
```

**Reference**: https://owasp.org/www-community/attacks/SQL_Injection

---

### 2. Missing Error Handling
**Location**: line 1-5
**Severity**: CRITICAL
**Issue**: No try/catch block around database query
**Why**: Unhandled errors will crash the application or expose sensitive info
**Fix**:
```javascript
async function getUserData(userId: string): Promise<User | null> {
  try {
    const query = 'SELECT id, email, name FROM users WHERE id = $1';
    const result = await db.query<User>(query, [userId]);
    return result.rows[0] || null;
  } catch (error) {
    logger.error('Failed to fetch user', { userId, error });

    if (error.code === 'ECONNREFUSED') {
      throw new DatabaseConnectionError('Database unavailable');
    }

    throw new Error('Failed to fetch user data');
  }
}
```

---

## 🟠 MAJOR Issues

### 3. SELECT * Performance Issue
**Location**: line 2
**Severity**: MAJOR
**Issue**: Using `SELECT *` fetches all columns, even if not needed
**Why**:
- Network overhead (transfer unused data)
- Memory waste (store unused data)
- Security risk (expose sensitive fields like password_hash)
**Fix**:
```javascript
// ❌ SELECT * - fetches everything
const query = 'SELECT * FROM users WHERE id = $1';

// ✅ SELECT specific columns
const query = 'SELECT id, email, name, created_at FROM users WHERE id = $1';
```
**Performance Gain**: ~30-50% less data transfer for typical user table

---

### 4. No Input Validation
**Location**: line 1
**Severity**: MAJOR
**Issue**: No validation of `userId` parameter
**Why**: Could receive null, undefined, wrong type, etc.
**Fix**:
```typescript
async function getUserData(userId: string): Promise<User | null> {
  // Input validation
  if (!userId || typeof userId !== 'string') {
    throw new ValidationError('userId must be a non-empty string');
  }

  if (!isValidUUID(userId)) {
    throw new ValidationError('userId must be a valid UUID');
  }

  // ... rest of function
}
```

---

## 🟡 MINOR Issues

### 5. No Type Annotations
**Location**: line 1
**Severity**: MINOR
**Issue**: Function lacks TypeScript type annotations
**Why**: Reduces type safety, makes code harder to understand
**Fix**:
```typescript
// ❌ No types
async function getUserData(userId) {

// ✅ Fully typed
async function getUserData(userId: string): Promise<User | null> {
```

---

## ✅ What's Good

- Uses async/await (modern JavaScript)
- Function name is descriptive
- Simple and focused function

## 📊 Code Metrics

- Lines of Code: 5
- Functions: 1
- Complexity: Low (no branching)
- Type Safety: None (JavaScript, no types)

## 📚 Resources

- [OWASP Top 10](https://owasp.org/Top10/)
- [Node.js Security Best Practices](https://nodejs.org/en/docs/guides/security/)
- [SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
```

#### Audit de Sécurité Ciblé

```python
result = agent.run({
    "code": "/* Your code */",
    "language": "typescript",
    "focus": "security"  # Focus uniquement sur la sécurité
})
```

#### Analyse de Performance

```python
result = agent.run({
    "code": """
    function findDuplicates(arr) {
      const duplicates = [];
      for (let i = 0; i < arr.length; i++) {
        for (let j = i + 1; j < arr.length; j++) {
          if (arr[i] === arr[j] && !duplicates.includes(arr[i])) {
            duplicates.push(arr[i]);
          }
        }
      }
      return duplicates;
    }
    """,
    "language": "javascript",
    "focus": "performance"
})
```

**Output identifiera**: O(n³) complexity et suggérera Set-based O(n) solution.

#### Détection d'Anti-Patterns

```python
result = agent.run({
    "code": "/* Your code */",
    "focus": "anti-patterns"
})
```

## Types de Tests Supportés

### TestEngineerAgent

| Type | Description | Framework | Output |
|------|-------------|-----------|--------|
| `e2e` | Tests End-to-End | Playwright | POM + tests specs |
| `unit` | Tests Unitaires | Jest/Vitest | AAA pattern tests |
| `integration` | Tests d'Intégration | Vitest + MSW | Integration tests |
| `fixtures` | Fixtures & Factories | Faker.js | Factories & builders |
| `coverage` | Analyse Coverage | - | Gap analysis + tests manquants |
| `strategy` | Stratégie de Test | - | Test strategy doc |
| `regression` | Tests de Régression | Playwright/Vitest | Regression tests |

### CodeReviewerAgent

| Focus | Description | Output |
|-------|-------------|--------|
| `all` | Review complète | Sécurité + Performance + Qualité + Architecture |
| `security` | Audit sécurité | OWASP Top 10 analysis |
| `performance` | Audit performance | Big O, bottlenecks, optimizations |
| `quality` | Qualité code | SOLID, DRY, KISS, smells |
| `architecture` | Architecture | Design patterns, anti-patterns |
| `anti-patterns` | Code smells | Bloaters, Couplers, etc. |

## Best Practices

### Pour les Tests

1. **Tests E2E**: Utiliser Page Object Model (POM) pour maintenabilité
2. **Tests Unitaires**: Suivre AAA pattern (Arrange-Act-Assert)
3. **Fixtures**: Factory pattern pour flexibilité, Builder pour complexité
4. **Coverage**: Viser 80%+ mais privilégier qualité > quantité
5. **Anti-Flaky**: Pas de sleeps, utiliser auto-wait Playwright

### Pour la Review

1. **Security First**: Toujours commencer par audit sécurité
2. **Prioriser**: Fix les CRITICAL avant MAJOR avant MINOR
3. **Mesurer**: Utiliser métriques (complexité, coverage) pour tracking
4. **Apprendre**: Lire les références OWASP, Clean Code, etc.
5. **Itérer**: Review régulière, pas seulement en fin de projet

## Intégration CI/CD

### GitHub Actions Example

```yaml
name: QA Automation

on: [pull_request]

jobs:
  code-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run Code Review
        env:
          OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
        run: |
          python scripts/auto_review.py \
            --files-changed "$(git diff --name-only origin/main...HEAD)" \
            --output review-report.md

      - name: Comment PR with Review
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const review = fs.readFileSync('review-report.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: review
            });
```

## Métriques et KPIs

### Test Quality Metrics

- **Test Coverage**: Statement, Branch, Function, Line coverage
- **Test Count**: Total tests, par type (unit/integration/e2e)
- **Test Performance**: Temps d'exécution moyen, tests flaky
- **Test Maintenance**: Nombre de tests à update par changement de code

### Code Quality Metrics

- **Issue Severity Distribution**: Critical, Major, Minor, Suggestions
- **Complexity**: Cyclomatique moyenne, max par fonction
- **Code Smells**: Count par catégorie (Bloaters, Couplers, etc.)
- **Security**: Vulnérabilités par catégorie OWASP
- **Refactoring Opportunities**: Count et estimation effort

## Troubleshooting

### Tests ne se génèrent pas correctement

```python
# Augmenter max_tokens si tests tronqués
config.max_tokens = 8192

# Baisser temperature pour plus de déterminisme
config.temperature = 0.2
```

### Review trop générique

```python
# Fournir plus de contexte
result = agent.run({
    "code": code,
    "context": """
    Context détaillé:
    - Framework utilisé: Next.js 14
    - Database: PostgreSQL avec Prisma
    - Auth: NextAuth.js
    - Ce code gère les paiements Stripe
    """
})
```

### API timeouts

```python
# Augmenter timeout
config.timeout = 120  # 2 minutes
```

## Contributing

Pour contribuer au QA Squad:

1. Fork le repo
2. Créer une branch (`git checkout -b feature/amazing-feature`)
3. Commit (`git commit -m 'Add amazing feature'`)
4. Push (`git push origin feature/amazing-feature`)
5. Ouvrir une Pull Request

## License

MIT License - Voir LICENSE file pour détails.

## Support

- **Documentation**: [Devora Docs](https://devora.dev/docs)
- **Issues**: [GitHub Issues](https://github.com/devora/orchestration/issues)
- **Discord**: [Devora Community](https://discord.gg/devora)

---

**Version**: 1.0.0
**Last Updated**: 2024-12-09
**Maintainers**: Devora Team
