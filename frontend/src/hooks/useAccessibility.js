/**
 * Devora Accessibility Hooks
 *
 * Collection of React hooks for implementing WCAG 2.1 AA accessibility features
 */

import { useEffect, useRef, useCallback, useState } from 'react';

/**
 * useFocusTrap
 *
 * Traps focus within a container (useful for modals/dialogs)
 * Implements WCAG 2.1.2: No Keyboard Trap
 *
 * @param {RefObject} containerRef - Ref to the container element
 * @param {boolean} isActive - Whether the trap is active
 *
 * @example
 * const dialogRef = useRef(null);
 * useFocusTrap(dialogRef, isOpen);
 */
export function useFocusTrap(containerRef, isActive = true) {
  useEffect(() => {
    if (!isActive || !containerRef.current) return;

    const container = containerRef.current;
    const focusableElements = container.querySelectorAll(
      'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
    );

    if (focusableElements.length === 0) return;

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    // Focus first element when trap activates
    firstElement.focus();

    const handleTabKey = (e) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey) {
        // Shift + Tab
        if (document.activeElement === firstElement) {
          e.preventDefault();
          lastElement.focus();
        }
      } else {
        // Tab
        if (document.activeElement === lastElement) {
          e.preventDefault();
          firstElement.focus();
        }
      }
    };

    container.addEventListener('keydown', handleTabKey);

    return () => {
      container.removeEventListener('keydown', handleTabKey);
    };
  }, [containerRef, isActive]);
}

/**
 * useKeyboardNavigation
 *
 * Adds keyboard navigation to custom components
 * Supports Arrow keys, Home, End, Enter, Space
 *
 * @param {RefObject} listRef - Ref to the list/menu container
 * @param {Object} options - Configuration options
 * @param {function} options.onSelect - Callback when item is selected
 * @param {string} options.orientation - 'vertical' or 'horizontal'
 * @param {boolean} options.loop - Whether navigation loops
 *
 * @example
 * const menuRef = useRef(null);
 * useKeyboardNavigation(menuRef, {
 *   onSelect: (index) => handleSelect(index),
 *   orientation: 'vertical',
 *   loop: true
 * });
 */
export function useKeyboardNavigation(listRef, options = {}) {
  const {
    onSelect,
    orientation = 'vertical',
    loop = true
  } = options;

  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (!listRef.current) return;

    const list = listRef.current;
    const items = Array.from(list.querySelectorAll('[role="option"], [role="menuitem"], [role="tab"]'));

    if (items.length === 0) return;

    const handleKeyDown = (e) => {
      let nextIndex = currentIndex;

      switch (e.key) {
        case 'ArrowDown':
          if (orientation === 'vertical') {
            e.preventDefault();
            nextIndex = currentIndex + 1;
            if (nextIndex >= items.length) {
              nextIndex = loop ? 0 : items.length - 1;
            }
          }
          break;

        case 'ArrowUp':
          if (orientation === 'vertical') {
            e.preventDefault();
            nextIndex = currentIndex - 1;
            if (nextIndex < 0) {
              nextIndex = loop ? items.length - 1 : 0;
            }
          }
          break;

        case 'ArrowRight':
          if (orientation === 'horizontal') {
            e.preventDefault();
            nextIndex = currentIndex + 1;
            if (nextIndex >= items.length) {
              nextIndex = loop ? 0 : items.length - 1;
            }
          }
          break;

        case 'ArrowLeft':
          if (orientation === 'horizontal') {
            e.preventDefault();
            nextIndex = currentIndex - 1;
            if (nextIndex < 0) {
              nextIndex = loop ? items.length - 1 : 0;
            }
          }
          break;

        case 'Home':
          e.preventDefault();
          nextIndex = 0;
          break;

        case 'End':
          e.preventDefault();
          nextIndex = items.length - 1;
          break;

        case 'Enter':
        case ' ':
          e.preventDefault();
          if (onSelect) {
            onSelect(currentIndex);
          }
          return;

        default:
          return;
      }

      setCurrentIndex(nextIndex);
      items[nextIndex].focus();
    };

    list.addEventListener('keydown', handleKeyDown);

    return () => {
      list.removeEventListener('keydown', handleKeyDown);
    };
  }, [listRef, currentIndex, orientation, loop, onSelect]);

  return { currentIndex, setCurrentIndex };
}

/**
 * useAriaAnnouncement
 *
 * Announces messages to screen readers via live regions
 * Implements WCAG 4.1.3: Status Messages
 *
 * @param {string} politeness - 'polite' or 'assertive'
 *
 * @returns {function} announce - Function to announce a message
 *
 * @example
 * const announce = useAriaAnnouncement('polite');
 * announce('Form submitted successfully');
 */
