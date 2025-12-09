/**
 * Devora Design System - Shadow Tokens
 * Shadows and glow effects for depth and premium feel
 */

export const shadows = {
  // Standard shadows
  xs: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  sm: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)',
  '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',

  // Inner shadows
  inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.05)',
  innerLg: 'inset 0 4px 8px 0 rgba(0, 0, 0, 0.1)',

  // No shadow
  none: 'none',

  // Glow effects (premium)
  glow: {
    primary: '0 0 20px rgba(99, 102, 241, 0.5), 0 0 40px rgba(99, 102, 241, 0.3)',
    primarySm: '0 0 10px rgba(99, 102, 241, 0.4)',
    primaryLg: '0 0 30px rgba(99, 102, 241, 0.6), 0 0 60px rgba(99, 102, 241, 0.4)',

    accent: '0 0 20px rgba(34, 211, 238, 0.5), 0 0 40px rgba(34, 211, 238, 0.3)',
    accentSm: '0 0 10px rgba(34, 211, 238, 0.4)',
    accentLg: '0 0 30px rgba(34, 211, 238, 0.6), 0 0 60px rgba(34, 211, 238, 0.4)',

    secondary: '0 0 20px rgba(168, 85, 247, 0.5), 0 0 40px rgba(168, 85, 247, 0.3)',
    secondarySm: '0 0 10px rgba(168, 85, 247, 0.4)',
    secondaryLg: '0 0 30px rgba(168, 85, 247, 0.6), 0 0 60px rgba(168, 85, 247, 0.4)',

    success: '0 0 20px rgba(34, 197, 94, 0.5)',
    error: '0 0 20px rgba(239, 68, 68, 0.5)',
    warning: '0 0 20px rgba(245, 158, 11, 0.5)',

    white: '0 0 20px rgba(255, 255, 255, 0.5), 0 0 40px rgba(255, 255, 255, 0.3)',
  },

  // Colored shadows for cards and buttons
  colored: {
    primary: '0 10px 25px -5px rgba(99, 102, 241, 0.3)',
    accent: '0 10px 25px -5px rgba(34, 211, 238, 0.3)',
    secondary: '0 10px 25px -5px rgba(168, 85, 247, 0.3)',
    success: '0 10px 25px -5px rgba(34, 197, 94, 0.3)',
    error: '0 10px 25px -5px rgba(239, 68, 68, 0.3)',
    warning: '0 10px 25px -5px rgba(245, 158, 11, 0.3)',
  },

  // Elevation shadows (layered)
  elevation: {
    1: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    2: '0 2px 4px 0 rgba(0, 0, 0, 0.08)',
    3: '0 4px 8px 0 rgba(0, 0, 0, 0.1)',
    4: '0 8px 16px 0 rgba(0, 0, 0, 0.12)',
    5: '0 16px 32px 0 rgba(0, 0, 0, 0.15)',
    6: '0 24px 48px 0 rgba(0, 0, 0, 0.18)',
  },
} as const;

// Drop shadow filters (for images and SVGs)
export const dropShadows = {
  sm: 'drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1))',
  md: 'drop-shadow(0 4px 6px rgba(0, 0, 0, 0.1))',
  lg: 'drop-shadow(0 10px 15px rgba(0, 0, 0, 0.1))',
  xl: 'drop-shadow(0 20px 25px rgba(0, 0, 0, 0.15))',

  // Colored drop shadows
  primary: 'drop-shadow(0 4px 12px rgba(99, 102, 241, 0.3))',
  accent: 'drop-shadow(0 4px 12px rgba(34, 211, 238, 0.3))',
  secondary: 'drop-shadow(0 4px 12px rgba(168, 85, 247, 0.3))',

  // Glow drop shadows
  glowPrimary: 'drop-shadow(0 0 12px rgba(99, 102, 241, 0.5))',
  glowAccent: 'drop-shadow(0 0 12px rgba(34, 211, 238, 0.5))',
  glowWhite: 'drop-shadow(0 0 12px rgba(255, 255, 255, 0.5))',
} as const;

// Text shadows
export const textShadows = {
  sm: '0 1px 2px rgba(0, 0, 0, 0.1)',
  md: '0 2px 4px rgba(0, 0, 0, 0.15)',
  lg: '0 4px 8px rgba(0, 0, 0, 0.2)',
  xl: '0 8px 16px rgba(0, 0, 0, 0.25)',

  // Glow text shadows
  glow: '0 0 10px rgba(255, 255, 255, 0.8), 0 0 20px rgba(255, 255, 255, 0.5)',
  glowPrimary: '0 0 10px rgba(99, 102, 241, 0.8), 0 0 20px rgba(99, 102, 241, 0.5)',
  glowAccent: '0 0 10px rgba(34, 211, 238, 0.8), 0 0 20px rgba(34, 211, 238, 0.5)',
} as const;

export type ShadowToken = keyof typeof shadows;
export type DropShadowToken = keyof typeof dropShadows;
export type TextShadowToken = keyof typeof textShadows;
