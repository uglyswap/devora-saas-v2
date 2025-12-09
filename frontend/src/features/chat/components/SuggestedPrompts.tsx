/**
 * SuggestedPrompts Component
 * Agent: AI Chat Engineer
 *
 * Affichage des suggestions de prompts contextuels
 */

import React from 'react';
import type { SuggestedPrompt } from '../types/chat.types';

export interface SuggestedPromptsProps {
  suggestions: SuggestedPrompt[];
  onSelect: (prompt: SuggestedPrompt) => void;
  className?: string;
}

const DEFAULT_SUGGESTIONS: SuggestedPrompt[] = [
  {
    id: '1',
    text: 'Créer une nouvelle page',
    category: 'create',
    icon: '📄',
    description: 'Créer une nouvelle page avec routing',
  },
  {
    id: '2',
    text: 'Ajouter une API endpoint',
    category: 'create',
    icon: '🔌',
    description: 'Créer une nouvelle route API',
  },
  {
    id: '3',
    text: 'Optimiser les performances',
    category: 'optimize',
    icon: '⚡',
    description: 'Analyser et optimiser le code',
  },
  {
    id: '4',
    text: 'Corriger les erreurs TypeScript',
    category: 'debug',
    icon: '🐛',
    description: 'Résoudre les erreurs de type',
  },
  {
    id: '5',
    text: 'Ajouter des tests',
    category: 'test',
    icon: '🧪',
    description: 'Générer des tests unitaires',
  },
  {
    id: '6',
    text: 'Refactoriser le code',
    category: 'refactor',
    icon: '♻️',
    description: 'Améliorer la structure du code',
  },
];

export const SuggestedPrompts: React.FC<SuggestedPromptsProps> = ({
  suggestions,
  onSelect,
  className = '',
}) => {
  const prompts = suggestions.length > 0 ? suggestions : DEFAULT_SUGGESTIONS;

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'create':
        return 'bg-green-50 text-green-700 border-green-200 hover:bg-green-100';
      case 'modify':
        return 'bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100';
      case 'debug':
        return 'bg-red-50 text-red-700 border-red-200 hover:bg-red-100';
      case 'optimize':
        return 'bg-purple-50 text-purple-700 border-purple-200 hover:bg-purple-100';
      case 'explain':
        return 'bg-yellow-50 text-yellow-700 border-yellow-200 hover:bg-yellow-100';
      case 'test':
        return 'bg-indigo-50 text-indigo-700 border-indigo-200 hover:bg-indigo-100';
      case 'refactor':
        return 'bg-orange-50 text-orange-700 border-orange-200 hover:bg-orange-100';
      default:
        return 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100';
    }
  };

  return (
    <div className={`space-y-3 ${className}`}>
      <h4 className="text-sm font-medium text-gray-700">Suggestions</h4>
      <div className="grid grid-cols-1 gap-2">
        {prompts.map((prompt) => (
          <button
            key={prompt.id}
            onClick={() => onSelect(prompt)}
            className={`text-left p-3 rounded-lg border transition-colors ${getCategoryColor(prompt.category)}`}
          >
            <div className="flex items-start gap-2">
              {prompt.icon && <span className="text-lg">{prompt.icon}</span>}
              <div className="flex-1 min-w-0">
                <p className="font-medium text-sm">{prompt.text}</p>
                {prompt.description && <p className="text-xs opacity-75 mt-1">{prompt.description}</p>}
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};

export default SuggestedPrompts;
