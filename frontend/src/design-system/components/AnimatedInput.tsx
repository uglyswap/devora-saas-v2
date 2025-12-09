/**
 * Devora Design System - Animated Input
 * Premium input with focus animations
 */

import React, { forwardRef, useState } from 'react';
import { motion, HTMLMotionProps, AnimatePresence } from 'framer-motion';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '../../lib/utils';
import { inputVariants } from '../animations/variants';
import { transitions } from '../animations/transitions';

const inputStyles = cva(
  [
    'w-full rounded-lg',
    'bg-dark-surface',
    'border-2 border-dark-border',
    'px-4 py-3',
    'text-foreground',
    'placeholder:text-muted-foreground',
    'transition-colors',
    'focus:outline-none',
    'disabled:cursor-not-allowed disabled:opacity-50',
  ],
  {
    variants: {
      size: {
        sm: 'px-3 py-2 text-sm',
        md: 'px-4 py-3 text-base',
        lg: 'px-5 py-4 text-lg',
      },
      variant: {
        default: '',
        ghost: 'bg-transparent border-transparent hover:border-dark-border',
        filled: 'bg-dark-elevated border-transparent',
      },
      state: {
        default: '',
        error: 'border-error-500 focus:border-error-500',
        success: 'border-success-500 focus:border-success-500',
      },
    },
    defaultVariants: {
      size: 'md',
      variant: 'default',
      state: 'default',
    },
  }
);

export interface AnimatedInputProps
  extends Omit<HTMLMotionProps<'input'>, 'size'>,
    VariantProps<typeof inputStyles> {
  label?: string;
  error?: string;
  success?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  containerClassName?: string;
  glow?: boolean;
}

export const AnimatedInput = forwardRef<HTMLInputElement, AnimatedInputProps>(
  (
    {
      label,
      error,
      success,
      helperText,
      leftIcon,
      rightIcon,
      size,
      variant,
      state,
      className,
      containerClassName,
      glow = false,
      disabled,
      ...props
    },
    ref
  ) => {
    const [isFocused, setIsFocused] = useState(false);

    const inputState = error ? 'error' : success ? 'success' : state;

    const getFocusShadow = () => {
      if (!glow) return undefined;
      if (error) return '0 0 20px rgba(239, 68, 68, 0.3)';
      if (success) return '0 0 20px rgba(34, 197, 94, 0.3)';
      return '0 0 20px rgba(99, 102, 241, 0.3)';
    };

    return (
      <div className={cn('w-full', containerClassName)}>
        {/* Label */}
        {label && (
          <motion.label
            className="mb-2 block text-sm font-medium text-foreground"
            initial={{ opacity: 0.8 }}
            animate={{
              opacity: isFocused ? 1 : 0.8,
              color: error
                ? 'rgb(239, 68, 68)'
                : success
                ? 'rgb(34, 197, 94)'
                : 'inherit',
            }}
            transition={transitions.inputFocus}
          >
            {label}
          </motion.label>
        )}

        {/* Input Container */}
        <div className="relative">
          {/* Left Icon */}
          {leftIcon && (
            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground">
              {leftIcon}
            </div>
          )}

          {/* Input */}
          <motion.input
            ref={ref}
            className={cn(
              inputStyles({ size, variant, state: inputState }),
              leftIcon && 'pl-11',
              rightIcon && 'pr-11',
              className
            )}
            variants={inputVariants}
            initial="initial"
            animate={isFocused ? (error ? 'error' : 'focus') : 'initial'}
            onFocus={(e) => {
              setIsFocused(true);
              props.onFocus?.(e);
            }}
            onBlur={(e) => {
              setIsFocused(false);
              props.onBlur?.(e);
            }}
            disabled={disabled}
            whileFocus={
              glow
                ? {
                    boxShadow: getFocusShadow(),
                  }
                : undefined
            }
            transition={transitions.inputFocus}
            {...props}
          />

          {/* Right Icon */}
          {rightIcon && (
            <div className="absolute right-4 top-1/2 -translate-y-1/2 text-muted-foreground">
              {rightIcon}
            </div>
          )}

          {/* Focus Ring Animation */}
          <AnimatePresence>
            {isFocused && !disabled && (
              <motion.div
                className="pointer-events-none absolute inset-0 rounded-lg"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                style={{
                  border: '2px solid',
                  borderColor: error
                    ? 'rgb(239, 68, 68)'
                    : success
                    ? 'rgb(34, 197, 94)'
                    : 'rgb(99, 102, 241)',
                }}
                transition={transitions.inputFocus}
              />
            )}
          </AnimatePresence>
        </div>

        {/* Helper Text / Error / Success */}
        <AnimatePresence mode="wait">
          {(error || success || helperText) && (
            <motion.p
              key={error || success || helperText}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={transitions.fadeIn}
              className={cn(
                'mt-2 text-sm',
                error && 'text-error-500',
                success && 'text-success-500',
                !error && !success && 'text-muted-foreground'
              )}
            >
              {error || success || helperText}
            </motion.p>
          )}
        </AnimatePresence>
      </div>
    );
  }
);

