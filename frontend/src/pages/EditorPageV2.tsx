/**
 * EditorPageV2 - Next-generation AI code editor
 *
 * This is the completely redesigned editor page that provides:
 * - WebContainer-based browser-native preview (like Bolt.new)
 * - Select & Edit visual editing (like Lovable)
 * - One-click deployment to multiple providers
 * - Modern, polished UI/UX
 *
 * @author Devora Team
 * @version 2.0.0
 */

import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import Editor from '@monaco-editor/react';
import { toast } from 'sonner';
import axios from 'axios';
import JSZip from 'jszip';

// UI Components
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { ScrollArea } from '../components/ui/scroll-area';
import { Badge } from '../components/ui/badge';
import { Separator } from '../components/ui/separator';
import { Switch } from '../components/ui/switch';
import { Label } from '../components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '../components/ui/select';
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup
} from '../components/ui/resizable';
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
  TooltipProvider
} from '../components/ui/tooltip';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger
} from '../components/ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger
} from '../components/ui/dialog';
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger
} from '../components/ui/sheet';
import {
  Command,
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
  CommandShortcut
} from '../components/ui/command';

// Icons
import {
  ArrowLeft,
  Send,
  Save,
  Download,
  Github,
  Globe,
  Loader2,
  Code2,
  Eye,
  MessageSquare,
  FileCode,
  Play,
  Settings,
  Plus,
  X,
  Copy,
  Check,
  Bot,
  Sparkles,
  Trash2,
  ExternalLink,
  Rocket,
  Layers,
  Terminal,
  FolderTree,
  Search,
  Command as CommandIcon,
  Sun,
  Moon,
  Laptop,
  ChevronRight,
  ChevronDown,
  File,
  Folder,
  MoreVertical,
  RefreshCw,
  Maximize2,
  Minimize2,
  PanelLeftClose,
  PanelLeftOpen,
  Wand2,
  MousePointer2,
  Undo2,
  Redo2,
  Zap,
  History,
  GitBranch,
  Upload
} from 'lucide-react';

// Custom Components
import { WebContainerPreview } from '../components/preview/WebContainerPreview';
import { SelectAndEdit } from '../components/editor/SelectAndEdit';
import { OneClickDeploy } from '../components/deploy/OneClickDeploy';

// Utils
import { cn } from '../lib/utils';

// Constants
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
const API = `${BACKEND_URL}/api`;

// Types
interface ProjectFile {
  name: string;
  content: string;
  language?: string;
}

interface Project {
  id?: string;
  name: string;
  description: string;
  files: ProjectFile[];
  conversation_history: Array<{
    role: 'user' | 'assistant';
    content: string;
  }>;
}

interface AIModel {
  id: string;
  name: string;
  context_length?: number;
  pricing?: {
    prompt: number;
    completion: number;
  };
}

// File tree helpers
interface FileTreeNode {
  name: string;
  path: string;
  type: 'file' | 'folder';
  children?: FileTreeNode[];
  language?: string;
}

function buildFileTree(files: ProjectFile[]): FileTreeNode[] {
  const root: FileTreeNode[] = [];
  const nodeMap: Record<string, FileTreeNode> = {};

  // Sort files to ensure folders come before their contents
  const sortedFiles = [...files].sort((a, b) => a.name.localeCompare(b.name));

  for (const file of sortedFiles) {
    const parts = file.name.split('/').filter(Boolean);
    let currentPath = '';

    for (let i = 0; i < parts.length; i++) {
      const part = parts[i];
      const isLast = i === parts.length - 1;
      const parentPath = currentPath;
      currentPath = currentPath ? `${currentPath}/${part}` : part;

      if (!nodeMap[currentPath]) {
        const node: FileTreeNode = {
          name: part,
          path: currentPath,
          type: isLast ? 'file' : 'folder',
          language: isLast ? file.language : undefined,
          children: isLast ? undefined : []
        };

        nodeMap[currentPath] = node;

        if (parentPath && nodeMap[parentPath]) {
          nodeMap[parentPath].children?.push(node);
        } else if (!parentPath) {
          root.push(node);
        }
      }
    }
  }

  return root;
}

