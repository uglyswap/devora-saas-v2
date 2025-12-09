import React, { memo, forwardRef } from 'react';
import { Loader2 } from 'lucide-react';
import { cn } from '../../../lib/utils';

/**
 * Button Variants Configuration
 */
const buttonVariants = {
  variant: {
    default: 'bg-primary text-primary-foreground hover:bg-primary/90',
    destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
    outline: 'border border-input bg-background hover:bg-accent hover:text-accent-foreground',
    secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
    ghost: 'hover:bg-accent hover:text-accent-foreground',
    link: 'text-primary underline-offset-4 hover:underline',
    gradient: 'bg-gradient-to-r from-emerald-600 to-blue-600 text-white hover:from-emerald-700 hover:to-blue-700',
  },
  size: {
    default: 'h-10 px-4 py-2',
    sm: 'h-9 rounded-md px-3 text-xs',
    lg: 'h-11 rounded-md px-8',
    xl: 'h-12 rounded-lg px-10 text-base',
    icon: 'h-10 w-10',
  },
};

/**
 * Button - Optimized button component with variants
 *
 * Performance optimizations:
 * - React.memo to prevent unnecessary re-renders
 * - forwardRef for ref forwarding
 * - Memoized className computation
 *
 * @version 2.0.0 - Optimized by Frontend Squad
 */
const Button = memo(forwardRef(function Button(
  {
    className,
    variant = 'default',
    size = 'default',
    loading = false,
    disabled = false,
    children,
    leftIcon,
    rightIcon,
    ...props
  },
  ref
) {
  const variantClass = buttonVariants.variant[variant] || buttonVariants.variant.default;
  const sizeClass = buttonVariants.size[size] || buttonVariants.size.default;

  const isDisabled = disabled || loading;

  return (
    <button
      ref={ref}
      className={cn(
        'inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-all duration-200',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2',
        'disabled:pointer-events-none disabled:opacity-50',
        'active:scale-[0.98]',
        variantClass,
        sizeClass,
        className
      )}
      disabled={isDisabled}
      {...props}
    >
      {loading && <Loader2 className="w-4 h-4 animate-spin" />}
      {!loading && leftIcon && <span className="inline-flex">{leftIcon}</span>}
      {children}
      {!loading && rightIcon && <span className="inline-flex">{rightIcon}</span>}
    </button>
  );
}));

Button.displayName = 'Button';

export { Button, buttonVariants };
