/**
 * Devora Design System - Micro Interaction Hook
 */
import { useAnimation } from 'framer-motion';
import { useCallback } from 'react';

export const useMicroInteraction = () => {
  const controls = useAnimation();

  const triggerRipple = useCallback(async () => {
    await controls.start({
      scale: [1, 1.5, 1],
      opacity: [0.5, 0, 0],
      transition: { duration: 0.4 },
    });
  }, [controls]);

  const triggerShake = useCallback(async () => {
    await controls.start({
      x: [0, -10, 10, -10, 10, 0],
      transition: { duration: 0.4 },
    });
  }, [controls]);

  const triggerBounce = useCallback(async () => {
    await controls.start({
      scale: [1, 1.2, 0.9, 1.1, 1],
      transition: { duration: 0.5 },
    });
  }, [controls]);

  const triggerPulse = useCallback(async () => {
    await controls.start({
      scale: [1, 1.05, 1],
      boxShadow: [
        '0 0 0 0 rgba(99, 102, 241, 0)',
        '0 0 0 10px rgba(99, 102, 241, 0.3)',
        '0 0 0 0 rgba(99, 102, 241, 0)',
      ],
      transition: { duration: 0.8, repeat: 2 },
    });
  }, [controls]);

  const triggerSuccess = useCallback(async () => {
    await controls.start({
      scale: [1, 1.1, 1],
      backgroundColor: ['transparent', 'rgba(16, 185, 129, 0.2)', 'transparent'],
      transition: { duration: 0.5 },
    });
  }, [controls]);

  const triggerError = useCallback(async () => {
    await controls.start({
      x: [0, -8, 8, -8, 8, 0],
      backgroundColor: ['transparent', 'rgba(239, 68, 68, 0.2)', 'transparent'],
      transition: { duration: 0.4 },
    });
  }, [controls]);

  return {
    controls,
    triggerRipple,
    triggerShake,
    triggerBounce,
    triggerPulse,
    triggerSuccess,
    triggerError,
  };
};

export default useMicroInteraction;
