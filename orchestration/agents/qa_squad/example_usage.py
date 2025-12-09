"""
Example Usage - QA Squad Agents

Ce fichier démontre l'utilisation complète des agents du QA Squad:
- TestEngineerAgent: Génération de tests automatisés
- CodeReviewerAgent: Review de code automatique

Author: Devora Orchestration System
Version: 1.0.0
"""

import os
import asyncio
from orchestration.agents.qa_squad import TestEngineerAgent, CodeReviewerAgent
from orchestration.core.base_agent import AgentConfig


# ==================== CONFIGURATION ====================

def get_config(agent_name: str, temperature: float = 0.4) -> AgentConfig:
    """
    Crée une configuration pour un agent.

    Args:
        agent_name: Nom de l'agent
        temperature: Temperature du modèle (0.0-1.0)

    Returns:
        AgentConfig configuré
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable must be set")

    return AgentConfig(
        name=agent_name,
        model="anthropic/claude-3.5-sonnet",  # Meilleur modèle pour code
        api_key=api_key,
        temperature=temperature,
        max_tokens=8192,  # Plus élevé pour tests/reviews complets
        timeout=120,  # 2 minutes timeout
        log_level="INFO"
    )


# ==================== TEST ENGINEER EXAMPLES ====================

async def example_e2e_tests():
    """Exemple: Générer des tests E2E avec Playwright."""
    print("\n" + "="*80)
    print("EXAMPLE 1: Generating E2E Tests with Playwright")
    print("="*80)

    config = get_config("test_engineer_e2e", temperature=0.3)
    agent = TestEngineerAgent(config)

    code = """
    export function LoginPage() {
      const [email, setEmail] = useState('');
      const [password, setPassword] = useState('');
      const [error, setError] = useState('');

      const handleSubmit = async (e) => {
        e.preventDefault();
        try {
          await authService.login(email, password);
          router.push('/dashboard');
        } catch (err) {
          setError('Invalid credentials');
        }
      };

      return (
        <form onSubmit={handleSubmit}>
          <input
            data-testid="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            data-testid="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button type="submit">Log In</button>
          {error && <div role="alert">{error}</div>}
        </form>
      );
    }
    """

    result = agent.run({
        "type": "e2e",
        "code": code,
        "context": "Login page with email/password authentication",
        "framework": "playwright"
    })

    if result["status"] == "success":
        print("\n✅ E2E Tests Generated Successfully!")
        print(f"\nFramework: {result['output']['metadata']['framework']}")
        print(f"Test Count: {result['output']['coverage_analysis']['test_count']}")
        print(f"\n{result['output']['tests'][:500]}...")  # Preview
    else:
        print(f"\n❌ Error: {result['error']}")


async def example_unit_tests():
    """Exemple: Générer des tests unitaires avec Vitest."""
    print("\n" + "="*80)
    print("EXAMPLE 2: Generating Unit Tests with Vitest")
    print("="*80)

    config = get_config("test_engineer_unit", temperature=0.3)
    agent = TestEngineerAgent(config)

    code = """
    export function calculateShippingCost(
      weight: number,
      distance: number,
      expedited: boolean = false
    ): number {
      if (weight <= 0 || distance <= 0) {
        throw new Error('Weight and distance must be positive');
      }

      const baseCost = weight * 0.5 + distance * 0.1;
      const expeditedMultiplier = expedited ? 1.5 : 1;

      return Math.round(baseCost * expeditedMultiplier * 100) / 100;
    }
    """

    result = agent.run({
        "type": "unit",
        "code": code,
        "framework": "vitest",
        "context": "E-commerce shipping cost calculation"
    })

    if result["status"] == "success":
        print("\n✅ Unit Tests Generated Successfully!")
        print(f"\nRecommendations:")
        for rec in result['output']['recommendations']:
            print(f"  - {rec}")
        print(f"\n{result['output']['tests'][:800]}...")


async def example_fixtures():
    """Exemple: Générer des fixtures et factories."""
    print("\n" + "="*80)
    print("EXAMPLE 3: Generating Test Fixtures and Factories")
    print("="*80)

    config = get_config("test_engineer_fixtures", temperature=0.3)
    agent = TestEngineerAgent(config)

    code = """
    interface Product {
      id: string;
      name: string;
      description: string;
      price: number;
      category: string;
      inStock: boolean;
      images: string[];
      createdAt: Date;
      updatedAt: Date;
    }
    """

    result = agent.run({
        "type": "fixtures",
        "code": code,
        "context": "E-commerce product fixtures"
    })

    if result["status"] == "success":
        print("\n✅ Fixtures Generated Successfully!")
        print(f"\n{result['output']['tests'][:1000]}...")


async def example_test_strategy():
    """Exemple: Créer une stratégie de test complète."""
    print("\n" + "="*80)
    print("EXAMPLE 4: Creating Test Strategy")
    print("="*80)

    config = get_config("test_engineer_strategy", temperature=0.4)
    agent = TestEngineerAgent(config)

    result = agent.run({
        "type": "strategy",
        "context": """
        Project: SaaS platform for project management
        Stack: Next.js 14, TypeScript, Supabase, Stripe
        Features:
          - User authentication (email/password + OAuth)
          - Project management (CRUD, collaboration)
          - Task tracking (kanban, gantt)
          - File uploads (images, documents)
          - Real-time collaboration
          - Stripe payments (subscriptions)
          - Admin dashboard
        Team: 8 developers (4 frontend, 3 backend, 1 full-stack)
        Timeline: 6 months to MVP
        Quality goals: 80%+ coverage, zero critical bugs in production
        """
    })

    if result["status"] == "success":
        print("\n✅ Test Strategy Created Successfully!")
        print(f"\n{result['output']['tests'][:1500]}...")


# ==================== CODE REVIEWER EXAMPLES ====================

async def example_full_review():
    """Exemple: Review complète de code."""
    print("\n" + "="*80)
    print("EXAMPLE 5: Full Code Review")
    print("="*80)

    config = get_config("code_reviewer_full", temperature=0.4)
    agent = CodeReviewerAgent(config)

    code = """
    async function getUser(id) {
      const query = `SELECT * FROM users WHERE id = ${id}`;
      const result = await db.query(query);
      return result.rows[0];
    }

    async function updateUserEmail(userId, newEmail) {
      const user = await getUser(userId);
      user.email = newEmail;
      await db.query(`UPDATE users SET email = '${newEmail}' WHERE id = ${userId}`);
      return user;
    }
    """

    result = agent.run({
        "code": code,
        "language": "javascript",
        "focus": "all",
        "context": "User management API endpoints"
    })

    if result["status"] == "success":
        print("\n✅ Code Review Completed!")
        summary = result['output']['summary']
        print(f"\nSummary:")
        print(f"  - Total Issues: {summary['total_issues']}")
        print(f"  - Critical: {summary['critical']}")
        print(f"  - Major: {summary['major']}")
        print(f"  - Minor: {summary['minor']}")
        print(f"  - Suggestions: {summary['suggestions']}")

        print(f"\nDetailed Review:")
        print(f"{result['output']['review'][:2000]}...")


async def example_security_audit():
    """Exemple: Audit de sécurité ciblé."""
    print("\n" + "="*80)
    print("EXAMPLE 6: Security Audit")
    print("="*80)

    config = get_config("code_reviewer_security", temperature=0.3)
    agent = CodeReviewerAgent(config)

    code = """
    const API_KEY = "sk-1234567890abcdef";  // Hardcoded!

    app.post('/api/login', async (req, res) => {
      const { username, password } = req.body;

      // No validation!
      const user = await db.query(
        `SELECT * FROM users WHERE username = '${username}' AND password = '${password}'`
      );

      if (user) {
        const token = jwt.sign({ id: user.id }, API_KEY);
        res.json({ token, user });  // Exposing full user object!
      } else {
        res.status(401).json({ error: 'Login failed' });  // Vague error
      }
    });
    """

    result = agent.run({
        "code": code,
        "language": "javascript",
        "focus": "security"
    })

    if result["status"] == "success":
        print("\n✅ Security Audit Completed!")
        print(f"\n{result['output']['review'][:2000]}...")


async def example_performance_audit():
    """Exemple: Audit de performance."""
    print("\n" + "="*80)
    print("EXAMPLE 7: Performance Audit")
    print("="*80)

    config = get_config("code_reviewer_performance", temperature=0.4)
    agent = CodeReviewerAgent(config)

    code = """
    async function getUsersWithOrders(userId) {
      const users = await db.query('SELECT * FROM users');

      for (const user of users) {
        // N+1 problem!
        const orders = await db.query(`SELECT * FROM orders WHERE user_id = ${user.id}`);
        user.orders = orders;
      }

      // O(n²) filtering
      const filtered = [];
      for (let i = 0; i < users.length; i++) {
        for (let j = 0; j < users.length; j++) {
          if (users[i].email === users[j].email && i !== j) {
            filtered.push(users[i]);
          }
        }
      }

      return filtered;
    }
    """

    result = agent.run({
        "code": code,
        "language": "javascript",
        "focus": "performance"
    })

    if result["status"] == "success":
        print("\n✅ Performance Audit Completed!")
        print(f"\n{result['output']['review'][:2000]}...")


async def example_anti_patterns():
    """Exemple: Détection d'anti-patterns."""
    print("\n" + "="*80)
    print("EXAMPLE 8: Anti-Pattern Detection")
    print("="*80)

    config = get_config("code_reviewer_patterns", temperature=0.4)
    agent = CodeReviewerAgent(config)

    code = """
    class UserManager {
      // God Object anti-pattern
      constructor() {
        this.db = new Database();
        this.emailService = new EmailService();
        this.paymentService = new PaymentService();
      }

      // Long method (50+ lines)
      async createUser(data) {
        // Validate
        if (!data.email) throw new Error('Email required');
        if (!data.password) throw new Error('Password required');
        if (data.password.length < 8) throw new Error('Password too short');
        if (!data.name) throw new Error('Name required');

        // Hash password
        const salt = bcrypt.genSaltSync(10);
        const hash = bcrypt.hashSync(data.password, salt);

        // Create user
        const user = await this.db.query(
          'INSERT INTO users (email, password, name) VALUES ($1, $2, $3)',
          [data.email, hash, data.name]
        );

        // Send welcome email
        await this.emailService.send({
          to: user.email,
          subject: 'Welcome!',
          body: `Hi ${user.name}, welcome!`
        });

        // Create free subscription
        await this.paymentService.createSubscription({
          userId: user.id,
          plan: 'free'
        });

        // Log event
        await this.db.query(
          'INSERT INTO events (type, user_id) VALUES ($1, $2)',
          ['user_created', user.id]
        );

        return user;
      }

      // Duplicate code
      async updateUserEmail(userId, email) {
        if (!email) throw new Error('Email required');
        await this.db.query('UPDATE users SET email = $1 WHERE id = $2', [email, userId]);
      }

      async updateUserName(userId, name) {
        if (!name) throw new Error('Name required');
        await this.db.query('UPDATE users SET name = $1 WHERE id = $2', [name, userId]);
      }

      async updateUserPassword(userId, password) {
        if (!password) throw new Error('Password required');
        if (password.length < 8) throw new Error('Password too short');
        const hash = bcrypt.hashSync(password, 10);
        await this.db.query('UPDATE users SET password = $1 WHERE id = $2', [hash, userId]);
      }
    }
    """

    result = agent.run({
        "code": code,
        "language": "javascript",
        "focus": "anti-patterns"
    })

    if result["status"] == "success":
        print("\n✅ Anti-Pattern Detection Completed!")
        print(f"\n{result['output']['review'][:2000]}...")


