/**
 * Devora Design System - Skeleton Loader
 * Loading skeleton with pulse animation
 */

import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../lib/utils';

interface SkeletonProps {
  className?: string;
  variant?: 'text' | 'circular' | 'rectangular' | 'rounded';
  width?: string | number;
  height?: string | number;
  animated?: boolean;
}

export const Skeleton: React.FC<SkeletonProps> = ({
  className,
  variant = 'text',
  width,
  height,
  animated = true,
}) => {
  const getVariantClasses = () => {
    switch (variant) {
      case 'text':
        return 'h-4 rounded';
      case 'circular':
        return 'rounded-full';
      case 'rectangular':
        return '';
      case 'rounded':
        return 'rounded-lg';
      default:
        return '';
    }
  };

  return (
    <motion.div
      className={cn(
        'bg-gradient-to-r from-gray-800 via-gray-700 to-gray-800',
        'bg-[length:200%_100%]',
        getVariantClasses(),
        className
      )}
      style={{
        width: width || (variant === 'circular' ? height : '100%'),
        height: height || 'auto',
        aspectRatio: variant === 'circular' ? '1/1' : undefined,
      }}
      animate={
        animated
          ? {
              backgroundPosition: ['200% 0', '-200% 0'],
            }
          : undefined
      }
      transition={
        animated
          ? {
              duration: 2,
              repeat: Infinity,
              ease: 'linear',
            }
          : undefined
      }
    />
  );
};

// Preset skeleton components
export const SkeletonText: React.FC<{ lines?: number; className?: string }> = ({
  lines = 3,
  className,
}) => (
  <div className={cn('space-y-2', className)}>
    {Array.from({ length: lines }).map((_, i) => (
      <Skeleton
        key={i}
        variant="text"
        width={i === lines - 1 ? '70%' : '100%'}
      />
    ))}
  </div>
);

export const SkeletonCard: React.FC<{ className?: string }> = ({ className }) => (
  <div
    className={cn(
      'border border-gray-700 rounded-xl p-6 space-y-4',
      className
    )}
  >
    <Skeleton variant="rounded" height={200} />
    <SkeletonText lines={2} />
    <div className="flex gap-2">
      <Skeleton variant="rounded" width={80} height={32} />
      <Skeleton variant="rounded" width={80} height={32} />
    </div>
  </div>
);

export const SkeletonAvatar: React.FC<{
  size?: number;
  className?: string;
}> = ({ size = 40, className }) => (
  <Skeleton
    variant="circular"
    width={size}
    height={size}
    className={className}
  />
);

export const SkeletonButton: React.FC<{
  width?: string | number;
  className?: string;
}> = ({ width = 120, className }) => (
  <Skeleton variant="rounded" width={width} height={40} className={className} />
);

export default Skeleton;
