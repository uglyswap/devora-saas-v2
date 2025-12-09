import * as React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Command,
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
  CommandShortcut,
} from '@/components/ui/command';
import {
  FolderPlus,
  Settings,
  CreditCard,
  LogOut,
  Search,
  FileCode,
  Rocket,
  Moon,
  Sun,
  Sparkles,
  LayoutDashboard,
  HelpCircle,
  FileText,
  Shield,
  Zap,
} from 'lucide-react';

export default function CommandPalette({
  onCreateProject,
  onLogout,
  projects = [],
  isDarkMode = true,
  onToggleTheme,
}) {
  const [open, setOpen] = React.useState(false);
  const navigate = useNavigate();

  // Global keyboard shortcut
  React.useEffect(() => {
    const down = (e) => {
      // Cmd+K or Ctrl+K
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((open) => !open);
      }
      // Escape to close
      if (e.key === 'Escape') {
        setOpen(false);
      }
    };

    document.addEventListener('keydown', down);
    return () => document.removeEventListener('keydown', down);
  }, []);

  const runCommand = React.useCallback((command) => {
    setOpen(false);
    command();
  }, []);

  // Define all available commands
  const commands = React.useMemo(
    () => [
      // Navigation
      {
        id: 'dashboard',
        label: 'Aller au Dashboard',
        icon: LayoutDashboard,
        shortcut: 'G D',
        keywords: ['accueil', 'home', 'projets'],
        action: () => navigate('/dashboard'),
        group: 'navigation',
      },
      {
        id: 'new-project',
        label: 'Nouveau projet',
        icon: FolderPlus,
        shortcut: 'N P',
        keywords: ['create', 'nouveau', 'ajouter'],
        action: () => {
          if (onCreateProject) {
            onCreateProject();
          } else {
            navigate('/new');
          }
        },
        group: 'navigation',
      },
      {
        id: 'settings',
        label: 'Parametres',
        icon: Settings,
        shortcut: 'G S',
        keywords: ['config', 'options', 'preferences'],
        action: () => navigate('/settings'),
        group: 'navigation',
      },
      {
        id: 'billing',
        label: 'Facturation',
        icon: CreditCard,
        shortcut: 'G B',
        keywords: ['payment', 'subscription', 'plan', 'abonnement'],
        action: () => navigate('/billing'),
        group: 'navigation',
      },

      // Actions
      {
        id: 'ai-chat',
        label: 'Ouvrir le chat AI',
        icon: Sparkles,
        shortcut: 'A I',
        keywords: ['assistant', 'claude', 'gpt', 'aide'],
        action: () => {
          // Dispatch event to open AI chat
          window.dispatchEvent(new CustomEvent('devora:open-ai-chat'));
        },
        group: 'actions',
      },
      {
        id: 'search-files',
        label: 'Rechercher dans les fichiers',
        icon: Search,
        shortcut: 'Cmd+Shift+F',
        keywords: ['find', 'grep', 'chercher'],
        action: () => {
          window.dispatchEvent(new CustomEvent('devora:search-files'));
        },
        group: 'actions',
      },
      {
        id: 'deploy',
        label: 'Deployer le projet',
        icon: Rocket,
        keywords: ['publish', 'production', 'vercel', 'netlify'],
        action: () => {
          window.dispatchEvent(new CustomEvent('devora:deploy'));
        },
        group: 'actions',
      },

      // Settings
      {
        id: 'toggle-theme',
        label: isDarkMode ? 'Passer en mode clair' : 'Passer en mode sombre',
        icon: isDarkMode ? Sun : Moon,
        shortcut: 'T T',
        keywords: ['theme', 'dark', 'light', 'apparence'],
        action: () => {
          if (onToggleTheme) {
            onToggleTheme();
          }
        },
        group: 'settings',
      },
      {
        id: 'logout',
        label: 'Se deconnecter',
        icon: LogOut,
        keywords: ['signout', 'exit', 'quitter'],
        action: () => {
          if (onLogout) {
            onLogout();
          } else {
            navigate('/login');
          }
        },
        group: 'settings',
      },

      // Help
      {
        id: 'help',
        label: 'Aide et support',
        icon: HelpCircle,
        shortcut: '?',
        keywords: ['faq', 'documentation', 'contact'],
        action: () => navigate('/support'),
        group: 'help',
      },
      {
        id: 'docs',
        label: 'Documentation',
        icon: FileText,
        keywords: ['api', 'guide', 'tutorial'],
        action: () => window.open('/docs', '_blank'),
        group: 'help',
      },
      {
        id: 'shortcuts',
        label: 'Raccourcis clavier',
        icon: Zap,
        keywords: ['keyboard', 'hotkeys'],
        action: () => {
          window.dispatchEvent(new CustomEvent('devora:show-shortcuts'));
        },
        group: 'help',
      },
      {
        id: 'privacy',
        label: 'Politique de confidentialite',
        icon: Shield,
        keywords: ['gdpr', 'data', 'privacy'],
        action: () => navigate('/legal/privacy'),
        group: 'help',
      },
    ],
    [navigate, onCreateProject, onLogout, isDarkMode, onToggleTheme]
  );

  // Group commands by category
  const groupedCommands = React.useMemo(() => {
    return {
      navigation: commands.filter((c) => c.group === 'navigation'),
      actions: commands.filter((c) => c.group === 'actions'),
      settings: commands.filter((c) => c.group === 'settings'),
      help: commands.filter((c) => c.group === 'help'),
    };
  }, [commands]);

  return (
    <>
      {/* Trigger button (optional - can be used in navbar) */}
      <button
        onClick={() => setOpen(true)}
        className="hidden sm:flex items-center gap-2 px-3 py-1.5 text-sm text-gray-400 bg-gray-800/50 border border-gray-700 rounded-lg hover:bg-gray-700/50 hover:text-gray-300 transition-colors"
      >
        <Search className="w-4 h-4" />
        <span className="hidden md:inline">Rechercher...</span>
        <kbd className="hidden md:inline-flex items-center gap-1 px-1.5 py-0.5 text-xs font-mono bg-gray-900 border border-gray-600 rounded">
          <span className="text-xs">{navigator.platform.includes('Mac') ? '\u2318' : 'Ctrl'}</span>K
        </kbd>
      </button>

      {/* Command Dialog */}
      <CommandDialog open={open} onOpenChange={setOpen}>
        <CommandInput placeholder="Rechercher une commande, un projet..." />
        <CommandList>
          <CommandEmpty>Aucun resultat trouve.</CommandEmpty>

          {/* Recent Projects */}
          {projects.length > 0 && (
            <>
              <CommandGroup heading="Projets recents">
                {projects.slice(0, 5).map((project) => (
                  <CommandItem
                    key={project.id}
                    value={project.name}
                    onSelect={() => runCommand(() => navigate(`/editor/${project.id}`))}
                  >
                    <FileCode className="mr-2 h-4 w-4" />
                    <span>{project.name}</span>
                  </CommandItem>
                ))}
              </CommandGroup>
              <CommandSeparator />
            </>
          )}

          {/* Navigation */}
          <CommandGroup heading="Navigation">
            {groupedCommands.navigation.map((command) => (
              <CommandItem
                key={command.id}
                value={`${command.label} ${command.keywords?.join(' ') || ''}`}
                onSelect={() => runCommand(command.action)}
              >
                <command.icon className="mr-2 h-4 w-4" />
                <span>{command.label}</span>
                {command.shortcut && (
                  <CommandShortcut>{command.shortcut}</CommandShortcut>
                )}
              </CommandItem>
            ))}
          </CommandGroup>

          <CommandSeparator />

          {/* Actions */}
          <CommandGroup heading="Actions">
            {groupedCommands.actions.map((command) => (
              <CommandItem
                key={command.id}
                value={`${command.label} ${command.keywords?.join(' ') || ''}`}
                onSelect={() => runCommand(command.action)}
              >
                <command.icon className="mr-2 h-4 w-4" />
                <span>{command.label}</span>
                {command.shortcut && (
                  <CommandShortcut>{command.shortcut}</CommandShortcut>
                )}
              </CommandItem>
            ))}
          </CommandGroup>

          <CommandSeparator />

          {/* Settings */}
          <CommandGroup heading="Parametres">
            {groupedCommands.settings.map((command) => (
              <CommandItem
                key={command.id}
                value={`${command.label} ${command.keywords?.join(' ') || ''}`}
                onSelect={() => runCommand(command.action)}
              >
                <command.icon className="mr-2 h-4 w-4" />
                <span>{command.label}</span>
                {command.shortcut && (
                  <CommandShortcut>{command.shortcut}</CommandShortcut>
                )}
              </CommandItem>
            ))}
          </CommandGroup>

          <CommandSeparator />

          {/* Help */}
          <CommandGroup heading="Aide">
            {groupedCommands.help.map((command) => (
              <CommandItem
                key={command.id}
                value={`${command.label} ${command.keywords?.join(' ') || ''}`}
                onSelect={() => runCommand(command.action)}
              >
                <command.icon className="mr-2 h-4 w-4" />
                <span>{command.label}</span>
                {command.shortcut && (
                  <CommandShortcut>{command.shortcut}</CommandShortcut>
                )}
              </CommandItem>
            ))}
          </CommandGroup>
        </CommandList>
      </CommandDialog>
    </>
  );
}

// Hook to programmatically open command palette
export function useCommandPalette() {
  const open = React.useCallback(() => {
    // Simulate Cmd+K
    const event = new KeyboardEvent('keydown', {
      key: 'k',
      metaKey: true,
      ctrlKey: true,
    });
    document.dispatchEvent(event);
  }, []);

  return { open };
}
