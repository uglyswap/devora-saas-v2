/**
 * Performance Monitoring Utilities
 * Agent: Performance Engineer
 *
 * Objectif: Tracker et optimiser Core Web Vitals
 * - LCP: Largest Contentful Paint
 * - FID: First Input Delay
 * - CLS: Cumulative Layout Shift
 * - FCP: First Contentful Paint
 * - TTFB: Time to First Byte
 */

// ==========================================
// 1. WEB VITALS TRACKING
// ==========================================

export interface WebVitalsMetric {
  name: 'LCP' | 'FID' | 'CLS' | 'FCP' | 'TTFB';
  value: number;
  delta: number;
  id: string;
  rating: 'good' | 'needs-improvement' | 'poor';
}

/**
 * Track Core Web Vitals et envoie au backend pour analytics
 */
export const trackWebVitals = (metric: WebVitalsMetric): void => {
  const { name, value, rating } = metric;

  // Log en développement
  if (process.env.NODE_ENV === 'development') {
    console.log(`[Web Vitals] ${name}:`, {
      value: `${Math.round(value)}ms`,
      rating,
    });
  }

  // Envoyer au backend analytics en production
  if (process.env.NODE_ENV === 'production') {
    const endpoint = `${process.env.REACT_APP_API_URL}/api/analytics/web-vitals`;

    // Utiliser sendBeacon pour ne pas bloquer le thread
    if (navigator.sendBeacon) {
      const data = JSON.stringify({
        metric: name,
        value: Math.round(value),
        rating,
        timestamp: Date.now(),
        url: window.location.pathname,
        userAgent: navigator.userAgent,
      });

      navigator.sendBeacon(endpoint, data);
    } else {
      // Fallback pour anciens navigateurs
      fetch(endpoint, {
        method: 'POST',
        body: JSON.stringify({
          metric: name,
          value: Math.round(value),
          rating,
          timestamp: Date.now(),
          url: window.location.pathname,
        }),
        headers: { 'Content-Type': 'application/json' },
        keepalive: true,
      }).catch(() => {
        // Silently fail - ne pas bloquer l'app
      });
    }
  }
};

/**
 * Observer LCP (Largest Contentful Paint)
 * Target: < 2.5s (good), < 4s (needs improvement), > 4s (poor)
 */
export const observeLCP = (): void => {
  if (!('PerformanceObserver' in window)) return;

  try {
    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      const lastEntry = entries[entries.length - 1] as any;

      trackWebVitals({
        name: 'LCP',
        value: lastEntry.renderTime || lastEntry.loadTime,
        delta: 0,
        id: `lcp-${Date.now()}`,
        rating: getRating('LCP', lastEntry.renderTime || lastEntry.loadTime),
      });
    });

    observer.observe({ type: 'largest-contentful-paint', buffered: true });
  } catch (error) {
    console.error('[Performance] LCP observer error:', error);
  }
};

/**
 * Observer FID (First Input Delay)
 * Target: < 100ms (good), < 300ms (needs improvement), > 300ms (poor)
 */
export const observeFID = (): void => {
  if (!('PerformanceObserver' in window)) return;

  try {
    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      entries.forEach((entry: any) => {
        trackWebVitals({
          name: 'FID',
          value: entry.processingStart - entry.startTime,
          delta: 0,
          id: `fid-${Date.now()}`,
          rating: getRating('FID', entry.processingStart - entry.startTime),
        });
      });
    });

    observer.observe({ type: 'first-input', buffered: true });
  } catch (error) {
    console.error('[Performance] FID observer error:', error);
  }
};

/**
 * Observer CLS (Cumulative Layout Shift)
 * Target: < 0.1 (good), < 0.25 (needs improvement), > 0.25 (poor)
 */
export const observeCLS = (): void => {
  if (!('PerformanceObserver' in window)) return;

  let clsValue = 0;

  try {
    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      entries.forEach((entry: any) => {
        if (!entry.hadRecentInput) {
          clsValue += entry.value;

          trackWebVitals({
            name: 'CLS',
            value: clsValue,
            delta: entry.value,
            id: `cls-${Date.now()}`,
            rating: getRating('CLS', clsValue),
          });
        }
      });
    });

    observer.observe({ type: 'layout-shift', buffered: true });
  } catch (error) {
    console.error('[Performance] CLS observer error:', error);
  }
};

