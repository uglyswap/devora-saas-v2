/**
 * Devora Design System - Page Transition Component
 * Wrapper component for page transitions with Framer Motion
 */

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { pageVariants } from '../animations/variants';

interface PageTransitionProps {
  children: React.ReactNode;
  className?: string;
}

export const PageTransition: React.FC<PageTransitionProps> = ({
  children,
  className,
}) => {
  return (
    <motion.div
      variants={pageVariants}
      initial="initial"
      animate="enter"
      exit="exit"
      className={className}
    >
      {children}
    </motion.div>
  );
};

interface AnimatedPageWrapperProps {
  children: React.ReactNode;
  location?: { pathname: string };
}

export const AnimatedPageWrapper: React.FC<AnimatedPageWrapperProps> = ({
  children,
  location,
}) => {
  return (
    <AnimatePresence mode="wait" initial={false}>
      <motion.div
        key={location?.pathname || 'page'}
        variants={pageVariants}
        initial="initial"
        animate="enter"
        exit="exit"
        className="w-full"
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
};

export default PageTransition;
