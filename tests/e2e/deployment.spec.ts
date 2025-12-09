import { test, expect, Page } from '@playwright/test';

/**
 * Tests E2E pour le flux de déploiement
 * Couvre: GitHub integration, Deployment configuration, Deploy process
 */

async function loginAsUser(page: Page) {
  await page.goto('/login');
  await page.fill('input[name="email"]', 'test@devora.test');
  await page.fill('input[name="password"]', 'TestPassword123!');
  await page.click('button[type="submit"]');
  await page.waitForURL('/dashboard');
}

async function createTestProject(page: Page, projectName: string) {
  await page.goto('/editor');
  await page.fill('input[name="projectName"]', projectName);
  await page.locator('[data-testid="code-editor"]').click();
  await page.keyboard.type('<h1>Deployment Test</h1>');
  await page.click('button:has-text("Sauvegarder")');
  await expect(page.locator('text=/sauvegardé/i')).toBeVisible();
}

test.describe('Deployment Flow', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsUser(page);
  });

  test.describe('GitHub Integration', () => {
    test('should display GitHub connection option', async ({ page }) => {
      const projectName = `Deploy Project ${Date.now()}`;
      await createTestProject(page, projectName);

      // Navigate to deployment section
      await page.click('[data-testid="deploy-tab"]');

      await expect(page.locator('text=/connecter.*github/i')).toBeVisible();
    });

    test('should initiate GitHub OAuth flow', async ({ page }) => {
      const projectName = `GitHub Project ${Date.now()}`;
      await createTestProject(page, projectName);

      await page.click('[data-testid="deploy-tab"]');

      // Click connect GitHub
      const popupPromise = page.waitForEvent('popup');
      await page.click('button:has-text("Connecter GitHub")');

      const popup = await popupPromise;

      // Should redirect to GitHub OAuth
      await expect(popup).toHaveURL(/github\.com\/login\/oauth\/authorize/);
    });

    test('should show connected GitHub account', async ({ page }) => {
      // Assuming user already connected GitHub
      const projectName = `Connected Project ${Date.now()}`;
      await createTestProject(page, projectName);

      await page.click('[data-testid="deploy-tab"]');

      // Should show connected account
      await expect(page.locator('[data-testid="github-connected"]')).toBeVisible();
      await expect(page.locator('text=/connecté en tant que/i')).toBeVisible();
    });

    test('should allow disconnecting GitHub', async ({ page }) => {
      const projectName = `Disconnect Project ${Date.now()}`;
      await createTestProject(page, projectName);

      await page.click('[data-testid="deploy-tab"]');

      // Disconnect GitHub
      await page.click('button:has-text("Déconnecter")');

      // Confirm
      await page.click('button:has-text("Confirmer")');

      // Should show connect option again
      await expect(page.locator('button:has-text("Connecter GitHub")')).toBeVisible();
    });
  });

  test.describe('Repository Configuration', () => {
    test('should create new GitHub repository', async ({ page }) => {
      const projectName = `New Repo ${Date.now()}`;
      await createTestProject(page, projectName);

      await page.click('[data-testid="deploy-tab"]');

      // Select "Create new repository"
      await page.click('input[value="create-new"]');

      const repoName = `devora-${projectName.toLowerCase().replace(/\s+/g, '-')}`;
      await page.fill('input[name="repositoryName"]', repoName);

      // Set visibility
      await page.click('input[value="public"]');

      // Create repo
      await page.click('button:has-text("Créer le dépôt")');

      // Should show success
      await expect(page.locator('text=/dépôt créé avec succès/i')).toBeVisible({ timeout: 10000 });
    });

    test('should use existing GitHub repository', async ({ page }) => {
      const projectName = `Existing Repo ${Date.now()}`;
      await createTestProject(page, projectName);

      await page.click('[data-testid="deploy-tab"]');

      // Select "Use existing repository"
      await page.click('input[value="use-existing"]');

      // Select from dropdown
      await page.click('[data-testid="repo-select"]');
      await page.click('text=my-existing-repo');

      // Should show selected repo
      await expect(page.locator('text=my-existing-repo')).toBeVisible();
    });

    test('should validate repository name', async ({ page }) => {
      const projectName = `Invalid Repo ${Date.now()}`;
      await createTestProject(page, projectName);

      await page.click('[data-testid="deploy-tab"]');
      await page.click('input[value="create-new"]');

      // Try invalid characters
      await page.fill('input[name="repositoryName"]', 'Invalid Repo Name!@#');
      await page.click('button:has-text("Créer le dépôt")');

      await expect(page.locator('text=/nom.*invalide/i')).toBeVisible();
    });
  });

  test.describe('Deployment Configuration', () => {
    test('should configure deployment platform', async ({ page }) => {
      const projectName = `Platform Config ${Date.now()}`;
      await createTestProject(page, projectName);

      await page.click('[data-testid="deploy-tab"]');

      // Select deployment platform
      await expect(page.locator('text=/vercel/i')).toBeVisible();
      await expect(page.locator('text=/netlify/i')).toBeVisible();
      await expect(page.locator('text=/github pages/i')).toBeVisible();

      // Select Vercel
      await page.click('[data-platform="vercel"]');

      await expect(page.locator('[data-testid="platform-selected"]')).toHaveAttribute('data-platform', 'vercel');
    });

    test('should configure build settings', async ({ page }) => {
      const projectName = `Build Config ${Date.now()}`;
      await createTestProject(page, projectName);

      await page.click('[data-testid="deploy-tab"]');

      // Expand build settings
      await page.click('text=/paramètres de build/i');

      // Configure
      await page.fill('input[name="buildCommand"]', 'npm run build');
      await page.fill('input[name="outputDirectory"]', 'dist');

      await page.click('button:has-text("Sauvegarder")');

      await expect(page.locator('text=/configuration sauvegardée/i')).toBeVisible();
    });

    test('should configure environment variables', async ({ page }) => {
      const projectName = `Env Vars ${Date.now()}`;
      await createTestProject(page, projectName);

      await page.click('[data-testid="deploy-tab"]');

      // Add environment variable
      await page.click('button:has-text("Ajouter variable")');

      await page.fill('input[name="envKey"]', 'API_URL');
      await page.fill('input[name="envValue"]', 'https://api.example.com');

      await page.click('button:has-text("Ajouter")');

      // Should appear in list
      await expect(page.locator('text=API_URL')).toBeVisible();
    });

    test('should configure custom domain', async ({ page }) => {
      const projectName = `Custom Domain ${Date.now()}`;
      await createTestProject(page, projectName);

      await page.click('[data-testid="deploy-tab"]');

      // Custom domain section
      await page.click('text=/domaine personnalisé/i');

      await page.fill('input[name="customDomain"]', 'myapp.example.com');
      await page.click('button:has-text("Configurer")');

      // Should show DNS instructions
      await expect(page.locator('text=/configuration dns/i')).toBeVisible();
    });
  });

  test.describe('Deploy Process', () => {
    test('should successfully deploy project', async ({ page }) => {
      const projectName = `Deploy Success ${Date.now()}`;
      await createTestProject(page, projectName);

      await page.click('[data-testid="deploy-tab"]');

      // Configure minimal settings
      await page.click('[data-platform="vercel"]');

      // Click deploy
      await page.click('button:has-text("Déployer")');

      // Should show deployment progress
      await expect(page.locator('[data-testid="deploy-progress"]')).toBeVisible();
      await expect(page.locator('text=/déploiement en cours/i')).toBeVisible();

      // Wait for completion (max 2 minutes)
      await expect(page.locator('text=/déployé avec succès/i')).toBeVisible({ timeout: 120000 });

      // Should show deployment URL
      await expect(page.locator('[data-testid="deployment-url"]')).toBeVisible();
    });

    test('should show deployment logs', async ({ page }) => {
      const projectName = `Deploy Logs ${Date.now()}`;
      await createTestProject(page, projectName);

      await page.click('[data-testid="deploy-tab"]');
      await page.click('[data-platform="vercel"]');
      await page.click('button:has-text("Déployer")');

      // Open logs panel
      await page.click('button:has-text("Voir les logs")');

      // Should show log output
      await expect(page.locator('[data-testid="deployment-logs"]')).toBeVisible();

      const logs = await page.locator('[data-testid="deployment-logs"]').textContent();
      expect(logs).toBeTruthy();
    });

    test('should handle deployment failures gracefully', async ({ page }) => {
      const projectName = `Deploy Fail ${Date.now()}`;
      await createTestProject(page, projectName);

      await page.click('[data-testid="deploy-tab"]');

      // Simulate deployment failure (missing config or invalid setup)
      await page.click('button:has-text("Déployer")');

      // Should show error
      await expect(page.locator('text=/erreur.*déploiement/i')).toBeVisible({ timeout: 30000 });

      // Error details should be visible
      await expect(page.locator('[data-testid="deployment-error"]')).toBeVisible();
    });

    test('should allow canceling deployment', async ({ page }) => {
      const projectName = `Cancel Deploy ${Date.now()}`;
      await createTestProject(page, projectName);

      await page.click('[data-testid="deploy-tab"]');
      await page.click('[data-platform="vercel"]');
      await page.click('button:has-text("Déployer")');

      // Wait a moment then cancel
      await page.waitForTimeout(2000);
      await page.click('button:has-text("Annuler")');

      await expect(page.locator('text=/déploiement annulé/i')).toBeVisible();
    });

    test('should redeploy existing deployment', async ({ page }) => {
      const projectName = `Redeploy ${Date.now()}`;
      await createTestProject(page, projectName);

      // First deployment
      await page.click('[data-testid="deploy-tab"]');
      await page.click('[data-platform="vercel"]');
      await page.click('button:has-text("Déployer")');
      await expect(page.locator('text=/déployé avec succès/i')).toBeVisible({ timeout: 120000 });

      // Make a change
      await page.click('[data-testid="editor-tab"]');
      await page.locator('[data-testid="code-editor"]').click();
      await page.keyboard.type('<p>Updated content</p>');
      await page.click('button:has-text("Sauvegarder")');

      // Redeploy
      await page.click('[data-testid="deploy-tab"]');
      await page.click('button:has-text("Redéployer")');

      await expect(page.locator('text=/redéployé avec succès/i')).toBeVisible({ timeout: 120000 });
    });
  });

  test.describe('Deployment History', () => {
    test('should display deployment history', async ({ page }) => {
      const projectName = `Deploy History ${Date.now()}`;
      await createTestProject(page, projectName);

      // Deploy once
      await page.click('[data-testid="deploy-tab"]');
      await page.click('[data-platform="vercel"]');
      await page.click('button:has-text("Déployer")');
      await expect(page.locator('text=/déployé avec succès/i')).toBeVisible({ timeout: 120000 });

      // Check history
      await page.click('text=/historique/i');

      // Should show at least one deployment
      await expect(page.locator('[data-testid="deployment-item"]')).toBeVisible();
    });

    test('should show deployment details', async ({ page }) => {
      const projectName = `Deploy Details ${Date.now()}`;
      await createTestProject(page, projectName);

      await page.click('[data-testid="deploy-tab"]');
      await page.click('[data-platform="vercel"]');
      await page.click('button:has-text("Déployer")');
      await expect(page.locator('text=/déployé avec succès/i')).toBeVisible({ timeout: 120000 });

      // View details
      await page.click('text=/historique/i');
      await page.click('[data-testid="deployment-item"]');

      // Should show details
      await expect(page.locator('text=/durée/i')).toBeVisible();
      await expect(page.locator('text=/commit/i')).toBeVisible();
      await expect(page.locator('text=/url/i')).toBeVisible();
    });

    test('should rollback to previous deployment', async ({ page }) => {
      const projectName = `Rollback ${Date.now()}`;
      await createTestProject(page, projectName);

      // First deployment
      await page.click('[data-testid="deploy-tab"]');
      await page.click('[data-platform="vercel"]');
      await page.click('button:has-text("Déployer")');
      await expect(page.locator('text=/déployé avec succès/i')).toBeVisible({ timeout: 120000 });

      // Second deployment (with changes)
      await page.click('[data-testid="editor-tab"]');
      await page.locator('[data-testid="code-editor"]').click();
      await page.keyboard.type('<p>Version 2</p>');
      await page.click('button:has-text("Sauvegarder")');

      await page.click('[data-testid="deploy-tab"]');
      await page.click('button:has-text("Redéployer")');
      await expect(page.locator('text=/déployé avec succès/i')).toBeVisible({ timeout: 120000 });

      // Rollback to first deployment
      await page.click('text=/historique/i');
      const firstDeployment = page.locator('[data-testid="deployment-item"]').first();
      await firstDeployment.click();
      await page.click('button:has-text("Rollback")');

      await expect(page.locator('text=/rollback réussi/i')).toBeVisible();
    });
  });

  test.describe('Preview Deployments', () => {
    test('should create preview deployment for branch', async ({ page }) => {
      const projectName = `Preview Deploy ${Date.now()}`;
      await createTestProject(page, projectName);

      await page.click('[data-testid="deploy-tab"]');

      // Create preview deployment
      await page.click('button:has-text("Créer preview")');

      await page.fill('input[name="branchName"]', 'feature/test');
      await page.click('button:has-text("Déployer preview")');

      await expect(page.locator('text=/preview créé/i')).toBeVisible({ timeout: 120000 });

      // Should have separate preview URL
      await expect(page.locator('[data-testid="preview-url"]')).toBeVisible();
    });
  });
});
