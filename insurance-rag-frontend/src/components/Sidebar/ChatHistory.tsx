import { useEffect, useState } from 'react';
import { History, Clock, Trash2, MessageSquare, RefreshCw } from 'lucide-react';
import { api } from '../../services/api';
import { useChatStore } from '../../stores/chatStore';

interface Session {
  session_id: string;
  title: string;
  timestamp: string;
  first_query: string;
}

export const ChatHistory = () => {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { loadSession, sessionId: currentSessionId, loadHistory } = useChatStore();

  useEffect(() => {
    fetchSessions();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchSessions, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchSessions = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.getSessions();
      setSessions(response.sessions || []);
    } catch (error) {
      console.error('Failed to load sessions:', error);
      setError('Failed to load chat history');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    fetchSessions();
  };

  const handleLoadSession = async (sessionId: string) => {
    try {
      await loadSession(sessionId);
    } catch (error) {
      console.error('Failed to load session:', error);
    }
  };

  const handleDeleteSession = async (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await api.deleteSession(sessionId);
      setSessions(sessions.filter(s => s.session_id !== sessionId));
    } catch (error) {
      console.error('Failed to delete session:', error);
    }
  };

  const formatDate = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      const now = new Date();
      const diff = now.getTime() - date.getTime();
      
      // Invalid date check
      if (isNaN(date.getTime())) {
        return 'Invalid date';
      }
      
      // Same day - show relative time
      if (diff < 60000) return 'Just now';
      if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
      if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
      if (diff < 604800000) return `${Math.floor(diff / 86400000)}d ago`;
      
      // Older - show formatted date in Hong Kong timezone
      return date.toLocaleString('en-HK', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        timeZone: 'Asia/Hong_Kong'
      });
    } catch (e) {
      return 'Invalid date';
    }
  };

  const getTimeAgo = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      const now = new Date();
      const diff = now.getTime() - date.getTime();
      
      if (diff < 60000) return 'Just now';
      if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
      if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
      if (diff < 604800000) return `${Math.floor(diff / 86400000)}d ago`;
      return formatDate(timestamp);
    } catch (e) {
      return 'Invalid date';
    }
  };

  return (
    <div className="space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <History className="w-4 h-4 text-gray-500 dark:text-gray-400" />
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Chat History
            {sessions.length > 0 && (
              <span className="ml-1 text-xs text-gray-400">({sessions.length})</span>
            )}
          </span>
        </div>
        <button 
          onClick={handleRefresh}
          className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          title="Refresh history"
          disabled={loading}
        >
          <RefreshCw className={`w-3.5 h-3.5 text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Error State */}
      {error && (
        <div className="text-sm text-red-500 dark:text-red-400 text-center py-2 px-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
          {error}
          <button 
            onClick={handleRefresh}
            className="ml-2 text-blue-500 hover:text-blue-600 underline"
          >
            Retry
          </button>
        </div>
      )}

      {/* Loading State */}
      {loading ? (
        <div className="flex items-center justify-center py-6">
          <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
          <span className="ml-2 text-sm text-gray-500 dark:text-gray-400">Loading...</span>
        </div>
      ) : sessions.length === 0 ? (
        // Empty State
        <div className="text-sm text-gray-400 dark:text-gray-500 text-center py-6">
          <MessageSquare className="w-8 h-8 mx-auto mb-2 text-gray-300 dark:text-gray-600" />
          <p>No chat history yet</p>
          <p className="text-xs mt-1">Start a conversation to see it here</p>
        </div>
      ) : (
        // Sessions List
        <div className="space-y-1.5 max-h-64 overflow-y-auto pr-1">
          {sessions.map((session) => (
            <div
              key={session.session_id}
              onClick={() => handleLoadSession(session.session_id)}
              className={`group flex items-center justify-between p-2.5 rounded-lg cursor-pointer transition-all duration-200 ${
                session.session_id === currentSessionId
                  ? 'bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800'
                  : 'hover:bg-gray-50 dark:hover:bg-gray-800 border border-transparent'
              }`}
            >
              <div className="flex-1 min-w-0">
                {/* Title */}
                <p className={`text-sm truncate ${
                  session.session_id === currentSessionId 
                    ? 'text-blue-700 dark:text-blue-400 font-medium' 
                    : 'text-gray-700 dark:text-gray-300'
                }`}>
                  {session.title || session.first_query || 'New Chat'}
                </p>
                {/* Timestamp */}
                <div className="flex items-center gap-2 mt-0.5">
                  <Clock className="w-3 h-3 text-gray-400 dark:text-gray-500 flex-shrink-0" />
                  <span className="text-xs text-gray-400 dark:text-gray-500">
                    {getTimeAgo(session.timestamp)}
                  </span>
                  {/* Session ID indicator (tooltip) */}
                  {session.session_id === currentSessionId && (
                    <span className="text-[10px] px-1.5 py-0.5 bg-blue-100 dark:bg-blue-900/50 text-blue-600 dark:text-blue-400 rounded-full">
                      Active
                    </span>
                  )}
                </div>
              </div>
              
              {/* Delete Button */}
              <button
                onClick={(e) => handleDeleteSession(session.session_id, e)}
                className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-100 dark:hover:bg-red-900/30 rounded-lg transition-all duration-200"
                title="Delete session"
              >
                <Trash2 className="w-3.5 h-3.5 text-gray-400 hover:text-red-500 dark:hover:text-red-400" />
              </button>
            </div>
          ))}
        </div>
      )}
      
      {/* Footer with total count */}
      {sessions.length > 0 && !loading && (
        <div className="text-[10px] text-gray-400 dark:text-gray-500 text-center pt-1 border-t border-gray-100 dark:border-gray-700">
          {sessions.length} session{sessions.length > 1 ? 's' : ''} • Click to load
        </div>
      )}
    </div>
  );
};