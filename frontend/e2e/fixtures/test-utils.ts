import { Page, expect } from '@playwright/test';

/**
 * Test Utilities and Helpers for Devora E2E Tests
 */

/**
 * Wait for WebContainer to be ready
 */
export async function waitForWebContainer(page: Page, timeout = 180000): Promise<void> {
  await page.waitForSelector(
    '[data-testid="webcontainer-status"]:has-text("ready")',
    { timeout }
  ).catch(() => {
    console.log('WebContainer status not found, continuing...');
  });
}

/**
 * Navigate to editor with specific template
 */
export async function openEditorWithTemplate(
  page: Page,
  template: 'react' | 'nextjs' | 'vue' | 'html' = 'react'
): Promise<void> {
  await page.goto(`/editor?template=${template}`);
  await page.waitForLoadState('networkidle');
}

/**
 * Enable select mode
 */
export async function enableSelectMode(page: Page): Promise<void> {
  const selectModeButton = page.locator('[data-testid="select-mode-toggle"]');
  if (await selectModeButton.isVisible()) {
    await selectModeButton.click();
    await expect(selectModeButton).toHaveAttribute('data-active', 'true');
  }
}

/**
 * Select an element in the preview iframe
 */
export async function selectElementInPreview(
  page: Page,
  selector: string
): Promise<boolean> {
  await enableSelectMode(page);

  const iframe = page.locator('[data-testid="preview-iframe"]');
  const frame = iframe.contentFrame();

  if (frame) {
    const element = frame.locator(selector).first();
    if (await element.isVisible()) {
      await element.click();
      return true;
    }
  }
  return false;
}

/**
 * Open deploy panel
 */
export async function openDeployPanel(page: Page): Promise<void> {
  const deployButton = page.locator('[data-testid="deploy-button"]');
  await deployButton.click();
  await expect(page.locator('[data-testid="deploy-panel"]')).toBeVisible();
}

/**
 * Select a deploy provider
 */
export async function selectDeployProvider(
  page: Page,
  provider: 'vercel' | 'netlify' | 'cloudflare'
): Promise<void> {
  await openDeployPanel(page);
  const providerOption = page.locator(`[data-testid="provider-${provider}"]`);
  await providerOption.click();
  await expect(providerOption).toHaveAttribute('data-selected', 'true');
}

/**
 * Type in Monaco editor
 */
export async function typeInEditor(page: Page, text: string): Promise<void> {
  const editor = page.locator('.monaco-editor textarea');
  if (await editor.isVisible()) {
    await editor.focus();
    await page.keyboard.type(text);
  }
}

/**
 * Save current file
 */
export async function saveFile(page: Page): Promise<void> {
  await page.keyboard.press('Control+s');
  // Wait for save indicator
  await page.waitForTimeout(500);
}

/**
 * Open file in editor
 */
export async function openFile(page: Page, fileName: string): Promise<boolean> {
  const file = page.locator('[data-testid="file-item"]').filter({ hasText: fileName });
  if (await file.isVisible()) {
    await file.click();
    return true;
  }
  return false;
}

/**
 * Send a message in chat
 */
export async function sendChatMessage(page: Page, message: string): Promise<void> {
  const chatInput = page.locator('[data-testid="chat-input"]');
  await chatInput.fill(message);
  await page.keyboard.press('Enter');
}

/**
 * Wait for chat response
 */
export async function waitForChatResponse(page: Page, timeout = 60000): Promise<void> {
  // Wait for loading to appear
  const loading = page.locator('[data-testid="chat-loading"]');
  await loading.waitFor({ state: 'visible', timeout: 5000 }).catch(() => {});

  // Wait for loading to disappear
  await loading.waitFor({ state: 'hidden', timeout });
}

/**
 * Open command palette
 */
export async function openCommandPalette(page: Page): Promise<void> {
  await page.keyboard.press('Control+k');
  await expect(page.locator('[data-testid="command-palette"]')).toBeVisible();
}

/**
 * Mock API endpoint
 */
export async function mockApiEndpoint(
  page: Page,
  endpoint: string,
  response: { status?: number; body: object }
): Promise<void> {
  await page.route(`**${endpoint}`, route => {
    route.fulfill({
      status: response.status || 200,
      contentType: 'application/json',
      body: JSON.stringify(response.body)
    });
  });
}

