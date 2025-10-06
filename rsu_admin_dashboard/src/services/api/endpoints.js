/**
 * 🇬🇦 RSU Gabon - API Endpoints
 * Standards Top 1% - Configuration centralisée
 * Fichier: rsu_admin_dashboard/src/services/api/endpoints.js
 */

const ENDPOINTS = {
  // Authentification
  AUTH: {
    TOKEN: '/auth/token/',
    REFRESH: '/auth/token/refresh/',
    LOGOUT: '/auth/logout/',
  },

  // Analytics (Dashboard)
  ANALYTICS: {
    DASHBOARD: '/analytics/dashboard/',
    PROVINCE_STATS: '/analytics/province-stats/',
    REPORTS: '/analytics/reports/',
  },

  // Identity (Bénéficiaires)
  IDENTITY: {
    PERSONS: '/identity/persons/',
    PERSON_DETAIL: (id) => `/identity/persons/${id}/`,
    SEARCH: '/identity/persons/search/',
    CHECK_DUPLICATES: '/identity/persons/check-duplicates/',
    STATISTICS: '/identity/persons/statistics/',
    
    HOUSEHOLDS: '/identity/households/',
    HOUSEHOLD_DETAIL: (id) => `/identity/households/${id}/`,
    HOUSEHOLD_STATS: '/identity/households/statistics/',
    
    GEOGRAPHIC_DATA: '/identity/geographic-data/',
  },

  // Services (Vulnérabilité)
  SERVICES: {
    VULNERABILITY: '/services/vulnerability-assessment/',
    VULNERABILITY_DETAIL: (id) => `/services/vulnerability-assessment/${id}/`,
    CALCULATE_SCORE: '/services/vulnerability-assessment/calculate/',
    STATISTICS: '/services/vulnerability-assessment/statistics/',
  },

  // Core (Utilisateurs & Audit)
  CORE: {
    USERS: '/core/users/',
    USER_DETAIL: (id) => `/core/users/${id}/`,
    CURRENT_USER: '/core/users/me/',
    
    AUDIT_LOGS: '/core/audit-logs/',
    AUDIT_STATS: '/core/audit-logs/stats/',
  },
};

export default ENDPOINTS;