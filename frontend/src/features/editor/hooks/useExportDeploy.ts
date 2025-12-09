/**
 * Hook pour l'export et le déploiement (GitHub, Vercel)
 */

import { useCallback } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';
import { useEditorStore } from './useEditorState';
import {
  GithubExportOptions,
  VercelDeployOptions,
} from '../types/editor.types';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

/**
 * Hook pour gérer l'export et le déploiement
 */
export function useExportDeploy(projectId?: string) {
  const navigate = useNavigate();

  const {
    project,
    githubToken,
    vercelToken,
    setLoading,
    setPreviewLoading,
    setPreviewUrl,
    setProject,
  } = useEditorStore();

  /**
   * Exporter vers GitHub
   */
  const exportToGithub = useCallback(
    async (options: GithubExportOptions) => {
      if (!options.repoName || !options.githubToken) {
        toast.error('Veuillez remplir tous les champs');
        return;
      }

      setLoading(true);
      try {
        const response = await axios.post(`${API}/github/export`, {
          project_id: projectId || project.id,
          repo_name: options.repoName,
          github_token: options.githubToken,
          private: options.isPrivate,
        });

        toast.success('Projet exporté sur GitHub !');
        window.open(response.data.repo_url, '_blank');
      } catch (error: any) {
        console.error('Error exporting to GitHub:', error);
        toast.error(
          error.response?.data?.detail || "Erreur lors de l'export"
        );
      } finally {
        setLoading(false);
      }
    },
    [projectId, project.id, setLoading]
  );

  /**
   * Déployer sur Vercel (production)
   */
  const deployToVercel = useCallback(
    async (options: VercelDeployOptions) => {
      if (!options.projectName || !options.vercelToken) {
        toast.error('Veuillez remplir tous les champs');
        return;
      }

      setLoading(true);
      try {
        const response = await axios.post(`${API}/vercel/deploy`, {
          project_id: projectId || project.id,
          vercel_token: options.vercelToken,
          project_name: options.projectName,
        });

        toast.success('Projet déployé sur Vercel !');
        window.open(response.data.url, '_blank');
      } catch (error: any) {
        console.error('Error deploying to Vercel:', error);
        toast.error(
          error.response?.data?.detail || 'Erreur lors du déploiement'
        );
      } finally {
        setLoading(false);
      }
    },
    [projectId, project.id, setLoading]
  );

  /**
   * Générer un preview Vercel pour les projets Full-Stack
   */
  const generateVercelPreview = useCallback(async () => {
    if (!vercelToken) {
      toast.error('Veuillez configurer votre token Vercel dans les paramètres');
      navigate('/settings');
      return;
    }

    if (!projectId) {
      toast.error("Veuillez d'abord sauvegarder le projet");
      return;
    }

    setPreviewLoading(true);

    try {
      const previewName = `${project.name.toLowerCase().replace(/[^a-z0-9]/g, '-')}-preview-${Date.now()}`;

      const response = await axios.post(`${API}/vercel/deploy`, {
        project_id: projectId,
        vercel_token: vercelToken,
        project_name: previewName,
      });

      if (response.data.success) {
        setPreviewUrl(response.data.url);
        toast.success('Preview déployé sur Vercel !');

        // Mettre à jour le projet avec l'URL du preview
        setProject({ ...project, vercel_url: response.data.url });
      }
    } catch (error: any) {
      console.error('Error creating Vercel preview:', error);
      toast.error(
        error.response?.data?.detail || 'Erreur lors du déploiement preview'
      );
    } finally {
      setPreviewLoading(false);
    }
  }, [
    vercelToken,
    projectId,
    project,
    setPreviewLoading,
    setPreviewUrl,
    setProject,
    navigate,
  ]);

  return {
    exportToGithub,
    deployToVercel,
    generateVercelPreview,
  };
}
