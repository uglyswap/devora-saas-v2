/**
 * Hook principal pour la collaboration temps réel
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import * as Y from 'yjs';
import { WebsocketProvider } from 'y-websocket';
import type {
  CollaborationConfig,
  CollaborationHookState as CollaborationState,
  CollaborationHookReturn,
  User,
  CursorPosition,
  Selection,
  AwarenessState,
} from '../types';

const COLORS = [
  '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
  '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B739', '#52B788',
];

function getRandomColor(): string {
  return COLORS[Math.floor(Math.random() * COLORS.length)];
}

export function useCollaboration(config: CollaborationConfig): CollaborationHookReturn {
  const [state, setState] = useState<CollaborationState>({
    status: 'disconnected',
    users: new Map(),
    currentUser: config.user,
    latency: 0,
  });

  const ydocRef = useRef<Y.Doc | null>(null);
  const providerRef = useRef<WebsocketProvider | null>(null);
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  /**
   * Mesure la latence
   */
  const measureLatency = useCallback(() => {
    const start = Date.now();
    const provider = providerRef.current;

    if (provider && provider.ws && provider.ws.readyState === WebSocket.OPEN) {
      provider.ws.send(JSON.stringify({ type: 'ping' }));

      const handlePong = () => {
        const latency = Date.now() - start;
        setState((prev) => ({ ...prev, latency }));
      };

      provider.ws.addEventListener('message', handlePong, { once: true });
    }
  }, []);

  /**
   * Met à jour les utilisateurs depuis l'awareness
   */
  const updateUsers = useCallback(() => {
    const provider = providerRef.current;
    if (!provider || !provider.awareness) return;

    const users = new Map<number, User>();
    const states = provider.awareness.getStates();

    states.forEach((state: unknown, clientId: number) => {
      const awarenessState = state as AwarenessState;
      if (awarenessState.user) {
        users.set(clientId, awarenessState.user);
      }
    });

    setState((prev) => ({ ...prev, users }));
  }, []);

  /**
   * Connexion au serveur
   */
  const connect = useCallback(async () => {
    if (providerRef.current) {
      console.warn('Already connected');
      return;
    }

    setState((prev) => ({ ...prev, status: 'connecting' }));

    try {
      // Crée le document Yjs
      const ydoc = new Y.Doc();
      ydocRef.current = ydoc;

      // Crée le provider WebSocket
      const provider = new WebsocketProvider(
        config.wsUrl,
        config.documentId,
        ydoc,
        {
          connect: config.autoConnect !== false,
          WebSocketPolyfill: WebSocket,
        }
      );

      providerRef.current = provider;

      // Assure que la couleur de l'utilisateur est définie
      if (!config.user.color) {
        config.user.color = getRandomColor();
      }

      // Configure l'awareness
      if (provider.awareness) {
        provider.awareness.setLocalStateField('user', config.user);

        // Écoute les changements d'awareness
        provider.awareness.on('change', () => {
          updateUsers();
        });
      }

      // Gère les événements de connexion
      provider.on('status', ({ status }: { status: string }) => {
        console.log('Collaboration status:', status);

        if (status === 'connected') {
          setState((prev) => ({ ...prev, status: 'connected' }));
          measureLatency();

          // Démarre le monitoring de latence
          pingIntervalRef.current = setInterval(measureLatency, 30000);
        } else if (status === 'disconnected') {
          setState((prev) => ({ ...prev, status: 'disconnected' }));

          if (pingIntervalRef.current) {
            clearInterval(pingIntervalRef.current);
            pingIntervalRef.current = null;
          }
        }
      });

      provider.on('sync', (isSynced: boolean) => {
        console.log('Collaboration synced:', isSynced);
        setState((prev) => ({
          ...prev,
          status: isSynced ? 'connected' : 'syncing',
        }));
      });

      // Gère les erreurs
      provider.on('connection-error', (error: Error) => {
        console.error('Collaboration connection error:', error);
        setState((prev) => ({
          ...prev,
          status: 'error',
          error: error.message,
        }));
      });

      provider.on('connection-close', (event: CloseEvent) => {
        console.log('Collaboration connection closed:', event.code, event.reason);
        setState((prev) => ({ ...prev, status: 'disconnected' }));
      });

    } catch (error) {
      console.error('Failed to connect:', error);
      setState((prev) => ({
        ...prev,
        status: 'error',
        error: error instanceof Error ? error.message : 'Connection failed',
      }));
    }
  }, [config, measureLatency, updateUsers]);

  /**
   * Déconnexion
   */
  const disconnect = useCallback(() => {
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
      pingIntervalRef.current = null;
    }

    if (providerRef.current) {
      providerRef.current.destroy();
      providerRef.current = null;
    }

    if (ydocRef.current) {
      ydocRef.current.destroy();
      ydocRef.current = null;
    }

    setState((prev) => ({
      ...prev,
      status: 'disconnected',
      users: new Map(),
    }));
  }, []);

  /**
   * Met à jour la position du curseur
   */
  const updateCursor = useCallback((position: CursorPosition) => {
    const provider = providerRef.current;
    if (!provider || !provider.awareness) return;

    const currentState = provider.awareness.getLocalState() as AwarenessState | null;
    provider.awareness.setLocalStateField('cursor', position);
    provider.awareness.setLocalStateField('timestamp', Date.now());

    // Met à jour l'utilisateur local
    if (currentState?.user) {
      const updatedUser = {
        ...currentState.user,
        cursor: position,
      };
      setState((prev) => ({ ...prev, currentUser: updatedUser }));
    }
  }, []);

  /**
   * Met à jour la sélection
   */
  const updateSelection = useCallback((selection: Selection) => {
    const provider = providerRef.current;
    if (!provider || !provider.awareness) return;

    provider.awareness.setLocalStateField('selection', selection);
    provider.awareness.setLocalStateField('timestamp', Date.now());
  }, []);

  /**
   * Nettoyage à la déconnexion
   */
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  /**
   * Connexion automatique si configuré
   */
  useEffect(() => {
    if (config.autoConnect !== false) {
      connect();
    }
  }, [config.autoConnect, connect]);

  return {
    state,
    connect,
    disconnect,
    updateCursor,
    updateSelection,
    isConnected: state.status === 'connected',
    activeUsers: Array.from(state.users.values()),
  };
}
