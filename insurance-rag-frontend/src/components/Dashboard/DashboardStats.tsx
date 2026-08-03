// src/components/Dashboard/DashboardStats.tsx
import { Shield, Users, Zap, Clock, DollarSign, HardDrive, UserCheck, FileText, AlertCircle, Activity, CheckCircle, XCircle } from 'lucide-react';
import { DashboardStats } from '../../types';

interface Props {
  data: DashboardStats;
  loading?: boolean;
}

export const DashboardStats = ({ data, loading = false }: Props) => {
  // Loading state
  if (loading) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {[...Array(6)].map((_, i) => (
          <div
            key={i}
            className="p-4 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 animate-pulse"
          >
            <div className="flex items-center gap-2 mb-1">
              <div className="w-4 h-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
              <div className="h-3 w-16 bg-gray-200 dark:bg-gray-700 rounded"></div>
            </div>
            <div className="h-6 w-20 bg-gray-200 dark:bg-gray-700 rounded mt-1"></div>
          </div>
        ))}
      </div>
    );
  }

  // Safely access data with fallbacks
  const systemStatus = data?.system_status || 'healthy';
  const totalUsers = data?.total_users ?? 0;
  const activeUsers = data?.active_users ?? 0;
  const totalRequests = data?.total_requests ?? 0;
  const pendingRequests = data?.pending_requests ?? 0;
  const safetyScore = data?.safety_score ?? 95;

  const stats = [
    {
      label: 'System Status',
      value: systemStatus === 'healthy' ? '✅ Healthy' : '⚠️ Degraded',
      icon: systemStatus === 'healthy' ? CheckCircle : AlertCircle,
      color: systemStatus === 'healthy' ? 'text-green-500' : 'text-red-500',
      bg: systemStatus === 'healthy' ? 'bg-green-50 dark:bg-green-900/20' : 'bg-red-50 dark:bg-red-900/20',
    },
    {
      label: 'Total Users',
      value: totalUsers.toLocaleString(),
      icon: Users,
      color: 'text-blue-500',
      bg: 'bg-blue-50 dark:bg-blue-900/20',
    },
    {
      label: 'Active Users',
      value: activeUsers.toLocaleString(),
      icon: UserCheck,
      color: 'text-green-500',
      bg: 'bg-green-50 dark:bg-green-900/20',
    },
    {
      label: 'Total Requests',
      value: totalRequests.toLocaleString(),
      icon: FileText,
      color: 'text-purple-500',
      bg: 'bg-purple-50 dark:bg-purple-900/20',
    },
    {
      label: 'Pending Requests',
      value: pendingRequests.toLocaleString(),
      icon: Clock,
      color: 'text-amber-500',
      bg: 'bg-amber-50 dark:bg-amber-900/20',
    },
    {
      label: 'Safety Score',
      value: `${safetyScore}%`,
      icon: Shield,
      color: safetyScore > 90 ? 'text-green-500' : 'text-yellow-500',
      bg: safetyScore > 90 ? 'bg-green-50 dark:bg-green-900/20' : 'bg-yellow-50 dark:bg-yellow-900/20',
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
      {stats.map((stat, index) => (
        <div
          key={index}
          className={`p-4 rounded-xl border border-gray-200 dark:border-gray-700 ${stat.bg} hover:shadow-md transition-shadow duration-200`}
        >
          <div className="flex items-center gap-2 mb-1">
            <stat.icon className={`w-4 h-4 ${stat.color}`} />
            <span className="text-xs text-gray-500 dark:text-gray-400">{stat.label}</span>
          </div>
          <p className={`text-lg font-bold ${stat.color}`}>{stat.value}</p>
        </div>
      ))}
    </div>
  );
};

export default DashboardStats;