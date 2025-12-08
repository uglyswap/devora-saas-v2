import React, { useState, useEffect, useRef, useCallback } from "react";
import { Monitor, Tablet, Smartphone, RefreshCw, Maximize2, Minimize2, Terminal, Play, Loader2, CheckCircle, XCircle, AlertTriangle, WifiOff } from "lucide-react";
import { Button } from "../ui/button";

const DEVICE_PRESETS = {
  desktop: { width: "100%", height: "100%", label: "Desktop", icon: Monitor },
  tablet: { width: "768px", height: "1024px", label: "Tablet", icon: Tablet },
  mobile: { width: "375px", height: "667px", label: "Mobile", icon: Smartphone }
};

const WebContainerPreview = ({ files = [], className = "" }) => {
  const [status, setStatus] = useState("ready");
  const [device, setDevice] = useState("desktop");
  const [showTerminal, setShowTerminal] = useState(false);
  const [logs, setLogs] = useState([]);
  const containerRef = useRef(null);
  const iframeRef = useRef(null);

  useEffect(() => {
    if (!iframeRef.current || !files.length) return;
    const htmlFile = files.find(f => f.name.endsWith(".html"));
    const cssFile = files.find(f => f.name.endsWith(".css"));
    const jsFile = files.find(f => f.name.endsWith(".js") && !f.name.includes("config"));
    
    let html = htmlFile?.content || "<!DOCTYPE html><html><head></head><body></body></html>";
    if (cssFile && html.includes("</head>")) {
      html = html.replace("</head>", "<style>" + cssFile.content + "</style></head>");
    }
    if (jsFile && html.includes("</body>")) {
      html = html.replace("</body>", "<script>" + jsFile.content + "<\/script></body>");
    }
    iframeRef.current.srcdoc = html;
  }, [files]);

  const StatusIndicator = () => {
    const cfg = { icon: CheckCircle, color: "text-green-500", label: "Pret" };
    const Icon = cfg.icon;
    return (<div className={"flex items-center gap-2 " + cfg.color}><Icon className="w-4 h-4" /><span className="text-sm font-medium">{cfg.label}</span></div>);
  };

  return (
    <div ref={containerRef} className={"flex flex-col h-full bg-gray-900 " + className}>
      <div className="flex items-center justify-between px-4 py-2 bg-gray-800 border-b border-gray-700">
        <StatusIndicator />
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 bg-gray-700 rounded-lg p-1">
            {Object.entries(DEVICE_PRESETS).map(([key, { icon: Icon, label }]) => (
              <Button key={key} variant={device === key ? "default" : "ghost"} size="sm" onClick={() => setDevice(key)} className={"px-2 " + (device === key ? "bg-blue-600" : "")} title={label}><Icon className="w-4 h-4" /></Button>
            ))}
          </div>
          <Button variant="ghost" size="sm" onClick={() => setShowTerminal(!showTerminal)} className="text-gray-400 hover:text-white"><Terminal className="w-4 h-4" /></Button>
          <Button variant="ghost" size="sm" onClick={() => iframeRef.current && (iframeRef.current.srcdoc = iframeRef.current.srcdoc)} className="text-gray-400 hover:text-white"><RefreshCw className="w-4 h-4" /></Button>
        </div>
      </div>
      <div className="flex-1 flex overflow-hidden">
        <div className="flex-1 flex items-center justify-center bg-gray-950 p-4">
          <div className="bg-white rounded-lg shadow-2xl overflow-hidden" style={{ width: DEVICE_PRESETS[device].width, height: DEVICE_PRESETS[device].height, maxWidth: "100%", maxHeight: "100%" }}>
            <iframe ref={iframeRef} className="w-full h-full border-0" title="Preview" sandbox="allow-scripts allow-forms allow-modals allow-same-origin allow-popups" />
          </div>
        </div>
        {showTerminal && (
          <div className="w-80 bg-gray-900 border-l border-gray-700 flex flex-col">
            <div className="px-3 py-2 bg-gray-800 border-b border-gray-700"><span className="text-sm text-gray-300">Terminal</span></div>
            <div className="flex-1 overflow-y-auto p-3 font-mono text-xs">{logs.map((log, i) => (<div key={i} className="text-gray-400">{log}</div>))}</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default WebContainerPreview;
