// src/components/Dashboard/DashboardAlerts.tsx
import { AlertTriangle, CheckCircle, Info } from 'lucide-react';

interface Alert {
  time: string;
  type: string;
  message: string;
  severity: 'info' | 'warning' | 'error';
}

interface Props {
  alerts: Alert[];
}

export const DashboardAlerts = ({ alerts }: Props) => {
  const getIcon = (severity: string) => {
    switch (severity) {
      case 'error': return <AlertTriangle className="w-4 h-4 text-red-500" />;
      case 'warning': return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
      default: return <Info className="w-4 h-4 text-blue-500" />;
    }
  };

  const getColor = (severity: string) => {
    switch (severity) {
      case 'error': return 'border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20';
      case 'warning': return 'border-yellow-200 dark:border-yellow-800 bg-yellow-50 dark:bg-yellow-900/20';
      default: return 'border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-900/20';
    }
  };

  return (
    <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-700">
      <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
        🚨 Recent Alerts
      </h3>

      {alerts.length === 0 ? (
        <div className="text-center py-4 text-gray-500 dark:text-gray-400 text-sm">
          <CheckCircle className="w-6 h-6 mx-auto mb-2 text-green-500" />
          No alerts to display
        </div>
      ) : (
        <div className="space-y-2">
          {alerts.slice(0, 5).map((alert, i) => (
            <div
              key={i}
              className={`flex items-start gap-3 p-2 rounded-lg border ${getColor(alert.severity)}`}
            >
              {getIcon(alert.severity)}
              <div className="flex-1 min-w-0">
                <p className="text-sm text-gray-700 dark:text-gray-300">{alert.message}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {alert.time} • {alert.type}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};