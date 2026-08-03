// src/components/Sidebar/SettingsPanel.tsx
import { useState } from 'react';
import {
  Settings,
  Moon,
  Sun,
  Database,
  Shield,
  Sparkles,
  FileText,
  Zap,
  RefreshCw,
  ChevronRight,
  ChevronDown,
  CheckCircle,
  XCircle,
  AlertCircle,
  Eye,
  Lock,
  Gauge,
  ExternalLink,
  BarChart3,
  LogOut,
  User,
  Mail,
  Building,
  Activity,
  Key,
  X
} from 'lucide-react';
import { authService } from '../../services/auth';

export const SettingsPanel = () => {
  const [darkMode, setDarkMode] = useState(() => {
    return document.documentElement.classList.contains('dark');
  });
  const [expandedRag, setExpandedRag] = useState(false);
  const [expandedGovernance, setExpandedGovernance] = useState(false);
  const [expandedPerformance, setExpandedPerformance] = useState(false);
  const [expandedUser, setExpandedUser] = useState(true);

  // Password Change Modal State
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordMessage, setPasswordMessage] = useState<{ text: string; type: string } | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    document.documentElement.classList.toggle('dark');
    localStorage.setItem('theme', darkMode ? 'light' : 'dark');
  };

  const currentUser = authService.getCurrentUser();

  const ragItems = [
    // ... (keep your existing ragItems)
    { id: 'hyde', icon: Sparkles, label: 'HyDE Search', description: 'Generate hypothetical documents for better retrieval', status: 'enabled' as const, color: 'text-purple-500' },
    { id: 'query_rewrite', icon: RefreshCw, label: 'Query Rewriting', description: 'Optimize queries for better search results', status: 'enabled' as const, color: 'text-blue-500' },
    { id: 'hybrid_search', icon: Database, label: 'Hybrid Search', description: 'Combine FAISS + BM25 for optimal retrieval', status: 'enabled' as const, color: 'text-green-500' },
    { id: 'document_intelligence', icon: FileText, label: 'Document Intelligence', description: 'Auto-classification and multi-format support', status: 'enabled' as const, color: 'text-cyan-500' },
    { id: 'qlora', icon: Sparkles, label: 'QLoRA Fine-tuning', description: '910+ examples trained on insurance data', status: 'enabled' as const, color: 'text-amber-500' },
    { id: 'mcp', icon: ExternalLink, label: 'MCP Integration', description: '9 tools exposed via MCP Gateway', status: 'enabled' as const, color: 'text-indigo-500' },
    { id: 'vision', icon: Eye, label: 'Vision Analysis', description: 'Ollama + Qwen2.5-VL for image analysis', status: 'enabled' as const, color: 'text-pink-500' },
    { id: 'analytics', icon: BarChart3, label: 'Analytics Dashboard', description: 'Track usage, costs, and performance metrics', status: 'enabled' as const, color: 'text-blue-500' },
  ];

  const governanceItems = [
    { id: 'content_safety', icon: Shield, label: 'Content Safety', description: 'Multi-layer content filtering for harmful inputs', status: 'enabled' as const, color: 'text-red-500' },
    { id: 'audit_logging', icon: FileText, label: 'Audit Logging', description: 'Complete traceability of all interactions', status: 'enabled' as const, color: 'text-blue-500' },
    { id: 'data_privacy', icon: Lock, label: 'Data Privacy (PII)', description: 'Automatic PII detection and redaction', status: 'enabled' as const, color: 'text-amber-500' },
    { id: 'explainability', icon: Sparkles, label: 'Explainability', description: 'AI decision explanations for transparency', status: 'enabled' as const, color: 'text-purple-500' },
  ];

  const performanceItems = [
    { id: 'qlora_acceleration', icon: Zap, label: 'QLoRA Acceleration', description: '2x faster inference with optimized parameters', status: 'enabled' as const, color: 'text-yellow-500' },
    { id: 'kv_cache', icon: Database, label: 'KV Cache Optimization', description: 'Reuses computed attention values for speed', status: 'enabled' as const, color: 'text-blue-500' },
    { id: 'cuda_optimizations', icon: Gauge, label: 'CUDA Optimizations', description: 'GPU-level optimizations for faster operations', status: 'enabled' as const, color: 'text-emerald-500' },
    { id: 'fast_generation', icon: Sparkles, label: 'Fast Generation', description: 'num_beams=1, top_p, top_k for faster sampling', status: 'enabled' as const, color: 'text-purple-500' },
  ];

  const enabledCount = ragItems.filter(item => item.status === 'enabled').length;
  const totalCount = ragItems.length;

  const handleSignOut = () => {
    if (window.confirm('Are you sure you want to sign out?')) {
      authService.logout();
    }
  };

  const handleChangePassword = async () => {
    if (newPassword !== confirmPassword) {
      setPasswordMessage({ text: 'Passwords do not match', type: 'error' });
      return;
    }
    
    if (newPassword.length < 8) {
      setPasswordMessage({ text: 'Password must be at least 8 characters', type: 'error' });
      return;
    }
    
    setIsLoading(true);
    setPasswordMessage(null);
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8001/api/auth/change-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ new_password: newPassword })
      });
      
      const data = await response.json();
      if (data.success) {
        setPasswordMessage({ text: '✅ Password changed successfully!', type: 'success' });
        setNewPassword('');
        setConfirmPassword('');
        setTimeout(() => {
          setShowPasswordModal(false);
          setPasswordMessage(null);
          // Optional: Log out user after password change
          // authService.logout();
        }, 2000);
      } else {
        setPasswordMessage({ text: '❌ ' + (data.detail || 'Failed to change password'), type: 'error' });
      }
    } catch (error) {
      setPasswordMessage({ text: '❌ Connection error. Please try again.', type: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <div className="space-y-4">
        {/* ============ USER PROFILE SECTION ============ */}
        <div className="border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden">
          <button
            onClick={() => setExpandedUser(!expandedUser)}
            className="w-full flex items-center justify-between p-3 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950/30 dark:to-purple-950/30 hover:from-blue-100 hover:to-purple-100 dark:hover:from-blue-950/50 dark:hover:to-purple-950/50 transition-colors"
          >
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center text-white text-sm font-bold">
                {currentUser?.name?.charAt(0)?.toUpperCase() || 'U'}
              </div>
              <div className="text-left">
                <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  {currentUser?.name || 'User'}
                </p>
                <p className="text-xs text-gray-400 dark:text-gray-500">
                  {currentUser?.email || 'No email'}
                </p>
              </div>
            </div>
            {expandedUser ? (
              <ChevronDown className="w-4 h-4 text-gray-400" />
            ) : (
              <ChevronRight className="w-4 h-4 text-gray-400" />
            )}
          </button>

          {expandedUser && currentUser && (
            <div className="p-3 space-y-2 bg-white dark:bg-gray-900">
              <div className="flex items-center gap-3 p-2 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
                <Mail className="w-4 h-4 text-gray-400" />
                <div className="flex-1 min-w-0">
                  <p className="text-xs text-gray-500 dark:text-gray-400">Email</p>
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300 truncate">
                    {currentUser.email}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3 p-2 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
                <Building className="w-4 h-4 text-gray-400" />
                <div className="flex-1 min-w-0">
                  <p className="text-xs text-gray-500 dark:text-gray-400">Company</p>
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300 truncate">
                    {currentUser.company || 'N/A'}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3 p-2 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
                <Activity className="w-4 h-4 text-gray-400" />
                <div className="flex-1 min-w-0">
                  <p className="text-xs text-gray-500 dark:text-gray-400">Status</p>
                  <span className={`text-xs px-2 py-0.5 rounded-full inline-block ${
                    currentUser.status === 'ACTIVE'
                      ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
                      : 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400'
                  }`}>
                    {currentUser.status}
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-3 p-2 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
                <User className="w-4 h-4 text-gray-400" />
                <div className="flex-1 min-w-0">
                  <p className="text-xs text-gray-500 dark:text-gray-400">User ID</p>
                  <p className="text-xs font-mono text-gray-700 dark:text-gray-300 truncate">
                    {currentUser.user_id}
                  </p>
                </div>
              </div>

              {/* ✅ Change Password Button */}
              <button
                onClick={() => setShowPasswordModal(true)}
                className="w-full flex items-center justify-center gap-2 mt-2 px-4 py-2 bg-blue-50 dark:bg-blue-900/30 hover:bg-blue-100 dark:hover:bg-blue-900/50 text-blue-600 dark:text-blue-400 text-sm font-medium rounded-lg transition-colors border border-blue-200 dark:border-blue-800"
              >
                <Key className="w-4 h-4" />
                Change Password
              </button>
            </div>
          )}
        </div>

        {/* ============ DARK MODE TOGGLE ============ */}
        <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3">
            {darkMode ? (
              <Moon className="w-4 h-4 text-blue-500" />
            ) : (
              <Sun className="w-4 h-4 text-yellow-500" />
            )}
            <div>
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Dark Mode</p>
              <p className="text-xs text-gray-400 dark:text-gray-500">Toggle light/dark theme</p>
            </div>
          </div>
          <button
            onClick={toggleDarkMode}
            className={`relative w-11 h-6 rounded-full transition-colors flex-shrink-0 ${
              darkMode ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'
            }`}
          >
            <div
              className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${
                darkMode ? 'translate-x-5' : ''
              }`}
            />
          </button>
        </div>

        {/* ============ RAG FEATURES ============ */}
        <div className="border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden">
          <button
            onClick={() => setExpandedRag(!expandedRag)}
            className="w-full flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800/50 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          >
            <div className="flex items-center gap-3">
              <Database className="w-4 h-4 text-blue-500" />
              <div className="text-left">
                <p className="text-sm font-medium text-gray-700 dark:text-gray-300">RAG Features</p>
                <p className="text-xs text-gray-400 dark:text-gray-500">
                  {enabledCount} of {totalCount} active
                </p>
              </div>
            </div>
            {expandedRag ? (
              <ChevronDown className="w-4 h-4 text-gray-400" />
            ) : (
              <ChevronRight className="w-4 h-4 text-gray-400" />
            )}
          </button>

          {expandedRag && (
            <div className="p-2 space-y-1.5 bg-white dark:bg-gray-900">
              {ragItems.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center justify-between p-2.5 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                >
                  <div className="flex items-center gap-2.5 min-w-0">
                    <item.icon className={`w-4 h-4 flex-shrink-0 ${item.color}`} />
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-gray-700 dark:text-gray-300 truncate">
                        {item.label}
                      </p>
                      <p className="text-xs text-gray-400 dark:text-gray-500 truncate">
                        {item.description}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-1.5 flex-shrink-0 ml-2">
                    {item.status === 'enabled' ? (
                      <span className="flex items-center gap-1 text-xs text-green-600 dark:text-green-400">
                        <CheckCircle className="w-3 h-3" />
                        Active
                      </span>
                    ) : (
                      <span className="flex items-center gap-1 text-xs text-amber-500 dark:text-amber-400">
                        <AlertCircle className="w-3 h-3" />
                        Coming
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* ============ GOVERNANCE ============ */}
        <div className="border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden">
          <button
            onClick={() => setExpandedGovernance(!expandedGovernance)}
            className="w-full flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800/50 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          >
            <div className="flex items-center gap-3">
              <Shield className="w-4 h-4 text-red-500" />
              <div className="text-left">
                <p className="text-sm font-medium text-gray-700 dark:text-gray-300">AI Governance</p>
                <p className="text-xs text-gray-400 dark:text-gray-500">
                  {governanceItems.filter(i => i.status === 'enabled').length} of {governanceItems.length} active
                </p>
              </div>
            </div>
            {expandedGovernance ? (
              <ChevronDown className="w-4 h-4 text-gray-400" />
            ) : (
              <ChevronRight className="w-4 h-4 text-gray-400" />
            )}
          </button>

          {expandedGovernance && (
            <div className="p-2 space-y-1.5 bg-white dark:bg-gray-900">
              {governanceItems.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center justify-between p-2.5 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                >
                  <div className="flex items-center gap-2.5 min-w-0">
                    <item.icon className={`w-4 h-4 flex-shrink-0 ${item.color}`} />
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-gray-700 dark:text-gray-300 truncate">
                        {item.label}
                      </p>
                      <p className="text-xs text-gray-400 dark:text-gray-500 truncate">
                        {item.description}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-1.5 flex-shrink-0 ml-2">
                    <span className="flex items-center gap-1 text-xs text-green-600 dark:text-green-400">
                      <CheckCircle className="w-3 h-3" />
                      Active
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* ============ PERFORMANCE ============ */}
        <div className="border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden">
          <button
            onClick={() => setExpandedPerformance(!expandedPerformance)}
            className="w-full flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800/50 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          >
            <div className="flex items-center gap-3">
              <Gauge className="w-4 h-4 text-emerald-500" />
              <div className="text-left">
                <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Performance</p>
                <p className="text-xs text-gray-400 dark:text-gray-500">
                  {performanceItems.filter(i => i.status === 'enabled').length} of {performanceItems.length} active
                </p>
              </div>
            </div>
            {expandedPerformance ? (
              <ChevronDown className="w-4 h-4 text-gray-400" />
            ) : (
              <ChevronRight className="w-4 h-4 text-gray-400" />
            )}
          </button>

          {expandedPerformance && (
            <div className="p-2 space-y-1.5 bg-white dark:bg-gray-900">
              {performanceItems.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center justify-between p-2.5 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                >
                  <div className="flex items-center gap-2.5 min-w-0">
                    <item.icon className={`w-4 h-4 flex-shrink-0 ${item.color}`} />
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-gray-700 dark:text-gray-300 truncate">
                        {item.label}
                      </p>
                      <p className="text-xs text-gray-400 dark:text-gray-500 truncate">
                        {item.description}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-1.5 flex-shrink-0 ml-2">
                    <span className="flex items-center gap-1 text-xs text-green-600 dark:text-green-400">
                      <CheckCircle className="w-3 h-3" />
                      Active
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* ============ SYSTEM STATUS ============ */}
        <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <div>
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300">System Status</p>
              <p className="text-xs text-gray-400 dark:text-gray-500">All services operational</p>
            </div>
          </div>
          <span className="text-xs text-green-600 dark:text-green-400">✅ Online</span>
        </div>

        {/* ============ SIGN OUT BUTTON ============ */}
        <div className="pt-2 border-t border-gray-200 dark:border-gray-700">
          <button
            onClick={handleSignOut}
            className="w-full flex items-center gap-3 px-3 py-3 bg-red-50 dark:bg-red-900/20 hover:bg-red-100 dark:hover:bg-red-900/30 rounded-xl transition-all duration-200 border border-red-200 dark:border-red-800 group"
          >
            <div className="p-1.5 bg-red-100 dark:bg-red-900/30 rounded-lg group-hover:bg-red-200 dark:group-hover:bg-red-900/50 transition-colors">
              <LogOut className="w-4 h-4 text-red-600 dark:text-red-400" />
            </div>
            <div className="flex-1 text-left">
              <p className="text-sm font-medium text-red-700 dark:text-red-300">Sign Out</p>
              <p className="text-xs text-red-500/70 dark:text-red-400/70">End your session</p>
            </div>
            <ChevronRight className="w-4 h-4 text-red-400 opacity-0 group-hover:opacity-100 transition-opacity" />
          </button>
        </div>

        {/* ============ VERSION ============ */}
        <div className="flex items-center justify-between p-2">
          <span className="text-xs text-gray-400 dark:text-gray-500">Version</span>
          <span className="text-xs font-medium text-gray-600 dark:text-gray-400">2.0.0</span>
        </div>
      </div>

      {/* ============ PASSWORD CHANGE MODAL ============ */}
      {showPasswordModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" onClick={() => setShowPasswordModal(false)}>
          <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl max-w-md w-full mx-4 p-6" onClick={(e) => e.stopPropagation()}>
            {/* Modal Header */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-xl">
                  <Key className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                </div>
                <h3 className="text-lg font-bold text-gray-900 dark:text-white">Change Password</h3>
              </div>
              <button
                onClick={() => setShowPasswordModal(false)}
                className="p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            {/* Modal Content */}
            <div className="space-y-4">
              {passwordMessage && (
                <div className={`p-3 rounded-lg text-sm ${
                  passwordMessage.type === 'success'
                    ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
                    : 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400'
                }`}>
                  {passwordMessage.text}
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  New Password
                </label>
                <input
                  type="password"
                  placeholder="Enter new password (min 8 characters)"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Confirm New Password
                </label>
                <input
                  type="password"
                  placeholder="Confirm your new password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                />
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  onClick={() => setShowPasswordModal(false)}
                  className="flex-1 px-4 py-2 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-lg font-medium transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleChangePassword}
                  disabled={isLoading}
                  className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? 'Updating...' : 'Update Password'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};