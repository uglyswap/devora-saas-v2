/**
 * Provider React pour la collaboration
 */

import React, { createContext, useContext, useMemo } from 'react';
import { useCollaboration } from '../hooks';
import type { CollaborationConfig, CollaborationContextValue } from '../types';

const CollaborationContext = createContext<CollaborationContextValue | null>(null);

interface CollaborationProviderProps {
  children: React.ReactNode;
  config: CollaborationConfig;
}

export function CollaborationProvider({ children, config }: CollaborationProviderProps) {
  const {
    state,
    connect,
    disconnect,
    updateCursor,
    updateSelection,
  } = useCollaboration(config);

  const value = useMemo<CollaborationContextValue>(
    () => ({
      state,
      actions: {
        connect,
        disconnect,
        updateCursor,
        updateSelection,
      },
    }),
    [state, connect, disconnect, updateCursor, updateSelection]
  );

  return (
    <CollaborationContext.Provider value={value}>
      {children}
    </CollaborationContext.Provider>
  );
}

/**
 * Hook pour accéder au contexte de collaboration
 */
export function useCollaborationContext(): CollaborationContextValue {
  const context = useContext(CollaborationContext);

  if (!context) {
    throw new Error(
      'useCollaborationContext must be used within a CollaborationProvider'
    );
  }

  return context;
}
