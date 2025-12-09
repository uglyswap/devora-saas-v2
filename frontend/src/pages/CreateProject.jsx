/**
 * DEVORA CREATE PROJECT PAGE - Ultimate Creation Experience
 * @version 5.0.0
 */

import React, { useState, useCallback, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, ArrowLeft, Code2, Rocket, Eye, Zap, Loader2, CheckCircle, XCircle, Play, Save, Download, Github, Globe, Settings, MessageSquare, FileCode, PanelLeftClose, PanelRightClose, ChevronRight } from 'lucide-react';
import { Button } from '../components/ui/button';
import { toast } from 'sonner';
import axios from 'axios';
import ProjectWizard from '../components/wizard/ProjectWizard';
import LivePreview, { SimplePreview } from '../components/preview/LivePreview';
import QuickDeploy from '../components/deploy/QuickDeploy';
import Editor from '@monaco-editor/react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:4521';

const GenerationProgress = ({ isGenerating, progress, currentStep, files }) => {
  if (!isGenerating) return null;
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm">
      <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl p-8 max-w-md w-full mx-4 border border-white/10">
        <div className="text-center mb-6">
          <motion.div animate={{ rotate: 360 }} transition={{ duration: 2, repeat: Infinity, ease: "linear" }} className="w-16 h-16 mx-auto mb-4 bg-gradient-to-r from-emerald-500 to-blue-500 rounded-full flex items-center justify-center">
            <Sparkles className="w-8 h-8 text-white" />
          </motion.div>
          <h2 className="text-2xl font-bold text-white mb-2">Génération en cours</h2>
          <p className="text-gray-400">{currentStep}</p>
        </div>
        <div className="mb-6">
          <div className="h-3 bg-white/10 rounded-full overflow-hidden">
            <motion.div className="h-full bg-gradient-to-r from-emerald-500 via-blue-500 to-purple-500" initial={{ width: 0 }} animate={{ width: `${progress}%` }} transition={{ duration: 0.5 }} />
          </div>
          <div className="flex justify-between mt-2 text-sm text-gray-500"><span>Progression</span><span>{progress}%</span></div>
        </div>
        {files.length > 0 && (
          <div className="space-y-2">
            <p className="text-sm text-gray-400 mb-2">{files.length} fichier(s) généré(s)</p>
            <div className="max-h-32 overflow-y-auto space-y-1">
              {files.map((file, idx) => (
                <motion.div key={file.name} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: idx * 0.1 }} className="flex items-center gap-2 p-2 bg-white/5 rounded-lg text-sm">
                  <FileCode className="w-4 h-4 text-emerald-400" />
                  <span className="text-gray-300 truncate">{file.name}</span>
                  <CheckCircle className="w-4 h-4 text-emerald-400 ml-auto" />
                </motion.div>
              ))}
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
};

