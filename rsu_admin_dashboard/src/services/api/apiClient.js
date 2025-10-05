const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

class APIClient {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  async request(endpoint, options = {}) {
    const token = localStorage.getItem('access_token');
    
    const config = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options.headers,
      },
    };

    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, config);
      
      if (response.status === 401) {
        await this.refreshToken();
        return this.request(endpoint, options);
      }

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  async refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) throw new Error('No refresh token');

    const response = await fetch(`${this.baseURL}/auth/token/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: refreshToken }),
    });

    if (response.ok) {
      const { access } = await response.json();
      localStorage.setItem('access_token', access);
    } else {
      localStorage.clear();
      window.location.href = '/login';
    }
  }

  get(endpoint, params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`${endpoint}${query ? `?${query}` : ''}`);
  }

  post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
}

export default new APIClient();