export function useAriaAnnouncement(politeness = 'polite') {
  const announcerRef = useRef(null);

  useEffect(() => {
    // Create live region if it doesn't exist
    if (!announcerRef.current) {
      const announcer = document.createElement('div');
      announcer.setAttribute('role', 'status');
      announcer.setAttribute('aria-live', politeness);
      announcer.setAttribute('aria-atomic', 'true');
      announcer.className = 'sr-only';
      document.body.appendChild(announcer);
      announcerRef.current = announcer;
    }

    return () => {
      if (announcerRef.current) {
        document.body.removeChild(announcerRef.current);
        announcerRef.current = null;
      }
    };
  }, [politeness]);

  const announce = useCallback((message) => {
    if (!announcerRef.current) return;

    // Clear previous message
    announcerRef.current.textContent = '';

    // Set new message after a brief delay to ensure screen readers detect the change
    setTimeout(() => {
      if (announcerRef.current) {
        announcerRef.current.textContent = message;
      }
    }, 100);
  }, []);

  return announce;
}

/**
 * useReducedMotion
 *
 * Detects user's motion preferences
 * Implements WCAG 2.3.3: Animation from Interactions
 *
 * @returns {boolean} prefersReducedMotion
 *
 * @example
 * const prefersReducedMotion = useReducedMotion();
 * const animationClass = prefersReducedMotion ? '' : 'animate-fade-in';
 */
export function useReducedMotion() {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(
    () => window.matchMedia('(prefers-reduced-motion: reduce)').matches
  );

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');

    const handleChange = (e) => {
      setPrefersReducedMotion(e.matches);
    };

    // Modern browsers
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    } else {
      // Fallback for older browsers
      mediaQuery.addListener(handleChange);
      return () => mediaQuery.removeListener(handleChange);
    }
  }, []);

  return prefersReducedMotion;
}

/**
 * useEscapeKey
 *
 * Handles Escape key press (useful for closing modals)
 *
 * @param {function} callback - Function to call when Escape is pressed
 * @param {boolean} isActive - Whether the handler is active
 *
 * @example
 * useEscapeKey(() => setIsOpen(false), isOpen);
 */
export function useEscapeKey(callback, isActive = true) {
  useEffect(() => {
    if (!isActive) return;

    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        callback();
      }
    };

    document.addEventListener('keydown', handleEscape);

    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  }, [callback, isActive]);
}

/**
 * useAriaInvalid
 *
 * Manages aria-invalid state for form fields
 *
 * @param {boolean} hasError - Whether the field has an error
 *
 * @returns {Object} ARIA attributes
 *
 * @example
 * const ariaProps = useAriaInvalid(!!errors.email);
 * <input {...ariaProps} />
 */
export function useAriaInvalid(hasError) {
  return {
    'aria-invalid': hasError ? 'true' : 'false'
  };
}

/**
 * useAriaDescribedBy
 *
 * Manages aria-describedby for form fields with hints/errors
 *
 * @param {string} baseId - Base ID for the field
 * @param {Object} options - Options
 * @param {boolean} options.hasHint - Whether there's a hint
 * @param {boolean} options.hasError - Whether there's an error
 *
 * @returns {Object} IDs and ARIA attributes
 *
 * @example
 * const { ariaDescribedBy, hintId, errorId } = useAriaDescribedBy('email', {
 *   hasHint: true,
 *   hasError: !!errors.email
 * });
 * <input aria-describedby={ariaDescribedBy} />
 * <span id={hintId}>Hint text</span>
 * {error && <span id={errorId}>{error}</span>}
 */
export function useAriaDescribedBy(baseId, options = {}) {
  const { hasHint = false, hasError = false } = options;

  const hintId = `${baseId}-hint`;
  const errorId = `${baseId}-error`;

  const ids = [];
  if (hasHint) ids.push(hintId);
  if (hasError) ids.push(errorId);

  return {
    ariaDescribedBy: ids.length > 0 ? ids.join(' ') : undefined,
    hintId,
    errorId
  };
}

/**
 * useKeyboardFocus
 *
 * Detects whether user is navigating with keyboard
 * Adds 'user-is-tabbing' class to body for custom focus styles
 *
 * @example
 * useKeyboardFocus();
 */
export function useKeyboardFocus() {
  useEffect(() => {
    const handleFirstTab = (e) => {
      if (e.key === 'Tab') {
        document.body.classList.add('user-is-tabbing');
        window.removeEventListener('keydown', handleFirstTab);
        window.addEventListener('mousedown', handleMouseDownOnce);
      }
    };

    const handleMouseDownOnce = () => {
      document.body.classList.remove('user-is-tabbing');
      window.removeEventListener('mousedown', handleMouseDownOnce);
      window.addEventListener('keydown', handleFirstTab);
    };

    window.addEventListener('keydown', handleFirstTab);

    return () => {
      window.removeEventListener('keydown', handleFirstTab);
      window.removeEventListener('mousedown', handleMouseDownOnce);
    };
  }, []);
}

