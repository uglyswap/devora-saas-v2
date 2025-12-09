/**
 * Devora Design System - Color Tokens
 */

export const colors = {
  brand: {
    primary: '#6366f1',
    primaryLight: '#818cf8',
    primaryDark: '#4f46e5',
    accent: '#22d3ee',
    accentLight: '#67e8f9',
    accentDark: '#06b6d4',
  },
  gradients: {
    primary: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%)',
    accent: 'linear-gradient(135deg, #06b6d4 0%, #22d3ee 100%)',
    surface: 'linear-gradient(180deg, rgba(99, 102, 241, 0.1) 0%, transparent 100%)',
  },
  dark: {
    bg: { primary: '#0f0f23', secondary: '#1a1a2e', surface: '#1f2937' },
    border: { default: '#374151', subtle: 'rgba(255, 255, 255, 0.1)' },
    text: { primary: '#f9fafb', secondary: '#9ca3af', muted: '#6b7280' },
  },
  semantic: { success: '#10b981', warning: '#f59e0b', error: '#ef4444', info: '#3b82f6' },
} as const;

export type ColorToken = typeof colors;
