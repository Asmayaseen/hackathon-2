'use client';

import { useState, useEffect, useCallback } from 'react';
import { api, Task, TasksResponse } from '../lib/api';
import TaskItem from './TaskItem';

interface TaskListProps {
  userId: string;
  refreshTrigger: number;
}

type FilterStatus = 'all' | 'pending' | 'completed';

export default function TaskList({ userId, refreshTrigger }: TaskListProps) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [counts, setCounts] = useState({ total: 0, pending: 0, completed: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState<FilterStatus>('all');

  const fetchTasks = useCallback(async () => {
    setLoading(true);
    setError('');

    try {
      const response: TasksResponse = await api.getTasks(userId, filter);
      setTasks(response.tasks);
      setCounts(response.count);
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Failed to load tasks';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [userId, filter]);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks, refreshTrigger]);

  const handleTaskUpdated = () => {
    fetchTasks();
  };

  const handleTaskDeleted = () => {
    fetchTasks();
  };

  const filterButtons: { status: FilterStatus; label: string; color: string }[] = [
    { status: 'all', label: 'All', color: 'cyan' },
    { status: 'pending', label: 'Active', color: 'fuchsia' },
    { status: 'completed', label: 'Done', color: 'green' },
  ];

  return (
    <div>
      {/* Stats Bar */}
      <div className="relative bg-card/80 backdrop-blur-sm p-4 rounded-2xl mb-4 border-2 border-cyan-500/20">
        <div className="flex flex-wrap gap-4 justify-between items-center">
          <div className="flex gap-6 text-sm">
            <span className="text-muted-foreground">
              Total: <span className="text-cyan-400 font-bold">{counts.total}</span>
            </span>
            <span className="text-muted-foreground">
              Active: <span className="text-fuchsia-400 font-bold">{counts.pending}</span>
            </span>
            <span className="text-muted-foreground">
              Done: <span className="text-green-400 font-bold">{counts.completed}</span>
            </span>
          </div>

          {/* Filter Buttons */}
          <div className="flex gap-2">
            {filterButtons.map(({ status, label, color }) => (
              <button
                key={status}
                onClick={() => setFilter(status)}
                className={`px-4 py-2 rounded-xl text-sm font-medium uppercase tracking-wide transition-all ${
                  filter === status
                    ? color === 'cyan'
                      ? 'bg-gradient-to-r from-cyan-500 to-cyan-600 text-white shadow-[0_0_20px_rgba(0,217,255,0.3)]'
                      : color === 'fuchsia'
                      ? 'bg-gradient-to-r from-fuchsia-500 to-fuchsia-600 text-white shadow-[0_0_20px_rgba(217,70,239,0.3)]'
                      : 'bg-gradient-to-r from-green-500 to-green-600 text-white shadow-[0_0_20px_rgba(34,197,94,0.3)]'
                    : 'bg-background/50 border border-cyan-500/20 text-muted-foreground hover:text-foreground hover:border-cyan-400/50'
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="text-red-400 text-sm bg-red-500/10 border-2 border-red-500/30 rounded-xl p-4 mb-4 flex items-center gap-2">
          <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {error}
          <button
            onClick={fetchTasks}
            className="ml-auto text-red-300 hover:text-red-200 underline"
          >
            Retry
          </button>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="relative bg-card/80 backdrop-blur-sm p-8 rounded-2xl text-center border-2 border-cyan-500/20">
          <div className="relative w-12 h-12 mx-auto mb-4">
            <div className="absolute inset-0 bg-gradient-to-br from-cyan-400 to-fuchsia-500 rounded-xl blur-md opacity-60 animate-pulse" />
            <div className="relative w-full h-full bg-gradient-to-br from-cyan-500 to-fuchsia-500 rounded-xl flex items-center justify-center border-2 border-cyan-400/50">
              <svg className="w-6 h-6 text-white animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
            </div>
          </div>
          <p className="text-cyan-400 uppercase tracking-wider text-sm">Loading tasks...</p>
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && tasks.length === 0 && (
        <div className="relative bg-card/80 backdrop-blur-sm p-8 rounded-2xl text-center border-2 border-cyan-500/20">
          <div className="w-20 h-20 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-cyan-500/20 to-fuchsia-500/20 flex items-center justify-center">
            {filter === 'completed' ? (
              <svg className="w-10 h-10 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            ) : filter === 'pending' ? (
              <svg className="w-10 h-10 text-fuchsia-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            ) : (
              <svg className="w-10 h-10 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            )}
          </div>
          <h3 className="text-xl font-bold mb-2 text-foreground">
            {filter === 'completed'
              ? 'No completed missions'
              : filter === 'pending'
              ? 'All missions complete!'
              : 'No active missions'}
          </h3>
          <p className="text-muted-foreground">
            {filter === 'all'
              ? 'Initialize your first task above'
              : filter === 'pending'
              ? 'Outstanding work, agent!'
              : 'Complete some tasks to see them here'}
          </p>
        </div>
      )}

      {/* Task List */}
      {!loading && !error && tasks.length > 0 && (
        <div className="space-y-3 max-h-[60vh] overflow-y-auto pr-2 scrollbar-thin">
          {tasks.map((task) => (
            <TaskItem
              key={task.id}
              task={task}
              userId={userId}
              onTaskUpdated={handleTaskUpdated}
              onTaskDeleted={handleTaskDeleted}
            />
          ))}
        </div>
      )}
    </div>
  );
}
