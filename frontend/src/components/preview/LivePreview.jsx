/**
 * DEVORA LIVE PREVIEW - Ultimate Preview Experience
 *
 * Preview en temps réel avec Sandpack pour React/TypeScript
 * Support multi-devices, hot reload, et terminal intégré
 *
 * @version 5.0.0
 */

import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import {
  SandpackProvider,
  SandpackLayout,
  SandpackPreview,
  SandpackConsole,
  useSandpack,
  useActiveCode
} from '@codesandbox/sandpack-react';
import {
  Monitor, Tablet, Smartphone, RefreshCw, Maximize2, Minimize2,
  Terminal, Play, Loader2, CheckCircle, XCircle, AlertTriangle,
  Eye, EyeOff, ExternalLink, Copy, Check, Zap, Code2
} from 'lucide-react';
import { Button } from '../ui/button';
import { cn } from '../../lib/utils';
import { toast } from 'sonner';

const DEVICE_PRESETS = {
  desktop: { width: '100%', height: '100%', label: 'Desktop', icon: Monitor, maxWidth: '100%' },
  tablet: { width: '768px', height: '1024px', label: 'Tablet', icon: Tablet, maxWidth: '768px' },
  mobile: { width: '375px', height: '667px', label: 'Mobile', icon: Smartphone, maxWidth: '375px' }
};

const DEVORA_THEME = {
  colors: {
    surface1: '#0a0a0b',
    surface2: '#111113',
    surface3: '#1a1a1c',
    clickable: '#6B7280',
    base: '#9CA3AF',
    disabled: '#4B5563',
    hover: '#F3F4F6',
    accent: '#10b981',
    error: '#ef4444',
    errorSurface: '#7f1d1d'
  },
  syntax: {
    plain: '#F8F8F2',
    comment: { color: '#6272A4', fontStyle: 'italic' },
    keyword: '#FF79C6',
    tag: '#F1FA8C',
    punctuation: '#F8F8F2',
    definition: '#50FA7B',
    property: '#66D9EF',
    static: '#BD93F9',
    string: '#F1FA8C'
  },
  font: {
    body: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
    mono: '"JetBrains Mono", "Fira Code", "Fira Mono", Menlo, Consolas, monospace',
    size: '14px',
    lineHeight: '1.6'
  }
};

const convertFilesToSandpack = (files = []) => {
  const sandpackFiles = {};
  files.forEach(file => {
    let path = file.name;
    if (!path.startsWith('/')) path = '/' + path;
    sandpackFiles[path] = { code: file.content || '', active: false };
  });
  return sandpackFiles;
};

const detectProjectType = (files = []) => {
  const fileNames = files.map(f => f.name.toLowerCase());
  if (fileNames.some(f => f.endsWith('.tsx') || f.endsWith('.ts'))) {
    if (fileNames.includes('package.json')) {
      const pkgFile = files.find(f => f.name.toLowerCase() === 'package.json');
      if (pkgFile?.content?.includes('next')) return 'nextjs';
      if (pkgFile?.content?.includes('vite')) return 'vite-react-ts';
    }
    return 'react-ts';
  }
  if (fileNames.some(f => f.endsWith('.jsx'))) return 'react';
  if (fileNames.some(f => f.endsWith('.vue'))) return 'vue';
  if (fileNames.some(f => f.endsWith('.svelte'))) return 'svelte';
  return 'vanilla';
};

const getTemplateDependencies = (projectType) => {
  const base = {
    'vanilla': {},
    'react': { 'react': '^18.2.0', 'react-dom': '^18.2.0' },
    'react-ts': { 'react': '^18.2.0', 'react-dom': '^18.2.0', '@types/react': '^18.2.0', '@types/react-dom': '^18.2.0' },
    'vite-react-ts': { 'react': '^18.2.0', 'react-dom': '^18.2.0', '@types/react': '^18.2.0', '@types/react-dom': '^18.2.0' },
    'nextjs': { 'next': '^14.0.0', 'react': '^18.2.0', 'react-dom': '^18.2.0' },
    'vue': { 'vue': '^3.3.0' },
    'svelte': { 'svelte': '^4.0.0' }
  };
  return base[projectType] || {};
};

