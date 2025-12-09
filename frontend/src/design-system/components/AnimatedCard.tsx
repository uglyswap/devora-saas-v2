/**
 * Devora Design System - Animated Card Component
 */
import React from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';
import { cn } from '../../lib/utils';

interface AnimatedCardProps extends HTMLMotionProps<'div'> {
  children: React.ReactNode;
  className?: string;
  delay?: number;
  hover?: boolean;
  glow?: boolean;
}

export const AnimatedCard: React.FC<AnimatedCardProps> = ({
  children,
  className,
  delay = 0,
  hover = true,
  glow = false,
  ...props
}) => {
  return (
    <motion.div
      className={cn(
        'relative bg-gradient-to-br from-gray-800/50 to-gray-900/50',
        'border border-gray-700/50 rounded-xl p-6',
        'backdrop-blur-sm',
        glow && 'shadow-glow',
        className
      )}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{
        duration: 0.5,
        delay,
        ease: [0.25, 0.1, 0.25, 1],
      }}
      whileHover={
        hover
          ? {
              scale: 1.02,
              boxShadow: '0 20px 40px -20px rgba(99, 102, 241, 0.3)',
              borderColor: 'rgba(99, 102, 241, 0.5)',
            }
          : undefined
      }
      {...props}
    >
      {/* Glow effect on hover */}
      {hover && (
        <motion.div
          className="absolute inset-0 rounded-xl opacity-0 pointer-events-none"
          style={{
            background:
              'radial-gradient(circle at 50% 50%, rgba(99, 102, 241, 0.15), transparent 70%)',
          }}
          whileHover={{ opacity: 1 }}
        />
      )}
      <div className="relative z-10">{children}</div>
    </motion.div>
  );
};

export default AnimatedCard;
