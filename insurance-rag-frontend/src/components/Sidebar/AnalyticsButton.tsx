import { BarChart3, ChevronRight } from 'lucide-react';
import { useState } from 'react';

export const AnalyticsButton = () => {
  const [hovered, setHovered] = useState(false);

  return (
    <div className="border-t border-gray-200 dark:border-gray-700 pt-3">
      <button
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
        className="flex items-center justify-between w-full px-3 py-2.5 bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-950/30 dark:to-purple-950/30 hover:from-indigo-100 hover:to-purple-100 dark:hover:from-indigo-950/50 dark:hover:to-purple-950/50 rounded-lg transition-all duration-200 border border-indigo-200 dark:border-indigo-800"
      >
        <div className="flex items-center gap-2">
          <BarChart3 className={`w-4 h-4 transition-colors ${hovered ? 'text-indigo-600 dark:text-indigo-400' : 'text-gray-500 dark:text-gray-400'}`} />
          <span className={`text-sm font-medium transition-colors ${hovered ? 'text-indigo-700 dark:text-indigo-300' : 'text-gray-700 dark:text-gray-300'}`}>
            Analytics
          </span>
        </div>
        <ChevronRight className={`w-4 h-4 transition-all ${hovered ? 'text-indigo-600 dark:text-indigo-400 translate-x-0.5' : 'text-gray-400'}`} />
      </button>
      <p className="text-[10px] text-gray-400 dark:text-gray-500 mt-1 px-1">Coming soon - Phase 7</p>
    </div>
  );
};