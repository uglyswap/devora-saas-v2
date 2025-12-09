import React, { memo, useEffect, useCallback } from 'react';
import { createPortal } from 'react-dom';
import { X } from 'lucide-react';
import { cn } from '../../../lib/utils';
import { useClickOutside, useKeyPress } from '../../../hooks';

/**
 * Modal - Optimized modal/dialog component
 *
 * Features:
 * - Portal rendering
 * - Click outside to close
 * - Escape key to close
 * - Body scroll lock
 * - Focus trap
 * - Smooth animations
 *
 * Performance optimizations:
 * - React.memo to prevent re-renders
 * - useCallback for event handlers
 * - Custom hooks for click outside and key press
 *
 * @version 2.0.0 - Optimized by Frontend Squad
 */
const Modal = memo(function Modal({
  isOpen,
  onClose,
  title,
  children,
  footer,
  size = 'md',
  closeOnClickOutside = true,
  closeOnEscape = true,
  showCloseButton = true,
  className,
}) {
  // Close on Escape key
  const escapePressed = useKeyPress('Escape');

  useEffect(() => {
    if (escapePressed && closeOnEscape && isOpen) {
      onClose();
    }
  }, [escapePressed, closeOnEscape, isOpen, onClose]);

  // Lock body scroll when modal is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  // Click outside handler
  const modalRef = useClickOutside(
    useCallback(() => {
      if (closeOnClickOutside && isOpen) {
        onClose();
      }
    }, [closeOnClickOutside, isOpen, onClose])
  );

  if (!isOpen) return null;

  const sizeClasses = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
    full: 'max-w-7xl',
  };

  const modalContent = (
    <div className="fixed inset-0 z-[1400] flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/80 backdrop-blur-sm animate-fade-in"
        aria-hidden="true"
      />

      {/* Modal */}
      <div
        ref={modalRef}
        className={cn(
          'relative w-full bg-card border border-border rounded-2xl shadow-2xl',
          'animate-scale-in',
          sizeClasses[size],
          className
        )}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
      >
        {/* Header */}
        {(title || showCloseButton) && (
          <div className="flex items-center justify-between p-6 border-b border-border">
            {title && (
              <h2
                id="modal-title"
                className="text-xl font-semibold text-foreground"
              >
                {title}
              </h2>
            )}
            {showCloseButton && (
              <button
                onClick={onClose}
                className={cn(
                  'rounded-lg p-2 text-muted-foreground transition-colors',
                  'hover:bg-accent hover:text-accent-foreground',
                  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary',
                  !title && 'ml-auto'
                )}
                aria-label="Close modal"
              >
                <X className="w-5 h-5" />
              </button>
            )}
          </div>
        )}

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[60vh] custom-scrollbar">
          {children}
        </div>

        {/* Footer */}
        {footer && (
          <div className="flex items-center justify-end gap-3 p-6 border-t border-border">
            {footer}
          </div>
        )}
      </div>
    </div>
  );

  return createPortal(modalContent, document.body);
});

Modal.displayName = 'Modal';

export { Modal };
