/**
 * Chat Store - Zustand
 * Agent: Frontend State Management Specialist
 *
 * Gestion des conversations et de la generation de code
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import type {
  ChatMessage,
  GenerationProgress,
  GenerationResult,
  ProjectFile,
  ConversationMessage,
  MessageRole,
  GenerationMode,
  ProjectType,
} from '../types';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

// ============================================
// Types
// ============================================

interface GenerateOptions {
  prompt: string;
  projectId?: string;
  userId?: string;
  currentFiles?: ProjectFile[];
  conversationHistory?: ConversationMessage[];
  mode?: GenerationMode;
  projectType?: ProjectType;
  model?: string;
  apiKey?: string;
  onProgress?: (progress: GenerationProgress) => void;
  onStream?: (content: string) => void;
}

interface ChatState {
  // State
  messages: ChatMessage[];
  isGenerating: boolean;
  isThinking: boolean;
  progress: GenerationProgress;
  error: string | null;
  streamingContent: string;
  currentModel: string;
  generationMode: GenerationMode;

  // Actions
  addMessage: (message: Omit<ChatMessage, 'id' | 'timestamp'>) => void;
  updateLastMessage: (content: string) => void;
  appendToLastMessage: (content: string) => void;
  setThinking: (isThinking: boolean) => void;
  setProgress: (progress: Partial<GenerationProgress>) => void;
  setGenerating: (isGenerating: boolean) => void;
  setModel: (model: string) => void;
  setGenerationMode: (mode: GenerationMode) => void;
  clearMessages: () => void;
  removeMessage: (id: string) => void;

  // Generation Actions
  generate: (options: GenerateOptions) => Promise<GenerationResult>;
  generateWithStreaming: (options: GenerateOptions) => Promise<GenerationResult>;
  cancelGeneration: () => void;

  // Utility Actions
  reset: () => void;
  clearError: () => void;
}

// ============================================
// Initial State
// ============================================

const initialProgress: GenerationProgress = {
  step: '',
  progress: 0,
  message: '',
  isComplete: false,
};

const initialState = {
  messages: [] as ChatMessage[],
  isGenerating: false,
  isThinking: false,
  progress: initialProgress,
  error: null as string | null,
  streamingContent: '',
  currentModel: 'gpt-4',
  generationMode: 'agentic' as GenerationMode,
};

// ============================================
// Abort Controller for cancellation
// ============================================

let abortController: AbortController | null = null;

// ============================================
// Store
// ============================================

export const useChatStore = create<ChatState>()(
  devtools(
    immer((set, get) => ({
      ...initialState,

      // ========================================
      // Message Actions
      // ========================================

      addMessage: (message: Omit<ChatMessage, 'id' | 'timestamp'>) => {
        const newMessage: ChatMessage = {
          ...message,
          id: uuidv4(),
          timestamp: Date.now(),
        };

        set((state) => {
          state.messages.push(newMessage);
        });
      },

      updateLastMessage: (content: string) => {
        set((state) => {
          if (state.messages.length > 0) {
            const lastIndex = state.messages.length - 1;
            state.messages[lastIndex].content = content;
            state.messages[lastIndex].isStreaming = false;
            state.messages[lastIndex].isThinking = false;
          }
        });
      },

      appendToLastMessage: (content: string) => {
        set((state) => {
          if (state.messages.length > 0) {
            const lastIndex = state.messages.length - 1;
            state.messages[lastIndex].content += content;
          }
          state.streamingContent += content;
        });
      },

      setThinking: (isThinking: boolean) => {
        set((state) => {
          state.isThinking = isThinking;
          if (state.messages.length > 0) {
            const lastIndex = state.messages.length - 1;
            if (state.messages[lastIndex].role === 'assistant') {
              state.messages[lastIndex].isThinking = isThinking;
            }
          }
        });
      },

      setProgress: (progress: Partial<GenerationProgress>) => {
        set((state) => {
          state.progress = { ...state.progress, ...progress };
        });
      },

      setGenerating: (isGenerating: boolean) => {
        set((state) => {
          state.isGenerating = isGenerating;
          if (!isGenerating) {
            state.streamingContent = '';
          }
        });
      },

      setModel: (model: string) => {
        set((state) => {
          state.currentModel = model;
        });
      },

      setGenerationMode: (mode: GenerationMode) => {
        set((state) => {
          state.generationMode = mode;
        });
      },

      clearMessages: () => {
        set((state) => {
          state.messages = [];
          state.streamingContent = '';
        });
      },

      removeMessage: (id: string) => {
        set((state) => {
          state.messages = state.messages.filter((m) => m.id !== id);
        });
      },

      // ========================================
      // Generation Actions
      // ========================================

      generate: async (options: GenerateOptions): Promise<GenerationResult> => {
        const {
          prompt,
          projectId,
          userId,
          currentFiles,
          conversationHistory,
          mode = get().generationMode,
          projectType,
          model = get().currentModel,
          apiKey,
          onProgress,
        } = options;

        // Reset state
        set((state) => {
          state.isGenerating = true;
          state.isThinking = true;
          state.error = null;
          state.progress = {
            step: 'initializing',
            progress: 0,
            message: 'Initialisation...',
            isComplete: false,
          };
        });

        // Add user message
        get().addMessage({ role: 'user', content: prompt });

        // Add thinking assistant message
        get().addMessage({
          role: 'assistant',
          content: '',
          isThinking: true,
        });

        try {
          // Create abort controller
          abortController = new AbortController();

          // Determine endpoint based on mode
          let endpoint: string;
          let requestBody: Record<string, unknown>;

          switch (mode) {
            case 'fullstack':
              endpoint = `${API_URL}/api/fullstack/generate`;
              requestBody = {
                message: prompt,
                model,
                api_key: apiKey || process.env.REACT_APP_OPENAI_API_KEY,
                current_files: currentFiles,
                conversation_history: conversationHistory,
                project_type: projectType,
                project_id: projectId,
                user_id: userId,
              };
              break;
            case 'agentic':
              endpoint = `${API_URL}/api/agentic/generate`;
              requestBody = {
                message: prompt,
                model,
                api_key: apiKey || process.env.REACT_APP_OPENAI_API_KEY,
                current_files: currentFiles,
                conversation_history: conversationHistory,
                project_id: projectId,
                user_id: userId,
              };
              break;
            default:
              endpoint = `${API_URL}/api/generate`;
              requestBody = {
                message: prompt,
                model,
                api_key: apiKey || process.env.REACT_APP_OPENAI_API_KEY,
                conversation_history: conversationHistory,
              };
          }

          // Update progress
          set((state) => {
            state.progress = {
              step: 'generating',
              progress: 25,
              message: 'Generation en cours...',
              isComplete: false,
            };
          });
          onProgress?.(get().progress);

          const response = await axios.post<GenerationResult>(endpoint, requestBody, {
            signal: abortController.signal,
            timeout: 300000, // 5 minutes timeout
          });

          const result = response.data;

          // Update progress
          set((state) => {
            state.progress = {
              step: 'complete',
              progress: 100,
              message: 'Generation terminee!',
              isComplete: true,
            };
            state.isThinking = false;
          });
          onProgress?.(get().progress);

          // Update assistant message
          get().updateLastMessage(result.message);

          set((state) => {
            state.isGenerating = false;
          });

          return result;
        } catch (error) {
          let errorMessage: string;

          if (axios.isCancel(error)) {
            errorMessage = 'Generation annulee';
          } else if (axios.isAxiosError(error)) {
            errorMessage = error.response?.data?.detail || error.message;
          } else {
            errorMessage = 'Erreur lors de la generation';
          }

          set((state) => {
            state.error = errorMessage;
            state.isGenerating = false;
            state.isThinking = false;
            state.progress = {
              step: 'error',
              progress: 0,
              message: errorMessage,
              isComplete: false,
            };
          });

          // Update last message with error
          get().updateLastMessage(`Erreur: ${errorMessage}`);

          throw new Error(errorMessage);
        } finally {
          abortController = null;
        }
      },

      generateWithStreaming: async (options: GenerateOptions): Promise<GenerationResult> => {
        const {
          prompt,
          projectId,
          userId,
          currentFiles,
          conversationHistory,
          mode = get().generationMode,
          projectType,
          model = get().currentModel,
          apiKey,
          onProgress,
          onStream,
        } = options;

        // Reset state
        set((state) => {
          state.isGenerating = true;
          state.isThinking = true;
          state.error = null;
          state.streamingContent = '';
          state.progress = {
            step: 'initializing',
            progress: 0,
            message: 'Initialisation...',
            isComplete: false,
          };
        });

        // Add user message
        get().addMessage({ role: 'user', content: prompt });

        // Add streaming assistant message
        get().addMessage({
          role: 'assistant',
          content: '',
          isStreaming: true,
        });

        try {
          abortController = new AbortController();

          const endpoint = `${API_URL}/api/generate/stream`;
          const requestBody = {
            message: prompt,
            model,
            api_key: apiKey || process.env.REACT_APP_OPENAI_API_KEY,
            current_files: currentFiles,
            conversation_history: conversationHistory,
            project_type: projectType,
            project_id: projectId,
            user_id: userId,
            mode,
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
          let fullContent = '';
          let result: GenerationResult | null = null;

          set((state) => {
            state.isThinking = false;
          });

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
                  const parsed = JSON.parse(data);

                  if (parsed.type === 'content') {
                    fullContent += parsed.content;
                    get().appendToLastMessage(parsed.content);
                    onStream?.(parsed.content);
                  } else if (parsed.type === 'progress') {
                    set((state) => {
                      state.progress = {
                        step: parsed.step,
                        progress: parsed.progress,
                        message: parsed.message,
                        currentFile: parsed.currentFile,
                        isComplete: false,
                      };
                    });
                    onProgress?.(get().progress);
                  } else if (parsed.type === 'result') {
                    result = parsed.data;
                  } else if (parsed.type === 'error') {
                    throw new Error(parsed.message);
                  }
                } catch (e) {
                  // Ignore parse errors for incomplete chunks
                }
              }
            }
          }

          // Finalize
          set((state) => {
            state.progress = {
              step: 'complete',
              progress: 100,
              message: 'Generation terminee!',
              isComplete: true,
            };
            state.isGenerating = false;
            state.streamingContent = '';
          });

          // Update message to remove streaming flag
          set((state) => {
            if (state.messages.length > 0) {
              const lastIndex = state.messages.length - 1;
              state.messages[lastIndex].isStreaming = false;
              if (result?.message) {
                state.messages[lastIndex].content = result.message;
              }
            }
          });

          return result || {
            success: true,
            files: [],
            message: fullContent,
          };
        } catch (error) {
          let errorMessage: string;

          if (error instanceof Error && error.name === 'AbortError') {
            errorMessage = 'Generation annulee';
          } else if (error instanceof Error) {
            errorMessage = error.message;
          } else {
            errorMessage = 'Erreur lors de la generation';
          }

          set((state) => {
            state.error = errorMessage;
            state.isGenerating = false;
            state.isThinking = false;
            state.streamingContent = '';
            state.progress = {
              step: 'error',
              progress: 0,
              message: errorMessage,
              isComplete: false,
            };
          });

          get().updateLastMessage(`Erreur: ${errorMessage}`);

          throw new Error(errorMessage);
        } finally {
          abortController = null;
        }
      },

      cancelGeneration: () => {
        if (abortController) {
          abortController.abort();
          abortController = null;
        }

        set((state) => {
          state.isGenerating = false;
          state.isThinking = false;
          state.streamingContent = '';
          state.progress = {
            step: 'cancelled',
            progress: 0,
            message: 'Generation annulee',
            isComplete: false,
          };
        });
      },

      // ========================================
      // Utility Actions
      // ========================================

      reset: () => {
        if (abortController) {
          abortController.abort();
          abortController = null;
        }

        set((state) => {
          Object.assign(state, initialState);
        });
      },

      clearError: () => {
        set((state) => {
          state.error = null;
        });
      },
    })),
    { name: 'ChatStore' }
  )
);

// ============================================
// Selectors
// ============================================

export const selectLastUserMessage = (state: ChatState): ChatMessage | undefined => {
  return [...state.messages].reverse().find((m) => m.role === 'user');
};

export const selectLastAssistantMessage = (state: ChatState): ChatMessage | undefined => {
  return [...state.messages].reverse().find((m) => m.role === 'assistant');
};

export const selectConversationHistory = (state: ChatState): ConversationMessage[] => {
  return state.messages
    .filter((m) => !m.isThinking)
    .map((m) => ({
      role: m.role,
      content: m.content,
    }));
};

export const selectIsGenerating = (state: ChatState): boolean => {
  return state.isGenerating || state.isThinking;
};