/**
 * Calculer le rating d'une métrique
 */
const getRating = (
  metric: WebVitalsMetric['name'],
  value: number
): WebVitalsMetric['rating'] => {
  const thresholds = {
    LCP: { good: 2500, poor: 4000 },
    FID: { good: 100, poor: 300 },
    CLS: { good: 0.1, poor: 0.25 },
    FCP: { good: 1800, poor: 3000 },
    TTFB: { good: 800, poor: 1800 },
  };

  const threshold = thresholds[metric];
  if (value <= threshold.good) return 'good';
  if (value <= threshold.poor) return 'needs-improvement';
  return 'poor';
};

// ==========================================
// 2. LAZY LOADING UTILITIES
// ==========================================

/**
 * Lazy load d'images avec Intersection Observer
 * Usage: <img data-src="image.jpg" class="lazy" />
 */
export const initLazyImages = (): void => {
  if (!('IntersectionObserver' in window)) {
    // Fallback: charger toutes les images immédiatement
    document.querySelectorAll('img[data-src]').forEach((img: any) => {
      img.src = img.dataset.src;
      if (img.dataset.srcset) {
        img.srcset = img.dataset.srcset;
      }
    });
    return;
  }

  const imageObserver = new IntersectionObserver(
    (entries, observer) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const img = entry.target as HTMLImageElement;

          // Charger l'image
          if (img.dataset.src) {
            img.src = img.dataset.src;
          }
          if (img.dataset.srcset) {
            img.srcset = img.dataset.srcset;
          }

          // Ajouter classe loaded
          img.classList.add('loaded');

          // Stop observer cette image
          observer.unobserve(img);
        }
      });
    },
    {
      rootMargin: '50px 0px', // Charger 50px avant d'être visible
      threshold: 0.01,
    }
  );

  // Observer toutes les images lazy
  document.querySelectorAll('img[data-src]').forEach((img) => {
    imageObserver.observe(img);
  });
};

/**
 * Lazy load de composants avec préchargement au hover
 */
export const createPreloadableComponent = <T extends React.ComponentType<any>>(
  importFunc: () => Promise<{ default: T }>
) => {
  let componentPromise: Promise<{ default: T }> | null = null;

  const preload = () => {
    if (!componentPromise) {
      componentPromise = importFunc();
    }
    return componentPromise;
  };

  const LazyComponent = React.lazy(preload);

  return {
    Component: LazyComponent,
    preload,
  };
};

// ==========================================
// 3. RESOURCE HINTS
// ==========================================

/**
 * Ajouter preconnect pour domaines externes
 */
export const addPreconnect = (url: string): void => {
  const link = document.createElement('link');
  link.rel = 'preconnect';
  link.href = url;
  link.crossOrigin = 'anonymous';
  document.head.appendChild(link);
};

/**
 * Ajouter dns-prefetch pour domaines externes
 */
export const addDnsPrefetch = (url: string): void => {
  const link = document.createElement('link');
  link.rel = 'dns-prefetch';
  link.href = url;
  document.head.appendChild(link);
};

/**
 * Preload d'une ressource critique
 */
export const preloadResource = (
  href: string,
  as: 'script' | 'style' | 'font' | 'image',
  type?: string
): void => {
  const link = document.createElement('link');
  link.rel = 'preload';
  link.href = href;
  link.as = as;
  if (type) link.type = type;
  if (as === 'font') link.crossOrigin = 'anonymous';
  document.head.appendChild(link);
};

// ==========================================
// 4. PERFORMANCE MONITORING
// ==========================================

/**
 * Mesurer le temps d'exécution d'une fonction
 */
