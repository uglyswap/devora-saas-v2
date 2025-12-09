/**
 * ChatMessage Component
 * Agent: AI Chat Engineer
 *
 * Affichage d'un message de chat avec support pour le streaming et les plans d'exécution
 */

import React, { useState } from 'react';
import type { AIChatMessage } from '../types/chat.types';
import { StreamingIndicator } from './StreamingIndicator';
import { ExecutionPlanCard } from './ExecutionPlanCard';

export interface ChatMessageProps {
  message: AIChatMessage;
  onApprovePlan?: (planId: string) => void;
  onRejectPlan?: (planId: string, reason?: string) => void;
  className?: string;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({
  message,
  onApprovePlan,
  onRejectPlan,
  className = '',
}) => {
  const [showMetadata, setShowMetadata] = useState(false);

  const isUser = message.role === 'user';
  const isAssistant = message.role === 'assistant';

  // Format timestamp
  const formatTime = (timestamp: number) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
  };

  // Parse markdown-style code blocks
  const parseContent = (content: string) => {
    const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g;
    const parts: Array<{ type: 'text' | 'code'; content: string; language?: string }> = [];
    let lastIndex = 0;
    let match;

    while ((match = codeBlockRegex.exec(content)) !== null) {
      // Add text before code block
      if (match.index > lastIndex) {
        parts.push({
          type: 'text',
          content: content.slice(lastIndex, match.index),
        });
      }

      // Add code block
      parts.push({
        type: 'code',
        content: match[2],
        language: match[1] || 'plaintext',
      });

      lastIndex = match.index + match[0].length;
    }

    // Add remaining text
    if (lastIndex < content.length) {
      parts.push({
        type: 'text',
        content: content.slice(lastIndex),
      });
    }

    return parts.length > 0 ? parts : [{ type: 'text' as const, content }];
  };

  const contentParts = parseContent(message.content);

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} ${className}`}>
      <div className={`max-w-[80%] ${isUser ? 'order-2' : 'order-1'}`}>
        {/* Message Bubble */}
        <div
          className={`rounded-lg px-4 py-3 ${
            isUser
              ? 'bg-blue-600 text-white'
              : message.metadata?.error
              ? 'bg-red-50 text-red-900 border border-red-200'
              : 'bg-gray-100 text-gray-900'
          }`}
        >
          {/* Thinking/Streaming Indicator */}
          {message.isThinking && <StreamingIndicator isThinking className="mb-2" />}
          {message.isStreaming && !message.isThinking && <StreamingIndicator className="mb-2" />}

          {/* Message Content */}
          <div className="space-y-2">
            {contentParts.map((part, index) => {
              if (part.type === 'code') {
                return (
                  <div key={index} className="my-2">
                    <div className="bg-gray-900 text-gray-100 rounded-md overflow-hidden">
                      <div className="bg-gray-800 px-3 py-1 text-xs font-mono flex items-center justify-between">
                        <span>{part.language}</span>
                        <button
                          onClick={() => navigator.clipboard.writeText(part.content)}
                          className="text-gray-400 hover:text-gray-200 text-xs"
                        >
                          Copier
                        </button>
                      </div>
                      <pre className="p-3 overflow-x-auto">
                        <code className="text-sm">{part.content}</code>
                      </pre>
                    </div>
                  </div>
                );
              }

              return (
                <div key={index} className="whitespace-pre-wrap break-words">
                  {part.content}
                </div>
              );
            })}
          </div>

          {/* Metadata */}
          {message.metadata && (
            <div className="mt-2 pt-2 border-t border-opacity-20">
              <button
                onClick={() => setShowMetadata(!showMetadata)}
                className="text-xs opacity-75 hover:opacity-100"
              >
                {showMetadata ? '▼' : '▶'} Détails
              </button>
              {showMetadata && (
                <div className="mt-2 text-xs space-y-1 opacity-75">
                  {message.metadata.model && <div>Modèle: {message.metadata.model}</div>}
                  {message.metadata.tokensUsed && <div>Tokens: {message.metadata.tokensUsed}</div>}
                  {message.metadata.duration && <div>Durée: {message.metadata.duration}ms</div>}
                  {message.metadata.filesAffected && message.metadata.filesAffected.length > 0 && (
                    <div>Fichiers: {message.metadata.filesAffected.join(', ')}</div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Timestamp */}
          <div className={`text-xs mt-2 ${isUser ? 'text-blue-200' : 'text-gray-500'}`}>
            {formatTime(message.timestamp)}
          </div>
        </div>

        {/* Execution Plan */}
        {message.executionPlan && isAssistant && (
          <div className="mt-3">
            <ExecutionPlanCard
              plan={message.executionPlan}
              onApprove={() => onApprovePlan?.(message.executionPlan!.id)}
              onReject={(reason) => onRejectPlan?.(message.executionPlan!.id, reason)}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatMessage;
