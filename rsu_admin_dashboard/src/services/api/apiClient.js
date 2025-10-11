/**
 * 🇬🇦 RSU Gabon - API Client FIX DÉFINITIF
 * Standards Top 1% - Client HTTP avec JWT
 * Fichier: rsu_admin_dashboard/src/services/api/apiClient.js
 */

class APIClient {
  constructor() {
    // ✅ FIX DÉFINITIF: URL hardcodée avec /api/v1
    this.baseURL = 'http://localhost:8000/api/v1';
  }

  /**
   * Récupérer user actuel depuis localStorage
   */
  getCurrentUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  }

  /**
   * Requête HTTP générique
   */
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

    const url = `${this.baseURL}${endpoint}`;
    console.log(`🌐 ${options.method || 'GET'} ${url}`);

    const response = await fetch(url, config);

    if (!response.ok) {
      console.error(`❌ API Error: ${response.status} ${response.statusText}`);
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    return data;
  }

  /**
   * GET request
   */
  async get(endpoint, params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const fullEndpoint = queryString ? `${endpoint}?${queryString}` : endpoint;
    return this.request(fullEndpoint, { method: 'GET' });
  }

  /**
   * POST request
   */
  async post(endpoint, body = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }

  /**
   * PATCH request
   */
  async patch(endpoint, body = {}) {
    return this.request(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(body),
    });
  }

  /**
   * PUT request
   */
  async put(endpoint, body = {}) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(body),
    });
  }

  /**
   * DELETE request
   */
  async delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }
}

// Export instance singleton
const apiClient = new APIClient();
export default apiClient;