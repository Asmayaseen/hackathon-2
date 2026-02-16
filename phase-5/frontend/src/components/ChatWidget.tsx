'use client';

import { useState, useEffect, useRef } from 'react';
import { MessageCircle, X, Send, Loader2 } from 'lucide-react';
import axios from 'axios';
import { useTranslation } from '@/lib/i18n';

interface Message {
  id: number;
  role: 'user' | 'assistant';
  content: string;
}

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    { id: 0, role: 'assistant', content: "Hello! I'm your task management assistant. How can I help you today?" }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    const storedToken = localStorage.getItem('auth_token');
    const storedUserId = localStorage.getItem('user_id');
    if (storedToken && storedUserId) {
      setToken(storedToken);
      setUserId(storedUserId);
    }
  }, []);

  const sendMessage = async () => {
    if (!input.trim() || !userId || !token) return;

    const userMessage = input.trim();
    setInput('');
    setIsLoading(true);

    setMessages(prev => [...prev, {
      id: Date.now(),
      role: 'user',
      content: userMessage
    }]);

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

      if (!conversationId) {
        setConversationId(response.data.conversation_id);
      }

      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.data.response
      }]);
    } catch (error: any) {
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        role: 'assistant',
        content: `Error: ${error.response?.data?.detail || 'Something went wrong'}`
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  if (!userId || !token) return null;

  return (
    <>
      {/* Floating Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 z-50 p-4 bg-gradient-to-r from-[#00d9ff] to-[#d946ef] text-white rounded-full shadow-lg hover:shadow-[0_0_30px_rgba(0,217,255,0.5)] transition-all hover:scale-110"
        >
          <MessageCircle size={24} />
        </button>
      )}

      {/* Chat Widget Panel */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 z-50 w-80 sm:w-96 h-[500px] bg-[rgba(15,23,42,0.95)] backdrop-blur-xl rounded-2xl shadow-2xl border border-[rgba(0,217,255,0.3)] flex flex-col overflow-hidden">
          {/* Header */}
          <div className="p-4 bg-gradient-to-r from-[#00d9ff]/20 to-[#d946ef]/20 border-b border-[rgba(0,217,255,0.2)] flex items-center justify-between">
            <div>
              <h3 className="text-white font-semibold flex items-center gap-2">
                <span className="text-xl">🤖</span> Evolution Todo AI
              </h3>
              <p className="text-xs text-slate-400">Manage tasks in English or Urdu</p>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="p-2 hover:bg-slate-700/50 rounded-lg transition-colors"
            >
              <X size={18} className="text-slate-400" />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] px-3 py-2 rounded-lg text-sm ${
                    message.role === 'user'
                      ? 'bg-gradient-to-r from-[#00d9ff] to-[#d946ef] text-white'
                      : 'bg-slate-700/50 text-slate-200 border border-[rgba(0,217,255,0.2)]'
                  }`}
                >
                  {message.content}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-slate-700/50 px-3 py-2 rounded-lg border border-[rgba(0,217,255,0.2)]">
                  <Loader2 className="animate-spin text-[#00d9ff]" size={16} />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="p-3 border-t border-[rgba(0,217,255,0.2)]">
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                placeholder="Type your message..."
                disabled={isLoading}
                className="flex-1 px-3 py-2 text-sm bg-slate-700/50 border border-[rgba(0,217,255,0.2)] rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-[#00d9ff]"
              />
              <button
                onClick={sendMessage}
                disabled={isLoading || !input.trim()}
                className="p-2 bg-gradient-to-r from-[#00d9ff] to-[#d946ef] text-white rounded-lg hover:shadow-[0_0_15px_rgba(0,217,255,0.4)] disabled:opacity-50 transition-all"
              >
                <Send size={16} />
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
