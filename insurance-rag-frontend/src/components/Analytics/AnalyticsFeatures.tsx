// src/components/Analytics/AnalyticsFeatures.tsx
interface FeatureData {
  total_calls: number;
  feature_usage: Record<string, number>;
  most_used: Array<{ name: string; count: number }>;
  least_used: Array<{ name: string; count: number }>;
}

interface Props {
  data: FeatureData;
}

export const AnalyticsFeatures = ({ data }: Props) => {
  return (
    <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-700">
      <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
        📋 Feature Adoption
      </h3>

      <div className="grid grid-cols-2 gap-2 mb-4">
        <div className="p-2 bg-white dark:bg-gray-900/50 rounded-lg text-center">
          <p className="text-lg font-bold text-gray-900 dark:text-white">
            {data.total_calls.toLocaleString()}
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400">Total Feature Calls</p>
        </div>
        <div className="p-2 bg-white dark:bg-gray-900/50 rounded-lg text-center">
          <p className="text-lg font-bold text-green-600 dark:text-green-400">
            {Object.keys(data.feature_usage).length}
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400">Active Features</p>
        </div>
      </div>

      {/* Most Used */}
      <div className="mb-3">
        <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">
          🔥 Most Used
        </p>
        <div className="space-y-1">
          {data.most_used.slice(0, 3).map((item, i) => (
            <div key={i} className="flex items-center justify-between px-2 py-1 bg-white dark:bg-gray-900/50 rounded-lg">
              <span className="text-sm text-gray-700 dark:text-gray-300">{item.name}</span>
              <span className="text-sm font-medium text-gray-900 dark:text-white">{item.count}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Least Used */}
      {data.least_used.length > 0 && (
        <div>
          <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">
            💤 Least Used
          </p>
          <div className="space-y-1">
            {data.least_used.slice(0, 2).map((item, i) => (
              <div key={i} className="flex items-center justify-between px-2 py-1 bg-white dark:bg-gray-900/50 rounded-lg">
                <span className="text-sm text-gray-500 dark:text-gray-400">{item.name}</span>
                <span className="text-sm font-medium text-gray-500">{item.count}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};