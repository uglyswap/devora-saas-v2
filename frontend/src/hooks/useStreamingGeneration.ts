/**
 * DEVORA STREAMING GENERATION HOOK
 *
 * Hook React pour la generation de code en streaming via SSE (Server-Sent Events)
 * Gere la connexion, le parsing des evenements, et l'etat de generation
 *
 * @author Frontend Squad - Hooks Specialist
 * @version 1.0.0
 */

import { useState, useCallback, useRef } from 'react';

// Types
interface ProjectFile {
  name: string;
  content: string;
  language: string;
}

interface StreamingState {
  isStreaming: boolean;
  content: string;
  files: ProjectFile[];
  progress: number;
  currentStep: string;
  error: string | null;
}

interface UseStreamingGenerationReturn extends StreamingState {
  generate: (prompt: string, projectId: string, apiKey: string, model?: string) => Promise<void>;
  abort: () => void;
  reset: () => void;
}

interface SSEEventData {
  type: 'progress' | 'content' | 'file' | 'done' | 'error';
  progress?: number;
  step?: string;
  content?: string;
  file?: ProjectFile;
  message?: string;
}

// Configuration
const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:4521';

// Initial state
const initialState: StreamingState = {
  isStreaming: false,
  content: '',
  files: [],
  progress: 0,
  currentStep: '',
  error: null,
};

/**
 * Hook pour la generation de code en streaming
 *
 * @example
 * ```tsx
 * const { generate, abort, reset, isStreaming, content, files, progress, currentStep, error } = useStreamingGeneration();
 *
 * // Lancer une generation
 * await generate('Create a React component', 'project-123', 'api-key');
 *
 * // Annuler en cours
 * abort();
 *
 * // Reinitialiser
 * reset();
 * ```
 */
export function useStreamingGeneration(): UseStreamingGenerationReturn {
  const [state, setState] = useState<StreamingState>(initialState);
  const abortControllerRef = useRef<AbortController | null>(null);

  /**
   * Reinitialise l'etat du hook
   */
  const reset = useCallback(() => {
    setState(initialState);
  }, []);

  /**
   * Annule la generation en cours
   */
  const abort = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
      setState(s => ({
        ...s,
        isStreaming: false,
        currentStep: 'Annule'
      }));
    }
  }, []);

  /**
   * Parse une ligne SSE et extrait les donnees
   */
  const parseSSELine = (line: string): SSEEventData | null => {
    if (!line.startsWith('data: ')) {
      return null;
    }

    try {
      return JSON.parse(line.slice(6));
    } catch (e) {
      console.error('Error parsing SSE data:', e);
      return null;
    }
  };

  /**
   * Traite un evenement SSE et met a jour l'etat
   */
  const handleSSEEvent = useCallback((data: SSEEventData) => {
    switch (data.type) {
      case 'progress':
        setState(s => ({
          ...s,
          progress: data.progress ?? s.progress,
          currentStep: data.step ?? s.currentStep,
        }));
        break;

      case 'content':
        setState(s => ({
          ...s,
          content: s.content + (data.content ?? ''),
        }));
        break;

      case 'file':
        if (data.file) {
          setState(s => ({
            ...s,
            files: [...s.files, data.file!],
            progress: data.progress ?? s.progress,
          }));
        }
        break;

      case 'done':
        setState(s => ({
          ...s,
          isStreaming: false,
          progress: 100,
          currentStep: 'Termine!',
        }));
        break;

      case 'error':
        setState(s => ({
          ...s,
          isStreaming: false,
          error: data.message ?? 'Erreur inconnue',
          currentStep: 'Erreur',
        }));
        break;
    }
  }, []);

  /**
   * Lance la generation de code en streaming
   *
   * @param prompt - Le prompt de generation
   * @param projectId - L'ID du projet
   * @param apiKey - La cle API pour l'IA
   * @param model - Le modele a utiliser (optionnel)
   */
  const generate = useCallback(async (
    prompt: string,
    projectId: string,
    apiKey: string,
    model: string = 'openai/gpt-4o'
  ) => {
    // Reset state and prepare for streaming
    setState({
      isStreaming: true,
      content: '',
      files: [],
      progress: 0,
      currentStep: 'Connexion...',
      error: null,
    });

    // Create abort controller for cancellation
    abortControllerRef.current = new AbortController();

    try {
      // Make the streaming request
      const response = await fetch(`${API_URL}/api/stream/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          message: prompt,
          project_id: projectId,
          api_key: apiKey,
          model,
          current_files: [],
        }),
        signal: abortControllerRef.current.signal,
      });

      // Check for HTTP errors
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
      }

      // Check for response body
      if (!response.body) {
        throw new Error('No response body received');
      }

      // Setup stream reading
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      // Read the stream
      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          // Process any remaining buffer
          if (buffer.trim()) {
            const lines = buffer.split('\n').filter(line => line.startsWith('data: '));
            for (const line of lines) {
              const data = parseSSELine(line);
              if (data) {
                handleSSEEvent(data);
              }
            }
          }
          break;
        }

        // Decode the chunk and add to buffer
        buffer += decoder.decode(value, { stream: true });

        // Process complete lines
        const lines = buffer.split('\n');

        // Keep the last potentially incomplete line in the buffer
        buffer = lines.pop() || '';

        // Process complete lines
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = parseSSELine(line);
            if (data) {
              handleSSEEvent(data);
            }
          }
        }
      }

      // Ensure we mark as complete if not already done
      setState(s => {
        if (s.isStreaming) {
          return {
            ...s,
            isStreaming: false,
            progress: 100,
            currentStep: 'Termine!',
          };
        }
        return s;
      });

    } catch (error) {
      // Handle abort (user cancelled)
      if (error instanceof Error && error.name === 'AbortError') {
        // Already handled in abort function
        return;
      }

      // Handle other errors
      const errorMessage = error instanceof Error ? error.message : 'Erreur inconnue';
      console.error('Streaming generation error:', error);

      setState(s => ({
        ...s,
        isStreaming: false,
        error: errorMessage,
        currentStep: 'Erreur',
      }));
    } finally {
      abortControllerRef.current = null;
    }
  }, [handleSSEEvent]);

  return {
    ...state,
    generate,
    abort,
    reset,
  };
}

export default useStreamingGeneration;
