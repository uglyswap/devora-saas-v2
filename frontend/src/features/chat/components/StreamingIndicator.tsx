/**
 * StreamingIndicator Component
 * Agent: AI Chat Engineer
 *
 * Indicateur de streaming avec animation de typing
 */

import React from 'react';

export interface StreamingIndicatorProps {
  isThinking?: boolean;
  text?: string;
  className?: string;
}

export const StreamingIndicator: React.FC<StreamingIndicatorProps> = ({
  isThinking = false,
  text,
  className = '',
}) => {
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      {isThinking ? (
        <>
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
          <span className="text-sm text-gray-500">Réflexion en cours...</span>
        </>
      ) : (
        <>
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" style={{ animationDelay: '200ms' }} />
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" style={{ animationDelay: '400ms' }} />
          </div>
          <span className="text-sm text-gray-500">{text || 'Génération en cours...'}</span>
        </>
      )}
    </div>
  );
};

export default StreamingIndicator;
