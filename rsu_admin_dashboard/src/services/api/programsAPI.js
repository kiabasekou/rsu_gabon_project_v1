/**
 * 🇬🇦 RSU Gabon - Programs API Service
 * Standards Top 1% - Intégration APIs Django REST
 * Fichier: src/services/api/programsAPI.js
 */

import apiClient from './apiClient';
import { API_ENDPOINTS } from './endpoints';

/**
 * Service API pour gestion des programmes sociaux
 */
class ProgramsAPIService {
  // ================================================================================
  // ENROLLMENTS
  // ================================================================================

  /**
   * Récupère toutes les inscriptions avec filtres
   * GET /api/v1/programs/enrollments/
   * 
   * @param {Object} params - Paramètres de filtrage
   * @param {string} params.status - PENDING, APPROVED, ACTIVE, REJECTED, COMPLETED
   * @param {number} params.program - ID programme
   * @param {number} params.beneficiary - ID bénéficiaire
   */
  async getEnrollments(params = {}) {
    try {
      const response = await apiClient.get(API_ENDPOINTS.PROGRAMS.ENROLLMENTS, params);
      console.log('✅ Enrollments loaded:', response.results?.length || 0);
      return response;
    } catch (error) {
      console.error('❌ Error fetching enrollments:', error);
      throw error;
    }
  }

  /**
   * Récupère une inscription spécifique
   * GET /api/v1/programs/enrollments/{id}/
   */
  async getEnrollmentById(id) {
    try {
      const response = await apiClient.get(`${API_ENDPOINTS.PROGRAMS.ENROLLMENTS}${id}/`);
      return response;
    } catch (error) {
      console.error(`❌ Error fetching enrollment ${id}:`, error);
      throw error;
    }
  }

  /**
   * Vérifie l'éligibilité d'une personne pour un programme
   * POST /api/v1/programs/enrollments/check_eligibility/
   * 
   * @param {Object} data
   * @param {number} data.program - ID programme
   * @param {number} data.beneficiary - ID personne
   */
  async checkEligibility(data) {
    try {
      const response = await apiClient.post(
        `${API_ENDPOINTS.PROGRAMS.ENROLLMENTS}check_eligibility/`,
        data
      );
      console.log('✅ Eligibility checked:', response.eligible);
      return response;
    } catch (error) {
      console.error('❌ Error checking eligibility:', error);
      throw error;
    }
  }

  /**
   * Crée une nouvelle inscription
   * POST /api/v1/programs/enrollments/
   */
  async createEnrollment(data) {
    try {
      const response = await apiClient.post(API_ENDPOINTS.PROGRAMS.ENROLLMENTS, data);
      console.log('✅ Enrollment created:', response.id);
      return response;
    } catch (error) {
      console.error('❌ Error creating enrollment:', error);
      throw error;
    }
  }

  /**
   * Approuve une inscription
   * POST /api/v1/programs/enrollments/{id}/approve/
   */
  async approveEnrollment(id, data = {}) {
    try {
      const response = await apiClient.post(
        `${API_ENDPOINTS.PROGRAMS.ENROLLMENTS}${id}/approve/`,
        data
      );
      console.log('✅ Enrollment approved:', id);
      return response;
    } catch (error) {
      console.error(`❌ Error approving enrollment ${id}:`, error);
      throw error;
    }
  }

  /**
   * Rejette une inscription
   * POST /api/v1/programs/enrollments/{id}/reject/
   */
  async rejectEnrollment(id, data) {
    try {
      const response = await apiClient.post(
        `${API_ENDPOINTS.PROGRAMS.ENROLLMENTS}${id}/reject/`,
        data
      );
      console.log('✅ Enrollment rejected:', id);
      return response;
    } catch (error) {
      console.error(`❌ Error rejecting enrollment ${id}:`, error);
      throw error;
    }
  }

