import { motion, AnimatePresence } from 'framer-motion';
import { 
  TrendingUp, 
  Car, 
  Shield, 
  DollarSign, 
  ChevronDown,
  BarChart3,
  CheckCircle,
  Sparkles
} from 'lucide-react';
import { useState } from 'react';

interface PremiumData {
  monthly: number;
  yearly: number;
  breakdown: Array<{
    step: number;
    label: string;
    value: string;
    description: string;
  }>;
  summary: string;
  tip: string;
}

export const PremiumQuote = ({ data }: { data: PremiumData }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 overflow-hidden max-w-2xl">
      <div className="bg-gradient-to-br from-blue-600 to-blue-700 px-6 py-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-white/20 p-2 rounded-xl backdrop-blur-sm">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-white font-semibold text-lg">Premium Quote</h3>
              <p className="text-blue-100 text-sm">Auto Insurance • Comprehensive</p>
            </div>
          </div>
          <div className="flex items-center gap-2 bg-white/20 px-3 py-1.5 rounded-full backdrop-blur-sm">
            <CheckCircle className="w-3.5 h-3.5 text-green-300" />
            <span className="text-xs text-white font-medium">Calculated</span>
          </div>
        </div>
      </div>

      <div className="p-6">
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.4, type: "spring" }}
          className="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-xl p-6 border border-green-200 dark:border-green-800"
        >
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Monthly Premium</p>
              <div className="flex items-baseline gap-2">
                <span className="text-4xl font-bold text-green-700 dark:text-green-400">${data.monthly}</span>
                <span className="text-sm text-gray-500 dark:text-gray-400">/ month</span>
              </div>
            </div>
            <div className="flex items-center gap-6">
              <div>
                <p className="text-xs text-gray-500 dark:text-gray-400">Yearly Total</p>
                <p className="text-lg font-semibold text-gray-700 dark:text-gray-300">${data.yearly}</p>
              </div>
              <div className="w-px h-10 bg-gray-300 dark:bg-gray-600" />
              <div>
                <p className="text-xs text-gray-500 dark:text-gray-400">Coverage</p>
                <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Comprehensive</p>
              </div>
            </div>
          </div>
        </motion.div>

        <button
          onClick={() => setExpanded(!expanded)}
          className="mt-4 flex items-center gap-2 text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 transition-colors"
        >
          <BarChart3 className="w-4 h-4" />
          <span>See Calculation Breakdown</span>
          <ChevronDown className={`w-4 h-4 transition-transform duration-200 ${expanded ? 'rotate-180' : ''}`} />
        </button>

        <AnimatePresence>
          {expanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="overflow-hidden"
            >
              <div className="mt-4 space-y-3">
                {data.breakdown.map((step, index) => (
                  <motion.div
                    key={step.step}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-gray-200 dark:border-gray-700"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-7 h-7 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 text-xs font-bold flex items-center justify-center">
                        {step.step}
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-800 dark:text-gray-200">{step.label}</p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">{step.description}</p>
                      </div>
                    </div>
                    <span className="text-sm font-mono font-bold text-blue-600 dark:text-blue-400">{step.value}</span>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <div className="mt-4 flex items-start gap-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
          <TrendingUp className="w-4 h-4 text-blue-500 dark:text-blue-400 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-gray-700 dark:text-gray-300">{data.summary}</p>
        </div>

        <div className="mt-2 flex items-start gap-3 p-3 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800">
          <DollarSign className="w-4 h-4 text-amber-500 dark:text-amber-400 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-gray-700 dark:text-gray-300">{data.tip}</p>
        </div>

        <div className="mt-4 flex flex-wrap gap-3">
          <button className="flex-1 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors shadow-sm hover:shadow-md">
            Get Full Quote
          </button>
          <button className="px-4 py-2.5 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200 text-sm font-medium rounded-lg transition-colors">
            Compare
          </button>
          <button className="px-4 py-2.5 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200 text-sm font-medium rounded-lg transition-colors">
            Export PDF
          </button>
        </div>
      </div>
    </div>
  );
};