/**
 * Devora Design System - Animation Transitions
 * Reusable transition configurations for Framer Motion
 */

import { Transition } from 'framer-motion';

// Easing curves
export const easings = {
  // Standard easings
  linear: [0, 0, 1, 1],
  ease: [0.25, 0.1, 0.25, 1],
  easeIn: [0.42, 0, 1, 1],
  easeOut: [0, 0, 0.58, 1],
  easeInOut: [0.42, 0, 0.58, 1],

  // Custom easings
  smooth: [0.25, 0.1, 0.25, 1],
  bounce: [0.68, -0.55, 0.265, 1.55],
  elastic: [0.175, 0.885, 0.32, 1.275],

  // Premium easings
  premium: [0.25, 0.46, 0.45, 0.94],
  butter: [0.33, 1, 0.68, 1],
  snap: [0.87, 0, 0.13, 1],
} as const;

// Duration presets
export const durations = {
  instant: 0.1,
  fast: 0.2,
  normal: 0.3,
  slow: 0.5,
  slower: 0.8,
  slowest: 1,
} as const;

// Spring configurations
export const springs = {
  // Gentle spring
  gentle: {
    type: 'spring' as const,
    stiffness: 100,
    damping: 15,
  },

  // Standard spring
  default: {
    type: 'spring' as const,
    stiffness: 200,
    damping: 20,
  },

  // Bouncy spring
  bouncy: {
    type: 'spring' as const,
    stiffness: 300,
    damping: 10,
  },

  // Snappy spring
  snappy: {
    type: 'spring' as const,
    stiffness: 400,
    damping: 25,
  },

  // Wobbly spring
  wobbly: {
    type: 'spring' as const,
    stiffness: 180,
    damping: 8,
  },

  // Stiff spring
  stiff: {
    type: 'spring' as const,
    stiffness: 500,
    damping: 30,
  },
} as const;

// Transition presets
export const transitions = {
  // Fade transitions
  fadeIn: {
    duration: durations.normal,
    ease: easings.ease,
  } as Transition,

  fadeOut: {
    duration: durations.fast,
    ease: easings.ease,
  } as Transition,

  // Scale transitions
  scaleIn: {
    duration: durations.normal,
    ease: easings.premium,
  } as Transition,

  scaleOut: {
    duration: durations.fast,
    ease: easings.ease,
  } as Transition,

  // Slide transitions
  slideIn: {
    duration: durations.slow,
    ease: easings.premium,
  } as Transition,

  slideOut: {
    duration: durations.normal,
    ease: easings.ease,
  } as Transition,

  // Button transitions
  button: {
    duration: durations.fast,
    ease: easings.easeOut,
  } as Transition,

  buttonPress: {
    duration: durations.instant,
    ease: easings.snap,
  } as Transition,

  // Card transitions
  cardHover: {
    duration: durations.normal,
    ease: easings.premium,
  } as Transition,

  cardPress: {
    duration: durations.instant,
    ease: easings.snap,
  } as Transition,

  // Input transitions
  inputFocus: {
    duration: durations.fast,
    ease: easings.ease,
  } as Transition,

  // Modal transitions
  modalBackdrop: {
    duration: durations.normal,
    ease: easings.ease,
  } as Transition,

  modalContent: {
    duration: durations.normal,
    ease: easings.premium,
  } as Transition,

  // Page transitions
  pageEnter: {
    duration: durations.normal,
    ease: easings.premium,
  } as Transition,

  pageExit: {
    duration: durations.fast,
    ease: easings.ease,
  } as Transition,

  // List stagger
  staggerFast: {
    staggerChildren: 0.05,
    delayChildren: 0,
  } as Transition,

  staggerNormal: {
    staggerChildren: 0.1,
    delayChildren: 0.1,
  } as Transition,

  staggerSlow: {
    staggerChildren: 0.2,
    delayChildren: 0.2,
  } as Transition,

  // Loading transitions
  spinner: {
    duration: 1,
    ease: easings.linear,
    repeat: Infinity,
  } as Transition,

  pulse: {
    duration: 2,
    ease: easings.easeInOut,
    repeat: Infinity,
    repeatType: 'reverse' as const,
  } as Transition,

  // Micro-interactions
  ripple: {
    duration: durations.slow,
    ease: easings.easeOut,
  } as Transition,

  bounce: {
    duration: durations.slow,
    ease: easings.bounce,
  } as Transition,

  shake: {
    duration: durations.slow,
    ease: easings.elastic,
  } as Transition,

  // Premium transitions
  premium: {
    duration: durations.slow,
    ease: easings.premium,
  } as Transition,

  butter: {
    duration: durations.normal,
    ease: easings.butter,
  } as Transition,
} as const;

// Layout transition (for layout animations)
export const layoutTransition: Transition = {
  type: 'spring',
  stiffness: 300,
  damping: 30,
};

// Reduced motion support
export const getTransition = (
  transition: Transition,
  prefersReducedMotion?: boolean
): Transition => {
  if (prefersReducedMotion) {
    return {
      duration: 0.01,
      ease: easings.linear,
    };
  }
  return transition;
};

// Utility to create custom transitions
export const createTransition = (
  duration: number,
  ease: number[] | string = easings.ease
): Transition => ({
  duration,
  ease,
});

// Utility to create spring transition
export const createSpring = (
  stiffness: number = 200,
  damping: number = 20
): Transition => ({
  type: 'spring',
  stiffness,
  damping,
});

export type TransitionPreset = keyof typeof transitions;
export type SpringPreset = keyof typeof springs;
export type EasingPreset = keyof typeof easings;
