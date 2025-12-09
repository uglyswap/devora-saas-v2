/**
 * Composant Toolbar de l'éditeur (header avec actions)
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Save,
  Download,
  Github,
  Globe,
  Loader2,
} from 'lucide-react';
import { Button } from '../../../components/ui/button';
import { Input } from '../../../components/ui/input';
import { Label } from '../../../components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../../../components/ui/dialog';
import { useEditorStore } from '../hooks/useEditorState';
import { useEditorActions } from '../hooks/useEditorActions';
import { useExportDeploy } from '../hooks/useExportDeploy';
import { isFullStackProject } from '../types/editor.types';

export const EditorToolbar: React.FC = () => {
  const navigate = useNavigate();

  const {
    project,
    loading,
    githubToken,
    vercelToken,
    showGithubDialog,
    showVercelDialog,
    updateProjectName,
    setShowGithubDialog,
    setShowVercelDialog,
  } = useEditorStore();

  const { projectId, saveProject, downloadProject } = useEditorActions();
  const { exportToGithub, deployToVercel } = useExportDeploy(projectId);

  // États locaux pour les dialogs
  const [githubRepoName, setGithubRepoName] = useState('');
  const [vercelProjectName, setVercelProjectName] = useState('');
  const [githubTokenInput, setGithubTokenInput] = useState(githubToken);
  const [vercelTokenInput, setVercelTokenInput] = useState(vercelToken);
  const [isPrivateRepo, setIsPrivateRepo] = useState(false);

  const handleGithubExport = () => {
    exportToGithub({
      repoName: githubRepoName,
      githubToken: githubTokenInput,
      isPrivate: isPrivateRepo,
    });
    setShowGithubDialog(false);
  };

  const handleVercelDeploy = () => {
    deployToVercel({
      projectName: vercelProjectName,
      vercelToken: vercelTokenInput,
    });
    setShowVercelDialog(false);
  };

  const isFullStack = isFullStackProject(project.files);

  return (
    <header className="border-b border-white/5 bg-black/40 backdrop-blur-xl z-50 flex-shrink-0">
      <div className="px-6 py-3 flex justify-between items-center">
        {/* Left side */}
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
            onChange={(e) => updateProjectName(e.target.value)}
            className="bg-transparent border-none text-lg font-semibold focus-visible:ring-0 w-64"
          />
          {isFullStack && (
            <span className="text-xs bg-gradient-to-r from-emerald-500 to-blue-500 text-white px-2 py-1 rounded-full">
              Full-Stack
            </span>
          )}
        </div>

        {/* Right side */}
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

          {/* GitHub Export Dialog */}
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
                    value={githubTokenInput}
                    onChange={(e) => setGithubTokenInput(e.target.value)}
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
                  onClick={handleGithubExport}
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-purple-500 to-purple-600"
                >
                  {loading ? (
                    <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  ) : (
                    <Github className="w-4 h-4 mr-2" />
                  )}
                  Exporter
                </Button>
              </div>
            </DialogContent>
          </Dialog>

          {/* Vercel Deploy Dialog */}
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
                    value={vercelTokenInput}
                    onChange={(e) => setVercelTokenInput(e.target.value)}
                    placeholder="..."
                    className="bg-white/5 border-white/10 mt-2"
                  />
                </div>
                <Button
                  data-testid="confirm-vercel-deploy"
                  onClick={handleVercelDeploy}
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-blue-500 to-blue-600"
                >
                  {loading ? (
                    <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  ) : (
                    <Globe className="w-4 h-4 mr-2" />
                  )}
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
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin mr-2" />
            ) : (
              <Save className="w-4 h-4 mr-2" />
            )}
            Sauvegarder
          </Button>
        </div>
      </div>
    </header>
  );
};
