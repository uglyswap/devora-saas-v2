/**
 * DEVORA CUSTOM HOOKS - Centralized Export
 *
 * Collection of optimized, reusable React hooks for Devora
 *
 * @author Frontend Squad - Component Architect
 * @version 1.0.0
 */

// Utility Hooks
export { useDebounce } from './useDebounce';
export { useLocalStorage } from './useLocalStorage';
export { useAsync } from './useAsync';
export { useCopyToClipboard } from './useCopyToClipboard';

// UI/UX Hooks
export { useMediaQuery, useIsMobile, useIsTablet, useIsDesktop, usePrefersDarkMode, usePrefersReducedMotion } from './useMediaQuery';
export { useClickOutside } from './useClickOutside';
export { useKeyPress, useKeyCombo } from './useKeyPress';

// Import from existing hooks
export { useToast } from './use-toast';
