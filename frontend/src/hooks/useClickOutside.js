import { useEffect, useRef } from 'react';

/**
 * useClickOutside - Custom hook to detect clicks outside an element
 *
 * Useful for closing modals, dropdowns, popovers when clicking outside.
 *
 * @param {Function} callback - Function to call when clicking outside
 * @returns {React.RefObject} - Ref to attach to the element
 *
 * @example
 * const DropdownMenu = () => {
 *   const [isOpen, setIsOpen] = useState(false);
 *   const menuRef = useClickOutside(() => setIsOpen(false));
 *
 *   return (
 *     <div ref={menuRef}>
 *       {isOpen && <Menu />}
 *     </div>
 *   );
 * };
 *
 * @author Frontend Squad - Component Architect
 * @version 1.0.0
 */
export function useClickOutside(callback) {
  const ref = useRef(null);

  useEffect(() => {
    const handleClick = (event) => {
      if (ref.current && !ref.current.contains(event.target)) {
        callback();
      }
    };

    // Bind the event listener
    document.addEventListener('mousedown', handleClick);
    document.addEventListener('touchstart', handleClick);

    // Cleanup
    return () => {
      document.removeEventListener('mousedown', handleClick);
      document.removeEventListener('touchstart', handleClick);
    };
  }, [callback]);

  return ref;
}
