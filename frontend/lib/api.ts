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
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  completed?: boolean;
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
   * Get all tasks for a user with optional status filtering
   */
  async getTasks(
    userId: string,
    status: 'all' | 'pending' | 'completed' = 'all'
  ): Promise<TasksResponse> {
    const response = await apiClient.get(`/api/${userId}/tasks`, {
      params: { status },
    });
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
};

export default api;
