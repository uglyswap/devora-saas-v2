import React, { useState, useRef, useEffect } from "react";
import { Bot, Send, Sparkles, Lightbulb, Code, Palette, Database, Rocket, Loader2, User, Wand2 } from "lucide-react";
import { Button } from "../ui/button";
import { Textarea } from "../ui/textarea";

const QUICK_PROMPTS = [
  { icon: Palette, text: "Ameliore le design", prompt: "Ameliore le design de mon application avec un style moderne et professionnel" },
  { icon: Code, text: "Ajoute une feature", prompt: "Ajoute une nouvelle fonctionnalite a mon application" },
  { icon: Database, text: "Connecte une BDD", prompt: "Connecte mon application a une base de donnees Supabase" },
  { icon: Rocket, text: "Optimise perf", prompt: "Optimise les performances de mon application" }
];

const SmartAI = ({ onGenerate, projectFiles = [], isGenerating = false }) => {
  const [message, setMessage] = useState("");
  const [conversation, setConversation] = useState([
    { role: "assistant", content: "Salut! Je suis ton assistant IA. Decris-moi ton projet ou choisis une action rapide ci-dessous. Je peux creer des applications completes, des landing pages, des dashboards, ou nimporte quelle interface web!" }
  ]);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [conversation]);

  const handleSend = async () => {
    if (!message.trim() || isGenerating) return;
    
    const userMessage = { role: "user", content: message };
    setConversation(prev => [...prev, userMessage]);
    setMessage("");

    if (onGenerate) {
      setConversation(prev => [...prev, { role: "assistant", content: "thinking", isThinking: true }]);
      
      try {
        await onGenerate(message);
        setConversation(prev => {
          const filtered = prev.filter(m => !m.isThinking);
          return [...filtered, { role: "assistant", content: "Jai genere le code! Tu peux voir les modifications dans lediteur et lapercu." }];
        });
      } catch (error) {
        setConversation(prev => {
          const filtered = prev.filter(m => !m.isThinking);
          return [...filtered, { role: "assistant", content: "Oups! Une erreur est survenue. Reessaie ou reformule ta demande." }];
        });
      }
    }
  };

  const handleQuickPrompt = (prompt) => {
    setMessage(prompt);
  };

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-gray-900 to-gray-800">
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl">
            <Bot className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="font-bold text-white">Assistant IA</h3>
            <p className="text-xs text-gray-400">Powered by GPT-4 Vision</p>
          </div>
          <div className="ml-auto flex items-center gap-1">
            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
            <span className="text-xs text-green-400">En ligne</span>
          </div>
        </div>
      </div>

      <div className="p-3 border-b border-gray-700 bg-gray-800/50">
        <div className="flex items-center gap-2 overflow-x-auto pb-2">
          <Lightbulb className="w-4 h-4 text-yellow-500 flex-shrink-0" />
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
        {conversation.map((msg, i) => (
          <div key={i} className={"flex gap-3 " + (msg.role === "user" ? "flex-row-reverse" : "")}>
            <div className={"w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 " + 
              (msg.role === "user" ? "bg-blue-600" : "bg-gradient-to-r from-purple-500 to-pink-500")}>
              {msg.role === "user" ? <User className="w-4 h-4 text-white" /> : <Bot className="w-4 h-4 text-white" />}
            </div>
            <div className={"max-w-[80%] p-3 rounded-2xl " + 
              (msg.role === "user" 
                ? "bg-blue-600 text-white rounded-br-sm" 
                : "bg-gray-700 text-gray-100 rounded-bl-sm")}>
              {msg.isThinking ? (
                <div className="flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Je reflechis...</span>
                </div>
              ) : (
                <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
              )}
            </div>
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>

      <div className="p-4 border-t border-gray-700 bg-gray-800/50">
        <div className="flex gap-2">
          <Textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Decris ton projet ou demande une modification..."
            className="flex-1 min-h-[60px] max-h-[120px] bg-gray-700 border-gray-600 text-white placeholder-gray-400 resize-none"
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
          />
          <Button
            onClick={handleSend}
            disabled={!message.trim() || isGenerating}
            className="h-[60px] w-[60px] bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
          >
            {isGenerating ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
          </Button>
        </div>
        <div className="mt-2 flex items-center justify-between text-xs text-gray-500">
          <span>Shift + Enter pour nouvelle ligne</span>
          <span className="flex items-center gap-1">
            <Wand2 className="w-3 h-3" />
            Mode magique active
          </span>
        </div>
      </div>
    </div>
  );
};

export default SmartAI;
