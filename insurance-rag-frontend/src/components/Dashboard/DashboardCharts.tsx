// src/components/Dashboard/DashboardCharts.tsx
import { DashboardStats } from '../../types';

interface Props {
  data: DashboardStats;
}

export const DashboardCharts = ({ data }: Props) => {
  // Use the new data structure with fallbacks
  const totalUsers = data.total_users || 0;
  const activeUsers = data.active_users || 0;
  const totalRequests = data.total_requests || 0;
  const pendingRequests = data.pending_requests || 0;

  // Calculate percentages for charts
  const activePercent = totalUsers > 0 ? (activeUsers / totalUsers) * 100 : 0;
  const pendingPercent = totalRequests > 0 ? (pendingRequests / totalRequests) * 100 : 0;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {/* User Distribution */}
      <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-700">
        <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
          👥 User Distribution
        </h3>
        <div className="space-y-3">
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-600 dark:text-gray-400">Total Users</span>
              <span className="font-medium text-blue-600 dark:text-blue-400">
                {totalUsers}
              </span>
            </div>
            <div className="w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full transition-all duration-500"
                style={{ width: '100%' }}
              />
            </div>
          </div>
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-600 dark:text-gray-400">Active Users</span>
              <span className="font-medium text-green-600 dark:text-green-400">
                {activeUsers} ({activePercent.toFixed(1)}%)
              </span>
            </div>
            <div className="w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-green-500 to-emerald-500 rounded-full transition-all duration-500"
                style={{ width: `${activePercent}%` }}
              />
            </div>
          </div>
        </div>
        <div className="mt-3 text-xs text-gray-500 dark:text-gray-400">
          {activeUsers} active out of {totalUsers} total users
        </div>
      </div>

      {/* Request Distribution */}
      <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-700">
        <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
          📋 Request Distribution
        </h3>
        <div className="space-y-3">
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-600 dark:text-gray-400">Total Requests</span>
              <span className="font-medium text-purple-600 dark:text-purple-400">
                {totalRequests}
              </span>
            </div>
            <div className="w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full transition-all duration-500"
                style={{ width: '100%' }}
              />
            </div>
          </div>
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-600 dark:text-gray-400">Pending Requests</span>
              <span className="font-medium text-amber-600 dark:text-amber-400">
                {pendingRequests} ({pendingPercent.toFixed(1)}%)
              </span>
            </div>
            <div className="w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-amber-500 to-orange-500 rounded-full transition-all duration-500"
                style={{ width: `${pendingPercent}%` }}
              />
            </div>
          </div>
        </div>
        <div className="mt-3 text-xs text-gray-500 dark:text-gray-400">
          {pendingRequests} pending out of {totalRequests} total requests
        </div>
      </div>
    </div>
  );
};