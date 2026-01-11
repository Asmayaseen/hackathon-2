'use client';

import { useRouter } from 'next/navigation';
import { useState } from 'react';
import axios from 'axios';

export default function LoginPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [isSignup, setIsSignup] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: ''
  });
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const endpoint = isSignup ? '/api/auth/signup' : '/api/auth/signin';
      const payload = isSignup
        ? formData
        : { email: formData.email, password: formData.password };

     const response = await axios.post(endpoint, payload);


      // Store token and user info
      localStorage.setItem('token', response.data.token);
      localStorage.setItem('userId', response.data.user.id);
      localStorage.setItem('userName', response.data.user.name);
      localStorage.setItem('userEmail', response.data.user.email);

      // Redirect to chat
      router.push('/chat');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Authentication failed');
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#0a0a0f] relative">
      {/* Cyber Grid Background */}
      <div className="absolute inset-0 opacity-30" style={{
        backgroundImage: 'linear-gradient(to right, rgba(0, 217, 255, 0.06) 1px, transparent 1px), linear-gradient(to bottom, rgba(0, 217, 255, 0.06) 1px, transparent 1px)',
        backgroundSize: '50px 50px'
      }} />

      <div className="relative z-10 bg-[rgba(15,23,42,0.8)] backdrop-blur-xl border border-[rgba(0,217,255,0.2)] rounded-lg p-8 shadow-[0_0_30px_rgba(0,217,255,0.2)] max-w-md w-full mx-4">
        <h1 className="text-3xl font-bold bg-gradient-to-r from-[#00d9ff] to-[#d946ef] bg-clip-text text-transparent mb-2 text-center">
          🤖 Evolution Todo
        </h1>

        <p className="text-slate-400 text-center mb-6 text-sm">
          Phase III AI-Powered Task Management
        </p>

        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setIsSignup(false)}
            className={`flex-1 px-4 py-2 rounded-lg transition-all ${
              !isSignup
                ? 'bg-gradient-to-r from-[#00d9ff] to-[#d946ef] text-white'
                : 'bg-slate-700 text-slate-300'
            }`}
          >
            Sign In
          </button>
          <button
            onClick={() => setIsSignup(true)}
            className={`flex-1 px-4 py-2 rounded-lg transition-all ${
              isSignup
                ? 'bg-gradient-to-r from-[#00d9ff] to-[#d946ef] text-white'
                : 'bg-slate-700 text-slate-300'
            }`}
          >
            Sign Up
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {isSignup && (
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">
                Name
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required={isSignup}
                className="w-full px-4 py-2 bg-[rgba(15,23,42,0.6)] border border-[rgba(0,217,255,0.2)] rounded-lg text-slate-200 focus:outline-none focus:border-[#00d9ff] focus:shadow-[0_0_15px_rgba(0,217,255,0.3)] transition-all"
                placeholder="Your name"
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">
              Email
            </label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              required
              className="w-full px-4 py-2 bg-[rgba(15,23,42,0.6)] border border-[rgba(0,217,255,0.2)] rounded-lg text-slate-200 focus:outline-none focus:border-[#00d9ff] focus:shadow-[0_0_15px_rgba(0,217,255,0.3)] transition-all"
              placeholder="your@email.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">
              Password
            </label>
            <input
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              required
              minLength={8}
              className="w-full px-4 py-2 bg-[rgba(15,23,42,0.6)] border border-[rgba(0,217,255,0.2)] rounded-lg text-slate-200 focus:outline-none focus:border-[#00d9ff] focus:shadow-[0_0_15px_rgba(0,217,255,0.3)] transition-all"
              placeholder="••••••••"
            />
            {isSignup && (
              <p className="text-xs text-slate-500 mt-1">Minimum 8 characters</p>
            )}
          </div>

          {error && (
            <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-3 text-red-400 text-sm">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full px-6 py-3 bg-gradient-to-r from-[#00d9ff] to-[#d946ef] text-white rounded-lg hover:shadow-[0_0_20px_rgba(0,217,255,0.4)] transition-all disabled:opacity-50 font-semibold"
          >
            {loading ? 'Please wait...' : (isSignup ? 'Create Account' : 'Sign In')}
          </button>
        </form>

        <p className="text-xs text-slate-500 text-center mt-4">
          {isSignup ? 'Already have an account?' : "Don't have an account?"}{' '}
          <button
            onClick={() => setIsSignup(!isSignup)}
            className="text-[#00d9ff] hover:underline"
          >
            {isSignup ? 'Sign in' : 'Sign up'}
          </button>
        </p>
      </div>
    </div>
  );
}
