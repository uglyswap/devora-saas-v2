/**
 * useAIChat Hook
 * Agent: AI Chat Engineer
 *
 * Hook principal pour interagir avec le système de chat AI
 */

import { useCallback, useEffect, useState } from 'react';
import {
  useAIChatStore,
  selectCurrentSession,
  selectCurrentMessages,
  selectIsProcessing,
  selectHasPendingPlan,
} from '../stores/aiChatStore';
import type { ChatOptions, SuggestedPrompt } from '../types/chat.types';

export interface UseAIChatReturn {
  // State
  currentSession: ReturnType<typeof selectCurrentSession>;
  messages: ReturnType<typeof selectCurrentMessages>;
  isProcessing: boolean;
  isStreaming: boolean;
  isThinking: boolean;
  streamingContent: string;
  currentExecutionPlan: ReturnType<typeof useAIChatStore>['currentExecutionPlan'];
  hasPendingPlan: boolean;
  error: string | null;
  suggestions: SuggestedPrompt[];

  // Actions
  sendMessage: (message: string, options?: ChatOptions) => Promise<void>;
  approvePlan: (planId: string) => Promise<void>;
  rejectPlan: (planId: string, reason?: string) => void;
  modifyPlan: (planId: string, modifications: any) => void;
  cancelExecution: () => void;
  clearError: () => void;

  // Session Management
  createNewSession: (projectId?: string, title?: string) => void;
  switchSession: (sessionId: string) => void;
  deleteSession: (sessionId: string) => void;
  updateSessionTitle: (sessionId: string, title: string) => void;

  // Utility
  canSendMessage: boolean;
  hasHistory: boolean;
}

export const useAIChat = (): UseAIChatReturn => {
  const {
    sessions,
    currentSessionId,
    isStreaming,
    isThinking,
    streamingContent,
    currentExecutionPlan,
    error,
    suggestions,
    sendMessage,
    approvePlan,
    rejectPlan,
    modifyPlan,
    cancelExecution,
    clearError,
    createSession,
    switchSession,
    deleteSession,
    updateSessionTitle,
    getCurrentSession,
  } = useAIChatStore();

  const currentSession = useAIChatStore(selectCurrentSession);
  const messages = useAIChatStore(selectCurrentMessages);
  const isProcessing = useAIChatStore(selectIsProcessing);
  const hasPendingPlan = useAIChatStore(selectHasPendingPlan);

  // Derived state
  const canSendMessage = !isProcessing && !hasPendingPlan;
  const hasHistory = messages.length > 0;

  // Create session if none exists
  useEffect(() => {
    if (!currentSessionId && sessions.size === 0) {
      createSession();
    }
  }, [currentSessionId, sessions.size, createSession]);

  // Session management callbacks
  const createNewSession = useCallback(
    (projectId?: string, title?: string) => {
      createSession(projectId, title);
    },
    [createSession]
  );

  const handleSwitchSession = useCallback(
    (sessionId: string) => {
      switchSession(sessionId);
    },
    [switchSession]
  );

  const handleDeleteSession = useCallback(
    (sessionId: string) => {
      deleteSession(sessionId);
    },
    [deleteSession]
  );

  const handleUpdateSessionTitle = useCallback(
    (sessionId: string, title: string) => {
      updateSessionTitle(sessionId, title);
    },
    [updateSessionTitle]
  );

  // Message handling
  const handleSendMessage = useCallback(
    async (message: string, options?: ChatOptions) => {
      if (!canSendMessage) return;
      await sendMessage(message, options);
    },
    [canSendMessage, sendMessage]
  );

  // Plan handling
  const handleApprovePlan = useCallback(
    async (planId: string) => {
      await approvePlan(planId);
    },
    [approvePlan]
  );

  const handleRejectPlan = useCallback(
    (planId: string, reason?: string) => {
      rejectPlan(planId, reason);
    },
    [rejectPlan]
  );

  const handleModifyPlan = useCallback(
    (planId: string, modifications: any) => {
      modifyPlan(planId, modifications);
    },
    [modifyPlan]
  );

  return {
    // State
    currentSession,
    messages,
    isProcessing,
    isStreaming,
    isThinking,
    streamingContent,
    currentExecutionPlan,
    hasPendingPlan,
    error,
    suggestions,

    // Actions
    sendMessage: handleSendMessage,
    approvePlan: handleApprovePlan,
    rejectPlan: handleRejectPlan,
    modifyPlan: handleModifyPlan,
    cancelExecution,
    clearError,

    // Session Management
    createNewSession,
    switchSession: handleSwitchSession,
    deleteSession: handleDeleteSession,
    updateSessionTitle: handleUpdateSessionTitle,

    // Utility
    canSendMessage,
    hasHistory,
  };
};

export default useAIChat;
