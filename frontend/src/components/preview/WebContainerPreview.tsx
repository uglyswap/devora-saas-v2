/**
 * WebContainerPreview - Browser-native code execution preview
 *
 * This component provides Bolt.new-like functionality using WebContainers
 * to run Node.js directly in the browser with instant preview.
 *
 * @author Devora Team
 * @version 2.0.0
 */

import React, { useEffect, useRef, useState, useCallback, useMemo } from 'react';
import { WebContainer, FileSystemTree } from '@webcontainer/api';
import {
  Play,
  RefreshCw,
  Terminal,
  Loader2,
  CheckCircle2,
  XCircle,
  Maximize2,
  Minimize2,
  ExternalLink,
  Download,
  Copy
} from 'lucide-react';
import { Button } from '../ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { ScrollArea } from '../ui/scroll-area';
import { Badge } from '../ui/badge';
import { toast } from 'sonner';
import { cn } from '../../lib/utils';

// Types
interface ProjectFile {
  name: string;
  content: string;
  language?: string;
}

interface WebContainerPreviewProps {
  files: ProjectFile[];
  className?: string;
  onPreviewReady?: (url: string) => void;
  onError?: (error: Error) => void;
  autoStart?: boolean;
  showTerminal?: boolean;
}

type PreviewStatus =
  | 'idle'
  | 'booting'
  | 'mounting'
  | 'installing'
  | 'starting'
  | 'ready'
  | 'error';

interface TerminalLine {
  id: string;
  type: 'stdout' | 'stderr' | 'system';
  content: string;
  timestamp: Date;
}

// Singleton WebContainer instance
let webcontainerInstance: WebContainer | null = null;
let webcontainerPromise: Promise<WebContainer> | null = null;

/**
 * Get or create the singleton WebContainer instance
 */
async function getWebContainer(): Promise<WebContainer> {
  if (webcontainerInstance) {
    return webcontainerInstance;
  }

  if (webcontainerPromise) {
    return webcontainerPromise;
  }

  webcontainerPromise = WebContainer.boot().then((instance) => {
    webcontainerInstance = instance;
    return instance;
  });

  return webcontainerPromise;
}

/**
 * Convert project files to WebContainer FileSystemTree format
 */
function filesToFileSystemTree(files: ProjectFile[]): FileSystemTree {
  const tree: FileSystemTree = {};

  for (const file of files) {
    const parts = file.name.split('/').filter(Boolean);
    let current: FileSystemTree = tree;

    for (let i = 0; i < parts.length; i++) {
      const part = parts[i];
      const isLast = i === parts.length - 1;

      if (isLast) {
        // It's a file
        current[part] = {
          file: {
            contents: file.content
          }
        };
      } else {
        // It's a directory
        if (!current[part]) {
          current[part] = {
            directory: {}
          };
        }
        const node = current[part];
        if ('directory' in node) {
          current = node.directory;
        }
      }
    }
  }

  return tree;
}

/**
 * WebContainerPreview Component
 *
 * Provides browser-native Node.js execution for instant code preview.
 * Similar to Bolt.new's WebContainers implementation.
 */
