'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Navbar from '@/components/layout/Navbar';
import { api, HistoryEntry } from '@/lib/api';
import { History, Search, Filter, Loader2, ArrowLeftRight, Edit3, Trash2, CheckCircle2, PlusCircle, Activity } from 'lucide-react';

export default function HistoryPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [userId, setUserId] = useState<string | null>(null);
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [query, setQuery] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    const storedUserId = localStorage.getItem('user_id');

    if (!token || !storedUserId) {
      router.push('/auth/signin');
      return;
    }

    setUserId(storedUserId);

    const fetchHistory = async () => {
      try {
        const data = await api.getHistory(storedUserId);
        setHistory(data.history);
      } catch (err) {
        console.error('Failed to fetch audit log:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [router]);

  const getActionIcon = (action: string) => {
    const a = action.toLowerCase();
    if (a.includes('create')) return <PlusCircle className="w-4 h-4 text-green-400" />;
    if (a.includes('update')) return <Edit3 className="w-4 h-4 text-cyan-400" />;
    if (a.includes('delete')) return <Trash2 className="w-4 h-4 text-red-400" />;
    if (a.includes('complete')) return <CheckCircle2 className="w-4 h-4 text-fuchsia-400" />;
    return <Activity className="w-4 h-4 text-slate-400" />;
  };

  const filteredHistory = Array.isArray(history) ? history.filter(item =>
    item.action.toLowerCase().includes(query.toLowerCase()) ||
    (item.task_title && item.task_title.toLowerCase().includes(query.toLowerCase()))
  ) : [];

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
              <div className="p-3 rounded-2xl bg-fuchsia-500/10 border border-fuchsia-500/30">
                <History className="w-8 h-8 text-fuchsia-400" />
              </div>
              <div>
                <h1 className="text-3xl font-bold uppercase tracking-wider bg-gradient-to-r from-fuchsia-400 to-cyan-500 bg-clip-text text-transparent">
                  Neural Logs
                </h1>
                <p className="text-muted-foreground uppercase text-xs tracking-[0.2em]">Immutable action history</p>
              </div>
            </div>

            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search Action Logs..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="pl-10 pr-4 py-2 bg-card border border-cyan-500/20 rounded-xl focus:outline-none focus:border-cyan-500 transition-all font-medium text-sm"
              />
            </div>
          </div>

          {/* Audit Log Table */}
          <div className="bg-card/50 backdrop-blur-xl border border-cyan-500/10 rounded-2xl overflow-hidden">
             <div className="p-4 border-b border-cyan-500/10 bg-cyan-500/5 flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-[0.3em] text-cyan-400">Transaction Stream</span>
                <span className="text-[10px] text-muted-foreground font-bold uppercase">{filteredHistory.length} entries detected</span>
             </div>

             <div className="divide-y divide-cyan-500/5">
                {filteredHistory.length > 0 ? (
                  filteredHistory.map((item, idx) => (
                    <div key={item.id || idx} className="p-4 hover:bg-cyan-500/5 transition-colors group">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex items-start gap-4">
                           <div className="mt-1 p-2 rounded-lg bg-background/50 border border-border group-hover:border-cyan-500/30 transition-all">
                              {getActionIcon(item.action)}
                           </div>
                           <div>
                              <div className="flex items-center gap-2">
                                <span className="font-bold text-sm uppercase tracking-wide text-foreground">
                                  {item.action}
                                </span>
                                {item.task_id && (
                                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted border border-border font-mono">
                                    NODE_{item.task_id}
                                  </span>
                                )}
                              </div>
                              <p className="text-sm text-muted-foreground mt-0.5">
                                {item.details || `Modified task structure: "${item.task_title || 'Untitled Node'}"`}
                              </p>
                           </div>
                        </div>
                        <div className="text-right flex flex-col items-end">
                          <span className="text-xs font-mono text-cyan-400/70">
                            {new Date(item.timestamp).toLocaleTimeString([], { hour12: false })}
                          </span>
                          <span className="text-[10px] text-muted-foreground font-medium uppercase tracking-tighter">
                            {new Date(item.timestamp).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="py-20 text-center">
                    <Activity className="w-12 h-12 text-muted-foreground/20 mx-auto mb-4" />
                    <p className="text-muted-foreground uppercase tracking-widest text-sm">No neural logs found in specified range</p>
                  </div>
                )}
             </div>
          </div>

          <div className="flex justify-center flex-col items-center gap-2 opacity-30">
             <div className="w-1 h-1 bg-cyan-500 rounded-full" />
             <div className="w-1 h-1 bg-cyan-500 rounded-full" />
             <div className="w-1 h-1 bg-cyan-500 rounded-full" />
             <span className="text-[10px] uppercase tracking-[0.5em] font-bold">End of Log Stream</span>
          </div>
        </div>
      </main>
    </div>
  );
}
