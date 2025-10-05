// =============================================================================
// 3. OFFLINE STORAGE SERVICE (services/offline/storageService.js)
// =============================================================================
import AsyncStorage from '@react-native-async-storage/async-storage';
import { v4 as uuidv4 } from 'uuid';

class OfflineStorageService {
  QUEUE_KEY = 'rsu_sync_queue';
  DRAFTS_KEY = 'rsu_drafts';

  // Ajouter à la queue de synchronisation
  async addToQueue(action, data) {
    try {
      const queue = await this.getQueue();
      const item = {
        id: uuidv4(),
        action, // 'CREATE_PERSON', 'UPDATE_HOUSEHOLD', etc.
        data,
        timestamp: new Date().toISOString(),
        retries: 0,
        status: 'pending', // pending, syncing, failed, synced
      };

      queue.push(item);
      await AsyncStorage.setItem(this.QUEUE_KEY, JSON.stringify(queue));
      return item;
    } catch (error) {
      console.error('Erreur ajout queue:', error);
      throw error;
    }
  }

  // Récupérer la queue
  async getQueue() {
    try {
      const queueJson = await AsyncStorage.getItem(this.QUEUE_KEY);
      return queueJson ? JSON.parse(queueJson) : [];
    } catch (error) {
      return [];
    }
  }

  // Marquer item comme synchronisé
  async markAsSynced(itemId) {
    const queue = await this.getQueue();
    const updatedQueue = queue.filter((item) => item.id !== itemId);
    await AsyncStorage.setItem(this.QUEUE_KEY, JSON.stringify(updatedQueue));
  }

  // Marquer item comme échoué
  async markAsFailed(itemId, error) {
    const queue = await this.getQueue();
    const updatedQueue = queue.map((item) =>
      item.id === itemId
        ? { ...item, status: 'failed', error, retries: item.retries + 1 }
        : item
    );
    await AsyncStorage.setItem(this.QUEUE_KEY, JSON.stringify(updatedQueue));
  }

  // Sauvegarder brouillon
  async saveDraft(type, data) {
    const drafts = await this.getDrafts();
    const draft = {
      id: uuidv4(),
      type,
      data,
      savedAt: new Date().toISOString(),
    };
    drafts.push(draft);
    await AsyncStorage.setItem(this.DRAFTS_KEY, JSON.stringify(drafts));
    return draft;
  }

  // Récupérer brouillons
  async getDrafts() {
    const draftsJson = await AsyncStorage.getItem(this.DRAFTS_KEY);
    return draftsJson ? JSON.parse(draftsJson) : [];
  }

  // Supprimer brouillon
  async deleteDraft(draftId) {
    const drafts = await this.getDrafts();
    const updatedDrafts = drafts.filter((d) => d.id !== draftId);
    await AsyncStorage.setItem(this.DRAFTS_KEY, JSON.stringify(updatedDrafts));
  }

  // Vider toutes les données offline
  async clearAll() {
    await AsyncStorage.multiRemove([this.QUEUE_KEY, this.DRAFTS_KEY]);
  }
}

export default new OfflineStorageService();
