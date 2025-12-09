/**
 * Hook pour les actions de l'éditeur (save, load, etc.)
 */

import { useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';
import JSZip from 'jszip';
import { useEditorStore } from './useEditorState';
import { EditorProject } from '../types/editor.types';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

/**
 * Hook pour gérer les actions CRUD sur le projet
 */
export function useEditorActions() {
  const navigate = useNavigate();
  const { projectId } = useParams<{ projectId: string }>();

  const {
    project,
    chatMessages,
    setProject,
    setLoading,
    setApiKey,
    setGithubToken,
    setVercelToken,
  } = useEditorStore();

  /**
   * Charger un projet depuis l'API
   */
  const loadProject = useCallback(async () => {
    if (!projectId) return;

    try {
      const response = await axios.get(`${API}/projects/${projectId}`);
      const loadedProject: EditorProject = response.data;
      setProject(loadedProject);
    } catch (error) {
      console.error('Error loading project:', error);
      toast.error('Erreur lors du chargement du projet');
    }
  }, [projectId, setProject]);

  /**
   * Charger les paramètres (API keys, tokens)
   */
  const loadSettings = useCallback(async () => {
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
  }, [setApiKey, setGithubToken, setVercelToken]);

  /**
   * Sauvegarder le projet
   */
  const saveProject = useCallback(async () => {
    setLoading(true);
    try {
      const projectToSave: EditorProject = {
        ...project,
        conversation_history: chatMessages,
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
  }, [project, chatMessages, projectId, navigate, setLoading]);

  /**
   * Télécharger le projet en ZIP
   */
  const downloadProject = useCallback(async () => {
    try {
      const zip = new JSZip();

      // Ajouter chaque fichier au ZIP
      project.files.forEach((file) => {
        zip.file(file.name, file.content);
      });

      // Générer le ZIP
      const blob = await zip.generateAsync({
        type: 'blob',
        compression: 'DEFLATE',
        compressionOptions: { level: 9 },
      });

      // Télécharger
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
  }, [project]);

  /**
   * Copier le code du fichier courant
   */
  const copyCode = useCallback(
    async (fileContent: string) => {
      try {
        await navigator.clipboard.writeText(fileContent);
        toast.success('Code copié');
        return true;
      } catch (error) {
        toast.error('Erreur lors de la copie');
        return false;
      }
    },
    []
  );

  return {
    projectId,
    loadProject,
    loadSettings,
    saveProject,
    downloadProject,
    copyCode,
  };
}
