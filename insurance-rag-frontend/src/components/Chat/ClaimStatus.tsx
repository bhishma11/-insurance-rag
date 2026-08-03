import { FileCheck, Clock, DollarSign } from 'lucide-react';

interface ClaimData {
  claim_id: string;
  status: string;
  estimated_payment_date?: string;
  next_steps: string;
}

export const ClaimStatus = ({ data }: { data: ClaimData }) => {
  const statusColors: Record<string, string> = {
    'Approved': 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400',
    'Pending Review': 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400',
    'Processing': 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400',
    'Paid': 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400',
    'Denied': 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400',
  };

  const statusColor = statusColors[data.status] || 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-400';

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 overflow-hidden max-w-2xl">
      <div className="bg-gradient-to-br from-purple-600 to-purple-700 px-6 py-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-white/20 p-2 rounded-xl backdrop-blur-sm">
              <FileCheck className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-white font-semibold text-lg">Claim Status</h3>
              <p className="text-purple-100 text-sm">Claim #{data.claim_id}</p>
            </div>
          </div>
          <div className={`px-3 py-1.5 rounded-full ${statusColor}`}>
            <span className="text-xs font-medium">{data.status}</span>
          </div>
        </div>
      </div>

      <div className="p-6 space-y-4">
        <div className="flex items-center gap-4 p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-700">
          <Clock className="w-5 h-5 text-gray-400 dark:text-gray-500" />
          <div>
            <p className="text-sm text-gray-500 dark:text-gray-400">Next Steps</p>
            <p className="text-sm font-medium text-gray-800 dark:text-gray-200">{data.next_steps}</p>
          </div>
        </div>

        {data.estimated_payment_date && (
          <div className="flex items-center gap-4 p-4 bg-green-50 dark:bg-green-900/20 rounded-xl border border-green-200 dark:border-green-800">
            <DollarSign className="w-5 h-5 text-green-500 dark:text-green-400" />
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Estimated Payment Date</p>
              <p className="text-sm font-medium text-green-700 dark:text-green-400">{data.estimated_payment_date}</p>
            </div>
          </div>
        )}

        <button className="w-full px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors shadow-sm hover:shadow-md">
          Track Claim Progress
        </button>
      </div>
    </div>
  );
};