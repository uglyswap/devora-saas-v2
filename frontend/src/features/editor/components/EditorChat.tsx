/**
 * Composant Chat IA avec assistant
 */

import React, { useRef, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  MessageSquare,
  Send,
  Settings,
  Trash2,
  Bot,
  Sparkles,
  Layers,
  Rocket,
  Loader2,
} from 'lucide-react';
import { Button } from '../../../components/ui/button';
import { Textarea } from '../../../components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../../../components/ui/select';
import { useEditorStore } from '../hooks/useEditorState';
import { useAIGeneration } from '../hooks/useAIGeneration';

export const EditorChat: React.FC = () => {
  const navigate = useNavigate();
  const chatEndRef = useRef<HTMLDivElement>(null);

  const [inputMessage, setInputMessage] = useState('');

  const {
    chatMessages,
    generating,
    apiKey,
    selectedModel,
    availableModels,
    useAgenticMode,
    useFullstackMode,
    setSelectedModel,
    setUseAgenticMode,
    setUseFullstackMode,
    clearChatMessages,
  } = useEditorStore();

  const { generateCode, fetchModels } = useAIGeneration();

  // Auto-scroll au dernier message
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  // Charger les modèles disponibles
  useEffect(() => {
    if (apiKey) {
      fetchModels();
    }
  }, [apiKey, fetchModels]);

  const handleSendMessage = () => {
    if (!inputMessage.trim()) return;
    generateCode(inputMessage);
    setInputMessage('');
  };

  const handleClearConversation = () => {
    if (
      window.confirm(
        "Voulez-vous vraiment effacer l'historique de conversation ?"
      )
    ) {
      clearChatMessages();
    }
  };

  return (
    <div className="h-full border-r border-white/5 bg-black/20 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-white/5 flex-shrink-0">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-emerald-400" />
            Assistant IA
          </h2>
          {chatMessages.length > 0 && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleClearConversation}
              className="text-gray-400 hover:text-red-400"
              title="Effacer la conversation"
            >
              <Trash2 className="w-4 h-4" />
            </Button>
          )}
        </div>

        {/* Mode Agentique Toggle */}
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
                Système multi-agents : planification, génération, test et
                amélioration automatique
              </>
            ) : (
              'Génération simple et rapide'
            )}
          </p>
        </div>

        {/* Mode Full-Stack Toggle */}
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

        {/* Sélection du modèle */}
        <div className="mt-3 space-y-2">
          <Select value={selectedModel} onValueChange={setSelectedModel}>
            <SelectTrigger
              data-testid="model-selector"
              className="bg-white/5 border-white/10"
            >
              <SelectValue placeholder="Modèle" />
            </SelectTrigger>
            <SelectContent className="bg-[#1a1a1c] border-white/10 max-h-80 overflow-y-auto">
              {availableModels.length > 0 ? (
                availableModels.map((model) => (
                  <SelectItem key={model.id} value={model.id}>
                    {model.name || model.id}
                  </SelectItem>
                ))
              ) : (
                <>
                  <SelectItem value="openai/gpt-4o">GPT-4o</SelectItem>
                  <SelectItem value="anthropic/claude-3.5-sonnet">
                    Claude 3.5 Sonnet
                  </SelectItem>
                  <SelectItem value="google/gemini-2.0-flash-exp">
                    Gemini 2.0 Flash
                  </SelectItem>
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

      {/* Messages */}
      <div
        className="flex-1 overflow-y-auto p-4 space-y-4"
        data-testid="chat-messages-container"
      >
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

      {/* Input */}
      <div className="p-4 border-t border-white/5 flex-shrink-0">
        <div className="flex gap-2">
          <Textarea
            data-testid="chat-input"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
              }
            }}
            placeholder={
              useFullstackMode
                ? 'Décrivez votre app SaaS, e-commerce, dashboard...'
                : 'Décrivez ce que vous voulez créer...'
            }
            className="bg-white/5 border-white/10 resize-none"
            rows={3}
          />
          <Button
            data-testid="send-message-button"
            onClick={handleSendMessage}
            disabled={generating || !apiKey}
            className={`self-end ${
              useFullstackMode
                ? 'bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600'
                : useAgenticMode
                ? 'bg-gradient-to-r from-emerald-500 to-blue-500 hover:from-emerald-600 hover:to-blue-600'
                : 'bg-emerald-500 hover:bg-emerald-600'
            }`}
            title={
              useFullstackMode
                ? 'Générer projet Full-Stack'
                : useAgenticMode
                ? 'Générer avec système agentique'
                : 'Générer normalement'
            }
          >
            {useFullstackMode ? (
              <Layers className="w-4 h-4" />
            ) : useAgenticMode ? (
              <Bot className="w-4 h-4" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </Button>
        </div>
      </div>
    </div>
  );
};
