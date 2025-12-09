import React, { useState, useEffect, useRef, useCallback, useMemo, memo } from "react";
import {
  Monitor,
  Tablet,
  Smartphone,
  RefreshCw,
  Terminal,
  CheckCircle,
  Loader2,
  XCircle,
  AlertTriangle
} from "lucide-react";
import { Button } from "../ui/button";

/**
 * Device Presets Configuration
 * Memoized to prevent re-creation on each render
 */
const DEVICE_PRESETS = {
  desktop: { width: "100%", height: "100%", label: "Desktop", icon: Monitor },
  tablet: { width: "768px", height: "1024px", label: "Tablet", icon: Tablet },
  mobile: { width: "375px", height: "667px", label: "Mobile", icon: Smartphone }
};

/**
 * Status Configurations
 * Static object to avoid re-creation
 */
const STATUS_CONFIG = {
  ready: { icon: CheckCircle, color: "text-green-500", label: "Prêt" },
  loading: { icon: Loader2, color: "text-blue-500", label: "Chargement..." },
  error: { icon: XCircle, color: "text-red-500", label: "Erreur" },
  warning: { icon: AlertTriangle, color: "text-yellow-500", label: "Attention" }
};

/**
 * DeviceSelector - Memoized component for device selection
 */
const DeviceSelector = memo(function DeviceSelector({ currentDevice, onDeviceChange }) {
  return (
    <div className="flex items-center gap-1 bg-gray-700 rounded-lg p-1">
      {Object.entries(DEVICE_PRESETS).map(([key, { icon: Icon, label }]) => (
        <Button
          key={key}
          variant={currentDevice === key ? "default" : "ghost"}
          size="sm"
          onClick={() => onDeviceChange(key)}
          className={`px-2 transition-smooth ${currentDevice === key ? "bg-blue-600" : ""}`}
          title={label}
          aria-label={`Switch to ${label} view`}
        >
          <Icon className="w-4 h-4" />
        </Button>
      ))}
    </div>
  );
});

/**
 * StatusIndicator - Memoized component for status display
 */
const StatusIndicator = memo(function StatusIndicator({ status }) {
  const config = STATUS_CONFIG[status] || STATUS_CONFIG.ready;
  const Icon = config.icon;

  return (
    <div className={`flex items-center gap-2 ${config.color}`}>
      <Icon className={`w-4 h-4 ${status === 'loading' ? 'animate-spin' : ''}`} />
      <span className="text-sm font-medium">{config.label}</span>
    </div>
  );
});

/**
 * Terminal - Memoized terminal component
 */
const Terminal = memo(function TerminalComponent({ logs }) {
  const terminalRef = useRef(null);

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="w-80 bg-gray-900 border-l border-gray-700 flex flex-col">
      <div className="px-3 py-2 bg-gray-800 border-b border-gray-700">
        <span className="text-sm text-gray-300 font-medium">Terminal</span>
      </div>
      <div
        ref={terminalRef}
        className="flex-1 overflow-y-auto p-3 font-mono text-xs custom-scrollbar"
      >
        {logs.length === 0 ? (
          <div className="text-gray-500 italic">No logs yet...</div>
        ) : (
          logs.map((log, i) => (
            <div key={`log-${i}`} className="text-gray-400 mb-1">
              <span className="text-gray-600">[{i}]</span> {log}
            </div>
          ))
        )}
      </div>
    </div>
  );
});

/**
 * WebContainerPreview - Optimized preview component
 *
 * Performance optimizations:
 * - React.memo to prevent unnecessary re-renders
 * - useMemo for computed values (HTML generation)
 * - useCallback for event handlers
 * - Lazy iframe updates with debouncing
 * - Memoized child components
 *
 * @version 2.0.0 - Optimized by Frontend Squad
 */
