// src/components/Analytics/AnalyticsCharts.tsx
import { AnalyticsStats } from '../../types';

interface Props {
  data: AnalyticsStats;
}

export const AnalyticsCharts = ({ data }: Props) => {
  // Calculate percentages
  const totalQueries = data.queries.total_queries || 1;
  const premiumPct = (data.queries.categories.premium / totalQueries) * 100;
  const claimPct = (data.queries.categories.claim / totalQueries) * 100;
  const comparisonPct = (data.queries.categories.comparison / totalQueries) * 100;
  const coveragePct = (data.queries.categories.coverage / totalQueries) * 100;
  const generalPct = (data.queries.categories.general / totalQueries) * 100;

  // Feature usage for bar chart
  const features = data.features.most_used || [];
  const maxFeatureCount = features.length > 0 ? features[0].count : 1;

  // Daily queries for line chart (mock data for now)
  const dailyData = data.queries.daily_queries || [];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {/* Query Categories - Bar Chart */}
      <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-700">
        <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
          📊 Query Categories
        </h3>
        <div className="space-y-2">
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-600 dark:text-gray-400">Premium</span>
              <span className="font-medium text-blue-600 dark:text-blue-400">
                {premiumPct.toFixed(1)}% ({data.queries.categories.premium})
              </span>
            </div>
            <div className="w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full transition-all duration-500"
                style={{ width: `${premiumPct}%` }}
              />
            </div>
          </div>
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-600 dark:text-gray-400">Claim</span>
              <span className="font-medium text-orange-500">
                {claimPct.toFixed(1)}% ({data.queries.categories.claim})
              </span>
            </div>
            <div className="w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-orange-500 to-red-500 rounded-full transition-all duration-500"
                style={{ width: `${claimPct}%` }}
              />
            </div>
          </div>
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-600 dark:text-gray-400">Comparison</span>
              <span className="font-medium text-purple-500">
                {comparisonPct.toFixed(1)}% ({data.queries.categories.comparison})
              </span>
            </div>
            <div className="w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full transition-all duration-500"
                style={{ width: `${comparisonPct}%` }}
              />
            </div>
          </div>
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-600 dark:text-gray-400">Coverage</span>
              <span className="font-medium text-green-500">
                {coveragePct.toFixed(1)}% ({data.queries.categories.coverage})
              </span>
            </div>
            <div className="w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-green-500 to-emerald-500 rounded-full transition-all duration-500"
                style={{ width: `${coveragePct}%` }}
              />
            </div>
          </div>
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-600 dark:text-gray-400">General</span>
              <span className="font-medium text-gray-500">
                {generalPct.toFixed(1)}% ({data.queries.categories.general})
              </span>
            </div>
            <div className="w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-gray-400 to-gray-500 rounded-full transition-all duration-500"
                style={{ width: `${generalPct}%` }}
              />
            </div>
          </div>
        </div>
        <div className="mt-3 text-xs text-gray-500 dark:text-gray-400">
          Total queries: {data.queries.total_queries.toLocaleString()}
        </div>
      </div>

      {/* Feature Usage - Horizontal Bar Chart */}
      <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-700">
        <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
          🛠️ Top Features
        </h3>
        {features.length === 0 ? (
          <div className="text-center py-4 text-gray-500 dark:text-gray-400 text-sm">
            No feature usage data yet
          </div>
        ) : (
          <div className="space-y-2">
            {features.slice(0, 5).map((feature, i) => {
              const pct = (feature.count / maxFeatureCount) * 100;
              const colors = ['blue', 'green', 'purple', 'orange', 'pink'];
              const color = colors[i % colors.length];
              const gradColors = {
                blue: 'from-blue-500 to-blue-600',
                green: 'from-green-500 to-emerald-600',
                purple: 'from-purple-500 to-purple-600',
                orange: 'from-orange-500 to-orange-600',
                pink: 'from-pink-500 to-pink-600',
              };
              return (
                <div key={i}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600 dark:text-gray-400 truncate max-w-[150px]">
                      {feature.name}
                    </span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {feature.count}
                    </span>
                  </div>
                  <div className="w-full h-2.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className={`h-full bg-gradient-to-r ${gradColors[color as keyof typeof gradColors]} rounded-full transition-all duration-500`}
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};