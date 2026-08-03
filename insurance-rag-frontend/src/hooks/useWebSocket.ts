// src/hooks/useWebSocket.ts
import { useEffect, useRef, useState } from 'react';
import { useChatStore } from '../stores/chatStore';

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

export const useWebSocket = (sessionId: string) => {
  const [isConnected, setIsConnected] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const wsRef = useRef<WebSocket | null>(null);
  const recognitionRef = useRef<any>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const { addMessage, updateLastMessage, setProcessing } = useChatStore();

  const getWebSocketUrl = (sessionId: string): string => {
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8001/api';
    const baseUrl = apiUrl.replace(/\/api$/, '');
    
    // Remove trailing slash if present
    let cleanBaseUrl = baseUrl;
    if (cleanBaseUrl.endsWith('/')) {
      cleanBaseUrl = cleanBaseUrl.slice(0, -1);
    }
    
    const wsUrl = cleanBaseUrl.replace(/^http/, 'ws');
    const finalUrl = `${wsUrl}/ws/${sessionId}`;
    console.log('🔍 Generated WebSocket URL:', finalUrl);
    
    return finalUrl;
  };

  // Initialize Speech Recognition
  useEffect(() => {
    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onresult = (event: any) => {
        let finalTranscript = '';
        let interimTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript;
          } else {
            interimTranscript += transcript;
          }
        }

        setTranscript(finalTranscript || interimTranscript);

        if (finalTranscript) {
          const message = finalTranscript.trim();
          if (message) {
            startChat(message);
          }
        }
      };

      recognitionRef.current.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    }

    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch (e) {}
      }
    };
  }, []);

  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      setIsListening(true);
      setTranscript('');
      try {
        recognitionRef.current.start();
      } catch (e) {
        console.log('Speech recognition already started');
      }
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      try {
        recognitionRef.current.stop();
      } catch (e) {}
      setIsListening(false);
    }
  };

  const connect = () => {
    try {
      const wsUrl = getWebSocketUrl(sessionId);
      console.log('🔗 Connecting to WebSocket:', wsUrl);
      
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        console.log('✅ WebSocket connected to:', wsUrl);

        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
        }
        pingIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping' }));
          }
        }, 15000);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('📨 Received:', data.type);

          switch (data.type) {
            case 'start':
              setProcessing(true);
              break;

            case 'premium_calculation':
              console.log('💰 Premium data:', data.data);
              updateLastMessage({
                content: `💰 **Premium Calculation:**\nMonthly: $${data.data.monthly}\nYearly: $${data.data.yearly}`,
                isStreaming: false,
                premiumData: data.data
              });
              break;

            case 'final':
              updateLastMessage({
                content: data.response,
                isStreaming: false,
                modelUsed: data.model_used,
                sources: data.sources || []
              });
              setProcessing(false);
              break;

            case 'done':
              setProcessing(false);
              break;

            case 'error':
              console.error('❌ Error:', data.message);
              updateLastMessage({
                content: `❌ Error: ${data.message}`,
                isStreaming: false
              });
              setProcessing(false);
              break;

            case 'ping':
              ws.send(JSON.stringify({ type: 'pong' }));
              break;

            case 'pong':
              break;

            default:
              console.log('Unknown message type:', data.type);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        setIsConnected(false);
      };

      ws.onclose = (event) => {
        setIsConnected(false);
        console.log(`🔌 WebSocket disconnected - Code: ${event.code}, Reason: ${event.reason}`);

        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
          pingIntervalRef.current = null;
        }

        if (event.code !== 1000) {
          if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
          }
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log('🔄 Attempting to reconnect...');
            connect();
          }, 3000);
        }
      };

    } catch (error) {
      console.error('❌ WebSocket connection failed:', error);
    }
  };

  useEffect(() => {
    connect();
    return () => {
      if (pingIntervalRef.current) {
        clearInterval(pingIntervalRef.current);
        pingIntervalRef.current = null;
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
      if (wsRef.current) {
        if (wsRef.current.readyState === WebSocket.OPEN) {
          wsRef.current.close(1000, 'Component unmounting');
        }
        wsRef.current = null;
      }
      stopListening();
    };
  }, [sessionId]);

  const startChat = (query: string) => {
    if (!query.trim()) return;

    addMessage({
      id: Date.now().toString(),
      type: 'user',
      content: query,
      timestamp: new Date()
    });

    addMessage({
      id: (Date.now() + 1).toString(),
      type: 'assistant',
      content: '',
      timestamp: new Date(),
      isStreaming: true
    });

    setTranscript('');

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'chat',
        content: query
      }));
    } else {
      console.warn('⚠️ WebSocket not connected');
    }
  };

  return {
    sendMessage: startChat,
    isConnected,
    startListening,
    stopListening,
    isListening,
    transcript
  };
};