export function WebContainerPreview({
  files,
  className,
  onPreviewReady,
  onError,
  autoStart = true,
  showTerminal = true
}: WebContainerPreviewProps) {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const webcontainerRef = useRef<WebContainer | null>(null);

  const [status, setStatus] = useState<PreviewStatus>('idle');
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [terminalOutput, setTerminalOutput] = useState<TerminalLine[]>([]);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [activeTab, setActiveTab] = useState<'preview' | 'terminal'>('preview');
  const [installProgress, setInstallProgress] = useState(0);

  const terminalEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll terminal
  useEffect(() => {
    terminalEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [terminalOutput]);

  /**
   * Add line to terminal output
   */
  const addTerminalLine = useCallback((type: TerminalLine['type'], content: string) => {
    setTerminalOutput(prev => [...prev, {
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      type,
      content,
      timestamp: new Date()
    }]);
  }, []);

  /**
   * Start the WebContainer and run the project
   */
  const startPreview = useCallback(async () => {
    if (files.length === 0) {
      toast.error('No files to preview');
      return;
    }

    try {
      // Reset state
      setStatus('booting');
      setPreviewUrl(null);
      setTerminalOutput([]);
      setInstallProgress(0);

      addTerminalLine('system', '🚀 Booting WebContainer...');

      // Boot WebContainer
      const webcontainer = await getWebContainer();
      webcontainerRef.current = webcontainer;

      setStatus('mounting');
      addTerminalLine('system', '📁 Mounting project files...');

      // Convert files and mount
      const fileSystemTree = filesToFileSystemTree(files);
      await webcontainer.mount(fileSystemTree);

      addTerminalLine('system', `✓ Mounted ${files.length} files`);

      // Check if package.json exists
      const hasPackageJson = files.some(f => f.name === 'package.json');

      if (hasPackageJson) {
        setStatus('installing');
        addTerminalLine('system', '📦 Installing dependencies...');

        // Run npm install
        const installProcess = await webcontainer.spawn('npm', ['install']);

        // Stream install output
        installProcess.output.pipeTo(new WritableStream({
          write(data) {
            addTerminalLine('stdout', data);
            // Estimate progress based on output
            setInstallProgress(prev => Math.min(prev + 5, 90));
          }
        }));

        const installExitCode = await installProcess.exit;
        setInstallProgress(100);

        if (installExitCode !== 0) {
          throw new Error(`npm install failed with exit code ${installExitCode}`);
        }

        addTerminalLine('system', '✓ Dependencies installed');

        // Start dev server
        setStatus('starting');
        addTerminalLine('system', '🌐 Starting development server...');

        // Listen for server-ready event
        webcontainer.on('server-ready', (port, url) => {
          setPreviewUrl(url);
          setStatus('ready');
          addTerminalLine('system', `✓ Server ready at ${url}`);
          onPreviewReady?.(url);
          toast.success('Preview ready!');
        });

        // Start the dev server
        const devProcess = await webcontainer.spawn('npm', ['run', 'dev']);

        devProcess.output.pipeTo(new WritableStream({
          write(data) {
            addTerminalLine('stdout', data);
          }
        }));

      } else {
        // No package.json - try to serve static files
        setStatus('ready');
        addTerminalLine('system', '📄 Serving static files...');

        // For static HTML files, we can use a simple approach
        const indexHtml = files.find(f =>
          f.name === 'index.html' || f.name.endsWith('/index.html')
        );

        if (indexHtml) {
          // Create a blob URL for static preview
          const blob = new Blob([indexHtml.content], { type: 'text/html' });
          const url = URL.createObjectURL(blob);
          setPreviewUrl(url);
          onPreviewReady?.(url);
          addTerminalLine('system', '✓ Static preview ready');
          toast.success('Static preview ready!');
        }
      }

    } catch (error) {
      const err = error instanceof Error ? error : new Error(String(error));
      setStatus('error');
      addTerminalLine('stderr', `❌ Error: ${err.message}`);
      onError?.(err);
      toast.error(`Preview failed: ${err.message}`);
    }
  }, [files, addTerminalLine, onPreviewReady, onError]);

  /**
   * Restart the preview
   */
  const restartPreview = useCallback(async () => {
    if (webcontainerRef.current) {
      // Teardown and restart
      await webcontainerRef.current.teardown();
      webcontainerInstance = null;
      webcontainerPromise = null;
    }
    await startPreview();
  }, [startPreview]);

  /**
   * Copy preview URL to clipboard
   */
  const copyPreviewUrl = useCallback(() => {
    if (previewUrl) {
      navigator.clipboard.writeText(previewUrl);
      toast.success('URL copied to clipboard');
    }
  }, [previewUrl]);

  /**
   * Open preview in new tab
   */
  const openInNewTab = useCallback(() => {
    if (previewUrl) {
      window.open(previewUrl, '_blank');
    }
  }, [previewUrl]);

  // Auto-start on mount if enabled
  useEffect(() => {
    if (autoStart && files.length > 0) {
      startPreview();
    }
  }, [autoStart]); // Only run on mount, not on file changes

  // Status indicator
  const StatusIndicator = useMemo(() => {
    const statusConfig = {
      idle: { icon: Play, color: 'bg-gray-500', text: 'Ready to start' },
      booting: { icon: Loader2, color: 'bg-blue-500', text: 'Booting...' },
      mounting: { icon: Loader2, color: 'bg-blue-500', text: 'Mounting files...' },
      installing: { icon: Loader2, color: 'bg-yellow-500', text: 'Installing...' },
      starting: { icon: Loader2, color: 'bg-yellow-500', text: 'Starting server...' },
      ready: { icon: CheckCircle2, color: 'bg-green-500', text: 'Ready' },
      error: { icon: XCircle, color: 'bg-red-500', text: 'Error' }
    };

    const config = statusConfig[status];
    const Icon = config.icon;
    const isLoading = ['booting', 'mounting', 'installing', 'starting'].includes(status);

    return (
      <Badge variant="outline" className={cn('gap-1.5', config.color, 'text-white')}>
        <Icon className={cn('h-3 w-3', isLoading && 'animate-spin')} />
        {config.text}
      </Badge>
    );
  }, [status]);

  return (
    <div className={cn(
      'flex flex-col border rounded-lg overflow-hidden bg-background',
      isFullscreen && 'fixed inset-0 z-50',
      className
    )}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 border-b bg-muted/50">
        <div className="flex items-center gap-3">
          {StatusIndicator}
          {status === 'installing' && (
            <div className="w-32 h-2 bg-muted rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-500 transition-all duration-300"
                style={{ width: `${installProgress}%` }}
              />
            </div>
          )}
        </div>

        <div className="flex items-center gap-2">
          {status === 'idle' || status === 'error' ? (
            <Button size="sm" onClick={startPreview}>
              <Play className="h-4 w-4 mr-1" />
              Start
            </Button>
          ) : (
            <Button size="sm" variant="outline" onClick={restartPreview}>
              <RefreshCw className="h-4 w-4 mr-1" />
              Restart
            </Button>
          )}

          {previewUrl && (
            <>
              <Button size="sm" variant="ghost" onClick={copyPreviewUrl}>
                <Copy className="h-4 w-4" />
              </Button>
              <Button size="sm" variant="ghost" onClick={openInNewTab}>
                <ExternalLink className="h-4 w-4" />
              </Button>
            </>
          )}

          <Button
            size="sm"
            variant="ghost"
            onClick={() => setIsFullscreen(!isFullscreen)}
          >
            {isFullscreen ? (
              <Minimize2 className="h-4 w-4" />
            ) : (
              <Maximize2 className="h-4 w-4" />
            )}
          </Button>
        </div>
      </div>

      {/* Content */}
      {showTerminal ? (
        <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as 'preview' | 'terminal')}>
          <TabsList className="mx-4 mt-2">
            <TabsTrigger value="preview">Preview</TabsTrigger>
            <TabsTrigger value="terminal" className="gap-1.5">
              <Terminal className="h-3.5 w-3.5" />
              Terminal
              {terminalOutput.length > 0 && (
                <Badge variant="secondary" className="ml-1 h-5 px-1.5">
                  {terminalOutput.length}
                </Badge>
              )}
            </TabsTrigger>
          </TabsList>

          <TabsContent value="preview" className="flex-1 m-0">
            <div className="relative w-full h-[500px] bg-white">
              {previewUrl ? (
                <iframe
                  ref={iframeRef}
                  src={previewUrl}
                  className="w-full h-full border-0"
                  title="Preview"
                  sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
                />
              ) : (
                <div className="flex items-center justify-center h-full text-muted-foreground">
                  {status === 'idle' ? (
                    <div className="text-center">
                      <Play className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>Click Start to run your project</p>
                    </div>
                  ) : (
                    <div className="text-center">
                      <Loader2 className="h-12 w-12 mx-auto mb-4 animate-spin opacity-50" />
                      <p>Loading preview...</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </TabsContent>

          <TabsContent value="terminal" className="flex-1 m-0">
            <ScrollArea className="h-[500px] bg-gray-900 text-gray-100 font-mono text-sm">
              <div className="p-4 space-y-1">
                {terminalOutput.map((line) => (
                  <div
                    key={line.id}
                    className={cn(
                      'whitespace-pre-wrap break-all',
                      line.type === 'stderr' && 'text-red-400',
                      line.type === 'system' && 'text-blue-400'
                    )}
                  >
                    {line.content}
                  </div>
                ))}
                <div ref={terminalEndRef} />
              </div>
            </ScrollArea>
          </TabsContent>
        </Tabs>
      ) : (
        <div className="relative w-full h-[500px] bg-white">
          {previewUrl ? (
            <iframe
              ref={iframeRef}
              src={previewUrl}
              className="w-full h-full border-0"
              title="Preview"
              sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
            />
          ) : (
            <div className="flex items-center justify-center h-full text-muted-foreground">
              <Loader2 className="h-8 w-8 animate-spin" />
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default WebContainerPreview;
