/** 
 * FIX: apiClient.js - Correction Authorization header 
 * Fichier: rsu_admin_dashboard/src/services/api/apiClient.js 
 */

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
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        ...options.headers,
      },
    };

    const response = await fetch(`${this.baseURL}${endpoint}`, config);

    if (response.status === 401) {
      console.error('401 Unauthorized - Token:', token ? 'EXISTS' : 'MISSING');
      window.location.href = '/login';
      throw new Error('Unauthorized');
    }

    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  }

  get(endpoint, params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`${endpoint}${query ? `?${query}` : ''}`);
  }
}

export default new APIClient();
