/**
 * 🇬🇦 RSU Gabon - Programs API Service
 * Standards Top 1% - Gestion API Programmes Sociaux
 * Fichier: rsu_admin_dashboard/src/services/api/programsAPI.js
 */

import apiClient from './apiClient';

class ProgramsAPI {
  constructor() {
    this.baseUrl = '/programs';
  }

  // ==================== PROGRAMMES ====================

  /**
   * Récupérer tous les programmes
   * @param {Object} filters - Filtres optionnels (status, category, search)
   * @returns {Promise<Array>}
   */
  async getPrograms(filters = {}) {
    const params = new URLSearchParams();
    
    if (filters.status) params.append('status', filters.status);
    if (filters.category) params.append('category', filters.category);
    if (filters.search) params.append('search', filters.search);
    if (filters.ordering) params.append('ordering', filters.ordering);
    
    const queryString = params.toString();
    const endpoint = `${this.baseUrl}/programs/${queryString ? `?${queryString}` : ''}`;
    
    return await apiClient.get(endpoint);
  }

  /**
   * Récupérer un programme par ID
   * @param {number} programId
   * @returns {Promise<Object>}
   */
  async getProgramById(programId) {
    return await apiClient.get(`${this.baseUrl}/programs/${programId}/`);
  }

  /**
   * Créer un nouveau programme
   * @param {Object} programData
   * @returns {Promise<Object>}
   */
  async createProgram(programData) {
    return await apiClient.post(`${this.baseUrl}/programs/`, programData);
  }

  /**
   * Mettre à jour un programme
   * @param {number} programId
   * @param {Object} programData
   * @returns {Promise<Object>}
   */
  async updateProgram(programId, programData) {
    return await apiClient.patch(`${this.baseUrl}/programs/${programId}/`, programData);
  }

  /**
   * Supprimer un programme
   * @param {number} programId
   * @returns {Promise<void>}
   */
  async deleteProgram(programId) {
    return await apiClient.delete(`${this.baseUrl}/programs/${programId}/`);
  }

  /**
   * Récupérer programmes actifs uniquement
   * @returns {Promise<Array>}
   */
  async getActivePrograms() {
    return await apiClient.get(`${this.baseUrl}/programs/active/`);
  }

  /**
   * Statistiques détaillées d'un programme
   * @param {number} programId
   * @returns {Promise<Object>}
   */
  async getProgramStatistics(programId) {
    return await apiClient.get(`${this.baseUrl}/programs/${programId}/statistics/`);
  }

  /**
   * Activer un programme
   * @param {number} programId
   * @returns {Promise<Object>}
   */
  async activateProgram(programId) {
    return await apiClient.post(`${this.baseUrl}/programs/${programId}/activate/`);
  }

  /**
   * Suspendre un programme
   * @param {number} programId
   * @returns {Promise<Object>}
   */
  async pauseProgram(programId) {
    return await apiClient.post(`${this.baseUrl}/programs/${programId}/pause/`);
  }

  /**
   * Clôturer un programme
   * @param {number} programId
   * @returns {Promise<Object>}
   */
  async closeProgram(programId) {
    return await apiClient.post(`${this.baseUrl}/programs/${programId}/close/`);
  }

  // ==================== CATÉGORIES ====================

  /**
   * Récupérer toutes les catégories
   * @returns {Promise<Array>}
   */
  async getCategories() {
    return await apiClient.get(`${this.baseUrl}/categories/`);
  }

  /**
   * Créer une catégorie
   * @param {Object} categoryData
   * @returns {Promise<Object>}
   */
  async createCategory(categoryData) {
    return await apiClient.post(`${this.baseUrl}/categories/`, categoryData);
  }

  // ==================== INSCRIPTIONS ====================

  /**
   * Récupérer inscriptions d'un programme
   * @param {number} programId
   * @param {Object} filters
   * @returns {Promise<Array>}
   */
  async getEnrollments(programId = null, filters = {}) {
    const params = new URLSearchParams();
    
    if (programId) params.append('program', programId);
    if (filters.status) params.append('status', filters.status);
    if (filters.beneficiary) params.append('beneficiary', filters.beneficiary);
    
    const queryString = params.toString();
    const endpoint = `${this.baseUrl}/enrollments/${queryString ? `?${queryString}` : ''}`;
    
    return await apiClient.get(endpoint);
  }

  /**
   * Récupérer une inscription par ID
   * @param {number} enrollmentId
   * @returns {Promise<Object>}
   */
  async getEnrollmentById(enrollmentId) {
    return await apiClient.get(`${this.baseUrl}/enrollments/${enrollmentId}/`);
  }

  /**
   * Créer une inscription
   * @param {Object} enrollmentData
   * @returns {Promise<Object>}
   */
  async createEnrollment(enrollmentData) {
    return await apiClient.post(`${this.baseUrl}/enrollments/`, enrollmentData);
  }

