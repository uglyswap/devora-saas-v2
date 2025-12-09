/**
 * DEVORA WEBSOCKET COLLABORATION HOOK
 *
 * Hook React pour la collaboration en temps reel via WebSocket
 * Gere la connexion, la reconnexion automatique, et les evenements collaboratifs
 *
 * @author Frontend Squad - Hooks Specialist
 * @version 1.0.0
 */

import { useEffect, useRef, useState, useCallback } from 'react';

// Types
interface ConnectedUser {
  user_id: string;
  email: string;
  display_name?: string;
  avatar_url?: string;
  cursor_position?: CursorPosition;
  current_file?: string;
  color?: string;
}

interface CursorPosition {
  line: number;
  column: number;
}

interface FileChange {
  type: 'insert' | 'delete' | 'replace';
  position: { start: number; end?: number };
  text?: string;
}

interface WebSocketMessage {
  type: string;
  [key: string]: any;
}

interface UseWebSocketOptions {
  projectId: string;
  token: string;
  onMessage?: (data: WebSocketMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
  autoReconnect?: boolean;
  reconnectDelay?: number;
  maxReconnectAttempts?: number;
}

interface UseWebSocketReturn {
  isConnected: boolean;
  connectedUsers: ConnectedUser[];
  send: (data: WebSocketMessage) => void;
  sendCursorMove: (fileName: string, position: CursorPosition) => void;
  sendFileChange: (fileName: string, changes: FileChange[]) => void;
  sendFileSelect: (fileName: string) => void;
  sendChatMessage: (message: string) => void;
  disconnect: () => void;
  reconnect: () => void;
  connectionState: 'connecting' | 'connected' | 'disconnected' | 'reconnecting';
}

// Configuration
const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:4521';
const DEFAULT_RECONNECT_DELAY = 3000;
const DEFAULT_MAX_RECONNECT_ATTEMPTS = 5;

/**
 * Hook pour la collaboration en temps reel via WebSocket
 *
 * @example
 * ```tsx
 * const {
 *   isConnected,
 *   connectedUsers,
 *   sendCursorMove,
 *   sendFileChange,
 * } = useWebSocket({
 *   projectId: 'project-123',
 *   token: 'auth-token',
 *   onMessage: (data) => console.log('Received:', data),
 * });
 *
 * // Envoyer une position de curseur
 * sendCursorMove('App.tsx', { line: 10, column: 5 });
 *
 * // Envoyer un changement de fichier
 * sendFileChange('App.tsx', [{ type: 'insert', position: { start: 100 }, text: 'new code' }]);
 * ```
 */
export function useWebSocket(options: UseWebSocketOptions): UseWebSocketReturn {
  const {
    projectId,
    token,
    onMessage,
    onConnect,
    onDisconnect,
    onError,
    autoReconnect = true,
    reconnectDelay = DEFAULT_RECONNECT_DELAY,
    maxReconnectAttempts = DEFAULT_MAX_RECONNECT_ATTEMPTS,
  } = options;

  // State
  const [isConnected, setIsConnected] = useState(false);
  const [connectedUsers, setConnectedUsers] = useState<ConnectedUser[]>([]);
  const [connectionState, setConnectionState] = useState<'connecting' | 'connected' | 'disconnected' | 'reconnecting'>('disconnected');

  // Refs
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const isManualDisconnectRef = useRef(false);

  /**
   * Nettoie le timeout de reconnexion
   */
  const clearReconnectTimeout = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
  }, []);

  /**
   * Traite les messages WebSocket entrants
   */
  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const data: WebSocketMessage = JSON.parse(event.data);

      // Gestion des evenements de presence
      switch (data.type) {
        case 'connected_users':
          setConnectedUsers(data.users || []);
          break;

        case 'user_joined':
          setConnectedUsers(prev => {
            // Evite les doublons
            if (prev.some(u => u.user_id === data.user?.user_id)) {
              return prev;
            }
            return [...prev, data.user];
          });
          break;

        case 'user_left':
          setConnectedUsers(prev =>
            prev.filter(u => u.user_id !== data.user_id)
          );
          break;

        case 'cursor_update':
          setConnectedUsers(prev =>
            prev.map(u =>
              u.user_id === data.user_id
                ? { ...u, cursor_position: data.position, current_file: data.file_name }
                : u
            )
          );
          break;

        case 'file_change':
          // Delegate to external handler
          break;

        case 'ping':
          // Respond to keep-alive
          wsRef.current?.send(JSON.stringify({ type: 'pong' }));
          break;
      }

      // Appelle le callback externe
      onMessage?.(data);
    } catch (e) {
      console.error('Error parsing WebSocket message:', e);
    }
  }, [onMessage]);

  /**
   * Etablit la connexion WebSocket
   */
  const connect = useCallback(() => {
    // Don't reconnect if manually disconnected
    if (isManualDisconnectRef.current) {
      return;
    }

    // Close existing connection
    if (wsRef.current) {
      wsRef.current.close();
    }

    setConnectionState('connecting');

    const wsUrl = `${WS_URL}/ws/project/${projectId}?token=${token}`;

    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        setConnectionState('connected');
        reconnectAttemptsRef.current = 0;
        onConnect?.();
      };

      ws.onclose = (event) => {
        setIsConnected(false);
        wsRef.current = null;

        // Only auto-reconnect if not manually disconnected
        if (!isManualDisconnectRef.current && autoReconnect) {
          if (reconnectAttemptsRef.current < maxReconnectAttempts) {
            setConnectionState('reconnecting');
            reconnectAttemptsRef.current += 1;

            const delay = reconnectDelay * Math.pow(1.5, reconnectAttemptsRef.current - 1);
            reconnectTimeoutRef.current = setTimeout(connect, Math.min(delay, 30000));
          } else {
            setConnectionState('disconnected');
            console.warn('Max reconnection attempts reached');
          }
        } else {
          setConnectionState('disconnected');
        }

        onDisconnect?.();
      };

      ws.onmessage = handleMessage;

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        onError?.(error);
      };
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      setConnectionState('disconnected');
    }
  }, [projectId, token, onConnect, onDisconnect, onError, handleMessage, autoReconnect, reconnectDelay, maxReconnectAttempts]);

  /**
   * Deconnecte le WebSocket
   */
  const disconnect = useCallback(() => {
    isManualDisconnectRef.current = true;
    clearReconnectTimeout();

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setIsConnected(false);
    setConnectionState('disconnected');
    setConnectedUsers([]);
  }, [clearReconnectTimeout]);

  /**
   * Reconnecte manuellement le WebSocket
   */
  const reconnect = useCallback(() => {
    isManualDisconnectRef.current = false;
    reconnectAttemptsRef.current = 0;
    connect();
  }, [connect]);

  /**
   * Envoie un message via WebSocket
   */
  const send = useCallback((data: WebSocketMessage) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    } else {
      console.warn('WebSocket is not connected. Message not sent:', data);
    }
  }, []);

  /**
   * Envoie une mise a jour de position de curseur
   */
  const sendCursorMove = useCallback((fileName: string, position: CursorPosition) => {
    send({
      type: 'cursor_move',
      file_name: fileName,
      position,
    });
  }, [send]);

  /**
   * Envoie des changements de fichier
   */
  const sendFileChange = useCallback((fileName: string, changes: FileChange[]) => {
    send({
      type: 'file_change',
      file_name: fileName,
      changes,
    });
  }, [send]);

  /**
   * Envoie une selection de fichier
   */
  const sendFileSelect = useCallback((fileName: string) => {
    send({
      type: 'file_select',
      file_name: fileName,
    });
  }, [send]);

  /**
   * Envoie un message de chat
   */
  const sendChatMessage = useCallback((message: string) => {
    send({
      type: 'chat_message',
      message,
      timestamp: new Date().toISOString(),
    });
  }, [send]);

  // Effect: Connect on mount, disconnect on unmount
  useEffect(() => {
    isManualDisconnectRef.current = false;
    connect();

    return () => {
      isManualDisconnectRef.current = true;
      clearReconnectTimeout();
      wsRef.current?.close();
    };
  }, [connect, clearReconnectTimeout]);

  // Effect: Handle visibility change (reconnect when tab becomes visible)
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible' && !isConnected && !isManualDisconnectRef.current) {
        reconnect();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, [isConnected, reconnect]);

  return {
    isConnected,
    connectedUsers,
    send,
    sendCursorMove,
    sendFileChange,
    sendFileSelect,
    sendChatMessage,
    disconnect,
    reconnect,
    connectionState,
  };
}

export default useWebSocket;
