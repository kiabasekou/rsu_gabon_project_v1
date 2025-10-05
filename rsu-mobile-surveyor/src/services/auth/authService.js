// =============================================================================
// 2. AUTHENTICATION SERVICE (services/auth/authService.js)
// =============================================================================
import AsyncStorage from '@react-native-async-storage/async-storage';
import apiClient from '../api/apiClient';

class AuthService {
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
      return {
        success: false,
        error: error.response?.data?.detail || 'Échec de connexion',
      };
    }
  }

  async logout() {
    await AsyncStorage.multiRemove(['access_token', 'refresh_token', 'user']);
  }

  async getCurrentUser() {
    const userJson = await AsyncStorage.getItem('user');
    return userJson ? JSON.parse(userJson) : null;
  }

  async isAuthenticated() {
    const token = await AsyncStorage.getItem('access_token');
    return !!token;
  }
}

export default new AuthService();
