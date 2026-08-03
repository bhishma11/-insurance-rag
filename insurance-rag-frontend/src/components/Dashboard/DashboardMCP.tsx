// src/components/Dashboard/DashboardMCP.tsx
import { Wrench, CheckCircle, XCircle, Clock } from 'lucide-react';

interface MCPTool {
  name: string;
  calls: number;
  success_rate: number;
  latency: number;
  last_used: string;
}

interface Props {
  data: {
    total_calls: number;
    success_rate: number;
    avg_latency: number;
    tools: MCPTool[];
    top_5: Array<{ name: string; calls: number }>;
  };
}

export const DashboardMCP = ({ data }: Props) => {
  return (
    <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-700">
      <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
        🔌 MCP Tools
      </h3>

      {/* Summary */}
      <div className="grid grid-cols-3 gap-2 mb-4">
        <div className="p-2 bg-white dark:bg-gray-900/50 rounded-lg text-center">
          <p className="text-lg font-bold text-gray-900 dark:text-white">{data.total_calls}</p>
          <p className="text-xs text-gray-500 dark:text-gray-400">Total Calls</p>
        </div>
        <div className="p-2 bg-white dark:bg-gray-900/50 rounded-lg text-center">
          <p className="text-lg font-bold text-green-600 dark:text-green-400">{data.success_rate}%</p>
          <p className="text-xs text-gray-500 dark:text-gray-400">Success Rate</p>
        </div>
        <div className="p-2 bg-white dark:bg-gray-900/50 rounded-lg text-center">
          <p className="text-lg font-bold text-purple-600 dark:text-purple-400">{data.avg_latency}s</p>
          <p className="text-xs text-gray-500 dark:text-gray-400">Avg Latency</p>
        </div>
      </div>

      {/* Top Tools */}
      <div>
        <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">Top Tools</p>
        <div className="space-y-1.5">
          {data.top_5.map((tool, i) => (
            <div key={i} className="flex items-center justify-between px-2 py-1.5 bg-white dark:bg-gray-900/50 rounded-lg">
              <div className="flex items-center gap-2">
                <span className="text-xs font-medium text-gray-700 dark:text-gray-300">
                  {i + 1}
                </span>
                <span className="text-sm text-gray-900 dark:text-white">{tool.name}</span>
              </div>
              <span className="text-sm font-medium text-gray-600 dark:text-gray-400">{tool.calls} calls</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};