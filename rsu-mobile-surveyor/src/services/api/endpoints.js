const ENDPOINTS = {
  // Authentification
  AUTH: {
    LOGIN: '/auth/token/',
    REFRESH: '/auth/token/refresh/',
    LOGOUT: '/auth/logout/',
    PROFILE: '/auth/profile/',
  },

  // Identity App
  IDENTITY: {
    PERSONS: '/identity/persons/',
    PERSON_DETAIL: (id) => `/identity/persons/${id}/`,
    CHECK_DUPLICATES: '/identity/persons/check-duplicates/',
    SEARCH: '/identity/persons/search/',
    
    HOUSEHOLDS: '/identity/households/',
    HOUSEHOLD_DETAIL: (id) => `/identity/households/${id}/`,
    
    GEOGRAPHIC_DATA: '/identity/geographic-data/',
    
    RBPP_SYNC: '/identity/rbpp-sync/',
  },

  // Services App
  SERVICES: {
    VULNERABILITY_ASSESSMENT: '/services/vulnerability-assessment/',
    CALCULATE_SCORE: '/services/vulnerability-assessment/calculate/',
    STATISTICS: '/services/vulnerability-assessment/statistics/',
  },

  // Analytics
  ANALYTICS: {
    DASHBOARD: '/analytics/dashboard/',
    PROVINCE_STATS: '/analytics/province-stats/',
    REPORTS: '/analytics/reports/',
  },

  // Media
  MEDIA: {
    UPLOAD: '/media/upload/',
    DOWNLOAD: (filename) => `/media/download/${filename}/`,
  },
};

export default ENDPOINTS;