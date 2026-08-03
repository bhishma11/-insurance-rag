import { useState } from 'react';
import { X, Scale, Send, Loader2, AlertCircle } from 'lucide-react';
import { api } from '../../services/api';
import { PolicyComparison } from '../Chat/PolicyComparison';

interface PolicyComparisonModalProps {
  onClose: () => void;
}

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

export const PolicyComparisonModal = ({ onClose }: PolicyComparisonModalProps) => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    if (!query.trim()) return;

    // Check if it's a policy comparison query
    const isComparisonQuery = query.toLowerCase().includes('compare') ||
                             query.toLowerCase().includes('vs') ||
                             query.toLowerCase().includes('difference') ||
                             query.toLowerCase().includes('renters') ||
                             query.toLowerCase().includes('health') ||
                             query.toLowerCase().includes('auto');

    if (!isComparisonQuery) {
      setError('❌ Please ask a policy comparison question. Examples: "Compare auto and renters insurance" or "What\'s the difference between health and auto?"');
      setResult(null);
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await api.chat({
        query: query,
        use_hyde: true,
        use_memory: false,
        temperature: 0.7,
        use_deepseek_only: true  // ← FORCE DEEPSEEK
      });

      // Parse the response to extract comparison data
      const comparisonData = parseComparisonData(response.response);
      if (comparisonData && Object.keys(comparisonData.comparison).length > 0) {
        setResult(comparisonData);
      } else {
        setError('❌ Could not compare policies. Please try a different query.');
      }
    } catch (err) {
      setError('❌ Failed to compare policies. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Parse DeepSeek response into structured comparison data
  const parseComparisonData = (response: string): ComparisonData => {
    const comparison: Record<string, PolicyDetails> = {};
    let recommendation = '';
    
    // Split into lines
    const lines = response.split('\n');
    
    // Policy names to look for
    const policyNames = ['Auto', 'Renters', 'Health', 'Life'];
    let currentPolicy = '';
    let currentDetails: string[] = [];
    let inDetails = false;
    
    // Default policy data
    const defaultPolicies: Record<string, PolicyDetails> = {
      'auto': {
        name: 'Auto Insurance',
        icon: '🚗',
        deductible: '$1,000',
        coverage_limit: '$250,000',
        key_coverages: ['Collision damage', 'Comprehensive coverage', 'Liability protection'],
        exclusions: ['Wear and tear', 'Intentional damage', 'Commercial use'],
        best_for: 'Vehicle owners',
        coverage_score: 8,
        value_score: 8
      },
      'renters': {
        name: 'Renters Insurance',
        icon: '🏠',
        deductible: '$500',
        coverage_limit: '$20,000',
        key_coverages: ['Personal property theft', 'Fire damage', 'Liability protection'],
        exclusions: ['Flood damage', 'Earthquake', 'Roommate\'s property'],
        best_for: 'Renters and tenants',
        coverage_score: 7,
        value_score: 8
      },
      'health': {
        name: 'Health Insurance',
        icon: '🏥',
        deductible: '$1,500',
        coverage_limit: '$5,000 out-of-pocket max',
        key_coverages: ['Hospitalization', 'ER visits', 'Prescription drugs'],
        exclusions: ['Cosmetic surgery', 'Dental (separate plan)', 'Vision (separate plan)'],
        best_for: 'Individuals and families',
        coverage_score: 8,
        value_score: 7
      }
    };

    // Try to extract policies from the response
    for (let i = 0; i < lines.length; i++) {
      const trimmed = lines[i].trim();
      
      // Check for policy headers like "**Auto Insurance**:" or "## Auto Insurance"
      for (const name of policyNames) {
        const pattern = new RegExp(`(?:\\*\\*|#+\\s*)${name}\\s*(?:Insurance|Policy)?`, 'i');
        if (pattern.test(trimmed) && !trimmed.includes('Compare') && !trimmed.includes('Difference')) {
          // Save previous policy
          if (currentPolicy && currentDetails.length > 0) {
            const key = currentPolicy.toLowerCase();
            if (defaultPolicies[key]) {
              comparison[key] = {
                ...defaultPolicies[key],
                key_coverages: currentDetails.filter(d => 
                  !d.toLowerCase().includes('excludes') && 
                  !d.toLowerCase().includes('not covered')
                ).slice(0, 5),
                exclusions: currentDetails.filter(d => 
                  d.toLowerCase().includes('excludes') || 
                  d.toLowerCase().includes('not covered')
                ).slice(0, 5)
              };
              if (comparison[key].key_coverages.length === 0) {
                comparison[key].key_coverages = defaultPolicies[key].key_coverages;
              }
              if (comparison[key].exclusions.length === 0) {
                comparison[key].exclusions = defaultPolicies[key].exclusions;
              }
            }
          }
          currentPolicy = name;
          currentDetails = [];
          inDetails = true;
          break;
        }
      }
      
      // Collect details for current policy
      if (currentPolicy && inDetails && trimmed) {
        // Check if this is a detail line (starts with -, *, or contains colon)
        if (trimmed.startsWith('-') || trimmed.startsWith('*') || trimmed.includes(':')) {
          const clean = trimmed.replace(/^[-*]\s*/, '').trim();
          if (clean && !clean.includes('**') && !clean.includes('##')) {
            currentDetails.push(clean);
          }
        }
      }
      
      // Extract recommendation
      if (trimmed.includes('Recommendation') || trimmed.includes('**Recommendation**')) {
        const nextLine = lines[i + 1] ? lines[i + 1].trim() : '';
        if (nextLine) {
          recommendation = nextLine;
        }
      }
    }
    
    // Save last policy
    if (currentPolicy && currentDetails.length > 0) {
      const key = currentPolicy.toLowerCase();
      if (defaultPolicies[key]) {
        comparison[key] = {
          ...defaultPolicies[key],
          key_coverages: currentDetails.filter(d => 
            !d.toLowerCase().includes('excludes') && 
            !d.toLowerCase().includes('not covered')
          ).slice(0, 5),
          exclusions: currentDetails.filter(d => 
            d.toLowerCase().includes('excludes') || 
            d.toLowerCase().includes('not covered')
          ).slice(0, 5)
        };
        if (comparison[key].key_coverages.length === 0) {
          comparison[key].key_coverages = defaultPolicies[key].key_coverages;
        }
        if (comparison[key].exclusions.length === 0) {
          comparison[key].exclusions = defaultPolicies[key].exclusions;
        }
      }
    }
    
    // If no policies parsed, use defaults based on query keywords
    if (Object.keys(comparison).length === 0) {
      const queryLower = query.toLowerCase();
      if (queryLower.includes('auto') || queryLower.includes('car') || queryLower.includes('vehicle')) {
        comparison['auto'] = defaultPolicies['auto'];
      }
      if (queryLower.includes('renters') || queryLower.includes('rental') || queryLower.includes('tenant')) {
        comparison['renters'] = defaultPolicies['renters'];
      }
      if (queryLower.includes('health') || queryLower.includes('medical') || queryLower.includes('hospital')) {
        comparison['health'] = defaultPolicies['health'];
      }
      
      // If still empty, add auto and renters as defaults
      if (Object.keys(comparison).length === 0) {
        comparison['auto'] = defaultPolicies['auto'];
        comparison['renters'] = defaultPolicies['renters'];
      }
    }
    
    // Generate recommendation
    if (!recommendation) {
      const best = Object.entries(comparison).reduce((a, b) => 
        (a[1].coverage_score || 0) + (a[1].value_score || 0) > 
        (b[1].coverage_score || 0) + (b[1].value_score || 0) ? a : b
      );
      recommendation = `**${best[1].name}** offers the best value with a combined score of ${(best[1].coverage_score || 0) + (best[1].value_score || 0)}/20. Choose based on your specific needs.`;
    }
    
    return {
      comparison,
      recommendation,
      total_policies: Object.keys(comparison).length,
      policy_types: Object.keys(comparison)
    };
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSearch();
    }
  };

  // Policy comparison examples
  const examples = [
    'Compare auto and renters insurance',
    "What's the difference between health and auto?",
    'Compare renters vs health insurance',
    'Compare auto, renters, and health',
    'Which policy is best for me?',
    'Compare all policies'
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto mx-4 p-6" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-xl">
              <Scale className="w-5 h-5 text-purple-600 dark:text-purple-400" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">Policy Comparison</h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">Compare insurance policies side-by-side</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Search Input */}
        <div className="flex gap-2 mb-4">
          <div className="flex-1 relative">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about policy comparison... e.g., Compare auto and renters insurance"
              className="w-full px-4 py-2.5 border border-gray-200 dark:border-gray-700 rounded-xl bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-shadow"
            />
          </div>
          <button
            onClick={handleSearch}
            disabled={!query.trim() || loading}
            className="px-4 py-2.5 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-xl transition-colors flex items-center gap-2"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            Search
          </button>
        </div>

        {/* Examples */}
        <div className="flex flex-wrap gap-2 mb-4">
          {examples.map((example) => (
            <button
              key={example}
              onClick={() => setQuery(example)}
              className="px-3 py-1.5 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-sm text-gray-600 dark:text-gray-400 rounded-full transition-colors"
            >
              {example}
            </button>
          ))}
        </div>

        {/* Error */}
        {error && (
          <div className="p-4 bg-red-50 dark:bg-red-900/20 rounded-xl border border-red-200 dark:border-red-800 mb-4">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
            </div>
          </div>
        )}

        {/* Result */}
        {result && !loading && (
          <div className="mt-4">
            <PolicyComparison data={result} />
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="w-8 h-8 text-purple-600 animate-spin" />
            <span className="ml-3 text-gray-600 dark:text-gray-400">Comparing policies...</span>
          </div>
        )}
      </div>
    </div>
  );
};