/**
 * OneClickDeploy - Universal deployment to Vercel, Netlify, and Cloudflare
 *
 * This component provides seamless one-click deployment similar to Bolt.new
 * with support for multiple hosting providers.
 *
 * @author Devora Team
 * @version 2.0.0
 */

import React, { useState, useCallback } from 'react';
import {
  Rocket,
  Cloud,
  Globe,
  ExternalLink,
  Loader2,
  CheckCircle2,
  XCircle,
  Copy,
  RefreshCw,
  Settings,
  ChevronRight,
  AlertCircle,
  Info
} from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger
} from '../ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '../ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { Separator } from '../ui/separator';
import { Switch } from '../ui/switch';
import { Alert, AlertDescription } from '../ui/alert';
import { toast } from 'sonner';
import { cn } from '../../lib/utils';

// Types
interface ProjectFile {
  name: string;
  content: string;
  language?: string;
}

interface DeploymentConfig {
  projectName: string;
  framework: 'nextjs' | 'react' | 'vite' | 'static';
  buildCommand?: string;
  outputDirectory?: string;
  nodeVersion?: string;
  envVars?: Record<string, string>;
}

interface DeploymentResult {
  success: boolean;
  url?: string;
  deploymentId?: string;
  error?: string;
  logs?: string[];
}

type DeploymentProvider = 'vercel' | 'netlify' | 'cloudflare';

type DeploymentStatus =
  | 'idle'
  | 'preparing'
  | 'uploading'
  | 'building'
  | 'deploying'
  | 'ready'
  | 'error';

interface OneClickDeployProps {
  files: ProjectFile[];
  projectName?: string;
  onDeploySuccess?: (result: DeploymentResult) => void;
  onDeployError?: (error: Error) => void;
  className?: string;
}

// Provider configurations
const PROVIDERS: Record<DeploymentProvider, {
  name: string;
  icon: React.ReactNode;
  color: string;
  description: string;
  docsUrl: string;
}> = {
  vercel: {
    name: 'Vercel',
    icon: <span className="font-bold">▲</span>,
    color: 'bg-black text-white',
    description: 'Best for Next.js apps with Edge Functions',
    docsUrl: 'https://vercel.com/docs'
  },
  netlify: {
    name: 'Netlify',
    icon: <span className="text-[#00c7b7] font-bold">◆</span>,
    color: 'bg-[#00c7b7] text-white',
    description: 'Great for static sites and serverless',
    docsUrl: 'https://docs.netlify.com'
  },
  cloudflare: {
    name: 'Cloudflare Pages',
    icon: <Cloud className="h-4 w-4" />,
    color: 'bg-[#f38020] text-white',
    description: 'Global CDN with Workers integration',
    docsUrl: 'https://developers.cloudflare.com/pages'
  }
};

// Framework detection
function detectFramework(files: ProjectFile[]): DeploymentConfig['framework'] {
  const packageJson = files.find(f => f.name === 'package.json');

  if (packageJson) {
    try {
      const pkg = JSON.parse(packageJson.content);
      const deps = { ...pkg.dependencies, ...pkg.devDependencies };

      if (deps['next']) return 'nextjs';
      if (deps['vite']) return 'vite';
      if (deps['react']) return 'react';
    } catch (e) {
      // Ignore parse errors
    }
  }

  // Check for index.html
  if (files.some(f => f.name === 'index.html')) {
    return 'static';
  }

  return 'react';
}

// Get default build config based on framework
function getDefaultConfig(framework: DeploymentConfig['framework']): Partial<DeploymentConfig> {
  switch (framework) {
    case 'nextjs':
      return {
        buildCommand: 'npm run build',
        outputDirectory: '.next',
        nodeVersion: '18.x'
      };
    case 'vite':
      return {
        buildCommand: 'npm run build',
        outputDirectory: 'dist',
        nodeVersion: '18.x'
      };
    case 'react':
      return {
        buildCommand: 'npm run build',
        outputDirectory: 'build',
        nodeVersion: '18.x'
      };
    case 'static':
      return {
        buildCommand: '',
        outputDirectory: '.',
        nodeVersion: '18.x'
      };
  }
}

/**
 * OneClickDeploy Component
 *
 * Provides universal one-click deployment to multiple providers.
 */
