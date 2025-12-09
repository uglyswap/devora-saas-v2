/**
 * Indicateur de présence des utilisateurs
 */

import React from 'react';
import type { User } from '../types';

interface PresenceIndicatorProps {
  users: User[];
  maxVisible?: number;
  className?: string;
}

export function PresenceIndicator({ users, maxVisible = 5, className = '' }: PresenceIndicatorProps) {
  const visibleUsers = users.slice(0, maxVisible);
  const hiddenCount = Math.max(0, users.length - maxVisible);

  if (users.length === 0) {
    return (
      <div className={`flex items-center gap-2 px-3 py-1.5 rounded-md bg-gray-100 dark:bg-gray-800 ${className}`}>
        <span className="text-xs text-gray-500 dark:text-gray-400">
          Vous êtes seul
        </span>
      </div>
    );
  }

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      {/* Avatars des utilisateurs */}
      <div className="flex -space-x-2">
        {visibleUsers.map((user) => (
          <UserAvatar key={user.id} user={user} />
        ))}

        {/* Indicateur d'utilisateurs cachés */}
        {hiddenCount > 0 && (
          <div
            className="w-8 h-8 rounded-full bg-gray-300 dark:bg-gray-700 flex items-center justify-center text-xs font-medium text-gray-700 dark:text-gray-300 ring-2 ring-white dark:ring-gray-900"
            title={`+${hiddenCount} autres utilisateurs`}
          >
            +{hiddenCount}
          </div>
        )}
      </div>

      {/* Nombre d'utilisateurs */}
      <span className="text-xs font-medium text-gray-700 dark:text-gray-300">
        {users.length === 1 ? '1 utilisateur' : `${users.length} utilisateurs`}
      </span>
    </div>
  );
}

interface UserAvatarProps {
  user: User;
}

function UserAvatar({ user }: UserAvatarProps) {
  const initials = user.name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);

  return (
    <div
      className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium text-white ring-2 ring-white dark:ring-gray-900"
      style={{ backgroundColor: user.color }}
      title={user.name}
    >
      {user.avatar ? (
        <img src={user.avatar} alt={user.name} className="w-full h-full rounded-full" />
      ) : (
        initials
      )}
    </div>
  );
}
