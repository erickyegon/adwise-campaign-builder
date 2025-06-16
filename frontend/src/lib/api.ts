/**
 * API Client for AdWise AI Campaign Builder
 * 
 * Provides a centralized HTTP client for all API interactions
 * with proper error handling, authentication, and type safety.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

interface ApiResponse<T = any> {
  data?: T;
  message?: string;
  error?: string;
  status: number;
}

class ApiClient {
  private baseURL: string;
  private token: string | null = null;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
    this.token = localStorage.getItem('auth_token');
  }

  private async request<T = any>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Authentication methods
  setToken(token: string) {
    this.token = token;
    localStorage.setItem('auth_token', token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('auth_token');
  }

  // HTTP methods
  async get<T = any>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  async post<T = any>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T = any>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async patch<T = any>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async delete<T = any>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }

  // Specific API endpoints
  
  // Campaigns
  async getCampaigns(params?: any) {
    const query = params ? `?${new URLSearchParams(params)}` : '';
    return this.get(`/campaigns${query}`);
  }

  async getCampaign(id: string) {
    return this.get(`/campaigns/${id}`);
  }

  async createCampaign(data: any) {
    return this.post('/campaigns', data);
  }

  async updateCampaign(id: string, data: any) {
    return this.put(`/campaigns/${id}`, data);
  }

  async deleteCampaign(id: string) {
    return this.delete(`/campaigns/${id}`);
  }

  // Ads
  async getAds(params?: any) {
    const query = params ? `?${new URLSearchParams(params)}` : '';
    return this.get(`/ads${query}`);
  }

  async getAd(id: string) {
    return this.get(`/ads/${id}`);
  }

  async createAd(data: any) {
    return this.post('/ads', data);
  }

  async updateAd(id: string, data: any) {
    return this.put(`/ads/${id}`, data);
  }

  async deleteAd(id: string) {
    return this.delete(`/ads/${id}`);
  }

  // Analytics
  async getAnalytics(params?: any) {
    const query = params ? `?${new URLSearchParams(params)}` : '';
    return this.get(`/analytics${query}`);
  }

  async getCampaignAnalytics(campaignId: string) {
    return this.get(`/analytics/campaigns/${campaignId}`);
  }

  async getAdAnalytics(adId: string) {
    return this.get(`/analytics/ads/${adId}`);
  }

  // Users
  async getUsers(params?: any) {
    const query = params ? `?${new URLSearchParams(params)}` : '';
    return this.get(`/users${query}`);
  }

  async getUser(id: string) {
    return this.get(`/users/${id}`);
  }

  async createUser(data: any) {
    return this.post('/users', data);
  }

  async updateUser(id: string, data: any) {
    return this.put(`/users/${id}`, data);
  }

  async deleteUser(id: string) {
    return this.delete(`/users/${id}`);
  }

  // Teams
  async getTeams(params?: any) {
    const query = params ? `?${new URLSearchParams(params)}` : '';
    return this.get(`/teams${query}`);
  }

  async getTeam(id: string) {
    return this.get(`/teams/${id}`);
  }

  async createTeam(data: any) {
    return this.post('/teams', data);
  }

  async updateTeam(id: string, data: any) {
    return this.put(`/teams/${id}`, data);
  }

  async deleteTeam(id: string) {
    return this.delete(`/teams/${id}`);
  }

  // Reports
  async getReports(params?: any) {
    const query = params ? `?${new URLSearchParams(params)}` : '';
    return this.get(`/reports${query}`);
  }

  async generateReport(data: any) {
    return this.post('/reports/generate', data);
  }

  async downloadReport(id: string, format: string = 'pdf') {
    return this.get(`/reports/${id}/download?format=${format}`);
  }

  // AI Services
  async generateContent(data: any) {
    return this.post('/ai/content/generate', data);
  }

  async optimizeCampaign(data: any) {
    return this.post('/ai/campaigns/optimize', data);
  }

  async analyzePerformance(data: any) {
    return this.post('/ai/analytics/analyze', data);
  }

  // Health check
  async healthCheck() {
    return this.get('/health');
  }
}

// Create and export the API client instance
export const api = new ApiClient(API_BASE_URL);

// Export types for use in components
export type { ApiResponse };
