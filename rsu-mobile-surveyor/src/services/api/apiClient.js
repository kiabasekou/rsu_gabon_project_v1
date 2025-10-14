// =============================================================================
// SERVICES MOBILE RSU GABON
// =============================================================================

// =============================================================================
// 1. API CLIENT (services/api/apiClient.js)
// =============================================================================
import AsyncStorage from '@react-native-async-storage/async-storage';
import axios from 'axios';
import NetInfo from '@react-native-community/netinfo';

const BASE_URL = __DEV__ 
  ? 'http://localhost:8000/api/v1' 
  : 'https://rsu-api.gouv.ga/api/v1';

const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Intercepteur pour ajouter token JWT automatiquement
apiClient.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Intercepteur pour gérer refresh token
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = await AsyncStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${BASE_URL}/auth/token/refresh/`, {
            refresh: refreshToken,
          });

          const { access } = response.data;
          await AsyncStorage.setItem('access_token', access);

          originalRequest.headers.Authorization = `Bearer ${access}`;
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        // Token refresh échoué, rediriger vers login
        await AsyncStorage.multiRemove(['access_token', 'refresh_token', 'user']);
        // Déclencher logout dans l'app
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;

