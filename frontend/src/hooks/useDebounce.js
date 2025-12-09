import { useState, useEffect } from 'react';

/**
 * useDebounce - Custom hook for debouncing values
 *
 * Delays updating a value until after a specified delay has elapsed
 * since the last time the value changed. Useful for optimizing
 * expensive operations like API calls or search filters.
 *
 * @param {*} value - The value to debounce
 * @param {number} delay - Delay in milliseconds (default: 500ms)
 * @returns {*} - The debounced value
 *
 * @example
 * const [searchTerm, setSearchTerm] = useState('');
 * const debouncedSearch = useDebounce(searchTerm, 300);
 *
 * useEffect(() => {
 *   // API call only fires after user stops typing for 300ms
 *   fetchSearchResults(debouncedSearch);
 * }, [debouncedSearch]);
 *
 * @author Frontend Squad - Component Architect
 * @version 1.0.0
 */
export function useDebounce(value, delay = 500) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    // Set timeout to update debounced value
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    // Cleanup function to cancel the timeout if value changes
    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}
