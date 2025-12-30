'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import TaskForm from '@/components/TaskForm';
import TaskList from '@/components/TaskList';
import StatsCard from '@/components/StatsCard';
import ProgressBar from '@/components/ProgressBar';
import ThemeToggle from '@/components/ThemeToggle';
import { api, TasksResponse } from '@/lib/api';

export default function TasksPage() {
  const router = useRouter();
  const [user, setUser] = useState<{ id: string; email: string; name?: string } | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [stats, setStats] = useState({ total: 0, pending: 0, completed: 0 });

  const fetchStats = useCallback(async (userId: string) => {
    try {
      const response: TasksResponse = await api.getTasks(userId, 'all');
      setStats(response.count);
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  }, []);

  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    const userId = localStorage.getItem('user_id');
    const userEmail = localStorage.getItem('user_email');
    const userName = localStorage.getItem('user_name');

    if (!token || !userId) {
      router.push('/auth/signin');
    } else {
      setUser({
        id: userId,
        email: userEmail || '',
        name: userName || undefined,
      });
      setLoading(false);
      fetchStats(userId);
    }
  }, [router, fetchStats]);

  useEffect(() => {
    if (user?.id && refreshTrigger > 0) {
      fetchStats(user.id);
    }
  }, [refreshTrigger, user?.id, fetchStats]);

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('user_email');
    localStorage.removeItem('user_name');
    router.push('/auth/signin');
  };

  const handleTaskAdded = () => {
    setRefreshTrigger((prev) => prev + 1);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="relative w-16 h-16 mx-auto mb-4">
            <div className="absolute inset-0 bg-gradient-to-br from-cyan-400 to-fuchsia-500 rounded-2xl blur-md opacity-60 animate-pulse" />
            <div className="relative w-full h-full bg-gradient-to-br from-cyan-500 to-fuchsia-500 rounded-2xl flex items-center justify-center border-2 border-cyan-400/50">
              <svg className="w-8 h-8 text-white animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
            </div>
          </div>
          <p className="text-cyan-400 uppercase tracking-wider text-sm">Initializing Neural Interface...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background relative overflow-hidden transition-colors duration-300">
      {/* Cyber grid background */}
      <div className="absolute inset-0 cyber-grid" />

      {/* Neon glow effects */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-500/10 rounded-full filter blur-[150px]" />
      <div className="absolute bottom-0 left-0 w-96 h-96 bg-fuchsia-500/10 rounded-full filter blur-[150px]" />

      {/* Header */}
      <header className="sticky top-0 z-50 bg-card/80 backdrop-blur-xl border-b-2 border-cyan-500/20">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <Link href="/" className="flex items-center space-x-3 group">
            <div className="relative w-10 h-10">
              <div className="absolute inset-0 bg-gradient-to-br from-cyan-400 to-fuchsia-500 rounded-xl blur-md opacity-60 group-hover:opacity-100 transition-opacity" />
              <div className="relative w-full h-full bg-gradient-to-br from-cyan-500 to-fuchsia-500 rounded-xl flex items-center justify-center border-2 border-cyan-400/50">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-fuchsia-400 bg-clip-text text-transparent tracking-wider">
              NEURAL TASKS
            </span>
          </Link>

          <div className="flex items-center gap-4">
            <ThemeToggle />
            <div className="hidden sm:flex items-center gap-2 px-4 py-2 bg-card/50 rounded-xl border border-cyan-500/20">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              <span className="text-sm text-muted-foreground">
                {user?.name || user?.email}
              </span>
            </div>
            <button
              onClick={handleLogout}
              className="px-4 py-2 rounded-xl bg-card/50 border-2 border-red-500/30 text-red-400 hover:border-red-400 hover:shadow-[0_0_20px_rgba(239,68,68,0.3)] transition-all uppercase text-sm font-medium tracking-wide"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 relative z-10">
        <div className="max-w-4xl mx-auto">
          {/* Dashboard Header */}
          <div className="mb-8 text-center sm:text-left">
            <h2 className="text-4xl font-bold mb-2">
              <span className="text-foreground">Mission</span>{' '}
              <span className="bg-gradient-to-r from-cyan-400 to-fuchsia-500 bg-clip-text text-transparent">Control</span>
            </h2>
            <p className="text-muted-foreground">Neural task management interface active</p>
          </div>

          {/* Stats Section */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
            <StatsCard
              label="Total Tasks"
              value={stats.total}
              icon="total"
              color="cyan"
            />
            <StatsCard
              label="Pending"
              value={stats.pending}
              icon="pending"
              color="fuchsia"
            />
            <StatsCard
              label="Completed"
              value={stats.completed}
              icon="completed"
              color="green"
            />
          </div>

          {/* Progress Bar */}
          <div className="mb-6">
            <ProgressBar completed={stats.completed} total={stats.total} />
          </div>

          {/* Task Form */}
          {user && (
            <TaskForm userId={user.id} onTaskAdded={handleTaskAdded} />
          )}

          {/* Task List */}
          {user && (
            <TaskList userId={user.id} refreshTrigger={refreshTrigger} />
          )}
        </div>
      </main>
    </div>
  );
}
