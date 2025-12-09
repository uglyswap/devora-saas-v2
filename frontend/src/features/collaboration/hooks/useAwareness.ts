/**
 * Hook pour gérer l'awareness (curseurs, présence)
 */

import { useEffect, useState } from 'react';
import type { WebsocketProvider } from 'y-websocket';
import type { User, AwarenessState } from '../types';

export interface UseAwarenessReturn {
  users: Map<number, User>;
  localClientId: number | null;
  isAlone: boolean;
}

export function useAwareness(provider: WebsocketProvider | null): UseAwarenessReturn {
  const [users, setUsers] = useState<Map<number, User>>(new Map());
  const [localClientId, setLocalClientId] = useState<number | null>(null);

  useEffect(() => {
    if (!provider || !provider.awareness) return;

    const awareness = provider.awareness;
    setLocalClientId(awareness.clientID);

    const updateUsers = () => {
      const newUsers = new Map<number, User>();
      const states = awareness.getStates();

      states.forEach((state: unknown, clientId: number) => {
        // Skip le client local
        if (clientId === awareness.clientID) return;

        const awarenessState = state as AwarenessState;
        if (awarenessState.user) {
          newUsers.set(clientId, awarenessState.user);
        }
      });

      setUsers(newUsers);
    };

    // Mise à jour initiale
    updateUsers();

    // Écoute les changements
    awareness.on('change', updateUsers);

    return () => {
      awareness.off('change', updateUsers);
    };
  }, [provider]);

  return {
    users,
    localClientId,
    isAlone: users.size === 0,
  };
}
