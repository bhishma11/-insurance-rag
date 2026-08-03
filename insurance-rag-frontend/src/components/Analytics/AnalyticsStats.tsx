// src/components/Analytics/AnalyticsStats.tsx
import { Users, TrendingUp, Clock, DollarSign, Zap, BarChart3 } from 'lucide-react';
import { AnalyticsStats } from '../../types';

interface Props {
  data: AnalyticsStats;
}

export const AnalyticsStats = ({ data }: Props) => {
  const stats = [
    {
      label: 'Total Users',
      value: data.users.total_users.toLocaleString(),
      icon: Users,
      color: 'text-blue-500',
      bg: 'bg-blue-50 dark:bg-blue-900/20',
    },
    {
      label: 'Active (7d)',
      value: data.users.active_users_7d.toLocaleString(),
      icon: TrendingUp,
      color: 'text-green-500',
      bg: 'bg-green-50 dark:bg-green-900/20',
    },
    {
      label: 'Growth Rate',
      value: `${data.users.growth_rate}%`,
      icon: BarChart3,
      color: 'text-purple-500',
      bg: 'bg-purple-50 dark:bg-purple-900/20',
    },
    {
      label: 'Avg Session',
      value: `${data.sessions.avg_session_duration}m`,
      icon: Clock,
      color: 'text-amber-500',
      bg: 'bg-amber-50 dark:bg-amber-900/20',
    },
    {
      label: 'Cost/Query',
      value: `$${data.cost.cost_per_query.toFixed(3)}`,
      icon: DollarSign,
      color: 'text-red-500',
      bg: 'bg-red-50 dark:bg-red-900/20',
    },
    {
      label: 'QLoRA Savings',
      value: `${data.cost.savings_percentage}%`,
      icon: Zap,
      color: 'text-emerald-500',
      bg: 'bg-emerald-50 dark:bg-emerald-900/20',
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
      {stats.map((stat, index) => (
        <div
          key={index}
          className={`p-4 rounded-xl border border-gray-200 dark:border-gray-700 ${stat.bg}`}
        >
          <div className="flex items-center gap-2 mb-1">
            <stat.icon className={`w-4 h-4 ${stat.color}`} />
            <span className="text-xs text-gray-500 dark:text-gray-400">{stat.label}</span>
          </div>
          <p className={`text-xl font-bold ${stat.color}`}>{stat.value}</p>
        </div>
      ))}
    </div>
  );
};