export function OneClickDeploy({
  files,
  projectName = 'my-project',
  onDeploySuccess,
  onDeployError,
  className
}: OneClickDeployProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [provider, setProvider] = useState<DeploymentProvider>('vercel');
  const [status, setStatus] = useState<DeploymentStatus>('idle');
  const [progress, setProgress] = useState(0);
  const [deploymentUrl, setDeploymentUrl] = useState<string | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [showAdvanced, setShowAdvanced] = useState(false);

  // Config state
  const detectedFramework = detectFramework(files);
  const defaultConfig = getDefaultConfig(detectedFramework);

  const [config, setConfig] = useState<DeploymentConfig>({
    projectName: projectName.toLowerCase().replace(/[^a-z0-9-]/g, '-'),
    framework: detectedFramework,
    ...defaultConfig
  });

  // Token state (stored in localStorage)
  const [tokens, setTokens] = useState<Record<DeploymentProvider, string>>(() => {
    try {
      return JSON.parse(localStorage.getItem('devora_deploy_tokens') || '{}');
    } catch {
      return {};
    }
  });

  const addLog = useCallback((message: string) => {
    setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${message}`]);
  }, []);

  /**
   * Save token to localStorage
   */
  const saveToken = (provider: DeploymentProvider, token: string) => {
    const newTokens = { ...tokens, [provider]: token };
    setTokens(newTokens);
    localStorage.setItem('devora_deploy_tokens', JSON.stringify(newTokens));
  };

  /**
   * Deploy to Vercel
   */
  const deployToVercel = async (): Promise<DeploymentResult> => {
    const token = tokens.vercel;
    if (!token) {
      throw new Error('Vercel token not configured');
    }

    addLog('Preparing deployment for Vercel...');
    setStatus('preparing');
    setProgress(10);

    // Create deployment files payload
    const deployFiles: Record<string, string> = {};
    files.forEach(file => {
      deployFiles[file.name] = file.content;
    });

    addLog(`Uploading ${files.length} files...`);
    setStatus('uploading');
    setProgress(30);

    // Create deployment via API
    const response = await fetch('/api/vercel/deploy', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        name: config.projectName,
        files: deployFiles,
        projectSettings: {
          framework: config.framework === 'nextjs' ? 'nextjs' : null,
          buildCommand: config.buildCommand,
          outputDirectory: config.outputDirectory,
          nodeVersion: config.nodeVersion
        }
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Vercel deployment failed');
    }

    setStatus('building');
    setProgress(60);
    addLog('Building project...');

    const result = await response.json();

    // Poll for deployment status
    let attempts = 0;
    while (attempts < 60) {
      const statusRes = await fetch(`/api/vercel/deployment/${result.id}/status`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (statusRes.ok) {
        const statusData = await statusRes.json();

        if (statusData.readyState === 'READY') {
          setStatus('ready');
          setProgress(100);
          addLog(`Deployment ready: ${statusData.url}`);
          return {
            success: true,
            url: statusData.url,
            deploymentId: result.id
          };
        }

        if (statusData.readyState === 'ERROR') {
          throw new Error('Build failed');
        }
      }

      setProgress(60 + Math.min(attempts, 30));
      addLog(`Building... (${statusData?.readyState || 'QUEUED'})`);
      await new Promise(r => setTimeout(r, 2000));
      attempts++;
    }

    throw new Error('Deployment timed out');
  };

  /**
   * Deploy to Netlify
   */
  const deployToNetlify = async (): Promise<DeploymentResult> => {
    const token = tokens.netlify;
    if (!token) {
      throw new Error('Netlify token not configured');
    }

    addLog('Preparing deployment for Netlify...');
    setStatus('preparing');
    setProgress(10);

    // Create deployment files
    const deployFiles: Record<string, string> = {};
    files.forEach(file => {
      deployFiles[file.name] = file.content;
    });

    addLog(`Uploading ${files.length} files...`);
    setStatus('uploading');
    setProgress(30);

    const response = await fetch('/api/netlify/deploy', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        name: config.projectName,
        files: deployFiles,
        buildSettings: {
          cmd: config.buildCommand,
          dir: config.outputDirectory
        }
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Netlify deployment failed');
    }

    setStatus('deploying');
    setProgress(70);
    addLog('Processing deployment...');

    const result = await response.json();

    setStatus('ready');
    setProgress(100);
    addLog(`Deployment ready: ${result.ssl_url || result.url}`);

    return {
      success: true,
      url: result.ssl_url || result.url,
      deploymentId: result.id
    };
  };

  /**
   * Deploy to Cloudflare Pages
   */
  const deployToCloudflare = async (): Promise<DeploymentResult> => {
    const token = tokens.cloudflare;
    if (!token) {
      throw new Error('Cloudflare token not configured');
    }

    addLog('Preparing deployment for Cloudflare Pages...');
    setStatus('preparing');
    setProgress(10);

    // Create deployment files
    const deployFiles: Record<string, string> = {};
    files.forEach(file => {
      deployFiles[file.name] = file.content;
    });

    addLog(`Uploading ${files.length} files...`);
    setStatus('uploading');
    setProgress(30);

    const response = await fetch('/api/cloudflare/deploy', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        projectName: config.projectName,
        files: deployFiles,
        buildConfig: {
          buildCommand: config.buildCommand,
          destinationDir: config.outputDirectory
        }
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Cloudflare deployment failed');
    }

    setStatus('building');
    setProgress(60);
    addLog('Building project...');

    const result = await response.json();

    setStatus('ready');
    setProgress(100);
    addLog(`Deployment ready: ${result.url}`);

    return {
      success: true,
      url: result.url,
      deploymentId: result.id
    };
  };

  /**
   * Handle deployment
   */
  const handleDeploy = async () => {
    if (!tokens[provider]) {
      toast.error(`Please configure your ${PROVIDERS[provider].name} API token first`);
      return;
    }

    setStatus('preparing');
    setProgress(0);
    setLogs([]);
    setDeploymentUrl(null);

    try {
      addLog(`Starting deployment to ${PROVIDERS[provider].name}...`);

      let result: DeploymentResult;

      switch (provider) {
        case 'vercel':
          result = await deployToVercel();
          break;
        case 'netlify':
          result = await deployToNetlify();
          break;
        case 'cloudflare':
          result = await deployToCloudflare();
          break;
        default:
          throw new Error('Unknown provider');
      }

      if (result.success && result.url) {
        setDeploymentUrl(result.url);
        onDeploySuccess?.(result);
        toast.success('Deployment successful!', {
          action: {
            label: 'Open',
            onClick: () => window.open(result.url, '_blank')
          }
        });
      }
    } catch (error) {
      const err = error instanceof Error ? error : new Error(String(error));
      setStatus('error');
      addLog(`Error: ${err.message}`);
      onDeployError?.(err);
      toast.error(`Deployment failed: ${err.message}`);
    }
  };

  /**
   * Copy deployment URL
   */
  const copyUrl = () => {
    if (deploymentUrl) {
      navigator.clipboard.writeText(deploymentUrl);
      toast.success('URL copied to clipboard');
    }
  };

  /**
   * Status indicator component
   */
  const StatusBadge = () => {
    const statusConfig: Record<DeploymentStatus, { color: string; text: string }> = {
      idle: { color: 'bg-gray-500', text: 'Ready' },
      preparing: { color: 'bg-blue-500', text: 'Preparing...' },
      uploading: { color: 'bg-blue-500', text: 'Uploading...' },
      building: { color: 'bg-yellow-500', text: 'Building...' },
      deploying: { color: 'bg-yellow-500', text: 'Deploying...' },
      ready: { color: 'bg-green-500', text: 'Deployed!' },
      error: { color: 'bg-red-500', text: 'Error' }
    };

    const config = statusConfig[status];
    const isLoading = ['preparing', 'uploading', 'building', 'deploying'].includes(status);

    return (
      <Badge className={cn(config.color, 'text-white gap-1.5')}>
        {isLoading ? (
          <Loader2 className="h-3 w-3 animate-spin" />
        ) : status === 'ready' ? (
          <CheckCircle2 className="h-3 w-3" />
        ) : status === 'error' ? (
          <XCircle className="h-3 w-3" />
        ) : null}
        {config.text}
      </Badge>
    );
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button className={cn('gap-2', className)}>
          <Rocket className="h-4 w-4" />
          Deploy
        </Button>
      </DialogTrigger>

      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Rocket className="h-5 w-5" />
            One-Click Deploy
          </DialogTitle>
          <DialogDescription>
            Deploy your project to production in seconds
          </DialogDescription>
        </DialogHeader>

        <Tabs defaultValue="deploy" className="mt-4">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="deploy">Deploy</TabsTrigger>
            <TabsTrigger value="settings">Settings</TabsTrigger>
          </TabsList>

          <TabsContent value="deploy" className="space-y-4">
            {/* Provider Selection */}
            <div className="grid grid-cols-3 gap-3">
              {(Object.keys(PROVIDERS) as DeploymentProvider[]).map((p) => (
                <button
                  key={p}
                  onClick={() => setProvider(p)}
                  className={cn(
                    'p-4 rounded-lg border-2 transition-all text-left',
                    provider === p
                      ? 'border-primary bg-primary/5'
                      : 'border-muted hover:border-muted-foreground/50'
                  )}
                >
                  <div className="flex items-center gap-2 mb-2">
                    <div className={cn(
                      'w-8 h-8 rounded flex items-center justify-center',
                      PROVIDERS[p].color
                    )}>
                      {PROVIDERS[p].icon}
                    </div>
                    <span className="font-medium">{PROVIDERS[p].name}</span>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {PROVIDERS[p].description}
                  </p>
                  {!tokens[p] && (
                    <Badge variant="outline" className="mt-2 text-xs">
                      <AlertCircle className="h-3 w-3 mr-1" />
                      Token required
                    </Badge>
                  )}
                </button>
              ))}
            </div>

            {/* Project Config Preview */}
            <div className="p-4 rounded-lg bg-muted/50 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Project</span>
                <span className="font-mono text-sm">{config.projectName}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Framework</span>
                <Badge variant="secondary">{config.framework}</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Files</span>
                <span className="text-sm">{files.length} files</span>
              </div>
            </div>

            {/* Deployment Progress */}
            {status !== 'idle' && (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <StatusBadge />
                  <span className="text-sm text-muted-foreground">{progress}%</span>
                </div>
                <Progress value={progress} className="h-2" />

                {/* Logs */}
                <div className="max-h-32 overflow-y-auto bg-gray-900 rounded-lg p-3 font-mono text-xs text-gray-300">
                  {logs.map((log, i) => (
                    <div key={i}>{log}</div>
                  ))}
                </div>
              </div>
            )}

            {/* Deployment Result */}
            {deploymentUrl && (
              <Alert className="bg-green-500/10 border-green-500/50">
                <CheckCircle2 className="h-4 w-4 text-green-500" />
                <AlertDescription className="flex items-center justify-between">
                  <span className="font-mono text-sm">{deploymentUrl}</span>
                  <div className="flex gap-2">
                    <Button size="sm" variant="ghost" onClick={copyUrl}>
                      <Copy className="h-4 w-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => window.open(deploymentUrl, '_blank')}
                    >
                      <ExternalLink className="h-4 w-4" />
                    </Button>
                  </div>
                </AlertDescription>
              </Alert>
            )}
          </TabsContent>

          <TabsContent value="settings" className="space-y-4">
            {/* API Tokens */}
            <div className="space-y-4">
              <h3 className="font-medium">API Tokens</h3>
              <p className="text-sm text-muted-foreground">
                Configure your deployment provider tokens for one-click deploys
              </p>

              {(Object.keys(PROVIDERS) as DeploymentProvider[]).map((p) => (
                <div key={p} className="space-y-2">
                  <Label className="flex items-center gap-2">
                    <div className={cn(
                      'w-5 h-5 rounded flex items-center justify-center text-xs',
                      PROVIDERS[p].color
                    )}>
                      {PROVIDERS[p].icon}
                    </div>
                    {PROVIDERS[p].name} Token
                  </Label>
                  <div className="flex gap-2">
                    <Input
                      type="password"
                      placeholder={`Enter ${PROVIDERS[p].name} API token`}
                      value={tokens[p] || ''}
                      onChange={(e) => saveToken(p, e.target.value)}
                    />
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={() => window.open(PROVIDERS[p].docsUrl, '_blank')}
                    >
                      <Info className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>

            <Separator />

            {/* Build Settings */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-medium">Build Settings</h3>
                <Switch
                  checked={showAdvanced}
                  onCheckedChange={setShowAdvanced}
                />
              </div>

              {showAdvanced && (
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label>Project Name</Label>
                    <Input
                      value={config.projectName}
                      onChange={(e) => setConfig({ ...config, projectName: e.target.value })}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Framework</Label>
                    <Select
                      value={config.framework}
                      onValueChange={(v) => {
                        const framework = v as DeploymentConfig['framework'];
                        setConfig({
                          ...config,
                          framework,
                          ...getDefaultConfig(framework)
                        });
                      }}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="nextjs">Next.js</SelectItem>
                        <SelectItem value="react">React (CRA)</SelectItem>
                        <SelectItem value="vite">Vite</SelectItem>
                        <SelectItem value="static">Static HTML</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Build Command</Label>
                    <Input
                      value={config.buildCommand}
                      onChange={(e) => setConfig({ ...config, buildCommand: e.target.value })}
                      placeholder="npm run build"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Output Directory</Label>
                    <Input
                      value={config.outputDirectory}
                      onChange={(e) => setConfig({ ...config, outputDirectory: e.target.value })}
                      placeholder="build"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Node.js Version</Label>
                    <Select
                      value={config.nodeVersion}
                      onValueChange={(v) => setConfig({ ...config, nodeVersion: v })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="20.x">20.x (Latest LTS)</SelectItem>
                        <SelectItem value="18.x">18.x (LTS)</SelectItem>
                        <SelectItem value="16.x">16.x</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              )}
            </div>
          </TabsContent>
        </Tabs>

        <DialogFooter>
          <Button variant="outline" onClick={() => setIsOpen(false)}>
            Cancel
          </Button>
          <Button
            onClick={handleDeploy}
            disabled={!tokens[provider] || ['preparing', 'uploading', 'building', 'deploying'].includes(status)}
          >
            {['preparing', 'uploading', 'building', 'deploying'].includes(status) ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Deploying...
              </>
            ) : (
              <>
                <Rocket className="h-4 w-4 mr-2" />
                Deploy to {PROVIDERS[provider].name}
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export default OneClickDeploy;