# ==================== COMBINED WORKFLOW EXAMPLE ====================

async def example_full_qa_workflow():
    """Exemple: Workflow QA complet (review + tests)."""
    print("\n" + "="*80)
    print("EXAMPLE 9: Full QA Workflow (Review → Fix → Test)")
    print("="*80)

    # Step 1: Review du code
    print("\n📋 Step 1: Code Review...")
    reviewer = CodeReviewerAgent(get_config("reviewer", 0.4))

    original_code = """
    function calculateTotal(items) {
      let total = 0;
      for (let i = 0; i < items.length; i++) {
        total += items[i].price * items[i].quantity;
      }
      return total;
    }
    """

    review_result = reviewer.run({
        "code": original_code,
        "language": "javascript",
        "focus": "all"
    })

    if review_result["status"] == "success":
        print(f"✅ Review completed: {review_result['output']['summary']['total_issues']} issues found")

    # Step 2: Code "amélioré" basé sur review
    improved_code = """
    /**
     * Calculate total price for cart items
     * @param items - Array of cart items
     * @returns Total price in cents
     * @throws Error if items is not an array or contains invalid data
     */
    export function calculateTotal(items: CartItem[]): number {
      if (!Array.isArray(items)) {
        throw new Error('Items must be an array');
      }

      return items.reduce((total, item) => {
        if (typeof item.price !== 'number' || typeof item.quantity !== 'number') {
          throw new Error('Invalid item data');
        }

        if (item.price < 0 || item.quantity < 0) {
          throw new Error('Price and quantity must be positive');
        }

        return total + (item.price * item.quantity);
      }, 0);
    }
    """

    # Step 3: Générer des tests pour le code amélioré
    print("\n🧪 Step 2: Generating Tests for Improved Code...")
    tester = TestEngineerAgent(get_config("tester", 0.3))

    test_result = tester.run({
        "type": "unit",
        "code": improved_code,
        "framework": "vitest",
        "context": "E-commerce cart total calculation"
    })

    if test_result["status"] == "success":
        print(f"✅ Tests generated: {test_result['output']['coverage_analysis']['test_count']} tests")
        print(f"\n{test_result['output']['tests'][:1000]}...")

    print("\n✅ Full QA Workflow Completed!")


# ==================== MAIN EXECUTION ====================

async def main():
    """Exécute tous les exemples."""
    print("\n" + "="*80)
    print("QA SQUAD - EXAMPLE USAGE DEMONSTRATIONS")
    print("="*80)

    # Check API key
    if not os.getenv("OPENROUTER_API_KEY"):
        print("\n❌ ERROR: OPENROUTER_API_KEY environment variable not set!")
        print("Please set it with: export OPENROUTER_API_KEY='your-key'")
        return

    # Test Engineer Examples
    await example_e2e_tests()
    await asyncio.sleep(2)  # Rate limiting

    await example_unit_tests()
    await asyncio.sleep(2)

    await example_fixtures()
    await asyncio.sleep(2)

    await example_test_strategy()
    await asyncio.sleep(2)

    # Code Reviewer Examples
    await example_full_review()
    await asyncio.sleep(2)

    await example_security_audit()
    await asyncio.sleep(2)

    await example_performance_audit()
    await asyncio.sleep(2)

    await example_anti_patterns()
    await asyncio.sleep(2)

    # Combined Workflow
    await example_full_qa_workflow()

    print("\n" + "="*80)
    print("ALL EXAMPLES COMPLETED!")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())