  /**
   * Suspend une inscription
   * POST /api/v1/programs/enrollments/{id}/suspend/
   */
  async suspendEnrollment(id, data) {
    try {
      const response = await apiClient.post(
        `${API_ENDPOINTS.PROGRAMS.ENROLLMENTS}${id}/suspend/`,
        data
      );
      console.log('✅ Enrollment suspended:', id);
      return response;
    } catch (error) {
      console.error(`❌ Error suspending enrollment ${id}:`, error);
      throw error;
    }
  }

  /**
   * Réactive une inscription
   * POST /api/v1/programs/enrollments/{id}/reactivate/
   */
  async reactivateEnrollment(id) {
    try {
      const response = await apiClient.post(
        `${API_ENDPOINTS.PROGRAMS.ENROLLMENTS}${id}/reactivate/`
      );
      console.log('✅ Enrollment reactivated:', id);
      return response;
    } catch (error) {
      console.error(`❌ Error reactivating enrollment ${id}:`, error);
      throw error;
    }
  }

  /**
   * Complète une inscription
   * POST /api/v1/programs/enrollments/{id}/complete/
   */
  async completeEnrollment(id, data = {}) {
    try {
      const response = await apiClient.post(
        `${API_ENDPOINTS.PROGRAMS.ENROLLMENTS}${id}/complete/`,
        data
      );
      console.log('✅ Enrollment completed:', id);
      return response;
    } catch (error) {
      console.error(`❌ Error completing enrollment ${id}:`, error);
      throw error;
    }
  }

  // ================================================================================
  // PAYMENTS
  // ================================================================================

  /**
   * Récupère tous les paiements avec filtres
   * GET /api/v1/programs/payments/
   * 
   * @param {Object} params - Paramètres de filtrage
   * @param {string} params.status - PENDING, PROCESSING, COMPLETED, FAILED, CANCELLED
   * @param {number} params.program - ID programme
   * @param {number} params.enrollment - ID inscription
   */
  async getPayments(params = {}) {
    try {
      const response = await apiClient.get(API_ENDPOINTS.PROGRAMS.PAYMENTS, params);
      console.log('✅ Payments loaded:', response.results?.length || 0);
      return response;
    } catch (error) {
      console.error('❌ Error fetching payments:', error);
      throw error;
    }
  }

  /**
   * Récupère un paiement spécifique
   * GET /api/v1/programs/payments/{id}/
   */
  async getPaymentById(id) {
    try {
      const response = await apiClient.get(`${API_ENDPOINTS.PROGRAMS.PAYMENTS}${id}/`);
      return response;
    } catch (error) {
      console.error(`❌ Error fetching payment ${id}:`, error);
      throw error;
    }
  }

  /**
   * Récupère paiements en attente
   * GET /api/v1/programs/payments/pending/
   */
  async getPendingPayments() {
    try {
      const response = await apiClient.get(`${API_ENDPOINTS.PROGRAMS.PAYMENTS}pending/`);
      console.log('✅ Pending payments:', response.length);
      return response;
    } catch (error) {
      console.error('❌ Error fetching pending payments:', error);
      throw error;
    }
  }

  /**
   * Récupère statistiques des paiements
   * GET /api/v1/programs/payments/statistics/
   */
  async getPaymentsStatistics(params = {}) {
    try {
      const response = await apiClient.get(
        `${API_ENDPOINTS.PROGRAMS.PAYMENTS}statistics/`,
        params
      );
      return response;
    } catch (error) {
      console.error('❌ Error fetching payment statistics:', error);
      throw error;
    }
  }

  /**
   * Crée un nouveau paiement
   * POST /api/v1/programs/payments/
   */
  async createPayment(data) {
    try {
      const response = await apiClient.post(API_ENDPOINTS.PROGRAMS.PAYMENTS, data);
      console.log('✅ Payment created:', response.id);
      return response;
    } catch (error) {
      console.error('❌ Error creating payment:', error);
      throw error;
    }
  }

