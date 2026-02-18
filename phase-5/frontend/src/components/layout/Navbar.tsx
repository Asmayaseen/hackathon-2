'use client';

import { useTheme } from 'next-themes';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import ThemeToggle from '../ThemeToggle';
import { LayoutDashboard, CheckSquare, History, Bell, Settings, LogOut, Menu, X, MessageCircle } from 'lucide-react';
import { useTranslation } from '@/lib/i18n';

export default function Navbar() {
  const { t } = useTranslation();
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<{ name?: string; email?: string } | null>(null);
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  useEffect(() => {
    const userName = localStorage.getItem('user_name');
    const userEmail = localStorage.getItem('user_email');
    if (userEmail) {
      setUser({ name: userName || undefined, email: userEmail });
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('user_email');
    localStorage.removeItem('user_name');
    document.cookie = 'auth_token=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;';
    router.push('/auth/signin');
  };

  const navItems: Array<{
    name: string;
    href: string;
    icon: React.ReactNode;
    highlight?: boolean;
  }> = [
    { name: t('nav.tasks'), href: '/tasks', icon: <CheckSquare className="w-5 h-5" /> },
    { name: t('nav.dashboard'), href: '/dashboard', icon: <LayoutDashboard className="w-5 h-5" /> },
    { name: t('nav.aiChat'), href: '/chat', icon: <MessageCircle className="w-5 h-5" />, highlight: true },
    { name: t('nav.history'), href: '/history', icon: <History className="w-5 h-5" /> },
    { name: t('nav.notifications'), href: '/notifications', icon: <Bell className="w-5 h-5" /> },
    { name: t('nav.settings'), href: '/settings', icon: <Settings className="w-5 h-5" /> },
  ];

  return (
    <nav className="sticky top-0 z-50 bg-card/80 backdrop-blur-xl border-b-2 border-cyan-500/20">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link href="/tasks" className="flex items-center space-x-3 group">
            <div className="relative w-10 h-10">
              <div className="absolute inset-0 bg-gradient-to-br from-cyan-400 to-fuchsia-500 rounded-xl blur-md opacity-60 group-hover:opacity-100 transition-opacity" />
              <div className="relative w-full h-full bg-gradient-to-br from-cyan-500 to-fuchsia-500 rounded-xl flex items-center justify-center border-2 border-cyan-400/50">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-fuchsia-400 bg-clip-text text-transparent tracking-wider hidden sm:block">
              {t('auth.neuralTasks')}
            </span>
          </Link>

          {/* Desktop Nav */}
          <div className="hidden lg:flex items-center space-x-1">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center space-x-2 px-3 py-2 rounded-xl transition-all duration-200 ${
                  item.highlight
                    ? pathname === item.href
                      ? 'bg-gradient-to-r from-cyan-500/20 to-fuchsia-500/20 text-cyan-400 border border-cyan-500/50 shadow-[0_0_15px_rgba(0,217,255,0.3)]'
                      : 'text-cyan-400 hover:bg-gradient-to-r hover:from-cyan-500/10 hover:to-fuchsia-500/10 border border-transparent hover:border-cyan-500/30'
                    : pathname === item.href
                    ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'
                    : 'text-muted-foreground hover:text-cyan-400 hover:bg-cyan-500/5'
                }`}
              >
                {item.icon}
                <span className="font-medium">{item.name}</span>
              </Link>
            ))}
          </div>

          {/* Right section */}
          <div className="flex items-center gap-3">
            <div className="hidden md:flex items-center gap-2 px-3 py-1.5 bg-card/50 rounded-lg border border-cyan-500/10">
              <div className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse" />
              <span className="text-xs text-muted-foreground max-w-[120px] truncate">
                {user?.name || user?.email || t('common.authenticated')}
              </span>
            </div>
            <ThemeToggle />

            <button
              onClick={handleLogout}
              className="hidden sm:flex p-2 rounded-xl bg-card/50 border border-red-500/20 text-red-400 hover:border-red-400 hover:bg-red-500/5 transition-all"
              title={t('common.logout')}
            >
              <LogOut className="w-5 h-5" />
            </button>

            {/* Mobile menu button */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="lg:hidden p-2 rounded-xl bg-card/50 border border-cyan-500/20 text-cyan-400"
            >
              {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Nav */}
        {isMenuOpen && (
          <div className="lg:hidden pb-4 space-y-1 animate-in slide-in-from-top duration-300">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setIsMenuOpen(false)}
                className={`flex items-center space-x-3 px-4 py-3 rounded-xl transition-all ${
                  item.highlight
                    ? pathname === item.href
                      ? 'bg-gradient-to-r from-cyan-500/20 to-fuchsia-500/20 text-cyan-400 border border-cyan-500/50 shadow-[0_0_20px_rgba(0,217,255,0.3)]'
                      : 'text-cyan-400 border border-cyan-500/20 hover:bg-gradient-to-r hover:from-cyan-500/10 hover:to-fuchsia-500/10'
                    : pathname === item.href
                    ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 shadow-[0_0_15px_rgba(34,211,238,0.1)]'
                    : 'text-muted-foreground hover:bg-cyan-500/5'
                }`}
              >
                {item.icon}
                <span className="font-bold tracking-wide uppercase text-sm">{item.name}</span>
              </Link>
            ))}
            <button
              onClick={handleLogout}
              className="flex items-center space-x-3 px-4 py-3 rounded-xl w-full text-red-400 hover:bg-red-500/5 transition-all border border-transparent hover:border-red-500/20"
            >
              <LogOut className="w-5 h-5" />
              <span className="font-bold tracking-wide uppercase text-sm">{t('common.logoutTerminal')}</span>
            </button>
          </div>
        )}
      </div>
    </nav>
  );
}
