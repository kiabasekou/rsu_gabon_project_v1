/**
 * 🇬🇦 RSU Gabon - API Endpoints
 * Standards Top 1% - Configuration centralisée COMPLÈTE
 * Fichier: rsu_admin_dashboard/src/services/api/endpoints.js
 */

const ENDPOINTS = {
  // ==================== AUTHENTIFICATION ====================
  AUTH: {
    TOKEN: '/auth/token/',
    REFRESH: '/auth/token/refresh/',
    LOGOUT: '/auth/logout/',
  },

  // ==================== ANALYTICS (DASHBOARD) ====================
  ANALYTICS: {
    DASHBOARD: '/analytics/dashboard/',
    PROVINCE_STATS: '/analytics/province-stats/',
    REPORTS: '/analytics/reports/',
  },

  // ==================== IDENTITY (BÉNÉFICIAIRES) ====================
  IDENTITY: {
    // Personnes
    PERSONS: '/identity/persons/',
    PERSON_DETAIL: (id) => `/identity/persons/${id}/`,
    SEARCH: '/identity/persons/search/',
    CHECK_DUPLICATES: '/identity/persons/check-duplicates/',
    STATISTICS: '/identity/persons/statistics/',
    
    // Ménages
    HOUSEHOLDS: '/identity/households/',
    HOUSEHOLD_DETAIL: (id) => `/identity/households/${id}/`,
    HOUSEHOLD_STATS: '/identity/households/statistics/',
    
    // Données géographiques
    GEOGRAPHIC_DATA: '/identity/geographic-data/',
  },

  // ==================== PROGRAMS (PROGRAMMES SOCIAUX) ====================
  PROGRAMS: {
    // Catégories
    CATEGORIES: '/programs/categories/',
    CATEGORY_DETAIL: (id) => `/programs/categories/${id}/`,
    
    // Programmes
    PROGRAMS: '/programs/programs/',
    PROGRAM_DETAIL: (id) => `/programs/programs/${id}/`,
    PROGRAM_STATISTICS: (id) => `/programs/programs/${id}/statistics/`,
    ACTIVE_PROGRAMS: '/programs/programs/active/',
    ACTIVATE_PROGRAM: (id) => `/programs/programs/${id}/activate/`,
    PAUSE_PROGRAM: (id) => `/programs/programs/${id}/pause/`,
    CLOSE_PROGRAM: (id) => `/programs/programs/${id}/close/`,
    EXPORT_PROGRAM: (id, format) => `/programs/programs/${id}/export/?format=${format}`,
    
    // Inscriptions
    ENROLLMENTS: '/programs/enrollments/',
    ENROLLMENT_DETAIL: (id) => `/programs/enrollments/${id}/`,
    PENDING_ENROLLMENTS: '/programs/enrollments/pending/',
    CHECK_ELIGIBILITY: '/programs/enrollments/check_eligibility/',
    APPROVE_ENROLLMENT: (id) => `/programs/enrollments/${id}/approve/`,
    REJECT_ENROLLMENT: (id) => `/programs/enrollments/${id}/reject/`,
    SUSPEND_ENROLLMENT: (id) => `/programs/enrollments/${id}/suspend/`,
    EXPORT_ENROLLMENTS: (programId, format) => `/programs/enrollments/export/?program=${programId}&format=${format}`,
    
    // Paiements
    PAYMENTS: '/programs/payments/',
    PAYMENT_DETAIL: (id) => `/programs/payments/${id}/`,
    PENDING_PAYMENTS: '/programs/payments/pending/',
    PAYMENT_STATISTICS: '/programs/payments/statistics/',
    PROCESS_PAYMENT: (id) => `/programs/payments/${id}/process/`,
    MARK_FAILED: (id) => `/programs/payments/${id}/mark_failed/`,
    BATCH_PROCESS: '/programs/payments/batch_process/',
  },

  // ==================== SERVICES (VULNÉRABILITÉ & IA) ====================
  SERVICES: {
    // Évaluation vulnérabilité
    VULNERABILITY: '/services/vulnerability-assessment/',
    VULNERABILITY_DETAIL: (id) => `/services/vulnerability-assessment/${id}/`,
    CALCULATE_SCORE: '/services/vulnerability-assessment/calculate/',
    BULK_CALCULATE: '/services/vulnerability-assessment/bulk_calculate/',
    VULNERABILITY_STATISTICS: '/services/vulnerability-assessment/statistics/',
    
    // Éligibilité programmes
    ELIGIBILITY: '/services/program-eligibility/',
    CHECK_PROGRAM_ELIGIBILITY: '/services/program-eligibility/check/',
    
    // Géotargeting
    GEOTARGETING: '/services/geotargeting/',
    PRIORITY_ZONES: '/services/geotargeting/priority_zones/',
    
    // Budget programmes
    PROGRAM_BUDGETS: '/services/social-programs/',
    BUDGET_DASHBOARD: '/services/social-programs/budget_dashboard/',
    BUDGET_HISTORY: (id) => `/services/social-programs/${id}/budget_history/`,
  },

  // ==================== CORE (UTILISATEURS & AUDIT) ====================
  CORE: {
    // Utilisateurs
    USERS: '/core/users/',
    USER_DETAIL: (id) => `/core/users/${id}/`,
    CURRENT_USER: '/core/users/me/',
    UPDATE_PROFILE: '/core/users/update_profile/',
    CHANGE_PASSWORD: '/core/users/change_password/',
    
    // Audit logs
    AUDIT_LOGS: '/core/audit-logs/',
    AUDIT_STATS: '/core/audit-logs/stats/',
    USER_ACTIVITY: (userId) => `/core/audit-logs/user_activity/?user=${userId}`,
  },
};

export default ENDPOINTS;