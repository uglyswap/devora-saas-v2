import * as React from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Keyboard } from 'lucide-react';

const shortcutCategories = [
  {
    name: 'Generale',
    shortcuts: [
      { keys: ['Cmd', 'K'], description: 'Ouvrir la palette de commandes' },
      { keys: ['Cmd', 'S'], description: 'Sauvegarder le fichier' },
      { keys: ['Cmd', 'Shift', 'S'], description: 'Sauvegarder tous les fichiers' },
      { keys: ['Cmd', 'P'], description: 'Rechercher un fichier' },
      { keys: ['Cmd', 'Shift', 'F'], description: 'Rechercher dans les fichiers' },
      { keys: ['Escape'], description: 'Fermer le dialogue actif' },
    ],
  },
  {
    name: 'Editeur',
    shortcuts: [
      { keys: ['Cmd', 'Z'], description: 'Annuler' },
      { keys: ['Cmd', 'Shift', 'Z'], description: 'Refaire' },
      { keys: ['Cmd', 'D'], description: 'Selectionner le mot suivant' },
      { keys: ['Cmd', '/'], description: 'Commenter/Decommenter' },
      { keys: ['Cmd', 'L'], description: 'Selectionner la ligne' },
      { keys: ['Cmd', 'Enter'], description: 'Executer le code' },
      { keys: ['Alt', 'Up'], description: 'Deplacer la ligne vers le haut' },
      { keys: ['Alt', 'Down'], description: 'Deplacer la ligne vers le bas' },
    ],
  },
  {
    name: 'Navigation',
    shortcuts: [
      { keys: ['G', 'D'], description: 'Aller au Dashboard' },
      { keys: ['G', 'S'], description: 'Aller aux Parametres' },
      { keys: ['G', 'B'], description: 'Aller a la Facturation' },
      { keys: ['N', 'P'], description: 'Nouveau projet' },
    ],
  },
  {
    name: 'Chat AI',
    shortcuts: [
      { keys: ['Cmd', 'I'], description: 'Ouvrir le chat AI' },
      { keys: ['Enter'], description: 'Envoyer le message' },
      { keys: ['Shift', 'Enter'], description: 'Nouvelle ligne' },
      { keys: ['Cmd', 'Up'], description: 'Message precedent' },
      { keys: ['Cmd', 'Down'], description: 'Message suivant' },
    ],
  },
  {
    name: 'Panneaux',
    shortcuts: [
      { keys: ['Cmd', 'B'], description: 'Toggle barre laterale' },
      { keys: ['Cmd', 'J'], description: 'Toggle terminal' },
      { keys: ['Cmd', '1'], description: 'Focus explorateur' },
      { keys: ['Cmd', '2'], description: 'Focus editeur' },
      { keys: ['Cmd', '3'], description: 'Focus preview' },
    ],
  },
];

export default function KeyboardShortcuts({ open, onOpenChange }) {
  // Global shortcut to open this modal
  React.useEffect(() => {
    const handleKeyDown = (e) => {
      // ? key opens shortcuts
      if (e.key === '?' && !e.ctrlKey && !e.metaKey) {
        // Don't trigger if typing in an input
        const target = e.target;
        if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable) {
          return;
        }
        e.preventDefault();
        onOpenChange(true);
      }
    };

    // Listen for custom event from CommandPalette
    const handleShowShortcuts = () => onOpenChange(true);
    window.addEventListener('devora:show-shortcuts', handleShowShortcuts);
    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('devora:show-shortcuts', handleShowShortcuts);
    };
  }, [onOpenChange]);

  // Format key for display (handles Mac vs Windows)
  const formatKey = (key) => {
    const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;

    const keyMap = {
      Cmd: isMac ? '\u2318' : 'Ctrl',
      Alt: isMac ? '\u2325' : 'Alt',
      Shift: '\u21E7',
      Enter: '\u21B5',
      Escape: 'Esc',
      Up: '\u2191',
      Down: '\u2193',
      Left: '\u2190',
      Right: '\u2192',
    };

    return keyMap[key] || key;
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto bg-gray-900 border-gray-700">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-white">
            <Keyboard className="w-5 h-5 text-purple-400" />
            Raccourcis clavier
          </DialogTitle>
        </DialogHeader>

        <div className="grid gap-6 mt-4">
          {shortcutCategories.map((category) => (
            <div key={category.name}>
              <h3 className="text-sm font-semibold text-purple-400 mb-3 uppercase tracking-wider">
                {category.name}
              </h3>
              <div className="grid gap-2">
                {category.shortcuts.map((shortcut, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between py-2 px-3 rounded-lg bg-gray-800/50 hover:bg-gray-800 transition-colors"
                  >
                    <span className="text-sm text-gray-300">{shortcut.description}</span>
                    <div className="flex items-center gap-1">
                      {shortcut.keys.map((key, keyIndex) => (
                        <React.Fragment key={keyIndex}>
                          <kbd className="px-2 py-1 text-xs font-mono bg-gray-700 border border-gray-600 rounded text-gray-200 min-w-[24px] text-center">
                            {formatKey(key)}
                          </kbd>
                          {keyIndex < shortcut.keys.length - 1 && (
                            <span className="text-gray-500 text-xs">+</span>
                          )}
                        </React.Fragment>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-6 pt-4 border-t border-gray-700">
          <p className="text-xs text-gray-500 text-center">
            Appuyez sur <kbd className="px-1 py-0.5 text-xs font-mono bg-gray-700 border border-gray-600 rounded">?</kbd> n'importe ou pour voir ces raccourcis
          </p>
        </div>
      </DialogContent>
    </Dialog>
  );
}

// Hook for keyboard shortcuts
export function useKeyboardShortcuts() {
  const [open, setOpen] = React.useState(false);
  return { open, setOpen, KeyboardShortcutsModal: () => <KeyboardShortcuts open={open} onOpenChange={setOpen} /> };
}
