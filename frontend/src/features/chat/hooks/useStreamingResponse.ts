/**
 * useStreamingResponse Hook
 * Agent: AI Chat Engineer
 *
 * Hook pour gérer le streaming des réponses AI avec Server-Sent Events
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import type { StreamChunk } from '../types/chat.types';

export interface UseStreamingResponseOptions {
  onChunk?: (chunk: StreamChunk) => void;
  onComplete?: () => void;
  onError?: (error: Error) => void;
  autoConnect?: boolean;
}

export interface UseStreamingResponseReturn {
  isConnected: boolean;
  isStreaming: boolean;
  content: string;
  error: Error | null;
  connect: (url: string, requestBody: any) => Promise<void>;
  disconnect: () => void;
  reset: () => void;
}

export const useStreamingResponse = (
  options: UseStreamingResponseOptions = {}
): UseStreamingResponseReturn => {
  const { onChunk, onComplete, onError, autoConnect = false } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [content, setContent] = useState('');
  const [error, setError] = useState<Error | null>(null);

  const abortControllerRef = useRef<AbortController | null>(null);
  const readerRef = useRef<ReadableStreamDefaultReader<Uint8Array> | null>(null);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, []);

  const disconnect = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }

    if (readerRef.current) {
      readerRef.current.cancel();
      readerRef.current = null;
    }

    setIsConnected(false);
    setIsStreaming(false);
  }, []);

  const reset = useCallback(() => {
    disconnect();
    setContent('');
    setError(null);
  }, [disconnect]);

  const connect = useCallback(
    async (url: string, requestBody: any) => {
      try {
        // Cleanup previous connection
        disconnect();

        // Reset state
        setContent('');
        setError(null);
        setIsStreaming(true);

        // Create new abort controller
        abortControllerRef.current = new AbortController();

        // Make fetch request
        const response = await fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
          body: JSON.stringify(requestBody),
          signal: abortControllerRef.current.signal,
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        setIsConnected(true);

        // Get reader
        const reader = response.body?.getReader();
        if (!reader) {
          throw new Error('No reader available');
        }

        readerRef.current = reader;

        // Create decoder
        const decoder = new TextDecoder();
        let buffer = '';

        // Read stream
        while (true) {
          const { done, value } = await reader.read();

          if (done) {
            setIsStreaming(false);
            onComplete?.();
            break;
          }

          // Decode chunk
          const chunk = decoder.decode(value, { stream: true });
          buffer += chunk;

          // Process complete lines
          const lines = buffer.split('\n');
          buffer = lines.pop() || ''; // Keep incomplete line in buffer

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6).trim();

              if (data === '[DONE]') {
                setIsStreaming(false);
                onComplete?.();
                continue;
              }

              try {
                const parsed: StreamChunk = JSON.parse(data);

                // Update content if it's a content chunk
                if (parsed.type === 'content' && parsed.content) {
                  setContent((prev) => prev + parsed.content);
                }

                // Call onChunk callback
                onChunk?.(parsed);

                // Handle error chunks
                if (parsed.type === 'error') {
                  const errorObj = new Error(parsed.content || 'Stream error');
                  setError(errorObj);
                  onError?.(errorObj);
                }

                // Handle complete chunks
                if (parsed.type === 'complete') {
                  setIsStreaming(false);
                  onComplete?.();
                }
              } catch (parseError) {
                console.warn('Failed to parse SSE data:', data, parseError);
                // Continue processing other chunks
              }
            }
          }
        }
      } catch (err) {
        const errorObj = err instanceof Error ? err : new Error('Unknown streaming error');

        // Don't set error for abort errors
        if (errorObj.name !== 'AbortError') {
          setError(errorObj);
          onError?.(errorObj);
        }

        setIsStreaming(false);
        setIsConnected(false);
      } finally {
        readerRef.current = null;
        abortControllerRef.current = null;
      }
    },
    [onChunk, onComplete, onError, disconnect]
  );

  return {
    isConnected,
    isStreaming,
    content,
    error,
    connect,
    disconnect,
    reset,
  };
};

export default useStreamingResponse;
