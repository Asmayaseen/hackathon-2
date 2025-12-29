'use client';

/**
 * Sign In Page
 *
 * Task: 2.8
 * Spec: specs/ui/design.md
 */

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function SigninPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Temporary mock authentication - will be replaced with Better Auth
      // For now, just store a mock token
      if (email && password) {
        // Mock JWT token (for development only)
        const mockToken = 'mock-jwt-token-' + Date.now();
        const mockUserId = email.split('@')[0]; // Use email prefix as user ID

        localStorage.setItem('auth_token', mockToken);
        localStorage.setItem('user_id', mockUserId);
        localStorage.setItem('user_email', email);

        // Redirect to tasks page
        router.push('/tasks');
      } else {
        setError('Please enter email and password');
      }
    } catch (err: any) {
      setError(err.message || 'Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="glass max-w-md w-full p-8 rounded-2xl mx-4">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-primary bg-clip-text text-transparent mb-2">
            Evolution Todo
          </h1>
          <p className="text-slate-400 text-sm">Sign in to your account</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="email" className="block text-sm font-medium mb-2 text-slate-300">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 rounded-lg bg-slate-800/50 border border-slate-700 text-white placeholder-slate-500 focus:border-purple-primary focus:ring-2 focus:ring-purple-primary/20 focus:outline-none transition-all"
              placeholder="you@example.com"
              required
              disabled={loading}
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium mb-2 text-slate-300">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 rounded-lg bg-slate-800/50 border border-slate-700 text-white placeholder-slate-500 focus:border-purple-primary focus:ring-2 focus:ring-purple-primary/20 focus:outline-none transition-all"
              placeholder="••••••••"
              required
              disabled={loading}
            />
          </div>

          {error && (
            <div className="text-red-400 text-sm bg-red-500/10 border border-red-500/20 rounded-lg p-3">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-lg bg-gradient-primary text-white font-semibold hover:scale-105 active:scale-95 transition-transform disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-slate-400">
          Don't have an account?{' '}
          <Link href="/auth/signup" className="text-purple-primary hover:text-purple-400 font-medium transition-colors">
            Sign up
          </Link>
        </p>

        <div className="mt-6 text-center">
          <p className="text-xs text-slate-500">
            Demo: Use any email and password to sign in
          </p>
        </div>
      </div>
    </div>
  );
}
