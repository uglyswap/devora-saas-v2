/**
 * useDeployment Hook
 * Handle deployment operations with SSE streaming
 * @version 1.0.0
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import axios from 'axios';
import {
  DeployProvider,
  DeploymentRequest,
  DeploymentResponse,
  DeploymentHistoryItem,
  ProviderInfo,
  DeployProgressEvent,
  DeploymentStatus
} from '../types/deployment.types';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

interface UseDeploymentOptions {
  onProgress?: (event: DeployProgressEvent) => void;
  onComplete?: (result: DeploymentResponse) => void;
  onError?: (error: string) => void;
}

interface UseDeploymentReturn {
  // State
  isDeploying: boolean;
  progress: number;
  status: DeploymentStatus | null;
  currentDeployment: DeploymentResponse | null;
  logs: string[];
  error: string | null;

  // Actions
  deploy: (request: DeploymentRequest) => Promise<DeploymentResponse>;
  deployWithStream: (request: DeploymentRequest) => void;
  cancelDeployment: (deploymentId: string) => Promise<void>;
  getStatus: (deploymentId: string) => Promise<DeploymentResponse>;
  getHistory: (limit?: number) => Promise<DeploymentHistoryItem[]>;
  getProviders: () => Promise<ProviderInfo[]>;
  saveProviderToken: (provider: DeployProvider, token: string) => Promise<void>;

  // Utilities
  reset: () => void;
}

export function useDeployment(options: UseDeploymentOptions = {}): UseDeploymentReturn {
  const { onProgress, onComplete, onError } = options;

  const [isDeploying, setIsDeploying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState<DeploymentStatus | null>(null);
  const [currentDeployment, setCurrentDeployment] = useState<DeploymentResponse | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  const eventSourceRef = useRef<EventSource | null>(null);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  const reset = useCallback(() => {
    setIsDeploying(false);
    setProgress(0);
    setStatus(null);
    setCurrentDeployment(null);
    setLogs([]);
    setError(null);

    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
  }, []);

  /**
   * Deploy without streaming (simple POST request)
   */
  const deploy = useCallback(async (request: DeploymentRequest): Promise<DeploymentResponse> => {
    reset();
    setIsDeploying(true);
    setStatus('pending');

    try {
      const response = await axios.post<DeploymentResponse>(
        `${API_URL}/api/deploy/quick`,
        {
          project_id: request.projectId,
          project_name: request.projectName,
          files: request.files.map(f => ({
            name: f.name,
            content: f.content,
            language: f.language
          })),
          provider: request.provider,
          env_vars: request.envVars,
          framework: request.framework
        }
      );

      const result = response.data;
      setCurrentDeployment(result);
      setStatus(result.status);
      setProgress(result.progress);

      if (result.success) {
        onComplete?.(result);
      } else {
        setError(result.error || 'Deployment failed');
        onError?.(result.error || 'Deployment failed');
      }

      return result;
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || 'Deployment failed';
      setError(errorMsg);
      setStatus('error');
      onError?.(errorMsg);
      throw err;
    } finally {
      setIsDeploying(false);
    }
  }, [reset, onComplete, onError]);

  /**
   * Deploy with SSE streaming for real-time progress
   */
  const deployWithStream = useCallback((request: DeploymentRequest) => {
    reset();
    setIsDeploying(true);
    setStatus('pending');

    // Use fetch with POST for SSE (EventSource only supports GET)
    const controller = new AbortController();

    fetch(`${API_URL}/api/deploy/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream'
      },
      body: JSON.stringify({
        project_id: request.projectId,
        project_name: request.projectName,
        files: request.files.map(f => ({
          name: f.name,
          content: f.content,
          language: f.language
        })),
        provider: request.provider,
        env_vars: request.envVars,
        framework: request.framework
      }),
      signal: controller.signal
    })
      .then(async (response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();

        if (!reader) {
          throw new Error('No response body');
        }

        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();

          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (!line.trim()) continue;

            const eventMatch = line.match(/event: (\w+)/);
            const dataMatch = line.match(/data: (.+)/);

            if (eventMatch && dataMatch) {
              const event: DeployProgressEvent = {
                event: eventMatch[1] as DeployProgressEvent['event'],
                data: JSON.parse(dataMatch[1])
              };

              // Update state based on event
              switch (event.event) {
                case 'start':
                case 'progress':
                  setProgress(event.data.progress || 0);
                  setStatus((event.data.status as DeploymentStatus) || 'building');
                  if (event.data.message) {
                    setLogs(prev => [...prev, event.data.message!]);
                  }
                  break;

                case 'log':
                  if (event.data.message) {
                    setLogs(prev => [...prev, event.data.message!]);
                  }
                  break;

                case 'complete':
                  setProgress(100);
                  setStatus('ready');
                  const result: DeploymentResponse = {
                    id: event.data.id,
                    success: true,
                    status: 'ready',
                    url: event.data.url,
                    progress: 100,
                    provider: request.provider,
                    deploymentId: event.data.id
                  };
                  setCurrentDeployment(result);
                  setIsDeploying(false);
                  onComplete?.(result);
                  break;

                case 'error':
                  setStatus('error');
                  setError(event.data.error || 'Deployment failed');
                  setIsDeploying(false);
                  onError?.(event.data.error || 'Deployment failed');
                  break;
              }

              onProgress?.(event);
            }
          }
        }
      })
      .catch((err) => {
        if (err.name === 'AbortError') return;

        const errorMsg = err.message || 'Deployment failed';
        setError(errorMsg);
        setStatus('error');
        setIsDeploying(false);
        onError?.(errorMsg);
      });

    // Store abort function for cleanup
    eventSourceRef.current = { close: () => controller.abort() } as any;
  }, [reset, onProgress, onComplete, onError]);

  /**
   * Cancel a running deployment
   */
  const cancelDeployment = useCallback(async (deploymentId: string): Promise<void> => {
    try {
      await axios.delete(`${API_URL}/api/deploy/${deploymentId}`);
      setStatus('canceled');
      setIsDeploying(false);

      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
    } catch (err: any) {
      throw err;
    }
  }, []);

  /**
   * Get deployment status
   */
  const getStatus = useCallback(async (deploymentId: string): Promise<DeploymentResponse> => {
    const response = await axios.get<DeploymentResponse>(
      `${API_URL}/api/deploy/status/${deploymentId}`
    );
    return response.data;
  }, []);

  /**
   * Get deployment history
   */
  const getHistory = useCallback(async (limit = 50): Promise<DeploymentHistoryItem[]> => {
    const response = await axios.get<DeploymentHistoryItem[]>(
      `${API_URL}/api/deploy/history`,
      { params: { limit } }
    );
    return response.data;
  }, []);

  /**
   * Get available providers
   */
  const getProviders = useCallback(async (): Promise<ProviderInfo[]> => {
    const response = await axios.get<ProviderInfo[]>(
      `${API_URL}/api/deploy/providers`
    );
    return response.data;
  }, []);

  /**
   * Save provider API token
   */
  const saveProviderToken = useCallback(async (
    provider: DeployProvider,
    token: string
  ): Promise<void> => {
    await axios.post(`${API_URL}/api/deploy/config/token`, {
      provider,
      token
    });
  }, []);

  return {
    // State
    isDeploying,
    progress,
    status,
    currentDeployment,
    logs,
    error,

    // Actions
    deploy,
    deployWithStream,
    cancelDeployment,
    getStatus,
    getHistory,
    getProviders,
    saveProviderToken,

    // Utilities
    reset
  };
}

export default useDeployment;
