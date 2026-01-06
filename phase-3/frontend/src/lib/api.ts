/**
 * API Client for Evolution Todo Backend
 *
 * Task: 2.5
 * Spec: specs/api/rest-endpoints.md
 */
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach JWT token to all requests
apiClient.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid - redirect to login
      if (typeof window !== 'undefined') {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_id');
        localStorage.removeItem('user_email');
        localStorage.removeItem('user_name');
        window.location.href = '/auth/signin';
      }
    }
    return Promise.reject(error);
  }
);

// TypeScript Interfaces
export interface User {
  id: string;
  email: string;
  name: string;
}

export interface AuthResponse {
  token: string;
  user: User;
}

export interface Task {
  id: number;
  user_id: string;
  title: string;
  description?: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
  // Phase 2 Advanced Features (T019)
  due_date?: string;
  priority: 'high' | 'medium' | 'low' | 'none';
  tags: string[];
  recurrence_pattern?: string;
  reminder_offset?: number;
  is_recurring: boolean;
  parent_recurring_id?: number;
}

export interface TasksResponse {
  tasks: Task[];
  count: {
    total: number;
    pending: number;
    completed: number;
  };
}

export interface TaskCreate {
  title: string;
  description?: string;
  // Phase 2 Advanced Features (T019)
  due_date?: string;
  priority?: 'high' | 'medium' | 'low' | 'none';
  tags?: string[];
  recurrence_pattern?: string;
  reminder_offset?: number;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  completed?: boolean;
  // Phase 2 Advanced Features (T019)
  due_date?: string;
  priority?: 'high' | 'medium' | 'low' | 'none';
  tags?: string[];
  recurrence_pattern?: string;
  reminder_offset?: number;
}

export interface HistoryEntry {
  id: number;
  user_id: string;
  task_id?: number;
  task_title?: string;
  action: string;
  details?: string;
  timestamp: string;
}

export interface HistoryResponse {
  history: HistoryEntry[];
  count: number;
  offset: number;
  limit: number;
}

export interface Notification {
  id: number;
  user_id: string;
  task_id: number;
  scheduled_time: string;
  sent: boolean;
  notification_type: string;
  created_at: string;
  sent_at?: string;
}

export interface NotificationsResponse {
  notifications: Notification[];
  count: number;
}

