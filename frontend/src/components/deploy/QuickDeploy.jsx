/**
 * DEVORA QUICK DEPLOY - Ultimate 1-Click Deploy Experience
 * @version 5.0.0
 */

import React, { useState, useCallback, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Rocket, Cloud, Globe, CheckCircle, Loader2, ExternalLink, Copy, Sparkles, Zap, AlertCircle, RefreshCw, Settings, ChevronRight, Clock, Shield, Check, X } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { cn } from '../../lib/utils';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:4521';

const DEPLOY_PROVIDERS = [
  { id: 'vercel', name: 'Vercel', icon: '▲', color: 'bg-black', gradient: 'from-gray-900 to-black', description: 'Deploy en ~30 secondes', features: ['Edge Network', 'SSL automatique', 'CDN mondial'], recommended: true },
  { id: 'netlify', name: 'Netlify', icon: '◆', color: 'bg-teal-500', gradient: 'from-teal-500 to-emerald-600', description: 'Gratuit et rapide', features: ['Formulaires', 'Functions', 'Identity'] },
  { id: 'railway', name: 'Railway', icon: '🚂', color: 'bg-purple-600', gradient: 'from-purple-600 to-violet-700', description: 'Backend inclus', features: ['Databases', 'Cron jobs', 'Scaling auto'], comingSoon: true }
];

const DEPLOY_STEPS = [
  { id: 'prepare', label: 'Préparation', progress: 10 },
  { id: 'upload', label: 'Upload', progress: 30 },
  { id: 'build', label: 'Build', progress: 60 },
  { id: 'deploy', label: 'Déploiement', progress: 85 },
  { id: 'ready', label: 'En ligne!', progress: 100 }
];

