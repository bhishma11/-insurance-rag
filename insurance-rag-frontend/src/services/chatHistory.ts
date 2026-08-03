// src/services/chatHistory.ts

const N8N_URL = 'https://n8n-ceaooreqza-uc.a.run.app';

export interface ChatMessage {
  id: number;
  session_id: string;
  user_id: string;
  user_message: string;
  ai_response: string;
  sources: string | null;
  created_at: string;
}

export interface ChatHistoryResponse {
  success: boolean;
  count: number;
  history: ChatMessage[];
}

export interface SaveChatResponse {
  success: boolean;
  message?: string;
}

export const chatHistoryService = {
  /**
   * Save a chat message to Supabase via n8n
   */
  saveChat: async (data: {
    session_id: string;
    user_id?: string;
    user_message: string;
    ai_response: string;
    sources?: any;
  }): Promise<SaveChatResponse> => {
    try {
      const response = await fetch(`${N8N_URL}/webhook/save-chat-history`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      
      const result = await response.json();
      console.log('✅ Chat saved to history:', result);
      return result;
    } catch (error) {
      console.error('❌ Failed to save chat:', error);
      // Non-critical - don't break the user experience
      return { success: false };
    }
  },

  /**
   * Get chat history from Supabase via n8n
   */
  getHistory: async (sessionId: string): Promise<ChatHistoryResponse> => {
    try {
      const response = await fetch(
        `${N8N_URL}/webhook/get-chat-history?session_id=${sessionId}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
      
      const data = await response.json();
      console.log('📚 Chat history loaded:', data);
      return data;
    } catch (error) {
      console.error('❌ Failed to get chat history:', error);
      return { success: false, count: 0, history: [] };
    }
  },

  /**
   * Get all unique session IDs (for sidebar history)
   * Note: This is a simplified version - you may want to implement
   * a proper endpoint in n8n for this
   */
  getSessions: async (): Promise<{ sessions: { session_id: string; title: string; timestamp: string }[] }> => {
    try {
      // For now, we'll return an empty array since we don't have a dedicated endpoint
      // You can add a new n8n workflow to get all sessions
      console.warn('⚠️ getSessions not implemented in n8n yet - using fallback');
      return { sessions: [] };
    } catch (error) {
      console.error('❌ Failed to get sessions:', error);
      return { sessions: [] };
    }
  },

  /**
   * Delete a session (optional - if you implement in n8n)
   */
  deleteSession: async (sessionId: string): Promise<{ success: boolean }> => {
    try {
      // Not implemented yet - you can add a DELETE workflow in n8n
      console.warn('⚠️ deleteSession not implemented in n8n yet');
      return { success: false };
    } catch (error) {
      console.error('❌ Failed to delete session:', error);
      return { success: false };
    }
  }
};