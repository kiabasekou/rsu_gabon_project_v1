/**
 * 🇬🇦 RSU Gabon - API Client Enhanced
 * Standards Top 1% - Gestion automatique refresh token + retry
 * Fichier: rsu_admin_dashboard/src/services/api/apiClient.js
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

class APIClient {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.isRefreshing = false;
    this.failedQueue = [];
  }

  /**
   * Gestion de la file d'attente pendant refresh
   */
  processQueue(error, token = null) {
    this.failedQueue.forEach(prom => {
      if (error) {
        prom.reject(error);
      } else {
        prom.resolve(token);
      }
    });
    this.failedQueue = [];
  }

  /**
   * Refresh token et retry de la requête originale
   */
  async refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      const response = await fetch(`${this.baseURL}/auth/token/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: refreshToken })
      });

      if (!response.ok) {
        throw new Error('Refresh token expired');
      }

      const data = await response.json();
      
      // Stockage nouveau access token
      localStorage.setItem('access_token', data.access);
      
      // Rotation refresh token si fourni
      if (data.refresh) {
        localStorage.setItem('refresh_token', data.refresh);
      }

      return data.access;
    } catch (error) {
      // Refresh échoué → Logout
      this.logout();
      throw error;
    }
  }

  /**
   * Requête principale avec gestion erreurs 401 et retry automatique
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

    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, config);

      // Gestion erreur 401 (Unauthorized)
      if (response.status === 401) {
        // Si déjà en cours de refresh, on met la requête en queue
        if (this.isRefreshing) {
          return new Promise((resolve, reject) => {
            this.failedQueue.push({ resolve, reject });
          }).then(token => {
            // Retry avec nouveau token
            config.headers['Authorization'] = `Bearer ${token}`;
            return fetch(`${this.baseURL}${endpoint}`, config);
          }).then(response => {
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return response.json();
          });
        }

        // Première 401 → Tentative refresh
        this.isRefreshing = true;

        try {
          const newToken = await this.refreshToken();
          this.isRefreshing = false;
          this.processQueue(null, newToken);

          // Retry requête originale avec nouveau token
          config.headers['Authorization'] = `Bearer ${newToken}`;
          const retryResponse = await fetch(`${this.baseURL}${endpoint}`, config);
          
          if (!retryResponse.ok) {
            throw new Error(`HTTP ${retryResponse.status}`);
          }
          
          return await retryResponse.json();
        } catch (refreshError) {
          this.isRefreshing = false;
          this.processQueue(refreshError, null);
          throw refreshError;
        }
      }

      // Autres erreurs HTTP
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  /**
   * Méthodes HTTP
   */
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

  patch(endpoint, data) {
    return this.request(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  delete(endpoint) {
    return this.request(endpoint, {
      method: 'DELETE',
    });
  }

  /**
   * Utilitaires authentification
   */
  getCurrentUser() {
    const userJson = localStorage.getItem('user');
    return userJson ? JSON.parse(userJson) : null;
  }

  isAuthenticated() {
    return !!localStorage.getItem('access_token');
  }

  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    window.location.href = '/login';
  }
}

const client = new APIClient();
export default client;