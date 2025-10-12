/**
 * 🇬🇦 RSU Gabon - Programs API Service
 * Standards Top 1% - Appels API Programmes
 */

import apiClient from './apiClient';
import ENDPOINTS from './endpoints';

export const programsAPI = {
  /**
   * Liste programmes avec filtres
   */
  async getPrograms(filters = {}) {
    const params = new URLSearchParams();
    
    if (filters.status) params.append('status', filters.status);
    if (filters.search) params.append('search', filters.search);
    if (filters.ordering) params.append('ordering', filters.ordering);
    
    const queryString = params.toString();
    const url = `${ENDPOINTS.PROGRAMS.PROGRAMS}${queryString ? `?${queryString}` : ''}`;
    
    return await apiClient.get(url);
  },

  /**
   * Détails programme par ID
   */
  async getProgramById(id) {
    return await apiClient.get(ENDPOINTS.PROGRAMS.PROGRAM_DETAIL(id));
  },

  /**
   * Statistiques programme
   */
  async getProgramStatistics(id) {
    return await apiClient.get(ENDPOINTS.PROGRAMS.PROGRAM_STATISTICS(id));
  },

  /**
   * Activer programme
   */
  async activateProgram(id) {
    return await apiClient.post(ENDPOINTS.PROGRAMS.ACTIVATE_PROGRAM(id), {});
  },

  /**
   * Suspendre programme
   */
  async pauseProgram(id) {
    return await apiClient.post(ENDPOINTS.PROGRAMS.PAUSE_PROGRAM(id), {});
  },

  /**
   * Clôturer programme
   */
  async closeProgram(id) {
    return await apiClient.post(ENDPOINTS.PROGRAMS.CLOSE_PROGRAM(id), {});
  },

  /**
   * Export données programme
   */
  async exportProgram(id, format = 'csv') {
    return await apiClient.get(ENDPOINTS.PROGRAMS.EXPORT_PROGRAM(id, format));
  }
};