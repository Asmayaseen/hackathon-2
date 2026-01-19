/**
 * AI-Powered Todo Chatbot Page - Phase III
 *
 * Task: T-CHAT-014
 * Spec: specs/phase-3-chatbot/spec.md (US-CHAT-1 through US-CHAT-8)
 *
 * Features:
 * - Natural language task management
 * - Voice input support (Whisper STT)
 * - Urdu language support
 * - Stateless conversation persistence
 */
'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { Send, Mic, MicOff, Loader2, MessageCircle, Trash2 } from 'lucide-react';
import axios from 'axios';

interface Message {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  tool_calls?: Array<{ tool: string; args: any }>;
  created_at: string;
}

interface Conversation {
  id: number;
  created_at: string;
  updated_at: string;
}

export default function ChatPage() {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [userId, setUserId] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Helper function to check if token is expired
  const isTokenExpired = (token: string): boolean => {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const exp = payload.exp * 1000; // Convert to milliseconds
      return Date.now() >= exp;
    } catch {
      return true; // If can't decode, consider expired
    }
  };

  // Helper function to handle authentication errors
  const handleAuthError = () => {
    console.error('Authentication failed - redirecting to login');
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_id');
    router.push('/auth/signin');
  };

  // Load user session and conversations on mount
  useEffect(() => {
    const loadSession = async () => {
      // Get token and user ID from localStorage (set during login)
      const storedToken = localStorage.getItem('auth_token');
      const storedUserId = localStorage.getItem('user_id');

      if (!storedToken || !storedUserId) {
        // Redirect to login if not authenticated
        console.log('No token or userId found - redirecting to login');
        router.push('/login');
        return;
      }

      // Check if token is expired
      if (isTokenExpired(storedToken)) {
        console.log('Token expired - redirecting to login');
        handleAuthError();
        return;
      }

      setToken(storedToken);
      setUserId(storedUserId);

      // Load user's conversations
      try {
        const response = await axios.get(
          `${process.env.NEXT_PUBLIC_API_URL}/api/${storedUserId}/conversations`,
          {
            headers: { Authorization: `Bearer ${storedToken}` }
          }
        );
        setConversations(response.data);
      } catch (error: any) {
        console.error('Error loading conversations:', error);

        // Handle 401 Unauthorized - token is invalid or expired
        if (error.response?.status === 401) {
          console.log('401 Unauthorized - token invalid');
          handleAuthError();
        }
      }
    };

    loadSession();
  }, [router]);

  // Load conversation messages
  const loadConversation = async (convId: number) => {
    if (!userId || !token) return;

    try {
      const response = await axios.get(
        `${process.env.NEXT_PUBLIC_API_URL}/api/${userId}/conversations/${convId}/messages`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      setMessages(response.data);
      setConversationId(convId);
    } catch (error) {
      console.error('Error loading conversation:', error);
    }
  };

  // Send message to AI chatbot
  const sendMessage = async () => {
    if (!input.trim() || !userId || !token) return;

    const userMessage = input.trim();
    setInput('');
    setIsLoading(true);

    // Optimistically add user message to UI
    const tempMessage: Message = {
      id: Date.now(),
      role: 'user',
      content: userMessage,
      created_at: new Date().toISOString()
    };
    setMessages(prev => [...prev, tempMessage]);

    try {
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/api/${userId}/chat`,
        {
          conversation_id: conversationId,
          message: userMessage
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      // Update conversation ID if this was first message
      if (!conversationId) {
        setConversationId(response.data.conversation_id);
      }

      // Add assistant response to messages
      const assistantMessage: Message = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.data.response,
        tool_calls: response.data.tool_calls,
        created_at: new Date().toISOString()
      };

      // Replace temp message with real ones from server
      setMessages(prev => [
        ...prev.slice(0, -1),
        tempMessage,
        assistantMessage
      ]);

      // Reload conversations list to show updated timestamp
      const convsResponse = await axios.get(
        `${process.env.NEXT_PUBLIC_API_URL}/api/${userId}/conversations`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      setConversations(convsResponse.data);

    } catch (error: any) {
      console.error('Error sending message:', error);

      // Handle 401 Unauthorized - token is invalid or expired
      if (error.response?.status === 401) {
        console.log('401 Unauthorized - token invalid');
        handleAuthError();
        return;
      }

      // Add error message
      setMessages(prev => [
        ...prev,
        {
          id: Date.now() + 1,
          role: 'assistant',
          content: `❌ Error: ${error.response?.data?.detail || error.message}`,
          created_at: new Date().toISOString()
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // Start voice recording
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        await transcribeAudio(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error starting recording:', error);
      alert('Could not access microphone. Please allow microphone permissions.');
    }
  };

  // Stop voice recording
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  // Transcribe audio using backend Whisper endpoint (avoids CORS)
  const transcribeAudio = async (audioBlob: Blob) => {
    if (!token || !userId) return;

    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'audio.webm');

      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/api/${userId}/transcribe`,
        formData,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        }
      );

      const transcribedText = response.data.text;
      setInput(transcribedText);

      // Auto-send after transcription (optional)
      // await sendMessage();

    } catch (error: any) {
      console.error('Error transcribing audio:', error);

      // Handle 401 Unauthorized - token is invalid or expired
      if (error.response?.status === 401) {
        console.log('401 Unauthorized - token invalid');
        handleAuthError();
        return;
      }

      alert('Failed to transcribe audio. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Start new conversation
  const startNewConversation = () => {
    setConversationId(null);
    setMessages([]);
  };

  // Toggle sidebar
  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <div className="flex h-screen bg-[#0a0a0f] relative overflow-hidden">
      {/* Cyber Grid Background */}
      <div className="absolute inset-0 opacity-30" style={{
        backgroundImage: 'linear-gradient(to right, rgba(0, 217, 255, 0.06) 1px, transparent 1px), linear-gradient(to bottom, rgba(0, 217, 255, 0.06) 1px, transparent 1px)',
        backgroundSize: '50px 50px'
      }} />

      {/* Mobile Header */}
      <div className="lg:hidden fixed top-0 left-0 right-0 z-50 bg-[rgba(15,23,42,0.95)] backdrop-blur-xl border-b border-[rgba(0,217,255,0.2)] p-3 flex items-center justify-between">
        <button
          onClick={toggleSidebar}
          className="p-2 rounded-lg bg-[rgba(0,217,255,0.2)] text-[#00d9ff]"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <h1 className="text-lg font-bold bg-gradient-to-r from-[#00d9ff] to-[#d946ef] bg-clip-text text-transparent">
          🤖 AI Assistant
        </h1>
        <div className="w-10" />
      </div>

      {/* Sidebar - Conversations List */}
      <div className={`${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'} fixed lg:relative z-40 lg:z-10 w-64 lg:w-64 md:w-72 h-full transition-transform duration-300 ease-in-out flex flex-col bg-[rgba(15,23,42,0.95)] lg:bg-[rgba(15,23,42,0.8)] backdrop-blur-xl border-r border-[rgba(0,217,255,0.2)] pt-16 lg:pt-0`}>
        {/* Sidebar overlay for mobile */}
        {sidebarOpen && (
          <div
            className="lg:hidden fixed inset-0 bg-black/50 z-[-1]"
            onClick={toggleSidebar}
          />
        )}

        <div className="p-4 border-b border-[rgba(0,217,255,0.2)] hidden lg:block">
          <button
            onClick={startNewConversation}
            className="w-full px-4 py-2 bg-gradient-to-r from-[#00d9ff] to-[#d946ef] text-white rounded-lg hover:shadow-[0_0_20px_rgba(0,217,255,0.4)] transition-all flex items-center justify-center gap-2 text-sm"
          >
            <MessageCircle size={18} />
            New Chat
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-2">
          <h3 className="px-2 text-xs sm:text-sm font-semibold text-slate-400 mb-2">
            Conversations
          </h3>
          {conversations.map(conv => (
            <button
              key={conv.id}
              onClick={() => {
                loadConversation(conv.id);
                if (typeof window !== 'undefined' && window.innerWidth < 1024) {
                  setSidebarOpen(false);
                }
              }}
              className={`w-full text-left px-3 py-2 rounded-lg mb-1 transition-all hover:-translate-y-0.5 text-xs sm:text-sm ${
                conversationId === conv.id
                  ? 'bg-[#00d9ff]/20 text-[#00d9ff] border border-[#00d9ff]/50 shadow-[0_0_20px_rgba(0,217,255,0.3)]'
                  : 'text-slate-200 hover:bg-slate-700/50'
              }`}
            >
              <div className="font-medium truncate">
                Conversation #{conv.id}
              </div>
              <div className="text-xs text-slate-400">
                {new Date(conv.updated_at).toLocaleDateString()}
              </div>
            </button>
          ))}
        </div>

        <div className="p-3 sm:p-4 border-t border-[rgba(0,217,255,0.2)]">
          <button
            onClick={() => router.push('/dashboard')}
            className="w-full px-3 sm:px-4 py-2 text-xs sm:text-sm text-slate-200 hover:bg-slate-700/50 rounded-lg transition-all flex items-center justify-center gap-2"
          >
            ← Back to Dashboard
          </button>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col h-full relative z-10 pt-14 lg:pt-0">
        {/* Header */}
        <div className="hidden lg:block bg-[rgba(15,23,42,0.8)] backdrop-blur-xl border-b border-[rgba(0,217,255,0.2)] p-3 sm:p-4">
          <h1 className="text-lg sm:text-xl md:text-2xl font-bold bg-gradient-to-r from-[#00d9ff] to-[#d946ef] bg-clip-text text-transparent">
            🤖 Evolution Todo AI Assistant
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Manage your tasks using natural language in English or Urdu (اردو)
          </p>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-3 sm:p-4 space-y-3 sm:space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-slate-400 mt-10 sm:mt-20">
              <MessageCircle size={36} className="mx-auto mb-3 sm:mb-4 opacity-50 text-[#00d9ff] animate-pulse" />
              <p className="text-base sm:text-lg font-medium text-slate-200">Start a conversation</p>
              <p className="text-xs sm:text-sm mt-2 px-4">
                Try: "Add a task to buy groceries tomorrow" or "اپنی فہرست دکھائیں"
              </p>
            </div>
          )}

          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[85%] sm:max-w-[75%] md:max-w-2xl px-3 sm:px-4 py-2 sm:py-3 rounded-lg transition-all hover:-translate-y-1 ${
                  message.role === 'user'
                    ? 'bg-gradient-to-r from-[#00d9ff] to-[#d946ef] text-white shadow-[0_0_20px_rgba(0,217,255,0.4)]'
                    : 'bg-[rgba(15,23,42,0.8)] backdrop-blur-xl text-slate-200 border border-[rgba(0,217,255,0.2)]'
                }`}
              >
                <div className="whitespace-pre-wrap text-xs sm:text-sm">{message.content}</div>
                {message.tool_calls && message.tool_calls.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-[rgba(0,217,255,0.3)] text-xs opacity-75">
                    🔧 Tools used: {message.tool_calls.map(tc => tc.tool).join(', ')}
                  </div>
                )}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-[rgba(15,23,42,0.8)] backdrop-blur-xl px-3 sm:px-4 py-2 sm:py-3 rounded-lg border border-[rgba(0,217,255,0.2)]">
                <Loader2 className="animate-spin text-[#00d9ff]" size={18} />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="bg-[rgba(15,23,42,0.9)] backdrop-blur-xl border-t border-[rgba(0,217,255,0.2)] p-3 sm:p-4">
          <div className="flex gap-2">
            <button
              onClick={isRecording ? stopRecording : startRecording}
              disabled={isLoading}
              className={`shrink-0 px-3 sm:px-4 py-2 rounded-lg transition-all ${
                isRecording
                  ? 'bg-red-600 hover:bg-red-700 text-white shadow-[0_0_20px_rgba(217,70,239,0.4)]'
                  : 'bg-slate-700 hover:bg-[#00d9ff]/20 text-slate-200 hover:text-[#00d9ff]'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
              title={isRecording ? 'Stop recording' : 'Start recording'}
            >
              {isRecording ? <MicOff size={18} /> : <Mic size={18} />}
            </button>

            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
              placeholder="Type your message..."
              disabled={isLoading}
              className="flex-1 px-3 sm:px-4 py-2 text-sm sm:text-base border border-[rgba(0,217,255,0.2)] rounded-lg bg-[rgba(15,23,42,0.6)] text-slate-200 placeholder-slate-400 focus:outline-none focus:border-[#00d9ff] focus:shadow-[0_0_15px_rgba(0,217,255,0.3)] transition-all disabled:opacity-50"
            />

            <button
              onClick={sendMessage}
              disabled={isLoading || !input.trim()}
              className="shrink-0 px-4 sm:px-6 py-2 bg-gradient-to-r from-[#00d9ff] to-[#d946ef] text-white rounded-lg hover:shadow-[0_0_20px_rgba(0,217,255,0.4)] transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 text-sm"
            >
              {isLoading ? <Loader2 className="animate-spin" size={16} /> : <Send size={16} />}
              <span className="hidden sm:inline">Send</span>
            </button>
          </div>

          <div className="mt-2 text-[10px] sm:text-xs text-slate-400 text-center">
            🎤 Voice input supports English & Urdu
          </div>
        </div>
      </div>
    </div>
  );
}
