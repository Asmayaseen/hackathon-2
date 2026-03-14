'use client';

/**
 * ChatKit Floating Widget - Phase IV
 *
 * Uses @openai/chatkit-react (useChatKit + ChatKit component)
 * CDN web component loaded in layout.tsx (beforeInteractive)
 * HostedApiConfig: getClientSecret → backend /api/chatkit/session
 * i18n: useTranslation for Urdu / English
 */

import { useChatKit, ChatKit } from '@openai/chatkit-react';
import { useState, useEffect, useCallback } from 'react';
import { MessageCircle, X } from 'lucide-react';
import { useTranslation } from '@/lib/i18n';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function ChatWidget() {
  const { t } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [scriptReady, setScriptReady] = useState(false);

  // Detect CDN script registration
  useEffect(() => {
    if (typeof window === 'undefined') return;
    if (window.customElements?.get('openai-chatkit')) {
      setScriptReady(true);
      return;
    }
    customElements.whenDefined('openai-chatkit').then(() => setScriptReady(true));
  }, []);

  // Auth check on mount
  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    const userId = localStorage.getItem('user_id');
    setIsAuthenticated(!!(token && userId));
  }, []);

  // ChatKit HostedApiConfig — fetches session secret from our backend
  const getClientSecret = useCallback(async (_current: string | null): Promise<string> => {
    const token = localStorage.getItem('auth_token');
    const userId = localStorage.getItem('user_id');
    if (!token || !userId) throw new Error('Not authenticated');

    const res = await fetch(`${API_BASE}/api/chatkit/session`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ user_id: userId }),
    });

    if (!res.ok) throw new Error('Failed to get ChatKit session');
    const data = await res.json();
    return data.client_secret;
  }, []);

  const { control } = useChatKit({
    api: { getClientSecret },
    theme: 'dark',
    onError: ({ error }: { error: unknown }) => {
      console.error('[ChatKit] Error:', error);
    },
  });

  if (!isAuthenticated) return null;

  return (
    <>
      {/* Floating Toggle Button */}
      <button
        onClick={() => setIsOpen((v) => !v)}
        className="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full bg-gradient-to-r from-[#00d9ff] to-[#d946ef] text-white shadow-lg hover:shadow-[0_0_30px_rgba(0,217,255,0.5)] transition-all duration-300 flex items-center justify-center"
        aria-label={isOpen ? t('chat.close') : t('chat.open')}
      >
        {isOpen ? <X size={24} /> : <MessageCircle size={24} />}
      </button>

      {/* ChatKit Widget */}
      {isOpen && scriptReady && (
        <div
          className="fixed bottom-24 right-6 z-50 w-[380px] h-[550px] rounded-2xl overflow-hidden shadow-2xl border border-[rgba(0,217,255,0.3)] bg-[rgba(15,23,42,0.95)] backdrop-blur-xl"
          style={{ boxShadow: '0 0 40px rgba(0,217,255,0.3), 0 0 80px rgba(217,70,239,0.2)' }}
        >
          <div className="bg-gradient-to-r from-[#00d9ff]/20 to-[#d946ef]/20 p-4 border-b border-[rgba(0,217,255,0.2)]">
            <h3 className="text-lg font-bold bg-gradient-to-r from-[#00d9ff] to-[#d946ef] bg-clip-text text-transparent">
              Evolution Todo AI
            </h3>
            <p className="text-xs text-slate-400">{t('chat.subtitle')} • اردو</p>
          </div>
          <div className="h-[calc(100%-80px)]">
            <ChatKit control={control} />
          </div>
        </div>
      )}

      {isOpen && !scriptReady && (
        <div className="fixed bottom-24 right-6 z-50 w-[380px] h-[80px] rounded-2xl flex items-center justify-center bg-[rgba(15,23,42,0.95)] border border-[rgba(0,217,255,0.3)]">
          <p className="text-slate-400 text-sm">{t('chat.loading')}</p>
        </div>
      )}
    </>
  );
}
