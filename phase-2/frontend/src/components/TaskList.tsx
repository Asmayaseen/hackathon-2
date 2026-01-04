'use client';

import { useState, useEffect, useCallback } from 'react';
import { api, Task, TasksResponse } from '../lib/api';
import TaskItem from './TaskItem';

interface TaskListProps {
  userId: string;
  refreshTrigger: number;
}

type FilterStatus = 'all' | 'pending' | 'completed';
type FilterPriority = 'all' | 'high' | 'medium' | 'low' | 'none';
type FilterDue = 'all' | 'today' | 'overdue' | 'week';
type SortField = 'created_at' | 'due_date' | 'priority' | 'title';
type SortOrder = 'asc' | 'desc';

export default function TaskList({ userId, refreshTrigger }: TaskListProps) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [counts, setCounts] = useState({ total: 0, pending: 0, completed: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // US2: Advanced filtering and sorting state
  const [statusFilter, setStatusFilter] = useState<FilterStatus>('all');
  const [priorityFilter, setPriorityFilter] = useState<FilterPriority>('all');
  const [dueFilter, setDueFilter] = useState<FilterDue>('all');
  const [sortField, setSortField] = useState<SortField>('created_at');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const [showAdvanced, setShowAdvanced] = useState(false);

  // US5: Search state
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);

  // US6: Bulk select state
  const [selectedTaskIds, setSelectedTaskIds] = useState<number[]>([]);
  const [isBulkLoading, setIsBulkLoading] = useState(false);

  const fetchTasks = useCallback(async () => {
    setLoading(true);
    setError('');

    try {
      let response: TasksResponse;

      if (searchQuery.trim()) {
        response = await api.searchTasks(userId, searchQuery, statusFilter);
      } else {
        response = await api.getTasks(userId, statusFilter, {
          priority: priorityFilter,
          due: dueFilter,
          sort: sortField,
          order: sortOrder,
        });
      }

      setTasks(response.tasks);
      setCounts(response.count);
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Failed to load tasks';
      setError(message);
    } finally {
      setLoading(false);
      setIsSearching(false);
    }
  }, [userId, statusFilter, priorityFilter, dueFilter, sortField, sortOrder, searchQuery]);

  useEffect(() => {
    const delayDebounceFn = setTimeout(() => {
      if (searchQuery.trim() || !isSearching) {
        fetchTasks();
      }
    }, 500);

    return () => clearTimeout(delayDebounceFn);
  }, [searchQuery, fetchTasks]);

  useEffect(() => {
    if (!searchQuery.trim()) {
      fetchTasks();
    }
  }, [fetchTasks, refreshTrigger]);

  const handleTaskUpdated = () => {
    fetchTasks();
  };

  const handleTaskDeleted = () => {
    fetchTasks();
  };

  // Bulk actions (US6)
  const toggleSelectTask = (taskId: number) => {
    setSelectedTaskIds(prev =>
      prev.includes(taskId)
        ? prev.filter(id => id !== taskId)
        : [...prev, taskId]
    );
  };

  const selectAllTasks = () => {
    if (selectedTaskIds.length === tasks.length) {
      setSelectedTaskIds([]);
    } else {
      setSelectedTaskIds(tasks.map(t => t.id));
    }
  };

  const handleBulkDelete = async () => {
    if (!selectedTaskIds.length || !confirm(`Delete ${selectedTaskIds.length} tasks?`)) return;
    setIsBulkLoading(true);
    try {
      await api.bulkDelete(userId, selectedTaskIds);
      setSelectedTaskIds([]);
      fetchTasks();
    } catch (err) {
      console.error('Bulk delete failed:', err);
    } finally {
      setIsBulkLoading(false);
    }
  };

  const handleBulkComplete = async (completed: boolean) => {
    if (!selectedTaskIds.length) return;
    setIsBulkLoading(true);
    try {
      await api.bulkToggleComplete(userId, selectedTaskIds, completed);
      setSelectedTaskIds([]);
      fetchTasks();
    } catch (err) {
      console.error('Bulk complete failed:', err);
    } finally {
      setIsBulkLoading(false);
    }
  };

  const filterButtons: { status: FilterStatus; label: string; color: string }[] = [
    { status: 'all', label: 'All', color: 'cyan' },
    { status: 'pending', label: 'Active', color: 'fuchsia' },
    { status: 'completed', label: 'Done', color: 'green' },
  ];

  const priorityOptions: { value: FilterPriority; label: string }[] = [
    { value: 'all', label: 'All Priorities' },
    { value: 'high', label: '🔴 High' },
    { value: 'medium', label: '🟡 Medium' },
    { value: 'low', label: '🟢 Low' },
    { value: 'none', label: '⚪ None' },
  ];

  const dueOptions: { value: FilterDue; label: string }[] = [
    { value: 'all', label: 'All Dates' },
    { value: 'today', label: '📅 Today' },
    { value: 'overdue', label: '⚠️ Overdue' },
    { value: 'week', label: '📆 This Week' },
  ];

  const sortOptions: { value: SortField; label: string }[] = [
    { value: 'created_at', label: 'Created' },
    { value: 'due_date', label: 'Due Date' },
    { value: 'priority', label: 'Priority' },
    { value: 'title', label: 'Title' },
  ];

  return (
    <div>
      {/* Search Bar (US5) */}
      <div className="relative mb-6">
        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
          <svg className="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => {
            setSearchQuery(e.target.value);
            setIsSearching(true);
          }}
          placeholder="Search neural task stream..."
          className="block w-full pl-12 pr-4 py-3 rounded-2xl bg-card/60 backdrop-blur-xl border-2 border-cyan-500/20 text-foreground placeholder-muted-foreground focus:border-cyan-500/50 focus:shadow-[0_0_20px_rgba(0,217,255,0.2)] focus:outline-none transition-all"
        />
        {isSearching && (
          <div className="absolute inset-y-0 right-0 pr-4 flex items-center">
            <div className="animate-spin rounded-full h-4 w-4 border-2 border-cyan-500 border-t-transparent"></div>
          </div>
        )}
      </div>

      {/* Stats Bar - Basic Filters */}
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

          <div className="flex flex-wrap gap-2">
            {/* US6: Bulk Actions */}
            {selectedTaskIds.length > 0 && (
              <div className="flex gap-2 mr-2 pr-4 border-r border-cyan-500/20">
                <button
                  onClick={() => handleBulkComplete(true)}
                  disabled={isBulkLoading}
                  className="px-3 py-2 rounded-xl text-xs font-bold uppercase tracking-wider bg-green-500/20 border border-green-500/50 text-green-400 hover:bg-green-500/30 transition-all"
                >
                  Done
                </button>
                <button
                  onClick={handleBulkDelete}
                  disabled={isBulkLoading}
                  className="px-3 py-2 rounded-xl text-xs font-bold uppercase tracking-wider bg-red-500/20 border border-red-500/50 text-red-400 hover:bg-red-500/30 transition-all"
                >
                  Delete
                </button>
              </div>
            )}

            {/* US2: Status Filter Buttons */}
            {filterButtons.map(({ status, label, color }) => (
              <button
                key={status}
                onClick={() => setStatusFilter(status)}
                className={`px-3 py-2 rounded-xl text-xs font-medium uppercase tracking-wide transition-all ${
                  statusFilter === status
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

            {/* US6: Select All */}
            <button
              onClick={selectAllTasks}
              className={`px-3 py-2 rounded-xl text-xs font-medium uppercase tracking-wide transition-all ${
                selectedTaskIds.length === tasks.length && tasks.length > 0
                  ? 'bg-cyan-500/20 border-cyan-500/50 text-cyan-400'
                  : 'bg-background/50 border border-cyan-500/20 text-muted-foreground hover:text-cyan-400'
              }`}
            >
              {selectedTaskIds.length === tasks.length && tasks.length > 0 ? 'Deselect' : 'Select All'}
            </button>

            {/* US2: Advanced Filters Toggle */}
            <button
              onClick={() => setShowAdvanced(!showAdvanced)}
              className={`px-3 py-2 rounded-xl text-xs font-medium uppercase tracking-wide transition-all ${
                showAdvanced
                  ? 'bg-purple-500/20 border-purple-500/50 text-purple-400'
                  : 'bg-background/50 border border-cyan-500/20 text-muted-foreground hover:text-cyan-400 hover:border-cyan-400'
              }`}
            >
              ⚙️ Filters
            </button>

            {/* US2: Sort Order Toggle */}
            <button
              onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
              className="px-3 py-2 rounded-xl text-xs font-medium uppercase tracking-wide bg-background/50 border border-cyan-500/20 text-muted-foreground hover:text-cyan-400"
              title={`Sort ${sortOrder === 'asc' ? 'A-Z' : 'Z-A'}`}
            >
              {sortOrder === 'asc' ? '↑' : '↓'}
            </button>
          </div>
        </div>

        {/* US2: Advanced Filters Section */}
        {showAdvanced && (
          <div className="mt-4 pt-4 border-t border-cyan-500/20 grid grid-cols-1 md:grid-cols-3 gap-3">
            {/* Priority Filter */}
            <div>
              <label className="block text-xs font-medium text-muted-foreground mb-2 uppercase tracking-wide">
                Priority
              </label>
              <select
                value={priorityFilter}
                onChange={(e) => setPriorityFilter(e.target.value as FilterPriority)}
                className="w-full px-3 py-2 rounded-lg bg-background/50 border border-cyan-500/30 text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-cyan-primary/50"
              >
                {priorityOptions.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Due Date Filter */}
            <div>
              <label className="block text-xs font-medium text-muted-foreground mb-2 uppercase tracking-wide">
                Due Date
              </label>
              <select
                value={dueFilter}
                onChange={(e) => setDueFilter(e.target.value as FilterDue)}
                className="w-full px-3 py-2 rounded-lg bg-background/50 border border-cyan-500/30 text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-cyan-primary/50"
              >
                {dueOptions.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Sort By */}
            <div>
              <label className="block text-xs font-medium text-muted-foreground mb-2 uppercase tracking-wide">
                Sort By
              </label>
              <select
                value={sortField}
                onChange={(e) => setSortField(e.target.value as SortField)}
                className="w-full px-3 py-2 rounded-lg bg-background/50 border border-cyan-500/30 text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-cyan-primary/50"
              >
                {sortOptions.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        )}
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
            {statusFilter === 'completed' ? (
              <svg className="w-10 h-10 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            ) : statusFilter === 'pending' ? (
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
            {statusFilter === 'completed'
              ? 'No completed missions'
              : statusFilter === 'pending'
              ? 'All missions complete!'
              : 'No active missions'}
          </h3>
          <p className="text-muted-foreground">
            {statusFilter === 'all'
              ? 'Initialize your first task above'
              : statusFilter === 'pending'
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
              isSelected={selectedTaskIds.includes(task.id)}
              onSelect={toggleSelectTask}
            />
          ))}
        </div>
      )}
    </div>
  );
}
