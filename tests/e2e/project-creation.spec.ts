import { test, expect, Page } from '@playwright/test';

/**
 * Tests E2E pour la création de projets et la génération de code
 * Couvre: Project creation, Code generation, Template selection, AI generation
 */

// Helper to login before tests
async function loginAsUser(page: Page) {
  await page.goto('/login');
  await page.fill('input[name="email"]', 'test@devora.test');
  await page.fill('input[name="password"]', 'TestPassword123!');
  await page.click('button[type="submit"]');
  await page.waitForURL('/dashboard');
}

test.describe('Project Creation Flow', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsUser(page);
  });

  test.describe('Dashboard Navigation', () => {
    test('should display dashboard with create project button', async ({ page }) => {
      await expect(page.locator('text=/créer.*projet/i')).toBeVisible();
      await expect(page.locator('text=/mes projets/i')).toBeVisible();
    });

    test('should navigate to unified editor on create project click', async ({ page }) => {
      await page.click('text=/créer.*projet/i');
      await page.waitForURL(/\/editor|\/create/);
    });
  });

  test.describe('Template Selection', () => {
    test('should display available templates', async ({ page }) => {
      await page.goto('/editor');

      // Should show template selection
      await expect(page.locator('text=/choisir.*template/i')).toBeVisible();

      // Common templates
      await expect(page.locator('text=/landing page/i')).toBeVisible();
      await expect(page.locator('text=/dashboard/i')).toBeVisible();
      await expect(page.locator('text=/e-commerce/i')).toBeVisible();
    });

    test('should preview template before selection', async ({ page }) => {
      await page.goto('/editor');

      // Click on a template
      await page.click('[data-template="landing-page"]');

      // Should show preview
      await expect(page.locator('[data-testid="template-preview"]')).toBeVisible();
    });

    test('should allow starting from blank template', async ({ page }) => {
      await page.goto('/editor');

      await page.click('text=/vierge|blank/i');

      // Should go to editor with blank canvas
      await expect(page.locator('[data-testid="code-editor"]')).toBeVisible();
      await expect(page.locator('[data-testid="preview-panel"]')).toBeVisible();
    });
  });

  test.describe('Project Configuration', () => {
    test('should allow configuring project name and description', async ({ page }) => {
      await page.goto('/editor');

      const projectName = `Test Project ${Date.now()}`;
      const projectDesc = 'This is a test project';

      await page.fill('input[name="projectName"]', projectName);
      await page.fill('textarea[name="projectDescription"]', projectDesc);

      // Save project
      await page.click('button:has-text("Sauvegarder")');

      // Verify saved
      await expect(page.locator(`text=${projectName}`)).toBeVisible();
    });

    test('should validate project name is required', async ({ page }) => {
      await page.goto('/editor');

      // Try to save without name
      await page.click('button:has-text("Sauvegarder")');

      await expect(page.locator('text=/nom.*requis/i')).toBeVisible();
    });
  });

  test.describe('AI Code Generation', () => {
    test('should generate code from natural language prompt', async ({ page }) => {
      await page.goto('/editor');

      // Enter AI prompt
      const prompt = 'Crée une landing page moderne avec un hero section et un formulaire de contact';
      await page.fill('[data-testid="ai-prompt-input"]', prompt);

      // Click generate
      await page.click('button:has-text("Générer")');

      // Should show loading state
      await expect(page.locator('[data-testid="generation-loading"]')).toBeVisible();

      // Wait for generation to complete (max 30s)
      await expect(page.locator('[data-testid="generation-loading"]')).toBeHidden({ timeout: 30000 });

      // Should have code in editor
      const editorContent = await page.locator('[data-testid="code-editor"]').textContent();
      expect(editorContent).toBeTruthy();
      expect(editorContent!.length).toBeGreaterThan(100);
    });

    test('should show error for invalid AI prompts', async ({ page }) => {
      await page.goto('/editor');

      // Empty prompt
      await page.click('button:has-text("Générer")');

      await expect(page.locator('text=/prompt.*requis/i')).toBeVisible();
    });

    test('should allow regenerating with different prompt', async ({ page }) => {
      await page.goto('/editor');

      // First generation
      await page.fill('[data-testid="ai-prompt-input"]', 'Create a simple button');
      await page.click('button:has-text("Générer")');
      await expect(page.locator('[data-testid="generation-loading"]')).toBeHidden({ timeout: 30000 });

      const firstContent = await page.locator('[data-testid="code-editor"]').textContent();

      // Second generation with different prompt
      await page.fill('[data-testid="ai-prompt-input"]', 'Create a complex form');
      await page.click('button:has-text("Générer")');
      await expect(page.locator('[data-testid="generation-loading"]')).toBeHidden({ timeout: 30000 });

      const secondContent = await page.locator('[data-testid="code-editor"]').textContent();

      // Content should be different
      expect(firstContent).not.toEqual(secondContent);
    });

    test('should handle AI generation errors gracefully', async ({ page }) => {
      await page.goto('/editor');

      // Simulate error by using invalid input or network failure
      await page.route('**/api/generate', (route) => {
        route.abort('failed');
      });

      await page.fill('[data-testid="ai-prompt-input"]', 'Test prompt');
      await page.click('button:has-text("Générer")');

      await expect(page.locator('text=/erreur.*génération/i')).toBeVisible({ timeout: 10000 });
    });
  });

  test.describe('Code Editor Features', () => {
    test('should display code editor with syntax highlighting', async ({ page }) => {
      await page.goto('/editor');

      await expect(page.locator('[data-testid="code-editor"]')).toBeVisible();

      // Type some code
      await page.locator('[data-testid="code-editor"]').click();
      await page.keyboard.type('<div>Hello World</div>');

      // Verify syntax highlighting (check for styled elements)
      const highlightedCode = await page.locator('.cm-tag, .token').count();
      expect(highlightedCode).toBeGreaterThan(0);
    });

    test('should support multiple file tabs', async ({ page }) => {
      await page.goto('/editor');

      // Should have at least index.html
      await expect(page.locator('[data-testid="file-tab-index.html"]')).toBeVisible();

      // Add new file
      await page.click('button:has-text("Nouveau fichier")');
      await page.fill('input[name="filename"]', 'styles.css');
      await page.click('button:has-text("Créer")');

      // Should now have two tabs
      await expect(page.locator('[data-testid="file-tab-styles.css"]')).toBeVisible();
    });

    test('should auto-save code changes', async ({ page }) => {
      await page.goto('/editor');

      // Make a change
      await page.locator('[data-testid="code-editor"]').click();
      await page.keyboard.type('<h1>Test</h1>');

      // Wait for auto-save indicator
      await expect(page.locator('text=/sauvegardé|saved/i')).toBeVisible({ timeout: 5000 });
    });
  });

  test.describe('Live Preview', () => {
    test('should display live preview of code', async ({ page }) => {
      await page.goto('/editor');

      // Write code
      await page.locator('[data-testid="code-editor"]').click();
      await page.keyboard.type('<h1 id="test-heading">Hello Devora</h1>');

      // Check preview panel
      const previewFrame = page.frameLocator('[data-testid="preview-iframe"]');
      await expect(previewFrame.locator('#test-heading')).toBeVisible({ timeout: 5000 });
      await expect(previewFrame.locator('text=Hello Devora')).toBeVisible();
    });

    test('should update preview in real-time', async ({ page }) => {
      await page.goto('/editor');

      const editor = page.locator('[data-testid="code-editor"]');
      const previewFrame = page.frameLocator('[data-testid="preview-iframe"]');

      // First update
      await editor.click();
      await page.keyboard.type('<p id="para1">First text</p>');
      await expect(previewFrame.locator('#para1')).toBeVisible({ timeout: 3000 });

      // Second update
      await page.keyboard.press('Enter');
      await page.keyboard.type('<p id="para2">Second text</p>');
      await expect(previewFrame.locator('#para2')).toBeVisible({ timeout: 3000 });
    });

    test('should toggle preview panel visibility', async ({ page }) => {
      await page.goto('/editor');

      // Preview should be visible by default
      await expect(page.locator('[data-testid="preview-panel"]')).toBeVisible();

      // Toggle off
      await page.click('[data-testid="toggle-preview"]');
      await expect(page.locator('[data-testid="preview-panel"]')).toBeHidden();

      // Toggle back on
      await page.click('[data-testid="toggle-preview"]');
      await expect(page.locator('[data-testid="preview-panel"]')).toBeVisible();
    });
  });

  test.describe('Project Management', () => {
    test('should save project and return to dashboard', async ({ page }) => {
      await page.goto('/editor');

      const projectName = `Saved Project ${Date.now()}`;
      await page.fill('input[name="projectName"]', projectName);

      await page.locator('[data-testid="code-editor"]').click();
      await page.keyboard.type('<h1>My Project</h1>');

      // Save and exit
      await page.click('button:has-text("Sauvegarder et quitter")');
      await page.waitForURL('/dashboard');

      // Verify project appears in dashboard
      await expect(page.locator(`text=${projectName}`)).toBeVisible();
    });

    test('should load existing project for editing', async ({ page }) => {
      // First, create and save a project
      await page.goto('/editor');
      const projectName = `Edit Project ${Date.now()}`;
      const projectCode = '<div>Original content</div>';

      await page.fill('input[name="projectName"]', projectName);
      await page.locator('[data-testid="code-editor"]').click();
      await page.keyboard.type(projectCode);
      await page.click('button:has-text("Sauvegarder")');
      await expect(page.locator('text=/sauvegardé/i')).toBeVisible();

      // Go back to dashboard
      await page.goto('/dashboard');

      // Find and open the project
      await page.click(`text=${projectName}`);

      // Should load in editor with saved content
      await page.waitForURL(/\/editor\//);
      await expect(page.locator('input[name="projectName"]')).toHaveValue(projectName);

      const editorContent = await page.locator('[data-testid="code-editor"]').textContent();
      expect(editorContent).toContain('Original content');
    });

    test('should delete project', async ({ page }) => {
      // Create a project first
      await page.goto('/editor');
      const projectName = `Delete Project ${Date.now()}`;
      await page.fill('input[name="projectName"]', projectName);
      await page.click('button:has-text("Sauvegarder")');
      await page.goto('/dashboard');

      // Delete project
      await page.hover(`text=${projectName}`);
      await page.click('[data-testid="delete-project"]');

      // Confirm deletion
      await page.click('button:has-text("Confirmer")');

      // Project should be removed
      await expect(page.locator(`text=${projectName}`)).toBeHidden();
    });
  });

  test.describe('Export and Download', () => {
    test('should export project as ZIP', async ({ page }) => {
      await page.goto('/editor');

      await page.fill('input[name="projectName"]', 'Export Test');
      await page.locator('[data-testid="code-editor"]').click();
      await page.keyboard.type('<h1>Export me</h1>');

      // Start download
      const downloadPromise = page.waitForEvent('download');
      await page.click('button:has-text("Exporter")');
      const download = await downloadPromise;

      // Verify download
      expect(download.suggestedFilename()).toMatch(/\.zip$/);
    });
  });
});
