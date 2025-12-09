import React, { memo, forwardRef } from 'react';
import { cn } from '../../../lib/utils';

/**
 * Card - Optimized card component with header, content, footer
 *
 * Performance optimizations:
 * - All components memoized with React.memo
 * - forwardRef for ref forwarding
 * - Compound component pattern for composition
 *
 * @version 2.0.0 - Optimized by Frontend Squad
 */

const Card = memo(forwardRef(function Card({ className, hover = false, ...props }, ref) {
  return (
    <div
      ref={ref}
      className={cn(
        'rounded-xl border bg-card text-card-foreground shadow-md',
        hover && 'transition-all duration-200 hover:-translate-y-1 hover:shadow-lg hover:border-primary/30',
        className
      )}
      {...props}
    />
  );
}));

const CardHeader = memo(forwardRef(function CardHeader({ className, ...props }, ref) {
  return (
    <div
      ref={ref}
      className={cn('flex flex-col space-y-1.5 p-6', className)}
      {...props}
    />
  );
}));

const CardTitle = memo(forwardRef(function CardTitle({ className, ...props }, ref) {
  return (
    <h3
      ref={ref}
      className={cn('text-2xl font-semibold leading-none tracking-tight', className)}
      {...props}
    />
  );
}));

const CardDescription = memo(forwardRef(function CardDescription({ className, ...props }, ref) {
  return (
    <p
      ref={ref}
      className={cn('text-sm text-muted-foreground', className)}
      {...props}
    />
  );
}));

const CardContent = memo(forwardRef(function CardContent({ className, ...props }, ref) {
  return (
    <div
      ref={ref}
      className={cn('p-6 pt-0', className)}
      {...props}
    />
  );
}));

const CardFooter = memo(forwardRef(function CardFooter({ className, ...props }, ref) {
  return (
    <div
      ref={ref}
      className={cn('flex items-center p-6 pt-0', className)}
      {...props}
    />
  );
}));

// Set display names
Card.displayName = 'Card';
CardHeader.displayName = 'CardHeader';
CardTitle.displayName = 'CardTitle';
CardDescription.displayName = 'CardDescription';
CardContent.displayName = 'CardContent';
CardFooter.displayName = 'CardFooter';

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent };
