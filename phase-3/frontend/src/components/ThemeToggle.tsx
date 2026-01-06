'use client';

import { useTheme } from 'next-themes';
import { useEffect, useState } from 'react';
import { Sun, Moon } from 'lucide-react';

export default function ThemeToggle() {
  const { theme, setTheme, resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  // Avoid hydration mismatch
  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <button
        className="p-2 rounded-xl bg-muted border border-border transition-all duration-300"
        aria-label="Toggle theme"
      >
        <div className="w-5 h-5" />
      </button>
    );
  }

  const isDark = resolvedTheme === 'dark';

  return (
    <button
      onClick={() => setTheme(isDark ? 'light' : 'dark')}
      className={`
        relative p-2.5 rounded-xl transition-all duration-300
        ${isDark
          ? 'bg-slate-800/80 border-2 border-cyan-500/30 hover:border-cyan-400 hover:shadow-[0_0_20px_rgba(0,217,255,0.3)]'
          : 'bg-slate-100 border-2 border-purple-300 hover:border-purple-400 hover:shadow-lg'
        }
      `}
      aria-label={`Switch to ${isDark ? 'light' : 'dark'} mode`}
    >
      <div className="relative w-5 h-5">
        {isDark ? (
          <Sun className="w-5 h-5 text-cyan-400 transition-transform duration-300 hover:rotate-45" />
        ) : (
          <Moon className="w-5 h-5 text-purple-600 transition-transform duration-300 hover:-rotate-12" />
        )}
      </div>
    </button>
  );
}
