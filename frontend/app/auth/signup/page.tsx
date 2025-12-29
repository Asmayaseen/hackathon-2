'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { api } from '@/lib/api';
import ThemeToggle from '@/components/ThemeToggle';

export default function SignupPage() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    setLoading(true);

    try {
      const response = await api.signup(name, email, password);

      localStorage.setItem('auth_token', response.token);
      localStorage.setItem('user_id', response.user.id);
      localStorage.setItem('user_email', response.user.email);
      localStorage.setItem('user_name', response.user.name);

      router.push('/tasks');
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Registration failed';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background relative overflow-hidden transition-colors duration-300">
      {/* Cyber grid background */}
      <div className="absolute inset-0 cyber-grid" />

      {/* Neon glow effects */}
      <div className="absolute top-1/4 right-0 w-96 h-96 bg-fuchsia-500/20 rounded-full filter blur-[120px] animate-pulse" />
      <div className="absolute bottom-1/4 left-0 w-96 h-96 bg-cyan-500/20 rounded-full filter blur-[120px] animate-pulse [animation-delay:1s]" />

      {/* Theme Toggle - Top Right */}
      <div className="absolute top-6 right-6 z-20">
        <ThemeToggle />
      </div>

      {/* Back to Home */}
      <Link
        href="/"
        className="absolute top-6 left-6 z-20 flex items-center gap-2 text-fuchsia-400 hover:text-fuchsia-300 transition-colors"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        <span className="text-sm font-medium uppercase tracking-wider">Back</span>
      </Link>

      <div className="min-h-screen flex items-center justify-center relative z-10 px-4 py-12">
        <div className="max-w-md w-full">
          {/* Card */}
          <div className="relative">
            <div className="absolute -inset-1 bg-gradient-to-r from-fuchsia-500 to-cyan-500 rounded-3xl blur-lg opacity-50" />
            <div className="relative bg-card/90 backdrop-blur-xl p-8 rounded-2xl border-2 border-fuchsia-500/30">

              {/* Logo */}
              <div className="text-center mb-8">
                <div className="inline-flex items-center justify-center mb-4">
                  <div className="relative w-16 h-16">
                    <div className="absolute inset-0 bg-gradient-to-br from-fuchsia-400 to-cyan-500 rounded-2xl blur-md opacity-60 animate-pulse" />
                    <div className="relative w-full h-full bg-gradient-to-br from-fuchsia-500 to-cyan-500 rounded-2xl flex items-center justify-center border-2 border-fuchsia-400/50 shadow-[0_0_30px_rgba(217,70,239,0.4)]">
                      <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                      </svg>
                    </div>
                  </div>
                </div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-fuchsia-400 to-cyan-400 bg-clip-text text-transparent mb-2">
                  JOIN THE NETWORK
                </h1>
                <p className="text-muted-foreground text-sm uppercase tracking-wider">Initialize New Account</p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-5">
                <div>
                  <label htmlFor="name" className="block text-sm font-medium mb-2 text-fuchsia-400 uppercase tracking-wide">
                    Display Name
                  </label>
                  <input
                    id="name"
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full px-4 py-3 rounded-xl bg-background/50 border-2 border-fuchsia-500/30 text-foreground placeholder-muted-foreground focus:border-fuchsia-400 focus:shadow-[0_0_20px_rgba(217,70,239,0.3)] focus:outline-none transition-all input-cyber"
                    placeholder="Your name"
                    required
                    disabled={loading}
                  />
                </div>

                <div>
                  <label htmlFor="email" className="block text-sm font-medium mb-2 text-fuchsia-400 uppercase tracking-wide">
                    Email Address
                  </label>
                  <input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full px-4 py-3 rounded-xl bg-background/50 border-2 border-fuchsia-500/30 text-foreground placeholder-muted-foreground focus:border-fuchsia-400 focus:shadow-[0_0_20px_rgba(217,70,239,0.3)] focus:outline-none transition-all input-cyber"
                    placeholder="you@example.com"
                    required
                    disabled={loading}
                  />
                </div>

                <div>
                  <label htmlFor="password" className="block text-sm font-medium mb-2 text-fuchsia-400 uppercase tracking-wide">
                    Password
                  </label>
                  <input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full px-4 py-3 rounded-xl bg-background/50 border-2 border-fuchsia-500/30 text-foreground placeholder-muted-foreground focus:border-fuchsia-400 focus:shadow-[0_0_20px_rgba(217,70,239,0.3)] focus:outline-none transition-all input-cyber"
                    placeholder="Min 8 characters"
                    required
                    minLength={8}
                    disabled={loading}
                  />
                </div>

                <div>
                  <label htmlFor="confirmPassword" className="block text-sm font-medium mb-2 text-fuchsia-400 uppercase tracking-wide">
                    Confirm Password
                  </label>
                  <input
                    id="confirmPassword"
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="w-full px-4 py-3 rounded-xl bg-background/50 border-2 border-fuchsia-500/30 text-foreground placeholder-muted-foreground focus:border-fuchsia-400 focus:shadow-[0_0_20px_rgba(217,70,239,0.3)] focus:outline-none transition-all input-cyber"
                    placeholder="Repeat password"
                    required
                    minLength={8}
                    disabled={loading}
                  />
                </div>

                {error && (
                  <div className="text-red-400 text-sm bg-red-500/10 border-2 border-red-500/30 rounded-xl p-3 flex items-center gap-2">
                    <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {error}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={loading}
                  className="relative w-full group"
                >
                  <div className="absolute -inset-0.5 bg-gradient-to-r from-fuchsia-500 to-cyan-500 rounded-xl blur opacity-75 group-hover:opacity-100 transition duration-300" />
                  <div className="relative w-full py-3 bg-gradient-to-r from-fuchsia-500 to-cyan-500 rounded-xl text-white font-bold uppercase tracking-wider border border-fuchsia-400/30 shadow-[0_0_30px_rgba(217,70,239,0.4)] hover:shadow-[0_0_40px_rgba(217,70,239,0.6)] transition-all disabled:opacity-50 disabled:cursor-not-allowed">
                    {loading ? (
                      <span className="flex items-center justify-center gap-2">
                        <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                        </svg>
                        Initializing...
                      </span>
                    ) : (
                      <span className="flex items-center justify-center gap-2">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                        Initialize Account
                      </span>
                    )}
                  </div>
                </button>
              </form>

              <div className="mt-6 text-center">
                <p className="text-sm text-muted-foreground">
                  Already in the network?{' '}
                  <Link href="/auth/signin" className="text-cyan-400 hover:text-cyan-300 font-medium transition-colors">
                    Access System
                  </Link>
                </p>
              </div>

            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
