'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Navbar from '@/components/layout/Navbar';
import StatsCard from '@/components/StatsCard';
import ProgressBar from '@/components/ProgressBar';
import { api } from '@/lib/api';
import { LayoutDashboard, TrendingUp, AlertCircle, Calendar, ArrowUpRight, Loader2, PieChart, BarChart3 } from 'lucide-react';

export default function DashboardPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [userId, setUserId] = useState<string | null>(null);
  const [userEmail, setUserEmail] = useState<string>('');
  const [userName, setUserName] = useState<string>('');
  const [stats, setStats] = useState<any>(null);
  const [completionHistory, setCompletionHistory] = useState<any[]>([]);

  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    const storedUserId = localStorage.getItem('user_id');
    const storedUserEmail = localStorage.getItem('user_email');
    const storedUserName = localStorage.getItem('user_name');

    if (!token || !storedUserId) {
      router.push('/auth/signin');
      return;
    }

    setUserId(storedUserId);
    setUserEmail(storedUserEmail || '');
    setUserName(storedUserName || '');

    const fetchData = async () => {
      try {
        const [statsData, historyData] = await Promise.all([
          api.getStats(storedUserId),
          api.getCompletionStats(storedUserId, 7)
        ]);
        setStats(statsData);
        setCompletionHistory(historyData);
      } catch (err) {
        console.error('Failed to fetch dashboard data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [router]);

  if (loading) {
    return (
      <div className="min-h-screen bg-background text-foreground">
        <Navbar />
        <div className="flex items-center justify-center h-[calc(100vh-64px)]">
          <Loader2 className="w-8 h-8 animate-spin text-cyan-500" />
        </div>
      </div>
    );
  }

  // Fallback if API returns null/err
  const data = stats || {
    total: 0,
    pending: 0,
    completed: 0,
    overdue: 0,
    upcoming: 0,
    completion_rate: 0,
    priority_distribution: { high: 0, medium: 0, low: 0, none: 0 }
  };

  return (
    <div className="min-h-screen bg-background relative overflow-hidden text-foreground">
      <div className="absolute inset-0 cyber-grid opacity-20" />
      <Navbar />

      <main className="container mx-auto px-4 py-8 relative z-10">
        <div className="max-w-6xl mx-auto space-y-8">
          {/* Header */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold uppercase tracking-wider bg-gradient-to-r from-cyan-400 to-fuchsia-500 bg-clip-text text-transparent">
                Mission Analytics
              </h1>
              <p className="text-muted-foreground uppercase text-xs tracking-[0.2em]">Neural performance data stream</p>
            </div>
            <div className="flex flex-col sm:flex-row items-end sm:items-center gap-3">
              {/* User Profile Card */}
              <div className="flex items-center gap-3 px-4 py-2 bg-card/50 border border-cyan-500/20 rounded-xl backdrop-blur-sm">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-fuchsia-500 flex items-center justify-center text-white font-bold text-sm">
                  {userName ? userName.charAt(0).toUpperCase() : (userEmail ? userEmail.charAt(0).toUpperCase() : 'U')}
                </div>
                <div className="flex flex-col">
                  <span className="text-xs font-bold text-foreground">{userName || 'Agent'}</span>
                  <span className="text-[10px] text-muted-foreground">{userEmail}</span>
                </div>
              </div>
              <div className="flex items-center gap-2 px-4 py-2 bg-cyan-500/10 border border-cyan-500/20 rounded-xl">
                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                <span className="text-xs font-bold uppercase text-cyan-400 tracking-wider">Live Uplink Active</span>
              </div>
            </div>
          </div>

          {/* Top Row: Mission Overview */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatsCard label="Total Nodes" value={data.total} icon="total" color="cyan" />
            <StatsCard label="Pending Tasks" value={data.pending} icon="pending" color="fuchsia" />
            <StatsCard label="Success Rate" value={Math.round(data.completion_rate * 100) / 100 + '%'} icon="completed" color="green" />
            <div className="relative bg-card/80 backdrop-blur-sm p-6 rounded-2xl border-2 border-red-500/30 hover:shadow-[0_0_30px_rgba(239,68,68,0.2)] transition-all card-hover">
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-red-500 to-red-600 flex items-center justify-center shadow-lg">
                  <AlertCircle className="text-white w-6 h-6" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground uppercase tracking-wide">Overdue</p>
                  <p className="text-3xl font-bold text-red-500">{data.overdue || 0}</p>
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Completion Progress */}
            <div className="lg:col-span-2 bg-card/50 backdrop-blur-xl border border-cyan-500/10 rounded-2xl p-6 space-y-6">
              <div className="flex justify-between items-center">
                <h3 className="text-sm font-bold text-cyan-400 uppercase tracking-widest flex items-center gap-2">
                  <TrendingUp className="w-4 h-4" /> Productivity Stream
                </h3>
                <span className="text-xs text-muted-foreground uppercase font-bold tracking-widest">Neural Index: Stable</span>
              </div>

              <div className="space-y-2">
                <div className="flex justify-between text-sm font-bold mb-2">
                   <span className="uppercase tracking-widest">Global Completion Status</span>
                   <span className="text-cyan-400">{Math.round((data.completed / (data.total || 1)) * 100)}%</span>
                </div>
                <ProgressBar completed={data.completed} total={data.total} />
              </div>

              {/* Visual History (Mock Chart via CSS) */}
              <div className="pt-4">
                <div className="h-48 flex items-end justify-between gap-2 px-2">
                  {(completionHistory.length > 0 ? completionHistory : [10, 30, 45, 25, 60, 80, 75]).map((val: any, i) => {
                    const count = typeof val === 'number' ? val : (val.completed || 0);
                    const height = Math.max(10, Math.min(100, (count / (data.total || 10)) * 100));
                    return (
                      <div key={i} className="flex-1 group relative">
                        <div
                          className="w-full bg-gradient-to-t from-cyan-500/50 to-cyan-400 rounded-t-lg transition-all duration-500 group-hover:from-fuchsia-500/50 group-hover:to-fuchsia-400"
                          style={{ height: `${height}%` }}
                        />
                        <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-popover border border-cyan-500/30 px-2 py-1 rounded text-[10px] font-bold opacity-0 group-hover:opacity-100 transition-opacity">
                          {count}
                        </div>
                      </div>
                    );
                  })}
                </div>
                <div className="flex justify-between mt-4 px-2 text-[10px] uppercase font-bold text-muted-foreground tracking-tighter">
                  <span>-7 Days</span>
                  <span>-6D</span>
                  <span>-5D</span>
                  <span>-4D</span>
                  <span>-3D</span>
                  <span>-2D</span>
                  <span>Today</span>
                </div>
              </div>
            </div>

            {/* Priority Matrix */}
            <div className="bg-card/50 backdrop-blur-xl border border-cyan-500/10 rounded-2xl p-6 space-y-6">
              <h3 className="text-sm font-bold text-fuchsia-400 uppercase tracking-widest flex items-center gap-2">
                <PieChart className="w-4 h-4" /> Priority Matrix
              </h3>

              <div className="space-y-4">
                {[
                  { label: 'Critical', key: 'high', color: 'bg-red-500', text: 'text-red-400' },
                  { label: 'Standard', key: 'medium', color: 'bg-yellow-500', text: 'text-yellow-400' },
                  { label: 'Low Trace', key: 'low', color: 'bg-green-500', text: 'text-green-400' },
                  { label: 'Default', key: 'none', color: 'bg-slate-500', text: 'text-slate-400' },
                ].map((p) => {
                  const count = data.priority_distribution?.[p.key] || 0;
                  const percent = Math.round((count / (data.total || 1)) * 100);
                  return (
                    <div key={p.key} className="space-y-1">
                      <div className="flex justify-between text-[10px] font-bold uppercase tracking-widest">
                        <span>{p.label}</span>
                        <span className={p.text}>{count} nodes ({percent}%)</span>
                      </div>
                      <div className="h-1.5 w-full bg-slate-900 rounded-full overflow-hidden border border-white/5">
                        <div
                          className={`h-full ${p.color} transition-all duration-1000`}
                          style={{ width: `${percent}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>

              <div className="mt-8 p-4 bg-background/50 rounded-xl border border-fuchsia-500/10">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-fuchsia-500/10 rounded-lg">
                    <Calendar className="w-4 h-4 text-fuchsia-400" />
                  </div>
                  <div>
                    <p className="text-[10px] uppercase text-muted-foreground font-bold tracking-widest">Upcoming Actions</p>
                    <p className="text-lg font-bold text-foreground">{data.upcoming || 0} scheduled</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Action Center Footer */}
          <div className="flex justify-center pt-4">
            <button
               onClick={() => router.push('/tasks')}
               className="group flex items-center gap-2 px-8 py-3 bg-card/50 border-2 border-cyan-500/30 rounded-2xl text-cyan-400 font-bold uppercase tracking-[0.2em] hover:bg-cyan-500/10 hover:border-cyan-400 transition-all shadow-[0_0_20px_rgba(0,217,255,0.1)]"
            >
              Back to Neural Deck
              <ArrowUpRight className="w-5 h-5 group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
