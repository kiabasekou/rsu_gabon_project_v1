/**
 * RSU Gabon - API Client
 * Avec gestion JWT automatique
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class APIClient {
  async request(method, url, data = null, params = null) {
    if (!url) {
      throw new Error('URL endpoint is required');
    }

    let fullUrl = `${API_BASE_URL}${url}`;

    // Ajouter query params si présents
    if (params) {
      const queryString = new URLSearchParams(params).toString();
      fullUrl += `?${queryString}`;
    }

    const token = localStorage.getItem('access_token');
    
    const headers = {
      'Content-Type': 'application/json',
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const config = {
      method,
      headers,
    };

    if (data && method !== 'GET') {
      config.body = JSON.stringify(data);
    }

    console.log(`🌐 ${method} ${fullUrl}`);

    try {
      const response = await fetch(fullUrl, config);
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  async get(url, params) {
    return this.request('GET', url, null, params);
  }

  async post(url, data) {
    return this.request('POST', url, data);
  }

  async put(url, data) {
    return this.request('PUT', url, data);
  }

  async delete(url) {
    return this.request('DELETE', url);
  }

  getCurrentUser() {
    const user = localStorage.getItem('current_user');
    return user ? JSON.parse(user) : null;
  }
}

const apiClient = new APIClient();
export default apiClient;