const WebContainerPreview = memo(function WebContainerPreview({ files = {}, className = "" }) {
  const [status, setStatus] = useState("ready");
  const [device, setDevice] = useState("desktop");
  const [showTerminal, setShowTerminal] = useState(false);
  const [logs, setLogs] = useState([]);

  const containerRef = useRef(null);
  const iframeRef = useRef(null);
  const updateTimeoutRef = useRef(null);

  /**
   * Generate HTML from files - Memoized to prevent recalculation
   */
  const generatedHTML = useMemo(() => {
    if (!files || Object.keys(files).length === 0) {
      return '<!DOCTYPE html><html><head><title>Preview</title></head><body><div style="display:flex;align-items:center;justify-content:center;height:100vh;font-family:sans-serif;color:#666;">No files to preview</div></body></html>';
    }

    // Find relevant files
    const htmlFile = Object.entries(files).find(([name]) => name.endsWith(".html"));
    const cssFile = Object.entries(files).find(([name]) => name.endsWith(".css"));
    const jsFile = Object.entries(files).find(([name]) =>
      name.endsWith(".js") && !name.includes("config")
    );

    let html = htmlFile?.[1] || "<!DOCTYPE html><html><head></head><body></body></html>";

    // Inject CSS
    if (cssFile && html.includes("</head>")) {
      const cssContent = cssFile[1];
      html = html.replace("</head>", `<style>${cssContent}</style></head>`);
    }

    // Inject JS
    if (jsFile && html.includes("</body>")) {
      const jsContent = jsFile[1];
      html = html.replace("</body>", `<script>${jsContent}<\/script></body>`);
    }

    return html;
  }, [files]);

  /**
   * Update iframe with debouncing for performance
   */
  useEffect(() => {
    if (!iframeRef.current) return;

    // Clear existing timeout
    if (updateTimeoutRef.current) {
      clearTimeout(updateTimeoutRef.current);
    }

    // Debounce iframe update
    updateTimeoutRef.current = setTimeout(() => {
      setStatus("loading");
      addLog("Updating preview...");

      try {
        if (iframeRef.current) {
          iframeRef.current.srcdoc = generatedHTML;

          // Set status to ready after a short delay
          setTimeout(() => {
            setStatus("ready");
            addLog("Preview updated successfully");
          }, 300);
        }
      } catch (error) {
        setStatus("error");
        addLog(`Error: ${error.message}`);
      }
    }, 150); // 150ms debounce

    return () => {
      if (updateTimeoutRef.current) {
        clearTimeout(updateTimeoutRef.current);
      }
    };
  }, [generatedHTML]);

  /**
   * Add log entry - useCallback to prevent re-creation
   */
  const addLog = useCallback((message) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, `[${timestamp}] ${message}`]);
  }, []);

  /**
   * Refresh iframe - useCallback
   */
  const handleRefresh = useCallback(() => {
    if (iframeRef.current) {
      addLog("Manual refresh triggered");
      iframeRef.current.srcdoc = generatedHTML;
    }
  }, [generatedHTML, addLog]);

  /**
   * Toggle terminal - useCallback
   */
  const handleToggleTerminal = useCallback(() => {
    setShowTerminal(prev => !prev);
    addLog(showTerminal ? "Terminal closed" : "Terminal opened");
  }, [showTerminal, addLog]);

  /**
   * Change device - useCallback
   */
  const handleDeviceChange = useCallback((newDevice) => {
    setDevice(newDevice);
    addLog(`Device changed to ${DEVICE_PRESETS[newDevice].label}`);
  }, [addLog]);

  /**
   * Get current device dimensions - Memoized
   */
  const deviceDimensions = useMemo(() => {
    const preset = DEVICE_PRESETS[device];
    return {
      width: preset.width,
      height: preset.height,
      maxWidth: "100%",
      maxHeight: "100%"
    };
  }, [device]);

  return (
    <div ref={containerRef} className={`flex flex-col h-full bg-gray-900 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 bg-gray-800 border-b border-gray-700">
        <StatusIndicator status={status} />

        <div className="flex items-center gap-2">
          <DeviceSelector currentDevice={device} onDeviceChange={handleDeviceChange} />

          <Button
            variant="ghost"
            size="sm"
            onClick={handleToggleTerminal}
            className="text-gray-400 hover:text-white transition-fast"
            aria-label="Toggle terminal"
          >
            <Terminal className="w-4 h-4" />
          </Button>

          <Button
            variant="ghost"
            size="sm"
            onClick={handleRefresh}
            className="text-gray-400 hover:text-white transition-fast"
            aria-label="Refresh preview"
          >
            <RefreshCw className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Preview Area */}
      <div className="flex-1 flex overflow-hidden">
        <div className="flex-1 flex items-center justify-center bg-gray-950 p-4">
          <div
            className="bg-white rounded-lg shadow-2xl overflow-hidden transition-all duration-300"
            style={deviceDimensions}
          >
            <iframe
              ref={iframeRef}
              className="w-full h-full border-0"
              title="Preview"
              sandbox="allow-scripts allow-forms allow-modals allow-same-origin allow-popups"
              loading="lazy"
            />
          </div>
        </div>

        {showTerminal && <Terminal logs={logs} />}
      </div>
    </div>
  );
});

// Set display name for debugging
WebContainerPreview.displayName = "WebContainerPreview";

export default WebContainerPreview;
