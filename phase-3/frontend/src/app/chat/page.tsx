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
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Load user session and conversations on mount
  useEffect(() => {
    const loadSession = async () => {
      // Get token and user ID from localStorage (set during login)
      const storedToken = localStorage.getItem('token');
      const storedUserId = localStorage.getItem('userId');

      if (!storedToken || !storedUserId) {
        // Redirect to login if not authenticated
        router.push('/login');
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
      } catch (error) {
        console.error('Error loading conversations:', error);
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

    } catch (error) {
      console.error('Error transcribing audio:', error);
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

  return (
    <div className="flex h-screen bg-[#0a0a0f] relative">
      {/* Cyber Grid Background */}
      <div className="absolute inset-0 opacity-30" style={{
        backgroundImage: 'linear-gradient(to right, rgba(0, 217, 255, 0.06) 1px, transparent 1px), linear-gradient(to bottom, rgba(0, 217, 255, 0.06) 1px, transparent 1px)',
        backgroundSize: '50px 50px'
      }} />

      {/* Sidebar - Conversations List */}
      <div className="w-64 flex flex-col relative z-10 bg-[rgba(15,23,42,0.8)] backdrop-blur-xl border-r border-[rgba(0,217,255,0.2)]">
        <div className="p-4 border-b border-[rgba(0,217,255,0.2)]">
          <button
            onClick={startNewConversation}
            className="w-full px-4 py-2 bg-gradient-to-r from-[#00d9ff] to-[#d946ef] text-white rounded-lg hover:shadow-[0_0_20px_rgba(0,217,255,0.4)] transition-all flex items-center justify-center gap-2"
          >
            <MessageCircle size={20} />
            New Chat
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-2">
          <h3 className="px-2 text-sm font-semibold text-slate-400 mb-2">
            Conversations
          </h3>
          {conversations.map(conv => (
            <button
              key={conv.id}
              onClick={() => loadConversation(conv.id)}
              className={`w-full text-left px-3 py-2 rounded-lg mb-1 transition-all hover:-translate-y-0.5 ${
                conversationId === conv.id
                  ? 'bg-[#00d9ff]/20 text-[#00d9ff] border border-[#00d9ff]/50 shadow-[0_0_20px_rgba(0,217,255,0.3)]'
                  : 'text-slate-200 hover:bg-slate-700/50'
              }`}
            >
              <div className="text-sm font-medium truncate">
                Conversation #{conv.id}
              </div>
              <div className="text-xs text-slate-400">
                {new Date(conv.updated_at).toLocaleDateString()}
              </div>
            </button>
          ))}
        </div>

        <div className="p-4 border-t border-[rgba(0,217,255,0.2)]">
          <button
            onClick={() => router.push('/dashboard')}
            className="w-full px-4 py-2 text-sm text-slate-200 hover:bg-slate-700/50 rounded-lg transition-all"
          >
            ← Back to Dashboard
          </button>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col relative z-10">
        {/* Header */}
        <div className="bg-[rgba(15,23,42,0.8)] backdrop-blur-xl border-b border-[rgba(0,217,255,0.2)] p-4">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-[#00d9ff] to-[#d946ef] bg-clip-text text-transparent">
            🤖 Evolution Todo AI Assistant
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Manage your tasks using natural language in English or Urdu (اردو)
          </p>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-slate-400 mt-20">
              <MessageCircle size={48} className="mx-auto mb-4 opacity-50 text-[#00d9ff] animate-pulse" />
              <p className="text-lg font-medium text-slate-200">Start a conversation</p>
              <p className="text-sm mt-2">
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
                className={`max-w-2xl px-4 py-3 rounded-lg transition-all hover:-translate-y-1 ${
                  message.role === 'user'
                    ? 'bg-gradient-to-r from-[#00d9ff] to-[#d946ef] text-white shadow-[0_0_20px_rgba(0,217,255,0.4)]'
                    : 'bg-[rgba(15,23,42,0.8)] backdrop-blur-xl text-slate-200 border border-[rgba(0,217,255,0.2)]'
                }`}
              >
                <div className="whitespace-pre-wrap">{message.content}</div>
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
              <div className="bg-[rgba(15,23,42,0.8)] backdrop-blur-xl px-4 py-3 rounded-lg border border-[rgba(0,217,255,0.2)]">
                <Loader2 className="animate-spin text-[#00d9ff]" size={20} />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="bg-[rgba(15,23,42,0.8)] backdrop-blur-xl border-t border-[rgba(0,217,255,0.2)] p-4">
          <div className="flex gap-2">
            <button
              onClick={isRecording ? stopRecording : startRecording}
              disabled={isLoading}
              className={`px-4 py-2 rounded-lg transition-all ${
                isRecording
                  ? 'bg-red-600 hover:bg-red-700 text-white shadow-[0_0_20px_rgba(217,70,239,0.4)]'
                  : 'bg-slate-700 hover:bg-[#00d9ff]/20 text-slate-200 hover:text-[#00d9ff]'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
              title={isRecording ? 'Stop recording (Voice Input - T-CHAT-015)' : 'Start recording'}
            >
              {isRecording ? <MicOff size={20} /> : <Mic size={20} />}
            </button>

            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
              placeholder="Type your message in English or Urdu... اپنا پیغام لکھیں"
              disabled={isLoading}
              className="flex-1 px-4 py-2 border border-[rgba(0,217,255,0.2)] rounded-lg bg-[rgba(15,23,42,0.6)] text-slate-200 placeholder-slate-400 focus:outline-none focus:border-[#00d9ff] focus:shadow-[0_0_15px_rgba(0,217,255,0.3)] transition-all disabled:opacity-50"
            />

            <button
              onClick={sendMessage}
              disabled={isLoading || !input.trim()}
              className="px-6 py-2 bg-gradient-to-r from-[#00d9ff] to-[#d946ef] text-white rounded-lg hover:shadow-[0_0_20px_rgba(0,217,255,0.4)] transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isLoading ? <Loader2 className="animate-spin" size={20} /> : <Send size={20} />}
              Send
            </button>
          </div>

          <div className="mt-2 text-xs text-slate-400 text-center">
            🎤 Voice input supports English & Urdu • 🌐 Powered by GPT-4 • 💾 Stateless architecture
          </div>
        </div>
      </div>
    </div>
  );
}
