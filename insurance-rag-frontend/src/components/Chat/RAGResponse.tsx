import { FileText, ExternalLink, Sparkles, Copy, Check } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useState } from 'react';

interface RAGResponseProps {
  response: string;
  sources?: any[];
}

export const RAGResponse = ({ response, sources = [] }: RAGResponseProps) => {
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

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-br from-indigo-600 to-purple-600 px-5 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-white/20 p-2 rounded-xl backdrop-blur-sm">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-white font-semibold text-lg">Insurance Assistant</h3>
              <p className="text-indigo-200 text-sm">AI-powered policy analysis</p>
            </div>
          </div>
          
          <button
            onClick={handleCopy}
            className="flex items-center gap-2 px-3 py-1.5 bg-white/20 hover:bg-white/30 text-white text-sm font-medium rounded-lg transition-all backdrop-blur-sm"
          >
            {copied ? (
              <>
                <Check className="w-4 h-4" />
                <span>Copied!</span>
              </>
            ) : (
              <>
                <Copy className="w-4 h-4" />
                <span>Copy</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Content - Tighter padding */}
      <div className="p-6 md:p-8">
        <div className="max-w-none w-full text-gray-700 dark:text-gray-300 
          [&_h1]:text-3xl [&_h1]:font-bold [&_h1]:mt-6 [&_h1]:mb-4 [&_h1]:text-indigo-700 dark:[&_h1]:text-indigo-300 [&_h1]:border-b-2 [&_h1]:border-indigo-200 dark:[&_h1]:border-indigo-800 [&_h1]:pb-3
          [&_h2]:text-2xl [&_h2]:font-bold [&_h2]:mt-6 [&_h2]:mb-4 [&_h2]:text-indigo-600 dark:[&_h2]:text-indigo-400 [&_h2]:border-b-2 [&_h2]:border-indigo-200 dark:[&_h2]:border-indigo-800 [&_h2]:pb-2
          [&_h3]:text-xl [&_h3]:font-semibold [&_h3]:mt-5 [&_h3]:mb-3 [&_h3]:text-indigo-600 dark:[&_h3]:text-indigo-400
          [&_h4]:text-lg [&_h4]:font-semibold [&_h4]:mt-4 [&_h4]:mb-2
          [&_p]:text-base [&_p]:leading-relaxed [&_p]:mt-0 [&_p]:mb-4
          [&_strong]:text-gray-900 dark:[&_strong]:text-white [&_strong]:font-bold
          [&_ul]:mt-3 [&_ul]:mb-4 [&_ul]:space-y-1.5 [&_ul]:list-disc [&_ul]:pl-5
          [&_ol]:mt-3 [&_ol]:mb-4 [&_ol]:space-y-1.5 [&_ol]:list-decimal [&_ol]:pl-5
          [&_li]:text-base [&_li]:my-1 [&_li]:leading-relaxed
          [&_table]:w-full [&_table]:border-collapse [&_table]:my-4 [&_table]:shadow-md [&_table]:rounded-lg [&_table]:overflow-hidden
          [&_th]:text-left [&_th]:font-bold [&_th]:p-3 [&_th]:text-base [&_th]:bg-gradient-to-r [&_th]:from-indigo-50 [&_th]:to-purple-50 dark:[&_th]:from-indigo-900/30 dark:[&_th]:to-purple-900/30 [&_th]:border-b-2 [&_th]:border-indigo-200 dark:[&_th]:border-indigo-700 [&_th]:text-gray-900 dark:[&_th]:text-white
          [&_td]:p-3 [&_td]:border-b [&_td]:border-gray-200 dark:[&_td]:border-gray-700 [&_td]:text-base [&_td]:align-top [&_td]:bg-white dark:[&_td]:bg-gray-800 [&_td]:even:bg-gray-50 dark:[&_td]:even:bg-gray-800/50
          [&_blockquote]:border-l-4 [&_blockquote]:border-indigo-500 [&_blockquote]:pl-4 [&_blockquote]:my-4 [&_blockquote]:bg-indigo-50 dark:[&_blockquote]:bg-indigo-950/30 [&_blockquote]:py-3 [&_blockquote]:pr-4 [&_blockquote]:rounded-r-lg [&_blockquote]:text-base [&_blockquote]:not-italic
          [&_hr]:my-6 [&_hr]:border-gray-200 dark:[&_hr]:border-gray-700
          [&_a]:text-indigo-600 dark:[&_a]:text-indigo-400 [&_a]:underline [&_a]:font-medium
          [&_code]:text-indigo-600 dark:[&_code]:text-indigo-400 [&_code]:bg-indigo-50 dark:[&_code]:bg-indigo-900/30 [&_code]:px-1.5 [&_code]:py-0.5 [&_code]:rounded [&_code]:text-sm
          [&_pre]:bg-gray-100 dark:[&_pre]:bg-gray-900 [&_pre]:p-4 [&_pre]:rounded-xl [&_pre]:my-4 [&_pre]:overflow-x-auto
        ">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {response}
          </ReactMarkdown>
        </div>

        {/* Sources */}
        {sources && sources.length > 0 && (
          <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
              <FileText className="w-4 h-4" />
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

        {/* Action Buttons */}
        <div className="mt-6 flex flex-wrap gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
          <button className="px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white text-sm font-medium rounded-lg transition-all shadow-md hover:shadow-lg flex items-center gap-2">
            <Sparkles className="w-4 h-4" />
            Get New Quote
          </button>
          <button className="px-5 py-2.5 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200 text-sm font-medium rounded-lg transition-all flex items-center gap-2">
            <ExternalLink className="w-4 h-4" />
            Contact Agent
          </button>
          <button className="px-5 py-2.5 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200 text-sm font-medium rounded-lg transition-all flex items-center gap-2">
            <FileText className="w-4 h-4" />
            View Policies
          </button>
        </div>
      </div>
    </div>
  );
};