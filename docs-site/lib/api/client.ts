// API 클라이언트

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class ApiClient {
  private apiKey: string | null = null;

  constructor() {
    // 클라이언트 사이드에서만 실행
    if (typeof window !== 'undefined') {
      this.apiKey = localStorage.getItem('api_key');
    }
  }

  setApiKey(key: string) {
    this.apiKey = key;
    if (typeof window !== 'undefined') {
      localStorage.setItem('api_key', key);
    }
  }

  clearApiKey() {
    this.apiKey = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('api_key');
    }
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (this.apiKey) {
      headers['X-API-Key'] = this.apiKey;
    }

    return headers;
  }

  async fetch(endpoint: string, options: RequestInit = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers = {
      ...this.getHeaders(),
      ...options.headers,
    };

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        error: response.statusText,
      }));
      throw new Error(error.error || error.detail || 'API Error');
    }

    return response.json();
  }

  // 지도 관련 API
  async uploadMap(file: File, metadata: {
    name: string;
    description?: string;
    map_type: string;
    scale_meters_per_pixel?: number;
  }) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('name', metadata.name);
    if (metadata.description) {
      formData.append('description', metadata.description);
    }
    formData.append('map_type', metadata.map_type);
    if (metadata.scale_meters_per_pixel) {
      formData.append('scale_meters_per_pixel', metadata.scale_meters_per_pixel.toString());
    }

    const url = `${API_BASE_URL}/api/v1/maps/upload`;
    const headers: HeadersInit = {};
    if (this.apiKey) {
      headers['X-API-Key'] = this.apiKey;
    }

    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        error: response.statusText,
      }));
      throw new Error(error.error || error.detail || 'Upload failed');
    }

    return response.json();
  }

  async getMaps() {
    return this.fetch('/api/v1/maps/');
  }

  async getMap(id: number) {
    return this.fetch(`/api/v1/maps/${id}`);
  }

  // 경로 찾기 API
  async findPath(data: {
    map_id: number;
    start: { x: number; y: number };
    end: { x: number; y: number };
    waypoints?: { x: number; y: number }[];
  }) {
    return this.fetch('/api/v1/pathfinding/route', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // 인증 API
  async verifyApiKey(key: string) {
    return this.fetch('/api/v1/auth/verify', {
      method: 'POST',
      body: JSON.stringify({ api_key: key }),
    });
  }

  // Dashboard API
  async getDashboardStats() {
    return this.fetch('/api/v1/dashboard/stats');
  }

  async getDashboardImages() {
    return this.fetch('/api/v1/dashboard/images');
  }

  async getApiUsage(period: 'day' | 'week' | 'month' = 'week') {
    return this.fetch(`/api/v1/dashboard/usage?period=${period}`);
  }

  async getApiKeys() {
    return this.fetch('/api/v1/dashboard/api-keys');
  }

  async createApiKey(name?: string) {
    return this.fetch('/api/v1/dashboard/api-keys', {
      method: 'POST',
      body: JSON.stringify({ name }),
    });
  }

  async deleteApiKey(keyId: number) {
    return this.fetch(`/api/v1/dashboard/api-keys/${keyId}`, {
      method: 'DELETE',
    });
  }
}

// 싱글톤 인스턴스
export const apiClient = new ApiClient();