AnimatedInput.displayName = 'AnimatedInput';

// Textarea variant
export interface AnimatedTextareaProps
  extends Omit<HTMLMotionProps<'textarea'>, 'size'>,
    Omit<AnimatedInputProps, 'leftIcon' | 'rightIcon'> {
  rows?: number;
}

export const AnimatedTextarea = forwardRef<
  HTMLTextAreaElement,
  AnimatedTextareaProps
>(
  (
    {
      label,
      error,
      success,
      helperText,
      size,
      variant,
      state,
      className,
      containerClassName,
      glow = false,
      disabled,
      rows = 4,
      ...props
    },
    ref
  ) => {
    const [isFocused, setIsFocused] = useState(false);

    const inputState = error ? 'error' : success ? 'success' : state;

    const getFocusShadow = () => {
      if (!glow) return undefined;
      if (error) return '0 0 20px rgba(239, 68, 68, 0.3)';
      if (success) return '0 0 20px rgba(34, 197, 94, 0.3)';
      return '0 0 20px rgba(99, 102, 241, 0.3)';
    };

    return (
      <div className={cn('w-full', containerClassName)}>
        {/* Label */}
        {label && (
          <motion.label
            className="mb-2 block text-sm font-medium text-foreground"
            initial={{ opacity: 0.8 }}
            animate={{
              opacity: isFocused ? 1 : 0.8,
              color: error
                ? 'rgb(239, 68, 68)'
                : success
                ? 'rgb(34, 197, 94)'
                : 'inherit',
            }}
            transition={transitions.inputFocus}
          >
            {label}
          </motion.label>
        )}

        {/* Textarea */}
        <motion.textarea
          ref={ref}
          className={cn(
            inputStyles({ size, variant, state: inputState }),
            'resize-none',
            className
          )}
          variants={inputVariants}
          initial="initial"
          animate={isFocused ? (error ? 'error' : 'focus') : 'initial'}
          onFocus={(e) => {
            setIsFocused(true);
            props.onFocus?.(e);
          }}
          onBlur={(e) => {
            setIsFocused(false);
            props.onBlur?.(e);
          }}
          disabled={disabled}
          rows={rows}
          whileFocus={
            glow
              ? {
                  boxShadow: getFocusShadow(),
                }
              : undefined
          }
          transition={transitions.inputFocus}
          {...(props as any)}
        />

        {/* Helper Text / Error / Success */}
        <AnimatePresence mode="wait">
          {(error || success || helperText) && (
            <motion.p
              key={error || success || helperText}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={transitions.fadeIn}
              className={cn(
                'mt-2 text-sm',
                error && 'text-error-500',
                success && 'text-success-500',
                !error && !success && 'text-muted-foreground'
              )}
            >
              {error || success || helperText}
            </motion.p>
          )}
        </AnimatePresence>
      </div>
    );
  }
);

AnimatedTextarea.displayName = 'AnimatedTextarea';

// Export input styles for reuse
export { inputStyles };
