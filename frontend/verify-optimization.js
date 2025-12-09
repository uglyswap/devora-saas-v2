#!/usr/bin/env node

/**
 * Frontend Squad - Optimization Verification Script
 *
 * Verifies that all optimization files are present and correctly structured.
 * Run before deployment to ensure nothing is missing.
 *
 * Usage:
 *   node verify-optimization.js
 *
 * @author Frontend Squad
 * @version 1.0.0
 */

const fs = require('fs');
const path = require('path');

// ANSI color codes
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
  bold: '\x1b[1m',
};

const log = {
  success: (msg) => console.log(`${colors.green}✓${colors.reset} ${msg}`),
  error: (msg) => console.log(`${colors.red}✗${colors.reset} ${msg}`),
  warning: (msg) => console.log(`${colors.yellow}⚠${colors.reset} ${msg}`),
  info: (msg) => console.log(`${colors.blue}ℹ${colors.reset} ${msg}`),
  header: (msg) => console.log(`\n${colors.bold}${colors.cyan}${msg}${colors.reset}\n`),
};

// Files to verify
const REQUIRED_FILES = [
  // Design System
  { path: 'src/styles/design-system.css', name: 'Design System CSS', critical: true },

  // Optimized Contexts
  { path: 'src/contexts/AuthContext.optimized.jsx', name: 'Optimized Auth Context', critical: true },

  // Optimized Components
  { path: 'src/components/preview/WebContainerPreview.optimized.jsx', name: 'Optimized Preview', critical: true },

  // Custom Hooks
  { path: 'src/hooks/index.js', name: 'Hooks Index', critical: true },
  { path: 'src/hooks/useDebounce.js', name: 'useDebounce Hook', critical: true },
  { path: 'src/hooks/useLocalStorage.js', name: 'useLocalStorage Hook', critical: true },
  { path: 'src/hooks/useMediaQuery.js', name: 'useMediaQuery Hook', critical: true },
  { path: 'src/hooks/useAsync.js', name: 'useAsync Hook', critical: true },
  { path: 'src/hooks/useClickOutside.js', name: 'useClickOutside Hook', critical: true },
  { path: 'src/hooks/useCopyToClipboard.js', name: 'useCopyToClipboard Hook', critical: true },
  { path: 'src/hooks/useKeyPress.js', name: 'useKeyPress Hook', critical: true },

  // Optimized UI Components
  { path: 'src/components/ui/optimized/Button.jsx', name: 'Optimized Button', critical: true },
  { path: 'src/components/ui/optimized/Card.jsx', name: 'Optimized Card', critical: true },
  { path: 'src/components/ui/optimized/Input.jsx', name: 'Optimized Input', critical: true },
  { path: 'src/components/ui/optimized/Modal.jsx', name: 'Optimized Modal', critical: true },

  // Examples
  { path: 'src/examples/OptimizedEditorExample.jsx', name: 'Example Component', critical: false },

  // Documentation
  { path: 'FRONTEND_OPTIMIZATION_GUIDE.md', name: 'Optimization Guide', critical: false },
  { path: 'DEPLOYMENT_CHECKLIST.md', name: 'Deployment Checklist', critical: false },
  { path: 'STRUCTURE.md', name: 'Structure Documentation', critical: false },
];

// Content checks
const CONTENT_CHECKS = [
  {
    file: 'src/styles/design-system.css',
    checks: [
      { pattern: /--devora-primary-500/, name: 'Primary color token' },
      { pattern: /--devora-space-4/, name: 'Spacing tokens' },
      { pattern: /--devora-font-sans/, name: 'Font tokens' },
      { pattern: /@keyframes fadeIn/, name: 'Animations' },
      { pattern: /\.gradient-primary/, name: 'Utility classes' },
    ],
  },
  {
    file: 'src/hooks/index.js',
    checks: [
      { pattern: /export.*useDebounce/, name: 'useDebounce export' },
      { pattern: /export.*useLocalStorage/, name: 'useLocalStorage export' },
      { pattern: /export.*useMediaQuery/, name: 'useMediaQuery export' },
    ],
  },
  {
    file: 'src/contexts/AuthContext.optimized.jsx',
    checks: [
      { pattern: /React\.memo/, name: 'React.memo usage' },
      { pattern: /useCallback/, name: 'useCallback optimization' },
      { pattern: /useMemo/, name: 'useMemo optimization' },
    ],
  },
];

// Statistics
let stats = {
  total: 0,
  found: 0,
  missing: 0,
  critical_missing: 0,
  content_checks_passed: 0,
  content_checks_failed: 0,
};

/**
 * Check if a file exists
 */
function fileExists(filePath) {
  try {
    return fs.existsSync(filePath);
  } catch (err) {
    return false;
  }
}

/**
 * Get file size in KB
 */
function getFileSize(filePath) {
  try {
    const stats = fs.statSync(filePath);
    return (stats.size / 1024).toFixed(2);
  } catch (err) {
    return 0;
  }
}

/**
 * Read file content
 */