/**
 * useScrollLock
 *
 * Locks body scroll when modals are open
 * Maintains scroll position and prevents background scrolling
 *
 * @param {boolean} isLocked - Whether scroll should be locked
 *
 * @example
 * useScrollLock(isModalOpen);
 */
export function useScrollLock(isLocked) {
  useEffect(() => {
    if (!isLocked) return;

    const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;
    const originalOverflow = document.body.style.overflow;
    const originalPaddingRight = document.body.style.paddingRight;

    // Lock scroll
    document.body.style.overflow = 'hidden';
    document.body.style.paddingRight = `${scrollbarWidth}px`;

    return () => {
      // Restore scroll
      document.body.style.overflow = originalOverflow;
      document.body.style.paddingRight = originalPaddingRight;
    };
  }, [isLocked]);
}

/**
 * useAutoId
 *
 * Generates unique IDs for form elements
 * Useful for label associations
 *
 * @param {string} prefix - Prefix for the ID
 *
 * @returns {string} Unique ID
 *
 * @example
 * const id = useAutoId('email');
 * <label htmlFor={id}>Email</label>
 * <input id={id} />
 */
let idCounter = 0;

export function useAutoId(prefix = 'field') {
  const idRef = useRef(null);

  if (idRef.current === null) {
    idRef.current = `${prefix}-${++idCounter}`;
  }

  return idRef.current;
}

/**
 * useSkipLink
 *
 * Manages skip link functionality
 * Focuses main content when skip link is clicked
 *
 * @returns {Object} Skip link props and main content props
 *
 * @example
 * const { skipLinkProps, mainContentProps } = useSkipLink();
 * <a {...skipLinkProps}>Skip to main content</a>
 * <main {...mainContentProps}>...</main>
 */
export function useSkipLink() {
  const mainContentId = 'main-content';

  const handleSkipClick = (e) => {
    e.preventDefault();
    const mainContent = document.getElementById(mainContentId);
    if (mainContent) {
      mainContent.focus();
      mainContent.scrollIntoView();
    }
  };

  return {
    skipLinkProps: {
      href: `#${mainContentId}`,
      onClick: handleSkipClick,
      className: 'skip-link'
    },
    mainContentProps: {
      id: mainContentId,
      tabIndex: -1
    }
  };
}

/**
 * useContrastChecker
 *
 * Checks color contrast ratios (development helper)
 * Warns in console if contrast is insufficient
 *
 * @param {string} foreground - Foreground color (hex)
 * @param {string} background - Background color (hex)
 * @param {number} minRatio - Minimum ratio (4.5 for text, 3 for large text/UI)
 *
 * @example
 * useContrastChecker('#333333', '#ffffff', 4.5);
 */
export function useContrastChecker(foreground, background, minRatio = 4.5) {
  useEffect(() => {
    if (process.env.NODE_ENV !== 'development') return;

    const hexToRgb = (hex) => {
      const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
      return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
      } : null;
    };

    const getLuminance = (r, g, b) => {
      const [rs, gs, bs] = [r, g, b].map(c => {
        c = c / 255;
        return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
      });
      return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
    };

    const getContrastRatio = (fg, bg) => {
      const fgRgb = hexToRgb(fg);
      const bgRgb = hexToRgb(bg);

      if (!fgRgb || !bgRgb) return null;

      const fgLum = getLuminance(fgRgb.r, fgRgb.g, fgRgb.b);
      const bgLum = getLuminance(bgRgb.r, bgRgb.g, bgRgb.b);

      const lighter = Math.max(fgLum, bgLum);
      const darker = Math.min(fgLum, bgLum);

      return (lighter + 0.05) / (darker + 0.05);
    };

    const ratio = getContrastRatio(foreground, background);

    if (ratio && ratio < minRatio) {
      console.warn(
        `⚠️ Insufficient contrast ratio: ${ratio.toFixed(2)}:1 (minimum: ${minRatio}:1)\n` +
        `Foreground: ${foreground}\n` +
        `Background: ${background}`
      );
    }
  }, [foreground, background, minRatio]);
}

/**
 * Default export with all hooks
 */
export default {
  useFocusTrap,
  useKeyboardNavigation,
  useAriaAnnouncement,
  useReducedMotion,
  useEscapeKey,
  useAriaInvalid,
  useAriaDescribedBy,
  useKeyboardFocus,
  useScrollLock,
  useAutoId,
  useSkipLink,
  useContrastChecker
};
