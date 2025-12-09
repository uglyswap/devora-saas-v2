import { useState, useCallback } from 'react';

/**
 * useCopyToClipboard - Custom hook for copying text to clipboard
 *
 * Provides a function to copy text and tracks the copied state.
 *
 * @returns {[string | null, Function]} - [copiedText, copy]
 *
 * @example
 * const [copiedText, copy] = useCopyToClipboard();
 *
 * const handleCopy = () => {
 *   copy('Text to copy');
 *   // copiedText will be 'Text to copy' for 2 seconds
 * };
 *
 * return (
 *   <button onClick={handleCopy}>
 *     {copiedText ? 'Copied!' : 'Copy'}
 *   </button>
 * );
 *
 * @author Frontend Squad - Component Architect
 * @version 1.0.0
 */
export function useCopyToClipboard() {
  const [copiedText, setCopiedText] = useState(null);

  const copy = useCallback(async (text) => {
    if (!navigator?.clipboard) {
      console.warn('Clipboard API not available');
      return false;
    }

    try {
      await navigator.clipboard.writeText(text);
      setCopiedText(text);

      // Reset after 2 seconds
      setTimeout(() => {
        setCopiedText(null);
      }, 2000);

      return true;
    } catch (error) {
      console.error('Failed to copy text:', error);
      setCopiedText(null);
      return false;
    }
  }, []);

  return [copiedText, copy];
}
