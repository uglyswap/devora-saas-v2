/**
 * useTemplateDownload Hook - Gère le téléchargement de templates
 * Enregistre le download et déclenche le téléchargement du fichier
 */
import { useState } from 'react';
import axios from 'axios';
import { DownloadResponse } from '../types/marketplace.types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const useTemplateDownload = () => {
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);

  /**
   * Télécharge un template
   * 1. Enregistre le download dans la DB (incrémente le compteur)
   * 2. Récupère l'URL du fichier
   * 3. Déclenche le téléchargement navigateur
   */
  const downloadTemplate = async (
    templateId: string,
    templateName: string
  ): Promise<boolean> => {
    setDownloading(true);
    setError(null);
    setProgress(0);

    try {
      // Enregistrer le download et récupérer l'URL
      const response = await axios.post<DownloadResponse>(
        `${API_BASE_URL}/api/marketplace/templates/${templateId}/download`,
        {},
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          },
        }
      );

      const { download_url } = response.data;

      // Télécharger le fichier avec progress tracking
      const fileResponse = await axios.get(download_url, {
        responseType: 'blob',
        onDownloadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            setProgress(percentCompleted);
          }
        },
      });

      // Créer un lien de téléchargement et le déclencher
      const blob = new Blob([fileResponse.data]);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${templateName.toLowerCase().replace(/\s+/g, '-')}.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      setProgress(100);
      return true;
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to download template');
      console.error('Error downloading template:', err);
      return false;
    } finally {
      setDownloading(false);
    }
  };

  const reset = () => {
    setError(null);
    setProgress(0);
  };

  return {
    downloadTemplate,
    downloading,
    error,
    progress,
    reset,
  };
};
