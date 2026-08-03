// src/components/Analytics/AnalyticsModal.tsx
import { useState, useEffect } from 'react';
import { X, RefreshCw, TrendingUp, Users, DollarSign, Zap, Clock, BarChart3 } from 'lucide-react';
import { api } from '../../services/api';
import { AnalyticsStats } from '../../types';
import { AnalyticsStats as StatsCards } from './AnalyticsStats';
import { AnalyticsCharts } from './AnalyticsCharts';
import { AnalyticsFeatures } from './AnalyticsFeatures';
import { AnalyticsCost } from './AnalyticsCost';
import { AnalyticsQueries } from './AnalyticsQueries';

interface AnalyticsModalProps {
  onClose: () => void;
}

export const AnalyticsModal = ({ onClose }: AnalyticsModalProps) => {
  const [data, setData] = useState<AnalyticsStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string>('');

  const fetchAnalytics = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.getAnalyticsStats();
      setData(response);
      setLastUpdated(new Date().toLocaleTimeString());
    } catch (err) {
      setError('Failed to load analytics data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
    const interval = setInterval(fetchAnalytics, 60000); // Auto-refresh every 60s
    return () => clearInterval(interval);
  }, []);

  if (loading && !data) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
        <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden mx-4">
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
              <p className="mt-4 text-gray-500 dark:text-gray-400">Loading analytics...</p>
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
            <div className="p-2 bg-gradient-to-r from-blue-600 to-cyan-600 rounded-xl">
              <BarChart3 className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">Analytics Dashboard</h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Business Intelligence & User Insights
                <span className="ml-2 text-green-500">● Live</span>
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-400">
              Last updated: {lastUpdated || 'Never'}
            </span>
            <button
              onClick={fetchAnalytics}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              title="Refresh data"
            >
              <RefreshCw className={`w-4 h-4 text-gray-500 ${loading ? 'animate-spin' : ''}`} />
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
              {/* Stats Cards */}
              <StatsCards data={data} />

              {/* Charts */}
              <AnalyticsCharts data={data} />

              {/* Features & Queries */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <AnalyticsFeatures data={data.features} />
                <AnalyticsQueries data={data.queries} />
              </div>

              {/* Cost & Performance */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <AnalyticsCost data={data.cost} />
                <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-700">
                  <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                    ⚡ Performance
                  </h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600 dark:text-gray-400">Avg Response Time</span>
                      <span className="font-medium text-gray-900 dark:text-white">
                        {data.performance.avg_response_time}s
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600 dark:text-gray-400">QLoRA Avg</span>
                      <span className="font-medium text-green-600 dark:text-green-400">
                        {data.performance.avg_qlora_time}s
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600 dark:text-gray-400">DeepSeek Avg</span>
                      <span className="font-medium text-blue-600 dark:text-blue-400">
                        {data.performance.avg_deepseek_time}s
                      </span>
                    </div>
                    <div className="flex justify-between pt-2 border-t border-gray-200 dark:border-gray-700">
                      <span className="text-sm text-gray-600 dark:text-gray-400">Success Rate</span>
                      <span className="font-medium text-green-600 dark:text-green-400">
                        {data.performance.success_rate}%
                      </span>
                    </div>
                  </div>
                </div>
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