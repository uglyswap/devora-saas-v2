/**
 * Indicateur de statut de connexion
 */

import React from 'react';
import type { ConnectionStatus as Status } from '../types';

interface ConnectionStatusProps {
  status: Status;
  latency?: number;
  className?: string;
}

const statusConfig = {
  connecting: {
    label: 'Connexion...',
    color: 'bg-yellow-500',
    icon: '⟳',
  },
  connected: {
    label: 'Connecté',
    color: 'bg-green-500',
    icon: '●',
  },
  syncing: {
    label: 'Synchronisation...',
    color: 'bg-blue-500',
    icon: '⇄',
  },
  synced: {
    label: 'Synchronisé',
    color: 'bg-green-500',
    icon: '✓',
  },
  disconnected: {
    label: 'Déconnecté',
    color: 'bg-gray-500',
    icon: '○',
  },
  error: {
    label: 'Erreur',
    color: 'bg-red-500',
    icon: '⚠',
  },
};

export function ConnectionStatus({ status, latency, className = '' }: ConnectionStatusProps) {
  const config = statusConfig[status];

  return (
    <div className={`flex items-center gap-2 px-3 py-1.5 rounded-md bg-gray-100 dark:bg-gray-800 ${className}`}>
      {/* Indicateur de statut */}
      <div className="flex items-center gap-1.5">
        <span className={`w-2 h-2 rounded-full ${config.color} animate-pulse`} />
        <span className="text-xs font-medium text-gray-700 dark:text-gray-300">
          {config.label}
        </span>
      </div>

      {/* Latence si connecté */}
      {status === 'connected' && latency !== undefined && (
        <span className="text-xs text-gray-500 dark:text-gray-400">
          {latency}ms
        </span>
      )}
    </div>
  );
}
