/**
 * Hook pour la génération IA (Agentique et OpenRouter)
 */

import { useCallback } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { useEditorStore, selectApiConfig } from './useEditorState';
import {
  AgenticGenerationResponse,
  OpenRouterGenerationResponse,
  ChatMessage,
} from '../types/editor.types';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

/**
 * Hook pour gérer la génération de code avec l'IA
 */
export function useAIGeneration() {
  const {
    project,
    chatMessages,
    addChatMessage,
    setGenerating,
    setProject,
    setPreviewUrl,
  } = useEditorStore();

  const apiConfig = useEditorStore(selectApiConfig);

  /**
   * Parser le code depuis la réponse de l'IA (pour mode standard)
   */
  const parseAndApplyCode = useCallback(
    (response: string) => {
      const codeBlockRegex = /```(\w+)\n?(?://\s*filename:\s*(.+)\n)?([\s\S]*?)```/g;
      let match;
      const newFiles = [];

      while ((match = codeBlockRegex.exec(response)) !== null) {
        const [, language, filename, code] = match;
        const cleanCode = code.trim();

        if (filename) {
          newFiles.push({
            name: filename.trim(),
            content: cleanCode,
            language: language || 'plaintext',
          });
        } else {
          const ext =
            language === 'html'
              ? 'html'
              : language === 'css'
              ? 'css'
              : language === 'javascript'
              ? 'js'
              : 'txt';
          const name = `file.${ext}`;
          newFiles.push({
            name,
            content: cleanCode,
            language: language || 'plaintext',
          });
        }
      }

      if (newFiles.length > 0) {
        setProject({
          ...project,
          files: [
            ...project.files.map((file) => {
              const newFile = newFiles.find((f) => f.name === file.name);
              return newFile || file;
            }),
            ...newFiles.filter(
              (newFile) => !project.files.some((f) => f.name === newFile.name)
            ),
          ],
        });

        setPreviewUrl(null);
        toast.success(`${newFiles.length} fichier(s) mis à jour`);
      }
    },
    [project, setProject, setPreviewUrl]
  );

  /**
   * Générer du code avec l'IA
   */
  const generateCode = useCallback(
    async (message: string) => {
      if (!message.trim() || !apiConfig.apiKey) {
        toast.error('Veuillez entrer un message et configurer votre clé API');
        return;
      }

      const userMessage: ChatMessage = { role: 'user', content: message };
      addChatMessage(userMessage);
      setGenerating(true);

      try {
        if (apiConfig.useAgenticMode) {
          // Mode Agentique ou Full-Stack
          const endpoint = apiConfig.useFullstackMode
            ? `${API}/generate/fullstack`
            : `${API}/generate/agentic`;

          const modeLabel = apiConfig.useFullstackMode
            ? 'Full-Stack Next.js'
            : 'Agentique';

          const agenticMessage: ChatMessage = {
            role: 'assistant',
            content:
              `🤖 **Système ${modeLabel} Activé**\n\n` +
              '🔄 **Phase 1 : Planification**\nAnalyse des exigences...',
          };
          addChatMessage(agenticMessage);

          const response = await axios.post<AgenticGenerationResponse>(endpoint, {
            message,
            model: apiConfig.selectedModel,
            api_key: apiConfig.apiKey,
            current_files: project.files,
            conversation_history: chatMessages.slice(-10),
            project_type: apiConfig.useFullstackMode ? 'saas' : undefined,
          });

          if (response.data.success) {
            // Construire le message de progression
            let progressMsg = `🤖 **Système ${modeLabel} - Résultat**\n\n`;

            const events = response.data.progress_events || [];
            events.forEach((evt) => {
              const emoji =
                {
                  planning: '📋',
                  plan_complete: '✅',
                  coding: '💻',
                  code_complete: '✅',
                  testing: '🧪',
                  test_complete: '✅',
                  reviewing: '🔍',
                  review_complete: '✅',
                  fixing: '🔧',
                  complete: '🎉',
                }[evt.event] || '•';

              progressMsg += `${emoji} ${evt.data.message}\n`;
            });

            progressMsg += `\n✨ Génération terminée en ${response.data.iterations} itération(s) !`;
            progressMsg += `\n📦 ${response.data.files?.length || 0} fichier(s) généré(s).`;

            if (apiConfig.useFullstackMode && response.data.stack) {
              progressMsg += `\n\n🛠️ **Stack:** ${response.data.stack.frontend?.join(', ')}`;
            }

            // Mettre à jour le dernier message
            const lastMessageIndex = chatMessages.length;
            const updatedMessages = [...chatMessages];
            updatedMessages[lastMessageIndex] = {
              role: 'assistant',
              content: progressMsg,
            };

            // Appliquer les fichiers générés
            if (response.data.files && response.data.files.length > 0) {
              const generatedFiles = response.data.files;

              let updatedFiles = [...project.files];

              // Pour les projets Full-Stack, supprimer les fichiers de démarrage par défaut
              if (apiConfig.useFullstackMode) {
                const defaultFiles = ['index.html', 'styles.css', 'script.js'];
                updatedFiles = updatedFiles.filter(
                  (f) => !defaultFiles.includes(f.name)
                );
              }

              generatedFiles.forEach((newFile) => {
                const existingIndex = updatedFiles.findIndex(
                  (f) => f.name === newFile.name
                );
                if (existingIndex >= 0) {
                  updatedFiles[existingIndex] = newFile;
                } else {
                  updatedFiles.push(newFile);
                }
              });

              setProject({ ...project, files: updatedFiles });
              setPreviewUrl(null);

              toast.success(
                `${response.data.files.length} fichier(s) généré(s) par le système ${modeLabel.toLowerCase()} !`
              );
            }
          }
        } else {
          // Mode OpenRouter standard
          const conversationHistory = chatMessages.map((msg) => ({
            role: msg.role,
            content: msg.content,
          }));

          const response = await axios.post<OpenRouterGenerationResponse>(
            `${API}/generate/openrouter`,
            {
              message,
              model: apiConfig.selectedModel,
              api_key: apiConfig.apiKey,
              conversation_history: conversationHistory,
            }
          );

          const assistantMessage: ChatMessage = {
            role: 'assistant',
            content: response.data.response,
          };
          addChatMessage(assistantMessage);

          // Parser et appliquer le code
          parseAndApplyCode(response.data.response);
        }
      } catch (error) {
        console.error('Error generating code:', error);
        toast.error('Erreur lors de la génération');
        addChatMessage({
          role: 'assistant',
          content:
            'Désolé, une erreur est survenue. Vérifiez votre clé API et réessayez.',
        });
      } finally {
        setGenerating(false);
      }
    },
    [
      apiConfig,
      project,
      chatMessages,
      addChatMessage,
      setGenerating,
      setProject,
      setPreviewUrl,
      parseAndApplyCode,
    ]
  );

  /**
   * Récupérer les modèles disponibles depuis OpenRouter
   */
  const fetchModels = useCallback(async () => {
    if (!apiConfig.apiKey) return;

    try {
      const response = await axios.get(
        `${API}/openrouter/models?api_key=${apiConfig.apiKey}`
      );
      const models = response.data.data || [];
      useEditorStore.getState().setAvailableModels(models);
    } catch (error) {
      console.error('Error fetching models:', error);
    }
  }, [apiConfig.apiKey]);

  return {
    generateCode,
    fetchModels,
  };
}