  /**
   * Approuver une inscription
   * @param {number} enrollmentId
   * @returns {Promise<Object>}
   */
  async approveEnrollment(enrollmentId) {
    return await apiClient.post(`${this.baseUrl}/enrollments/${enrollmentId}/approve/`);
  }

  /**
   * Rejeter une inscription
   * @param {number} enrollmentId
   * @param {string} reason
   * @returns {Promise<Object>}
   */
  async rejectEnrollment(enrollmentId, reason) {
    return await apiClient.post(`${this.baseUrl}/enrollments/${enrollmentId}/reject/`, { reason });
  }

  /**
   * Suspendre une inscription
   * @param {number} enrollmentId
   * @returns {Promise<Object>}
   */
  async suspendEnrollment(enrollmentId) {
    return await apiClient.post(`${this.baseUrl}/enrollments/${enrollmentId}/suspend/`);
  }

  /**
   * Récupérer inscriptions en attente
   * @returns {Promise<Array>}
   */
  async getPendingEnrollments() {
    return await apiClient.get(`${this.baseUrl}/enrollments/pending/`);
  }

  // ==================== PAIEMENTS ====================

  /**
   * Récupérer paiements
   * @param {Object} filters
   * @returns {Promise<Array>}
   */
  async getPayments(filters = {}) {
    const params = new URLSearchParams();
    
    if (filters.program) params.append('program', filters.program);
    if (filters.beneficiary) params.append('beneficiary', filters.beneficiary);
    if (filters.status) params.append('status', filters.status);
    if (filters.enrollment) params.append('enrollment', filters.enrollment);
    
    const queryString = params.toString();
    const endpoint = `${this.baseUrl}/payments/${queryString ? `?${queryString}` : ''}`;
    
    return await apiClient.get(endpoint);
  }

  /**
   * Récupérer un paiement par ID
   * @param {number} paymentId
   * @returns {Promise<Object>}
   */
  async getPaymentById(paymentId) {
    return await apiClient.get(`${this.baseUrl}/payments/${paymentId}/`);
  }

  /**
   * Créer un paiement
   * @param {Object} paymentData
   * @returns {Promise<Object>}
   */
  async createPayment(paymentData) {
    return await apiClient.post(`${this.baseUrl}/payments/`, paymentData);
  }

  /**
   * Traiter un paiement (marquer comme complété)
   * @param {number} paymentId
   * @returns {Promise<Object>}
   */
  async processPayment(paymentId) {
    return await apiClient.post(`${this.baseUrl}/payments/${paymentId}/process/`);
  }

  /**
   * Marquer un paiement comme échoué
   * @param {number} paymentId
   * @param {string} reason
   * @returns {Promise<Object>}
   */
  async markPaymentFailed(paymentId, reason) {
    return await apiClient.post(`${this.baseUrl}/payments/${paymentId}/mark_failed/`, { reason });
  }

  /**
   * Récupérer paiements en attente
   * @returns {Promise<Array>}
   */
  async getPendingPayments() {
    return await apiClient.get(`${this.baseUrl}/payments/pending/`);
  }

  /**
   * Statistiques globales paiements
   * @returns {Promise<Object>}
   */
  async getPaymentsStatistics() {
    return await apiClient.get(`${this.baseUrl}/payments/statistics/`);
  }

  /**
   * Traitement batch de paiements
   * @param {Array} paymentIds
   * @returns {Promise<Object>}
   */
  async batchProcessPayments(paymentIds) {
    return await apiClient.post(`${this.baseUrl}/payments/batch_process/`, { 
      payment_ids: paymentIds 
    });
  }

  // ==================== ÉLIGIBILITÉ ====================

  /**
   * Vérifier éligibilité d'un bénéficiaire
   * @param {number} personId
   * @param {number} programId
   * @returns {Promise<Object>}
   */
  async checkEligibility(personId, programId) {
    return await apiClient.post(`${this.baseUrl}/enrollments/check_eligibility/`, {
      person_id: personId,
      program_id: programId
    });
  }

  // ==================== EXPORT ====================

  /**
   * Exporter données programme
   * @param {number} programId
   * @param {string} format - 'csv' ou 'excel'
   * @returns {Promise<Blob>}
   */
  async exportProgram(programId, format = 'csv') {
    const response = await fetch(
      `${apiClient.baseURL}${this.baseUrl}/programs/${programId}/export/?format=${format}`,
      {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      }
    );
    
    if (!response.ok) {
      throw new Error('Export failed');
    }
    
    return await response.blob();
  }

  /**
   * Exporter liste inscriptions
   * @param {number} programId
   * @param {string} format
   * @returns {Promise<Blob>}
   */
  async exportEnrollments(programId, format = 'csv') {
    const response = await fetch(
      `${apiClient.baseURL}${this.baseUrl}/enrollments/export/?program=${programId}&format=${format}`,
      {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      }
    );
    
    if (!response.ok) {
      throw new Error('Export failed');
    }
    
    return await response.blob();
  }
}

// Export instance singleton
export const programsAPI = new ProgramsAPI();
export default programsAPI;