// Default files for new projects
const DEFAULT_FILES: ProjectFile[] = [
  {
    name: 'index.html',
    content: `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>My App</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <div class="container">
    <h1>Welcome to Devora</h1>
    <p>Start building your next app with AI</p>
    <button id="cta">Get Started</button>
  </div>
  <script src="script.js"></script>
</body>
</html>`,
    language: 'html'
  },
  {
    name: 'styles.css',
    content: `* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.container {
  text-align: center;
  color: white;
  padding: 2rem;
}

h1 {
  font-size: 3rem;
  margin-bottom: 1rem;
}

p {
  font-size: 1.25rem;
  opacity: 0.9;
  margin-bottom: 2rem;
}

button {
  background: white;
  color: #667eea;
  border: none;
  padding: 1rem 2rem;
  font-size: 1rem;
  font-weight: 600;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

button:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
}`,
    language: 'css'
  },
  {
    name: 'script.js',
    content: `document.addEventListener('DOMContentLoaded', () => {
  const button = document.getElementById('cta');

  button.addEventListener('click', () => {
    alert('Welcome to Devora! 🚀');
  });

  console.log('App initialized');
});`,
    language: 'javascript'
  }
];

/**
 * FileTreeItem Component
 */
function FileTreeItem({
  node,
  depth = 0,
  selectedFile,
  onSelect,
  expandedFolders,
  onToggleFolder
}: {
  node: FileTreeNode;
  depth?: number;
  selectedFile: string | null;
  onSelect: (path: string) => void;
  expandedFolders: Set<string>;
  onToggleFolder: (path: string) => void;
}) {
  const isExpanded = expandedFolders.has(node.path);
  const isSelected = selectedFile === node.path;

  const handleClick = () => {
    if (node.type === 'folder') {
      onToggleFolder(node.path);
    } else {
      onSelect(node.path);
    }
  };

  return (
    <>
      <button
        onClick={handleClick}
        className={cn(
          'w-full flex items-center gap-2 px-2 py-1.5 text-sm hover:bg-accent/50 rounded-md transition-colors text-left',
          isSelected && 'bg-accent text-accent-foreground'
        )}
        style={{ paddingLeft: `${depth * 12 + 8}px` }}
      >
        {node.type === 'folder' ? (
          <>
            {isExpanded ? (
              <ChevronDown className="h-4 w-4 text-muted-foreground" />
            ) : (
              <ChevronRight className="h-4 w-4 text-muted-foreground" />
            )}
            <Folder className="h-4 w-4 text-blue-500" />
          </>
        ) : (
          <>
            <span className="w-4" />
            <FileCode className="h-4 w-4 text-muted-foreground" />
          </>
        )}
        <span className="truncate">{node.name}</span>
      </button>

      {node.type === 'folder' && isExpanded && node.children && (
        <div>
          {node.children.map((child) => (
            <FileTreeItem
              key={child.path}
              node={child}
              depth={depth + 1}
              selectedFile={selectedFile}
              onSelect={onSelect}
              expandedFolders={expandedFolders}
              onToggleFolder={onToggleFolder}
            />
          ))}
        </div>
      )}
    </>
  );
}

/**
 * ChatMessage Component
 */
function ChatMessage({
  role,
  content
}: {
  role: 'user' | 'assistant';
  content: string;
}) {
  return (
    <div
      className={cn(
        'flex gap-3 p-4 rounded-lg',
        role === 'user' ? 'bg-primary/10' : 'bg-muted/50'
      )}
    >
      <div
        className={cn(
          'w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0',
          role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-violet-500 text-white'
        )}
      >
        {role === 'user' ? 'U' : <Bot className="h-4 w-4" />}
      </div>
      <div className="flex-1 overflow-hidden">
        <p className="text-sm font-medium mb-1">
          {role === 'user' ? 'You' : 'Devora AI'}
        </p>
        <div className="text-sm text-muted-foreground whitespace-pre-wrap break-words">
          {content}
        </div>
      </div>
    </div>
  );
}

/**
 * EditorPageV2 Component
 */
