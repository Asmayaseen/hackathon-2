/**
 * ChatKit Floating Widget Component
 *
 * Task: T-CHAT-016
 * Spec: specs/phase-3-chatbot/spec.md
 *
 * OpenAI ChatKit integration - floating widget (bottom-right)
 * Handles: history management, UI updates, widget rendering
 */
'use client';

import { useChatKit, ChatKit } from '@openai/chatkit-react';
import { useState, useEffect } from 'react';
import { MessageCircle, X } from 'lucide-react';

export function ChatKitWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [token, setToken] = useState<string | null>(null);
  const [userId, setUserId] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Load auth from localStorage
  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    const storedUserId = localStorage.getItem('userId');

    if (storedToken && storedUserId) {
      setToken(storedToken);
      setUserId(storedUserId);
      setIsAuthenticated(true);
    }
  }, []);

  // ChatKit hook with custom backend
  const chatkit = useChatKit({
    api: {
      domainKey: 'custom',
      url: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/chatkit`,
      fetch: async (url, init) => {
        // Add JWT token to all requests
        const currentToken = localStorage.getItem('token');
        const currentUserId = localStorage.getItem('userId');

        if (!currentToken) {
          throw new Error('Not authenticated');
        }

        // Parse body to add user context
        let body = init?.body;
        if (body && typeof body === 'string') {
          try {
            const parsed = JSON.parse(body);
            parsed.context = {
              user_id: currentUserId,
            };
            body = JSON.stringify(parsed);
          } catch (e) {
            // Keep original body if not JSON
          }
        }

        return fetch(url, {
          ...init,
          body,
          headers: {
            ...init?.headers,
            'Authorization': `Bearer ${currentToken}`,
            'Content-Type': 'application/json',
          },
        });
      },
    },
    onError: ({ error }) => {
      console.error('[ChatKit] Error:', error);
    },
  });

  // Don't render if not authenticated
  if (!isAuthenticated) {
    return null;
  }

  return (
    <>
      {/* Floating Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full bg-gradient-to-r from-[#00d9ff] to-[#d946ef] text-white shadow-lg hover:shadow-[0_0_30px_rgba(0,217,255,0.5)] transition-all duration-300 flex items-center justify-center"
        aria-label={isOpen ? 'Close chat' : 'Open chat'}
      >
        {isOpen ? (
          <X size={24} />
        ) : (
          <MessageCircle size={24} />
        )}
      </button>

      {/* ChatKit Widget Container */}
      {isOpen && (
        <div
          className="fixed bottom-24 right-6 z-50 w-[380px] h-[550px] rounded-2xl overflow-hidden shadow-2xl border border-[rgba(0,217,255,0.3)] bg-[rgba(15,23,42,0.95)] backdrop-blur-xl"
          style={{
            boxShadow: '0 0 40px rgba(0,217,255,0.3), 0 0 80px rgba(217,70,239,0.2)',
          }}
        >
          {/* Header */}
          <div className="bg-gradient-to-r from-[#00d9ff]/20 to-[#d946ef]/20 p-4 border-b border-[rgba(0,217,255,0.2)]">
            <h3 className="text-lg font-bold bg-gradient-to-r from-[#00d9ff] to-[#d946ef] bg-clip-text text-transparent">
              Evolution Todo AI
            </h3>
            <p className="text-xs text-slate-400">
              Manage tasks in English or Urdu
            </p>
          </div>

          {/* ChatKit Component */}
          <div className="h-[calc(100%-80px)]">
            <ChatKit control={chatkit.control} />
          </div>
        </div>
      )}
    </>
  );
}

export default ChatKitWidget;
