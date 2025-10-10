/**
 * 🇬🇦 RSU Gabon - API Endpoints
 * Standards Top 1% - Configuration Centralisée
 * Fichier: src/services/api/endpoints.js
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_VERSION = '/api/v1';

/**
 * Endpoints API organisés par module
 */
export const API_ENDPOINTS = {
  // ================================================================================
  // AUTHENTIFICATION
  // ================================================================================
  AUTH: {
    TOKEN: `${API_VERSION}/auth/token/`,
    REFRESH: `${API_VERSION}/auth/token/refresh/`,
    VERIFY: `${API_VERSION}/auth/token/verify/`,
  },

  // ================================================================================
  // CORE (UTILISATEURS & AUDIT)
  // ================================================================================
  CORE: {
    USERS: `${API_VERSION}/core/users/`,
    AUDIT_LOGS: `${API_VERSION}/core/audit/`,
    PERMISSIONS: `${API_VERSION}/core/permissions/`,
  },

  // ================================================================================
  // IDENTITY (PERSONNES & MÉNAGES)
  // ================================================================================
  IDENTITY: {
    PERSONS: `${API_VERSION}/identity/persons/`,
    HOUSEHOLDS: `${API_VERSION}/identity/households/`,
    GEOGRAPHIC: `${API_VERSION}/identity/geographic/`,
    RBPP_SYNC: `${API_VERSION}/identity/rbpp-sync/`,
  },

  // ================================================================================
  // PROGRAMS (NOUVEAUX ENDPOINTS)
  // ================================================================================
  PROGRAMS: {
    // Catégories
    CATEGORIES: `${API_VERSION}/programs/categories/`,
    
    // Programmes sociaux
    PROGRAMS: `${API_VERSION}/programs/programs/`,
    ACTIVE_PROGRAMS: `${API_VERSION}/programs/programs/active/`,
    
    // Inscriptions
    ENROLLMENTS: `${API_VERSION}/programs/enrollments/`,
    CHECK_ELIGIBILITY: `${API_VERSION}/programs/enrollments/check_eligibility/`,
    
    // Paiements
    PAYMENTS: `${API_VERSION}/programs/payments/`,
    PENDING_PAYMENTS: `${API_VERSION}/programs/payments/pending/`,
    PAYMENT_STATISTICS: `${API_VERSION}/programs/payments/statistics/`,
  },

  // ================================================================================
  // SERVICES (VULNÉRABILITÉ & ÉLIGIBILITÉ)
  // ================================================================================
  SERVICES: {
    VULNERABILITY: `${API_VERSION}/services/vulnerability/`,
    ELIGIBILITY: `${API_VERSION}/services/eligibility/`,
    GEOTARGETING: `${API_VERSION}/services/geotargeting/`,
  },

  // ================================================================================
  // ANALYTICS (TABLEAUX DE BORD)
  // ================================================================================
  ANALYTICS: {
    DASHBOARD: `${API_VERSION}/analytics/dashboard/`,
    REPORTS: `${API_VERSION}/analytics/reports/`,
    EXPORTS: `${API_VERSION}/analytics/exports/`,
  },
};

/**
 * Construction d'URL avec paramètres
 * @param {string} endpoint - Endpoint de base
 * @param {Object} params - Paramètres query string
 * @returns {string} URL complète avec paramètres
 */
export function buildURL(endpoint, params = {}) {
  const url = new URL(`${API_BASE_URL}${endpoint}`);
  
  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== '') {
      url.searchParams.append(key, value);
    }
  });
  
  return url.toString();
}

/**
 * Helpers pour endpoints spécifiques
 */
export const API_HELPERS = {
  // Détail d'une personne
  personDetail: (id) => `${API_ENDPOINTS.IDENTITY.PERSONS}${id}/`,
  
  // Détail d'un programme
  programDetail: (id) => `${API_ENDPOINTS.PROGRAMS.PROGRAMS}${id}/`,
  
  // Statistiques d'un programme
  programStats: (id) => `${API_ENDPOINTS.PROGRAMS.PROGRAMS}${id}/statistics/`,
  
  // Activation/Suspension programme
  activateProgram: (id) => `${API_ENDPOINTS.PROGRAMS.PROGRAMS}${id}/activate/`,
  suspendProgram: (id) => `${API_ENDPOINTS.PROGRAMS.PROGRAMS}${id}/suspend/`,
  closeProgram: (id) => `${API_ENDPOINTS.PROGRAMS.PROGRAMS}${id}/close/`,
  
  // Actions sur inscriptions
  approveEnrollment: (id) => `${API_ENDPOINTS.PROGRAMS.ENROLLMENTS}${id}/approve/`,
  rejectEnrollment: (id) => `${API_ENDPOINTS.PROGRAMS.ENROLLMENTS}${id}/reject/`,
  suspendEnrollment: (id) => `${API_ENDPOINTS.PROGRAMS.ENROLLMENTS}${id}/suspend/`,
  reactivateEnrollment: (id) => `${API_ENDPOINTS.PROGRAMS.ENROLLMENTS}${id}/reactivate/`,
  completeEnrollment: (id) => `${API_ENDPOINTS.PROGRAMS.ENROLLMENTS}${id}/complete/`,
  
  // Actions sur paiements
  processPayment: (id) => `${API_ENDPOINTS.PROGRAMS.PAYMENTS}${id}/process/`,
  cancelPayment: (id) => `${API_ENDPOINTS.PROGRAMS.PAYMENTS}${id}/cancel/`,
  batchProcessPayments: () => `${API_ENDPOINTS.PROGRAMS.PAYMENTS}batch_process/`,
  
  // Détails ménage
  householdDetail: (id) => `${API_ENDPOINTS.IDENTITY.HOUSEHOLDS}${id}/`,
  
  // Logs audit utilisateur
  userAuditLogs: (userId) => `${API_ENDPOINTS.CORE.AUDIT_LOGS}?user=${userId}`,
};

export default API_ENDPOINTS;