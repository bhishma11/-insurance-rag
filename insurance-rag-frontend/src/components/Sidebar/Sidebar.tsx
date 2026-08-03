// src/components/Sidebar/Sidebar.tsx
import { useState } from 'react';
import {
  MessageSquare,
  BarChart3,
  Settings,
  ChevronLeft,
  ChevronRight,
  History,
  FileText,
  Zap,
  ExternalLink,
  Calculator,
  Scale,
  ChevronDown,
  Activity
} from 'lucide-react';
import { ChatHistory } from './ChatHistory';
import { DocumentList } from './DocumentList';
import { SettingsPanel } from './SettingsPanel';
import { PremiumCalculatorModal } from './PremiumCalculatorModal';
import { PolicyComparisonModal } from './PolicyComparisonModal';
import { DashboardModal } from '../Dashboard/DashboardModal';
import { AnalyticsModal } from '../Analytics/AnalyticsModal';

export const Sidebar = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [showPremiumModal, setShowPremiumModal] = useState(false);
  const [showComparisonModal, setShowComparisonModal] = useState(false);
  const [showDashboard, setShowDashboard] = useState(false);
  const [showAnalytics, setShowAnalytics] = useState(false);
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    history: false,
    documents: false,
    settings: false,
  });

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const navItems = [
    { icon: MessageSquare, label: 'Chat', active: true },
  ];

  const langSmithUrl = 'https://smith.langchain.com/projects/lemonade-ai-prod?time_interval=7d';

  return (
    <aside className={`
      bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 transition-all duration-300 relative flex flex-col
      ${isCollapsed ? 'w-16' : 'w-72'}
    `}>
      <button
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="absolute -right-3 top-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-full p-1 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors z-10"
      >
        <ChevronLeft className={`w-4 h-4 text-gray-600 dark:text-gray-300 transition-transform duration-300 ${isCollapsed ? 'rotate-180' : ''}`} />
      </button>

      <div className="p-4 space-y-4 flex-1 overflow-y-auto">
        {/* Chat Navigation */}
        <nav className="space-y-1">
          {navItems.map((item) => (
            <a
              key={item.label}
              href="#"
              className={`
                flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200
                ${item.active
                  ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-white'
                }
                ${isCollapsed ? 'justify-center' : ''}
              `}
            >
              <item.icon className="w-5 h-5 flex-shrink-0" />
              {!isCollapsed && (
                <span className="text-sm font-medium">{item.label}</span>
              )}
            </a>
          ))}
        </nav>

        {/* Premium Calculator Button */}
        {!isCollapsed && (
          <div className="pt-3 border-t border-gray-200 dark:border-gray-700">
            <button
              onClick={() => setShowPremiumModal(true)}
              className="w-full flex items-center gap-3 px-3 py-2.5 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/30 dark:to-indigo-950/30 hover:from-blue-100 hover:to-indigo-100 dark:hover:from-blue-950/50 dark:hover:to-indigo-950/50 rounded-lg transition-all duration-200 border border-blue-200 dark:border-blue-800"
            >
              <Calculator className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              <span className="text-sm font-medium text-blue-700 dark:text-blue-300">Premium Calculator</span>
            </button>
          </div>
        )}

        {/* Policy Comparison Button */}
        {!isCollapsed && (
          <div className="pt-2">
            <button
              onClick={() => setShowComparisonModal(true)}
              className="w-full flex items-center gap-3 px-3 py-2.5 bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-950/30 dark:to-pink-950/30 hover:from-purple-100 hover:to-pink-100 dark:hover:from-purple-950/50 dark:hover:to-pink-950/50 rounded-lg transition-all duration-200 border border-purple-200 dark:border-purple-800"
            >
              <Scale className="w-5 h-5 text-purple-600 dark:text-purple-400" />
              <span className="text-sm font-medium text-purple-700 dark:text-purple-300">Policy Comparison</span>
            </button>
          </div>
        )}

        {/* System Monitor Button */}
        {!isCollapsed && (
          <div className="pt-2">
            <button
              onClick={() => setShowDashboard(true)}
              className="w-full flex items-center gap-3 px-3 py-2.5 bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-950/30 dark:to-purple-950/30 hover:from-indigo-100 hover:to-purple-100 dark:hover:from-indigo-950/50 dark:hover:to-purple-950/50 rounded-lg transition-all duration-200 border border-indigo-200 dark:border-indigo-800"
            >
              <Activity className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
              <span className="text-sm font-medium text-indigo-700 dark:text-indigo-300">System Monitor</span>
            </button>
          </div>
        )}

        {/* Analytics Button */}
        {!isCollapsed && (
          <div className="pt-2">
            <button
              onClick={() => setShowAnalytics(true)}
              className="w-full flex items-center gap-3 px-3 py-2.5 bg-gradient-to-r from-blue-50 to-cyan-50 dark:from-blue-950/30 dark:to-cyan-950/30 hover:from-blue-100 hover:to-cyan-100 dark:hover:from-blue-950/50 dark:hover:to-cyan-950/50 rounded-lg transition-all duration-200 border border-blue-200 dark:border-blue-800"
            >
              <BarChart3 className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              <span className="text-sm font-medium text-blue-700 dark:text-blue-300">Analytics</span>
            </button>
          </div>
        )}

        {/* History Section */}
        {!isCollapsed && (
          <div className="border-t border-gray-200 dark:border-gray-700 pt-3">
            <button
              onClick={() => toggleSection('history')}
              className="flex items-center justify-between w-full px-2 py-1.5 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-lg transition-colors"
            >
              <div className="flex items-center gap-2">
                <History className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">History</span>
              </div>
              {expandedSections.history ? (
                <ChevronDown className="w-4 h-4 text-gray-400" />
              ) : (
                <ChevronRight className="w-4 h-4 text-gray-400" />
              )}
            </button>
            {expandedSections.history && (
              <div className="mt-2 pl-2">
                <ChatHistory />
              </div>
            )}
          </div>
        )}

        {/* Documents Section */}
        {!isCollapsed && (
          <div className="border-t border-gray-200 dark:border-gray-700 pt-3">
            <button
              onClick={() => toggleSection('documents')}
              className="flex items-center justify-between w-full px-2 py-1.5 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-lg transition-colors"
            >
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Documents</span>
              </div>
              {expandedSections.documents ? (
                <ChevronDown className="w-4 h-4 text-gray-400" />
              ) : (
                <ChevronRight className="w-4 h-4 text-gray-400" />
              )}
            </button>
            {expandedSections.documents && (
              <div className="mt-2 pl-2">
                <DocumentList />
              </div>
            )}
          </div>
        )}

        {/* Settings Section - Now includes RAG Features, Governance, Performance inside */}
        {!isCollapsed && (
          <div className="border-t border-gray-200 dark:border-gray-700 pt-3">
            <button
              onClick={() => toggleSection('settings')}
              className="flex items-center justify-between w-full px-2 py-1.5 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-lg transition-colors"
            >
              <div className="flex items-center gap-2">
                <Settings className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Settings</span>
              </div>
              {expandedSections.settings ? (
                <ChevronDown className="w-4 h-4 text-gray-400" />
              ) : (
                <ChevronRight className="w-4 h-4 text-gray-400" />
              )}
            </button>
            {expandedSections.settings && (
              <div className="mt-2 pl-2">
                <SettingsPanel />
              </div>
            )}
          </div>
        )}

        {/* LangSmith */}
        {!isCollapsed && (
          <div className="pt-3 border-t border-gray-200 dark:border-gray-700">
            <a
              href={langSmithUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-between px-3 py-2.5 bg-purple-50 dark:bg-purple-900/30 hover:bg-purple-100 dark:hover:bg-purple-900/50 rounded-lg transition-colors border border-purple-200 dark:border-purple-800"
            >
              <div className="flex items-center gap-2">
                <ExternalLink className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                <span className="text-sm font-medium text-purple-700 dark:text-purple-300">LangSmith</span>
              </div>
              <span className="text-xs text-purple-400 dark:text-purple-500">Monitor</span>
            </a>
          </div>
        )}

        {/* System Status */}
        {!isCollapsed && (
          <div className="pt-3 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-3 px-3 py-2 bg-green-50 dark:bg-green-900/30 rounded-lg border border-green-100 dark:border-green-800">
              <Zap className="w-4 h-4 text-green-600 dark:text-green-400" />
              <div>
                <p className="text-xs font-medium text-green-700 dark:text-green-300">System Ready</p>
                <p className="text-[10px] text-green-600 dark:text-green-400">All services online</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Modals */}
      {showPremiumModal && (
        <PremiumCalculatorModal onClose={() => setShowPremiumModal(false)} />
      )}
      {showComparisonModal && (
        <PolicyComparisonModal onClose={() => setShowComparisonModal(false)} />
      )}
      {showDashboard && (
        <DashboardModal onClose={() => setShowDashboard(false)} />
      )}
      {showAnalytics && (
        <AnalyticsModal onClose={() => setShowAnalytics(false)} />
      )}
    </aside>
  );
};