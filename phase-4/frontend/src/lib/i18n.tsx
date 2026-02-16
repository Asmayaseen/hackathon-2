'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import en from '@/locales/en.json';
import ur from '@/locales/ur.json';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------
export type Locale = 'en' | 'ur';

type NestedMessages = { [key: string]: string | NestedMessages };

const messages: Record<Locale, NestedMessages> = { en, ur };

// RTL languages
const RTL_LOCALES: Locale[] = ['ur'];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Resolve a dot-separated key against a nested JSON object.
 * Falls back to English if the key is missing, then to the raw key.
 */
function resolve(obj: NestedMessages, path: string): string {
  const parts = path.split('.');
  let current: NestedMessages | string = obj;

  for (const part of parts) {
    if (typeof current === 'string') return path; // can't go deeper
    current = current[part];
    if (current === undefined) return path; // key not found
  }

  return typeof current === 'string' ? current : path;
}

// ---------------------------------------------------------------------------
// Context
// ---------------------------------------------------------------------------
interface I18nContextValue {
  locale: Locale;
  setLocale: (l: Locale) => void;
  t: (key: string) => string;
  dir: 'ltr' | 'rtl';
  isRTL: boolean;
}

const I18nContext = createContext<I18nContextValue | null>(null);

// ---------------------------------------------------------------------------
// Provider
// ---------------------------------------------------------------------------
export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>('en');

  // Hydrate from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem('app_language') as Locale | null;
    if (stored && messages[stored]) {
      setLocaleState(stored);
    }
  }, []);

  // Persist and update document attributes when locale changes
  useEffect(() => {
    localStorage.setItem('app_language', locale);
    document.documentElement.lang = locale === 'ur' ? 'ur' : 'en';
    document.documentElement.dir = RTL_LOCALES.includes(locale) ? 'rtl' : 'ltr';
  }, [locale]);

  const setLocale = useCallback((l: Locale) => {
    if (messages[l]) setLocaleState(l);
  }, []);

  const t = useCallback(
    (key: string): string => {
      // Try current locale first, fallback to English, then raw key
      const result = resolve(messages[locale], key);
      if (result !== key) return result;
      if (locale !== 'en') return resolve(messages.en, key);
      return key;
    },
    [locale],
  );

  const dir = RTL_LOCALES.includes(locale) ? 'rtl' : 'ltr';
  const isRTL = dir === 'rtl';

  return (
    <I18nContext.Provider value={{ locale, setLocale, t, dir, isRTL }}>
      {children}
    </I18nContext.Provider>
  );
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------
export function useTranslation() {
  const ctx = useContext(I18nContext);
  if (!ctx) {
    throw new Error('useTranslation must be used within a <LanguageProvider>');
  }
  return ctx;
}
