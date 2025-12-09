/**
 * DEVORA CUSTOM HOOKS - Centralized Export
 *
 * Collection of optimized, reusable React hooks for Devora
 * Includes utility hooks, streaming, and real-time collaboration
 *
 * @author Frontend Squad - Hooks Specialist
 * @version 2.0.0
 */

// ============================================
// STREAMING & REAL-TIME HOOKS
// ============================================

/**
 * Hook for streaming code generation via SSE
 * Handles connection, event parsing, and generation state
 */
export { useStreamingGeneration } from './useStreamingGeneration';
export type { default as UseStreamingGenerationDefault } from './useStreamingGeneration';

/**
 * Hook for real-time collaboration via WebSocket
 * Handles connection, reconnection, and collaborative events
 */
export { useWebSocket } from './useWebSocket';
export type { default as UseWebSocketDefault } from './useWebSocket';

// ============================================
// UTILITY HOOKS
// ============================================

/**
 * Hook for debouncing values
 * Useful for search inputs, API calls, etc.
 */
export { useDebounce } from './useDebounce';

/**
 * Hook for localStorage with automatic serialization
 * Persists state across browser sessions
 */
export { useLocalStorage } from './useLocalStorage';

/**
 * Hook for handling async operations
 * Manages loading, error, and data states
 */
export { useAsync } from './useAsync';

/**
 * Hook for copying text to clipboard
 * Provides feedback on copy success/failure
 */
export { useCopyToClipboard } from './useCopyToClipboard';

// ============================================
// UI/UX HOOKS
// ============================================

/**
 * Hooks for responsive design and media queries
 * Includes device detection and user preferences
 */
export {
  useMediaQuery,
  useIsMobile,
  useIsTablet,
  useIsDesktop,
  usePrefersDarkMode,
  usePrefersReducedMotion,
} from './useMediaQuery';

/**
 * Hook for detecting clicks outside an element
 * Useful for dropdown menus, modals, etc.
 */
export { useClickOutside } from './useClickOutside';

/**
 * Hooks for keyboard interactions
 * Includes single key press and key combinations
 */
export { useKeyPress, useKeyCombo } from './useKeyPress';

// ============================================
// UI FEEDBACK HOOKS
// ============================================

/**
 * Hook for toast notifications
 * Provides a simple API for showing notifications
 */
export { useToast } from './use-toast';

// ============================================
// ACCESSIBILITY HOOKS
// ============================================

/**
 * Comprehensive accessibility hooks
 * For building accessible components
 */
export { default as useAccessibility } from './useAccessibility';
