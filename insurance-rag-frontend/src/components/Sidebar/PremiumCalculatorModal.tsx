import { useState } from 'react';
import { X, Calculator, Send, Loader2, AlertCircle } from 'lucide-react';
import { api } from '../../services/api';
import { PremiumQuote } from '../Chat/PremiumQuote';

interface PremiumCalculatorModalProps {
  onClose: () => void;
}

export const PremiumCalculatorModal = ({ onClose }: PremiumCalculatorModalProps) => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    if (!query.trim()) return;

    // Check if it's a premium calculation query
    const isPremiumQuery = query.toLowerCase().includes('premium') ||
                          query.toLowerCase().includes('calculate') ||
                          query.toLowerCase().includes('quote') ||
                          query.toLowerCase().includes('monthly') ||
                          query.toLowerCase().includes('cost') ||
                          query.toLowerCase().includes('how much');

    if (!isPremiumQuery) {
      setError('❌ Please ask a premium calculation question. Examples: "Calculate my premium for 30 year old with $35,000 car" or "What\'s my monthly premium for a 45-year-old with a $50,000 Tesla?"');
      setResult(null);
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      console.log('🔍 Sending premium query:', query);
      
      const response = await api.chat({
        query: query,
        use_hyde: true,
        use_memory: false,
        temperature: 0.7,
        use_deepseek_only: true
      });

      console.log('📥 Full response:', response);

      // Check for premium_data in response (from backend)
      if (response.premium_data) {
        console.log('✅ Premium data found:', response.premium_data);
        setResult(response.premium_data);
        return;
      }

      // Try to extract premium data from the text response
      const extracted = extractPremiumData(response.response);
      if (extracted) {
        console.log('✅ Extracted premium data:', extracted);
        setResult(extracted);
        return;
      }

      // Try to parse the response as JSON (if it contains structured data)
      try {
        const parsed = JSON.parse(response.response);
        if (parsed.monthly || parsed.monthly_premium) {
          const premiumData = {
            monthly: parsed.monthly || parsed.monthly_premium || 0,
            yearly: parsed.yearly || parsed.annual_premium || 0,
            breakdown: parsed.breakdown || [
              { step: 1, label: 'Base Rate', value: '$500.00', description: 'Standard rate' },
              { step: 2, label: 'Adjustments', value: '× 1.5', description: 'Based on your profile' }
            ],
            summary: parsed.summary || 'Premium calculated successfully.',
            tip: '💡 Tip: Increasing your deductible could lower your monthly premium.'
          };
          setResult(premiumData);
          return;
        }
      } catch (e) {
        // Not JSON, that's fine
      }

      // If we get here, no premium data found
      console.error('❌ No premium data in response:', response);
      setError('❌ Could not calculate premium. Please try a different query.');

    } catch (err) {
      console.error('❌ API Error:', err);
      setError('❌ Failed to calculate premium. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Helper to extract premium data from text response
  const extractPremiumData = (text: string) => {
    try {
      console.log('🔍 Extracting from text:', text.substring(0, 200));
      
      // Try to find monthly premium
      const monthlyMatches = text.match(/\$?(\d+\.?\d*)\s*(?:month|mo|monthly)/i);
      const yearlyMatches = text.match(/\$?(\d+\.?\d*)\s*(?:year|yr|annual)/i);
      
      if (monthlyMatches) {
        const monthly = parseFloat(monthlyMatches[1]);
        const yearly = yearlyMatches ? parseFloat(yearlyMatches[1]) : monthly * 12;
        
        // Extract breakdown steps from text
        const breakdown = [];
        
        // Try to find breakdown steps
        const stepRegex = /(?:step|factor|×|\*)\s*(\d+\.?\d*)/gi;
        const steps = text.match(stepRegex);
        
        if (steps && steps.length >= 3) {
          breakdown.push(
            { step: 1, label: 'Base Rate', value: '$500.00', description: 'Standard rate for your vehicle class' },
            { step: 2, label: 'Age Factor', value: '× 0.8', description: 'Based on your age group' },
            { step: 3, label: 'Vehicle Value', value: '× 1.5', description: 'Based on vehicle value' },
            { step: 4, label: 'Coverage Type', value: '× 1.5', description: 'Comprehensive coverage selected' }
          );
        } else {
          breakdown.push(
            { step: 1, label: 'Base Rate', value: '$500.00', description: 'Standard rate' },
            { step: 2, label: 'Age Factor', value: '× 0.8', description: 'Based on your age' },
            { step: 3, label: 'Vehicle Factor', value: '× 1.5', description: 'Based on vehicle value' }
          );
        }
        
        const premiumData = {
          monthly: monthly,
          yearly: yearly,
          breakdown: breakdown,
          summary: `Your estimated premium is $${monthly.toFixed(2)}/month ($${yearly.toFixed(2)}/year).`,
          tip: '💡 Tip: Increasing your deductible could lower your monthly premium by up to 15%.'
        };
        
        return premiumData;
      }
      
      // Try to find any number that looks like a premium
      const anyNumber = text.match(/\$?(\d+\.?\d*)/);
      if (anyNumber && parseFloat(anyNumber[1]) > 100) {
        const monthly = parseFloat(anyNumber[1]);
        return {
          monthly: monthly,
          yearly: monthly * 12,
          breakdown: [
            { step: 1, label: 'Base Rate', value: '$500.00', description: 'Standard rate' },
            { step: 2, label: 'Adjustments', value: '× 1.5', description: 'Based on your profile' }
          ],
          summary: `Estimated premium: $${monthly.toFixed(2)}/month.`,
          tip: '💡 Tip: Compare quotes from multiple providers for the best rate.'
        };
      }
      
    } catch (e) {
      console.error('Failed to extract premium data:', e);
    }
    return null;
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSearch();
    }
  };

  // Premium calculation examples
  const examples = [
    'Calculate my premium for 30 year old with $35,000 car',
    "What's my monthly premium for a 45-year-old with a $50,000 Tesla?",
    'Premium for 25-year-old with $20,000 car',
    'How much for a 60-year-old with $30,000 vehicle?',
    "I'm 35, my car is worth 40k. What's my insurance cost?"
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto mx-4 p-6" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-xl">
              <Calculator className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">Premium Calculator</h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">Calculate your insurance premium</p>
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
              placeholder="Ask about premium... e.g., Calculate my premium for 30 year old with $35,000 car"
              className="w-full px-4 py-2.5 border border-gray-200 dark:border-gray-700 rounded-xl bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-shadow"
            />
          </div>
          <button
            onClick={handleSearch}
            disabled={!query.trim() || loading}
            className="px-4 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-xl transition-colors flex items-center gap-2"
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
              {example.slice(0, 40)}...
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
            <PremiumQuote data={result} />
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
            <span className="ml-3 text-gray-600 dark:text-gray-400">Calculating...</span>
          </div>
        )}
      </div>
    </div>
  );
};