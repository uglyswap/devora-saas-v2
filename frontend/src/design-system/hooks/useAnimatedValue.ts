/**
 * Devora Design System - Animated Value Hook
 * Custom hook for spring animations on numeric values
 */

import { useSpring, useTransform, MotionValue } from 'framer-motion';
import { useEffect } from 'react';

export interface AnimatedValueOptions {
  stiffness?: number;
  damping?: number;
  mass?: number;
  from?: number;
  to: number;
}

export const useAnimatedValue = (
  value: number,
  options: Omit<AnimatedValueOptions, 'to'> = {}
): MotionValue<number> => {
  const {
    stiffness = 300,
    damping = 30,
    mass = 1,
    from = 0,
  } = options;

  const springValue = useSpring(from, {
    stiffness,
    damping,
    mass,
  });

  useEffect(() => {
    springValue.set(value);
  }, [value, springValue]);

  return springValue;
};

// Hook for animated counter
export const useAnimatedCounter = (
  targetValue: number,
  options: Omit<AnimatedValueOptions, 'to'> = {}
) => {
  const animatedValue = useAnimatedValue(targetValue, options);

  return useTransform(animatedValue, (latest) => Math.round(latest));
};

// Hook for animated percentage
export const useAnimatedPercentage = (
  targetValue: number,
  options: Omit<AnimatedValueOptions, 'to'> = {}
) => {
  const animatedValue = useAnimatedValue(targetValue, options);

  return useTransform(
    animatedValue,
    (latest) => `${Math.round(latest)}%`
  );
};

// Hook for animated currency
export const useAnimatedCurrency = (
  targetValue: number,
  currency: string = '$',
  options: Omit<AnimatedValueOptions, 'to'> = {}
) => {
  const animatedValue = useAnimatedValue(targetValue, options);

  return useTransform(
    animatedValue,
    (latest) => `${currency}${latest.toFixed(2)}`
  );
};

// Hook for animated progress (0-100)
export const useAnimatedProgress = (
  targetValue: number,
  options: Omit<AnimatedValueOptions, 'to'> = {}
) => {
  const clampedValue = Math.max(0, Math.min(100, targetValue));
  return useAnimatedValue(clampedValue, options);
};

// Hook for animated scroll progress
export const useScrollProgress = (
  element?: HTMLElement | null
): MotionValue<number> => {
  const springValue = useSpring(0, {
    stiffness: 100,
    damping: 30,
  });

  useEffect(() => {
    const handleScroll = () => {
      const target = element || document.documentElement;
      const scrollHeight = target.scrollHeight - target.clientHeight;
      const scrollTop = element ? element.scrollTop : window.scrollY;
      const progress = (scrollTop / scrollHeight) * 100;

      springValue.set(Math.max(0, Math.min(100, progress)));
    };

    const scrollTarget = element || window;
    scrollTarget.addEventListener('scroll', handleScroll);
    handleScroll(); // Initial calculation

    return () => {
      scrollTarget.removeEventListener('scroll', handleScroll);
    };
  }, [element, springValue]);

  return springValue;
};

// Hook for animated mouse position
export const useMousePosition = (
  smooth: boolean = true
): { x: MotionValue<number>; y: MotionValue<number> } => {
  const x = smooth
    ? useSpring(0, { stiffness: 300, damping: 30 })
    : useSpring(0);

  const y = smooth
    ? useSpring(0, { stiffness: 300, damping: 30 })
    : useSpring(0);

  useEffect(() => {
    const handleMouseMove = (event: MouseEvent) => {
      x.set(event.clientX);
      y.set(event.clientY);
    };

    window.addEventListener('mousemove', handleMouseMove);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
    };
  }, [x, y]);

  return { x, y };
};

// Hook for parallax effect
export const useParallax = (
  value: MotionValue<number>,
  distance: number = 50
): MotionValue<number> => {
  return useTransform(value, [0, 1], [-distance, distance]);
};

// Hook for scale based on scroll
export const useScrollScale = (
  threshold: number = 100
): MotionValue<number> => {
  const scrollY = useSpring(0, { stiffness: 100, damping: 30 });

  useEffect(() => {
    const handleScroll = () => {
      scrollY.set(window.scrollY);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [scrollY]);

  return useTransform(
    scrollY,
    [0, threshold],
    [1, 0.95]
  );
};

// Hook for opacity based on scroll
export const useScrollOpacity = (
  threshold: number = 100
): MotionValue<number> => {
  const scrollY = useSpring(0, { stiffness: 100, damping: 30 });

  useEffect(() => {
    const handleScroll = () => {
      scrollY.set(window.scrollY);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [scrollY]);

  return useTransform(
    scrollY,
    [0, threshold],
    [1, 0]
  );
};