/**
 * Set local storage item
 */
export async function setLocalStorageItem(
  page: Page,
  key: string,
  value: string
): Promise<void> {
  await page.evaluate(([k, v]) => {
    localStorage.setItem(k, v);
  }, [key, value]);
}

/**
 * Get local storage item
 */
export async function getLocalStorageItem(
  page: Page,
  key: string
): Promise<string | null> {
  return page.evaluate(k => localStorage.getItem(k), key);
}

/**
 * Clear all local storage
 */
export async function clearLocalStorage(page: Page): Promise<void> {
  await page.evaluate(() => localStorage.clear());
}

/**
 * Take a screenshot with timestamp
 */
export async function takeTimestampedScreenshot(
  page: Page,
  name: string
): Promise<void> {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  await page.screenshot({
    path: `test-results/screenshots/${name}-${timestamp}.png`,
    fullPage: true
  });
}

/**
 * Wait for toast notification
 */
export async function waitForToast(
  page: Page,
  textMatch: string | RegExp,
  timeout = 5000
): Promise<void> {
  const toast = page.locator('[data-testid="toast"]').filter({
    hasText: textMatch
  });
  await expect(toast).toBeVisible({ timeout });
}

/**
 * Dismiss all toasts
 */
export async function dismissAllToasts(page: Page): Promise<void> {
  const closeButtons = page.locator('[data-testid="toast"] [data-testid="close-toast"]');
  const count = await closeButtons.count();

  for (let i = 0; i < count; i++) {
    await closeButtons.nth(0).click();
  }
}

/**
 * Assert no console errors
 */
export function setupConsoleErrorTracking(page: Page): { getErrors: () => string[] } {
  const errors: string[] = [];

  page.on('console', msg => {
    if (msg.type() === 'error') {
      errors.push(msg.text());
    }
  });

  return {
    getErrors: () => errors
  };
}

/**
 * Performance timing helper
 */
export async function measurePageLoadTime(page: Page, url: string): Promise<number> {
  const startTime = Date.now();
  await page.goto(url);
  await page.waitForLoadState('networkidle');
  return Date.now() - startTime;
}

/**
 * Check if element is in viewport
 */
export async function isElementInViewport(
  page: Page,
  selector: string
): Promise<boolean> {
  return page.evaluate(sel => {
    const element = document.querySelector(sel);
    if (!element) return false;

    const rect = element.getBoundingClientRect();
    return (
      rect.top >= 0 &&
      rect.left >= 0 &&
      rect.bottom <= window.innerHeight &&
      rect.right <= window.innerWidth
    );
  }, selector);
}

/**
 * Scroll element into view
 */
export async function scrollIntoView(page: Page, selector: string): Promise<void> {
  await page.evaluate(sel => {
    const element = document.querySelector(sel);
    element?.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }, selector);
}

/**
 * Wait for animation to complete
 */
export async function waitForAnimation(page: Page, timeout = 1000): Promise<void> {
  await page.waitForTimeout(timeout);
}

/**
 * Get computed style property
 */
export async function getComputedStyleProperty(
  page: Page,
  selector: string,
  property: string
): Promise<string> {
  return page.evaluate(
    ([sel, prop]) => {
      const element = document.querySelector(sel);
      if (!element) return '';
      return getComputedStyle(element).getPropertyValue(prop);
    },
    [selector, property]
  );
}

/**
 * Test data factory
 */
export const testData = {
  project: {
    name: 'test-project',
    files: [
      {
        name: 'App.tsx',
        content: 'export function App() { return <div>Hello</div>; }'
      },
      {
        name: 'index.tsx',
        content: 'import { App } from "./App"; render(<App />);'
      }
    ]
  },

  user: {
    email: 'test@example.com',
    name: 'Test User'
  },

  apiKey: 'sk-test-api-key-for-testing-12345',

  chatPrompts: {
    simple: 'Create a button component',
    complex: 'Create a full dashboard with charts, tables, and navigation',
    debug: 'Fix the error in my code'
  }
};