export const measurePerformance = async <T>(
  name: string,
  fn: () => T | Promise<T>
): Promise<T> => {
  const startTime = performance.now();

  try {
    const result = await fn();
    const duration = performance.now() - startTime;

    console.log(`[Performance] ${name}: ${duration.toFixed(2)}ms`);

    // Marquer dans Performance API
    performance.mark(`${name}-end`);
    performance.measure(name, `${name}-start`, `${name}-end`);

    return result;
  } catch (error) {
    const duration = performance.now() - startTime;
    console.error(`[Performance] ${name} failed after ${duration.toFixed(2)}ms:`, error);
    throw error;
  }
};

/**
 * Observer les long tasks (> 50ms)
 */
export const observeLongTasks = (): void => {
  if (!('PerformanceObserver' in window)) return;

  try {
    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      entries.forEach((entry) => {
        if (entry.duration > 50) {
          console.warn(
            `[Performance] Long task detected: ${entry.duration.toFixed(2)}ms`,
            entry
          );
        }
      });
    });

    observer.observe({ type: 'longtask', buffered: true });
  } catch (error) {
    // Long tasks API pas supporté par tous les navigateurs
    console.log('[Performance] Long tasks API not supported');
  }
};

// ==========================================
// 5. MEMORY MONITORING
// ==========================================

/**
 * Monitorer l'usage mémoire
 */
export const checkMemoryUsage = (): void => {
  if ('memory' in performance) {
    const memory = (performance as any).memory;
    const usedMB = (memory.usedJSHeapSize / 1048576).toFixed(2);
    const totalMB = (memory.totalJSHeapSize / 1048576).toFixed(2);
    const limitMB = (memory.jsHeapSizeLimit / 1048576).toFixed(2);

    console.log(`[Memory] Used: ${usedMB}MB / Total: ${totalMB}MB / Limit: ${limitMB}MB`);

    // Alerte si > 80% de la limite
    const usagePercent = (memory.usedJSHeapSize / memory.jsHeapSizeLimit) * 100;
    if (usagePercent > 80) {
      console.warn(`[Memory] Warning: ${usagePercent.toFixed(1)}% memory usage`);
    }
  }
};

// ==========================================
// 6. INITIALIZATION
// ==========================================

/**
 * Initialiser tous les observers de performance
 */
export const initPerformanceMonitoring = (): void => {
  // Web Vitals
  observeLCP();
  observeFID();
  observeCLS();

  // Long tasks
  observeLongTasks();

  // Lazy images
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initLazyImages);
  } else {
    initLazyImages();
  }

  // Resource hints pour API
  if (process.env.REACT_APP_API_URL) {
    addPreconnect(process.env.REACT_APP_API_URL);
  }

  // Memory check en dev
  if (process.env.NODE_ENV === 'development') {
    setInterval(checkMemoryUsage, 30000); // Check toutes les 30s
  }

  console.log('[Performance] Monitoring initialized');
};

// ==========================================
// 7. REACT HELPERS
// ==========================================

import React, { useEffect, useCallback, useRef } from 'react';

/**
 * Hook pour lazy load au scroll
 */
export const useLazyLoad = (callback: () => void, offset = 200) => {
  const elementRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!elementRef.current) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          callback();
          observer.disconnect();
        }
      },
      { rootMargin: `${offset}px` }
    );

    observer.observe(elementRef.current);

    return () => observer.disconnect();
  }, [callback, offset]);

  return elementRef;
};

/**
 * Hook pour mesurer le render time
 */
export const useRenderTime = (componentName: string) => {
  const renderCountRef = useRef(0);

  useEffect(() => {
    renderCountRef.current += 1;
    const renderTime = performance.now();

    console.log(
      `[Render] ${componentName} rendered (${renderCountRef.current}x) at ${renderTime.toFixed(2)}ms`
    );
  });
};

/**
 * Hook pour debounce (optimiser re-renders)
 */
export const useDebounce = <T,>(value: T, delay: number): T => {
  const [debouncedValue, setDebouncedValue] = React.useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => clearTimeout(handler);
  }, [value, delay]);

  return debouncedValue;
};

export default {
  trackWebVitals,
  initPerformanceMonitoring,
  initLazyImages,
  measurePerformance,
  checkMemoryUsage,
  addPreconnect,
  addDnsPrefetch,
  preloadResource,
  useLazyLoad,
  useRenderTime,
  useDebounce,
};
