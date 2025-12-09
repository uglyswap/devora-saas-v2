/**
 * AI Chat Store - Enhanced Zustand Store
 * Agent: AI Chat Engineer
 *
 * Store pour gérer les conversations AI avec plans d'exécution
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import { v4 as uuidv4 } from 'uuid';
import type {
  AIChatMessage,
  ChatSession,
  ExecutionPlan,
  FileChange,
  ChatRequest,
  ChatOptions,
  SuggestedPrompt,
  StreamChunk,
} from '../types/chat.types';
import type { ProjectFile } from '../../../types';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

// ============================================
// Types
// ============================================

interface AIEnhancedChatState {
  // Sessions
  sessions: Map<string, ChatSession>;
  currentSessionId: string | null;

  // Streaming
  isStreaming: boolean;
  streamingContent: string;
  isThinking: boolean;

  // Execution Plans
  currentExecutionPlan: ExecutionPlan | null;
  pendingPlans: Map<string, ExecutionPlan>;

  // UI State
  isConnected: boolean;
  error: string | null;
  suggestions: SuggestedPrompt[];

  // Actions - Session Management
  createSession: (projectId?: string, title?: string) => ChatSession;
  switchSession: (sessionId: string) => void;
  deleteSession: (sessionId: string) => void;
  getCurrentSession: () => ChatSession | null;
  updateSessionTitle: (sessionId: string, title: string) => void;

  // Actions - Messaging
  sendMessage: (message: string, options?: ChatOptions) => Promise<void>;
  addMessage: (sessionId: string, message: Omit<AIChatMessage, 'id' | 'timestamp'>) => void;
  updateMessage: (sessionId: string, messageId: string, updates: Partial<AIChatMessage>) => void;

  // Actions - Execution Plans
  createExecutionPlan: (plan: Omit<ExecutionPlan, 'id' | 'status'>) => ExecutionPlan;
  approvePlan: (planId: string) => Promise<void>;
  rejectPlan: (planId: string, reason?: string) => void;
  modifyPlan: (planId: string, modifications: Partial<ExecutionPlan>) => void;
  updatePlanStep: (planId: string, stepId: string, updates: any) => void;

  // Actions - Streaming
  handleStreamChunk: (chunk: StreamChunk) => void;
  startStreaming: () => void;
  stopStreaming: () => void;
  cancelExecution: () => void;

  // Actions - Utility
  clearError: () => void;
  setSuggestions: (suggestions: SuggestedPrompt[]) => void;
  reset: () => void;
}

// ============================================
// Initial State
// ============================================

const initialState = {
  sessions: new Map<string, ChatSession>(),
  currentSessionId: null,
  isStreaming: false,
  streamingContent: '',
  isThinking: false,
  currentExecutionPlan: null,
  pendingPlans: new Map<string, ExecutionPlan>(),
  isConnected: true,
  error: null,
  suggestions: [],
};

// ============================================
// Abort Controller
// ============================================

let abortController: AbortController | null = null;

// ============================================
// Store
// ============================================

export const useAIChatStore = create<AIEnhancedChatState>()(
  devtools(
    persist(
      immer((set, get) => ({
        ...initialState,

        // ========================================
        // Session Management
        // ========================================

        createSession: (projectId?: string, title?: string) => {
          const session: ChatSession = {
            id: uuidv4(),
            projectId,
            messages: [],
            title: title || 'Nouvelle conversation',
            createdAt: Date.now(),
            updatedAt: Date.now(),
            metadata: {
              model: 'gpt-4',
              totalTokensUsed: 0,
              totalDuration: 0,
              filesModified: new Set(),
            },
          };

          set((state) => {
            state.sessions.set(session.id, session);
            state.currentSessionId = session.id;
          });

          return session;
        },

        switchSession: (sessionId: string) => {
          set((state) => {
            if (state.sessions.has(sessionId)) {
              state.currentSessionId = sessionId;
              state.currentExecutionPlan = null;
              state.error = null;
            }
          });
        },

        deleteSession: (sessionId: string) => {
          set((state) => {
            state.sessions.delete(sessionId);
            if (state.currentSessionId === sessionId) {
              const remainingSessions = Array.from(state.sessions.keys());
              state.currentSessionId = remainingSessions[0] || null;
            }
          });
        },

        getCurrentSession: () => {
          const { currentSessionId, sessions } = get();
          if (!currentSessionId) return null;
          return sessions.get(currentSessionId) || null;
        },

        updateSessionTitle: (sessionId: string, title: string) => {
          set((state) => {
            const session = state.sessions.get(sessionId);
            if (session) {
              session.title = title;
              session.updatedAt = Date.now();
            }
          });
        },

        // ========================================
        // Messaging
        // ========================================

        sendMessage: async (message: string, options: ChatOptions = {}) => {
          const session = get().getCurrentSession();
          if (!session) {
            set({ error: 'Aucune session active' });
            return;
          }

          // Add user message
          const userMessage: AIChatMessage = {
            id: uuidv4(),
            role: 'user',
            content: message,
            timestamp: Date.now(),
          };

          get().addMessage(session.id, userMessage);

          // Start streaming
          get().startStreaming();

          // Create assistant message placeholder
          const assistantMessage: AIChatMessage = {
            id: uuidv4(),
            role: 'assistant',
            content: '',
            timestamp: Date.now(),
            isStreaming: true,
            isThinking: true,
          };

          get().addMessage(session.id, assistantMessage);

          try {
            abortController = new AbortController();

            const endpoint = `${API_URL}/api/chat`;
            const requestBody: ChatRequest = {
              message,
              sessionId: session.id,
              projectId: session.projectId,
              model: options.maxTokens ? 'gpt-4' : 'gpt-4',
              conversationHistory: session.messages.map((m) => ({
                role: m.role,
                content: m.content,
              })),
              options: {
                streaming: true,
                ...options,
              },
            };

            const response = await fetch(endpoint, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${localStorage.getItem('token')}`,
              },
              body: JSON.stringify(requestBody),
              signal: abortController.signal,
            });

            if (!response.ok) {
              throw new Error(`HTTP error! status: ${response.status}`);
            }

            const reader = response.body?.getReader();
            if (!reader) {
              throw new Error('No reader available');
            }

            const decoder = new TextDecoder();

            while (true) {
              const { done, value } = await reader.read();
              if (done) break;

              const chunk = decoder.decode(value, { stream: true });
              const lines = chunk.split('\n');

              for (const line of lines) {
                if (line.startsWith('data: ')) {
                  const data = line.slice(6);
                  if (data === '[DONE]') continue;

                  try {
                    const parsed: StreamChunk = JSON.parse(data);
                    get().handleStreamChunk(parsed);
                  } catch (e) {
                    // Ignore parse errors for incomplete chunks
                  }
                }
              }
            }

            // Finalize message
            set((state) => {
              const currentSession = state.sessions.get(session.id);
              if (currentSession) {
                const lastMessage = currentSession.messages[currentSession.messages.length - 1];
                if (lastMessage) {
                  lastMessage.isStreaming = false;
                  lastMessage.isThinking = false;
                }
                currentSession.updatedAt = Date.now();
              }
              state.isStreaming = false;
              state.isThinking = false;
              state.streamingContent = '';
            });
          } catch (error) {
            let errorMessage: string;

            if (error instanceof Error && error.name === 'AbortError') {
              errorMessage = 'Message annulé';
            } else if (error instanceof Error) {
              errorMessage = error.message;
            } else {
              errorMessage = 'Erreur lors de l\'envoi du message';
            }

            set((state) => {
              state.error = errorMessage;
              state.isStreaming = false;
              state.isThinking = false;
              state.streamingContent = '';

              // Update last message with error
              const currentSession = state.sessions.get(session.id);
              if (currentSession && currentSession.messages.length > 0) {
                const lastMessage = currentSession.messages[currentSession.messages.length - 1];
                if (lastMessage.role === 'assistant') {
                  lastMessage.content = `Erreur: ${errorMessage}`;
                  lastMessage.isStreaming = false;
                  lastMessage.isThinking = false;
                  lastMessage.metadata = { error: errorMessage };
                }
              }
            });
          } finally {
            abortController = null;
          }
        },

        addMessage: (sessionId: string, message: Omit<AIChatMessage, 'id' | 'timestamp'>) => {
          set((state) => {
            const session = state.sessions.get(sessionId);
            if (session) {
              const fullMessage: AIChatMessage = {
                ...message,
                id: message.id || uuidv4(),
                timestamp: message.timestamp || Date.now(),
              } as AIChatMessage;
              session.messages.push(fullMessage);
              session.updatedAt = Date.now();
            }
          });
        },

        updateMessage: (sessionId: string, messageId: string, updates: Partial<AIChatMessage>) => {
          set((state) => {
            const session = state.sessions.get(sessionId);
            if (session) {
              const messageIndex = session.messages.findIndex((m) => m.id === messageId);
              if (messageIndex !== -1) {
                session.messages[messageIndex] = {
                  ...session.messages[messageIndex],
                  ...updates,
                };
                session.updatedAt = Date.now();
              }
            }
          });
        },

        // ========================================
        // Execution Plans
        // ========================================

        createExecutionPlan: (plan: Omit<ExecutionPlan, 'id' | 'status'>) => {
          const executionPlan: ExecutionPlan = {
            ...plan,
            id: uuidv4(),
            status: plan.requiresConfirmation ? 'awaiting_confirmation' : 'approved',
          };

          set((state) => {
            state.pendingPlans.set(executionPlan.id, executionPlan);
            state.currentExecutionPlan = executionPlan;
          });

          return executionPlan;
        },

        approvePlan: async (planId: string) => {
          const plan = get().pendingPlans.get(planId);
          if (!plan) return;

          set((state) => {
            const currentPlan = state.pendingPlans.get(planId);
            if (currentPlan) {
              currentPlan.status = 'approved';
              currentPlan.status = 'executing';
            }
          });

          try {
            // Execute the plan via API
            const response = await fetch(`${API_URL}/api/chat/execute-plan`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${localStorage.getItem('token')}`,
              },
              body: JSON.stringify({ planId }),
            });

            if (!response.ok) {
              throw new Error('Failed to execute plan');
            }

            set((state) => {
              const currentPlan = state.pendingPlans.get(planId);
              if (currentPlan) {
                currentPlan.status = 'completed';
              }
            });
          } catch (error) {
            set((state) => {
              const currentPlan = state.pendingPlans.get(planId);
              if (currentPlan) {
                currentPlan.status = 'failed';
              }
              state.error = error instanceof Error ? error.message : 'Execution failed';
            });
          }
        },

        rejectPlan: (planId: string, reason?: string) => {
          set((state) => {
            const plan = state.pendingPlans.get(planId);
            if (plan) {
              plan.status = 'cancelled';
              if (reason && plan.metadata) {
                plan.metadata.warnings = [...(plan.metadata.warnings || []), reason];
              }
            }
            if (state.currentExecutionPlan?.id === planId) {
              state.currentExecutionPlan = null;
            }
          });
        },

        modifyPlan: (planId: string, modifications: Partial<ExecutionPlan>) => {
          set((state) => {
            const plan = state.pendingPlans.get(planId);
            if (plan) {
              Object.assign(plan, modifications);
            }
          });
        },

        updatePlanStep: (planId: string, stepId: string, updates: any) => {
          set((state) => {
            const plan = state.pendingPlans.get(planId);
            if (plan) {
              const step = plan.steps.find((s) => s.id === stepId);
              if (step) {
                Object.assign(step, updates);
              }
            }
          });
        },

        // ========================================
        // Streaming
        // ========================================

        handleStreamChunk: (chunk: StreamChunk) => {
          const session = get().getCurrentSession();
          if (!session) return;

          switch (chunk.type) {
            case 'thinking':
              set((state) => {
                state.isThinking = true;
              });
              break;

            case 'content':
              set((state) => {
                state.isThinking = false;
                state.streamingContent += chunk.content || '';

                // Update last message
                const currentSession = state.sessions.get(session.id);
                if (currentSession && currentSession.messages.length > 0) {
                  const lastMessage = currentSession.messages[currentSession.messages.length - 1];
                  if (lastMessage.role === 'assistant') {
                    lastMessage.content += chunk.content || '';
                  }
                }
              });
              break;

            case 'plan':
              if (chunk.data) {
                const plan = get().createExecutionPlan(chunk.data);
                set((state) => {
                  const currentSession = state.sessions.get(session.id);
                  if (currentSession && currentSession.messages.length > 0) {
                    const lastMessage = currentSession.messages[currentSession.messages.length - 1];
                    if (lastMessage.role === 'assistant') {
                      lastMessage.executionPlan = plan;
                    }
                  }
                });
              }
              break;

            case 'step_update':
              if (chunk.data && chunk.metadata?.planId && chunk.metadata?.stepId) {
                get().updatePlanStep(chunk.metadata.planId, chunk.metadata.stepId, chunk.data);
              }
              break;

            case 'file_change':
              // Handle file changes
              break;

            case 'error':
              set((state) => {
                state.error = chunk.content || 'Unknown error';
                state.isStreaming = false;
                state.isThinking = false;
              });
              break;

            case 'complete':
              set((state) => {
                state.isStreaming = false;
                state.isThinking = false;
                state.streamingContent = '';
              });
              break;
          }
        },

        startStreaming: () => {
          set((state) => {
            state.isStreaming = true;
            state.isThinking = true;
            state.streamingContent = '';
            state.error = null;
          });
        },

        stopStreaming: () => {
          set((state) => {
            state.isStreaming = false;
            state.isThinking = false;
            state.streamingContent = '';
          });
        },

        cancelExecution: () => {
          if (abortController) {
            abortController.abort();
            abortController = null;
          }

          set((state) => {
            state.isStreaming = false;
            state.isThinking = false;
            state.streamingContent = '';
            if (state.currentExecutionPlan) {
              state.currentExecutionPlan.status = 'cancelled';
            }
          });
        },

        // ========================================
        // Utility
        // ========================================

        clearError: () => {
          set({ error: null });
        },

        setSuggestions: (suggestions: SuggestedPrompt[]) => {
          set({ suggestions });
        },

        reset: () => {
          if (abortController) {
            abortController.abort();
            abortController = null;
          }
          set(initialState);
        },
      })),
      {
        name: 'ai-chat-storage',
        partialize: (state) => ({
          sessions: Array.from(state.sessions.entries()),
          currentSessionId: state.currentSessionId,
        }),
        onRehydrateStorage: () => (state) => {
          if (state && Array.isArray(state.sessions)) {
            state.sessions = new Map(state.sessions as any);
          }
        },
      }
    ),
    { name: 'AIEnhancedChatStore' }
  )
);

// ============================================
// Selectors
// ============================================

export const selectCurrentSession = (state: AIEnhancedChatState) => {
  if (!state.currentSessionId) return null;
  return state.sessions.get(state.currentSessionId) || null;
};

export const selectCurrentMessages = (state: AIEnhancedChatState) => {
  const session = selectCurrentSession(state);
  return session?.messages || [];
};

export const selectIsProcessing = (state: AIEnhancedChatState) => {
  return state.isStreaming || state.isThinking;
};

export const selectHasPendingPlan = (state: AIEnhancedChatState) => {
  return state.currentExecutionPlan?.status === 'awaiting_confirmation';
};
