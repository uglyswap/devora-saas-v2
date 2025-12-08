import React, { useState } from "react";
import { Rocket, Cloud, Globe, CheckCircle, Loader2, ExternalLink, Copy, Sparkles, Zap } from "lucide-react";
import { Button } from "../ui/button";
import { toast } from "sonner";

const DEPLOY_PROVIDERS = [
  { id: "vercel", name: "Vercel", icon: "▲", color: "bg-black", description: "Deploy en 30 secondes" },
  { id: "netlify", name: "Netlify", icon: "◆", color: "bg-teal-500", description: "Gratuit et rapide" },
  { id: "railway", name: "Railway", icon: "🚂", color: "bg-purple-600", description: "Backend inclus" }
];

const OneClickDeploy = ({ files = [], projectName = "mon-app", onDeployed }) => {
  const [deploying, setDeploying] = useState(false);
  const [deployedUrl, setDeployedUrl] = useState(null);
  const [selectedProvider, setSelectedProvider] = useState("vercel");
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState("");

  const simulateDeploy = async () => {
    setDeploying(true);
    setProgress(0);
    setStatus("Preparation des fichiers...");
    
    const steps = [
      { progress: 20, status: "Creation du projet..." },
      { progress: 40, status: "Upload des fichiers..." },
      { progress: 60, status: "Installation des dependances..." },
      { progress: 80, status: "Build en cours..." },
      { progress: 100, status: "Deploiement termine!" }
    ];

    for (const step of steps) {
      await new Promise(r => setTimeout(r, 1000));
      setProgress(step.progress);
      setStatus(step.status);
    }

    const url = "https://" + projectName.toLowerCase().replace(/[^a-z0-9]/g, "-") + ".vercel.app";
    setDeployedUrl(url);
    setDeploying(false);
    toast.success("Deploiement reussi!");
    if (onDeployed) onDeployed(url);
  };

  const copyUrl = async () => {
    if (deployedUrl) {
      await navigator.clipboard.writeText(deployedUrl);
      toast.success("URL copiee!");
    }
  };

  return (
    <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-6 text-white">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-3 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl">
          <Rocket className="w-6 h-6" />
        </div>
        <div>
          <h2 className="text-xl font-bold">Deploiement One-Click</h2>
          <p className="text-gray-400 text-sm">Publiez votre app en un clic - aucun compte requis</p>
        </div>
      </div>

      {!deployedUrl ? (
        <>
          <div className="grid grid-cols-3 gap-3 mb-6">
            {DEPLOY_PROVIDERS.map(provider => (
              <button
                key={provider.id}
                onClick={() => setSelectedProvider(provider.id)}
                className={"p-4 rounded-xl border-2 transition-all " + (selectedProvider === provider.id ? "border-blue-500 bg-blue-500/10" : "border-gray-700 hover:border-gray-600")}
              >
                <div className={"w-10 h-10 rounded-lg flex items-center justify-center text-xl mb-2 " + provider.color}>{provider.icon}</div>
                <div className="font-medium">{provider.name}</div>
                <div className="text-xs text-gray-400">{provider.description}</div>
              </button>
            ))}
          </div>

          {deploying ? (
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <Loader2 className="w-5 h-5 animate-spin text-blue-500" />
                <span>{status}</span>
              </div>
              <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                <div className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-500" style={{ width: progress + "%" }} />
              </div>
            </div>
          ) : (
            <Button onClick={simulateDeploy} className="w-full h-14 text-lg bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
              <Zap className="w-5 h-5 mr-2" />
              Deployer Maintenant
            </Button>
          )}
        </>
      ) : (
        <div className="space-y-4">
          <div className="flex items-center gap-3 p-4 bg-green-500/10 border border-green-500/30 rounded-xl">
            <CheckCircle className="w-6 h-6 text-green-500" />
            <div className="flex-1">
              <div className="font-medium text-green-400">Deploiement reussi!</div>
              <div className="text-sm text-gray-400">Votre app est en ligne</div>
            </div>
          </div>
          
          <div className="flex items-center gap-2 p-3 bg-gray-800 rounded-lg">
            <Globe className="w-5 h-5 text-blue-400" />
            <span className="flex-1 font-mono text-sm truncate">{deployedUrl}</span>
            <Button variant="ghost" size="sm" onClick={copyUrl}><Copy className="w-4 h-4" /></Button>
            <Button variant="ghost" size="sm" onClick={() => window.open(deployedUrl, "_blank")}><ExternalLink className="w-4 h-4" /></Button>
          </div>

          <Button onClick={() => setDeployedUrl(null)} variant="outline" className="w-full">
            Deployer une nouvelle version
          </Button>
        </div>
      )}

      <div className="mt-6 p-4 bg-gray-800/50 rounded-xl">
        <div className="flex items-center gap-2 text-sm text-gray-400">
          <Sparkles className="w-4 h-4 text-yellow-500" />
          <span>Pas de compte requis - SSL gratuit - CDN mondial - Zero configuration</span>
        </div>
      </div>
    </div>
  );
};

export default OneClickDeploy;
