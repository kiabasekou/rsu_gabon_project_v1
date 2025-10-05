// =============================================================================
// 5. BENEFICIARY SERVICE (services/beneficiary/beneficiaryService.js)
// =============================================================================
import apiClient from '../api/apiClient';
import offlineStorage from '../offline/storageService';

class BeneficiaryService {
  // Créer nouvelle personne
  async createPerson(personData, isOnline = true) {
    if (isOnline) {
      try {
        const response = await apiClient.post('/identity/persons/', personData);
        return { success: true, data: response.data };
      } catch (error) {
        // Si échec, sauvegarder offline
        await offlineStorage.addToQueue('CREATE_PERSON', personData);
        return {
          success: true,
          offline: true,
          message: 'Enregistré localement, sera synchronisé',
        };
      }
    } else {
      // Mode offline direct
      await offlineStorage.addToQueue('CREATE_PERSON', personData);
      return {
        success: true,
        offline: true,
        message: 'Enregistré localement',
      };
    }
  }

  // Rechercher personnes
  async searchPersons(query, filters = {}) {
    const params = {
      search: query,
      ...filters,
    };
    const response = await apiClient.get('/identity/persons/', params);
    return response.data;
  }

  // Obtenir détails personne
  async getPersonById(id) {
    const response = await apiClient.get(`/identity/persons/${id}/`);
    return response.data;
  }

  // Vérifier doublons (déduplication)
  async checkDuplicates(personData) {
    const response = await apiClient.post(
      '/identity/persons/check-duplicates/',
      personData
    );
    return response.data;
  }

  // Calculer score vulnérabilité
  async calculateVulnerabilityScore(personId) {
    const response = await apiClient.post(
      `/services/vulnerability-assessment/calculate/`,
      { person_id: personId }
    );
    return response.data;
  }

  // Obtenir statistiques
  async getStats(province = null) {
    const params = province ? { province } : {};
    const response = await apiClient.get('/analytics/dashboard/', params);
    return response.data;
  }
}

export default new BeneficiaryService();