  /**
   * Traite un paiement
   * POST /api/v1/programs/payments/{id}/process/
   */
  async processPayment(id, data = {}) {
    try {
      const response = await apiClient.post(
        `${API_ENDPOINTS.PROGRAMS.PAYMENTS}${id}/process/`,
        data
      );
      console.log('✅ Payment processed:', id);
      return response;
    } catch (error) {
      console.error(`❌ Error processing payment ${id}:`, error);
      throw error;
    }
  }

  /**
   * Traite plusieurs paiements en batch
   * POST /api/v1/programs/payments/batch_process/
   * 
   * @param {Object} data
   * @param {Array<number>} data.payment_ids - IDs des paiements
   */
  async batchProcessPayments(data) {
    try {
      const response = await apiClient.post(
        `${API_ENDPOINTS.PROGRAMS.PAYMENTS}batch_process/`,
        data
      );
      console.log('✅ Batch payments processed:', data.payment_ids.length);
      return response;
    } catch (error) {
      console.error('❌ Error batch processing payments:', error);
      throw error;
    }
  }

  /**
   * Annule un paiement
   * POST /api/v1/programs/payments/{id}/cancel/
   */
  async cancelPayment(id, data) {
    try {
      const response = await apiClient.post(
        `${API_ENDPOINTS.PROGRAMS.PAYMENTS}${id}/cancel/`,
        data
      );
      console.log('✅ Payment cancelled:', id);
      return response;
    } catch (error) {
      console.error(`❌ Error cancelling payment ${id}:`, error);
      throw error;
    }
  }

  // ================================================================================
  // DASHBOARD & ANALYTICS
  // ================================================================================

  /**
   * Récupère dashboard complet des programmes
   */
  async getProgramsDashboard() {
    try {
      const [programs, categories, enrollmentsStats, paymentsStats] = await Promise.all([
        this.getPrograms(),
        this.getCategories(),
        this.getEnrollments({ page_size: 1 }), // Juste pour stats
        this.getPayments({ page_size: 1 }) // Juste pour stats
      ]);

      return {
        programs: programs.results || [],
        categories: categories.results || categories || [],
        total_programs: programs.count || 0,
        total_enrollments: enrollmentsStats.count || 0,
        total_payments: paymentsStats.count || 0,
        active_programs: programs.results?.filter(p => p.status === 'ACTIVE').length || 0
      };
    } catch (error) {
      console.error('❌ Error loading programs dashboard:', error);
      throw error;
    }
  }
}

