/**
 * Devora Design System - Framer Motion Variants
 */
import { Variants, Transition } from 'framer-motion';

export const transitions = {
  spring: { type: 'spring', stiffness: 400, damping: 30 } as Transition,
  smooth: { duration: 0.3, ease: [0.25, 0.1, 0.25, 1] } as Transition,
  fast: { duration: 0.15, ease: 'easeOut' } as Transition,
};

export const pageVariants: Variants = {
  initial: { opacity: 0, x: -20 },
  enter: { opacity: 1, x: 0, transition: { duration: 0.4, staggerChildren: 0.1 } },
  exit: { opacity: 0, x: 20, transition: { duration: 0.3 } },
};

export const fadeVariants: Variants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: transitions.smooth },
};

export const scaleVariants: Variants = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: { opacity: 1, scale: 1, transition: transitions.spring },
};

export const slideUpVariants: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: transitions.spring },
};

export const staggerContainerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.05 } },
};

export const staggerItemVariants: Variants = {
  hidden: { opacity: 0, y: 10 },
  visible: { opacity: 1, y: 0, transition: transitions.spring },
};

export const cardHoverVariants = {
  rest: { scale: 1 },
  hover: { scale: 1.02, boxShadow: '0 20px 40px -20px rgba(99, 102, 241, 0.3)' },
  tap: { scale: 0.98 },
};

export const buttonHoverVariants = {
  rest: { scale: 1 },
  hover: { scale: 1.02, y: -1 },
  tap: { scale: 0.98 },
};

export const shakeVariants: Variants = {
  shake: { x: [0, -10, 10, -10, 10, 0], transition: { duration: 0.4 } },
};

export const bounceVariants: Variants = {
  bounce: { scale: [1, 1.2, 0.9, 1.1, 1], transition: { duration: 0.5 } },
};

export const spinnerVariants: Variants = {
  animate: { rotate: 360, transition: { duration: 1, repeat: Infinity, ease: 'linear' } },
};
