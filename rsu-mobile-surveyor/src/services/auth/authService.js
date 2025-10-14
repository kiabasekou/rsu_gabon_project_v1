// =============================================================================
// AUTH SERVICE COMPLET ET FONCTIONNEL
// Fichier: src/services/auth/authService.js
// =============================================================================
import AsyncStorage from '@react-native-async-storage/async-storage';
import apiClient from '../api/apiClient';

class AuthService {
  constructor() {
    this.isInitialized = false;
  }

  async initialize() {
    if (this.isInitialized) return;
    try {
      // Initialisation si nécessaire
      this.isInitialized = true;
    } catch (error) {
      console.warn('AuthService init error:', error);
    }
  }

  async login(username, password) {
    try {
      const response = await apiClient.post('/auth/token/', {
        username,
        password,
      });

      const { access, refresh, user } = response.data;

      // Stockage sécurisé
      await AsyncStorage.multiSet([
        ['access_token', access],
        ['refresh_token', refresh],
        ['user', JSON.stringify(user)],
      ]);

      return { success: true, user };
    } catch (error) {
      console.error('Login error:', error);
      return {
        success: false,
        error: error.response?.data?.detail || 'Échec de connexion',
      };
    }
  }

  async logout() {
    try {
      await AsyncStorage.multiRemove(['access_token', 'refresh_token', 'user']);
      return { success: true };
    } catch (error) {
      console.error('Logout error:', error);
      return { success: false, error: 'Erreur déconnexion' };
    }
  }

  async getCurrentUser() {
    try {
      const userJson = await AsyncStorage.getItem('user');
      return userJson ? JSON.parse(userJson) : null;
    } catch (error) {
      console.warn('Get current user error:', error);
      return null;
    }
  }

  async isAuthenticated() {
    try {
      const token = await AsyncStorage.getItem('access_token');
      return !!token;
    } catch (error) {
      console.warn('Is authenticated check error:', error);
      return false;
    }
  }

  async getAccessToken() {
    try {
      return await AsyncStorage.getItem('access_token');
    } catch (error) {
      console.warn('Get access token error:', error);
      return null;
    }
  }

  async getRefreshToken() {
    try {
      return await AsyncStorage.getItem('refresh_token');
    } catch (error) {
      console.warn('Get refresh token error:', error);
      return null;
    }
  }

  async updateUserInfo(user) {
    try {
      await AsyncStorage.setItem('user', JSON.stringify(user));
      return { success: true };
    } catch (error) {
      console.error('Update user info error:', error);
      return { success: false, error: 'Erreur mise à jour utilisateur' };
    }
  }

  async refreshAccessToken() {
    try {
      const refreshToken = await this.getRefreshToken();
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await apiClient.post('/auth/token/refresh/', {
        refresh: refreshToken,
      });

      const { access } = response.data;
      await AsyncStorage.setItem('access_token', access);

      return { success: true, token: access };
    } catch (error) {
      console.error('Refresh token error:', error);
      // Si refresh échoue, déconnecter
      await this.logout();
      return { success: false, error: 'Session expirée' };
    }
  }
}

// Export singleton
const authService = new AuthService();

// CRITIQUE: Export par défaut ET nommé pour compatibilité
export default authService;
export { authService };