function readFile(filePath) {
  try {
    return fs.readFileSync(filePath, 'utf8');
  } catch (err) {
    return null;
  }
}

/**
 * Verify file existence
 */
function verifyFiles() {
  log.header('📁 Verifying File Existence');

  REQUIRED_FILES.forEach((file) => {
    stats.total++;
    const exists = fileExists(file.path);

    if (exists) {
      stats.found++;
      const size = getFileSize(file.path);
      log.success(`${file.name} (${size} KB)`);
    } else {
      stats.missing++;
      if (file.critical) {
        stats.critical_missing++;
        log.error(`${file.name} - MISSING (CRITICAL)`);
      } else {
        log.warning(`${file.name} - MISSING`);
      }
    }
  });
}

/**
 * Verify file content
 */
function verifyContent() {
  log.header('📝 Verifying File Content');

  CONTENT_CHECKS.forEach((fileCheck) => {
    if (!fileExists(fileCheck.file)) {
      log.warning(`Skipping content check for ${fileCheck.file} (file not found)`);
      return;
    }

    const content = readFile(fileCheck.file);
    if (!content) {
      log.error(`Could not read ${fileCheck.file}`);
      return;
    }

    log.info(`Checking ${fileCheck.file}...`);

    fileCheck.checks.forEach((check) => {
      if (check.pattern.test(content)) {
        stats.content_checks_passed++;
        log.success(`  ${check.name}`);
      } else {
        stats.content_checks_failed++;
        log.error(`  ${check.name} - NOT FOUND`);
      }
    });
  });
}

/**
 * Check imports in App.js
 */
function verifyImports() {
  log.header('🔗 Verifying Imports');

  const appFiles = ['src/App.js', 'src/index.js'];
  let foundDesignSystem = false;

  appFiles.forEach((appFile) => {
    if (!fileExists(appFile)) return;

    const content = readFile(appFile);
    if (!content) return;

    if (content.includes('design-system.css')) {
      foundDesignSystem = true;
      log.success(`Design system imported in ${appFile}`);
    }
  });

  if (!foundDesignSystem) {
    log.warning('Design system CSS not imported in App.js or index.js');
    log.info('  Add: import \'./styles/design-system.css\';');
  }
}

/**
 * Check package.json for required dependencies
 */
function verifyDependencies() {
  log.header('📦 Verifying Dependencies');

  const packageJsonPath = 'package.json';
  if (!fileExists(packageJsonPath)) {
    log.error('package.json not found');
    return;
  }

  const packageJson = JSON.parse(readFile(packageJsonPath));
  const deps = { ...packageJson.dependencies, ...packageJson.devDependencies };

  const requiredDeps = [
    { name: 'react', version: '>=18.0.0' },
    { name: 'react-dom', version: '>=18.0.0' },
    { name: 'lucide-react', version: '*' },
  ];

  requiredDeps.forEach((dep) => {
    if (deps[dep.name]) {
      log.success(`${dep.name} (${deps[dep.name]})`);
    } else {
      log.error(`${dep.name} - NOT INSTALLED`);
    }
  });
}

/**
 * Print summary
 */
function printSummary() {
  log.header('📊 Summary');

  console.log(`Total files checked: ${stats.total}`);
  console.log(`${colors.green}Found: ${stats.found}${colors.reset}`);
  console.log(`${colors.red}Missing: ${stats.missing}${colors.reset}`);

  if (stats.critical_missing > 0) {
    console.log(`${colors.red}${colors.bold}Critical files missing: ${stats.critical_missing}${colors.reset}`);
  }

  console.log(`\nContent checks passed: ${colors.green}${stats.content_checks_passed}${colors.reset}`);
  console.log(`Content checks failed: ${colors.red}${stats.content_checks_failed}${colors.reset}`);

  const totalChecks = stats.content_checks_passed + stats.content_checks_failed;
  const successRate = totalChecks > 0 ? ((stats.content_checks_passed / totalChecks) * 100).toFixed(1) : 0;

  console.log(`\n${colors.bold}Success Rate: ${successRate}%${colors.reset}`);

  // Final verdict
  console.log('\n' + '='.repeat(60));
  if (stats.critical_missing === 0 && stats.content_checks_failed === 0) {
    log.success(`${colors.bold}All critical checks passed! Ready for deployment.${colors.reset}`);
    return 0;
  } else if (stats.critical_missing > 0) {
    log.error(`${colors.bold}Critical files missing. Fix before deploying.${colors.reset}`);
    return 1;
  } else {
    log.warning(`${colors.bold}Some checks failed. Review before deploying.${colors.reset}`);
    return 1;
  }
}

/**
 * Main function
 */
function main() {
  console.log('\n' + '='.repeat(60));
  console.log(colors.cyan + colors.bold + '  Frontend Squad - Optimization Verification' + colors.reset);
  console.log('='.repeat(60));

  verifyFiles();
  verifyContent();
  verifyImports();
  verifyDependencies();

  const exitCode = printSummary();
  process.exit(exitCode);
}

// Run
main();
