import { test, expect, Page } from '@playwright/test';

/**
 * Tests E2E pour le flux d'authentification
 * Couvre: Login, Register, Logout, Session persistence
 */

// Test data
const TEST_USER = {
  email: `test.user.${Date.now()}@devora.test`,
  password: 'TestPassword123!',
  name: 'Test User',
};

const EXISTING_USER = {
  email: 'existing@devora.test',
  password: 'ExistingPassword123!',
};

test.describe('Authentication Flow', () => {
  test.describe('User Registration', () => {
    test('should successfully register a new user', async ({ page }) => {
      await page.goto('/register');

      // Fill registration form
      await page.fill('input[name="name"]', TEST_USER.name);
      await page.fill('input[name="email"]', TEST_USER.email);
      await page.fill('input[name="password"]', TEST_USER.password);
      await page.fill('input[name="confirmPassword"]', TEST_USER.password);

      // Accept terms
      await page.check('input[type="checkbox"][name="acceptTerms"]');

      // Submit form
      await page.click('button[type="submit"]');

      // Should redirect to dashboard or billing
      await page.waitForURL(/\/(dashboard|billing)/);

      // Verify success message
      await expect(page.locator('text=Bienvenue')).toBeVisible({ timeout: 5000 });
    });

    test('should show validation errors for invalid inputs', async ({ page }) => {
      await page.goto('/register');

      // Submit empty form
      await page.click('button[type="submit"]');

      // Check for validation errors
      await expect(page.locator('text=/email.*requis/i')).toBeVisible();
      await expect(page.locator('text=/mot de passe.*requis/i')).toBeVisible();
    });

    test('should reject weak passwords', async ({ page }) => {
      await page.goto('/register');

      await page.fill('input[name="email"]', TEST_USER.email);
      await page.fill('input[name="password"]', '123'); // Weak password
      await page.fill('input[name="confirmPassword"]', '123');

      await page.click('button[type="submit"]');

      await expect(page.locator('text=/mot de passe.*faible/i')).toBeVisible();
    });

    test('should reject mismatched passwords', async ({ page }) => {
      await page.goto('/register');

      await page.fill('input[name="password"]', TEST_USER.password);
      await page.fill('input[name="confirmPassword"]', 'DifferentPassword123!');

      await page.click('button[type="submit"]');

      await expect(page.locator('text=/mots de passe.*correspondent pas/i')).toBeVisible();
    });

    test('should prevent duplicate email registration', async ({ page }) => {
      await page.goto('/register');

      await page.fill('input[name="email"]', EXISTING_USER.email);
      await page.fill('input[name="password"]', TEST_USER.password);
      await page.fill('input[name="confirmPassword"]', TEST_USER.password);
      await page.check('input[type="checkbox"][name="acceptTerms"]');

      await page.click('button[type="submit"]');

      await expect(page.locator('text=/email.*déjà.*utilisé/i')).toBeVisible();
    });
  });

  test.describe('User Login', () => {
    test('should successfully login with valid credentials', async ({ page }) => {
      await page.goto('/login');

      await page.fill('input[name="email"]', EXISTING_USER.email);
      await page.fill('input[name="password"]', EXISTING_USER.password);

      await page.click('button[type="submit"]');

      // Should redirect to dashboard
      await page.waitForURL('/dashboard');

      // Verify user is logged in
      await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
    });

    test('should show error for invalid credentials', async ({ page }) => {
      await page.goto('/login');

      await page.fill('input[name="email"]', 'wrong@email.com');
      await page.fill('input[name="password"]', 'WrongPassword123!');

      await page.click('button[type="submit"]');

      await expect(page.locator('text=/identifiants.*invalides/i')).toBeVisible();
    });

    test('should show validation for empty fields', async ({ page }) => {
      await page.goto('/login');

      await page.click('button[type="submit"]');

      await expect(page.locator('text=/email.*requis/i')).toBeVisible();
      await expect(page.locator('text=/mot de passe.*requis/i')).toBeVisible();
    });

    test('should have "Remember Me" functionality', async ({ page }) => {
      await page.goto('/login');

      await page.fill('input[name="email"]', EXISTING_USER.email);
      await page.fill('input[name="password"]', EXISTING_USER.password);
      await page.check('input[name="rememberMe"]');

      await page.click('button[type="submit"]');
      await page.waitForURL('/dashboard');

      // Verify persistent session cookie
      const cookies = await page.context().cookies();
      const sessionCookie = cookies.find(c => c.name.includes('session') || c.name.includes('token'));

      expect(sessionCookie).toBeDefined();
      // Should have long expiry if remember me is checked
      if (sessionCookie) {
        expect(sessionCookie.expires).toBeGreaterThan(Date.now() / 1000 + 86400); // > 24h
      }
    });
  });

  test.describe('User Logout', () => {
    test.beforeEach(async ({ page }) => {
      // Login before each logout test
      await page.goto('/login');
      await page.fill('input[name="email"]', EXISTING_USER.email);
      await page.fill('input[name="password"]', EXISTING_USER.password);
      await page.click('button[type="submit"]');
      await page.waitForURL('/dashboard');
    });

    test('should successfully logout user', async ({ page }) => {
      // Click user menu
      await page.click('[data-testid="user-menu"]');

      // Click logout
      await page.click('text=Déconnexion');

      // Should redirect to home or login
      await page.waitForURL(/\/(login|\/)/);

      // Verify user is logged out
      await expect(page.locator('text=Connexion')).toBeVisible();
    });

    test('should clear session on logout', async ({ page }) => {
      await page.click('[data-testid="user-menu"]');
      await page.click('text=Déconnexion');

      // Try to access protected route
      await page.goto('/dashboard');

      // Should redirect to login
      await page.waitForURL('/login');
    });

    test('should clear local storage on logout', async ({ page }) => {
      await page.click('[data-testid="user-menu"]');
      await page.click('text=Déconnexion');

      // Check that auth data is cleared
      const token = await page.evaluate(() => localStorage.getItem('token'));
      const user = await page.evaluate(() => localStorage.getItem('user'));

      expect(token).toBeNull();
      expect(user).toBeNull();
    });
  });

  test.describe('Session Persistence', () => {
    test('should maintain session across page reloads', async ({ page }) => {
      // Login
      await page.goto('/login');
      await page.fill('input[name="email"]', EXISTING_USER.email);
      await page.fill('input[name="password"]', EXISTING_USER.password);
      await page.click('button[type="submit"]');
      await page.waitForURL('/dashboard');

      // Reload page
      await page.reload();

      // User should still be logged in
      await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
      expect(page.url()).toContain('/dashboard');
    });

    test('should redirect to login when session expires', async ({ page }) => {
      await page.goto('/login');
      await page.fill('input[name="email"]', EXISTING_USER.email);
      await page.fill('input[name="password"]', EXISTING_USER.password);
      await page.click('button[type="submit"]');
      await page.waitForURL('/dashboard');

      // Simulate expired token
      await page.evaluate(() => {
        localStorage.setItem('token', 'expired.token.here');
      });

      // Navigate to protected route
      await page.goto('/editor');

      // Should redirect to login
      await page.waitForURL('/login');
    });
  });

  test.describe('Protected Routes', () => {
    test('should redirect unauthenticated users to login', async ({ page }) => {
      await page.goto('/dashboard');
      await page.waitForURL('/login');

      await page.goto('/editor');
      await page.waitForURL('/login');

      await page.goto('/settings');
      await page.waitForURL('/login');
    });

    test('should allow authenticated users to access protected routes', async ({ page }) => {
      // Login first
      await page.goto('/login');
      await page.fill('input[name="email"]', EXISTING_USER.email);
      await page.fill('input[name="password"]', EXISTING_USER.password);
      await page.click('button[type="submit"]');
      await page.waitForURL('/dashboard');

      // Access protected routes
      await page.goto('/editor');
      expect(page.url()).toContain('/editor');

      await page.goto('/settings');
      expect(page.url()).toContain('/settings');
    });
  });

  test.describe('Password Reset Flow', () => {
    test('should show forgot password link', async ({ page }) => {
      await page.goto('/login');
      await expect(page.locator('text=/mot de passe oublié/i')).toBeVisible();
    });

    test('should handle password reset request', async ({ page }) => {
      await page.goto('/login');
      await page.click('text=/mot de passe oublié/i');

      // Should navigate to reset page or show modal
      await page.fill('input[name="email"]', EXISTING_USER.email);
      await page.click('button:has-text("Envoyer")');

      await expect(page.locator('text=/email.*envoyé/i')).toBeVisible();
    });
  });
});
