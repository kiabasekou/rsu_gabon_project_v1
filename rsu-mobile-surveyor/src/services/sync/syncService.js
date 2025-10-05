// =============================================================================
// 4. SYNC SERVICE (services/sync/syncService.js)
// =============================================================================
import NetInfo from '@react-native-community/netinfo';
import apiClient from '../api/apiClient';
import offlineStorage from '../offline/storageService';

class SyncService {
  constructor() {
    this.isSyncing = false;
    this.listeners = [];
  }

  // Vérifier connexion
  async checkConnectivity() {
    const state = await NetInfo.fetch();
    return state.isConnected;
  }

  // Synchroniser queue complète
  async syncAll() {
    if (this.isSyncing) {
      console.log('Synchronisation déjà en cours');
      return;
    }

    const isOnline = await this.checkConnectivity();
    if (!isOnline) {
      throw new Error('Pas de connexion Internet');
    }

    this.isSyncing = true;
    this.notifyListeners({ status: 'started' });

    const queue = await offlineStorage.getQueue();
    const results = {
      total: queue.length,
      synced: 0,
      failed: 0,
      errors: [],
    };

    for (const item of queue) {
      try {
        await this.syncItem(item);
        await offlineStorage.markAsSynced(item.id);
        results.synced++;
        this.notifyListeners({
          status: 'progress',
          current: results.synced + results.failed,
          total: results.total,
        });
      } catch (error) {
        await offlineStorage.markAsFailed(item.id, error.message);
        results.failed++;
        results.errors.push({ item, error: error.message });
      }
    }

    this.isSyncing = false;
    this.notifyListeners({ status: 'completed', results });
    return results;
  }

  // Synchroniser un item individuel
  async syncItem(item) {
    const { action, data } = item;

    switch (action) {
      case 'CREATE_PERSON':
        return await apiClient.post('/identity/persons/', data);

      case 'UPDATE_PERSON':
        return await apiClient.patch(`/identity/persons/${data.id}/`, data);

      case 'CREATE_HOUSEHOLD':
        return await apiClient.post('/identity/households/', data);

      case 'UPDATE_HOUSEHOLD':
        return await apiClient.patch(`/identity/households/${data.id}/`, data);

      case 'UPLOAD_PHOTO':
        const formData = new FormData();
        formData.append('file', {
          uri: data.uri,
          type: data.type,
          name: data.name,
        });
        return await apiClient.upload('/media/upload/', formData);

      default:
        throw new Error(`Action inconnue: ${action}`);
    }
  }

  // Ajouter écouteur événements sync
  addListener(callback) {
    this.listeners.push(callback);
    return () => {
      this.listeners = this.listeners.filter((l) => l !== callback);
    };
  }

  // Notifier tous les écouteurs
  notifyListeners(event) {
    this.listeners.forEach((listener) => listener(event));
  }

  // Auto-sync quand connexion rétablie
  setupAutoSync() {
    NetInfo.addEventListener((state) => {
      if (state.isConnected && !this.isSyncing) {
        offlineStorage.getQueue().then((queue) => {
          if (queue.length > 0) {
            console.log(`Auto-sync: ${queue.length} items en attente`);
            this.syncAll().catch(console.error);
          }
        });
      }
    });
  }
}

export default new SyncService();