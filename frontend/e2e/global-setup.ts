import { chromium, FullConfig } from '@playwright/test';

/**
 * Global setup for Playwright tests
 * Runs once before all tests
 */
async function globalSetup(config: FullConfig) {
  console.log('Running global setup...');

  // Create a browser instance for setup tasks
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // Wait for the application to be ready
    const baseURL = config.projects[0].use?.baseURL || 'http://localhost:3000';
    await page.goto(baseURL, { waitUntil: 'networkidle', timeout: 60000 });
    console.log(`Application is ready at ${baseURL}`);

    // Store authentication state if needed
    // await context.storageState({ path: './e2e/fixtures/auth-state.json' });

  } catch (error) {
    console.error('Global setup failed:', error);
    throw error;
  } finally {
    await browser.close();
  }

  console.log('Global setup complete');
}

export default globalSetup;
