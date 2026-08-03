// src/components/Analytics/AnalyticsCost.tsx
interface CostData {
  total_cost: number;
  qlora_cost: number;
  deepseek_cost: number;
  cost_per_query: number;
  cost_per_user: number;
  savings: number;
  savings_percentage: number;
}

interface Props {
  data: CostData;
}

export const AnalyticsCost = ({ data }: Props) => {
  // Calculate percentages for the bar
  const total = data.qlora_cost + data.deepseek_cost;
  const qloraPct = total > 0 ? (data.qlora_cost / total) * 100 : 50;
  const deepseekPct = total > 0 ? (data.deepseek_cost / total) * 100 : 50;

  return (
    <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-700">
      <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
        💰 Cost Analytics
      </h3>

      <div className="grid grid-cols-2 gap-2 mb-4">
        <div className="p-2 bg-white dark:bg-gray-900/50 rounded-lg text-center">
          <p className="text-lg font-bold text-gray-900 dark:text-white">
            ${data.total_cost.toFixed(3)}
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400">Total Cost</p>
        </div>
        <div className="p-2 bg-white dark:bg-gray-900/50 rounded-lg text-center">
          <p className="text-lg font-bold text-green-600 dark:text-green-400">
            ${data.savings.toFixed(3)}
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400">Saved ({data.savings_percentage}%)</p>
        </div>
      </div>

      {/* Cost Breakdown Bar */}
      <div className="mb-3">
        <div className="flex justify-between text-sm mb-1">
          <span className="text-gray-600 dark:text-gray-400">QLoRA</span>
          <span className="font-medium text-green-600 dark:text-green-400">
            ${data.qlora_cost.toFixed(3)} ({qloraPct.toFixed(0)}%)
          </span>
        </div>
        <div className="w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-green-500 to-emerald-500 rounded-full transition-all duration-500"
            style={{ width: `${qloraPct}%` }}
          />
        </div>
      </div>

      <div className="mb-4">
        <div className="flex justify-between text-sm mb-1">
          <span className="text-gray-600 dark:text-gray-400">DeepSeek</span>
          <span className="font-medium text-blue-600 dark:text-blue-400">
            ${data.deepseek_cost.toFixed(3)} ({deepseekPct.toFixed(0)}%)
          </span>
        </div>
        <div className="w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full transition-all duration-500"
            style={{ width: `${deepseekPct}%` }}
          />
        </div>
      </div>

      {/* Cost per Query & User */}
      <div className="flex justify-between pt-2 border-t border-gray-200 dark:border-gray-700 text-sm">
        <div>
          <span className="text-gray-500 dark:text-gray-400">Cost/Query</span>
          <span className="ml-2 font-medium text-gray-900 dark:text-white">
            ${data.cost_per_query.toFixed(3)}
          </span>
        </div>
        <div>
          <span className="text-gray-500 dark:text-gray-400">Cost/User</span>
          <span className="ml-2 font-medium text-gray-900 dark:text-white">
            ${data.cost_per_user.toFixed(3)}
          </span>
        </div>
      </div>
    </div>
  );
};