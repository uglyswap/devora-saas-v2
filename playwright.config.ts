import { defineConfig, devices } from '@playwright/test';

/**
 * Configuration Playwright pour tests E2E Devora
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  testDir: './tests/e2e',

  // Timeout configurations
  timeout: 30 * 1000,
  expect: {
    timeout: 5000,
  },

  // Parallel execution
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,

  // Reporter configuration
  reporter: [
    ['html', { outputFolder: 'test_reports/playwright-report' }],
    ['json', { outputFile: 'test_reports/playwright-results.json' }],
    ['junit', { outputFile: 'test_reports/playwright-junit.xml' }],
    ['list'],
  ],

  // Shared settings for all projects
  use: {
    // Base URL for navigation
    baseURL: process.env.BASE_URL || 'http://localhost:3000',

    // API endpoint
    extraHTTPHeaders: {
      'Accept': 'application/json',
    },

    // Screenshots and traces
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',

    // Browser options
    viewport: { width: 1280, height: 720 },
    ignoreHTTPSErrors: true,

    // Context options
    locale: 'fr-FR',
    timezoneId: 'Europe/Paris',
  },

  // Test projects for different browsers
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    // Mobile viewports
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],

  // Web server configuration
  webServer: {
    command: 'cd frontend && npm start',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
    env: {
      REACT_APP_API_URL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
    },
  },
});
