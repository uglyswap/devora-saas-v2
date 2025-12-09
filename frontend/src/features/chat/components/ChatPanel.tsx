/**
 * ChatPanel Component
 * Agent: AI Chat Engineer
 *
 * Panel principal du chat AI avec interface complète
 */

import React, { useRef, useEffect, useState } from 'react';
import { useAIChat } from '../hooks/useAIChat';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { SuggestedPrompts } from './SuggestedPrompts';
import type { SuggestedPrompt } from '../types/chat.types';

export interface ChatPanelProps {
  projectId?: string;
  isOpen?: boolean;
  onToggle?: () => void;
  className?: string;
}

export const ChatPanel: React.FC<ChatPanelProps> = ({
  projectId,
  isOpen = true,
  onToggle,
  className = '',
}) => {
  const {
    currentSession,
    messages,
    isProcessing,
    isStreaming,
    isThinking,
    currentExecutionPlan,
    hasPendingPlan,
    error,
    suggestions,
    sendMessage,
    approvePlan,
    rejectPlan,
    cancelExecution,
    clearError,
    createNewSession,
    updateSessionTitle,
  } = useAIChat();

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [showSuggestions, setShowSuggestions] = useState(messages.length === 0);
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [editedTitle, setEditedTitle] = useState('');

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Hide suggestions when messages exist
  useEffect(() => {
    if (messages.length > 0) {
      setShowSuggestions(false);
    }
  }, [messages.length]);

  // Create session if needed
  useEffect(() => {
    if (!currentSession) {
      createNewSession(projectId);
    }
  }, [currentSession, projectId, createNewSession]);

  const handleSendMessage = async (message: string) => {
    await sendMessage(message);
  };

  const handleSuggestionSelect = (prompt: SuggestedPrompt) => {
    handleSendMessage(prompt.text);
  };

  const handleStartTitleEdit = () => {
    if (currentSession) {
      setEditedTitle(currentSession.title);
      setIsEditingTitle(true);
    }
  };

  const handleSaveTitle = () => {
    if (currentSession && editedTitle.trim()) {
      updateSessionTitle(currentSession.id, editedTitle.trim());
    }
    setIsEditingTitle(false);
  };

  const handleCancelTitleEdit = () => {
    setIsEditingTitle(false);
    setEditedTitle('');
  };

  if (!isOpen) {
    return (
      <div className={`fixed right-4 bottom-4 ${className}`}>
        <button
          onClick={onToggle}
          className="w-14 h-14 bg-blue-600 hover:bg-blue-700 text-white rounded-full shadow-lg flex items-center justify-center"
          aria-label="Ouvrir le chat"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
            />
          </svg>
        </button>
      </div>
    );
  }

  return (
    <div className={`flex flex-col h-full bg-white border-l shadow-lg ${className}`}>
      {/* Header */}
      <div className="flex-shrink-0 px-4 py-3 border-b bg-gradient-to-r from-blue-600 to-blue-700 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3 flex-1 min-w-0">
            <svg className="w-6 h-6 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
              />
            </svg>
            {isEditingTitle ? (
              <input
                type="text"
                value={editedTitle}
                onChange={(e) => setEditedTitle(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleSaveTitle();
                  if (e.key === 'Escape') handleCancelTitleEdit();
                }}
                onBlur={handleSaveTitle}
                className="flex-1 px-2 py-1 text-sm bg-white text-gray-900 rounded focus:outline-none focus:ring-2 focus:ring-white"
                autoFocus
              />
            ) : (
              <button
                onClick={handleStartTitleEdit}
                className="flex-1 text-left font-semibold text-lg truncate hover:text-blue-100"
              >
                {currentSession?.title || 'Chat AI'}
              </button>
            )}
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => createNewSession(projectId)}
              className="p-2 hover:bg-blue-500 rounded"
              title="Nouvelle conversation"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
            </button>
            {onToggle && (
              <button onClick={onToggle} className="p-2 hover:bg-blue-500 rounded" title="Fermer">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
          </div>
        </div>

        {/* Status Indicator */}
        {(isProcessing || hasPendingPlan) && (
          <div className="mt-2 text-sm flex items-center gap-2">
            {isProcessing && (
              <>
                <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
                <span>{isThinking ? 'Réflexion...' : isStreaming ? 'Génération...' : 'Traitement...'}</span>
              </>
            )}
            {hasPendingPlan && (
              <>
                <div className="w-2 h-2 bg-yellow-300 rounded-full animate-pulse" />
                <span>Plan en attente de confirmation</span>
              </>
            )}
          </div>
        )}
      </div>

      {/* Error Banner */}
      {error && (
        <div className="flex-shrink-0 px-4 py-3 bg-red-50 border-b border-red-200">
          <div className="flex items-start justify-between gap-2">
            <div className="flex items-start gap-2 flex-1">
              <svg
                className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <div className="flex-1">
                <p className="text-sm font-medium text-red-800">Erreur</p>
                <p className="text-sm text-red-700 mt-1">{error}</p>
              </div>
            </div>
            <button onClick={clearError} className="text-red-600 hover:text-red-800">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      )}

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <svg
              className="w-16 h-16 text-gray-300 mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
              />
            </svg>
            <h3 className="text-lg font-semibold text-gray-700 mb-2">Comment puis-je vous aider ?</h3>
            <p className="text-sm text-gray-500 max-w-md">
              Posez-moi des questions sur votre code, demandez-moi de créer de nouvelles fonctionnalités, ou
              d'optimiser votre projet.
            </p>
          </div>
        ) : (
          messages.map((message) => (
            <ChatMessage
              key={message.id}
              message={message}
              onApprovePlan={approvePlan}
              onRejectPlan={rejectPlan}
            />
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggestions */}
      {showSuggestions && messages.length === 0 && (
        <div className="flex-shrink-0 px-4 pb-4">
          <SuggestedPrompts suggestions={suggestions} onSelect={handleSuggestionSelect} />
        </div>
      )}

      {/* Input */}
      <div className="flex-shrink-0">
        <ChatInput
          onSend={handleSendMessage}
          onCancel={cancelExecution}
          disabled={hasPendingPlan}
          isProcessing={isProcessing}
          placeholder={
            hasPendingPlan
              ? 'Veuillez approuver ou rejeter le plan d\'exécution...'
              : 'Décrivez ce que vous voulez créer ou modifier...'
          }
        />
      </div>
    </div>
  );
};

export default ChatPanel;
