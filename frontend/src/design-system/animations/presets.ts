/**
 * Devora Design System - Animation Presets
 * Complete animation configurations ready to use
 */

import { MotionProps } from 'framer-motion';
import {
  fadeInUpVariants,
  fadeInVariants,
  scaleInVariants,
  cardVariants,
  buttonVariants,
  listContainerVariants,
  listItemVariants,
  pageVariants,
  modalContentVariants,
  modalBackdropVariants,
  glowCardVariants,
  glowButtonVariants,
  shakeVariants,
  bounceVariants,
  pulseVariants,
  skeletonVariants,
} from './variants';
import {
  transitions,
  springs,
  getTransition,
} from './transitions';

// Preset configurations ready to spread into motion components
export const animationPresets = {
  // Fade presets
  fadeIn: {
    initial: 'hidden',
    animate: 'visible',
    exit: 'exit',
    variants: fadeInVariants,
  } as MotionProps,

  fadeInUp: {
    initial: 'hidden',
    animate: 'visible',
    exit: 'exit',
    variants: fadeInUpVariants,
  } as MotionProps,

  // Scale presets
  scaleIn: {
    initial: 'hidden',
    animate: 'visible',
    exit: 'exit',
    variants: scaleInVariants,
  } as MotionProps,

  // Card presets
  card: {
    initial: 'initial',
    whileHover: 'hover',
    whileTap: 'tap',
    variants: cardVariants,
  } as MotionProps,

  cardGlow: {
    initial: 'initial',
    whileHover: 'hover',
    variants: glowCardVariants,
  } as MotionProps,

  // Button presets
  button: {
    initial: 'initial',
    whileHover: 'hover',
    whileTap: 'tap',
    variants: buttonVariants,
  } as MotionProps,

  buttonGlow: {
    initial: 'initial',
    whileHover: 'hover',
    variants: glowButtonVariants,
  } as MotionProps,

  // Page transition preset
  page: {
    initial: 'initial',
    animate: 'enter',
    exit: 'exit',
    variants: pageVariants,
  } as MotionProps,

  // List presets
  list: {
    initial: 'hidden',
    animate: 'visible',
    variants: listContainerVariants,
  } as MotionProps,

  listItem: {
    variants: listItemVariants,
  } as MotionProps,

  // Modal presets
  modalBackdrop: {
    initial: 'hidden',
    animate: 'visible',
    exit: 'hidden',
    variants: modalBackdropVariants,
  } as MotionProps,

  modalContent: {
    initial: 'hidden',
    animate: 'visible',
    exit: 'exit',
    variants: modalContentVariants,
  } as MotionProps,

  // Micro-interaction presets
  shake: {
    initial: 'initial',
    animate: 'shake',
    variants: shakeVariants,
  } as MotionProps,

  bounce: {
    initial: 'initial',
    animate: 'bounce',
    variants: bounceVariants,
  } as MotionProps,

  pulse: {
    initial: 'initial',
    animate: 'pulse',
    variants: pulseVariants,
  } as MotionProps,

  // Skeleton preset
  skeleton: {
    initial: 'start',
    animate: 'end',
    variants: skeletonVariants,
  } as MotionProps,
} as const;

// Quick animation utilities
export const quickAnimations = {
  // Hover scale
  hoverScale: {
    whileHover: { scale: 1.05 },
    whileTap: { scale: 0.95 },
    transition: transitions.button,
  } as MotionProps,

  // Hover lift
  hoverLift: {
    whileHover: { y: -4, scale: 1.02 },
    whileTap: { y: 0, scale: 1 },
    transition: transitions.cardHover,
  } as MotionProps,

  // Tap scale
  tapScale: {
    whileTap: { scale: 0.95 },
    transition: transitions.buttonPress,
  } as MotionProps,

  // Focus scale
  focusScale: {
    whileFocus: { scale: 1.02 },
    transition: transitions.inputFocus,
  } as MotionProps,

  // Hover glow (primary)
  hoverGlowPrimary: {
    whileHover: {
      boxShadow: '0 0 30px rgba(99, 102, 241, 0.6)',
    },
    transition: transitions.premium,
  } as MotionProps,

  // Hover glow (accent)
  hoverGlowAccent: {
    whileHover: {
      boxShadow: '0 0 30px rgba(34, 211, 238, 0.6)',
    },
    transition: transitions.premium,
  } as MotionProps,

  // Hover rotate
  hoverRotate: {
    whileHover: { rotate: 5 },
    transition: transitions.button,
  } as MotionProps,

  // Spring bounce
  springBounce: {
    transition: springs.bouncy,
  } as MotionProps,

  // Layout animation
  layout: {
    layout: true,
    transition: springs.default,
  } as MotionProps,
} as const;

// Component-specific presets
export const componentPresets = {
  // Button variants
  button: {
    primary: {
      ...animationPresets.button,
      ...quickAnimations.hoverGlowPrimary,
    },
    secondary: {
      ...animationPresets.button,
    },
    ghost: {
      whileHover: { scale: 1.05, backgroundColor: 'rgba(99, 102, 241, 0.1)' },
      whileTap: { scale: 0.95 },
      transition: transitions.button,
    },
  },

  // Card variants
  card: {
    default: animationPresets.card,
    glow: {
      ...animationPresets.card,
      ...animationPresets.cardGlow,
    },
    lift: {
      ...animationPresets.card,
      whileHover: {
        y: -8,
        scale: 1.02,
        boxShadow: '0 20px 40px rgba(0, 0, 0, 0.15)',
      },
    },
  },

  // Input variants
  input: {
    default: {
      whileFocus: {
        scale: 1.01,
        borderColor: 'rgba(99, 102, 241, 1)',
      },
      transition: transitions.inputFocus,
    },
    glow: {
      whileFocus: {
        boxShadow: '0 0 20px rgba(99, 102, 241, 0.4)',
      },
      transition: transitions.inputFocus,
    },
  },

  // Menu/Dropdown variants
  menu: {
    container: {
      initial: { opacity: 0, scale: 0.95, y: -10 },
      animate: { opacity: 1, scale: 1, y: 0 },
      exit: { opacity: 0, scale: 0.95, y: -10 },
      transition: transitions.premium,
    },
    item: {
      whileHover: { backgroundColor: 'rgba(99, 102, 241, 0.1)', x: 4 },
      transition: transitions.fast,
    },
  },

  // Toast/Notification variants
  toast: {
    initial: { opacity: 0, y: 50, scale: 0.3 },
    animate: { opacity: 1, y: 0, scale: 1 },
    exit: { opacity: 0, scale: 0.5 },
    transition: transitions.premium,
  },

  // Tooltip variants
  tooltip: {
    initial: { opacity: 0, scale: 0.9 },
    animate: { opacity: 1, scale: 1 },
    exit: { opacity: 0, scale: 0.9 },
    transition: { duration: 0.15 },
  },
} as const;

// Accessibility-aware preset creator
export const createAccessiblePreset = (
  preset: MotionProps,
  prefersReducedMotion?: boolean
): MotionProps => {
  if (prefersReducedMotion) {
    return {
      ...preset,
      transition: { duration: 0.01 },
      initial: preset.animate,
    };
  }
  return preset;
};

// Utility to combine multiple presets
export const combinePresets = (...presets: MotionProps[]): MotionProps => {
  return presets.reduce((acc, preset) => ({ ...acc, ...preset }), {});
};

export type AnimationPreset = keyof typeof animationPresets;
export type QuickAnimation = keyof typeof quickAnimations;
