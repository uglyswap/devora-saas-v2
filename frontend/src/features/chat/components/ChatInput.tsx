/**
 * ChatInput Component
 * Agent: AI Chat Engineer
 *
 * Zone de saisie pour envoyer des messages au chat
 */

import React, { useState, useRef, useEffect } from 'react';

export interface ChatInputProps {
  onSend: (message: string) => void;
  onCancel?: () => void;
  disabled?: boolean;
  isProcessing?: boolean;
  placeholder?: string;
  maxLength?: number;
  className?: string;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSend,
  onCancel,
  disabled = false,
  isProcessing = false,
  placeholder = 'Tapez votre message...',
  maxLength = 4000,
  className = '',
}) => {
  const [message, setMessage] = useState('');
  const [rows, setRows] = useState(1);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      const lineHeight = 24; // Approximate line height in pixels
      const maxRows = 10;
      const minRows = 1;

      const currentRows = Math.floor(textareaRef.current.scrollHeight / lineHeight);
      const newRows = Math.min(Math.max(currentRows, minRows), maxRows);

      setRows(newRows);
    }
  }, [message]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled && !isProcessing) {
      onSend(message.trim());
      setMessage('');
      setRows(1);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Submit on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleCancel = () => {
    onCancel?.();
  };

  const remainingChars = maxLength - message.length;
  const showCharCount = message.length > maxLength * 0.8;

  return (
    <form onSubmit={handleSubmit} className={`border-t bg-white ${className}`}>
      <div className="p-4">
        {/* Textarea */}
        <div className="relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={disabled || isProcessing}
            placeholder={placeholder}
            rows={rows}
            maxLength={maxLength}
            className={`w-full px-4 py-3 pr-24 border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              disabled || isProcessing ? 'bg-gray-50 cursor-not-allowed' : ''
            }`}
            style={{ minHeight: '52px', maxHeight: '240px' }}
          />

          {/* Character Count */}
          {showCharCount && (
            <div
              className={`absolute bottom-2 right-2 text-xs ${
                remainingChars < 0 ? 'text-red-500' : remainingChars < 100 ? 'text-yellow-600' : 'text-gray-400'
              }`}
            >
              {remainingChars}
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between mt-3">
          <div className="flex items-center gap-2">
            {/* Additional actions can go here */}
            <span className="text-xs text-gray-500">
              Appuyez sur <kbd className="px-1.5 py-0.5 bg-gray-100 border rounded text-xs">Entrée</kbd> pour
              envoyer, <kbd className="px-1.5 py-0.5 bg-gray-100 border rounded text-xs">Shift + Entrée</kbd>{' '}
              pour une nouvelle ligne
            </span>
          </div>

          <div className="flex items-center gap-2">
            {isProcessing && (
              <button
                type="button"
                onClick={handleCancel}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Annuler
              </button>
            )}
            <button
              type="submit"
              disabled={disabled || isProcessing || !message.trim() || remainingChars < 0}
              className={`px-4 py-2 text-sm font-medium text-white rounded-lg flex items-center gap-2 ${
                disabled || isProcessing || !message.trim() || remainingChars < 0
                  ? 'bg-gray-300 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700'
              }`}
            >
              {isProcessing ? (
                <>
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                      fill="none"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                  Génération...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                    />
                  </svg>
                  Envoyer
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </form>
  );
};

export default ChatInput;
