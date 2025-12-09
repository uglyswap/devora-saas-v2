import { useState, useEffect, useCallback } from 'react';

/**
 * useAsync - Custom hook for handling async operations
 *
 * Manages loading, error, and data states for async functions.
 * Prevents race conditions and memory leaks.
 *
 * @param {Function} asyncFunction - Async function to execute
 * @param {boolean} immediate - Execute immediately on mount (default: true)
 * @returns {Object} - { execute, loading, data, error, reset }
 *
 * @example
 * const { execute, loading, data, error } = useAsync(fetchUser);
 *
 * useEffect(() => {
 *   execute(userId);
 * }, [userId]);
 *
 * if (loading) return <Spinner />;
 * if (error) return <Error message={error} />;
 * return <UserProfile data={data} />;
 *
 * @author Frontend Squad - Component Architect
 * @version 1.0.0
 */
export function useAsync(asyncFunction, immediate = true) {
  const [status, setStatus] = useState('idle');
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  // The execute function wraps asyncFunction and handles setting state
  const execute = useCallback((...params) => {
    setStatus('pending');
    setData(null);
    setError(null);

    return asyncFunction(...params)
      .then((response) => {
        setData(response);
        setStatus('success');
        return response;
      })
      .catch((err) => {
        setError(err);
        setStatus('error');
        throw err;
      });
  }, [asyncFunction]);

  // Reset function to clear state
  const reset = useCallback(() => {
    setStatus('idle');
    setData(null);
    setError(null);
  }, []);

  // Call execute if we want to fire it right away
  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, [execute, immediate]);

  return {
    execute,
    loading: status === 'pending',
    data,
    error,
    status,
    reset
  };
}
