import { useState } from 'react';
import { Calculator, Send, DollarSign, Users, Car, TrendingUp } from 'lucide-react';
import { api } from '../../services/api';
import { useChatStore } from '../../stores/chatStore';

export const PremiumCalculator = () => {
  const [age, setAge] = useState(30);
  const [carValue, setCarValue] = useState(35000);
  const [deductible, setDeductible] = useState(500);
  const [coverageType, setCoverageType] = useState('comprehensive');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const { sendMessage } = useChatStore();

  const handleCalculate = async () => {
    setLoading(true);
    try {
      const response = await api.calculatePremium(age, carValue, deductible);
      setResult(response);
    } catch (error) {
      console.error('Failed to calculate premium:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSendToChat = () => {
    const query = `Calculate my premium for ${age} year old with $${carValue.toLocaleString()} car`;
    sendMessage(query);
  };

  return (
    <div className="space-y-3">
      {/* Age Input */}
      <div>
        <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
          Age
        </label>
        <input
          type="number"
          value={age}
          onChange={(e) => setAge(Number(e.target.value))}
          min={18}
          max={80}
          className="w-full px-3 py-1.5 text-sm border border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Car Value Input */}
      <div>
        <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
          Car Value ($)
        </label>
        <input
          type="number"
          value={carValue}
          onChange={(e) => setCarValue(Number(e.target.value))}
          min={5000}
          max={200000}
          className="w-full px-3 py-1.5 text-sm border border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Deductible Input */}
      <div>
        <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
          Deductible ($)
        </label>
        <input
          type="number"
          value={deductible}
          onChange={(e) => setDeductible(Number(e.target.value))}
          min={100}
          max={2000}
          step={100}
          className="w-full px-3 py-1.5 text-sm border border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Coverage Type */}
      <div>
        <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
          Coverage Type
        </label>
        <select
          value={coverageType}
          onChange={(e) => setCoverageType(e.target.value)}
          className="w-full px-3 py-1.5 text-sm border border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="basic">Basic</option>
          <option value="comprehensive">Comprehensive</option>
        </select>
      </div>

      {/* Calculate Button */}
      <button
        onClick={handleCalculate}
        disabled={loading}
        className="w-full px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white text-sm font-medium rounded-lg transition-all disabled:opacity-50 flex items-center justify-center gap-2"
      >
        <Calculator className="w-4 h-4" />
        {loading ? 'Calculating...' : 'Calculate Premium'}
      </button>

      {/* Result */}
      {result && (
        <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 border border-green-200 dark:border-green-800 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-600 dark:text-gray-400">Monthly Premium</span>
            <span className="text-lg font-bold text-green-700 dark:text-green-400">
              ${result.monthly_premium.toFixed(2)}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-600 dark:text-gray-400">Yearly Premium</span>
            <span className="text-lg font-bold text-green-700 dark:text-green-400">
              ${result.yearly_premium.toFixed(2)}
            </span>
          </div>
          <button
            onClick={handleSendToChat}
            className="w-full px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium rounded-lg transition-colors flex items-center justify-center gap-1"
          >
            <Send className="w-3 h-3" />
            Send to Chat
          </button>
        </div>
      )}
    </div>
  );
};