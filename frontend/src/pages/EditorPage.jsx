import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { 
  ArrowLeft, Send, Save, Download, Github, Globe, 
  Loader2, Code2, Eye, MessageSquare, FileCode,
  Play, Settings, Plus, X, Copy, Check, EyeOff, PanelLeftClose, PanelLeftOpen,
  Bot, Sparkles, Trash2, ExternalLink, Rocket, Layers
} from 'lucide-react';
import Editor from '@monaco-editor/react';
import axios from 'axios';
import { toast } from 'sonner';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../components/ui/dialog';
import { Label } from '../components/ui/label';
import SplitPane from 'react-split-pane';
import JSZip from 'jszip';
import './EditorPage.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const EditorPage = () => {
  const navigate = useNavigate();
  const { projectId } = useParams();
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [copied, setCopied] = useState(false);
  const [showEditor, setShowEditor] = useState(true);
  const [useAgenticMode, setUseAgenticMode] = useState(true);
  
  // NEW: Fullstack mode toggle for Next.js generation
  const [useFullstackMode, setUseFullstackMode] = useState(false);
  
  // Preview state for Full-Stack projects
  const [previewUrl, setPreviewUrl] = useState(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  
  // Project state with conversation history for BUG 4
  const [project, setProject] = useState({
    name: 'Nouveau Projet',
    description: '',
    files: [
      { name: 'index.html', content: '<!DOCTYPE html>\n<html>\n<head>\n  <title>Mon App</title>\n  <link rel="stylesheet" href="styles.css">\n</head>\n<body>\n  <h1>Hello World!</h1>\n  <script src="script.js"></script>\n</body>\n</html>', language: 'html' },
      { name: 'styles.css', content: 'body {\n  font-family: Arial, sans-serif;\n  margin: 0;\n  padding: 20px;\n  background: #f5f5f5;\n}\n\nh1 {\n  color: #333;\n}', language: 'css' },
      { name: 'script.js', content: 'console.log("Hello from JavaScript!");', language: 'javascript' }
    ],
    conversation_history: [] // BUG 4 FIX: Store conversation with project
  });
  
  const [currentFileIndex, setCurrentFileIndex] = useState(0);
  const [chatMessages, setChatMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [selectedModel, setSelectedModel] = useState('openai/gpt-4o');
  const [availableModels, setAvailableModels] = useState([]);
  
  // Export dialogs
  const [showGithubDialog, setShowGithubDialog] = useState(false);
  const [showVercelDialog, setShowVercelDialog] = useState(false);
  const [githubRepoName, setGithubRepoName] = useState('');
  const [vercelProjectName, setVercelProjectName] = useState('');
  const [githubToken, setGithubToken] = useState('');
  const [vercelToken, setVercelToken] = useState('');
  const [isPrivateRepo, setIsPrivateRepo] = useState(false);
  
  const chatEndRef = useRef(null);
  const iframeRef = useRef(null);

  // Detect if project is Full-Stack (Next.js/TypeScript)
  const isFullStackProject = useCallback(() => {
    const files = project.files || [];
    const hasTypeScript = files.some(f => f.name.endsWith('.tsx') || f.name.endsWith('.ts'));
    const hasAppRouter = files.some(f => f.name.includes('app/') || f.name.includes('app\\'));
    const hasPackageJson = files.some(f => f.name === 'package.json');
    const hasNextConfig = files.some(f => f.name === 'next.config.js' || f.name === 'next.config.ts');

    // Full-Stack if: has TypeScript OR App Router OR Next.js config (ignore default HTML files)
    return hasTypeScript || hasAppRouter || (hasPackageJson && hasNextConfig);
  }, [project.files]);

  useEffect(() => {
    if (projectId) {
      loadProject();
    }
    loadSettings();
  }, [projectId]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  useEffect(() => {
    if (apiKey) {
      fetchModels();
    }
  }, [apiKey]);

  useEffect(() => {
    updatePreview();
  }, [project.files]);

  // BUG 4 FIX: Sync chat messages with project conversation history
  useEffect(() => {
    if (chatMessages.length > 0) {
      setProject(prev => ({
        ...prev,
        conversation_history: chatMessages
      }));
    }
  }, [chatMessages]);

  // Ensure currentFileIndex is valid when files change
  useEffect(() => {
    if (currentFileIndex >= project.files.length) {
      setCurrentFileIndex(Math.max(0, project.files.length - 1));
    }
  }, [project.files.length, currentFileIndex]);

  const loadProject = async () => {
    try {
      const response = await axios.get(`${API}/projects/${projectId}`);
      const loadedProject = response.data;
      setProject(loadedProject);
      
      // BUG 4 FIX: Restore conversation history from project
      if (loadedProject.conversation_history && loadedProject.conversation_history.length > 0) {
        setChatMessages(loadedProject.conversation_history);
      }
      
      // Restore preview URL if exists
      if (loadedProject.vercel_url) {
        setPreviewUrl(loadedProject.vercel_url);
      }
      
      // Detect fullstack mode from existing files
      const hasTypeScript = loadedProject.files?.some(f => 
        f.name.endsWith('.tsx') || f.name.endsWith('.ts')
      );
      if (hasTypeScript) {
        setUseFullstackMode(true);
      }
      
      // Reset file index to 0 for newly loaded project
      setCurrentFileIndex(0);
    } catch (error) {
      console.error('Error loading project:', error);
      toast.error('Erreur lors du chargement du projet');
    }
  };

  const loadSettings = async () => {
    try {
      const response = await axios.get(`${API}/settings`);
      if (response.data.openrouter_api_key) {
        setApiKey(response.data.openrouter_api_key);
      }
      if (response.data.github_token) {
        setGithubToken(response.data.github_token);
      }
      if (response.data.vercel_token) {
        setVercelToken(response.data.vercel_token);
      }
    } catch (error) {
      console.error('Error loading settings:', error);
    }
  };

  const fetchModels = async () => {
    try {
      const response = await axios.get(`${API}/openrouter/models?api_key=${apiKey}`);
      const models = response.data.data || [];
      setAvailableModels(models);
    } catch (error) {
      console.error('Error fetching models:', error);
    }
  };

  const saveProject = async () => {
    setLoading(true);
    try {
      // Include conversation history in saved project
      const projectToSave = {
        ...project,
        conversation_history: chatMessages
      };
      
      if (projectId) {
        await axios.put(`${API}/projects/${projectId}`, projectToSave);
        toast.success('Projet sauvegardé');
      } else {
        const response = await axios.post(`${API}/projects`, projectToSave);
        toast.success('Projet créé');
        navigate(`/editor/${response.data.id}`);
      }
    } catch (error) {
      console.error('Error saving project:', error);
      toast.error('Erreur lors de la sauvegarde');
    } finally {
      setLoading(false);
    }
  };

  // BUG 4 FIX: Clear conversation function
  const clearConversation = () => {
    if (window.confirm('Voulez-vous vraiment effacer l\'historique de conversation ?')) {
      setChatMessages([]);
      setProject(prev => ({ ...prev, conversation_history: [] }));
      toast.success('Conversation effacée');
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || !apiKey) {
      toast.error('Veuillez entrer un message et configurer votre clé API');
      return;
    }

    const userMessage = { role: 'user', content: inputMessage };
    setChatMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setGenerating(true);

    try {
      if (useAgenticMode) {
        // Determine endpoint based on fullstack mode
        const endpoint = useFullstackMode 
          ? `${API}/generate/fullstack`
          : `${API}/generate/agentic`;
        
        const modeLabel = useFullstackMode ? 'Full-Stack Next.js' : 'Agentique';
        
        const agenticMessage = { 
          role: 'assistant', 
          content: `🤖 **Système ${modeLabel} Activé**\n\n` +
                   '🔄 **Phase 1 : Planification**\nAnalyse des exigences...' 
        };
        setChatMessages(prev => [...prev, agenticMessage]);

        // BUG 4 FIX: Include conversation history in request
        const response = await axios.post(endpoint, {
          message: inputMessage,
          model: selectedModel,
          api_key: apiKey,
          current_files: project.files,
          conversation_history: chatMessages.slice(-10), // Last 10 messages for context
          project_type: useFullstackMode ? 'saas' : undefined
        });

        if (response.data.success) {
          // Build detailed progress message
          let progressMsg = `🤖 **Système ${modeLabel} - Résultat**\n\n`;
          
          const events = response.data.progress_events || [];
          events.forEach(evt => {
            const emoji = {
              'planning': '📋',
              'plan_complete': '✅',
              'coding': '💻',
              'code_complete': '✅',
              'testing': '🧪',
              'test_complete': '✅',
              'reviewing': '🔍',
              'review_complete': '✅',
              'fixing': '🔧',
              'complete': '🎉'
            }[evt.event] || '•';
            
            progressMsg += `${emoji} ${evt.data.message}\n`;
          });
          
          progressMsg += `\n✨ Génération terminée en ${response.data.iterations} itération(s) !`;
          progressMsg += `\n📦 ${response.data.files?.length || 0} fichier(s) généré(s).`;
          
          if (useFullstackMode && response.data.stack) {
            progressMsg += `\n\n🛠️ **Stack:** ${response.data.stack.frontend?.join(', ')}`;
          }

          setChatMessages(prev => {
            const newMessages = [...prev];
            newMessages[newMessages.length - 1] = {
              role: 'assistant',
              content: progressMsg
            };
            return newMessages;
          });

          // Apply generated files
          if (response.data.files && response.data.files.length > 0) {
            const generatedFiles = response.data.files;

            setProject(prev => {
              let updatedFiles = [...prev.files];

              // For Full-Stack projects, remove default starter files
              if (useFullstackMode) {
                const defaultFiles = ['index.html', 'styles.css', 'script.js'];
                updatedFiles = updatedFiles.filter(f => !defaultFiles.includes(f.name));
              }

              generatedFiles.forEach(newFile => {
                const existingIndex = updatedFiles.findIndex(f => f.name === newFile.name);
                if (existingIndex >= 0) {
                  updatedFiles[existingIndex] = newFile;
                } else {
                  updatedFiles.push(newFile);
                }
              });

              return { ...prev, files: updatedFiles };
            });

            // For Full-Stack, select a meaningful file (package.json or first component)
            if (useFullstackMode) {
              const packageJsonIndex = generatedFiles.findIndex(f => f.name === 'package.json');
              if (packageJsonIndex >= 0) {
                setCurrentFileIndex(packageJsonIndex);
              } else {
                setCurrentFileIndex(0);
              }
            }

            // Clear preview URL when new files are generated (needs new preview)
            setPreviewUrl(null);

            toast.success(`${response.data.files.length} fichier(s) généré(s) par le système ${modeLabel.toLowerCase()} !`);
          }
        }
      } else {
        // Use Standard OpenRouter
        const conversationHistory = chatMessages.map(msg => ({
          role: msg.role,
          content: msg.content
        }));

        const response = await axios.post(`${API}/generate/openrouter`, {
          message: inputMessage,
          model: selectedModel,
          api_key: apiKey,
          conversation_history: conversationHistory
        });

        const assistantMessage = { role: 'assistant', content: response.data.response };
        setChatMessages(prev => [...prev, assistantMessage]);

        // Parse code from response
        parseAndApplyCode(response.data.response);
      }
      
    } catch (error) {
      console.error('Error generating code:', error);
      toast.error('Erreur lors de la génération');
      setChatMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Désolé, une erreur est survenue. Vérifiez votre clé API et réessayez.' 
      }]);
    } finally {
      setGenerating(false);
    }
  };

  const parseAndApplyCode = (response) => {
    const codeBlockRegex = /```(\w+)\n?(?:\/\/\s*filename:\s*(.+)\n)?([\s\S]*?)```/g;
    let match;
    const newFiles = [];

    while ((match = codeBlockRegex.exec(response)) !== null) {
      const [, language, filename, code] = match;
      const cleanCode = code.trim();
      
      if (filename) {
        newFiles.push({
          name: filename.trim(),
          content: cleanCode,
          language: language || 'plaintext'
        });
      } else {
        // If no filename, try to determine from language
        const ext = language === 'html' ? 'html' : language === 'css' ? 'css' : language === 'javascript' ? 'js' : 'txt';
        const name = `file.${ext}`;
        newFiles.push({
          name,
          content: cleanCode,
          language: language || 'plaintext'
        });
      }
    }

    if (newFiles.length > 0) {
      setProject(prev => {
        const updatedFiles = [...prev.files];
        
        newFiles.forEach(newFile => {
          const existingIndex = updatedFiles.findIndex(f => f.name === newFile.name);
          if (existingIndex >= 0) {
            updatedFiles[existingIndex] = newFile;
          } else {
            updatedFiles.push(newFile);
          }
        });
        
        return { ...prev, files: updatedFiles };
      });
      
      // Clear preview URL
      setPreviewUrl(null);
      
      toast.success(`${newFiles.length} fichier(s) mis à jour`);
    }
  };

  const updatePreview = () => {
    if (!iframeRef.current) return;
    
    // Check if Full-Stack project
    if (isFullStackProject()) {
      // Show informative message for Full-Stack projects
      const fullStackMessage = `
<!DOCTYPE html>
<html>
<head>
  <title>Preview Full-Stack</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
      color: white;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }
    .container {
      text-align: center;
      max-width: 500px;
    }
    .icon {
      font-size: 64px;
      margin-bottom: 24px;
    }
    h1 {
      font-size: 24px;
      margin-bottom: 16px;
      background: linear-gradient(90deg, #10b981, #3b82f6);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    p {
      color: #9ca3af;
      line-height: 1.6;
      margin-bottom: 24px;
    }
    .stack {
      display: flex;
      gap: 8px;
      justify-content: center;
      flex-wrap: wrap;
      margin-bottom: 24px;
    }
    .badge {
      background: rgba(255,255,255,0.1);
      padding: 6px 12px;
      border-radius: 20px;
      font-size: 12px;
      border: 1px solid rgba(255,255,255,0.1);
    }
    .info {
      background: rgba(59, 130, 246, 0.1);
      border: 1px solid rgba(59, 130, 246, 0.3);
      border-radius: 12px;
      padding: 16px;
      font-size: 14px;
      color: #93c5fd;
    }
    .arrow { margin: 0 8px; }
  </style>
</head>
<body>
  <div class="container">
    <div class="icon">🚀</div>
    <h1>Projet Full-Stack Next.js</h1>
    <p>
      Ce projet utilise Next.js 14+ avec App Router, TypeScript et des fonctionnalités serveur.
      L'aperçu instantané n'est pas disponible pour ce type de projet.
    </p>
    <div class="stack">
      <span class="badge">Next.js 14+</span>
      <span class="badge">TypeScript</span>
      <span class="badge">Tailwind CSS</span>
      <span class="badge">Supabase</span>
    </div>
    <div class="info">
      <strong>💡 Pour voir l'aperçu :</strong><br/>
      Cliquez sur le bouton <strong>"Preview Vercel"</strong> ci-dessus<br/>
      <span class="arrow">→</span> Déploiement en ~30-60 secondes
    </div>
  </div>
</body>
</html>
      `;
      iframeRef.current.srcdoc = fullStackMessage;
      return;
    }

    // Standard preview for HTML/CSS/JS projects
    const htmlFile = project.files.find(f => f.name.endsWith('.html'));
    const cssFile = project.files.find(f => f.name.endsWith('.css'));
    const jsFile = project.files.find(f => f.name.endsWith('.js'));

    let html = htmlFile?.content || '<!DOCTYPE html><html><head></head><body><h1>Pas de fichier HTML</h1></body></html>';
    
    // Inject CSS
    if (cssFile && html.includes('</head>')) {
      html = html.replace('</head>', `<style>${cssFile.content}</style></head>`);
    }
    
    // Inject JS
    if (jsFile && html.includes('</body>')) {
      html = html.replace('</body>', `<script>${jsFile.content}</script></body>`);
    }

    // Use srcdoc to avoid CORS issues
    iframeRef.current.srcdoc = html;
  };

  // Generate Vercel Preview for Full-Stack projects
  const generateVercelPreview = async () => {
    if (!vercelToken) {
      toast.error('Veuillez configurer votre token Vercel dans les paramètres');
      navigate('/settings');
      return;
    }

    // Save project first if needed
    if (!projectId) {
      toast.error('Veuillez d\'abord sauvegarder le projet');
      await saveProject();
      return;
    }

    setPreviewLoading(true);
    
    try {
      const previewName = `${project.name.toLowerCase().replace(/[^a-z0-9]/g, '-')}-preview-${Date.now()}`;
      
      const response = await axios.post(`${API}/vercel/deploy`, {
        project_id: projectId,
        vercel_token: vercelToken,
        project_name: previewName
      });

      if (response.data.success) {
        setPreviewUrl(response.data.url);
        toast.success('Preview déployé sur Vercel !');
        
        // Update project with preview URL
        setProject(prev => ({ ...prev, vercel_url: response.data.url }));
      }
    } catch (error) {
      console.error('Error creating Vercel preview:', error);
      toast.error(error.response?.data?.detail || 'Erreur lors du déploiement preview');
    } finally {
      setPreviewLoading(false);
    }
  };

  const exportToGithub = async () => {
    if (!githubRepoName || !githubToken) {
      toast.error('Veuillez remplir tous les champs');
      return;
    }

    // Save project first
    await saveProject();

    setLoading(true);
    try {
      const response = await axios.post(`${API}/github/export`, {
        project_id: projectId || project.id,
        repo_name: githubRepoName,
        github_token: githubToken,
        private: isPrivateRepo
      });

      toast.success('Projet exporté sur GitHub !');
      setShowGithubDialog(false);
      window.open(response.data.repo_url, '_blank');
    } catch (error) {
      console.error('Error exporting to GitHub:', error);
      toast.error(error.response?.data?.detail || 'Erreur lors de l\'export');
    } finally {
      setLoading(false);
    }
  };

  const deployToVercel = async () => {
    if (!vercelProjectName || !vercelToken) {
      toast.error('Veuillez remplir tous les champs');
      return;
    }

    // Save project first
    await saveProject();

    setLoading(true);
    try {
      const response = await axios.post(`${API}/vercel/deploy`, {
        project_id: projectId || project.id,
        vercel_token: vercelToken,
        project_name: vercelProjectName
      });

      toast.success('Projet déployé sur Vercel !');
      setShowVercelDialog(false);
      window.open(response.data.url, '_blank');
    } catch (error) {
      console.error('Error deploying to Vercel:', error);
      toast.error(error.response?.data?.detail || 'Erreur lors du déploiement');
    } finally {
      setLoading(false);
    }
  };

  const addNewFile = () => {
    const fileName = prompt('Nom du fichier (ex: app.js, styles.css):');
    if (!fileName) return;
    
    const extension = fileName.split('.').pop();
    const languageMap = {
      'html': 'html',
      'css': 'css',
      'js': 'javascript',
      'ts': 'typescript',
      'tsx': 'typescriptreact',
      'jsx': 'javascriptreact',
      'json': 'json',
      'md': 'markdown',
      'sql': 'sql'
    };
    
    const newFile = {
      name: fileName,
      content: '',
      language: languageMap[extension] || 'plaintext'
    };
    
    setProject(prev => ({
      ...prev,
      files: [...prev.files, newFile]
    }));
    
    // Select the new file
    setCurrentFileIndex(project.files.length);
  };

  const deleteFile = (index) => {
    if (project.files.length <= 1) {
      toast.error('Vous devez avoir au moins un fichier');
      return;
    }
    
    if (window.confirm('Supprimer ce fichier ?')) {
      setProject(prev => ({
        ...prev,
        files: prev.files.filter((_, i) => i !== index)
      }));
      
      // Adjust currentFileIndex if needed
      if (currentFileIndex >= index && currentFileIndex > 0) {
        setCurrentFileIndex(currentFileIndex - 1);
      }
    }
  };

  // BUG 2 FIX: Real ZIP download with JSZip instead of concatenated .txt
  const downloadProject = async () => {
    try {
      const zip = new JSZip();
      
      // Add each file to the ZIP
      project.files.forEach(file => {
        zip.file(file.name, file.content);
      });
      
      // Generate ZIP blob
      const blob = await zip.generateAsync({ 
        type: 'blob',
        compression: 'DEFLATE',
        compressionOptions: { level: 9 }
      });
      
      // Create download link
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${project.name.replace(/[^a-z0-9]/gi, '_')}.zip`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      toast.success(`Projet téléchargé (${project.files.length} fichiers)`);
    } catch (error) {
      console.error('Error creating ZIP:', error);
      toast.error('Erreur lors de la création du ZIP');
    }
  };

  const copyCode = async () => {
    try {
      await navigator.clipboard.writeText(project.files[currentFileIndex]?.content || '');
      setCopied(true);
      toast.success('Code copié');
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      toast.error('Erreur lors de la copie');
    }
  };

  // Render preview panel based on project type
  const renderPreviewPanel = (showToggleButton = false) => {
    const isFullStack = isFullStackProject();
    
    return (
      <div className="h-full flex flex-col bg-white">
        <div className="p-2 border-b border-gray-200 bg-gray-50 flex justify-between items-center flex-shrink-0">
          <div className="flex items-center gap-2">
            <Eye className="w-4 h-4 text-blue-500" />
            <span className="text-sm font-medium text-gray-700">
              {isFullStack ? 'Aperçu Full-Stack' : 'Aperçu'}
            </span>
            {isFullStack && (
              <span className="text-xs bg-blue-100 text-blue-600 px-2 py-0.5 rounded-full">
                Next.js
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            {/* Show editor toggle button when editor is hidden */}
            {showToggleButton && (
              <Button
                data-testid="show-editor-button"
                variant="ghost"
                size="sm"
                onClick={() => setShowEditor(true)}
                className="text-gray-600 hover:text-gray-900"
                title="Afficher l'éditeur"
              >
                <PanelLeftOpen className="w-4 h-4" />
              </Button>
            )}
            {/* Show Vercel Preview button for Full-Stack projects */}
            {isFullStack && (
              <>
                {previewUrl ? (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => window.open(previewUrl, '_blank')}
                    className="text-emerald-600 hover:text-emerald-700 hover:bg-emerald-50"
                    title="Ouvrir le preview"
                  >
                    <ExternalLink className="w-4 h-4 mr-1" />
                    Voir Preview
                  </Button>
                ) : (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={generateVercelPreview}
                    disabled={previewLoading || !projectId}
                    className="text-blue-600 hover:text-blue-700 hover:bg-blue-50"
                    title={!projectId ? 'Sauvegardez d\'abord le projet' : 'Déployer un preview sur Vercel'}
                  >
                    {previewLoading ? (
                      <Loader2 className="w-4 h-4 animate-spin mr-1" />
                    ) : (
                      <Rocket className="w-4 h-4 mr-1" />
                    )}
                    Preview Vercel
                  </Button>
                )}
              </>
            )}
            
            {/* Refresh button for simple projects */}
            {!isFullStack && (
              <Button
                data-testid="refresh-preview-button"
                variant="ghost"
                size="sm"
                onClick={updatePreview}
                className="text-gray-600 hover:text-gray-900"
              >
                <Play className="w-4 h-4" />
              </Button>
            )}
          </div>
        </div>
        
        {/* Preview content */}
        <div className="flex-1 overflow-hidden relative">
          {/* Show iframe for simple projects OR Full-Stack info message */}
          <iframe
            ref={iframeRef}
            data-testid="preview-iframe"
            title="Preview"
            className="w-full h-full border-0"
            sandbox="allow-scripts allow-modals"
          />
          
          {/* Overlay with Vercel preview iframe for Full-Stack when URL exists */}
          {isFullStack && previewUrl && (
            <div className="absolute inset-0 bg-white">
              <iframe
                src={previewUrl}
                title="Vercel Preview"
                className="w-full h-full border-0"
                sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
              />
            </div>
          )}
        </div>
      </div>
    );
  };

  // Render file tabs bar - always visible
  const renderFileTabs = () => (
    <div className="border-b border-white/5 bg-black/20 flex items-center gap-2 px-4 py-2 overflow-x-auto flex-shrink-0">
      {project.files.map((file, idx) => (
        <div
          key={file.name}
          data-testid={`file-tab-${idx}`}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-md cursor-pointer transition-colors flex-shrink-0 ${
            currentFileIndex === idx
              ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
              : 'bg-white/5 text-gray-400 hover:bg-white/10'
          }`}
          onClick={() => setCurrentFileIndex(idx)}
        >
          <FileCode className="w-4 h-4 flex-shrink-0" />
          <span className="text-sm font-medium whitespace-nowrap">{file.name}</span>
          {project.files.length > 1 && (
            <button
              data-testid={`delete-file-${idx}`}
              onClick={(e) => {
                e.stopPropagation();
                deleteFile(idx);
              }}
              className="text-gray-500 hover:text-red-400 flex-shrink-0"
            >
              <X className="w-3 h-3" />
            </button>
          )}
        </div>
      ))}
      <Button
        data-testid="add-file-button"
        variant="ghost"
        size="sm"
        onClick={addNewFile}
        className="text-gray-400 hover:text-white flex-shrink-0"
      >
        <Plus className="w-4 h-4" />
      </Button>
    </div>
  );

  return (
    <div className="h-screen flex flex-col bg-[#0a0a0b]">
      {/* Header */}
      <header className="border-b border-white/5 bg-black/40 backdrop-blur-xl z-50 flex-shrink-0">
        <div className="px-6 py-3 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <Button
              data-testid="back-to-dashboard"
              variant="ghost"
              size="sm"
              onClick={() => navigate('/dashboard')}
              className="text-gray-400 hover:text-white"
            >
              <ArrowLeft className="w-4 h-4" />
            </Button>
            <Input
              data-testid="project-name-input"
              value={project.name}
              onChange={(e) => setProject({ ...project, name: e.target.value })}
              className="bg-transparent border-none text-lg font-semibold focus-visible:ring-0 w-64"
            />
            {isFullStackProject() && (
              <span className="text-xs bg-gradient-to-r from-emerald-500 to-blue-500 text-white px-2 py-1 rounded-full">
                Full-Stack
              </span>
            )}
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              data-testid="download-project-button"
              variant="ghost"
              size="sm"
              onClick={downloadProject}
              className="text-gray-400 hover:text-white"
              title="Télécharger le projet en ZIP"
            >
              <Download className="w-4 h-4" />
            </Button>
            
            <Dialog open={showGithubDialog} onOpenChange={setShowGithubDialog}>
              <DialogTrigger asChild>
                <Button
                  data-testid="github-export-button"
                  variant="ghost"
                  size="sm"
                  className="text-purple-400 hover:text-purple-300 hover:bg-purple-500/10"
                >
                  <Github className="w-4 h-4 mr-2" />
                  GitHub
                </Button>
              </DialogTrigger>
              <DialogContent className="bg-[#1a1a1c] border-white/10">
                <DialogHeader>
                  <DialogTitle>Exporter vers GitHub</DialogTitle>
                  <DialogDescription>
                    Créez un nouveau repository GitHub avec votre projet
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label>Nom du repository</Label>
                    <Input
                      data-testid="github-repo-name-input"
                      value={githubRepoName}
                      onChange={(e) => setGithubRepoName(e.target.value)}
                      placeholder="mon-super-projet"
                      className="bg-white/5 border-white/10 mt-2"
                    />
                  </div>
                  <div>
                    <Label>GitHub Token</Label>
                    <Input
                      data-testid="github-token-dialog-input"
                      type="password"
                      value={githubToken}
                      onChange={(e) => setGithubToken(e.target.value)}
                      placeholder="ghp_..."
                      className="bg-white/5 border-white/10 mt-2"
                    />
                  </div>
                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      id="private-repo"
                      checked={isPrivateRepo}
                      onChange={(e) => setIsPrivateRepo(e.target.checked)}
                    />
                    <Label htmlFor="private-repo">Repository privé</Label>
                  </div>
                  <Button
                    data-testid="confirm-github-export"
                    onClick={exportToGithub}
                    disabled={loading}
                    className="w-full bg-gradient-to-r from-purple-500 to-purple-600"
                  >
                    {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Github className="w-4 h-4 mr-2" />}
                    Exporter
                  </Button>
                </div>
              </DialogContent>
            </Dialog>

            <Dialog open={showVercelDialog} onOpenChange={setShowVercelDialog}>
              <DialogTrigger asChild>
                <Button
                  data-testid="vercel-deploy-button"
                  variant="ghost"
                  size="sm"
                  className="text-blue-400 hover:text-blue-300 hover:bg-blue-500/10"
                >
                  <Globe className="w-4 h-4 mr-2" />
                  Vercel
                </Button>
              </DialogTrigger>
              <DialogContent className="bg-[#1a1a1c] border-white/10">
                <DialogHeader>
                  <DialogTitle>Déployer sur Vercel</DialogTitle>
                  <DialogDescription>
                    Déployez votre projet sur Vercel en production
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label>Nom du projet</Label>
                    <Input
                      data-testid="vercel-project-name-input"
                      value={vercelProjectName}
                      onChange={(e) => setVercelProjectName(e.target.value)}
                      placeholder="mon-super-projet"
                      className="bg-white/5 border-white/10 mt-2"
                    />
                  </div>
                  <div>
                    <Label>Vercel Token</Label>
                    <Input
                      data-testid="vercel-token-dialog-input"
                      type="password"
                      value={vercelToken}
                      onChange={(e) => setVercelToken(e.target.value)}
                      placeholder="..."
                      className="bg-white/5 border-white/10 mt-2"
                    />
                  </div>
                  <Button
                    data-testid="confirm-vercel-deploy"
                    onClick={deployToVercel}
                    disabled={loading}
                    className="w-full bg-gradient-to-r from-blue-500 to-blue-600"
                  >
                    {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Globe className="w-4 h-4 mr-2" />}
                    Déployer
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
            
            <Button
              data-testid="save-project-button"
              onClick={saveProject}
              disabled={loading}
              className="bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Save className="w-4 h-4 mr-2" />}
              Sauvegarder
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        <SplitPane split="vertical" minSize={250} maxSize={600} defaultSize={320}>
          {/* Chat Panel */}
          <div className="h-full border-r border-white/5 bg-black/20 flex flex-col">
            <div className="p-4 border-b border-white/5 flex-shrink-0">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold flex items-center gap-2">
                  <MessageSquare className="w-5 h-5 text-emerald-400" />
                  Assistant IA
                </h2>
                {/* BUG 4 FIX: Clear conversation button */}
                {chatMessages.length > 0 && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={clearConversation}
                    className="text-gray-400 hover:text-red-400"
                    title="Effacer la conversation"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                )}
              </div>
              
              {/* Agentic Mode Toggle */}
              <div className="mt-3 bg-white/5 rounded-lg p-3 border border-white/10">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Bot className="w-4 h-4 text-emerald-400" />
                    <span className="text-sm font-medium">Mode Agentique</span>
                  </div>
                  <button
                    onClick={() => setUseAgenticMode(!useAgenticMode)}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      useAgenticMode ? 'bg-emerald-500' : 'bg-gray-600'
                    }`}
                    data-testid="agentic-mode-toggle"
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        useAgenticMode ? 'translate-x-6' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>
                <p className="text-xs text-gray-400">
                  {useAgenticMode ? (
                    <>
                      <Sparkles className="w-3 h-3 inline mr-1" />
                      Système multi-agents : planification, génération, test et amélioration automatique
                    </>
                  ) : (
                    'Génération simple et rapide'
                  )}
                </p>
              </div>
              
              {/* NEW: Fullstack Mode Toggle */}
              {useAgenticMode && (
                <div className="mt-2 bg-gradient-to-r from-blue-500/10 to-purple-500/10 rounded-lg p-3 border border-blue-500/20">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Layers className="w-4 h-4 text-blue-400" />
                      <span className="text-sm font-medium">Mode Full-Stack</span>
                    </div>
                    <button
                      onClick={() => setUseFullstackMode(!useFullstackMode)}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                        useFullstackMode ? 'bg-blue-500' : 'bg-gray-600'
                      }`}
                      data-testid="fullstack-mode-toggle"
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                          useFullstackMode ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>
                  <p className="text-xs text-gray-400">
                    {useFullstackMode ? (
                      <>
                        <Rocket className="w-3 h-3 inline mr-1" />
                        Next.js 14+ • TypeScript • Tailwind • Supabase • shadcn/ui
                      </>
                    ) : (
                      'HTML/CSS/JS simple (aperçu instantané)'
                    )}
                  </p>
                </div>
              )}
              
              <div className="mt-3 space-y-2">
                <Select value={selectedModel} onValueChange={setSelectedModel}>
                  <SelectTrigger data-testid="model-selector" className="bg-white/5 border-white/10">
                    <SelectValue placeholder="Modèle" />
                  </SelectTrigger>
                  <SelectContent className="bg-[#1a1a1c] border-white/10">
                    {availableModels.length > 0 ? (
                      availableModels.slice(0, 20).map((model) => (
                        <SelectItem key={model.id} value={model.id}>
                          {model.name || model.id}
                        </SelectItem>
                      ))
                    ) : (
                      <>
                        <SelectItem value="openai/gpt-4o">GPT-4o</SelectItem>
                        <SelectItem value="anthropic/claude-3.5-sonnet">Claude 3.5 Sonnet</SelectItem>
                        <SelectItem value="google/gemini-2.0-flash-exp">Gemini 2.0 Flash</SelectItem>
                      </>
                    )}
                  </SelectContent>
                </Select>
                
                {!apiKey && (
                  <Button
                    data-testid="configure-api-key-button"
                    variant="outline"
                    size="sm"
                    onClick={() => navigate('/settings')}
                    className="w-full border-emerald-500/30 text-emerald-400"
                  >
                    <Settings className="w-4 h-4 mr-2" />
                    Configurer la clé API
                  </Button>
                )}
              </div>
            </div>
            
            <div className="flex-1 overflow-y-auto p-4 space-y-4" data-testid="chat-messages-container">
              {chatMessages.length === 0 ? (
                <div className="text-center text-gray-500 py-8">
                  <MessageSquare className="w-12 h-12 mx-auto mb-4 opacity-30" />
                  <p className="text-sm">Commencez une conversation</p>
                  <p className="text-xs mt-2">Décrivez ce que vous voulez créer</p>
                </div>
              ) : (
                chatMessages.map((msg, idx) => (
                  <div
                    key={idx}
                    data-testid={`chat-message-${idx}`}
                    className={`p-3 rounded-lg ${
                      msg.role === 'user'
                        ? 'bg-emerald-500/10 border border-emerald-500/20 ml-4'
                        : 'bg-white/5 border border-white/10 mr-4'
                    }`}
                  >
                    <p className="text-xs text-gray-400 mb-1">
                      {msg.role === 'user' ? 'Vous' : 'Assistant'}
                    </p>
                    <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                  </div>
                ))
              )}
              {generating && (
                <div className="bg-white/5 border border-white/10 p-3 rounded-lg mr-4">
                  <div className="flex items-center gap-2">
                    <Loader2 className="w-4 h-4 animate-spin text-emerald-400" />
                    <p className="text-sm text-gray-400">Génération en cours...</p>
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>
            
            <div className="p-4 border-t border-white/5 flex-shrink-0">
              <div className="flex gap-2">
                <Textarea
                  data-testid="chat-input"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      sendMessage();
                    }
                  }}
                  placeholder={useFullstackMode 
                    ? "Décrivez votre app SaaS, e-commerce, dashboard..." 
                    : "Décrivez ce que vous voulez créer..."
                  }
                  className="bg-white/5 border-white/10 resize-none"
                  rows={3}
                />
                <Button
                  data-testid="send-message-button"
                  onClick={sendMessage}
                  disabled={generating || !apiKey}
                  className={`self-end ${
                    useFullstackMode
                      ? 'bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600'
                      : useAgenticMode 
                        ? 'bg-gradient-to-r from-emerald-500 to-blue-500 hover:from-emerald-600 hover:to-blue-600' 
                        : 'bg-emerald-500 hover:bg-emerald-600'
                  }`}
                  title={useFullstackMode ? 'Générer projet Full-Stack' : useAgenticMode ? 'Générer avec système agentique' : 'Générer normalement'}
                >
                  {useFullstackMode ? <Layers className="w-4 h-4" /> : useAgenticMode ? <Bot className="w-4 h-4" /> : <Send className="w-4 h-4" />}
                </Button>
              </div>
            </div>
          </div>

          {/* Code Editor & Preview */}
          <div className="h-full flex flex-col">
            {/* File Tabs - ALWAYS VISIBLE (moved outside of showEditor condition) */}
            {renderFileTabs()}

            {/* Editor & Preview Split */}
            <div className="flex-1 overflow-hidden">
              {showEditor ? (
                <SplitPane split="vertical" minSize={300} defaultSize="50%">
                  {/* Code Editor */}
                  <div className="h-full flex flex-col border-r border-white/5">
                    <div className="p-2 border-b border-white/5 bg-black/20 flex justify-between items-center flex-shrink-0">
                      <div className="flex items-center gap-2">
                        <Code2 className="w-4 h-4 text-emerald-400" />
                        <span className="text-sm font-medium">Éditeur</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button
                          data-testid="toggle-editor-button"
                          variant="ghost"
                          size="sm"
                          onClick={() => setShowEditor(false)}
                          className="text-gray-400 hover:text-white"
                          title="Masquer l'éditeur"
                        >
                          <PanelLeftClose className="w-4 h-4" />
                        </Button>
                        <Button
                          data-testid="copy-code-button"
                          variant="ghost"
                          size="sm"
                          onClick={copyCode}
                          className="text-gray-400 hover:text-white"
                        >
                          {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                        </Button>
                      </div>
                    </div>
                    <div className="flex-1">
                      <Editor
                        height="100%"
                        language={project.files[currentFileIndex]?.language || 'plaintext'}
                        value={project.files[currentFileIndex]?.content || ''}
                        onChange={(value) => {
                          const updatedFiles = [...project.files];
                          if (updatedFiles[currentFileIndex]) {
                            updatedFiles[currentFileIndex].content = value || '';
                            setProject({ ...project, files: updatedFiles });
                          }
                        }}
                        theme="vs-dark"
                        options={{
                          minimap: { enabled: false },
                          fontSize: 14,
                          lineNumbers: 'on',
                          scrollBeyondLastLine: false,
                          automaticLayout: true,
                          tabSize: 2,
                        }}
                      />
                    </div>
                  </div>

                  {/* Preview */}
                  {renderPreviewPanel()}
                </SplitPane>
              ) : (
              /* Preview only when editor is hidden - use renderPreviewPanel with toggle button */
              renderPreviewPanel(true)
            )}
            </div>
          </div>
        </SplitPane>
      </div>
    </div>
  );
};

export default EditorPage;
