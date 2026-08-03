// src/components/Dashboard/DashboardGovernance.tsx
import { Shield, AlertTriangle, Eye, FileCheck, Lock } from 'lucide-react';

interface GovernanceData {
  safety_score: number;
  pii_detections: number;
  blocked_requests: number;
  audit_logs: number;
  explanations: number;
  safety_violations: Array<{
    category: string;
    count: number;
    severity: string;
  }>;
}

interface Props {
  data?: GovernanceData;  // ← Made optional
}

export const DashboardGovernance = ({ data }: Props) => {
  // ✅ Safe defaults if data is undefined
  const governance = data || {
    safety_score: 95,
    pii_detections: 0,
    blocked_requests: 0,
    audit_logs: 0,
    explanations: 0,
    safety_violations: []
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'CRITICAL': return 'text-red-500 bg-red-50 dark:bg-red-900/20';
      case 'HIGH': return 'text-orange-500 bg-orange-50 dark:bg-orange-900/20';
      case 'MEDIUM': return 'text-yellow-500 bg-yellow-50 dark:bg-yellow-900/20';
      default: return 'text-gray-500 bg-gray-50 dark:bg-gray-800';
    }
  };

  return (
    <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-700">
      <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
        🛡️ AI Governance
      </h3>

      <div className="grid grid-cols-2 gap-2 mb-4">
        <div className="p-2 bg-white dark:bg-gray-900/50 rounded-lg">
          <div className="flex items-center gap-2">
            <Shield className="w-4 h-4 text-green-500" />
            <span className="text-xs text-gray-500 dark:text-gray-400">Safety Score</span>
          </div>
          <p className="text-lg font-bold text-gray-900 dark:text-white">{governance.safety_score}%</p>
        </div>
        <div className="p-2 bg-white dark:bg-gray-900/50 rounded-lg">
          <div className="flex items-center gap-2">
            <Lock className="w-4 h-4 text-red-500" />
            <span className="text-xs text-gray-500 dark:text-gray-400">Blocked</span>
          </div>
          <p className="text-lg font-bold text-gray-900 dark:text-white">{governance.blocked_requests}</p>
        </div>
        <div className="p-2 bg-white dark:bg-gray-900/50 rounded-lg">
          <div className="flex items-center gap-2">
            <Eye className="w-4 h-4 text-purple-500" />
            <span className="text-xs text-gray-500 dark:text-gray-400">PII Detected</span>
          </div>
          <p className="text-lg font-bold text-gray-900 dark:text-white">{governance.pii_detections}</p>
        </div>
        <div className="p-2 bg-white dark:bg-gray-900/50 rounded-lg">
          <div className="flex items-center gap-2">
            <FileCheck className="w-4 h-4 text-blue-500" />
            <span className="text-xs text-gray-500 dark:text-gray-400">Explanations</span>
          </div>
          <p className="text-lg font-bold text-gray-900 dark:text-white">{governance.explanations}</p>
        </div>
      </div>

      {/* Violations */}
      {governance.safety_violations && governance.safety_violations.length > 0 && (
        <div>
          <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">Recent Violations</p>
          <div className="space-y-1.5">
            {governance.safety_violations.slice(0, 3).map((violation, i) => (
              <div
                key={i}
                className={`flex items-center justify-between px-2 py-1.5 rounded-lg ${getSeverityColor(violation.severity)}`}
              >
                <span className="text-xs font-medium">{violation.category}</span>
                <span className="text-xs">{violation.count} events</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};