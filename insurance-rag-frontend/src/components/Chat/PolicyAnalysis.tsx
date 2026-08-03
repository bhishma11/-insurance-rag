import { FileText, ExternalLink, Shield, Copy, Check } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useState } from 'react';

interface PolicyAnalysisProps {
  response: string;
  sources: any[];
}

export const PolicyAnalysis = ({ response, sources }: PolicyAnalysisProps) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(response);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const extractPolicyStatus = (text: string) => {
    const policies = [
      { name: 'Auto Policy', keyword: 'Auto', icon: '🚗' },
      { name: 'Renters Policy', keyword: 'Renters', icon: '🏠' },
      { name: 'Health Policy', keyword: 'Health', icon: '🏥' },
    ];
    
    return policies.map(policy => {
      const isCovered = text.includes(policy.keyword) && 
        (text.includes('covers') || text.includes('covered') || text.includes('Yes'));
      const isExcluded = text.includes(policy.keyword) && 
        (text.includes('excluded') || text.includes('does not cover') || text.includes('No'));
      
      return {
        ...policy,
        status: isCovered ? 'covered' : isExcluded ? 'excluded' : 'unknown'
      };
    });
  };

  const policyStatuses = extractPolicyStatus(response);
  const hasCoverage = policyStatuses.some(p => p.status === 'covered');

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 overflow-hidden w-full">
      {/* Header */}
      <div className={`px-6 py-5 ${hasCoverage ? 'bg-gradient-to-br from-blue-600 to-blue-700' : 'bg-gradient-to-br from-amber-600 to-amber-700'}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-white/20 p-2 rounded-xl backdrop-blur-sm">
              <Shield className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-white font-semibold text-2xl">Policy Coverage Analysis</h3>
              <p className="text-white/70 text-base">Based on your uploaded policy documents</p>
            </div>
          </div>
          
          <button
            onClick={handleCopy}
            className="flex items-center gap-2 px-4 py-2 bg-white/20 hover:bg-white/30 text-white text-base font-medium rounded-lg transition-all backdrop-blur-sm"
          >
            {copied ? (
              <>
                <Check className="w-5 h-5" />
                <span>Copied!</span>
              </>
            ) : (
              <>
                <Copy className="w-5 h-5" />
                <span>Copy</span>
              </>
            )}
          </button>
        </div>
      </div>

      <div className="p-8 md:p-10 lg:p-12">
        {/* Policy Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          {policyStatuses.map((policy) => (
            <div 
              key={policy.name}
              className={`p-5 rounded-xl border ${
                policy.status === 'covered' 
                  ? 'bg-green-50 dark:bg-green-900/30 border-green-200 dark:border-green-800'
                  : policy.status === 'excluded'
                  ? 'bg-red-50 dark:bg-red-900/30 border-red-200 dark:border-red-800'
                  : 'bg-gray-50 dark:bg-gray-800/50 border-gray-200 dark:border-gray-700'
              }`}
            >
              <div className="flex items-center gap-3">
                <span className="text-3xl">{policy.icon}</span>
                <h4 className="font-semibold text-lg text-gray-800 dark:text-gray-200">{policy.name}</h4>
              </div>
              <div className="mt-2 text-lg font-medium">
                {policy.status === 'covered' && (
                  <span className="text-green-600 dark:text-green-400">✅ Covered</span>
                )}
                {policy.status === 'excluded' && (
                  <span className="text-red-600 dark:text-red-400">❌ Not Covered</span>
                )}
                {policy.status === 'unknown' && (
                  <span className="text-gray-500 dark:text-gray-400">📋 Review details</span>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Content - Force large text with direct styling */}
        <div className="max-w-none w-full text-gray-700 dark:text-gray-300 [&_h1]:text-4xl [&_h1]:font-bold [&_h1]:mt-8 [&_h1]:mb-6 [&_h1]:text-blue-700 dark:[&_h1]:text-blue-300 [&_h1]:border-b-2 [&_h1]:border-blue-200 dark:[&_h1]:border-blue-800 [&_h1]:pb-4
          [&_h2]:text-3xl [&_h2]:font-bold [&_h2]:mt-8 [&_h2]:mb-5 [&_h2]:text-blue-600 dark:[&_h2]:text-blue-400 [&_h2]:border-b-2 [&_h2]:border-blue-200 dark:[&_h2]:border-blue-800 [&_h2]:pb-3
          [&_h3]:text-2xl [&_h3]:font-semibold [&_h3]:mt-6 [&_h3]:mb-4 [&_h3]:text-blue-600 dark:[&_h3]:text-blue-400
          [&_h4]:text-xl [&_h4]:font-semibold [&_h4]:mt-5 [&_h4]:mb-3
          [&_p]:text-xl [&_p]:leading-relaxed [&_p]:mt-0 [&_p]:mb-5
          [&_strong]:text-gray-900 dark:[&_strong]:text-white [&_strong]:font-bold
          [&_ul]:mt-4 [&_ul]:mb-6 [&_ul]:space-y-2 [&_ul]:list-disc [&_ul]:pl-6
          [&_ol]:mt-4 [&_ol]:mb-6 [&_ol]:space-y-2 [&_ol]:list-decimal [&_ol]:pl-6
          [&_li]:text-xl [&_li]:my-1.5 [&_li]:leading-relaxed
          [&_table]:w-full [&_table]:border-collapse [&_table]:my-6 [&_table]:shadow-lg [&_table]:rounded-lg [&_table]:overflow-hidden
          [&_th]:text-left [&_th]:font-bold [&_th]:p-4 [&_th]:text-xl [&_th]:bg-gradient-to-r [&_th]:from-blue-50 [&_th]:to-cyan-50 dark:[&_th]:from-blue-900/30 dark:[&_th]:to-cyan-900/30 [&_th]:border-b-2 [&_th]:border-blue-200 dark:[&_th]:border-blue-700 [&_th]:text-gray-900 dark:[&_th]:text-white
          [&_td]:p-4 [&_td]:border-b [&_td]:border-gray-200 dark:[&_td]:border-gray-700 [&_td]:text-xl [&_td]:align-top [&_td]:bg-white dark:[&_td]:bg-gray-800 [&_td]:even:bg-gray-50 dark:[&_td]:even:bg-gray-800/50
          [&_blockquote]:border-l-4 [&_blockquote]:border-blue-500 [&_blockquote]:pl-6 [&_blockquote]:my-6 [&_blockquote]:bg-blue-50 dark:[&_blockquote]:bg-blue-950/30 [&_blockquote]:py-4 [&_blockquote]:pr-5 [&_blockquote]:rounded-r-lg [&_blockquote]:text-xl [&_blockquote]:not-italic
          [&_hr]:my-10 [&_hr]:border-gray-200 dark:[&_hr]:border-gray-700
        ">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {response}
          </ReactMarkdown>
        </div>

        {/* Sources */}
        {sources && sources.length > 0 && (
          <div className="mt-8 pt-5 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-2 text-base text-gray-500 dark:text-gray-400">
              <FileText className="w-5 h-5" />
              <span className="font-medium">Sources:</span>
              <span>
                {sources.map((s: any, i: number) => (
                  <span key={i}>
                    {s.filename}
                    {i < sources.length - 1 && ', '}
                  </span>
                ))}
              </span>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="mt-8 flex flex-wrap gap-4 pt-5 border-t border-gray-200 dark:border-gray-700">
          <button className="px-6 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white text-base font-medium rounded-xl transition-all shadow-lg hover:shadow-xl flex items-center gap-2">
            <Shield className="w-5 h-5" />
            Get New Quote
          </button>
          <button className="px-6 py-3 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200 text-base font-medium rounded-xl transition-all flex items-center gap-2">
            <ExternalLink className="w-5 h-5" />
            Contact Agent
          </button>
          <button className="px-6 py-3 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200 text-base font-medium rounded-xl transition-all flex items-center gap-2">
            <FileText className="w-5 h-5" />
            View Policies
          </button>
        </div>
      </div>
    </div>
  );
};