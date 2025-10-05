// =============================================================================
// 1. API CLIENT SERVICE (services/api/apiClient.js)
// =============================================================================
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL = __DEV__ 
  ? 'http://localhost:8000/api/v1'
  : 'https://api.rsu.gouv.ga/api/v1';

class APIClient {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Intercepteur requêtes - Ajout JWT automatique
    this.client.interceptors.request.use(
      async (config) => {
        const token = await AsyncStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Intercepteur réponses - Gestion refresh token
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const refreshToken = await AsyncStorage.getItem('refresh_token');
            const response = await axios.post(
              `${API_BASE_URL}/auth/token/refresh/`,
              { refresh: refreshToken }
            );

            const { access } = response.data;
            await AsyncStorage.setItem('access_token', access);

            originalRequest.headers.Authorization = `Bearer ${access}`;
            return this.client(originalRequest);
          } catch (refreshError) {
            // Déconnexion si refresh échoue
            await AsyncStorage.multiRemove(['access_token', 'refresh_token', 'user']);
            // Navigation vers login
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  // Méthodes CRUD génériques
  get(url, params = {}) {
    return this.client.get(url, { params });
  }

  post(url, data) {
    return this.client.post(url, data);
  }

  put(url, data) {
    return this.client.put(url, data);
  }

  patch(url, data) {
    return this.client.patch(url, data);
  }

  delete(url) {
    return this.client.delete(url);
  }

  // Upload avec progression
  upload(url, formData, onProgress) {
    return this.client.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        if (onProgress) onProgress(percentCompleted);
      },
    });
  }
}

export default new APIClient();