// API Methods
export const api = {
  // ============ AUTH ENDPOINTS ============

  /**
   * Register a new user
   */
  async signup(name: string, email: string, password: string): Promise<AuthResponse> {
    const response = await apiClient.post('/api/auth/signup', {
      name,
      email,
      password,
    });
    return response.data;
  },

  /**
   * Sign in existing user
   */
  async signin(email: string, password: string): Promise<AuthResponse> {
    const response = await apiClient.post('/api/auth/signin', {
      email,
      password,
    });
    return response.data;
  },

  // ============ TASK ENDPOINTS ============

  /**
   * Get all tasks for a user with optional filtering and sorting (US2)
   */
  async getTasks(
    userId: string,
    status: 'all' | 'pending' | 'completed' = 'all',
    options?: {
      priority?: 'all' | 'high' | 'medium' | 'low' | 'none';
      due?: 'all' | 'today' | 'overdue' | 'week';
      sort?: 'created_at' | 'due_date' | 'priority' | 'title';
      order?: 'asc' | 'desc';
    }
  ): Promise<TasksResponse> {
    const params: any = { status };
    if (options?.priority && options.priority !== 'all') params.priority = options.priority;
    if (options?.due && options.due !== 'all') params.due = options.due;
    if (options?.sort) params.sort = options.sort;
    if (options?.order) params.order = options.order;

    const response = await apiClient.get(`/api/${userId}/tasks`, { params });
    return response.data;
  },

  /**
   * Get a single task by ID
   */
  async getTask(userId: string, taskId: number): Promise<Task> {
    const response = await apiClient.get(`/api/${userId}/tasks/${taskId}`);
    return response.data;
  },

  /**
   * Create a new task
   */
  async createTask(userId: string, data: TaskCreate): Promise<Task> {
    const response = await apiClient.post(`/api/${userId}/tasks`, data);
    return response.data;
  },

  /**
   * Update an existing task
   */
  async updateTask(
    userId: string,
    taskId: number,
    data: TaskUpdate
  ): Promise<Task> {
    const response = await apiClient.put(`/api/${userId}/tasks/${taskId}`, data);
    return response.data;
  },

  /**
   * Delete a task
   */
  async deleteTask(userId: string, taskId: number): Promise<void> {
    await apiClient.delete(`/api/${userId}/tasks/${taskId}`);
  },

  /**
   * Toggle task completion status
   */
  async toggleComplete(userId: string, taskId: number): Promise<Task> {
    const response = await apiClient.patch(
      `/api/${userId}/tasks/${taskId}/complete`
    );
    return response.data;
  },

  // ============ RECURRENCE ENDPOINTS ============ (US4)

  /**
   * Cancel upcoming occurrences of a recurring task
   */
  async cancelRecurrence(userId: string, taskId: number): Promise<void> {
    await apiClient.post(`/api/${userId}/tasks/${taskId}/recurrence/cancel`);
  },

  // ============ SEARCH ENDPOINTS ============ (US5)

  /**
   * Search tasks by title, description, or tags
   */
  async searchTasks(
    userId: string,
    query: string,
    status: 'all' | 'pending' | 'completed' = 'all'
  ): Promise<TasksResponse & { query: string }> {
    const response = await apiClient.get(`/api/${userId}/search`, {
      params: { q: query, status }
    });
    return response.data;
  },

  // ============ BULK ENDPOINTS ============ (US6)

  /**
   * Bulk operations (delete, complete, priority)
   */
  async bulkOperation(
    userId: string,
    data: {
      task_ids: number[];
      completed?: boolean;
      priority?: 'high' | 'medium' | 'low' | 'none';
      delete?: boolean;
    }
  ): Promise<{ count: number; message: string }> {
    const response = await apiClient.post(`/api/${userId}/tasks/bulk`, data);
    return response.data;
  },

  /**
   * Bulk delete tasks
   */
  async bulkDelete(userId: string, taskIds: number[]): Promise<{ count: number }> {
    return this.bulkOperation(userId, { task_ids: taskIds, delete: true });
  },

  /**
   * Bulk toggle completion status
   */
  async bulkToggleComplete(userId: string, taskIds: number[], completed: boolean): Promise<{ count: number }> {
    return this.bulkOperation(userId, { task_ids: taskIds, completed });
  },

  /**
   * Bulk update priority
   */
  async bulkUpdatePriority(
    userId: string,
    taskIds: number[],
    priority: 'high' | 'medium' | 'low' | 'none'
  ): Promise<{ count: number }> {
    return this.bulkOperation(userId, { task_ids: taskIds, priority });
  },

  // ============ HISTORY ENDPOINTS ============ (US7)

  /**
   * Get audit log for all tasks or a specific task
   */
  async getHistory(userId: string, taskId?: number): Promise<HistoryResponse> {
    const url = taskId
      ? `/api/${userId}/history/tasks/${taskId}`
      : `/api/${userId}/history`;
    const response = await apiClient.get(url);
    return response.data;
  },

  // ============ NOTIFICATION ENDPOINTS ============ (US8)

  /**
   * Get all notifications for user
   */
  async getNotifications(userId: string, unreadOnly: boolean = false): Promise<NotificationsResponse> {
    const response = await apiClient.get(`/api/${userId}/notifications`, {
      params: { unread_only: unreadOnly }
    });
    return response.data;
  },

  /**
   * Mark notification as read
   */
  async markNotificationRead(userId: string, notificationId: number): Promise<void> {
    await apiClient.patch(`/api/${userId}/notifications/${notificationId}/read`);
  },

  /**
   * Mark all notifications as read
   */
  async markAllNotificationsRead(userId: string): Promise<void> {
    await apiClient.patch(`/api/${userId}/notifications/mark-all-read`);
  },

  // ============ PREFERENCES ENDPOINTS ============ (US9)

  /**
   * Get user preferences
   */
  async getPreferences(userId: string): Promise<any> {
    const response = await apiClient.get(`/api/${userId}/preferences`);
    return response.data;
  },

  /**
   * Update user preferences
   */
  async updatePreferences(userId: string, data: any): Promise<any> {
    const response = await apiClient.put(`/api/${userId}/preferences`, data);
    return response.data;
  },

  // ============ STATS ENDPOINTS ============ (US10)

  /**
   * Get task statistics
   */
  async getStats(userId: string): Promise<any> {
    const response = await apiClient.get(`/api/${userId}/stats`);
    return response.data;
  },

  /**
   * Get completion history (over time)
   */
  async getCompletionStats(userId: string, days: number = 7): Promise<any[]> {
    const response = await apiClient.get(`/api/${userId}/stats/completion-history`, {
      params: { days }
    });
    return response.data;
  },

  // ============ EXPORT/IMPORT ENDPOINTS ============ (US11)

  /**
   * Export tasks as JSON and trigger download
   */
  async exportTasksJson(userId: string): Promise<void> {
    const response = await apiClient.get(`/api/${userId}/export/json`, {
      responseType: 'blob'
    });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `tasks_export_${userId}.json`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  },

  /**
   * Export tasks as CSV and trigger download
   */
  async exportTasksCsv(userId: string): Promise<void> {
    const response = await apiClient.get(`/api/${userId}/export/csv`, {
      responseType: 'blob'
    });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `tasks_export_${userId}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  },

  /**
   * Import tasks from JSON file
   */
  async importTasksJson(userId: string, file: File): Promise<{ message: string }> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post(`/api/${userId}/import/json`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  },
};

export default api;
