import { Message } from '../../types';
import { PremiumQuote } from './PremiumQuote';
import { ClaimStatus } from './ClaimStatus';
import { PolicyComparison } from './PolicyComparison';
import { TypingIndicator } from './TypingIndicator';
import { PolicyAnalysis } from './PolicyAnalysis';
import { RAGResponse } from './RAGResponse';
import { CheckCircle } from 'lucide-react';

interface Props {
  message: Message;
}

export const MessageBubble = ({ message }: Props) => {
  const isUser = message.type === 'user';

  const renderContent = () => {
    if (isUser) {
      return (
        <div className="text-base leading-relaxed text-white py-2 px-1">
          {message.content}
        </div>
      );
    }

    if (message.isStreaming) {
      return <TypingIndicator />;
    }

    try {
      const parsed = JSON.parse(message.content);
      
      if (parsed.type === 'premium_calculation') {
        return <PremiumQuote data={parsed.data} />;
      }
      
      if (parsed.type === 'claim_status') {
        return <ClaimStatus data={parsed.data} />;
      }
      
      if (parsed.type === 'policy_comparison') {
        return <PolicyComparison data={parsed.data} />;
      }
      
      if (parsed.type === 'callback_scheduled') {
        return (
          <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 p-6 max-w-2xl">
            <div className="flex items-center gap-3 mb-4">
              <div className="bg-green-100 dark:bg-green-900/30 p-2 rounded-xl">
                <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Callback Scheduled</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">ID: {parsed.data.callback_id}</p>
              </div>
            </div>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">{parsed.data.message}</p>
          </div>
        );
      }
      
      if (parsed.type === 'rag_response') {
        const response = parsed.data.response;
        const isPolicyAnalysis = response.includes('Policy') && 
          (response.includes('Coverage') || response.includes('covered') || response.includes('policy'));
        
        // Add model badge
        const modelBadge = parsed.model_used ? (
          <div className="mb-3 flex items-center gap-2">
            <span className={`text-xs px-2 py-0.5 rounded-full ${
              parsed.model_used === 'qlora' 
                ? 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400' 
                : 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400'
            }`}>
              {parsed.model_used === 'qlora' ? '🚀 Local (QLoRA)' : '☁️ DeepSeek'}
            </span>
          </div>
        ) : null;
        
        if (isPolicyAnalysis) {
          return (
            <>
              {modelBadge}
              <PolicyAnalysis response={response} sources={parsed.data.sources || []} />
            </>
          );
        }
        
        return (
          <>
            {modelBadge}
            <RAGResponse response={response} sources={parsed.data.sources || []} />
          </>
        );
      }
      
      return <RAGResponse response={message.content} sources={[]} />;
      
    } catch (e) {
      return <RAGResponse response={message.content} sources={[]} />;
    }
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} w-full`}>
      <div className={`rounded-2xl px-4 py-3 ${
        isUser 
          ? 'bg-blue-600 text-white max-w-md' 
          : 'bg-transparent max-w-4xl'
      }`}>
        {renderContent()}
      </div>
    </div>
  );
};