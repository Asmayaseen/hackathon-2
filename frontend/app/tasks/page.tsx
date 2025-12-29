'use client';

/**
 * Tasks Page - Protected Route
 *
 * Task: 2.10
 * Spec: specs/features/task-crud.md
 */

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function TasksPage() {
  const router = useRouter();
  const [user, setUser] = useState<{ id: string; email: string; name?: string } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check authentication
    const token = localStorage.getItem('auth_token');
    const userId = localStorage.getItem('user_id');
    const userEmail = localStorage.getItem('user_email');
    const userName = localStorage.getItem('user_name');

    if (!token || !userId) {
      // Not authenticated - redirect to signin
      router.push('/auth/signin');
    } else {
      // Set user data
      setUser({
        id: userId,
        email: userEmail || '',
        name: userName || undefined,
      });
      setLoading(false);
    }
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('user_email');
    localStorage.removeItem('user_name');
    router.push('/auth/signin');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-white text-lg">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      {/* Header */}
      <header className="glass border-b border-slate-700/50 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold bg-gradient-primary bg-clip-text text-transparent">
            Evolution Todo
          </h1>
          <div className="flex items-center gap-4">
            <div className="text-sm text-slate-400">
              {user?.name || user?.email}
            </div>
            <button
              onClick={handleLogout}
              className="px-4 py-2 rounded-lg bg-slate-800/50 border border-slate-700 text-slate-300 hover:border-purple-primary hover:text-purple-primary transition-all"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8">
            <h2 className="text-3xl font-bold mb-2">My Tasks</h2>
            <p className="text-slate-400">Manage your daily tasks efficiently</p>
          </div>

          {/* Placeholder - Components will be added in Phase 3 */}
          <div className="glass p-8 rounded-2xl text-center">
            <div className="text-6xl mb-4">📝</div>
            <h3 className="text-xl font-semibold mb-2">Task Components Coming Soon</h3>
            <p className="text-slate-400 mb-6">
              The task form and task list components will be implemented in Phase 3.
            </p>
            <div className="space-y-2 text-sm text-slate-500">
              <p>✅ Authentication working</p>
              <p>✅ Protected route working</p>
              <p>✅ UI theme configured</p>
              <p>⏳ Task CRUD components - Phase 3</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
