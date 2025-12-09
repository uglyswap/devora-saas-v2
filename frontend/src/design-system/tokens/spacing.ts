/**
 * Devora Design System - Spacing Tokens
 * Consistent spacing scale based on 4px base unit
 */

export const spacing = {
  0: '0',
  px: '1px',
  0.5: '0.125rem',   // 2px
  1: '0.25rem',      // 4px
  1.5: '0.375rem',   // 6px
  2: '0.5rem',       // 8px
  2.5: '0.625rem',   // 10px
  3: '0.75rem',      // 12px
  3.5: '0.875rem',   // 14px
  4: '1rem',         // 16px
  5: '1.25rem',      // 20px
  6: '1.5rem',       // 24px
  7: '1.75rem',      // 28px
  8: '2rem',         // 32px
  9: '2.25rem',      // 36px
  10: '2.5rem',      // 40px
  11: '2.75rem',     // 44px
  12: '3rem',        // 48px
  14: '3.5rem',      // 56px
  16: '4rem',        // 64px
  20: '5rem',        // 80px
  24: '6rem',        // 96px
  28: '7rem',        // 112px
  32: '8rem',        // 128px
  36: '9rem',        // 144px
  40: '10rem',       // 160px
  44: '11rem',       // 176px
  48: '12rem',       // 192px
  52: '13rem',       // 208px
  56: '14rem',       // 224px
  60: '15rem',       // 240px
  64: '16rem',       // 256px
  72: '18rem',       // 288px
  80: '20rem',       // 320px
  96: '24rem',       // 384px
} as const;

// Semantic spacing tokens for common use cases
export const semanticSpacing = {
  // Component spacing
  componentPadding: {
    xs: spacing[2],
    sm: spacing[3],
    md: spacing[4],
    lg: spacing[6],
    xl: spacing[8],
  },
  componentGap: {
    xs: spacing[1],
    sm: spacing[2],
    md: spacing[4],
    lg: spacing[6],
    xl: spacing[8],
  },

  // Layout spacing
  layoutPadding: {
    mobile: spacing[4],
    tablet: spacing[6],
    desktop: spacing[8],
  },
  layoutGap: {
    mobile: spacing[4],
    tablet: spacing[6],
    desktop: spacing[8],
  },

  // Section spacing
  sectionSpacing: {
    xs: spacing[8],
    sm: spacing[12],
    md: spacing[16],
    lg: spacing[24],
    xl: spacing[32],
  },

  // Card spacing
  cardPadding: {
    sm: spacing[4],
    md: spacing[6],
    lg: spacing[8],
  },
  cardGap: {
    sm: spacing[3],
    md: spacing[4],
    lg: spacing[6],
  },

  // Button spacing
  buttonPadding: {
    xs: `${spacing[2]} ${spacing[3]}`,
    sm: `${spacing[2.5]} ${spacing[4]}`,
    md: `${spacing[3]} ${spacing[6]}`,
    lg: `${spacing[4]} ${spacing[8]}`,
    xl: `${spacing[5]} ${spacing[10]}`,
  },
  buttonGap: {
    xs: spacing[1.5],
    sm: spacing[2],
    md: spacing[2.5],
    lg: spacing[3],
  },

  // Input spacing
  inputPadding: {
    sm: `${spacing[2]} ${spacing[3]}`,
    md: `${spacing[2.5]} ${spacing[4]}`,
    lg: `${spacing[3]} ${spacing[5]}`,
  },

  // Icon spacing
  iconMargin: {
    xs: spacing[1],
    sm: spacing[1.5],
    md: spacing[2],
    lg: spacing[2.5],
  },
} as const;

// Border radius tokens
export const borderRadius = {
  none: '0',
  sm: '0.125rem',    // 2px
  base: '0.25rem',   // 4px
  md: '0.375rem',    // 6px
  lg: '0.5rem',      // 8px
  xl: '0.75rem',     // 12px
  '2xl': '1rem',     // 16px
  '3xl': '1.5rem',   // 24px
  full: '9999px',
} as const;

export type SpacingToken = keyof typeof spacing;
export type BorderRadiusToken = keyof typeof borderRadius;
