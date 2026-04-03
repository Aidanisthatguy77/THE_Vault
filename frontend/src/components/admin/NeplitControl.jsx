import { useState, useEffect } from "react";
import axios from "axios";
import { 
  Package, Download, Wand2, RefreshCw, Shield, FileText, 
  CheckCircle, XCircle, AlertTriangle, Clock, Zap, 
  ChevronDown, ChevronUp, Wifi, WifiOff, Activity
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Connectivity Status Indicator
const ConnectivityIndicator = ({ isOnline, isApiConnected }) => {
  const mode = isOnline && isApiConnected ? 'live' : 'vault';
  
  return (
    <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium ${
      mode === 'live' 
        ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
        : 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
    }`}>
      {mode === 'live' ? (
        <>
          <Wifi size={14} className="animate-pulse" />
          <span>LIVE SYNC</span>
        </>
      ) : (
        <>
          <WifiOff size={14} />
          <span>VAULT MODE</span>
        </>
      )}
    </div>
  );
};

// Action Log Item
const LogItem = ({ log }) => {
  const getIcon = () => {
    switch (log.action_type) {
      case 'content_change': return <FileText size={14} className="text-blue-400" />;
      case 'export': return <Download size={14} className="text-green-400" />;
      case 'doc_fix': return <Shield size={14} className="text-purple-400" />;
      case 'ai_plan': return <Zap size={14} className="text-yellow-400" />;
      default: return <Activity size={14} className="text-white/50" />;
    }
  };

  const getStatusColor = () => {
    switch (log.status) {
      case 'success': return 'text-green-400';
      case 'failed': return 'text-red-400';
      default: return 'text-yellow-400';
    }
  };

  return (
    <div className="flex items-start gap-3 p-3 bg-black/50 rounded border border-white/5 text-sm">
      <div className="mt-0.5">{getIcon()}</div>
      <div className="flex-1 min-w-0">
        <p className="text-white/80 truncate">{log.description}</p>
        <p className="text-white/40 text-xs mt-1">
          {new Date(log.timestamp).toLocaleString()}
        </p>
      </div>
      <span className={`text-xs uppercase ${getStatusColor()}`}>{log.status}</span>
    </div>
  );
};

// The Doc Panel
const TheDocPanel = ({ onFix }) => {
  const [checking, setChecking] = useState(false);
  const [result, setResult] = useState(null);

  const runCheck = async () => {
    setChecking(true);
    try {
      const res = await axios.post(`${API}/neplit/doc/check`);
      setResult(res.data);
    } catch (error) {
      toast.error("Failed to run stability check");
    }
    setChecking(false);
  };

  const applyFix = async (fixType) => {
    try {
      const res = await axios.post(`${API}/neplit/doc/fix?fix_type=${fixType}`);
      if (res.data.fixed) {
        toast.success(res.data.message);
        runCheck(); // Re-run check after fix
        onFix?.();
      } else {
        toast.error(res.data.message);
      }
    } catch (error) {
      toast.error("Failed to apply fix");
    }
  };

  return (
    <div className="bg-[#09090B] p-6 rounded-lg border border-white/10">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <Shield className="text-purple-400" size={24} />
          <div>
            <h3 className="font-heading text-xl font-bold text-white uppercase">The Doc</h3>
            <p className="text-white/50 text-sm">Stability & health monitoring</p>
          </div>
        </div>
        <Button 
          onClick={runCheck} 
          disabled={checking}
          variant="outline"
          className="border-purple-500/50 text-purple-400 hover:bg-purple-500/10"
        >
          {checking ? <RefreshCw className="animate-spin mr-2" size={16} /> : <Activity className="mr-2" size={16} />}
          Run Check
        </Button>
      </div>

      {result && (
        <div className="space-y-4 mt-4">
          {/* Status Badge */}
          <div className={`flex items-center gap-2 p-3 rounded ${
            result.healthy ? 'bg-green-500/10 border border-green-500/30' : 'bg-yellow-500/10 border border-yellow-500/30'
          }`}>
            {result.healthy ? (
              <>
                <CheckCircle className="text-green-400" size={20} />
                <span className="text-green-400 font-medium">All systems healthy</span>
              </>
            ) : (
              <>
                <AlertTriangle className="text-yellow-400" size={20} />
                <span className="text-yellow-400 font-medium">
                  {result.issues?.length || 0} issues found
                </span>
              </>
            )}
          </div>

          {/* Issues */}
          {result.issues?.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-white/70 text-sm font-medium">Issues</h4>
              {result.issues.map((issue, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 bg-red-500/10 rounded border border-red-500/20">
                  <div>
                    <p className="text-white/80 text-sm">{issue.suggested_fix || issue.type}</p>
                    <p className="text-white/40 text-xs">Severity: {issue.severity}</p>
                  </div>
                  {issue.fix_available && (
                    <Button 
                      size="sm" 
                      onClick={() => applyFix(issue.type)}
                      className="bg-red-500/20 hover:bg-red-500/30 text-red-400 border border-red-500/30"
                    >
                      Fix
                    </Button>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Warnings */}
          {result.warnings?.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-white/70 text-sm font-medium">Warnings</h4>
              {result.warnings.map((warning, idx) => (
                <div key={idx} className="p-3 bg-yellow-500/10 rounded border border-yellow-500/20">
                  <p className="text-white/80 text-sm">{warning.message}</p>
                  <p className="text-white/40 text-xs">Severity: {warning.severity}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// AI Analyzer Panel
const AIAnalyzerPanel = ({ onPlanApplied }) => {
  const [command, setCommand] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [plan, setPlan] = useState(null);
  const [applying, setApplying] = useState(false);

  const analyzeCommand = async () => {
    if (!command.trim()) return;
    setAnalyzing(true);
    setPlan(null);

    try {
      const res = await axios.post(`${API}/neplit/analyze`, { command });
      if (res.data.error) {
        toast.error(res.data.error);
        // Fall back to direct execution
        executeDirectCommand();
      } else {
        setPlan(res.data.plan);
      }
    } catch (error) {
      toast.error("Analysis failed, trying direct execution...");
      executeDirectCommand();
    }
    setAnalyzing(false);
  };

  const executeDirectCommand = async () => {
    try {
      const res = await axios.post(`${API}/neplit/execute`, { command });
      toast.success(res.data.result);
      setCommand('');
      onPlanApplied?.();
    } catch (error) {
      toast.error("Command failed");
    }
  };

  const applyPlan = async () => {
    if (!plan) return;
    setApplying(true);

    try {
      const res = await axios.post(`${API}/neplit/apply-plan`, {
        command,
        plan,
        confirmed: true
      });

      if (res.data.success) {
        toast.success(`Applied ${res.data.changes_applied?.length || 0} changes`);
        setPlan(null);
        setCommand('');
        onPlanApplied?.();
      } else {
        toast.error(res.data.errors?.[0]?.error || "Failed to apply changes");
      }
    } catch (error) {
      toast.error("Failed to apply plan");
    }
    setApplying(false);
  };

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'low': return 'text-green-400 bg-green-500/10 border-green-500/30';
      case 'medium': return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30';
      case 'high': return 'text-red-400 bg-red-500/10 border-red-500/30';
      default: return 'text-white/50 bg-white/5 border-white/10';
    }
  };

  return (
    <div className="bg-[#09090B] p-6 rounded-lg border border-white/10">
      <div className="flex items-center gap-3 mb-4">
        <Zap className="text-yellow-400" size={24} />
        <div>
          <h3 className="font-heading text-xl font-bold text-white uppercase">AI Command Analyzer</h3>
          <p className="text-white/50 text-sm">Describe changes in natural language</p>
        </div>
      </div>

      <Textarea
        value={command}
        onChange={(e) => setCommand(e.target.value)}
        placeholder="e.g., 'Change the hero headline to THE LEGACY AWAITS and update the tagline to something more exciting'"
        className="bg-black border-white/20 text-white min-h-[100px] mb-4"
      />

      <div className="flex gap-3 mb-4">
        <Button 
          onClick={analyzeCommand}
          disabled={analyzing || !command.trim()}
          className="bg-yellow-500/20 hover:bg-yellow-500/30 text-yellow-400 border border-yellow-500/30"
        >
          {analyzing ? <RefreshCw className="animate-spin mr-2" size={16} /> : <Zap className="mr-2" size={16} />}
          Analyze & Plan
        </Button>
        <Button 
          onClick={executeDirectCommand}
          disabled={analyzing || !command.trim()}
          variant="outline"
          className="border-white/20 text-white/70 hover:bg-white/10"
        >
          Execute Directly
        </Button>
      </div>

      {/* Plan Preview */}
      {plan && (
        <div className="mt-4 p-4 bg-black rounded border border-yellow-500/30">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-white font-medium">Generated Plan</h4>
            <span className={`text-xs px-2 py-1 rounded border ${getRiskColor(plan.risk_level)}`}>
              {plan.risk_level?.toUpperCase()} RISK
            </span>
          </div>

          <p className="text-white/70 text-sm mb-3">{plan.summary}</p>

          {plan.changes?.length > 0 && (
            <div className="space-y-2 mb-4">
              <p className="text-white/50 text-xs uppercase">Changes to apply:</p>
              {plan.changes.map((change, idx) => (
                <div key={idx} className="flex items-center gap-2 text-sm">
                  <CheckCircle size={14} className="text-green-400" />
                  <span className="text-white/70">{change.key}:</span>
                  <span className="text-white/90 truncate">"{change.new_value}"</span>
                </div>
              ))}
            </div>
          )}

          {plan.warnings?.length > 0 && (
            <div className="mb-4 p-2 bg-yellow-500/10 rounded">
              {plan.warnings.map((w, idx) => (
                <p key={idx} className="text-yellow-400 text-xs flex items-center gap-1">
                  <AlertTriangle size={12} /> {w}
                </p>
              ))}
            </div>
          )}

          {plan.requires_code_edit && (
            <div className="mb-4 p-2 bg-red-500/10 rounded">
              <p className="text-red-400 text-xs flex items-center gap-1">
                <AlertTriangle size={12} /> {plan.code_edit_note || "This change requires code modification. Export the project to make these changes."}
              </p>
            </div>
          )}

          <div className="flex gap-2">
            <Button 
              onClick={applyPlan}
              disabled={applying || plan.requires_code_edit}
              className="bg-green-500/20 hover:bg-green-500/30 text-green-400 border border-green-500/30"
            >
              {applying ? <RefreshCw className="animate-spin mr-2" size={16} /> : <CheckCircle className="mr-2" size={16} />}
              Apply Changes
            </Button>
            <Button 
              onClick={() => setPlan(null)}
              variant="outline"
              className="border-white/20 text-white/70 hover:bg-white/10"
            >
              Cancel
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};

// Quick Commands Panel
const QuickCommandsPanel = ({ onExecute }) => {
  const [loading, setLoading] = useState(null);

  const quickCommands = [
    { label: "Change Hero Headline", template: "Change the hero headline to 'YOUR TEXT'" },
    { label: "Update Tagline", template: "Update the tagline to 'YOUR TEXT'" },
    { label: "Set Petition Goal", template: "Set petition goal to 10000" },
    { label: "Change CTA Button", template: "Change the CTA button to 'JOIN NOW'" },
    { label: "Update Vault Headline", template: "Change the vault headline to 'YOUR TEXT'" },
  ];

  const executeCommand = async (cmd) => {
    const userInput = window.prompt(`Enter the new value:\n\nTemplate: ${cmd.template}`);
    if (!userInput) return;

    const fullCommand = cmd.template.replace("'YOUR TEXT'", `'${userInput}'`).replace("10000", userInput);
    
    setLoading(cmd.label);
    try {
      const res = await axios.post(`${API}/neplit/execute`, { command: fullCommand });
      toast.success(res.data.result);
      onExecute?.();
    } catch (error) {
      toast.error("Command failed");
    }
    setLoading(null);
  };

  return (
    <div className="bg-[#09090B] p-6 rounded-lg border border-white/10">
      <h3 className="font-heading text-lg font-bold text-white uppercase mb-4">Quick Commands</h3>
      <div className="flex flex-wrap gap-2">
        {quickCommands.map((cmd) => (
          <Button
            key={cmd.label}
            onClick={() => executeCommand(cmd)}
            disabled={loading === cmd.label}
            variant="outline"
            size="sm"
            className="border-white/20 text-white/70 hover:bg-white/10 hover:text-white"
          >
            {loading === cmd.label ? <RefreshCw className="animate-spin mr-1" size={12} /> : null}
            {cmd.label}
          </Button>
        ))}
      </div>
    </div>
  );
};

// Main Neplit Control Component
const NeplitControl = () => {
  const [downloading, setDownloading] = useState(false);
  const [logs, setLogs] = useState([]);
  const [showLogs, setShowLogs] = useState(false);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [isApiConnected, setIsApiConnected] = useState(true);

  // Fetch logs
  const fetchLogs = async () => {
    try {
      const res = await axios.get(`${API}/neplit/logs`);
      setLogs(res.data);
    } catch (error) {
      console.error('Failed to fetch logs');
    }
  };

  // Check connectivity
  const checkConnectivity = async () => {
    try {
      await axios.get(`${API}/health`, { timeout: 5000 });
      setIsApiConnected(true);
    } catch {
      setIsApiConnected(false);
    }
  };

  useEffect(() => {
    fetchLogs();
    checkConnectivity();
    
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => { setIsOnline(false); setIsApiConnected(false); };
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    const interval = setInterval(checkConnectivity, 30000);
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      clearInterval(interval);
    };
  }, []);

  const downloadProject = async () => {
    setDownloading(true);
    toast.info("Generating your standalone project...");
    
    try {
      const response = await axios.get(`${API}/neplit/export`, {
        responseType: 'blob',
        timeout: 120000 // 2 minute timeout for large exports
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'nba2k-legacy-vault-standalone.zip');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast.success("Download started! Your full standalone project is ready.");
      fetchLogs();
    } catch (error) {
      toast.error("Export failed. Please try again.");
    }
    setDownloading(false);
  };

  return (
    <div data-testid="neplit-control" className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Package className="text-[#C8102E]" size={32} />
          <div>
            <h2 className="font-heading text-3xl font-bold text-white uppercase">Neplit</h2>
            <p className="text-white/60">Site control, AI commands & standalone export</p>
          </div>
        </div>
        <ConnectivityIndicator isOnline={isOnline} isApiConnected={isApiConnected} />
      </div>

      {/* Export Section */}
      <div className="bg-gradient-to-r from-[#C8102E]/20 to-transparent p-6 rounded-lg border border-[#C8102E]/50">
        <div className="flex items-start justify-between gap-6 flex-wrap">
          <div className="flex-1 min-w-[300px]">
            <h3 className="font-heading text-xl font-bold text-white uppercase flex items-center gap-2">
              <Download size={20} className="text-[#C8102E]" />
              Generate Standalone Build
            </h3>
            <p className="text-white/70 text-sm mt-2">
              Export your complete NBA 2K Legacy Vault as an independent package:
            </p>
            <ul className="text-white/60 text-sm mt-3 space-y-1">
              <li>• Full React frontend + FastAPI backend</li>
              <li>• Gemini AI integration (direct API, no platform dependency)</li>
              <li>• MongoDB schema & configuration</li>
              <li>• .env.example files (no secrets included)</li>
              <li>• Deployment guide for Vercel/Railway</li>
            </ul>
          </div>
          <Button 
            onClick={downloadProject} 
            disabled={downloading}
            className="bg-[#C8102E] hover:bg-[#9e0c24] text-white px-8 py-6 text-lg"
          >
            {downloading ? (
              <>
                <RefreshCw className="animate-spin mr-2" size={20} />
                Generating...
              </>
            ) : (
              <>
                <Download className="mr-2" size={20} />
                Download ZIP
              </>
            )}
          </Button>
        </div>
      </div>

      {/* AI Analyzer */}
      <AIAnalyzerPanel onPlanApplied={fetchLogs} />

      {/* Quick Commands */}
      <QuickCommandsPanel onExecute={fetchLogs} />

      {/* The Doc */}
      <TheDocPanel onFix={fetchLogs} />

      {/* Action Logs */}
      <div className="bg-[#09090B] p-6 rounded-lg border border-white/10">
        <button 
          onClick={() => setShowLogs(!showLogs)}
          className="flex items-center justify-between w-full"
        >
          <div className="flex items-center gap-3">
            <Clock className="text-white/50" size={20} />
            <h3 className="font-heading text-lg font-bold text-white uppercase">Action Log</h3>
            <span className="text-white/40 text-sm">({logs.length} actions)</span>
          </div>
          {showLogs ? <ChevronUp className="text-white/50" /> : <ChevronDown className="text-white/50" />}
        </button>

        {showLogs && (
          <div className="mt-4 space-y-2 max-h-[300px] overflow-y-auto">
            {logs.length === 0 ? (
              <p className="text-white/40 text-sm text-center py-4">No actions logged yet</p>
            ) : (
              logs.map((log) => <LogItem key={log.id} log={log} />)
            )}
          </div>
        )}
      </div>

      {/* Info Footer */}
      <div className="bg-black/50 p-4 rounded-lg border border-white/10">
        <p className="text-white/50 text-xs">
          <strong className="text-white/70">Note:</strong> The exported project is 100% standalone with Gemini AI integration. 
          Deploy anywhere — Vercel, Railway, Render, or your own server. No platform dependencies.
        </p>
      </div>
    </div>
  );
};

export default NeplitControl;
