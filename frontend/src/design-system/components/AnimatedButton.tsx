/**
 * Devora Design System - Animated Button Component
 * Premium button with Framer Motion animations
 */

import React, { forwardRef } from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';
import { cn } from '@/lib/utils';
import { buttonHoverVariants, transitions } from '../animations/variants';

export interface AnimatedButtonProps extends Omit<HTMLMotionProps<'button'>, 'children'> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'destructive' | 'outline';
  size?: 'sm' | 'md' | 'lg' | 'icon';
  loading?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  children?: React.ReactNode;
  glow?: boolean;
}

const variantStyles = {
  primary: 'bg-gradient-to-r from-devora-primary to-purple-500 text-white hover:from-devora-primary-dark hover:to-purple-600 shadow-glow-sm hover:shadow-glow',
  secondary: 'bg-white/10 text-white hover:bg-white/20 border border-white/20',
  ghost: 'text-gray-300 hover:text-white hover:bg-white/10',
  destructive: 'bg-red-500 text-white hover:bg-red-600',
  outline: 'border border-devora-primary/50 text-devora-primary hover:bg-devora-primary/10 hover:border-devora-primary',
};

const sizeStyles = {
  sm: 'px-3 py-1.5 text-sm gap-1.5',
  md: 'px-4 py-2 text-base gap-2',
  lg: 'px-6 py-3 text-lg gap-2.5',
  icon: 'p-2',
};

export const AnimatedButton = forwardRef<HTMLButtonElement, AnimatedButtonProps>(
  (
    {
      className,
      variant = 'primary',
      size = 'md',
      loading = false,
      icon,
      iconPosition = 'left',
      children,
      disabled,
      glow = false,
      ...props
    },
    ref
  ) => {
    const isDisabled = disabled || loading;

    return (
      <motion.button
        ref={ref}
        className={cn(
          'relative inline-flex items-center justify-center rounded-lg font-medium',
          'transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-devora-primary/50',
          'disabled:opacity-50 disabled:cursor-not-allowed',
          variantStyles[variant],
          sizeStyles[size],
          glow && 'animate-pulse-glow',
          className
        )}
        variants={buttonHoverVariants}
        initial="rest"
        whileHover={isDisabled ? undefined : "hover"}
        whileTap={isDisabled ? undefined : "tap"}
        disabled={isDisabled}
        {...props}
      >
        {/* Loading Spinner */}
        {loading && (
          <motion.div
            className="absolute inset-0 flex items-center justify-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={transitions.fast}
          >
            <motion.div
              className="w-5 h-5 border-2 border-current/30 border-t-current rounded-full"
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
            />
          </motion.div>
        )}

        {/* Content */}
        <motion.span
          className="flex items-center gap-inherit"
          animate={{ opacity: loading ? 0 : 1 }}
          transition={transitions.fast}
        >
          {icon && iconPosition === 'left' && (
            <span className="flex-shrink-0">{icon}</span>
          )}
          {children}
          {icon && iconPosition === 'right' && (
            <span className="flex-shrink-0">{icon}</span>
          )}
        </motion.span>
      </motion.button>
    );
  }
);

AnimatedButton.displayName = 'AnimatedButton';

export default AnimatedButton;
