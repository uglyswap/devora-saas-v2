import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { toast } from 'sonner';
import SplitPane from 'react-split-pane';

// Icons
import {
  Bot, Send, Sparkles, Code, Palette, Database, Rocket, Loader2, User,
  Save, Download, Upload, Settings, FolderOpen, Plus, Trash2, FileCode,
  Play, Eye, EyeOff, ChevronLeft, ChevronRight, Menu, X, Zap,
  GitBranch, Globe, Copy, ExternalLink, Wand2, MessageSquare, Layers,
  RefreshCw, CheckCircle, AlertCircle, Info, Terminal, Maximize2, Minimize2
} from 'lucide-react';

// UI Components
import { Button } from '../components/ui/button';
import { Textarea } from '../components/ui/textarea';
import { Input } from '../components/ui/input';
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue
} from '../components/ui/select';
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger
} from '../components/ui/dropdown-menu';

// Custom Components
import WebContainerPreview from '../components/preview/WebContainerPreview';
import TemplateSelector from '../components/templates/TemplateSelector';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

// Quick prompts for the AI
const QUICK_PROMPTS = [
  { icon: Palette, text: "Design moderne", prompt: "Ameliore le design avec un style moderne et professionnel" },
  { icon: Code, text: "Ajouter feature", prompt: "Ajoute une nouvelle fonctionnalite" },
  { icon: Database, text: "Connecter BDD", prompt: "Connecte a une base de donnees Supabase" },
  { icon: Rocket, text: "Optimiser", prompt: "Optimise les performances" }
];

// Default models
const DEFAULT_MODELS = [
  { id: 'openai/gpt-4o', name: 'GPT-4o (Recommande)' },
  { id: 'anthropic/claude-3.5-sonnet', name: 'Claude 3.5 Sonnet' },
  { id: 'anthropic/claude-3-opus', name: 'Claude 3 Opus' },
  { id: 'google/gemini-pro-1.5', name: 'Gemini Pro 1.5' }
];

