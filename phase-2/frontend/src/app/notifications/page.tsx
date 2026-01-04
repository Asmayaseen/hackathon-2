'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Navbar from '@/components/layout/Navbar';
import { api } from '@/lib/api';
import { Bell, Check, CheckAll, Trash2, Clock, AlertTriangle, Loader2, MessageSquare, BellOff } from 'lucide-react';

export default function NotificationsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [userId, setUserId] = useState<string | null>(null);
  const [notifications, setNotifications] = useState<any[]>([]);

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
        setNotifications(Array.isArray(data) ? data : data.notifications || []);
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
        prev.map(n => n.id === id ? { ...n, read: true } : n)
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
        prev.map(n => ({ ...n, read: true }))
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

  const unreadCount = Array.isArray(notifications) ? notifications.filter(n => !n.read).length : 0;

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
                  Neural Alerts
                </h1>
                <p className="text-muted-foreground uppercase text-xs tracking-[0.2em]">Signal synchronization inbox</p>
              </div>
            </div>

            {unreadCount > 0 && (
              <button
                onClick={handleMarkAllRead}
                className="flex items-center space-x-2 px-4 py-2 bg-cyan-500/10 border border-cyan-400/30 text-cyan-400 rounded-xl hover:bg-cyan-500/20 transition-all text-xs font-bold uppercase tracking-widest"
              >
                Clear All Signals
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
                    className={`p-6 transition-all group ${!n.read ? 'bg-cyan-500/5 border-l-4 border-l-cyan-400' : 'bg-transparent filter grayscale-[0.5] opacity-80'}`}
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex items-start gap-4">
                        <div className={`mt-1 p-3 rounded-2xl border-2 transition-all ${!n.read ? 'bg-background border-cyan-500/30 shadow-[0_0_15px_rgba(0,217,255,0.1)]' : 'bg-muted/50 border-transparent'}`}>
                          {getIcon(n.title)}
                        </div>
                        <div>
                          <div className="flex flex-wrap items-center gap-2">
                             <h3 className={`font-bold uppercase tracking-wide ${!n.read ? 'text-foreground' : 'text-muted-foreground line-through decoration-cyan-500/30'}`}>
                                {n.title}
                             </h3>
                             <span className="text-[10px] font-mono text-cyan-400/70 border border-cyan-500/20 px-1.5 py-0.5 rounded">
                                {new Date(n.created_at).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit' })}
                             </span>
                          </div>
                          <p className="text-sm text-muted-foreground mt-2 leading-relaxed">
                            {n.message}
                          </p>
                          <div className="flex items-center gap-4 mt-4 text-[10px] font-bold uppercase tracking-widest text-muted-foreground/60">
                             <span>Source: Neural Node {n.task_id || 'System'}</span>
                             <span>•</span>
                             <span>{new Date(n.created_at).toLocaleDateString()}</span>
                          </div>
                        </div>
                      </div>

                      {!n.read && (
                        <button
                          onClick={() => handleMarkRead(n.id)}
                          className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 opacity-0 group-hover:opacity-100 transition-all hover:bg-cyan-500/20"
                          title="Acknowledge Signal"
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
                 <h2 className="text-xl font-bold uppercase tracking-[0.2em] text-muted-foreground/50 mb-2">Signal Silence</h2>
                 <p className="text-sm text-muted-foreground/40 max-w-[280px] leading-relaxed">
                    No active notifications detected on the neural network at this time.
                 </p>
              </div>
            )}
          </div>

          <div className="flex justify-center p-4">
             <p className="text-[10px] uppercase tracking-widest text-muted-foreground/50 font-medium">
                System Time: {new Date().toISOString()} | Uplink Signal: 100%
             </p>
          </div>
        </div>
      </main>
    </div>
  );
}
