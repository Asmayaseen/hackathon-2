'use client';

import { useState } from 'react';
import { api, TaskCreate } from '../lib/api';

interface TaskFormProps {
  userId: string;
  onTaskAdded: () => void;
}

export default function TaskForm({ userId, onTaskAdded }: TaskFormProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showDescription, setShowDescription] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!title.trim()) {
      setError('Title is required');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const taskData: TaskCreate = {
        title: title.trim(),
        description: description.trim() || undefined,
      };

      await api.createTask(userId, taskData);

      setTitle('');
      setDescription('');
      setShowDescription(false);
      onTaskAdded();
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Failed to create task';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="relative bg-card/80 backdrop-blur-sm p-6 rounded-2xl mb-6 border-2 border-cyan-500/20">
      <div className="flex gap-3">
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Initialize new task..."
          className="flex-1 px-4 py-3 rounded-xl bg-background/50 border-2 border-cyan-500/30 text-foreground placeholder-muted-foreground focus:border-cyan-400 focus:shadow-[0_0_20px_rgba(0,217,255,0.3)] focus:outline-none transition-all"
          disabled={loading}
          maxLength={200}
        />
        <button
          type="button"
          onClick={() => setShowDescription(!showDescription)}
          className={`px-4 py-3 rounded-xl border-2 transition-all ${
            showDescription
              ? 'bg-fuchsia-500/20 border-fuchsia-500/50 text-fuchsia-400'
              : 'bg-background/50 border-cyan-500/30 text-muted-foreground hover:text-cyan-400 hover:border-cyan-400'
          }`}
          title="Add description"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h7" />
          </svg>
        </button>
        <button
          type="submit"
          disabled={loading || !title.trim()}
          className="relative group"
        >
          <div className="absolute -inset-0.5 bg-gradient-to-r from-cyan-500 to-fuchsia-500 rounded-xl blur opacity-75 group-hover:opacity-100 transition duration-300" />
          <div className="relative px-6 py-3 bg-gradient-to-r from-cyan-500 to-fuchsia-500 rounded-xl text-white font-bold uppercase tracking-wider border border-cyan-400/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed">
            {loading ? (
              <svg className="w-5 h-5 animate-spin" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
            ) : (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
            )}
          </div>
        </button>
      </div>

      {showDescription && (
        <div className="mt-3">
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Add mission details (optional)..."
            className="w-full px-4 py-3 rounded-xl bg-background/50 border-2 border-fuchsia-500/30 text-foreground placeholder-muted-foreground focus:border-fuchsia-400 focus:shadow-[0_0_20px_rgba(217,70,239,0.3)] focus:outline-none transition-all resize-none"
            rows={3}
            disabled={loading}
            maxLength={1000}
          />
        </div>
      )}

      {error && (
        <div className="mt-3 text-red-400 text-sm bg-red-500/10 border-2 border-red-500/30 rounded-xl p-3 flex items-center gap-2">
          <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {error}
        </div>
      )}
    </form>
  );
}
