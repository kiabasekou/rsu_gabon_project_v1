const ENDPOINTS = {
  // Analytics
  ANALYTICS: {
    DASHBOARD: '/analytics/dashboard/',
    PROVINCE_STATS: '/analytics/province-stats/',
    REPORTS: '/analytics/reports/',
  },

  // Identity
  IDENTITY: {
    PERSONS: '/identity/persons/',
    PERSON_DETAIL: (id) => `/identity/persons/${id}/`,
    SEARCH: '/identity/persons/search/',
    HOUSEHOLDS: '/identity/households/',
  },

  // Services
  SERVICES: {
    VULNERABILITY: '/services/vulnerability-assessment/',
    STATISTICS: '/services/vulnerability-assessment/statistics/',
  },
};

export default ENDPOINTS;