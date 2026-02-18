'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Navbar from '@/components/layout/Navbar';
import { api } from '@/lib/api';
import { Settings, User, Bell, Shield, Palette, Globe, Clock, Save, Loader2, Lock, Key, Eye, Moon, Sun, Monitor } from 'lucide-react';
import { useTranslation, Locale } from '@/lib/i18n';

type TabId = 'general' | 'appearance' | 'notifications' | 'security';

export default function SettingsPage() {
  const router = useRouter();
  const { locale, setLocale, t } = useTranslation();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<TabId>('general');
  const [preferences, setPreferences] = useState({
    theme: 'dark', // ONLY 'light' or 'dark' allowed (NOT 'system')
    language: 'en', // ONLY 'en' or 'ur' allowed
    timezone: 'UTC',
    email_notifications: true,
    push_notifications: false,
    default_priority: 'none',
  });
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

  // Security state
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [showSessionsModal, setShowSessionsModal] = useState(false);
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordChanging, setPasswordChanging] = useState(false);
  const [sessions, setSessions] = useState<Array<{ session_id: string; device: string; location: string; last_active: string; is_current: boolean }>>([]);
  const [sessionsLoading, setSessionsLoading] = useState(false);
  const [twoFactorEnabled, setTwoFactorEnabled] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    const storedUserId = localStorage.getItem('user_id');

    if (!token || !storedUserId) {
      router.push('/auth/signin');
      return;
    }

    setUserId(storedUserId);

    const fetchPreferences = async () => {
      try {
        const data = await api.getPreferences(storedUserId);
        console.log('📥 Fetched preferences from backend:', data);

        if (data) {
          // CRITICAL: Clean and validate ALL fields
          const validLanguages = ['en', 'ur'];
          const cleanData = {
            theme: data.theme || 'dark',
            language: validLanguages.includes(data.language) ? data.language : 'en',
            timezone: data.timezone || 'UTC',
            email_notifications: data.notifications_enabled ?? true,
            push_notifications: data.notification_sound ?? false,
            default_priority: data.default_priority || 'none',
          };
          console.log('✅ Cleaned preferences:', cleanData);
          console.log('   Original language was:', data.language);
          console.log('   Cleaned language is:', cleanData.language);

          setPreferences(cleanData);
          // Sync i18n context with backend preference
          setLocale(cleanData.language as Locale);
        }
      } catch (err: any) {
        console.error('Failed to fetch preferences:', err);
        // Fallback to default preferences if backend endpoint not available
        if (err.response?.status === 404) {
          console.warn('⚠️ Preferences endpoint not available, using defaults');
          setMessage({
            type: 'error',
            text: 'Settings feature is being deployed. Using default preferences for now.'
          });
        }
      } finally {
        setLoading(false);
      }
    };

    fetchPreferences();
  }, [router]);

  const handleSave = async () => {
    if (!userId) {
      console.error('❌ No userId found!');
      setMessage({ type: 'error', text: 'User ID not found. Please login again.' });
      return;
    }

    console.log('🚀 Starting save...');
    console.log('  userId:', userId);
    console.log('  preferences:', preferences);
    console.log('  API URL:', process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000');

    // FINAL validation before sending
    const validLanguages = ['en', 'ur'];
    if (!validLanguages.includes(preferences.language)) {
      console.error('❌ INVALID LANGUAGE DETECTED:', preferences.language);
      setMessage({ type: 'error', text: `Invalid language: ${preferences.language}. Resetting to English.` });
      setPreferences({ ...preferences, language: 'en' });
      return;
    }

    setSaving(true);
    setMessage(null);
    try {
      // Map frontend field names to backend field names
      const backendData = {
        theme: preferences.theme,
        language: preferences.language,
        timezone: preferences.timezone,
        notifications_enabled: preferences.email_notifications,
        notification_sound: preferences.push_notifications,
        default_priority: preferences.default_priority,
      };
      console.log('📤 Sending to backend:', backendData);
      const result = await api.updatePreferences(userId, backendData);
      console.log('✅ Save successful:', result);
      setMessage({ type: 'success', text: 'Terminal configurations updated successfully.' });
      setTimeout(() => setMessage(null), 3000);
    } catch (err: any) {
      console.error('❌ Save failed:', err);
      console.error('  Error message:', err.message);
      console.error('  Error response:', err.response);
      console.error('  Error request:', err.request);
      console.error('  Error config:', err.config);

      // Get detailed error message from backend
      const errorDetail = err.response?.data?.detail || err.message || 'Network error';

      // Special handling for 404 (endpoint not deployed yet)
      if (err.response?.status === 404) {
        setMessage({
          type: 'error',
          text: 'Settings feature is being deployed to the backend. Please try again in a few minutes.'
        });
      } else {
        setMessage({ type: 'error', text: `Failed: ${errorDetail}` });
      }
    } finally {
      setSaving(false);
    }
  };

  // ============ SECURITY HANDLERS ============

  const handleChangePassword = async () => {
    if (!userId) return;

    if (newPassword !== confirmPassword) {
      setMessage({ type: 'error', text: 'New passwords do not match' });
      return;
    }

    if (newPassword.length < 8) {
      setMessage({ type: 'error', text: 'New password must be at least 8 characters' });
      return;
    }

    setPasswordChanging(true);
    try {
      const result = await api.changePassword(userId, currentPassword, newPassword);
      setMessage({ type: 'success', text: result.message });
      setShowPasswordModal(false);
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err: any) {
      const errorDetail = err.response?.data?.detail || 'Failed to change password';
      setMessage({ type: 'error', text: errorDetail });
    } finally {
      setPasswordChanging(false);
    }
  };

  const handleViewSessions = async () => {
    if (!userId) return;

    setSessionsLoading(true);
    setShowSessionsModal(true);
    try {
      const result = await api.getActiveSessions(userId);
      setSessions(result.sessions);
    } catch (err: any) {
      setMessage({ type: 'error', text: 'Failed to load sessions' });
    } finally {
      setSessionsLoading(false);
    }
  };

  const handleLogoutAll = async () => {
    if (!userId) return;

    try {
      const result = await api.logoutAllSessions(userId);
      setMessage({ type: 'success', text: result.message });
      setShowSessionsModal(false);
    } catch (err: any) {
      setMessage({ type: 'error', text: 'Failed to logout sessions' });
    }
  };

  const load2FAStatus = async () => {
    if (!userId) return;
    try {
      const result = await api.get2FAStatus(userId);
      setTwoFactorEnabled(result.enabled);
    } catch (err) {
      console.log('2FA status not available');
    }
  };

  // Load 2FA status when security tab is active
  useEffect(() => {
    if (activeTab === 'security' && userId) {
      load2FAStatus();
    }
  }, [activeTab, userId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <div className="flex items-center justify-center h-[calc(100vh-64px)]">
          <Loader2 className="w-8 h-8 animate-spin text-cyan-500" />
        </div>
      </div>
    );
  }

  const tabs = [
    { id: 'general' as TabId, icon: <User className="w-4 h-4" />, label: t('settings.general') },
    { id: 'appearance' as TabId, icon: <Palette className="w-4 h-4" />, label: t('settings.appearance') },
    { id: 'notifications' as TabId, icon: <Bell className="w-4 h-4" />, label: t('settings.notificationsTab') },
    { id: 'security' as TabId, icon: <Shield className="w-4 h-4" />, label: t('settings.security') },
  ];

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      <div className="absolute inset-0 cyber-grid opacity-20" />
      <Navbar />

      <main className="container mx-auto px-4 py-8 relative z-10">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center space-x-4 mb-8">
            <div className="p-3 rounded-2xl bg-cyan-500/10 border border-cyan-500/30">
              <Settings className="w-8 h-8 text-cyan-400" />
            </div>
            <div>
              <h1 className="text-3xl font-bold uppercase tracking-wider bg-gradient-to-r from-cyan-400 to-fuchsia-500 bg-clip-text text-transparent">
                {t('settings.systemPreferences')}
              </h1>
              <p className="text-muted-foreground uppercase text-xs tracking-[0.2em]">{t('settings.neuralInterfaceConfigs')}</p>
            </div>
          </div>

          {message && (
            <div className={`mb-6 p-4 rounded-xl border-2 animate-in fade-in slide-in-from-top-2 duration-300 ${
              message.type === 'success'
                ? 'bg-green-500/10 border-green-500/30 text-green-400'
                : 'bg-red-500/10 border-red-500/30 text-red-400'
            }`}>
              <p className="text-sm font-bold uppercase tracking-wide flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-current animate-pulse" />
                {message.text}
              </p>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Sidebar Tabs */}
            <div className="space-y-2">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  type="button"
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    console.log(`🔘 Clicked: ${tab.label} (${tab.id})`);
                    console.log(`   Current tab: ${activeTab}`);
                    setActiveTab(tab.id);
                    console.log(`   New tab: ${tab.id}`);
                  }}
                  style={{ cursor: 'pointer', zIndex: 10, position: 'relative' }}
                  className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-sm font-bold uppercase tracking-wider transition-all border ${
                    activeTab === tab.id
                      ? 'bg-cyan-500/10 border-cyan-500/30 text-cyan-400 shadow-[0_0_20px_rgba(34,211,238,0.1)]'
                      : 'border-transparent text-muted-foreground hover:bg-card/50 hover:text-foreground'
                  }`}
                >
                  {tab.icon}
                  <span>{tab.label}</span>
                </button>
              ))}
            </div>

            {/* Main Content */}
            <div className="md:col-span-2">
              <div className="bg-card/50 backdrop-blur-xl border border-cyan-500/10 rounded-2xl p-6 space-y-8 min-h-[400px]">

                {/* GENERAL TAB */}
                {activeTab === 'general' && (
                  <div className="space-y-8 animate-in fade-in slide-in-from-right-5 duration-300">
                    <div className="text-xs text-cyan-400 mb-2">✅ Active Tab: GENERAL</div>
                    {/* Localization */}
                    <section className="space-y-4">
                      <h3 className="text-sm font-bold text-cyan-400 uppercase tracking-[0.2em] flex items-center gap-2">
                        <Globe className="w-4 h-4" /> {t('settings.localizationProtocols')}
                      </h3>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <label className="text-xs uppercase text-muted-foreground font-bold ml-1">{t('settings.interfaceLanguage')}</label>
                          <select
                            value={preferences.language}
                            onChange={(e) => {
                              const lang = e.target.value as Locale;
                              setPreferences({ ...preferences, language: lang });
                              setLocale(lang);
                            }}
                            className="w-full bg-background/50 border border-cyan-500/20 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-cyan-500 transition-all font-medium"
                          >
                            <option value="en">English (Neural Standard)</option>
                            <option value="ur">اردو (Urdu)</option>
                          </select>
                        </div>
                        <div className="space-y-2">
                          <label className="text-xs uppercase text-muted-foreground font-bold ml-1">{t('settings.temporalZone')}</label>
                          <select
                            value={preferences.timezone}
                            onChange={(e) => setPreferences({ ...preferences, timezone: e.target.value })}
                            className="w-full bg-background/50 border border-cyan-500/20 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-cyan-500 transition-all font-medium"
                          >
                            <option value="UTC">Universal Temporal (UTC)</option>
                            <option value="EST">Eastern (EST)</option>
                            <option value="PST">Pacific (PST)</option>
                            <option value="GMT">Greenwich (GMT)</option>
                            <option value="CST">Central (CST)</option>
                            <option value="JST">Japan (JST)</option>
                          </select>
                        </div>
                      </div>
                    </section>

                    <div className="h-px bg-cyan-500/10" />

                    {/* Task Defaults */}
                    <section className="space-y-4">
                      <h3 className="text-sm font-bold text-fuchsia-400 uppercase tracking-[0.2em] flex items-center gap-2">
                        <Clock className="w-4 h-4" /> {t('settings.taskLogicDefaults')}
                      </h3>
                      <div className="space-y-2">
                        <label className="text-xs uppercase text-muted-foreground font-bold ml-1">{t('settings.defaultPriority')}</label>
                        <div className="flex flex-wrap gap-2">
                          {['none', 'low', 'medium', 'high'].map((p) => (
                            <button
                              key={p}
                              onClick={() => setPreferences({ ...preferences, default_priority: p })}
                              className={`px-4 py-2 rounded-lg text-xs font-bold uppercase tracking-widest transition-all border-2 ${
                                preferences.default_priority === p
                                  ? 'bg-fuchsia-500/20 border-fuchsia-500 text-fuchsia-400 shadow-[0_0_15px_rgba(217,70,239,0.2)]'
                                  : 'bg-card/30 border-fuchsia-500/20 text-muted-foreground opacity-50 hover:opacity-100'
                              }`}
                            >
                              {p}
                            </button>
                          ))}
                        </div>
                      </div>
                    </section>
                  </div>
                )}

                {/* APPEARANCE TAB */}
                {activeTab === 'appearance' && (
                  <div className="space-y-8 animate-in fade-in slide-in-from-right-5 duration-300">
                    <div className="text-xs text-cyan-400 mb-2">✅ Active Tab: APPEARANCE</div>
                    <section className="space-y-4">
                      <h3 className="text-sm font-bold text-cyan-400 uppercase tracking-[0.2em] flex items-center gap-2">
                        <Palette className="w-4 h-4" /> {t('settings.visualInterface')}
                      </h3>
                      <div className="space-y-4">
                        <div className="space-y-2">
                          <label className="text-xs uppercase text-muted-foreground font-bold ml-1">{t('settings.displayTheme')}</label>
                          <div className="grid grid-cols-2 gap-3">
                            {[
                              { value: 'light', icon: <Sun className="w-4 h-4" />, label: t('settings.themeLight') },
                              { value: 'dark', icon: <Moon className="w-4 h-4" />, label: t('settings.themeDark') },
                            ].map((theme) => (
                              <button
                                key={theme.value}
                                type="button"
                                onClick={(e) => {
                                  e.preventDefault();
                                  console.log(`🎨 Theme clicked: ${theme.value}`);
                                  console.log(`   Current theme: ${preferences.theme}`);
                                  setPreferences({ ...preferences, theme: theme.value });
                                  console.log(`   New theme: ${theme.value}`);
                                }}
                                style={{ cursor: 'pointer', zIndex: 10, position: 'relative' }}
                                className={`flex flex-col items-center gap-2 p-4 rounded-xl border-2 transition-all ${
                                  preferences.theme === theme.value
                                    ? 'bg-cyan-500/20 border-cyan-500 text-cyan-400 shadow-[0_0_15px_rgba(34,211,238,0.3)]'
                                    : 'bg-card/30 border-cyan-500/10 text-muted-foreground hover:border-cyan-500/30 hover:bg-card/50'
                                }`}
                              >
                                {theme.icon}
                                <span className="text-xs font-bold uppercase">{theme.label}</span>
                                {preferences.theme === theme.value && (
                                  <div className="absolute -top-1 -right-1 w-3 h-3 bg-cyan-400 rounded-full animate-pulse" />
                                )}
                              </button>
                            ))}
                          </div>
                        </div>

                        <div className="p-4 rounded-xl bg-background/30 border border-cyan-500/10">
                          <p className="text-xs text-muted-foreground">
                            {t('settings.neuralTip')}
                          </p>
                        </div>
                      </div>
                    </section>
                  </div>
                )}

                {/* NOTIFICATIONS TAB */}
                {activeTab === 'notifications' && (
                  <div className="space-y-8 animate-in fade-in slide-in-from-right-5 duration-300">
                    <div className="text-xs text-cyan-400 mb-2">✅ Active Tab: NOTIFICATIONS</div>
                    <section className="space-y-4">
                      <h3 className="text-sm font-bold text-cyan-400 uppercase tracking-[0.2em] flex items-center gap-2">
                        <Bell className="w-4 h-4" /> {t('settings.alertProtocols')}
                      </h3>
                      <div className="space-y-3">
                        <label className="flex items-center justify-between p-4 rounded-xl bg-background/30 border border-cyan-500/5 cursor-pointer hover:bg-card/40 transition-all group">
                          <div className="flex items-center gap-3">
                            <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/20 group-hover:bg-cyan-500/20 transition-all">
                              <Bell className="w-4 h-4 text-cyan-400" />
                            </div>
                            <div>
                              <p className="text-sm font-bold">{t('settings.emailNotifications')}</p>
                              <p className="text-xs text-muted-foreground">{t('settings.emailNotificationsDesc')}</p>
                            </div>
                          </div>
                          <input
                            type="checkbox"
                            checked={preferences.email_notifications}
                            onChange={(e) => setPreferences({ ...preferences, email_notifications: e.target.checked })}
                            className="w-5 h-5 rounded border-cyan-500/30 bg-background text-cyan-500 focus:ring-cyan-500 focus:ring-2"
                          />
                        </label>

                        <label className="flex items-center justify-between p-4 rounded-xl bg-background/30 border border-cyan-500/5 cursor-pointer hover:bg-card/40 transition-all group">
                          <div className="flex items-center gap-3">
                            <div className="p-2 rounded-lg bg-fuchsia-500/10 border border-fuchsia-500/20 group-hover:bg-fuchsia-500/20 transition-all">
                              <Bell className="w-4 h-4 text-fuchsia-400" />
                            </div>
                            <div>
                              <p className="text-sm font-bold">{t('settings.pushNotifications')}</p>
                              <p className="text-xs text-muted-foreground">{t('settings.pushNotificationsDesc')}</p>
                            </div>
                          </div>
                          <input
                            type="checkbox"
                            checked={preferences.push_notifications}
                            onChange={(e) => setPreferences({ ...preferences, push_notifications: e.target.checked })}
                            className="w-5 h-5 rounded border-cyan-500/30 bg-background text-cyan-500 focus:ring-cyan-500 focus:ring-2"
                          />
                        </label>

                        <div className="p-4 rounded-xl bg-background/30 border border-cyan-500/10 mt-4">
                          <p className="text-xs text-muted-foreground">
                            {t('settings.privacyNotice')}
                          </p>
                        </div>
                      </div>
                    </section>
                  </div>
                )}

                {/* SECURITY TAB */}
                {activeTab === 'security' && (
                  <div className="space-y-8 animate-in fade-in slide-in-from-right-5 duration-300">
                    <div className="text-xs text-cyan-400 mb-2">✅ Active Tab: SECURITY</div>
                    <section className="space-y-4">
                      <h3 className="text-sm font-bold text-cyan-400 uppercase tracking-[0.2em] flex items-center gap-2">
                        <Shield className="w-4 h-4" /> {t('settings.securityProtocols')}
                      </h3>

                      <div className="space-y-3">
                        {/* Change Password */}
                        <div className="p-4 rounded-xl bg-background/30 border border-cyan-500/10 hover:border-cyan-500/30 transition-all cursor-pointer group">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/20 group-hover:bg-cyan-500/20 transition-all">
                                <Lock className="w-4 h-4 text-cyan-400" />
                              </div>
                              <div>
                                <p className="text-sm font-bold">{t('settings.changePassword')}</p>
                                <p className="text-xs text-muted-foreground">{t('settings.changePasswordDesc')}</p>
                              </div>
                            </div>
                            <button
                              onClick={() => setShowPasswordModal(true)}
                              className="px-4 py-2 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-bold uppercase hover:bg-cyan-500/20 transition-all"
                            >
                              Update
                            </button>
                          </div>
                        </div>

                        {/* Two-Factor Authentication */}
                        <div className="p-4 rounded-xl bg-background/30 border border-cyan-500/10 hover:border-fuchsia-500/30 transition-all cursor-pointer group">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              <div className="p-2 rounded-lg bg-fuchsia-500/10 border border-fuchsia-500/20 group-hover:bg-fuchsia-500/20 transition-all">
                                <Key className="w-4 h-4 text-fuchsia-400" />
                              </div>
                              <div>
                                <p className="text-sm font-bold">{t('settings.twoFactor')}</p>
                                <p className="text-xs text-muted-foreground">{t('settings.twoFactorDesc')}</p>
                              </div>
                            </div>
                            <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase ${
                              twoFactorEnabled
                                ? 'bg-green-500/10 border border-green-500/30 text-green-400'
                                : 'bg-red-500/10 border border-red-500/30 text-red-400'
                            }`}>
                              {twoFactorEnabled ? t('common.enabled') : t('common.disabled')}
                            </span>
                          </div>
                        </div>

                        {/* Active Sessions */}
                        <div className="p-4 rounded-xl bg-background/30 border border-cyan-500/10 hover:border-cyan-500/30 transition-all cursor-pointer group">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/20 group-hover:bg-cyan-500/20 transition-all">
                                <Eye className="w-4 h-4 text-cyan-400" />
                              </div>
                              <div>
                                <p className="text-sm font-bold">{t('settings.activeSessions')}</p>
                                <p className="text-xs text-muted-foreground">{t('settings.activeSessionsDesc')}</p>
                              </div>
                            </div>
                            <button
                              onClick={handleViewSessions}
                              className="px-4 py-2 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-bold uppercase hover:bg-cyan-500/20 transition-all"
                            >
                              View
                            </button>
                          </div>
                        </div>

                        <div className="p-4 rounded-xl bg-green-500/10 border border-green-500/30 mt-4">
                          <p className="text-xs text-green-400">
                            {t('settings.securityStatus')}
                          </p>
                        </div>
                      </div>
                    </section>
                  </div>
                )}

                {/* PASSWORD CHANGE MODAL */}
                {showPasswordModal && (
                  <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div className="bg-background border border-cyan-500/30 rounded-xl p-6 w-full max-w-md mx-4 shadow-[0_0_30px_rgba(0,217,255,0.2)]">
                      <h3 className="text-lg font-bold text-cyan-400 mb-4 flex items-center gap-2">
                        <Lock className="w-5 h-5" /> {t('settings.changePassword')}
                      </h3>
                      <div className="space-y-4">
                        <div>
                          <label className="text-xs text-muted-foreground uppercase tracking-wider">{t('settings.currentPassword')}</label>
                          <input
                            type="password"
                            value={currentPassword}
                            onChange={(e) => setCurrentPassword(e.target.value)}
                            className="w-full mt-1 px-4 py-2 rounded-lg bg-background/50 border border-cyan-500/20 text-sm focus:border-cyan-500/50 focus:outline-none"
                            placeholder={t('settings.currentPasswordPlaceholder')}
                          />
                        </div>
                        <div>
                          <label className="text-xs text-muted-foreground uppercase tracking-wider">{t('settings.newPassword')}</label>
                          <input
                            type="password"
                            value={newPassword}
                            onChange={(e) => setNewPassword(e.target.value)}
                            className="w-full mt-1 px-4 py-2 rounded-lg bg-background/50 border border-cyan-500/20 text-sm focus:border-cyan-500/50 focus:outline-none"
                            placeholder={t('settings.newPasswordPlaceholder')}
                          />
                        </div>
                        <div>
                          <label className="text-xs text-muted-foreground uppercase tracking-wider">{t('settings.confirmNewPassword')}</label>
                          <input
                            type="password"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            className="w-full mt-1 px-4 py-2 rounded-lg bg-background/50 border border-cyan-500/20 text-sm focus:border-cyan-500/50 focus:outline-none"
                            placeholder={t('settings.confirmNewPasswordPlaceholder')}
                          />
                        </div>
                        <div className="flex gap-3 mt-6">
                          <button
                            onClick={() => {
                              setShowPasswordModal(false);
                              setCurrentPassword('');
                              setNewPassword('');
                              setConfirmPassword('');
                            }}
                            className="flex-1 px-4 py-2 rounded-lg border border-cyan-500/30 text-cyan-400 text-sm font-bold hover:bg-cyan-500/10 transition-all"
                          >
                            Cancel
                          </button>
                          <button
                            onClick={handleChangePassword}
                            disabled={passwordChanging}
                            className="flex-1 px-4 py-2 rounded-lg bg-cyan-500 text-black text-sm font-bold hover:bg-cyan-400 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                          >
                            {passwordChanging && <Loader2 className="w-4 h-4 animate-spin" />}
                            {passwordChanging ? t('settings.changingPassword') : t('settings.changePassword')}
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* ACTIVE SESSIONS MODAL */}
                {showSessionsModal && (
                  <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div className="bg-background border border-cyan-500/30 rounded-xl p-6 w-full max-w-md mx-4 shadow-[0_0_30px_rgba(0,217,255,0.2)]">
                      <h3 className="text-lg font-bold text-cyan-400 mb-4 flex items-center gap-2">
                        <Eye className="w-5 h-5" /> {t('settings.activeSessions')}
                      </h3>
                      {sessionsLoading ? (
                        <div className="flex justify-center py-8">
                          <Loader2 className="w-8 h-8 animate-spin text-cyan-500" />
                        </div>
                      ) : (
                        <div className="space-y-3">
                          {sessions.map((session) => (
                            <div
                              key={session.session_id}
                              className={`p-3 rounded-lg border ${session.is_current ? 'border-green-500/30 bg-green-500/10' : 'border-cyan-500/20 bg-background/50'}`}
                            >
                              <div className="flex items-center justify-between">
                                <div>
                                  <p className="text-sm font-bold">{session.device}</p>
                                  <p className="text-xs text-muted-foreground">{session.location}</p>
                                  <p className="text-xs text-muted-foreground">Last active: {new Date(session.last_active).toLocaleString()}</p>
                                </div>
                                {session.is_current && (
                                  <span className="px-2 py-1 rounded-full bg-green-500/20 text-green-400 text-xs font-bold">
                                    {t('settings.current')}
                                  </span>
                                )}
                              </div>
                            </div>
                          ))}
                          {sessions.length === 0 && (
                            <p className="text-center text-muted-foreground py-4">{t('settings.noActiveSessions')}</p>
                          )}
                        </div>
                      )}
                      <div className="flex gap-3 mt-6">
                        <button
                          onClick={() => setShowSessionsModal(false)}
                          className="flex-1 px-4 py-2 rounded-lg border border-cyan-500/30 text-cyan-400 text-sm font-bold hover:bg-cyan-500/10 transition-all"
                        >
                          Close
                        </button>
                        <button
                          onClick={handleLogoutAll}
                          className="flex-1 px-4 py-2 rounded-lg bg-red-500/20 border border-red-500/30 text-red-400 text-sm font-bold hover:bg-red-500/30 transition-all"
                        >
                          {t('settings.logoutAllOthers')}
                        </button>
                      </div>
                    </div>
                  </div>
                )}

                {/* Footer Save Button - Always Visible */}
                <div className="flex justify-end pt-4 border-t border-cyan-500/10">
                  <button
                    onClick={handleSave}
                    disabled={saving}
                    className="flex items-center space-x-2 px-8 py-3 bg-gradient-to-r from-cyan-500 to-fuchsia-500 rounded-xl text-white font-bold uppercase tracking-widest shadow-[0_0_20px_rgba(0,217,255,0.3)] hover:shadow-[0_0_30px_rgba(0,217,255,0.5)] transform hover:-translate-y-0.5 active:translate-y-0 transition-all disabled:opacity-50 disabled:pointer-events-none"
                  >
                    {saving ? (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    ) : (
                      <Save className="w-5 h-5" />
                    )}
                    <span>{t('settings.syncConfigurations')}</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