// Export singleton instance
const programsAPI = new ProgramsAPIService();
export default programsAPI; 

  //================================================================================
  // CATEGORIES
  // ================================================================================

  /**
   * Récupère toutes les catégories de programmes
   * GET /api/v1/programs/categories/
   */
  async getCategories() {
    try {
      const response = await apiClient.get(API_ENDPOINTS.PROGRAMS.CATEGORIES);
      return response;
    } catch (error) {
      console.error('❌ Error fetching categories:', error);
      throw error;
    }
  }

  /**
   * Crée une nouvelle catégorie
   * POST /api/v1/programs/categories/
   */
  async createCategory(data) {
    try {
      const response = await apiClient.post(API_ENDPOINTS.PROGRAMS.CATEGORIES, data);
      console.log('✅ Category created:', response.id);
      return response;
    } catch (error) {
      console.error('❌ Error creating category:', error);
      throw error;
    }
  }

  // ================================================================================
  // PROGRAMS
  // ================================================================================

  /**
   * Récupère tous les programmes avec filtres optionnels
   * GET /api/v1/programs/programs/
   * 
   * @param {Object} params - Paramètres de filtrage
   * @param {string} params.status - Statut: ACTIVE, PAUSED, CLOSED, DRAFT
   * @param {number} params.category - ID catégorie
   * @param {string} params.search - Recherche par nom/code
   * @param {number} params.page - Numéro de page
   * @param {number} params.page_size - Taille de page
   */
  async getPrograms(params = {}) {
    try {
      // ✅ VÉRIFIER que API_ENDPOINTS.PROGRAMS.PROGRAMS existe
      console.log('🔍 Endpoint programs:', API_ENDPOINTS.PROGRAMS.PROGRAMS);
      
      const response = await apiClient.get(API_ENDPOINTS.PROGRAMS.PROGRAMS, params);
      console.log('✅ Programs loaded:', response.results?.length || 0);
      return response;
    } catch (error) {
      console.error('❌ Error fetching programs:', error);
      throw error;
    }
  }

  /**
   * Récupère un programme spécifique
   * GET /api/v1/programs/programs/{id}/
   */
  async getProgramById(id) {
    try {
      const response = await apiClient.get(`${API_ENDPOINTS.PROGRAMS.PROGRAMS}${id}/`);
      return response;
    } catch (error) {
      console.error(`❌ Error fetching program ${id}:`, error);
      throw error;
    }
  }

  /**
   * Récupère uniquement les programmes actifs
   * GET /api/v1/programs/programs/active/
   */
  async getActivePrograms() {
    try {
      const response = await apiClient.get(`${API_ENDPOINTS.PROGRAMS.PROGRAMS}active/`);
      console.log('✅ Active programs:', response.length);
      return response;
    } catch (error) {
      console.error('❌ Error fetching active programs:', error);
      throw error;
    }
  }

  /**
   * Récupère statistiques d'un programme
   * GET /api/v1/programs/programs/{id}/statistics/
   */
  async getProgramStatistics(id) {
    try {
      const response = await apiClient.get(`${API_ENDPOINTS.PROGRAMS.PROGRAMS}${id}/statistics/`);
      return response;
    } catch (error) {
      console.error(`❌ Error fetching program statistics ${id}:`, error);
      throw error;
    }
  }

  /**
   * Crée un nouveau programme
   * POST /api/v1/programs/programs/
   */
  async createProgram(data) {
    try {
      const response = await apiClient.post(API_ENDPOINTS.PROGRAMS.PROGRAMS, data);
      console.log('✅ Program created:', response.code);
      return response;
    } catch (error) {
      console.error('❌ Error creating program:', error);
      throw error;
    }
  }

  /**
   * Met à jour un programme
   * PUT /api/v1/programs/programs/{id}/
   */
  async updateProgram(id, data) {
    try {
      const response = await apiClient.put(`${API_ENDPOINTS.PROGRAMS.PROGRAMS}${id}/`, data);
      console.log('✅ Program updated:', response.code);
      return response;
    } catch (error) {
      console.error(`❌ Error updating program ${id}:`, error);
      throw error;
    }
  }

  /**
   * Active un programme
   * POST /api/v1/programs/programs/{id}/activate/
   */
  async activateProgram(id) {
    try {
      const response = await apiClient.post(`${API_ENDPOINTS.PROGRAMS.PROGRAMS}${id}/activate/`);
      console.log('✅ Program activated:', id);
      return response;
    } catch (error) {
      console.error(`❌ Error activating program ${id}:`, error);
      throw error;
    }
  }

  /**
   * Suspend un programme
   * POST /api/v1/programs/programs/{id}/suspend/
   */
  async suspendProgram(id) {
    try {
      const response = await apiClient.post(`${API_ENDPOINTS.PROGRAMS.PROGRAMS}${id}/suspend/`);
      console.log('✅ Program suspended:', id);
      return response;
    } catch (error) {
      console.error(`❌ Error suspending program ${id}:`, error);
      throw error;
    }
  }

  /**
   * Clôture un programme
   * POST /api/v1/programs/programs/{id}/close/
   */
  async closeProgram(id) {
    try {
      const response = await apiClient.post(`${API_ENDPOINTS.PROGRAMS.PROGRAMS}${id}/close/`);
      console.log('✅ Program closed:', id);
      return response;
    } catch (error) {
      console.error(`❌ Error closing program ${id}:`, error);
      throw error;
    }
  }

  