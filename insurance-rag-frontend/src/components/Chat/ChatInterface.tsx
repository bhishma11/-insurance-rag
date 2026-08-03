// src/components/Chat/ChatInterface.tsx
import { useState, useRef, useEffect } from 'react';
import { Send, Mic, Plus, Sparkles, MicOff, FileText, X, Image, Loader2 } from 'lucide-react';
import { useChatStore } from '../../stores/chatStore';
import { useWebSocket } from '../../hooks/useWebSocket';
import { MessageBubble } from './MessageBubble';
import { DocumentUpload } from '../DocumentUpload';
import { ImagePreview } from './ImagePreview';
import { api } from '../../services/api';
import { LemonMascotLogo } from '../Common/LemonMascotLogo';
import { useSessionTimeout } from '../../hooks/useSessionTimeout';

export const ChatInterface = () => {
  const [input, setInput] = useState('');
  const [showDocumentUpload, setShowDocumentUpload] = useState(false);
  
  // ============ Session Timeout (5 minutes) ============
  useSessionTimeout(5); // Auto-logout after 5 minutes of inactivity
  
  // ============ Image Upload State ============
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [imageError, setImageError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const { 
    messages, 
    sessionId, 
    addMessage, 
    newChat, 
    loadHistory,
    saveChatToN8n,      // ✅ New
    loadChatFromN8n      // ✅ New
  } = useChatStore();
  
  const { sendMessage, isConnected, startListening, stopListening, isListening, transcript } = useWebSocket(sessionId);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // ============ Load chat history from n8n on mount ============
  useEffect(() => {
    const loadInitialHistory = async () => {
      // Check if we have a session ID from localStorage
      const storedSessionId = localStorage.getItem('chat-storage');
      if (storedSessionId) {
        try {
          const parsed = JSON.parse(storedSessionId);
          if (parsed?.state?.sessionId) {
            await loadChatFromN8n(parsed.state.sessionId);
            return;
          }
        } catch (e) {
          console.log('No stored session, loading default');
        }
      }
      // Fallback to regular history
      loadHistory();
    };
    
    loadInitialHistory();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (transcript) {
      setInput(transcript);
    }
  }, [transcript]);

  // ============ Handle Send Message ============
  const handleSend = () => {
    if (!input.trim()) return;
    
    // Save user message to store
    const userMessage = input.trim();
    
    // Send via WebSocket
    sendMessage(userMessage);
    
    // Clear input
    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  // ============ Handle AI Response (called from WebSocket) ============
  const handleAIResponse = (aiResponse: string, userMessage: string) => {
    // Save both messages to n8n
    if (userMessage && aiResponse) {
      saveChatToN8n(userMessage, aiResponse);
    }
  };

  // ============ Expose save function to WebSocket handler ============
  // This is used in the WebSocket onmessage handler
  useEffect(() => {
    // Store the save function globally for WebSocket to use
    (window as any).__saveChatToN8n = saveChatToN8n;
  }, [saveChatToN8n]);

  const handleNewChat = () => {
    newChat();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    const textarea = e.target;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
  };

  const toggleListening = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  // ============ Image Upload Handlers ============
  
  const handleImageSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      setImageError('Please upload an image file');
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setImageError('Image size should be less than 10MB');
      return;
    }

    setSelectedImage(file);
    setImagePreview(URL.createObjectURL(file));
    setImageError(null);
    setAnalysisResult(null);
    setIsAnalyzing(true);

    try {
      // Call the vision API directly (NOT the chat API)
      const result = await api.analyzeImage(file);
      setAnalysisResult(result);
      
      // Display the analysis as a message WITHOUT going through RAG
      if (result.analysis && result.classification !== 'other') {
        // Format the response message
        let message = '';
        let title = '';
        
        if (result.classification === 'car_damage') {
          title = '🚗 Car Damage Analysis';
          message = `**Classification:** Car Damage\n**Recommendation:** ${result.recommendation || 'Auto insurance claim recommended'}\n\n${result.analysis}`;
        } else if (result.classification === 'injury') {
          title = '🏥 Injury Analysis';
          message = `**Classification:** Injury\n**Recommendation:** ${result.recommendation || 'Health insurance claim recommended'}\n\n${result.analysis}`;
        } else {
          title = '📷 Image Analysis';
          message = `**Classification:** Other\n\n${result.analysis}`;
        }
        
        // Add the message directly to the chat WITHOUT calling sendMessage
        // This bypasses the RAG pipeline entirely
        addMessage({
          id: `vision-${Date.now()}`,
          type: 'assistant',
          content: `## ${title}\n\n${message}`,
          timestamp: new Date(),
          isStreaming: false
        });
        
        // Auto-remove the image preview after 3 seconds
        setTimeout(() => {
          removeImage();
        }, 3000);
        
      } else if (result.classification === 'other') {
        setImageError('This image does not appear to show car damage or injury.');
        // Add a friendly message about the image
        addMessage({
          id: `vision-${Date.now()}`,
          type: 'assistant',
          content: `## 📷 Image Analysis\n\n**Classification:** Other\n\nThis image does not appear to show car damage or a personal injury. Please upload a relevant photo for insurance analysis.`,
          timestamp: new Date(),
          isStreaming: false
        });
        setTimeout(() => {
          removeImage();
        }, 3000);
      }
      
    } catch (error) {
      console.error('Image analysis failed:', error);
      setImageError('Failed to analyze image. Please try again.');
      
      // Add error message to chat
      addMessage({
        id: `vision-error-${Date.now()}`,
        type: 'assistant',
        content: `## ❌ Image Analysis Failed\n\nFailed to analyze the image. Please try again or check if Ollama is running.\n\n**Error:** ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date(),
        isStreaming: false
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const removeImage = () => {
    setSelectedImage(null);
    setImagePreview(null);
    setAnalysisResult(null);
    setImageError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Welcome screen suggestions
  const suggestions = [
    { label: 'Get a quote', prompt: 'Calculate my premium for 30 year old with $35,000 car' },
    { label: 'Check claim status', prompt: 'Check claim status for CL-12345' },
    { label: 'Compare policies', prompt: 'Compare auto and renters insurance' },
    { label: "What's covered?", prompt: 'What does my auto policy cover?' },
    { label: 'Upload Image', prompt: '', action: 'upload' },
  ];

  return (
    <div className="flex-1 flex flex-col bg-white dark:bg-gray-900">
      {/* Chat Header */}
      <div className="border-b border-gray-200 dark:border-gray-700 px-6 py-4 flex items-center justify-between bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="flex items-center gap-3">
          {/* ===== LEMON MASCOT LOGO ===== */}
          <div className="relative">
            <LemonMascotLogo size={44} />
            {isConnected && (
              <span className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-500 border-2 border-white dark:border-gray-900 rounded-full animate-pulse" />
            )}
          </div>
          <div>
            <h2 className="text-sm font-semibold text-gray-900 dark:text-white">Insurance Assistant</h2>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {isConnected ? '🟢 Online' : '🔴 Connecting...'}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button 
            onClick={() => setShowDocumentUpload(!showDocumentUpload)}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors group"
            title="Upload Document"
          >
            <FileText className="w-4 h-4 text-gray-500 dark:text-gray-400 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors" />
          </button>
          <button 
            onClick={handleNewChat}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors group"
            title="New Chat"
          >
            <Plus className="w-4 h-4 text-gray-500 dark:text-gray-400 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors" />
          </button>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center max-w-2xl mx-auto">
            {/* ===== LEMON MASCOT LOGO (Welcome Screen - Larger) ===== */}
            <div className="relative mb-6">
              <LemonMascotLogo size={100} />
              <div className="absolute -top-1 -right-1 w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center">
                <span className="text-xs text-white font-bold">AI</span>
              </div>
            </div>

            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
              Lemonade AI
            </h1>
            <p className="text-gray-500 dark:text-gray-400 text-lg mb-8">
              Your intelligent insurance assistant
            </p>

            <div className="grid grid-cols-2 gap-3 w-full max-w-md">
              {suggestions.map((suggestion) => (
                <button
                  key={suggestion.label}
                  onClick={() => {
                    if (suggestion.action === 'upload') {
                      fileInputRef.current?.click();
                    } else {
                      setInput(suggestion.prompt);
                      setTimeout(handleSend, 100);
                    }
                  }}
                  className="p-3 bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-xl border border-gray-200 dark:border-gray-700 transition-all hover:border-blue-300 dark:hover:border-blue-700 text-sm text-gray-700 dark:text-gray-300 text-center"
                >
                  {suggestion.label}
                </button>
              ))}
            </div>

            <p className="mt-8 text-xs text-gray-400 dark:text-gray-500">
              Powered by DeepSeek LLM • Enterprise RAG System • Vision AI
            </p>
          </div>
        ) : (
          messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 dark:border-gray-700 px-4 py-4 bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm">
        <div className="flex flex-col max-w-4xl mx-auto">
          
          {/* Image Preview (above input) */}
          {selectedImage && (
            <div className="mb-3 flex items-center gap-2 flex-wrap">
              <ImagePreview
                file={selectedImage}
                onRemove={removeImage}
                isUploading={isAnalyzing}
                analysisResult={analysisResult}
                error={imageError}
              />
              {analysisResult && analysisResult.classification !== 'other' && (
                <span className="text-xs text-green-600 dark:text-green-400 font-medium">
                  ✅ Analysis complete
                </span>
              )}
              {imageError && (
                <span className="text-xs text-red-600 dark:text-red-400 font-medium">
                  {imageError}
                </span>
              )}
            </div>
          )}

          {/* Input Row */}
          <div className="flex items-end gap-3">
            {/* Voice Button */}
            <button
              onClick={toggleListening}
              className={`p-2.5 rounded-xl transition-colors flex-shrink-0 ${
                isListening 
                  ? 'bg-red-500 hover:bg-red-600 text-white animate-pulse' 
                  : 'bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-400'
              }`}
              title={isListening ? 'Stop recording' : 'Start voice input'}
            >
              {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
            </button>

            {/* Image Upload Button */}
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleImageSelect}
              className="hidden"
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={isAnalyzing || !!selectedImage}
              className={`p-2.5 rounded-xl transition-colors flex-shrink-0 ${
                isAnalyzing || selectedImage
                  ? 'bg-gray-100 dark:bg-gray-800 text-gray-400 cursor-not-allowed'
                  : 'bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-400'
              }`}
              title="Upload image for analysis"
            >
              {isAnalyzing ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Image className="w-5 h-5" />
              )}
            </button>
            
            <div className="flex-1 relative">
              <textarea
                ref={textareaRef}
                value={input}
                onChange={handleInputChange}
                onKeyDown={handleKeyDown}
                placeholder={isListening ? '🎤 Listening...' : 'Ask anything about insurance...'}
                rows={1}
                className={`w-full resize-none border rounded-xl px-4 py-2.5 pr-12 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-shadow text-sm leading-relaxed ${
                  isListening 
                    ? 'border-red-300 dark:border-red-700 bg-red-50 dark:bg-red-900/20' 
                    : 'border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 hover:bg-white dark:hover:bg-gray-700 text-gray-900 dark:text-white'
                }`}
                style={{ minHeight: '52px', maxHeight: '200px' }}
              />
              <button
                onClick={handleSend}
                disabled={!input.trim()}
                className="absolute right-2 bottom-2 p-1.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
              >
                <Send className="w-4 h-5" />
              </button>
            </div>
          </div>

          {isListening && (
            <p className="text-xs text-red-500 dark:text-red-400 text-center mt-2 animate-pulse">
              🎤 Listening... Speak now
            </p>
          )}
          {!isListening && (
            <p className="text-[10px] text-gray-400 dark:text-gray-500 text-center mt-2">
              Press Enter to send, Shift+Enter for new line, click mic for voice
            </p>
          )}
        </div>
      </div>

      {/* Document Upload Modal */}
      {showDocumentUpload && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" onClick={() => setShowDocumentUpload(false)}>
          <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto mx-4 p-6" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">Upload Document</h2>
              <button
                onClick={() => setShowDocumentUpload(false)}
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>
            <DocumentUpload />
          </div>
        </div>
      )}
    </div>
  );
};