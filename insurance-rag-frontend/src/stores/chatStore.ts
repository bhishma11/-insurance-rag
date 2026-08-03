import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Message } from '../types';
import { api } from '../services/api';
import { chatHistoryService } from '../services/chatHistory';

interface ChatState {
  messages: Message[];
  sessionId: string;
  isProcessing: boolean;
  chatHistory: any[];
  isLoadingHistory: boolean;
  addMessage: (message: Message) => void;
  updateLastMessage: (updates: Partial<Message>) => void;
  setProcessing: (isProcessing: boolean) => void;
  clearMessages: () => void;
  setChatHistory: (history: any[]) => void;
  loadSession: (sessionId: string) => Promise<void>;
  loadHistory: () => Promise<void>;
  newChat: () => void;
  // ✅ New n8n methods
  saveChatToN8n: (userMessage: string, aiResponse: string) => Promise<void>;
  loadChatFromN8n: (sessionId: string) => Promise<void>;
}

export const useChatStore = create<ChatState>()(
  persist(
    (set, get) => ({
      messages: [],
      sessionId: crypto.randomUUID(),
      isProcessing: false,
      chatHistory: [],
      isLoadingHistory: false,
      
      addMessage: (message) => set((state) => ({
        messages: [...state.messages, message]
      })),
      
      updateLastMessage: (updates) => set((state) => {
        const messages = [...state.messages];
        const lastIndex = messages.length - 1;
        if (lastIndex < 0) return state;
        messages[lastIndex] = { ...messages[lastIndex], ...updates };
        return { messages };
      }),
      
      setProcessing: (isProcessing) => set({ isProcessing }),
      
      clearMessages: () => set({ messages: [] }),
      
      setChatHistory: (chatHistory) => set({ chatHistory }),
      
      loadHistory: async () => {
        set({ isLoadingHistory: true });
        try {
          const response = await api.getSessions();
          set({ chatHistory: response.sessions || [] });
        } catch (error) {
          console.error('Failed to load history:', error);
        } finally {
          set({ isLoadingHistory: false });
        }
      },
      
      loadSession: async (sessionId: string) => {
        set({ sessionId, isLoadingHistory: true });
        try {
          const response = await api.getHistory(sessionId);
          const allMessages: Message[] = [];
          response.history.forEach((h: any, idx: number) => {
            allMessages.push({
              id: `u-${idx}`,
              type: 'user',
              content: h.user_query,
              timestamp: new Date(h.timestamp)
            });
            allMessages.push({
              id: `a-${idx}`,
              type: 'assistant',
              content: h.ai_response,
              timestamp: new Date(h.timestamp)
            });
          });
          set({ messages: allMessages });
        } catch (error) {
          console.error('Failed to load session:', error);
        } finally {
          set({ isLoadingHistory: false });
        }
      },
      
      newChat: () => {
        const newSessionId = crypto.randomUUID();
        set({ 
          sessionId: newSessionId,
          messages: []
        });
        get().loadHistory();
      },

      // ✅ NEW: Save chat to n8n
      saveChatToN8n: async (userMessage: string, aiResponse: string) => {
        const state = get();
        const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
        
        try {
          await chatHistoryService.saveChat({
            session_id: state.sessionId,
            user_id: currentUser?.user_id || 'anonymous',
            user_message: userMessage,
            ai_response: aiResponse,
            sources: null
          });
          console.log('✅ Chat saved to n8n');
        } catch (error) {
          console.error('❌ Failed to save chat to n8n:', error);
        }
      },

      // ✅ NEW: Load chat from n8n
      loadChatFromN8n: async (sessionId: string) => {
        set({ isLoadingHistory: true });
        try {
          const response = await chatHistoryService.getHistory(sessionId);
          
          if (response.success && response.history.length > 0) {
            const messages: Message[] = [];
            response.history.forEach((item) => {
              messages.push({
                id: `u-${item.id}`,
                type: 'user',
                content: item.user_message,
                timestamp: new Date(item.created_at)
              });
              messages.push({
                id: `a-${item.id}`,
                type: 'assistant',
                content: item.ai_response,
                timestamp: new Date(item.created_at)
              });
            });
            set({ messages, sessionId });
          } else {
            // No history, clear messages
            set({ messages: [], sessionId });
          }
        } catch (error) {
          console.error('Failed to load chat from n8n:', error);
        } finally {
          set({ isLoadingHistory: false });
        }
      },
    }),
    {
      name: 'chat-storage',
      partialize: (state) => ({ sessionId: state.sessionId })
    }
  )
);