import { useState, useEffect } from 'react';

/**
 * useKeyPress - Custom hook to detect keyboard key presses
 *
 * Tracks whether a specific key is currently pressed.
 *
 * @param {string} targetKey - The key to track (e.g., 'Enter', 'Escape', 'a')
 * @returns {boolean} - Whether the key is pressed
 *
 * @example
 * const enterPressed = useKeyPress('Enter');
 * const escPressed = useKeyPress('Escape');
 *
 * useEffect(() => {
 *   if (enterPressed) {
 *     submitForm();
 *   }
 *   if (escPressed) {
 *     closeModal();
 *   }
 * }, [enterPressed, escPressed]);
 *
 * @author Frontend Squad - Component Architect
 * @version 1.0.0
 */
export function useKeyPress(targetKey) {
  const [keyPressed, setKeyPressed] = useState(false);

  useEffect(() => {
    const downHandler = ({ key }) => {
      if (key === targetKey) {
        setKeyPressed(true);
      }
    };

    const upHandler = ({ key }) => {
      if (key === targetKey) {
        setKeyPressed(false);
      }
    };

    window.addEventListener('keydown', downHandler);
    window.addEventListener('keyup', upHandler);

    return () => {
      window.removeEventListener('keydown', downHandler);
      window.removeEventListener('keyup', upHandler);
    };
  }, [targetKey]);

  return keyPressed;
}

/**
 * useKeyCombo - Detect keyboard shortcuts (combinations)
 *
 * @param {string[]} keys - Array of keys that must be pressed together
 * @param {Function} callback - Function to call when combo is pressed
 *
 * @example
 * useKeyCombo(['Control', 's'], (e) => {
 *   e.preventDefault();
 *   saveDocument();
 * });
 */
export function useKeyCombo(keys, callback) {
  useEffect(() => {
    const pressedKeys = new Set();

    const downHandler = (e) => {
      pressedKeys.add(e.key);

      // Check if all required keys are pressed
      const allPressed = keys.every(key => pressedKeys.has(key));

      if (allPressed) {
        callback(e);
      }
    };

    const upHandler = (e) => {
      pressedKeys.delete(e.key);
    };

    const blurHandler = () => {
      pressedKeys.clear();
    };

    window.addEventListener('keydown', downHandler);
    window.addEventListener('keyup', upHandler);
    window.addEventListener('blur', blurHandler);

    return () => {
      window.removeEventListener('keydown', downHandler);
      window.removeEventListener('keyup', upHandler);
      window.removeEventListener('blur', blurHandler);
    };
  }, [keys, callback]);
}