export default function UnifiedEditor() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const { user, hasActiveSubscription } = useAuth();

  // Default starter files for new projects
  const STARTER_FILES = {
    'index.html': `<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Mon Application</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div class="container">
    <header>
      <h1>Bienvenue sur Devora</h1>
      <p>Decrivez votre application et laissez l'IA la creer pour vous</p>
    </header>
    <main>
      <div class="card">
        <h2>Comment utiliser</h2>
        <ol>
          <li>Decrivez ce que vous voulez creer dans le chat</li>
          <li>L'IA va generer le code automatiquement</li>
          <li>Modifiez et affinez votre application</li>
          <li>Deployez en un clic!</li>
        </ol>
      </div>
    </main>
    <footer>
      <p>Cree avec Devora AI</p>
    </footer>
  </div>
  <script src="script.js"></script>
</body>
</html>`,
    'style.css': `/* Styles globaux */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  color: #333;
}

.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

header {
  text-align: center;
  padding: 3rem 0;
  color: white;
}

header h1 {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

header p {
  opacity: 0.9;
  font-size: 1.1rem;
}

.card {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 10px 40px rgba(0,0,0,0.2);
}

.card h2 {
  color: #667eea;
  margin-bottom: 1rem;
}

.card ol {
  padding-left: 1.5rem;
}

.card li {
  margin: 0.5rem 0;
  line-height: 1.6;
}

footer {
  text-align: center;
  padding: 2rem;
  color: white;
  opacity: 0.8;
}

.card {
  animation: slideUp 0.5s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}`,
    'script.js': `// Bienvenue dans votre nouvelle application!
// Decrivez vos idees dans le chat et l'IA generera le code

console.log('Application Devora initialisee');

document.addEventListener('DOMContentLoaded', () => {
  const header = document.querySelector('header');
  header.style.opacity = '0';
  header.style.transform = 'translateY(-20px)';

  setTimeout(() => {
    header.style.transition = 'all 0.5s ease';
    header.style.opacity = '1';
    header.style.transform = 'translateY(0)';
  }, 100);
});
`
  };

  const [project, setProject] = useState({
    id: null,
    name: 'Nouveau Projet',
    description: '',
    files: STARTER_FILES,
    created_at: null,
    updated_at: null
  });

  const filesToArray = (filesObj) => {
    return Object.entries(filesObj || {}).map(([name, content]) => ({
      name,
      content: typeof content === 'string' ? content : JSON.stringify(content),
      language: getLanguageFromFilename(name)
    }));
  };

  const filesToObject = (filesArr) => {
    const obj = {};
    (filesArr || []).forEach(file => {
      obj[file.name] = file.content;
    });
    return obj;
  };

  const getLanguageFromFilename = (filename) => {
    const ext = filename.split('.').pop()?.toLowerCase();
    const langMap = {
      'js': 'javascript', 'jsx': 'javascript', 'ts': 'typescript', 'tsx': 'typescript',
      'css': 'css', 'scss': 'scss', 'html': 'html', 'json': 'json',
      'md': 'markdown', 'py': 'python', 'sql': 'sql'
    };
    return langMap[ext] || 'text';
  };

  const [selectedFile, setSelectedFile] = useState('index.html');
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  const [apiKey, setApiKey] = useState('');
  const [selectedModel, setSelectedModel] = useState('openai/gpt-4o');
  const [availableModels, setAvailableModels] = useState(DEFAULT_MODELS);
  const [githubToken, setGithubToken] = useState('');
  const [vercelToken, setVercelToken] = useState('');
  const [settingsLoaded, setSettingsLoaded] = useState(false);
  const [apiKeyConfigured, setApiKeyConfigured] = useState(false);

  const [chatMessages, setChatMessages] = useState([
    { role: 'assistant', content: 'Salut! Je suis ton assistant IA Fullstack. Decris-moi ce que tu veux creer et je genererai tout le code necessaire. Tu peux aussi choisir un template SaaS pour demarrer rapidement!' }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationProgress, setGenerationProgress] = useState({ step: '', progress: 0 });
  const [hasStartedGeneration, setHasStartedGeneration] = useState(false);
  const chatEndRef = useRef(null);

  const [showSidebar, setShowSidebar] = useState(true);
  const [showPreview, setShowPreview] = useState(true);
  const [showTemplates, setShowTemplates] = useState(!projectId);
  const [previewKey, setPreviewKey] = useState(0);
  const [splitSizes, setSplitSizes] = useState([300, 'flex', 500]);

  const [isDeploying, setIsDeploying] = useState(false);
  const [deployUrl, setDeployUrl] = useState(null);

  useEffect(() => {
    loadSettings();
    if (projectId) {
      loadProject();
      setShowTemplates(false);
    } else {
      setIsLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  const loadSettings = async () => {
    try {
      const response = await axios.get(`${API}/settings`);
      if (response.data.openrouter_api_key) {
        setApiKey(response.data.openrouter_api_key);
        setApiKeyConfigured(true);
        fetchModels(response.data.openrouter_api_key);
      } else {
        setApiKeyConfigured(false);
      }
      if (response.data.github_token) setGithubToken(response.data.github_token);
      if (response.data.vercel_token) setVercelToken(response.data.vercel_token);
    } catch (error) {
      console.error('Error loading settings:', error);
      setApiKeyConfigured(false);
    } finally {
      setSettingsLoaded(true);
    }
  };

  const fetchModels = async (key) => {
    try {
      const response = await axios.get(`${API}/openrouter/models?api_key=${key}`);
      const models = response.data.data || [];
      if (models.length > 0) {
        setAvailableModels(models.slice(0, 20).map(m => ({ id: m.id, name: m.name || m.id })));
      }
    } catch (error) {
      console.error('Error fetching models:', error);
    }
  };

  const loadProject = async () => {
    setIsLoading(true);
    try {
      const response = await axios.get(`${API}/projects/${projectId}`);
      const projectData = response.data;

      let filesObj = {};
      if (Array.isArray(projectData.files)) {
        filesObj = filesToObject(projectData.files);
      } else if (typeof projectData.files === 'object') {
        filesObj = projectData.files;
      }

      setProject({
        ...projectData,
        files: filesObj
      });

      const firstFile = Object.keys(filesObj)[0];
      if (firstFile) setSelectedFile(firstFile);
    } catch (error) {
      console.error('Error loading project:', error);
      toast.error('Erreur lors du chargement du projet');
    } finally {
      setIsLoading(false);
    }
  };

  const saveProject = async () => {
    if (!project.name.trim()) {
      toast.error('Le nom du projet est requis');
      return;
    }

    setIsSaving(true);
    try {
      const projectToSave = {
        ...project,
        files: filesToArray(project.files),
        updated_at: new Date().toISOString()
      };

      if (project.id || projectId) {
        await axios.put(`${API}/projects/${project.id || projectId}`, projectToSave);
        toast.success('Projet sauvegarde!');
      } else {
        const response = await axios.post(`${API}/projects`, {
          ...projectToSave,
          id: undefined,
          created_at: new Date().toISOString()
        });
        setProject(prev => ({ ...prev, id: response.data.id }));
        navigate(`/editor/${response.data.id}`, { replace: true });
        toast.success('Projet cree!');
      }
    } catch (error) {
      console.error('Error saving project:', error);
      const errorMsg = error.response?.data?.detail || 'Erreur lors de la sauvegarde';
      toast.error(errorMsg);
    } finally {
      setIsSaving(false);
    }
  };

  const handleTemplateSelect = async (template) => {
    setHasStartedGeneration(true);
    setShowTemplates(false);

    setProject(prev => ({
      ...prev,
      name: template.name,
      description: template.description
    }));

    setChatMessages(prev => [
      ...prev,
      { role: 'user', content: `Creer: ${template.name}` },
      { role: 'assistant', content: 'thinking', isThinking: true }
    ]);

    const prompt = `Cree une application "${template.name}" complete et fonctionnelle.

Description: ${template.description}

Fonctionnalites requises:
${template.features.map(f => `- ${f}`).join('\n')}

Technologies a utiliser: ${template.tags.join(', ')}

IMPORTANT:
- Genere TOUS les fichiers necessaires (composants, pages, styles, config)
- Le code doit etre pret a l'emploi, pas juste un squelette
- Inclus les imports et exports corrects
- Utilise Tailwind CSS pour le styling
- Ajoute des donnees d'exemple realistes`;

    handleGenerate(prompt);
  };

  const handleGenerate = async (customMessage = null) => {
    const message = customMessage || inputMessage;
    if (!message.trim()) return;

    setHasStartedGeneration(true);
    setShowTemplates(false);

    if (!apiKey) {
      toast.error('Configurez votre cle API OpenRouter dans Parametres');
      setChatMessages(prev => {
        const filtered = prev.filter(m => !m.isThinking);
        return [...filtered, {
          role: 'assistant',
          content: 'Cle API OpenRouter non configuree. Allez dans Parametres pour ajouter votre cle API.'
        }];
      });
      return;
    }

    if (!hasActiveSubscription()) {
      toast.error('Abonnement requis pour utiliser l\'IA');
      setChatMessages(prev => {
        const filtered = prev.filter(m => !m.isThinking);
        return [...filtered, {
          role: 'assistant',
          content: 'Un abonnement actif est requis pour utiliser l\'IA. Rendez-vous sur la page Facturation.'
        }];
      });
      return;
    }

    setIsGenerating(true);
    setInputMessage('');

    if (!customMessage) {
      setChatMessages(prev => [
        ...prev,
        { role: 'user', content: message },
        { role: 'assistant', content: 'thinking', isThinking: true }
      ]);
    }

    try {
      const conversationHistory = chatMessages
        .filter(m => !m.isThinking)
        .map(m => ({ role: m.role, content: m.content }));

      const currentFiles = filesToArray(project.files);

      setGenerationProgress({ step: 'Analyse de votre demande...', progress: 15 });

      let response;

      try {
        setGenerationProgress({ step: 'Agents en action...', progress: 30 });
        response = await axios.post(`${API}/generate/agentic`, {
          message,
          model: selectedModel,
          api_key: apiKey,
          current_files: currentFiles,
          conversation_history: conversationHistory,
          project_id: project.id || projectId,
          user_id: user?.id
        }, { timeout: 120000 });
      } catch (agenticError) {
        console.log('Agentic endpoint failed, trying fullstack...', agenticError);
        setGenerationProgress({ step: 'Mode fullstack...', progress: 40 });

        response = await axios.post(`${API}/generate/fullstack`, {
          message,
          model: selectedModel,
          api_key: apiKey,
          current_files: currentFiles,
          conversation_history: conversationHistory,
          project_id: project.id || projectId,
          user_id: user?.id
        }, { timeout: 120000 });
      }

      setGenerationProgress({ step: 'Traitement des fichiers...', progress: 80 });

      if (response.data.files && response.data.files.length > 0) {
        const newFiles = {};
        response.data.files.forEach(file => {
          newFiles[file.name] = file.content;
        });

        setProject(prev => ({
          ...prev,
          files: { ...prev.files, ...newFiles }
        }));

        const firstNewFile = Object.keys(newFiles)[0];
        if (firstNewFile) setSelectedFile(firstNewFile);

        setPreviewKey(prev => prev + 1);

        setTimeout(() => {
          if (project.id || projectId) {
            saveProject();
          }
        }, 500);
      }

      setGenerationProgress({ step: 'Termine!', progress: 100 });

      const filesCount = response.data.files?.length || 0;
      const assistantMessage = response.data.message ||
        `J'ai genere ${filesCount} fichier${filesCount > 1 ? 's' : ''}. ${filesCount > 0 ? 'Tu peux voir le resultat dans l\'apercu!' : ''}`;

      setChatMessages(prev => {
        const filtered = prev.filter(m => !m.isThinking);
        return [...filtered, { role: 'assistant', content: assistantMessage }];
      });

    } catch (error) {
      console.error('Generation error:', error);

      setGenerationProgress({ step: '', progress: 0 });

      let errorMessage = 'Une erreur est survenue lors de la generation.';

      if (error.code === 'ECONNABORTED') {
        errorMessage = 'La generation a pris trop de temps. Reessayez avec une demande plus simple.';
      } else if (error.response?.status === 422) {
        errorMessage = 'Erreur de validation. Verifiez votre cle API.';
      } else if (error.response?.status === 401) {
        errorMessage = 'Cle API invalide. Verifiez vos parametres.';
      } else if (error.response?.status === 503) {
        errorMessage = 'Service temporairement indisponible. Reessayez dans quelques instants.';
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      }

      setChatMessages(prev => {
        const filtered = prev.filter(m => !m.isThinking);
        return [...filtered, { role: 'assistant', content: `Erreur: ${errorMessage}` }];
      });

      toast.error(errorMessage);
    } finally {
      setIsGenerating(false);
      setTimeout(() => setGenerationProgress({ step: '', progress: 0 }), 1000);
    }
  };

  const handleFileChange = (content) => {
    if (!selectedFile) return;
    setProject(prev => ({
      ...prev,
      files: { ...prev.files, [selectedFile]: content }
    }));
  };

  const createNewFile = () => {
    const fileName = prompt('Nom du fichier (ex: component.jsx):');
    if (!fileName) return;

    setProject(prev => ({
      ...prev,
      files: { ...prev.files, [fileName]: '' }
    }));
    setSelectedFile(fileName);
  };

  const deleteFile = (fileName) => {
    if (!confirm(`Supprimer ${fileName}?`)) return;

    setProject(prev => {
      const newFiles = { ...prev.files };
      delete newFiles[fileName];
      return { ...prev, files: newFiles };
    });

    if (selectedFile === fileName) {
      const remaining = Object.keys(project.files).filter(f => f !== fileName);
      setSelectedFile(remaining[0] || null);
    }
  };

  const handleQuickPrompt = (prompt) => {
    setInputMessage(prompt);
  };

  const handleDeploy = async () => {
    if (!vercelToken) {
      toast.error('Configurez votre token Vercel dans les parametres');
      return;
    }

    setIsDeploying(true);
    try {
      const response = await axios.post(`${API}/deploy/vercel`, {
        project_id: project.id || projectId,
        files: project.files,
        name: project.name.toLowerCase().replace(/[^a-z0-9]/g, '-')
      });

      setDeployUrl(response.data.url);
      toast.success('Deploiement reussi!');
    } catch (error) {
      console.error('Deploy error:', error);
      toast.error('Erreur lors du deploiement');
    } finally {
      setIsDeploying(false);
    }
  };

  const getFileIcon = (fileName) => {
    if (fileName.endsWith('.jsx') || fileName.endsWith('.tsx')) return <FileCode className="w-4 h-4 text-blue-400" />;
    if (fileName.endsWith('.css') || fileName.endsWith('.scss')) return <Palette className="w-4 h-4 text-pink-400" />;
    if (fileName.endsWith('.json')) return <Database className="w-4 h-4 text-yellow-400" />;
    return <Code className="w-4 h-4 text-gray-400" />;
  };

  if (isLoading) {
    return (
      <div className="h-screen bg-gradient-to-br from-[#0a0a0b] via-[#111113] to-[#0a0a0b] flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-12 h-12 animate-spin text-emerald-500" />
          <p className="text-gray-400">Chargement du projet...</p>
        </div>
      </div>
    );
  }

  if (showTemplates && !projectId && !hasStartedGeneration) {
    return (
      <div className="h-screen bg-gradient-to-br from-[#0a0a0b] via-[#111113] to-[#0a0a0b] overflow-auto">
        <div className="max-w-6xl mx-auto p-8">
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-4">
              <Button variant="ghost" onClick={() => navigate('/dashboard')}>
                <ChevronLeft className="w-5 h-5 mr-2" />
                Retour
              </Button>
              <div>
                <h1 className="text-3xl font-bold text-white">Nouveau Projet</h1>
                <p className="text-gray-400">Choisis un template ou commence de zero</p>
              </div>
            </div>
            <Button onClick={() => setShowTemplates(false)} className="bg-emerald-600 hover:bg-emerald-700">
              <Plus className="w-5 h-5 mr-2" />
              Projet Vide
            </Button>
          </div>

          <TemplateSelector onSelect={handleTemplateSelect} />
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen bg-[#0d0d0f] flex flex-col overflow-hidden">
      {/* Top Bar */}
      <div className="h-14 bg-[#1a1a1d] border-b border-white/10 flex items-center justify-between px-4">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={() => navigate('/dashboard')}>
            <ChevronLeft className="w-5 h-5" />
          </Button>
          <Input
            value={project.name}
            onChange={(e) => setProject(prev => ({ ...prev, name: e.target.value }))}
            className="w-48 bg-transparent border-none text-white font-semibold focus:ring-0"
          />
        </div>

        <div className="flex items-center gap-2 bg-gradient-to-r from-emerald-600/20 to-blue-600/20 border border-emerald-500/30 rounded-lg px-4 py-2">
          <Zap className="w-4 h-4 text-emerald-400" />
          <span className="text-sm font-medium text-white">Mode Fullstack Agentique</span>
          <span className="text-xs text-gray-400 ml-2">Multi-agents + Code complet</span>
        </div>

        <div className="flex items-center gap-2">
          {settingsLoaded && (
            <div
              onClick={() => !apiKeyConfigured && navigate('/settings')}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg cursor-pointer transition-colors ${
                apiKeyConfigured
                  ? 'bg-emerald-500/10 border border-emerald-500/30'
                  : 'bg-red-500/10 border border-red-500/30 hover:bg-red-500/20'
              }`}
              title={apiKeyConfigured ? 'Cle API configuree' : 'Cliquez pour configurer votre cle API'}
            >
              {apiKeyConfigured ? (
                <>
                  <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
                  <span className="text-xs font-medium text-emerald-400">API OK</span>
                </>
              ) : (
                <>
                  <AlertCircle className="w-3.5 h-3.5 text-red-400" />
                  <span className="text-xs font-medium text-red-400">Configurer API</span>
                </>
              )}
            </div>
          )}

          <Select value={selectedModel} onValueChange={setSelectedModel}>
            <SelectTrigger className="w-52 bg-gradient-to-r from-purple-600/10 to-blue-600/10 border-purple-500/30 text-white hover:from-purple-600/20 hover:to-blue-600/20">
              <div className="flex items-center gap-2">
                <Bot className="w-4 h-4 text-purple-400" />
                <SelectValue placeholder="Modele IA" />
              </div>
            </SelectTrigger>
            <SelectContent>
              {availableModels.map(model => (
                <SelectItem key={model.id} value={model.id}>
                  {model.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Button
            variant="outline"
            size="sm"
            onClick={saveProject}
            disabled={isSaving}
            className="border-white/10"
          >
            {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
          </Button>

          <Button
            size="sm"
            onClick={handleDeploy}
            disabled={isDeploying || !Object.keys(project.files).length}
            className="bg-gradient-to-r from-blue-600 to-purple-600"
          >
            {isDeploying ? <Loader2 className="w-4 h-4 animate-spin" /> : <Rocket className="w-4 h-4" />}
            <span className="ml-2">Deploy</span>
          </Button>

          <Button variant="ghost" size="sm" onClick={() => navigate('/settings')}>
            <Settings className="w-4 h-4" />
          </Button>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {showSidebar && (
          <div className="w-56 bg-[#141416] border-r border-white/10 flex flex-col">
            <div className="p-3 border-b border-white/10 flex items-center justify-between">
              <span className="text-sm font-medium text-gray-400">Fichiers</span>
              <Button variant="ghost" size="sm" onClick={createNewFile}>
                <Plus className="w-4 h-4" />
              </Button>
            </div>
            <div className="flex-1 overflow-auto p-2">
              {Object.keys(project.files || {}).length === 0 ? (
                <div className="text-center py-8 text-gray-500 text-sm">
                  <FolderOpen className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p>Aucun fichier</p>
                  <p className="text-xs mt-1">Utilise l'IA pour generer du code</p>
                </div>
              ) : (
                <div className="space-y-1">
                  {Object.keys(project.files).map(fileName => (
                    <div
                      key={fileName}
                      onClick={() => setSelectedFile(fileName)}
                      className={`flex items-center justify-between px-3 py-2 rounded-lg cursor-pointer group ${
                        selectedFile === fileName
                          ? 'bg-emerald-600/20 text-emerald-400'
                          : 'hover:bg-white/5 text-gray-300'
                      }`}
                    >
                      <div className="flex items-center gap-2 truncate">
                        {getFileIcon(fileName)}
                        <span className="text-sm truncate">{fileName}</span>
                      </div>
                      <button
                        onClick={(e) => { e.stopPropagation(); deleteFile(fileName); }}
                        className="opacity-0 group-hover:opacity-100 text-gray-500 hover:text-red-400"
                      >
                        <Trash2 className="w-3 h-3" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        <button
          onClick={() => setShowSidebar(!showSidebar)}
          className="absolute left-0 top-1/2 -translate-y-1/2 z-10 bg-[#1a1a1d] border border-white/10 rounded-r-lg p-1"
          style={{ left: showSidebar ? '224px' : '0' }}
        >
          {showSidebar ? <ChevronLeft className="w-4 h-4 text-gray-400" /> : <ChevronRight className="w-4 h-4 text-gray-400" />}
        </button>

        <div className="flex-1 flex">
          <div className="flex-1 flex flex-col min-w-0">
            <div className="flex-1 flex flex-col bg-gradient-to-br from-gray-900 to-gray-800 overflow-hidden">
              <div className="p-3 border-b border-gray-700 bg-gray-800/50">
                <div className="flex items-center gap-2 overflow-x-auto pb-1">
                  <Sparkles className="w-4 h-4 text-yellow-500 flex-shrink-0" />
                  {QUICK_PROMPTS.map((prompt, i) => {
                    const Icon = prompt.icon;
                    return (
                      <button
                        key={i}
                        onClick={() => handleQuickPrompt(prompt.prompt)}
                        className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-700 hover:bg-gray-600 rounded-full text-sm text-white whitespace-nowrap transition-colors"
                      >
                        <Icon className="w-3.5 h-3.5" />
                        {prompt.text}
                      </button>
                    );
                  })}
                </div>
              </div>

              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {chatMessages.map((msg, i) => (
                  <div key={i} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                      msg.role === 'user'
                        ? 'bg-blue-600'
                        : 'bg-gradient-to-r from-purple-500 to-pink-500'
                    }`}>
                      {msg.role === 'user' ? <User className="w-4 h-4 text-white" /> : <Bot className="w-4 h-4 text-white" />}
                    </div>
                    <div className={`max-w-[80%] p-3 rounded-2xl ${
                      msg.role === 'user'
                        ? 'bg-blue-600 text-white rounded-br-sm'
                        : 'bg-gray-700 text-gray-100 rounded-bl-sm'
                    }`}>
                      {msg.isThinking ? (
                        <div className="flex items-center gap-2">
                          <Loader2 className="w-4 h-4 animate-spin" />
                          <span>{generationProgress.step || 'Je reflechis...'}</span>
                        </div>
                      ) : (
                        <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                      )}
                    </div>
                  </div>
                ))}
                <div ref={chatEndRef} />
              </div>

              {isGenerating && generationProgress.progress > 0 && (
                <div className="px-4 py-2 border-t border-gray-700 bg-gray-800/50">
                  <div className="flex items-center gap-3 text-sm text-gray-400">
                    <Loader2 className="w-4 h-4 animate-spin text-emerald-500" />
                    <span>{generationProgress.step}</span>
                    <div className="flex-1 h-1.5 bg-gray-700 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-emerald-500 to-blue-500 transition-all duration-500"
                        style={{ width: `${generationProgress.progress}%` }}
                      />
                    </div>
                  </div>
                </div>
              )}

              <div className="p-4 border-t border-gray-700 bg-gray-800/50">
                <div className="flex gap-2">
                  <Textarea
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    placeholder="Decris ce que tu veux creer..."
                    className="flex-1 min-h-[60px] max-h-[120px] bg-gray-700 border-gray-600 text-white placeholder-gray-400 resize-none"
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleGenerate();
                      }
                    }}
                    disabled={isGenerating}
                  />
                  <Button
                    onClick={() => handleGenerate()}
                    disabled={!inputMessage.trim() || isGenerating}
                    className="h-[60px] w-[60px] bg-gradient-to-r from-emerald-600 to-blue-600 hover:from-emerald-700 hover:to-blue-700"
                  >
                    {isGenerating ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
                  </Button>
                </div>
                <div className="mt-2 flex items-center justify-between text-xs text-gray-500">
                  <span>Shift + Enter pour nouvelle ligne</span>
                  <span className="flex items-center gap-1">
                    <Zap className="w-3 h-3 text-emerald-500" />
                    Fullstack Agentique
                  </span>
                </div>
              </div>
            </div>

            {selectedFile && (
              <div className="h-64 border-t border-white/10 bg-[#1e1e1e]">
                <div className="flex items-center justify-between px-4 py-2 bg-[#252526] border-b border-white/10">
                  <div className="flex items-center gap-2">
                    {getFileIcon(selectedFile)}
                    <span className="text-sm text-gray-300">{selectedFile}</span>
                  </div>
                  <Button variant="ghost" size="sm" onClick={() => setPreviewKey(prev => prev + 1)}>
                    <RefreshCw className="w-4 h-4" />
                  </Button>
                </div>
                <textarea
                  value={project.files?.[selectedFile] || ''}
                  onChange={(e) => handleFileChange(e.target.value)}
                  className="w-full h-[calc(100%-40px)] bg-[#1e1e1e] text-gray-200 font-mono text-sm p-4 resize-none focus:outline-none"
                  spellCheck={false}
                />
              </div>
            )}
          </div>

          {showPreview && (
            <div className="w-[45%] border-l border-white/10 flex flex-col bg-white">
              <div className="flex items-center justify-between px-4 py-2 bg-[#1a1a1d] border-b border-white/10">
                <div className="flex items-center gap-2">
                  <Eye className="w-4 h-4 text-gray-400" />
                  <span className="text-sm text-gray-300">Apercu</span>
                </div>
                <div className="flex items-center gap-2">
                  <Button variant="ghost" size="sm" onClick={() => setPreviewKey(prev => prev + 1)}>
                    <RefreshCw className="w-4 h-4" />
                  </Button>
                  <Button variant="ghost" size="sm" onClick={() => setShowPreview(false)}>
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              </div>
              <div className="flex-1">
                <WebContainerPreview
                  key={previewKey}
                  files={project.files || {}}
                />
              </div>
            </div>
          )}

          {!showPreview && (
            <button
              onClick={() => setShowPreview(true)}
              className="absolute right-0 top-1/2 -translate-y-1/2 bg-[#1a1a1d] border border-white/10 rounded-l-lg p-2"
            >
              <Eye className="w-4 h-4 text-gray-400" />
            </button>
          )}
        </div>
      </div>

      {deployUrl && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50">
          <div className="bg-[#1a1a1d] border border-white/10 rounded-xl p-6 max-w-md w-full mx-4">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-green-500/20 rounded-full flex items-center justify-center">
                <CheckCircle className="w-6 h-6 text-green-500" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-white">Deploiement Reussi!</h3>
                <p className="text-gray-400 text-sm">Votre app est en ligne</p>
              </div>
            </div>

            <div className="flex items-center gap-2 p-3 bg-gray-800 rounded-lg mb-4">
              <Globe className="w-5 h-5 text-blue-400" />
              <span className="flex-1 font-mono text-sm text-gray-300 truncate">{deployUrl}</span>
              <Button variant="ghost" size="sm" onClick={() => navigator.clipboard.writeText(deployUrl)}>
                <Copy className="w-4 h-4" />
              </Button>
              <Button variant="ghost" size="sm" onClick={() => window.open(deployUrl, '_blank')}>
                <ExternalLink className="w-4 h-4" />
              </Button>
            </div>

            <Button onClick={() => setDeployUrl(null)} className="w-full bg-emerald-600 hover:bg-emerald-700">
              Fermer
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
