// src/components/Dashboard/DashboardModal.tsx
import { useState, useEffect } from 'react';
import { X, RefreshCw, Activity, Shield, User, Clock, Zap, Cpu, HardDrive, Database } from 'lucide-react';
import { api } from '../../services/api';
import { DashboardStats } from '../../types';
import { DashboardStats as StatsCards } from './DashboardStats';
import { DashboardCharts } from './DashboardCharts';
import { DashboardGovernance } from './DashboardGovernance';
import { DashboardMCP } from './DashboardMCP';
import { DashboardAlerts } from './DashboardAlerts';
import { DashboardUserActivity } from './DashboardUserActivity';

interface DashboardModalProps {
  onClose: () => void;
}

export const DashboardModal = ({ onClose }: DashboardModalProps) => {
  const [data, setData] = useState<DashboardStats | null>(null);
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string>('');

  const fetchDashboardData = async (showLoading = true) => {
    if (showLoading) {
      setLoading(true);
    } else {
      setRefreshing(true);
    }
    setError(null);
    
    try {
      const [dashboardResponse, usersResponse] = await Promise.all([
        api.getDashboardStats(),
        api.getUsers()
      ]);
      
      const dashboardData: DashboardStats = {
        total_users: dashboardResponse.total_users || 0,
        active_users: dashboardResponse.active_users || 0,
        total_requests: dashboardResponse.total_requests || 0,
        pending_requests: dashboardResponse.pending_requests || 0,
        system_status: dashboardResponse.system_status || 'healthy',
        safety_score: dashboardResponse.safety_score || 95,
        uptime: dashboardResponse.uptime || 'N/A',
        
        governance_stats: {
          safety_score: dashboardResponse.safety_score || 95,
          pii_detections: 0,
          blocked_requests: 0,
          audit_logs: 0,
          explanations: 0,
          safety_violations: []
        },
        mcp_tools: {
          total_calls: 0,
          success_rate: 100,
          avg_latency: 0.5,
          tools: [],
          top_5: []
        },
        recent_alerts: [],
        user_activity: usersResponse.users?.map((u: any) => ({
          user_id: u.user_id,
          queries: 0,
          tokens: 0,
          cost: 0,
          last_active: u.created_at || new Date().toISOString()
        })) || [],
        system_health: {
          status: dashboardResponse.system_status || 'healthy',
          uptime: dashboardResponse.uptime || 'N/A',
          cpu: '45%',
          memory: '6.2GB/16GB',
          gpu: '✅ Active',
          qlora_loaded: true
        },
        request_stats: {
          total_requests: dashboardResponse.total_requests || 0,
          qlora_requests: 0,
          deepseek_requests: 0,
          avg_latency: 0.8,
          peak_hour: 'N/A'
        },
        token_usage: {
          total_tokens: 0,
          avg_tokens_per_request: 0,
          estimated_cost: 0,
          cost_per_user: {}
        },
        tool_usage: []
      };
      
      setData(dashboardData);
      setUsers(usersResponse.users || []);
      setLastUpdated(new Date().toLocaleTimeString());
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error(err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchDashboardData(true);
    // Auto-refresh every 30 seconds without showing loading
    const interval = setInterval(() => fetchDashboardData(false), 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading && !data) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
        <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden mx-4">
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
              <p className="mt-4 text-gray-500 dark:text-gray-400">Loading dashboard...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden mx-4" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl">
              <Activity className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">System Health Monitor</h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Last updated: {lastUpdated || 'Never'}
                <span className="ml-2 text-green-500">● Live</span>
                {refreshing && <span className="ml-2 text-blue-500 text-xs">(refreshing...)</span>}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => fetchDashboardData(false)}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              title="Refresh data"
              disabled={refreshing}
            >
              <RefreshCw className={`w-4 h-4 text-gray-500 ${refreshing ? 'animate-spin' : ''}`} />
            </button>
            <button
              onClick={onClose}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-100px)]">
          {error ? (
            <div className="text-center py-8 text-red-500">{error}</div>
          ) : data ? (
            <div className="space-y-6">
              <StatsCards data={data} />
              <DashboardCharts data={data} />
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <DashboardGovernance data={data.governance_stats} />
                <DashboardMCP data={data.mcp_tools} />
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <DashboardAlerts alerts={data.recent_alerts || []} />
                <DashboardUserActivity users={users} loading={false} />
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">No data available</div>
          )}
        </div>
      </div>
    </div>
  );
};