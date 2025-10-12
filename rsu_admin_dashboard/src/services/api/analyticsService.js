import apiClient from './apiClient';

class AnalyticsService {
  /**
   * Récupérer dashboard complet
   */
  async getDashboard() {
    return apiClient.get('/services/analytics/dashboard/');
  }

  /**
   * Statistiques vulnérabilité
   */
  async getVulnerabilityStats() {
    return apiClient.get('/services/analytics/vulnerability-stats/');
  }

  /**
   * Distribution géographique
   */
  async getGeographicDistribution() {
    return apiClient.get('/services/analytics/geographic-distribution/');
  }

  /**
   * Insights démographiques
   */
  async getDemographicInsights() {
    return apiClient.get('/services/analytics/demographic-insights/');
  }

  /**
   * Calculer évaluation vulnérabilité
   */
  async calculateVulnerability(personId, forceRecalculate = false) {
    return apiClient.post('/services/vulnerability-assessments/calculate/', {
      person_id: personId,
      force_recalculate: forceRecalculate
    });
  }

  /**
   * Liste évaluations vulnérabilité
   */
  async getVulnerabilityAssessments(params = {}) {
    return apiClient.get('/services/vulnerability-assessments/', params);
  }

  /**
   * Cas critiques
   */
  async getCriticalCases() {
    return apiClient.get('/services/vulnerability-assessments/critical-cases/');
  }
}

export default new AnalyticsService();