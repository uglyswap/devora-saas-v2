/**
 * Devora Design System - Glow Effect Component
 * Premium glow effect for UI elements
 */

import React from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';
import { cn } from '../../lib/utils';

interface GlowEffectProps extends HTMLMotionProps<'div'> {
  children: React.ReactNode;
  className?: string;
  color?: 'primary' | 'accent' | 'secondary' | 'white';
  intensity?: 'low' | 'medium' | 'high';
  animated?: boolean;
}

export const GlowEffect: React.FC<GlowEffectProps> = ({
  children,
  className,
  color = 'primary',
  intensity = 'medium',
  animated = false,
  ...props
}) => {
  const getGlowColor = () => {
    const colors = {
      primary: '99, 102, 241',
      accent: '34, 211, 238',
      secondary: '168, 85, 247',
      white: '255, 255, 255',
    };
    return colors[color];
  };

  const getGlowIntensity = () => {
    const intensities = {
      low: { blur: '20px', opacity: 0.3 },
      medium: { blur: '30px', opacity: 0.5 },
      high: { blur: '40px', opacity: 0.7 },
    };
    return intensities[intensity];
  };

  const glowColor = getGlowColor();
  const { blur, opacity } = getGlowIntensity();

  return (
    <motion.div
      className={cn('relative', className)}
      {...props}
    >
      {/* Glow layer */}
      <motion.div
        className="absolute inset-0 rounded-lg pointer-events-none"
        style={{
          boxShadow: `0 0 ${blur} rgba(${glowColor}, ${opacity})`,
        }}
        animate={
          animated
            ? {
                boxShadow: [
                  `0 0 ${blur} rgba(${glowColor}, ${opacity * 0.7})`,
                  `0 0 ${blur} rgba(${glowColor}, ${opacity})`,
                  `0 0 ${blur} rgba(${glowColor}, ${opacity * 0.7})`,
                ],
              }
            : undefined
        }
        transition={
          animated
            ? {
                duration: 2,
                repeat: Infinity,
                ease: 'easeInOut',
              }
            : undefined
        }
      />

      {/* Content */}
      <div className="relative z-10">{children}</div>
    </motion.div>
  );
};

export default GlowEffect;
