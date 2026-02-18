'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Navbar from '@/components/layout/Navbar';
import { api, Notification } from '@/lib/api';
import { useTranslation } from '@/lib/i18n';
import { Bell, Check, CheckCheck, Trash2, Clock, AlertTriangle, Loader2, MessageSquare, BellOff } from 'lucide-react';

export default function NotificationsPage() {
  const router = useRouter();
  const { t } = useTranslation();
  const [loading, setLoading] = useState(true);
  const [userId, setUserId] = useState<string | null>(null);
  const [notifications, setNotifications] = useState<Notification[]>([]);

  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    const storedUserId = localStorage.getItem('user_id');

    if (!token || !storedUserId) {
      router.push('/auth/signin');
      return;
    }

    setUserId(storedUserId);

    const fetchNotifications = async () => {
      try {
        const data = await api.getNotifications(storedUserId);
        setNotifications(data.notifications);
      } catch (err) {
        console.error('Failed to fetch notifications:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchNotifications();
  }, [router]);

  const handleMarkRead = async (id: number) => {
    if (!userId) return;
    try {
      await api.markNotificationRead(userId, id);
      setNotifications(prev =>
        prev.map(n => n.id === id ? { ...n, sent: true } : n)
      );
    } catch (err) {
      console.error('Failed to mark read:', err);
    }
  };

  const handleMarkAllRead = async () => {
    if (!userId) return;
    try {
      await api.markAllNotificationsRead(userId);
      setNotifications(prev =>
        prev.map(n => ({ ...n, sent: true }))
      );
    } catch (err) {
      console.error('Failed to mark all read:', err);
    }
  };

  const getIcon = (type: string) => {
    if (type?.toLowerCase().includes('overdue')) return <AlertTriangle className="w-5 h-5 text-red-400" />;
    if (type?.toLowerCase().includes('reminder')) return <Clock className="w-5 h-5 text-cyan-400" />;
    return <MessageSquare className="w-5 h-5 text-fuchsia-400" />;
  };

  const formatNotificationType = (type: string) => {
    return type
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const generateMessage = (notification: Notification) => {
    const type = notification.notification_type.toLowerCase();
    if (type.includes('reminder')) {
      return `${t('notifications.taskReminder')} ${new Date(notification.scheduled_time).toLocaleString()}`;
    }
    if (type.includes('overdue')) {
      return t('notifications.taskOverdue');
    }
    return `${t('notifications.notificationForTask')} ${notification.task_id}`;
  };

  const unreadCount = Array.isArray(notifications) ? notifications.filter(n => !n.sent).length : 0;

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

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      <div className="absolute inset-0 cyber-grid opacity-20" />
      <Navbar />

      <main className="container mx-auto px-4 py-8 relative z-10">
        <div className="max-w-4xl mx-auto space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center space-x-4">
              <div className="relative">
                <div className="p-3 rounded-2xl bg-cyan-500/10 border border-cyan-500/30">
                  <Bell className="w-8 h-8 text-cyan-400" />
                </div>
                {unreadCount > 0 && (
                  <span className="absolute -top-1 -right-1 w-5 h-5 bg-fuchsia-500 rounded-full flex items-center justify-center text-[10px] font-bold text-white border-2 border-background animate-pulse">
                    {unreadCount}
                  </span>
                )}
              </div>
              <div>
                <h1 className="text-3xl font-bold uppercase tracking-wider bg-gradient-to-r from-cyan-400 to-fuchsia-500 bg-clip-text text-transparent">
                  {t('notifications.neuralAlerts')}
                </h1>
                <p className="text-muted-foreground uppercase text-xs tracking-[0.2em]">{t('notifications.signalSync')}</p>
              </div>
            </div>

            {unreadCount > 0 && (
              <button
                onClick={handleMarkAllRead}
                className="flex items-center space-x-2 px-4 py-2 bg-cyan-500/10 border border-cyan-400/30 text-cyan-400 rounded-xl hover:bg-cyan-500/20 transition-all text-xs font-bold uppercase tracking-widest"
              >
                {t('notifications.clearAllSignals')}
              </button>
            )}
          </div>

          {/* Notifications List */}
          <div className="bg-card/50 backdrop-blur-xl border border-cyan-500/10 rounded-2xl overflow-hidden min-h-[400px]">
            {notifications.length > 0 ? (
              <div className="divide-y divide-cyan-500/5">
                {notifications.map((n) => (
                  <div
                    key={n.id}
                    className={`p-6 transition-all group ${!n.sent ? 'bg-cyan-500/5 border-l-4 border-l-cyan-400' : 'bg-transparent filter grayscale-[0.5] opacity-80'}`}
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex items-start gap-4">
                        <div className={`mt-1 p-3 rounded-2xl border-2 transition-all ${!n.sent ? 'bg-background border-cyan-500/30 shadow-[0_0_15px_rgba(0,217,255,0.1)]' : 'bg-muted/50 border-transparent'}`}>
                          {getIcon(n.notification_type)}
                        </div>
                        <div>
                          <div className="flex flex-wrap items-center gap-2">
                             <h3 className={`font-bold uppercase tracking-wide ${!n.sent ? 'text-foreground' : 'text-muted-foreground line-through decoration-cyan-500/30'}`}>
                                {formatNotificationType(n.notification_type)}
                             </h3>
                             <span className="text-[10px] font-mono text-cyan-400/70 border border-cyan-500/20 px-1.5 py-0.5 rounded">
                                {new Date(n.created_at).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit' })}
                             </span>
                          </div>
                          <p className="text-sm text-muted-foreground mt-2 leading-relaxed">
                            {generateMessage(n)}
                          </p>
                          <div className="flex items-center gap-4 mt-4 text-[10px] font-bold uppercase tracking-widest text-muted-foreground/60">
                             <span>{t('notifications.source')} {n.task_id || t('notifications.system')}</span>
                             <span>•</span>
                             <span>{new Date(n.created_at).toLocaleDateString()}</span>
                          </div>
                        </div>
                      </div>

                      {!n.sent && (
                        <button
                          onClick={() => handleMarkRead(n.id)}
                          className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 opacity-0 group-hover:opacity-100 transition-all hover:bg-cyan-500/20"
                          title={t('notifications.acknowledgeSignal')}
                        >
                          <Check className="w-5 h-5" />
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-32 text-center">
                 <div className="relative mb-6">
                    <BellOff className="w-16 h-16 text-muted-foreground/20" />
                    <div className="absolute inset-0 bg-cyan-500/5 blur-2xl rounded-full" />
                 </div>
                 <h2 className="text-xl font-bold uppercase tracking-[0.2em] text-muted-foreground/50 mb-2">{t('notifications.signalSilence')}</h2>
                 <p className="text-sm text-muted-foreground/40 max-w-[280px] leading-relaxed">
                    {t('notifications.noActiveNotifications')}
                 </p>
              </div>
            )}
          </div>

          <div className="flex justify-center p-4">
             <p className="text-[10px] uppercase tracking-widest text-muted-foreground/50 font-medium">
                {t('notifications.systemTime')} {new Date().toISOString()} | {t('notifications.uplinkSignal')}
             </p>
          </div>
        </div>
      </main>
    </div>
  );
}
