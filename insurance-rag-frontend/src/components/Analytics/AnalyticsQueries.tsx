// src/components/Analytics/AnalyticsQueries.tsx
interface QueryData {
  total_queries: number;
  categories: {
    premium: number;
    claim: number;
    comparison: number;
    coverage: number;
    general: number;
  };
  daily_queries: Array<{ date: string; count: number }>;
  peak_hour: number;
}

interface Props {
  data: QueryData;
}

export const AnalyticsQueries = ({ data }: Props) => {
  const categories = [
    { name: 'Premium', count: data.categories.premium, color: 'blue' },
    { name: 'Claim', count: data.categories.claim, color: 'orange' },
    { name: 'Comparison', count: data.categories.comparison, color: 'purple' },
    { name: 'Coverage', count: data.categories.coverage, color: 'green' },
    { name: 'General', count: data.categories.general, color: 'gray' },
  ];

  const total = data.total_queries || 1;

  return (
    <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-700">
      <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
        🔍 Query Analytics
      </h3>

      <div className="grid grid-cols-2 gap-2 mb-4">
        <div className="p-2 bg-white dark:bg-gray-900/50 rounded-lg text-center">
          <p className="text-lg font-bold text-gray-900 dark:text-white">
            {data.total_queries.toLocaleString()}
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400">Total Queries</p>
        </div>
        <div className="p-2 bg-white dark:bg-gray-900/50 rounded-lg text-center">
          <p className="text-lg font-bold text-purple-600 dark:text-purple-400">
            {data.peak_hour}:00
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400">Peak Hour</p>
        </div>
      </div>

      {/* Category Breakdown */}
      <div className="space-y-1.5">
        {categories.map((cat) => {
          const pct = (cat.count / total) * 100;
          const colorMap = {
            blue: 'bg-blue-500',
            orange: 'bg-orange-500',
            purple: 'bg-purple-500',
            green: 'bg-green-500',
            gray: 'bg-gray-500',
          };
          return (
            <div key={cat.name}>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600 dark:text-gray-400">{cat.name}</span>
                <span className="font-medium text-gray-900 dark:text-white">
                  {cat.count} ({pct.toFixed(1)}%)
                </span>
              </div>
              <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <div
                  className={`h-full ${colorMap[cat.color as keyof typeof colorMap]} rounded-full transition-all duration-500`}
                  style={{ width: `${pct}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* Daily Queries Trend (simple) */}
      {data.daily_queries.length > 0 && (
        <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-1.5">
            📈 Daily Trend (Last 7 Days)
          </p>
          <div className="flex items-end gap-1 h-12">
            {data.daily_queries.slice(-7).map((day, i) => {
              const max = Math.max(...data.daily_queries.slice(-7).map(d => d.count), 1);
              const height = (day.count / max) * 100;
              return (
                <div key={i} className="flex-1 flex flex-col items-center">
                  <div
                    className="w-full bg-blue-500 rounded-t transition-all duration-500"
                    style={{ height: `${Math.max(height, 2)}%` }}
                  />
                  <span className="text-[8px] text-gray-400 mt-0.5">
                    {new Date(day.date).toLocaleDateString('en-US', { weekday: 'short' })}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};