export function EditorPageV2() {
  const navigate = useNavigate();
  const { projectId } = useParams<{ projectId?: string }>();

  // State
  const [project, setProject] = useState<Project>({
    name: 'New Project',
    description: '',
    files: DEFAULT_FILES,
    conversation_history: []
  });

  const [currentFilePath, setCurrentFilePath] = useState<string>('index.html');
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set());
  const [chatMessages, setChatMessages] = useState<Array<{ role: 'user' | 'assistant'; content: string }>>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  // UI State
  const [activeView, setActiveView] = useState<'code' | 'preview' | 'split'>('split');
  const [showSidebar, setShowSidebar] = useState(true);
  const [showChat, setShowChat] = useState(true);
  const [previewMode, setPreviewMode] = useState<'webcontainer' | 'iframe'>('iframe');
  const [isSelectAndEditActive, setIsSelectAndEditActive] = useState(false);

  // Settings
  const [selectedModel, setSelectedModel] = useState('openai/gpt-4o');
  const [availableModels, setAvailableModels] = useState<AIModel[]>([]);
  const [apiKey, setApiKey] = useState('');
  const [useAgenticMode, setUseAgenticMode] = useState(true);
  const [useFullstackMode, setUseFullstackMode] = useState(false);

  // Command palette
  const [showCommandPalette, setShowCommandPalette] = useState(false);

  // Refs
  const chatEndRef = useRef<HTMLDivElement>(null);
  const previewIframeRef = useRef<HTMLIFrameElement>(null);
  const editorRef = useRef<any>(null);

  // Computed values
  const currentFile = useMemo(() => {
    return project.files.find(f => f.name === currentFilePath);
  }, [project.files, currentFilePath]);

  const fileTree = useMemo(() => {
    return buildFileTree(project.files);
  }, [project.files]);

  // Effects
  useEffect(() => {
    // Load API key from localStorage or settings
    const savedKey = localStorage.getItem('devora_api_key');
    if (savedKey) {
      setApiKey(savedKey);
    }

    // Load available models
    loadModels();

    // Load project if ID provided
    if (projectId) {
      loadProject(projectId);
    }
  }, [projectId]);

  useEffect(() => {
    // Scroll to bottom of chat
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  useEffect(() => {
    // Keyboard shortcuts
    const handleKeyDown = (e: KeyboardEvent) => {
      // Command palette: Cmd/Ctrl + K
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setShowCommandPalette(true);
      }
      // Save: Cmd/Ctrl + S
      if ((e.metaKey || e.ctrlKey) && e.key === 's') {
        e.preventDefault();
        handleSave();
      }
      // Toggle preview: Cmd/Ctrl + P
      if ((e.metaKey || e.ctrlKey) && e.key === 'p' && e.shiftKey) {
        e.preventDefault();
        setActiveView(prev => prev === 'code' ? 'preview' : 'code');
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // API Functions
  const loadModels = async () => {
    try {
      const response = await axios.get(`${API}/openrouter/models`);
      setAvailableModels(response.data.data || []);
    } catch (error) {
      console.error('Failed to load models:', error);
    }
  };

  const loadProject = async (id: string) => {
    try {
      const response = await axios.get(`${API}/projects/${id}`);
      setProject(response.data);
      if (response.data.files.length > 0) {
        setCurrentFilePath(response.data.files[0].name);
      }
    } catch (error) {
      toast.error('Failed to load project');
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      if (projectId) {
        await axios.put(`${API}/projects/${projectId}`, project);
      } else {
        const response = await axios.post(`${API}/projects`, project);
        navigate(`/editor/${response.data.id}`, { replace: true });
      }
      toast.success('Project saved');
    } catch (error) {
      toast.error('Failed to save project');
    } finally {
      setIsSaving(false);
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isGenerating) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    setChatMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsGenerating(true);

    try {
      let endpoint = `${API}/generate/openrouter`;
      let body: any = {
        message: userMessage,
        model: selectedModel,
        api_key: apiKey,
        current_files: project.files
      };

      if (useFullstackMode) {
        endpoint = `${API}/generate/fullstack`;
        body = {
          ...body,
          project_type: 'saas',
          conversation_history: chatMessages
        };
      } else if (useAgenticMode) {
        endpoint = `${API}/generate/agentic`;
      }

      const response = await axios.post(endpoint, body);

      if (response.data.files) {
        setProject(prev => ({
          ...prev,
          files: response.data.files
        }));
      }

      const assistantMessage = response.data.message || 'Code generated successfully!';
      setChatMessages(prev => [...prev, { role: 'assistant', content: assistantMessage }]);

      toast.success('Code generated!');
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Generation failed';
      setChatMessages(prev => [...prev, { role: 'assistant', content: `Error: ${errorMessage}` }]);
      toast.error(errorMessage);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleFileChange = (content: string | undefined) => {
    if (content === undefined) return;

    setProject(prev => ({
      ...prev,
      files: prev.files.map(f =>
        f.name === currentFilePath ? { ...f, content } : f
      )
    }));
  };

  const handleSelectAndEditRequest = async (element: any, instruction: string) => {
    const message = `For the element ${element.selector} (${element.tagName}), ${instruction}`;
    setInputMessage(message);
    await handleSendMessage();
  };

  const handleDownload = async () => {
    const zip = new JSZip();
    project.files.forEach(file => {
      zip.file(file.name, file.content);
    });

    const blob = await zip.generateAsync({ type: 'blob' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${project.name.toLowerCase().replace(/\s+/g, '-')}.zip`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success('Project downloaded');
  };

  const createNewFile = (fileName: string) => {
    if (project.files.some(f => f.name === fileName)) {
      toast.error('File already exists');
      return;
    }

    const ext = fileName.split('.').pop() || '';
    const languageMap: Record<string, string> = {
      'js': 'javascript',
      'jsx': 'javascript',
      'ts': 'typescript',
      'tsx': 'typescript',
      'html': 'html',
      'css': 'css',
      'json': 'json',
      'md': 'markdown'
    };

    setProject(prev => ({
      ...prev,
      files: [...prev.files, {
        name: fileName,
        content: '',
        language: languageMap[ext] || 'plaintext'
      }]
    }));
    setCurrentFilePath(fileName);
    toast.success(`Created ${fileName}`);
  };

  const deleteFile = (fileName: string) => {
    if (project.files.length === 1) {
      toast.error('Cannot delete the last file');
      return;
    }

    setProject(prev => ({
      ...prev,
      files: prev.files.filter(f => f.name !== fileName)
    }));

    if (currentFilePath === fileName) {
      setCurrentFilePath(project.files[0].name);
    }

    toast.success(`Deleted ${fileName}`);
  };

  const toggleFolder = (path: string) => {
    setExpandedFolders(prev => {
      const next = new Set(prev);
      if (next.has(path)) {
        next.delete(path);
      } else {
        next.add(path);
      }
      return next;
    });
  };

  // Preview content generation
  const previewContent = useMemo(() => {
    const htmlFile = project.files.find(f => f.name.endsWith('.html'));
    if (!htmlFile) return '';

    let html = htmlFile.content;

    // Inject CSS
    project.files
      .filter(f => f.name.endsWith('.css'))
      .forEach(cssFile => {
        const cssContent = `<style>${cssFile.content}</style>`;
        html = html.replace('</head>', `${cssContent}</head>`);
      });

    // Inject JS
    project.files
      .filter(f => f.name.endsWith('.js'))
      .forEach(jsFile => {
        const jsContent = `<script>${jsFile.content}</script>`;
        html = html.replace('</body>', `${jsContent}</body>`);
      });

    return html;
  }, [project.files]);

  return (
    <TooltipProvider>
      <div className="h-screen flex flex-col bg-background">
        {/* Header */}
        <header className="h-14 border-b flex items-center justify-between px-4 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => navigate('/dashboard')}>
              <ArrowLeft className="h-4 w-4" />
            </Button>

            <Separator orientation="vertical" className="h-6" />

            <Input
              value={project.name}
              onChange={(e) => setProject(prev => ({ ...prev, name: e.target.value }))}
              className="w-48 h-8 text-sm font-medium"
              placeholder="Project name"
            />

            <Badge variant="outline" className="gap-1">
              <File className="h-3 w-3" />
              {project.files.length} files
            </Badge>
          </div>

          <div className="flex items-center gap-2">
            {/* View Toggle */}
            <div className="flex items-center border rounded-lg p-1">
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant={activeView === 'code' ? 'secondary' : 'ghost'}
                    size="sm"
                    className="h-7 px-2"
                    onClick={() => setActiveView('code')}
                  >
                    <Code2 className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Code View</TooltipContent>
              </Tooltip>

              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant={activeView === 'split' ? 'secondary' : 'ghost'}
                    size="sm"
                    className="h-7 px-2"
                    onClick={() => setActiveView('split')}
                  >
                    <Layers className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Split View</TooltipContent>
              </Tooltip>

              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant={activeView === 'preview' ? 'secondary' : 'ghost'}
                    size="sm"
                    className="h-7 px-2"
                    onClick={() => setActiveView('preview')}
                  >
                    <Eye className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Preview</TooltipContent>
              </Tooltip>
            </div>

            <Separator orientation="vertical" className="h-6" />

            {/* Actions */}
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="outline" size="icon" onClick={handleSave} disabled={isSaving}>
                  {isSaving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
                </Button>
              </TooltipTrigger>
              <TooltipContent>Save (⌘S)</TooltipContent>
            </Tooltip>

            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="outline" size="icon" onClick={handleDownload}>
                  <Download className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Download ZIP</TooltipContent>
            </Tooltip>

            <OneClickDeploy
              files={project.files}
              projectName={project.name}
              onDeploySuccess={(result) => {
                toast.success('Deployed successfully!');
                console.log('Deployment result:', result);
              }}
            />

            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="outline"
                  size="icon"
                  onClick={() => setShowCommandPalette(true)}
                >
                  <CommandIcon className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Command Palette (⌘K)</TooltipContent>
            </Tooltip>
          </div>
        </header>

        {/* Main Content */}
        <div className="flex-1 flex overflow-hidden">
          {/* Sidebar */}
          {showSidebar && (
            <div className="w-64 border-r flex flex-col bg-muted/30">
              {/* File Explorer Header */}
              <div className="h-10 px-3 flex items-center justify-between border-b">
                <span className="text-sm font-medium flex items-center gap-2">
                  <FolderTree className="h-4 w-4" />
                  Explorer
                </span>
                <Dialog>
                  <DialogTrigger asChild>
                    <Button variant="ghost" size="icon" className="h-6 w-6">
                      <Plus className="h-4 w-4" />
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Create New File</DialogTitle>
                    </DialogHeader>
                    <form onSubmit={(e) => {
                      e.preventDefault();
                      const input = e.currentTarget.elements.namedItem('filename') as HTMLInputElement;
                      if (input.value) {
                        createNewFile(input.value);
                      }
                    }}>
                      <Input
                        name="filename"
                        placeholder="filename.tsx"
                        className="mt-4"
                      />
                      <DialogFooter className="mt-4">
                        <Button type="submit">Create</Button>
                      </DialogFooter>
                    </form>
                  </DialogContent>
                </Dialog>
              </div>

              {/* File Tree */}
              <ScrollArea className="flex-1">
                <div className="p-2">
                  {fileTree.map(node => (
                    <FileTreeItem
                      key={node.path}
                      node={node}
                      selectedFile={currentFilePath}
                      onSelect={setCurrentFilePath}
                      expandedFolders={expandedFolders}
                      onToggleFolder={toggleFolder}
                    />
                  ))}
                </div>
              </ScrollArea>
            </div>
          )}

          {/* Editor & Preview Area */}
          <div className="flex-1 flex flex-col overflow-hidden">
            <ResizablePanelGroup direction="horizontal">
              {/* Code Editor Panel */}
              {(activeView === 'code' || activeView === 'split') && (
                <ResizablePanel defaultSize={activeView === 'split' ? 50 : 100} minSize={30}>
                  <div className="h-full flex flex-col">
                    {/* Editor Tabs */}
                    <div className="h-10 border-b flex items-center px-2 gap-1 bg-muted/30">
                      {project.files.slice(0, 5).map(file => (
                        <button
                          key={file.name}
                          onClick={() => setCurrentFilePath(file.name)}
                          className={cn(
                            'flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-md transition-colors',
                            currentFilePath === file.name
                              ? 'bg-background shadow-sm'
                              : 'hover:bg-accent/50'
                          )}
                        >
                          <FileCode className="h-3.5 w-3.5 text-muted-foreground" />
                          {file.name.split('/').pop()}
                          {currentFilePath === file.name && (
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                deleteFile(file.name);
                              }}
                              className="ml-1 hover:bg-destructive/20 rounded p-0.5"
                            >
                              <X className="h-3 w-3" />
                            </button>
                          )}
                        </button>
                      ))}
                    </div>

                    {/* Monaco Editor */}
                    <div className="flex-1">
                      <Editor
                        height="100%"
                        defaultLanguage={currentFile?.language || 'javascript'}
                        language={currentFile?.language || 'javascript'}
                        value={currentFile?.content || ''}
                        onChange={handleFileChange}
                        theme="vs-dark"
                        onMount={(editor) => {
                          editorRef.current = editor;
                        }}
                        options={{
                          minimap: { enabled: false },
                          fontSize: 14,
                          lineHeight: 1.6,
                          padding: { top: 16 },
                          scrollBeyondLastLine: false,
                          automaticLayout: true,
                          tabSize: 2,
                          wordWrap: 'on'
                        }}
                      />
                    </div>
                  </div>
                </ResizablePanel>
              )}

              {activeView === 'split' && <ResizableHandle withHandle />}

              {/* Preview Panel */}
              {(activeView === 'preview' || activeView === 'split') && (
                <ResizablePanel defaultSize={activeView === 'split' ? 50 : 100} minSize={30}>
                  <div className="h-full flex flex-col">
                    {/* Preview Header */}
                    <div className="h-10 border-b flex items-center justify-between px-3 bg-muted/30">
                      <div className="flex items-center gap-2">
                        <Globe className="h-4 w-4 text-muted-foreground" />
                        <span className="text-sm font-medium">Preview</span>
                      </div>

                      <div className="flex items-center gap-2">
                        {/* Select & Edit Toggle */}
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <Button
                              variant={isSelectAndEditActive ? 'default' : 'outline'}
                              size="sm"
                              className="h-7 gap-1.5"
                              onClick={() => setIsSelectAndEditActive(!isSelectAndEditActive)}
                            >
                              <MousePointer2 className="h-3.5 w-3.5" />
                              Select & Edit
                            </Button>
                          </TooltipTrigger>
                          <TooltipContent>Click elements to edit with AI</TooltipContent>
                        </Tooltip>

                        <Select
                          value={previewMode}
                          onValueChange={(v) => setPreviewMode(v as 'webcontainer' | 'iframe')}
                        >
                          <SelectTrigger className="h-7 w-36 text-xs">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="iframe">Simple Preview</SelectItem>
                            <SelectItem value="webcontainer">WebContainer (Node.js)</SelectItem>
                          </SelectContent>
                        </Select>

                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7"
                          onClick={() => {
                            if (previewIframeRef.current) {
                              previewIframeRef.current.src = previewIframeRef.current.src;
                            }
                          }}
                        >
                          <RefreshCw className="h-3.5 w-3.5" />
                        </Button>
                      </div>
                    </div>

                    {/* Preview Content */}
                    <div className="flex-1 bg-white relative">
                      {previewMode === 'webcontainer' ? (
                        <WebContainerPreview
                          files={project.files}
                          autoStart={false}
                          className="h-full"
                        />
                      ) : (
                        <iframe
                          ref={previewIframeRef}
                          srcDoc={previewContent}
                          className="w-full h-full border-0"
                          title="Preview"
                          sandbox="allow-scripts allow-same-origin"
                        />
                      )}

                      {/* Select & Edit Overlay */}
                      {isSelectAndEditActive && (
                        <div className="absolute bottom-4 left-4 right-4 z-10">
                          <SelectAndEdit
                            iframeRef={previewIframeRef}
                            onEditRequest={handleSelectAndEditRequest}
                            isLoading={isGenerating}
                          />
                        </div>
                      )}
                    </div>
                  </div>
                </ResizablePanel>
              )}
            </ResizablePanelGroup>
          </div>

          {/* Chat Panel */}
          {showChat && (
            <div className="w-96 border-l flex flex-col bg-background">
              {/* Chat Header */}
              <div className="h-14 px-4 flex items-center justify-between border-b">
                <div className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-violet-500" />
                  <span className="font-semibold">AI Assistant</span>
                </div>

                <div className="flex items-center gap-2">
                  <Select value={selectedModel} onValueChange={setSelectedModel}>
                    <SelectTrigger className="w-40 h-8 text-xs">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {availableModels.slice(0, 20).map(model => (
                        <SelectItem key={model.id} value={model.id} className="text-xs">
                          {model.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {/* Mode Toggles */}
              <div className="px-4 py-3 border-b space-y-3">
                <div className="flex items-center justify-between">
                  <Label htmlFor="agentic" className="text-sm flex items-center gap-2">
                    <Bot className="h-4 w-4" />
                    Agentic Mode
                  </Label>
                  <Switch
                    id="agentic"
                    checked={useAgenticMode}
                    onCheckedChange={setUseAgenticMode}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <Label htmlFor="fullstack" className="text-sm flex items-center gap-2">
                    <Zap className="h-4 w-4" />
                    Full-Stack Mode
                  </Label>
                  <Switch
                    id="fullstack"
                    checked={useFullstackMode}
                    onCheckedChange={setUseFullstackMode}
                  />
                </div>
              </div>

              {/* Messages */}
              <ScrollArea className="flex-1">
                <div className="p-4 space-y-4">
                  {chatMessages.length === 0 && (
                    <div className="text-center py-8 text-muted-foreground">
                      <Wand2 className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p className="text-sm">
                        Describe what you want to build and let AI generate the code
                      </p>
                    </div>
                  )}

                  {chatMessages.map((msg, i) => (
                    <ChatMessage key={i} role={msg.role} content={msg.content} />
                  ))}

                  {isGenerating && (
                    <div className="flex items-center gap-3 p-4 rounded-lg bg-muted/50">
                      <Loader2 className="h-5 w-5 animate-spin text-violet-500" />
                      <span className="text-sm text-muted-foreground">
                        Generating code...
                      </span>
                    </div>
                  )}

                  <div ref={chatEndRef} />
                </div>
              </ScrollArea>

              {/* Input */}
              <div className="p-4 border-t">
                <div className="flex gap-2">
                  <Textarea
                    placeholder="Describe what you want to build..."
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleSendMessage();
                      }
                    }}
                    className="min-h-[80px] resize-none"
                  />
                </div>
                <div className="flex justify-between items-center mt-3">
                  <p className="text-xs text-muted-foreground">
                    Press Enter to send, Shift+Enter for new line
                  </p>
                  <Button
                    onClick={handleSendMessage}
                    disabled={!inputMessage.trim() || isGenerating}
                    className="gap-2"
                  >
                    {isGenerating ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Send className="h-4 w-4" />
                    )}
                    Generate
                  </Button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Toggle Buttons */}
        <Button
          variant="outline"
          size="icon"
          className="fixed left-2 bottom-2 z-50 h-8 w-8 rounded-full shadow-lg"
          onClick={() => setShowSidebar(!showSidebar)}
        >
          {showSidebar ? <PanelLeftClose className="h-4 w-4" /> : <PanelLeftOpen className="h-4 w-4" />}
        </Button>

        <Button
          variant="outline"
          size="icon"
          className="fixed right-2 bottom-2 z-50 h-8 w-8 rounded-full shadow-lg"
          onClick={() => setShowChat(!showChat)}
        >
          <MessageSquare className="h-4 w-4" />
        </Button>

        {/* Command Palette */}
        <CommandDialog open={showCommandPalette} onOpenChange={setShowCommandPalette}>
          <CommandInput placeholder="Type a command or search..." />
          <CommandList>
            <CommandEmpty>No results found.</CommandEmpty>
            <CommandGroup heading="Actions">
              <CommandItem onSelect={() => { handleSave(); setShowCommandPalette(false); }}>
                <Save className="mr-2 h-4 w-4" />
                Save Project
                <CommandShortcut>⌘S</CommandShortcut>
              </CommandItem>
              <CommandItem onSelect={() => { handleDownload(); setShowCommandPalette(false); }}>
                <Download className="mr-2 h-4 w-4" />
                Download ZIP
              </CommandItem>
              <CommandItem onSelect={() => { setActiveView('preview'); setShowCommandPalette(false); }}>
                <Eye className="mr-2 h-4 w-4" />
                Open Preview
                <CommandShortcut>⇧⌘P</CommandShortcut>
              </CommandItem>
            </CommandGroup>
            <CommandSeparator />
            <CommandGroup heading="Files">
              {project.files.map(file => (
                <CommandItem
                  key={file.name}
                  onSelect={() => { setCurrentFilePath(file.name); setShowCommandPalette(false); }}
                >
                  <FileCode className="mr-2 h-4 w-4" />
                  {file.name}
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </CommandDialog>
      </div>
    </TooltipProvider>
  );
}

export default EditorPageV2;