const CreateProject = () => {
  const navigate = useNavigate();
  const [mode, setMode] = useState('wizard');
  const [project, setProject] = useState({ name: 'Nouveau Projet', description: '', files: [], conversation_history: [] });
  const [currentFileIndex, setCurrentFileIndex] = useState(0);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationProgress, setGenerationProgress] = useState(0);
  const [generationStep, setGenerationStep] = useState('');
  const [showPreview, setShowPreview] = useState(true);
  const [showDeploy, setShowDeploy] = useState(false);
  const [projectId, setProjectId] = useState(null);
  const [apiKey, setApiKey] = useState('');

  useEffect(() => { loadSettings(); }, []);

  const loadSettings = async () => {
    try { const response = await axios.get(`${BACKEND_URL}/api/settings`); if (response.data.openrouter_api_key) setApiKey(response.data.openrouter_api_key); }
    catch (error) { console.error('Error loading settings:', error); }
  };

  const handleWizardComplete = useCallback(async (wizardData) => {
    if (!apiKey) { toast.error('Veuillez configurer votre clé API dans les paramètres'); navigate('/settings'); return; }
    setIsGenerating(true); setGenerationProgress(0); setGenerationStep('Initialisation...');
    try {
      const progressSteps = [
        { progress: 10, step: 'Analyse de votre demande...' },
        { progress: 25, step: 'Agent Architecte en action...' },
        { progress: 40, step: 'Planification de la structure...' },
        { progress: 55, step: 'Génération du code...' },
        { progress: 70, step: 'Agent Frontend en action...' },
        { progress: 85, step: 'Finalisation...' }
      ];
      let currentStep = 0;
      const progressInterval = setInterval(() => { if (currentStep < progressSteps.length) { setGenerationProgress(progressSteps[currentStep].progress); setGenerationStep(progressSteps[currentStep].step); currentStep++; } }, 2000);
      const response = await axios.post(`${BACKEND_URL}/api/generate/fullstack`, { message: wizardData.generatedPrompt, model: 'openai/gpt-4o', api_key: apiKey, current_files: [], conversation_history: [], project_type: wizardData.templateData?.id || 'saas' });
      clearInterval(progressInterval);
      if (response.data.success && response.data.files) {
        setGenerationProgress(100); setGenerationStep('Terminé!');
        const newProject = { name: wizardData.templateData?.name || 'Mon Projet', description: wizardData.idea, files: response.data.files, conversation_history: [{ role: 'user', content: wizardData.generatedPrompt }, { role: 'assistant', content: `Projet généré avec ${response.data.files.length} fichiers.` }] };
        setProject(newProject);
        const saveResponse = await axios.post(`${BACKEND_URL}/api/projects`, newProject);
        if (saveResponse.data.id) setProjectId(saveResponse.data.id);
        toast.success(`${response.data.files.length} fichiers générés!`);
        setTimeout(() => { setIsGenerating(false); setMode('editor'); }, 1000);
      } else { throw new Error('Aucun fichier généré'); }
    } catch (error) { console.error('Generation error:', error); setIsGenerating(false); toast.error(error.response?.data?.detail || 'Erreur lors de la génération'); }
  }, [apiKey, navigate]);

  const handleWizardCancel = useCallback(() => { navigate('/dashboard'); }, [navigate]);

  const saveProject = async () => {
    try {
      if (projectId) await axios.put(`${BACKEND_URL}/api/projects/${projectId}`, project);
      else { const response = await axios.post(`${BACKEND_URL}/api/projects`, project); setProjectId(response.data.id); }
      toast.success('Projet sauvegardé');
    } catch (error) { toast.error('Erreur lors de la sauvegarde'); }
  };

  const downloadProject = async () => {
    try {
      const JSZip = (await import('jszip')).default;
      const zip = new JSZip();
      project.files.forEach(file => { zip.file(file.name, file.content); });
      const blob = await zip.generateAsync({ type: 'blob' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a'); a.href = url; a.download = `${project.name.replace(/[^a-z0-9]/gi, '_')}.zip`;
      document.body.appendChild(a); a.click(); document.body.removeChild(a); URL.revokeObjectURL(url);
      toast.success('Projet téléchargé');
    } catch (error) { toast.error('Erreur lors du téléchargement'); }
  };

  const isReactProject = project.files.some(f => f.name.endsWith('.tsx') || f.name.endsWith('.jsx'));

  if (mode === 'wizard') {
    return (
      <>
        <ProjectWizard onComplete={handleWizardComplete} onCancel={handleWizardCancel} />
        <GenerationProgress isGenerating={isGenerating} progress={generationProgress} currentStep={generationStep} files={project.files} />
      </>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-[#0a0a0b]">
      <header className="border-b border-white/5 bg-black/40 backdrop-blur-xl z-40 flex-shrink-0">
        <div className="px-6 py-3 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" onClick={() => navigate('/dashboard')} className="text-gray-400 hover:text-white"><ArrowLeft className="w-4 h-4" /></Button>
            <div className="flex items-center gap-2">
              <div className="bg-gradient-to-r from-emerald-500 to-blue-500 p-2 rounded-lg"><Code2 className="w-5 h-5 text-white" /></div>
              <input value={project.name} onChange={(e) => setProject({ ...project, name: e.target.value })} className="bg-transparent border-none text-lg font-semibold focus:outline-none" />
            </div>
            <span className="text-xs bg-emerald-500/20 text-emerald-400 px-2 py-1 rounded-full">{project.files.length} fichiers</span>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" onClick={downloadProject} className="text-gray-400 hover:text-white"><Download className="w-4 h-4" /></Button>
            <Button variant="ghost" size="sm" onClick={() => setShowDeploy(!showDeploy)} className={showDeploy ? 'bg-blue-500/20 text-blue-400' : 'text-gray-400 hover:text-white'}><Rocket className="w-4 h-4 mr-2" />Deploy</Button>
            <Button onClick={saveProject} className="bg-gradient-to-r from-emerald-500 to-emerald-600"><Save className="w-4 h-4 mr-2" />Sauvegarder</Button>
          </div>
        </div>
      </header>
      <div className="flex-1 flex overflow-hidden">
        <div className={`flex flex-col ${showDeploy ? 'w-1/3' : showPreview ? 'w-1/2' : 'flex-1'} border-r border-white/5`}>
          <div className="border-b border-white/5 bg-black/20 flex items-center gap-2 px-4 py-2 overflow-x-auto">
            {project.files.map((file, idx) => (
              <button key={file.name} onClick={() => setCurrentFileIndex(idx)} className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-sm transition-colors ${currentFileIndex === idx ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-white/5 text-gray-400 hover:bg-white/10'}`}>
                <FileCode className="w-4 h-4" /><span className="truncate max-w-[120px]">{file.name}</span>
              </button>
            ))}
          </div>
          <div className="flex-1">
            {project.files.length > 0 && (
              <Editor height="100%" language={project.files[currentFileIndex]?.language || 'typescript'} value={project.files[currentFileIndex]?.content || ''} onChange={(value) => { const updatedFiles = [...project.files]; updatedFiles[currentFileIndex].content = value || ''; setProject({ ...project, files: updatedFiles }); }} theme="vs-dark" options={{ minimap: { enabled: false }, fontSize: 14, lineNumbers: 'on', automaticLayout: true, tabSize: 2 }} />
            )}
          </div>
        </div>
        {showPreview && !showDeploy && (
          <div className="flex-1 flex flex-col">
            <div className="p-2 border-b border-white/5 bg-black/20 flex items-center justify-between">
              <div className="flex items-center gap-2"><Eye className="w-4 h-4 text-emerald-400" /><span className="text-sm font-medium text-gray-300">Preview</span>{isReactProject && <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-0.5 rounded">Sandpack</span>}</div>
              <Button variant="ghost" size="sm" onClick={() => setShowPreview(false)} className="text-gray-400 hover:text-white"><PanelRightClose className="w-4 h-4" /></Button>
            </div>
            <div className="flex-1">{isReactProject ? <LivePreview files={project.files} /> : <SimplePreview files={project.files} />}</div>
          </div>
        )}
        {showDeploy && (<div className="flex-1 p-6 overflow-y-auto"><QuickDeploy files={project.files} projectName={project.name} projectId={projectId} onDeployed={(url) => { setProject({ ...project, vercel_url: url }); toast.success('Projet déployé!'); }} /></div>)}
        {!showPreview && !showDeploy && (<Button variant="ghost" size="sm" onClick={() => setShowPreview(true)} className="absolute right-4 top-20 text-gray-400 hover:text-white"><Eye className="w-4 h-4 mr-2" />Preview</Button>)}
      </div>
    </div>
  );
};

export default CreateProject;
