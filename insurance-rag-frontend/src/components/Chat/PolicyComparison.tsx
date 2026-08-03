import { motion, AnimatePresence } from 'framer-motion';
import { 
  Scale, 
  TrendingUp, 
  DollarSign, 
  Shield, 
  CheckCircle, 
  XCircle,
  Star,
  Info,
  ChevronDown,
  ChevronUp,
  Zap,
  Award,
  FileText
} from 'lucide-react';
import { useState } from 'react';

interface PolicyDetails {
  name?: string;
  icon?: string;
  deductible: string;
  coverage_limit: string;
  monthly_premium?: string;
  annual_premium?: string;
  key_coverages: string[];
  exclusions: string[];
  best_for?: string;
  coverage_score?: number;
  value_score?: number;
  claims_process?: string;
  avg_claim_time?: string;
  discounts?: string[];
}

interface ComparisonData {
  comparison: Record<string, PolicyDetails>;
  recommendation: string;
  total_policies: number;
  policy_types?: string[];
}

export const PolicyComparison = ({ data }: { data: ComparisonData }) => {
  const [expandedPolicy, setExpandedPolicy] = useState<string | null>(null);

  // Safety check: if comparison is empty or invalid
  if (!data || !data.comparison || Object.keys(data.comparison).length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 p-6 text-center">
        <p className="text-gray-500 dark:text-gray-400">No policies to compare. Please try a different query.</p>
      </div>
    );
  }

  const policyNames = Object.keys(data.comparison);
  const colors = ['blue', 'green', 'purple', 'orange'];
  const bgColors = ['bg-blue-50/80 dark:bg-blue-900/20', 'bg-green-50/80 dark:bg-green-900/20', 'bg-purple-50/80 dark:bg-purple-900/20', 'bg-orange-50/80 dark:bg-orange-900/20'];
  const borderColors = ['border-blue-200 dark:border-blue-800', 'border-green-200 dark:border-green-800', 'border-purple-200 dark:border-purple-800', 'border-orange-200 dark:border-orange-800'];
  const textColors = ['text-blue-600 dark:text-blue-400', 'text-green-600 dark:text-green-400', 'text-purple-600 dark:text-purple-400', 'text-orange-600 dark:text-orange-400'];
  const gradientColors = ['from-blue-500 to-blue-600', 'from-green-500 to-green-600', 'from-purple-500 to-purple-600', 'from-orange-500 to-orange-600'];

  const toggleExpand = (policyName: string) => {
    setExpandedPolicy(expandedPolicy === policyName ? null : policyName);
  };

  const getBestPolicy = () => {
    let best = null;
    let bestScore = 0;
    for (const [name, details] of Object.entries(data.comparison)) {
      const score = (details.coverage_score || 0) + (details.value_score || 0);
      if (score > bestScore) {
        bestScore = score;
        best = name;
      }
    }
    return best;
  };

  const bestPolicy = getBestPolicy();

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 overflow-hidden w-full">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-500 px-6 py-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-white/20 p-2 rounded-xl backdrop-blur-sm">
              <Scale className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-white font-bold text-xl">Policy Comparison</h3>
              <p className="text-indigo-200 text-sm">
                {policyNames.length} policies compared • {data.total_policies || policyNames.length} total
              </p>
            </div>
          </div>
          {bestPolicy && (
            <div className="flex items-center gap-2 bg-amber-400/30 px-3 py-1.5 rounded-full backdrop-blur-sm border border-amber-400/50">
              <Award className="w-4 h-4 text-amber-300" />
              <span className="text-xs text-amber-100 font-medium">
                Best Pick: {data.comparison[bestPolicy].name || bestPolicy}
              </span>
            </div>
          )}
        </div>
      </div>

      <div className="p-6 md:p-8">
        {/* Comparison Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {policyNames.map((name, index) => {
            const details = data.comparison[name];
            
            // Safety check: if details is undefined, skip this policy
            if (!details || typeof details !== 'object') {
              return null;
            }

            const color = colors[index % colors.length];
            const bgColor = bgColors[index % bgColors.length];
            const borderColor = borderColors[index % borderColors.length];
            const textColor = textColors[index % textColors.length];
            const gradientColor = gradientColors[index % gradientColors.length];
            const isBest = name === bestPolicy;
            const isExpanded = expandedPolicy === name;

            return (
              <motion.div
                key={name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`rounded-xl border-2 ${borderColor} ${bgColor} p-5 transition-all hover:shadow-lg ${
                  isBest ? 'ring-2 ring-amber-400 ring-offset-2 shadow-lg' : ''
                }`}
              >
                {/* Policy Header */}
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <span className="text-3xl">{details.icon || '📋'}</span>
                    <h4 className={`font-bold text-lg ${textColor}`}>
                      {details.name || name}
                    </h4>
                  </div>
                  {isBest && (
                    <span className="flex items-center gap-1 text-xs bg-amber-100 dark:bg-amber-900/50 text-amber-700 dark:text-amber-300 px-3 py-1 rounded-full font-medium">
                      <Star className="w-3 h-3 fill-amber-500 text-amber-500" />
                      Best Value
                    </span>
                  )}
                </div>

                {/* Monthly Premium */}
                {details.monthly_premium && (
                  <div className="mb-4 p-3 bg-white/60 dark:bg-gray-800/60 rounded-lg border border-gray-200 dark:border-gray-700">
                    <div className="text-center">
                      <p className="text-xs text-gray-500 dark:text-gray-400">Monthly Premium</p>
                      <p className="text-2xl font-bold text-gray-900 dark:text-white">
                        {details.monthly_premium}
                      </p>
                    </div>
                  </div>
                )}

                {/* Key Metrics */}
                <div className="space-y-3 text-base">
                  <div className="flex flex-col p-3 bg-white/40 dark:bg-gray-800/40 rounded-lg border border-gray-200 dark:border-gray-700">
                    <span className="text-xs text-gray-500 dark:text-gray-400 font-medium">Deductible</span>
                    <span className="text-base font-semibold text-gray-800 dark:text-gray-200 break-words">
                      {details.deductible || 'N/A'}
                    </span>
                  </div>
                  <div className="flex flex-col p-3 bg-white/40 dark:bg-gray-800/40 rounded-lg border border-gray-200 dark:border-gray-700">
                    <span className="text-xs text-gray-500 dark:text-gray-400 font-medium">Coverage Limit</span>
                    <span className="text-base font-semibold text-gray-800 dark:text-gray-200 break-words">
                      {details.coverage_limit || 'N/A'}
                    </span>
                  </div>
                </div>

                {/* Score Bars */}
                <div className="mt-4 space-y-2">
                  {details.coverage_score !== undefined && (
                    <div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600 dark:text-gray-400 font-medium">Coverage Score</span>
                        <span className={`font-bold ${textColor}`}>
                          {details.coverage_score}/10
                        </span>
                      </div>
                      <div className="w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${((details.coverage_score || 0) / 10) * 100}%` }}
                          transition={{ delay: 0.2 + index * 0.1, duration: 0.6 }}
                          className={`h-full rounded-full bg-gradient-to-r ${gradientColor}`}
                        />
                      </div>
                    </div>
                  )}
                  {details.value_score !== undefined && (
                    <div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600 dark:text-gray-400 font-medium">Value Score</span>
                        <span className={`font-bold ${textColor}`}>
                          {details.value_score}/10
                        </span>
                      </div>
                      <div className="w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${((details.value_score || 0) / 10) * 100}%` }}
                          transition={{ delay: 0.3 + index * 0.1, duration: 0.6 }}
                          className={`h-full rounded-full bg-gradient-to-r ${gradientColor}`}
                        />
                      </div>
                    </div>
                  )}
                </div>

                {/* Expand Button */}
                <button
                  onClick={() => toggleExpand(name)}
                  className="mt-4 w-full flex items-center justify-center gap-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors py-2 border-t border-gray-200 dark:border-gray-700 pt-3"
                >
                  {isExpanded ? (
                    <>
                      <ChevronUp className="w-4 h-4" />
                      <span>Hide Details</span>
                    </>
                  ) : (
                    <>
                      <ChevronDown className="w-4 h-4" />
                      <span>View Full Details</span>
                    </>
                  )}
                </button>

                {/* Expanded Details */}
                <AnimatePresence>
                  {isExpanded && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.3 }}
                      className="overflow-hidden"
                    >
                      <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700 space-y-3 text-sm">
                        {/* Key Coverages */}
                        {details.key_coverages && details.key_coverages.length > 0 && (
                          <div>
                            <p className="font-bold text-gray-800 dark:text-gray-200 mb-2 flex items-center gap-2">
                              <CheckCircle className="w-4 h-4 text-green-500" />
                              Key Coverages
                            </p>
                            <ul className="space-y-1.5 text-gray-600 dark:text-gray-400">
                              {details.key_coverages.map((coverage, i) => (
                                <li key={i} className="flex items-start gap-2">
                                  <CheckCircle className="w-3.5 h-3.5 text-green-500 flex-shrink-0 mt-0.5" />
                                  <span>{coverage}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                        
                        {/* Exclusions */}
                        {details.exclusions && details.exclusions.length > 0 && (
                          <div>
                            <p className="font-bold text-gray-800 dark:text-gray-200 mb-2 flex items-center gap-2">
                              <XCircle className="w-4 h-4 text-red-500" />
                              Exclusions
                            </p>
                            <ul className="space-y-1.5 text-gray-600 dark:text-gray-400">
                              {details.exclusions.map((exclusion, i) => (
                                <li key={i} className="flex items-start gap-2">
                                  <XCircle className="w-3.5 h-3.5 text-red-400 flex-shrink-0 mt-0.5" />
                                  <span>{exclusion}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {/* Best For */}
                        {details.best_for && (
                          <div className="flex items-center gap-2 p-2 bg-white/60 dark:bg-gray-800/60 rounded-lg border border-gray-200 dark:border-gray-700">
                            <Info className="w-4 h-4 text-blue-500 flex-shrink-0" />
                            <span className="text-sm text-gray-600 dark:text-gray-400">
                              <span className="font-medium">Best for:</span> {details.best_for}
                            </span>
                          </div>
                        )}

                        {/* Additional Info */}
                        {details.claims_process && (
                          <div className="flex items-center gap-2 p-2 bg-white/60 dark:bg-gray-800/60 rounded-lg border border-gray-200 dark:border-gray-700">
                            <Zap className="w-4 h-4 text-amber-500 flex-shrink-0" />
                            <span className="text-sm text-gray-600 dark:text-gray-400">
                              <span className="font-medium">Claims:</span> {details.claims_process}
                            </span>
                          </div>
                        )}

                        {details.discounts && details.discounts.length > 0 && (
                          <div className="p-2 bg-white/60 dark:bg-gray-800/60 rounded-lg border border-gray-200 dark:border-gray-700">
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                              <span className="font-medium">💰 Discounts:</span> {details.discounts.join(', ')}
                            </p>
                          </div>
                        )}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            );
          })}
        </div>

        {/* Recommendation */}
        {data.recommendation && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="p-5 bg-gradient-to-r from-amber-50 to-yellow-50 dark:from-amber-950/30 dark:to-yellow-950/30 rounded-xl border-2 border-amber-200 dark:border-amber-800"
          >
            <div className="flex items-start gap-3">
              <div className="bg-amber-100 dark:bg-amber-900/50 p-2 rounded-full">
                <Star className="w-6 h-6 text-amber-500" />
              </div>
              <div>
                <p className="text-base font-bold text-gray-800 dark:text-gray-200">Recommendation</p>
                <p className="text-base text-gray-700 dark:text-gray-300 leading-relaxed">{data.recommendation}</p>
              </div>
            </div>
          </motion.div>
        )}

        {/* Action Buttons */}
        <div className="mt-8 flex flex-wrap gap-3">
          <button className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white text-sm font-semibold rounded-xl transition-all shadow-md hover:shadow-lg flex items-center gap-2">
            <Zap className="w-4 h-4" />
            Get Quote for Best Policy
          </button>
          <button className="px-6 py-3 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200 text-sm font-semibold rounded-xl transition-all flex items-center gap-2">
            <Scale className="w-4 h-4" />
            Compare All Details
          </button>
          <button className="px-6 py-3 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200 text-sm font-semibold rounded-xl transition-all flex items-center gap-2">
            <FileText className="w-4 h-4" />
            Export Comparison
          </button>
        </div>
      </div>
    </div>
  );
};