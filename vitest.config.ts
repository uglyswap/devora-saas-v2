import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    // Test environment
    environment: 'jsdom',

    // Global setup
    globals: true,
    setupFiles: ['./tests/setup.ts'],

    // Coverage configuration
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      reportsDirectory: './test_reports/coverage',
      exclude: [
        'node_modules/',
        'tests/',
        '**/*.d.ts',
        '**/*.config.*',
        '**/mockData',
        'dist/',
        'build/',
      ],
      // Target: 84% coverage
      thresholds: {
        lines: 84,
        functions: 84,
        branches: 84,
        statements: 84,
      },
    },

    // Include/exclude patterns
    include: ['**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}'],
    exclude: ['node_modules', 'dist', 'build', '.git', 'e2e'],

    // Reporter configuration
    reporters: ['verbose', 'json', 'html'],
    outputFile: {
      json: './test_reports/vitest-results.json',
      html: './test_reports/vitest-report.html',
    },

    // Mock configuration
    mockReset: true,
    restoreMocks: true,
    clearMocks: true,

    // Timeout
    testTimeout: 10000,
    hookTimeout: 10000,
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './frontend/src'),
      '@components': path.resolve(__dirname, './frontend/src/components'),
      '@pages': path.resolve(__dirname, './frontend/src/pages'),
      '@contexts': path.resolve(__dirname, './frontend/src/contexts'),
      '@hooks': path.resolve(__dirname, './frontend/src/hooks'),
      '@lib': path.resolve(__dirname, './frontend/src/lib'),
    },
  },
});
