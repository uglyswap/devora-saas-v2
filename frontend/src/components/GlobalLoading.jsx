import * as React from 'react';
import { cn } from '@/lib/utils';

/**
 * Global loading indicator - Shows at top of page
 * Similar to GitHub/YouTube loading bar
 */
export function GlobalLoadingBar({ isLoading }) {
  const [progress, setProgress] = React.useState(0);
  const [visible, setVisible] = React.useState(false);

  React.useEffect(() => {
    if (isLoading) {
      setVisible(true);
      setProgress(0);

      // Simulate progress
      const interval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 90) return prev;
          return prev + Math.random() * 10;
        });
      }, 200);

      return () => clearInterval(interval);
    } else {
      // Complete and hide
      setProgress(100);
      const timeout = setTimeout(() => {
        setVisible(false);
        setProgress(0);
      }, 300);

      return () => clearTimeout(timeout);
    }
  }, [isLoading]);

  if (!visible) return null;

  return (
    <div className="fixed top-0 left-0 right-0 z-[9999] h-1 bg-transparent">
      <div
        className={cn(
          'h-full bg-gradient-to-r from-purple-500 via-pink-500 to-purple-500',
          'transition-all duration-200 ease-out',
          progress === 100 && 'opacity-0'
        )}
        style={{ width: `${progress}%` }}
      />
    </div>
  );
}

/**
 * Full screen loading overlay
 */
export function FullScreenLoader({ message = 'Chargement...' }) {
  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-gray-900/80 backdrop-blur-sm">
      <div className="flex flex-col items-center gap-4">
        <div className="relative">
          {/* Outer ring */}
          <div className="w-16 h-16 border-4 border-gray-700 rounded-full" />
          {/* Spinning ring */}
          <div className="absolute inset-0 w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin" />
          {/* Inner glow */}
          <div className="absolute inset-2 w-12 h-12 bg-purple-500/20 rounded-full blur-sm" />
        </div>
        <p className="text-gray-300 text-sm font-medium">{message}</p>
      </div>
    </div>
  );
}

/**
 * Skeleton loader component
 */
export function Skeleton({ className, ...props }) {
  return (
    <div
      className={cn('animate-pulse rounded-md bg-gray-800/50', className)}
      {...props}
    />
  );
}

/**
 * Card skeleton for loading states
 */
export function CardSkeleton() {
  return (
    <div className="p-4 rounded-lg border border-gray-700 bg-gray-800/30">
      <Skeleton className="h-4 w-3/4 mb-4" />
      <Skeleton className="h-3 w-full mb-2" />
      <Skeleton className="h-3 w-5/6 mb-4" />
      <div className="flex gap-2">
        <Skeleton className="h-6 w-16 rounded-full" />
        <Skeleton className="h-6 w-20 rounded-full" />
      </div>
    </div>
  );
}

/**
 * Table skeleton for loading states
 */
export function TableSkeleton({ rows = 5 }) {
  return (
    <div className="space-y-3">
      {/* Header */}
      <div className="flex gap-4 pb-3 border-b border-gray-700">
        <Skeleton className="h-4 w-1/4" />
        <Skeleton className="h-4 w-1/4" />
        <Skeleton className="h-4 w-1/4" />
        <Skeleton className="h-4 w-1/4" />
      </div>
      {/* Rows */}
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex gap-4 py-2">
          <Skeleton className="h-4 w-1/4" />
          <Skeleton className="h-4 w-1/4" />
          <Skeleton className="h-4 w-1/4" />
          <Skeleton className="h-4 w-1/4" />
        </div>
      ))}
    </div>
  );
}

/**
 * Editor skeleton for loading states
 */
export function EditorSkeleton() {
  return (
    <div className="flex h-full">
      {/* Sidebar */}
      <div className="w-64 border-r border-gray-700 p-4 space-y-3">
        <Skeleton className="h-8 w-full mb-4" />
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="flex items-center gap-2">
            <Skeleton className="h-4 w-4" />
            <Skeleton className="h-4 flex-1" />
          </div>
        ))}
      </div>
      {/* Main content */}
      <div className="flex-1 p-4">
        <div className="flex gap-2 mb-4">
          <Skeleton className="h-8 w-24" />
          <Skeleton className="h-8 w-24" />
          <Skeleton className="h-8 w-24" />
        </div>
        <div className="space-y-2">
          {Array.from({ length: 15 }).map((_, i) => (
            <Skeleton
              key={i}
              className="h-4"
              style={{ width: `${Math.random() * 40 + 40}%` }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

/**
 * Global loading context
 */
const LoadingContext = React.createContext(null);

export function LoadingProvider({ children }) {
  const [isLoading, setIsLoading] = React.useState(false);

  const setLoading = React.useCallback((loading) => {
    setIsLoading(loading);
  }, []);

  const withLoading = React.useCallback(async (promise) => {
    setIsLoading(true);
    try {
      const result = await promise;
      return result;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return (
    <LoadingContext.Provider value={{ isLoading, setLoading, withLoading }}>
      <GlobalLoadingBar isLoading={isLoading} />
      {children}
    </LoadingContext.Provider>
  );
}

export function useGlobalLoading() {
  const context = React.useContext(LoadingContext);
  if (!context) {
    throw new Error('useGlobalLoading must be used within LoadingProvider');
  }
  return context;
}
