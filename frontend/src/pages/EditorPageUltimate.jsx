import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { ArrowLeft, Save, Download, Sparkles, Eye, Rocket, Palette, Moon, Sun } from "lucide-react";
import Editor from "@monaco-editor/react";
import axios from "axios";
import { toast } from "sonner";
import JSZip from "jszip";
import WebContainerPreview from "../components/preview/WebContainerPreview";
import OneClickDeploy from "../components/deploy/OneClickDeploy";
import TemplateSelector from "../components/templates/TemplateSelector";
import SmartAI from "../components/ai/SmartAI";

const API = process.env.REACT_APP_BACKEND_URL + "/api";

const EditorPageUltimate = () => {
  const navigate = useNavigate();
  const { projectId } = useParams();
  const [project, setProject] = useState({
    name: "Nouveau Projet",
    files: [
      { name: "index.html", content: "<!DOCTYPE html><html><body><h1>Hello</h1></body></html>", language: "html" },
      { name: "styles.css", content: "body { font-family: sans-serif; }", language: "css" },
      { name: "script.js", content: "console.log(\"loaded\");", language: "javascript" }
    ]
  });
  const [currentFileIndex, setCurrentFileIndex] = useState(0);
  const [activeTab, setActiveTab] = useState("preview");
  const [generating, setGenerating] = useState(false);
  const [darkMode, setDarkMode] = useState(true);
  const [showTemplates, setShowTemplates] = useState(false);
  const [apiKey, setApiKey] = useState("");

  useEffect(() => { if (projectId) loadProject(); loadSettings(); }, [projectId]);

  const loadProject = async () => {
    try { const res = await axios.get(API + "/projects/" + projectId); setProject(res.data); } 
    catch (e) { toast.error("Erreur chargement"); }
  };

  const loadSettings = async () => {
    try { const res = await axios.get(API + "/settings"); if (res.data.openrouter_api_key) setApiKey(res.data.openrouter_api_key); } catch (e) {}
  };

  const saveProject = async () => {
    try {
      if (projectId) await axios.put(API + "/projects/" + projectId, project);
      else { const res = await axios.post(API + "/projects", project); navigate("/editor/" + res.data.id); }
      toast.success("Sauvegarde!");
    } catch (e) { toast.error("Erreur sauvegarde"); }
  };

  const handleGenerate = async (message) => {
    if (!apiKey) { toast.error("Configurez API"); return; }
    setGenerating(true);
    try {
      const res = await axios.post(API + "/generate/agentic", { message, api_key: apiKey, current_files: project.files });
      if (res.data.success && res.data.files) {
        setProject(prev => {
          let files = [...prev.files];
          res.data.files.forEach(f => { const idx = files.findIndex(x => x.name === f.name); if (idx >= 0) files[idx] = f; else files.push(f); });
          return { ...prev, files };
        });
        toast.success(res.data.files.length + " fichiers!");
      }
    } catch (e) { toast.error("Erreur"); throw e; } finally { setGenerating(false); }
  };

  const downloadProject = async () => {
    const zip = new JSZip();
    project.files.forEach(f => zip.file(f.name, f.content));
    const blob = await zip.generateAsync({ type: "blob" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = project.name.replace(/[^a-z0-9]/gi, "_") + ".zip";
    a.click();
  };

  const file = project.files[currentFileIndex] || project.files[0];

  return (
    <div className={darkMode ? "min-h-screen bg-gray-950 text-white" : "min-h-screen bg-gray-50 text-gray-900"}>
      <header className={"border-b px-4 py-3 flex items-center justify-between " + (darkMode ? "border-gray-800 bg-gray-900" : "border-gray-200 bg-white")}>
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={() => navigate("/dashboard")}><ArrowLeft className="w-4 h-4 mr-2" />Retour</Button>
          <div className="flex items-center gap-2"><Sparkles className="w-5 h-5 text-purple-500" /><input value={project.name} onChange={(e) => setProject(prev => ({ ...prev, name: e.target.value }))} className="bg-transparent font-bold text-lg border-none focus:outline-none px-2" /></div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm" onClick={() => setShowTemplates(!showTemplates)}><Palette className="w-4 h-4 mr-2" />Templates</Button>
          <Button variant="ghost" size="sm" onClick={() => setDarkMode(!darkMode)}>{darkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}</Button>
          <Button variant="ghost" size="sm" onClick={downloadProject}><Download className="w-4 h-4" /></Button>
          <Button onClick={saveProject} className="bg-purple-600 hover:bg-purple-700"><Save className="w-4 h-4 mr-2" />Sauvegarder</Button>
        </div>
      </header>
      {showTemplates && (<div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4"><div className="max-w-4xl w-full"><TemplateSelector onSelect={(t) => { setShowTemplates(false); handleGenerate("Genere " + t.name); }} /><Button variant="ghost" className="mt-4 w-full text-white" onClick={() => setShowTemplates(false)}>Fermer</Button></div></div>)}
      <div className="flex h-[calc(100vh-65px)]">
        <div className={"w-80 border-r " + (darkMode ? "border-gray-800" : "border-gray-200")}><SmartAI onGenerate={handleGenerate} projectFiles={project.files} isGenerating={generating} /></div>
        <div className="flex-1 flex flex-col">
          <div className={"border-b flex items-center gap-1 px-2 py-1 " + (darkMode ? "border-gray-800 bg-gray-900" : "border-gray-200 bg-gray-100")}>{project.files.map((f, i) => (<button key={f.name} onClick={() => setCurrentFileIndex(i)} className={"px-3 py-1.5 rounded text-sm " + (currentFileIndex === i ? "bg-purple-600 text-white" : "text-gray-400 hover:bg-gray-800")}>{f.name}</button>))}<button onClick={() => { const n = prompt("Nom:"); if (n) setProject(prev => ({ ...prev, files: [...prev.files, { name: n, content: "", language: "plaintext" }] })); }} className="px-2 py-1.5 text-gray-500">+ Nouveau</button></div>
          <div className="flex-1"><Editor height="100%" language={file?.language} value={file?.content} theme={darkMode ? "vs-dark" : "light"} onChange={(v) => setProject(prev => { const f = [...prev.files]; f[currentFileIndex] = { ...f[currentFileIndex], content: v || "" }; return { ...prev, files: f }; })} options={{ minimap: { enabled: false }, fontSize: 14, padding: { top: 16 } }} /></div>
        </div>
        <div className={"w-[500px] border-l flex flex-col " + (darkMode ? "border-gray-800" : "border-gray-200")}>
          <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
            <TabsList className="border-b rounded-none justify-start px-2 bg-gray-900 border-gray-800"><TabsTrigger value="preview" className="gap-2"><Eye className="w-4 h-4" />Preview</TabsTrigger><TabsTrigger value="deploy" className="gap-2"><Rocket className="w-4 h-4" />Deploy</TabsTrigger></TabsList>
            <TabsContent value="preview" className="flex-1 m-0"><WebContainerPreview files={project.files} /></TabsContent>
            <TabsContent value="deploy" className="flex-1 m-0 p-4"><OneClickDeploy files={project.files} projectName={project.name} /></TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
};

export default EditorPageUltimate;