const DeployStatus = ({ status, progress, message, logs = [] }) => {
  const getStatusIcon = () => {
    switch (status) {
      case 'idle': return <Rocket className="w-5 h-5" />;
      case 'deploying': return <Loader2 className="w-5 h-5 animate-spin" />;
      case 'success': return <CheckCircle className="w-5 h-5" />;
      case 'error': return <AlertCircle className="w-5 h-5" />;
      default: return <Rocket className="w-5 h-5" />;
    }
  };
  const getStatusColor = () => {
    switch (status) {
      case 'idle': return 'text-gray-400';
      case 'deploying': return 'text-blue-400';
      case 'success': return 'text-emerald-400';
      case 'error': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };
  return (
    <div className="space-y-4">
      <div className={cn('flex items-center gap-3', getStatusColor())}>{getStatusIcon()}<span className="font-medium">{message || 'Prêt à déployer'}</span></div>
      {status === 'deploying' && (
        <div className="space-y-2">
          <div className="h-2 bg-white/10 rounded-full overflow-hidden">
            <motion.div className="h-full bg-gradient-to-r from-blue-500 to-emerald-500" initial={{ width: 0 }} animate={{ width: `${progress}%` }} transition={{ duration: 0.5 }} />
          </div>
          <div className="flex justify-between text-xs text-gray-500"><span>Progression</span><span>{progress}%</span></div>
        </div>
      )}
      {status === 'deploying' && (
        <div className="flex items-center justify-between mt-4">
          {DEPLOY_STEPS.map((step, idx) => {
            const isActive = progress >= step.progress - 10 && progress < step.progress + 10;
            const isComplete = progress > step.progress;
            return (
              <React.Fragment key={step.id}>
                <div className="flex flex-col items-center">
                  <div className={cn('w-8 h-8 rounded-full flex items-center justify-center text-sm transition-all', isComplete ? 'bg-emerald-500 text-white' : isActive ? 'bg-blue-500 text-white animate-pulse' : 'bg-white/10 text-gray-500')}>
                    {isComplete ? <Check className="w-4 h-4" /> : idx + 1}
                  </div>
                  <span className={cn('text-xs mt-1', isActive ? 'text-white' : 'text-gray-500')}>{step.label}</span>
                </div>
                {idx < DEPLOY_STEPS.length - 1 && <div className={cn('flex-1 h-0.5 mx-2', isComplete ? 'bg-emerald-500' : 'bg-white/10')} />}
              </React.Fragment>
            );
          })}
        </div>
      )}
    </div>
  );
};

const DeployedUrl = ({ url, onRedeploy }) => {
  const [copied, setCopied] = useState(false);
  const copyUrl = async () => {
    try { await navigator.clipboard.writeText(url); setCopied(true); toast.success('URL copiée!'); setTimeout(() => setCopied(false), 2000); }
    catch (error) { toast.error('Erreur lors de la copie'); }
  };
  return (
    <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="space-y-4">
      <div className="flex items-center gap-3 p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-xl">
        <CheckCircle className="w-6 h-6 text-emerald-500" />
        <div className="flex-1"><div className="font-medium text-emerald-400">Déploiement réussi!</div><div className="text-sm text-gray-400">Votre application est en ligne</div></div>
        <Sparkles className="w-5 h-5 text-yellow-500" />
      </div>
      <div className="flex items-center gap-2 p-3 bg-gray-800/50 rounded-lg border border-white/10">
        <Globe className="w-5 h-5 text-blue-400" />
        <span className="flex-1 font-mono text-sm truncate text-white">{url}</span>
        <Button variant="ghost" size="sm" onClick={copyUrl} className="text-gray-400 hover:text-white">{copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}</Button>
        <Button variant="ghost" size="sm" onClick={() => window.open(url, '_blank')} className="text-gray-400 hover:text-white"><ExternalLink className="w-4 h-4" /></Button>
      </div>
      <div className="flex gap-3">
        <Button onClick={() => window.open(url, '_blank')} className="flex-1 bg-gradient-to-r from-emerald-500 to-blue-500 hover:from-emerald-600 hover:to-blue-600"><ExternalLink className="w-4 h-4 mr-2" />Voir le site</Button>
        <Button variant="outline" onClick={onRedeploy} className="border-white/10 text-gray-300 hover:bg-white/5"><RefreshCw className="w-4 h-4 mr-2" />Redéployer</Button>
      </div>
    </motion.div>
  );
};

const QuickDeploy = ({ files = [], projectName = 'mon-app', projectId, onDeployed, className = '' }) => {
  const [status, setStatus] = useState('idle');
  const [provider, setProvider] = useState('vercel');
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState('');
  const [logs, setLogs] = useState([]);
  const [deployedUrl, setDeployedUrl] = useState(null);
  const [showSettings, setShowSettings] = useState(false);
  const [customProjectName, setCustomProjectName] = useState(projectName);

  useEffect(() => { if (status === 'success') { setStatus('idle'); setDeployedUrl(null); } }, [files]);

  const addLog = useCallback((log) => { setLogs(prev => [...prev.slice(-20), `[${new Date().toLocaleTimeString()}] ${log}`]); }, []);

  const deploy = async () => {
    if (!files || files.length === 0) { toast.error('Aucun fichier à déployer'); return; }
    const settingsResponse = await axios.get(`${BACKEND_URL}/api/settings`);
    const token = provider === 'vercel' ? settingsResponse.data.vercel_token : settingsResponse.data.netlify_token;
    if (!token) { toast.error(`Token ${provider} non configuré. Allez dans Paramètres.`); return; }
    setStatus('deploying'); setProgress(0); setLogs([]); addLog(`Démarrage du déploiement sur ${provider}...`);
    try {
      const progressInterval = setInterval(() => { setProgress(prev => Math.min(prev + 5, 85)); }, 1000);
      setMessage('Préparation des fichiers...'); setProgress(10); addLog('Préparation des fichiers...');
      const response = await axios.post(`${BACKEND_URL}/api/deploy/quick`, { project_id: projectId, project_name: customProjectName || projectName, provider: provider, files: files.map(f => ({ name: f.name, content: f.content })) });
      clearInterval(progressInterval);
      if (response.data.success) {
        setProgress(100); setMessage('Déploiement terminé!'); setStatus('success'); setDeployedUrl(response.data.url);
        addLog(`✓ Déployé avec succès: ${response.data.url}`); toast.success('Déploiement réussi!');
        if (onDeployed) onDeployed(response.data.url);
      } else { throw new Error(response.data.error || 'Échec du déploiement'); }
    } catch (error) { console.error('Deploy error:', error); setStatus('error'); setMessage(error.response?.data?.detail || error.message || 'Erreur de déploiement'); addLog(`✗ Erreur: ${error.message}`); toast.error('Échec du déploiement'); }
  };

  const reset = () => { setStatus('idle'); setProgress(0); setMessage(''); setLogs([]); setDeployedUrl(null); };

  return (
    <div className={cn('bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-6', className)}>
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl"><Rocket className="w-6 h-6 text-white" /></div>
          <div><h2 className="text-xl font-bold text-white">Déploiement 1-Click</h2><p className="text-gray-400 text-sm">Publiez en production instantanément</p></div>
        </div>
        <Button variant="ghost" size="sm" onClick={() => setShowSettings(!showSettings)} className="text-gray-400 hover:text-white"><Settings className="w-4 h-4" /></Button>
      </div>
      <AnimatePresence>
        {showSettings && (
          <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }} className="mb-6 p-4 bg-white/5 rounded-lg border border-white/10">
            <div className="space-y-4"><div><label className="text-sm text-gray-400 mb-2 block">Nom du projet</label><Input value={customProjectName} onChange={(e) => setCustomProjectName(e.target.value)} placeholder="mon-super-projet" className="bg-white/5 border-white/10" /></div></div>
          </motion.div>
        )}
      </AnimatePresence>
      {status === 'idle' && !deployedUrl && (
        <>
          <div className="grid grid-cols-3 gap-3 mb-6">
            {DEPLOY_PROVIDERS.map(p => (
              <button key={p.id} onClick={() => !p.comingSoon && setProvider(p.id)} disabled={p.comingSoon} className={cn('relative p-4 rounded-xl border-2 transition-all', provider === p.id && !p.comingSoon ? 'border-blue-500 bg-blue-500/10' : p.comingSoon ? 'border-gray-700 bg-gray-800/50 opacity-50 cursor-not-allowed' : 'border-gray-700 hover:border-gray-600 bg-gray-800/50')}>
                {p.recommended && <div className="absolute -top-2 -right-2 px-2 py-0.5 bg-gradient-to-r from-emerald-500 to-blue-500 rounded-full text-xs font-bold text-white">Recommandé</div>}
                {p.comingSoon && <div className="absolute -top-2 -right-2 px-2 py-0.5 bg-gray-600 rounded-full text-xs text-white">Bientôt</div>}
                <div className={cn('w-10 h-10 rounded-lg flex items-center justify-center text-xl mb-2', `bg-gradient-to-br ${p.gradient}`)}>{p.icon}</div>
                <div className="font-medium text-white">{p.name}</div>
                <div className="text-xs text-gray-400">{p.description}</div>
              </button>
            ))}
          </div>
          <Button onClick={deploy} disabled={files.length === 0} className="w-full h-14 text-lg bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"><Zap className="w-5 h-5 mr-2" />Déployer Maintenant</Button>
        </>
      )}
      {status === 'deploying' && <DeployStatus status={status} progress={progress} message={message} logs={logs} />}
      {status === 'success' && deployedUrl && <DeployedUrl url={deployedUrl} onRedeploy={reset} />}
      {status === 'error' && (
        <div className="space-y-4">
          <div className="flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-xl">
            <AlertCircle className="w-6 h-6 text-red-500" />
            <div className="flex-1"><div className="font-medium text-red-400">Échec du déploiement</div><div className="text-sm text-gray-400">{message}</div></div>
          </div>
          <Button onClick={reset} variant="outline" className="w-full border-white/10"><RefreshCw className="w-4 h-4 mr-2" />Réessayer</Button>
        </div>
      )}
      <div className="mt-6 p-4 bg-gray-800/50 rounded-xl">
        <div className="flex items-center gap-2 text-sm text-gray-400"><Shield className="w-4 h-4 text-emerald-500" /><span>SSL gratuit • CDN mondial • Zero configuration</span></div>
      </div>
    </div>
  );
};

export default QuickDeploy;