const PreviewStatus = ({ status }) => {
  const statusConfig = {
    idle: { icon: Eye, color: 'text-gray-400', label: 'Prêt' },
    loading: { icon: Loader2, color: 'text-blue-400', label: 'Chargement...', animate: true },
    running: { icon: CheckCircle, color: 'text-emerald-400', label: 'En cours' },
    error: { icon: XCircle, color: 'text-red-400', label: 'Erreur' },
    warning: { icon: AlertTriangle, color: 'text-yellow-400', label: 'Avertissement' }
  };
  const config = statusConfig[status] || statusConfig.idle;
  const Icon = config.icon;
  return (
    <div className={cn('flex items-center gap-2', config.color)}>
      <Icon className={cn('w-4 h-4', config.animate && 'animate-spin')} />
      <span className="text-sm font-medium">{config.label}</span>
    </div>
  );
};

const PreviewControls = ({ device, setDevice, showConsole, setShowConsole, isFullscreen, setIsFullscreen, onRefresh, onOpenExternal }) => {
  return (
    <div className="flex items-center gap-2">
      <div className="flex items-center gap-1 bg-white/5 rounded-lg p-1">
        {Object.entries(DEVICE_PRESETS).map(([key, { icon: Icon, label }]) => (
          <Button
            key={key}
            variant={device === key ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setDevice(key)}
            className={cn('px-2', device === key ? 'bg-emerald-600 text-white' : 'text-gray-400 hover:text-white')}
            title={label}
          >
            <Icon className="w-4 h-4" />
          </Button>
        ))}
      </div>
      <Button variant="ghost" size="sm" onClick={() => setShowConsole(!showConsole)} className={cn('text-gray-400 hover:text-white', showConsole && 'bg-white/10')} title="Toggle Console">
        <Terminal className="w-4 h-4" />
      </Button>
      <Button variant="ghost" size="sm" onClick={onRefresh} className="text-gray-400 hover:text-white" title="Rafraîchir">
        <RefreshCw className="w-4 h-4" />
      </Button>
      <Button variant="ghost" size="sm" onClick={() => setIsFullscreen(!isFullscreen)} className="text-gray-400 hover:text-white" title={isFullscreen ? 'Quitter plein écran' : 'Plein écran'}>
        {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
      </Button>
      <Button variant="ghost" size="sm" onClick={onOpenExternal} className="text-gray-400 hover:text-white" title="Ouvrir dans un nouvel onglet">
        <ExternalLink className="w-4 h-4" />
      </Button>
    </div>
  );
};

const SandpackPreviewWrapper = ({ device, showConsole }) => {
  const { sandpack } = useSandpack();
  const [previewUrl, setPreviewUrl] = useState(null);

  useEffect(() => {
    const listener = sandpack.listen((msg) => {
      if (msg.type === 'urlchange') setPreviewUrl(msg.url);
    });
    return () => listener();
  }, [sandpack]);

  const deviceConfig = DEVICE_PRESETS[device];

  return (
    <div className="flex-1 flex overflow-hidden">
      <div className="flex-1 flex items-center justify-center bg-gray-950 p-4">
        <div className="bg-white rounded-lg shadow-2xl overflow-hidden transition-all duration-300" style={{ width: deviceConfig.width, height: deviceConfig.height, maxWidth: deviceConfig.maxWidth, maxHeight: '100%' }}>
          <SandpackPreview showNavigator={false} showRefreshButton={false} showOpenInCodeSandbox={false} style={{ height: '100%', width: '100%' }} />
        </div>
      </div>
      {showConsole && (
        <div className="w-80 bg-gray-900 border-l border-gray-700 flex flex-col">
          <div className="px-3 py-2 bg-gray-800 border-b border-gray-700 flex items-center justify-between">
            <span className="text-sm text-gray-300 flex items-center gap-2"><Terminal className="w-4 h-4" />Console</span>
          </div>
          <div className="flex-1 overflow-hidden">
            <SandpackConsole style={{ height: '100%' }} showHeader={false} />
          </div>
        </div>
      )}
    </div>
  );
};

const LivePreview = ({ files = [], className = '', onFileChange, activeFile }) => {
  const [device, setDevice] = useState('desktop');
  const [showConsole, setShowConsole] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [status, setStatus] = useState('idle');
  const [refreshKey, setRefreshKey] = useState(0);
  const containerRef = useRef(null);

  const sandpackFiles = useMemo(() => convertFilesToSandpack(files), [files]);
  const projectType = useMemo(() => detectProjectType(files), [files]);
  const template = projectType === 'vanilla' ? 'vanilla' : 'react-ts';
  const customSetup = useMemo(() => ({
    dependencies: { ...getTemplateDependencies(projectType), 'lucide-react': '^0.300.0', 'clsx': '^2.0.0', 'tailwind-merge': '^2.0.0' }
  }), [projectType]);

  const handleRefresh = useCallback(() => { setRefreshKey(prev => prev + 1); toast.success('Preview rafraîchi'); }, []);
  const handleOpenExternal = useCallback(() => {
    const iframe = containerRef.current?.querySelector('iframe');
    if (iframe?.src) window.open(iframe.src, '_blank');
    else toast.error('Impossible d\'ouvrir le preview externe');
  }, []);

  useEffect(() => {
    const handleEsc = (e) => { if (e.key === 'Escape' && isFullscreen) setIsFullscreen(false); };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [isFullscreen]);

  if (!files || files.length === 0) {
    return (
      <div className={cn('flex flex-col h-full bg-gray-900', className)}>
        <div className="flex items-center justify-between px-4 py-2 bg-gray-800 border-b border-gray-700"><PreviewStatus status="idle" /></div>
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center text-gray-500">
            <Code2 className="w-12 h-12 mx-auto mb-4 opacity-30" />
            <p>Aucun fichier à prévisualiser</p>
            <p className="text-sm mt-2">Générez du code pour voir l'aperçu</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div ref={containerRef} className={cn('flex flex-col h-full bg-gray-900', isFullscreen && 'fixed inset-0 z-50', className)}>
      <div className="flex items-center justify-between px-4 py-2 bg-gray-800 border-b border-gray-700">
        <div className="flex items-center gap-3">
          <PreviewStatus status={status} />
          <span className="text-xs bg-emerald-500/20 text-emerald-400 px-2 py-1 rounded">{projectType.toUpperCase()}</span>
        </div>
        <PreviewControls device={device} setDevice={setDevice} showConsole={showConsole} setShowConsole={setShowConsole} isFullscreen={isFullscreen} setIsFullscreen={setIsFullscreen} onRefresh={handleRefresh} onOpenExternal={handleOpenExternal} />
      </div>
      <div className="flex-1 overflow-hidden">
        <SandpackProvider key={refreshKey} template={template} files={sandpackFiles} customSetup={customSetup} theme={DEVORA_THEME} options={{ autorun: true, autoReload: true, recompileMode: 'delayed', recompileDelay: 500, bundlerURL: 'https://sandpack-bundler.codesandbox.io' }}>
          <SandpackPreviewWrapper device={device} showConsole={showConsole} />
        </SandpackProvider>
      </div>
    </div>
  );
};

export const SimplePreview = ({ files = [], className = '' }) => {
  const [device, setDevice] = useState('desktop');
  const iframeRef = useRef(null);

  useEffect(() => {
    if (!iframeRef.current || !files.length) return;
    const htmlFile = files.find(f => f.name.endsWith('.html'));
    const cssFile = files.find(f => f.name.endsWith('.css'));
    const jsFile = files.find(f => f.name.endsWith('.js') && !f.name.includes('config'));
    let html = htmlFile?.content || '<!DOCTYPE html><html><head></head><body><h1>No HTML file</h1></body></html>';
    if (cssFile && html.includes('</head>')) html = html.replace('</head>', `<style>${cssFile.content}</style></head>`);
    if (jsFile && html.includes('</body>')) html = html.replace('</body>', `<script>${jsFile.content}<\/script></body>`);
    iframeRef.current.srcdoc = html;
  }, [files]);

  const deviceConfig = DEVICE_PRESETS[device];

  return (
    <div className={cn('flex flex-col h-full bg-gray-900', className)}>
      <div className="flex items-center justify-between px-4 py-2 bg-gray-800 border-b border-gray-700">
        <div className="flex items-center gap-2 text-emerald-400"><Eye className="w-4 h-4" /><span className="text-sm font-medium">Preview</span></div>
        <div className="flex items-center gap-1 bg-white/5 rounded-lg p-1">
          {Object.entries(DEVICE_PRESETS).map(([key, { icon: Icon, label }]) => (
            <Button key={key} variant={device === key ? 'default' : 'ghost'} size="sm" onClick={() => setDevice(key)} className={cn('px-2', device === key ? 'bg-emerald-600' : '')} title={label}>
              <Icon className="w-4 h-4" />
            </Button>
          ))}
        </div>
      </div>
      <div className="flex-1 flex items-center justify-center bg-gray-950 p-4">
        <div className="bg-white rounded-lg shadow-2xl overflow-hidden" style={{ width: deviceConfig.width, height: deviceConfig.height, maxWidth: '100%', maxHeight: '100%' }}>
          <iframe ref={iframeRef} className="w-full h-full border-0" title="Preview" sandbox="allow-scripts allow-forms allow-modals allow-same-origin allow-popups" />
        </div>
      </div>
    </div>
  );
};

export default LivePreview;
