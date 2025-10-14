// =============================================================================
// ÉCRANS MOBILE RSU GABON
// =============================================================================



// =============================================================================
// 3. OFFLINE QUEUE SCREEN (screens/Sync/OfflineQueueScreen.jsx)
// =============================================================================
import React, { useState, useEffect } from 'react';
import {
  View,
  FlatList,
  StyleSheet,
  Alert,
} from 'react-native';
import {
  Card,
  Title,
  Paragraph,
  Button,
  Chip,
  Avatar,
  ProgressBar,
  List,
  Divider,
  IconButton,
} from 'react-native-paper';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';
import NetInfo from '@react-native-community/netinfo';

import syncService from '../../services/sync/syncService';

export default function OfflineQueueScreen() {
  const [queueItems, setQueueItems] = useState([]);
  const [networkStatus, setNetworkStatus] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [syncProgress, setSyncProgress] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadQueueData();
    
    // Surveiller connexion réseau
    const unsubscribe = NetInfo.addEventListener(state => {
      setNetworkStatus(state.isConnected);
    });

    return () => unsubscribe();
  }, []);

  const loadQueueData = async () => {
    try {
      const pendingData = await syncService.getPendingData();
      setQueueItems(pendingData);
    } catch (error) {
      console.error('Erreur chargement queue:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSyncAll = async () => {
    if (!networkStatus) {
      Alert.alert(
        'Pas de connexion',
        'Une connexion internet est requise pour synchroniser les données.'
      );
      return;
    }

    setSyncing(true);
    setSyncProgress(0);

    try {
      const result = await syncService.syncPendingData();
      
      Alert.alert(
        'Synchronisation terminée',
        `✅ ${result.success} réussies\n❌ ${result.failed} échecs`,
        [
          {
            text: 'OK',
            onPress: () => loadQueueData()
          }
        ]
      );
    } catch (error) {
      Alert.alert('Erreur', 'Échec de la synchronisation');
    } finally {
      setSyncing(false);
      setSyncProgress(0);
    }
  };

  const handleClearSynced = async () => {
    Alert.alert(
      'Nettoyer les données',
      'Supprimer toutes les données déjà synchronisées ?',
      [
        { text: 'Annuler', style: 'cancel' },
        {
          text: 'Supprimer',
          style: 'destructive',
          onPress: async () => {
            const cleared = await syncService.clearSyncedData();
            Alert.alert('Nettoyage', `${cleared} éléments supprimés`);
            loadQueueData();
          }
        }
      ]
    );
  };

  const renderQueueItem = ({ item, index }) => (
    <Card style={styles.queueCard}>
      <Card.Content>
        <View style={styles.itemHeader}>
          <Avatar.Icon
            size={40}
            icon={item.type === 'enrollment' ? 'person-add' : 'assignment'}
            style={[
              styles.itemIcon,
              item.status === 'synced' && styles.syncedIcon,
              item.status === 'failed' && styles.failedIcon,
            ]}
          />
          
          <View style={styles.itemInfo}>
            <Title style={styles.itemTitle}>
              {item.type === 'enrollment' 
                ? `${item.data.person.firstName} ${item.data.person.lastName}`
                : `Enquête ${item.type}`}
            </Title>
            <Paragraph style={styles.itemDetails}>
              Créé le {format(new Date(item.timestamp), 'dd/MM/yyyy HH:mm', { locale: fr })}
            </Paragraph>
            {item.error && (
              <Paragraph style={styles.itemError}>
                Erreur: {item.error}
              </Paragraph>
            )}
          </View>

          <View style={styles.itemStatus}>
            <Chip
              mode="outlined"
              style={[
                styles.statusChip,
                item.status === 'synced' && styles.syncedChip,
                item.status === 'failed' && styles.failedChip,
                item.status === 'pending' && styles.pendingChip,
              ]}
            >
              {item.status === 'pending' ? 'En attente' :
               item.status === 'synced' ? 'Synchronisé' :
               item.status === 'failed' ? 'Échec' : item.status}
            </Chip>
            
            {item.status === 'failed' && (
              <IconButton
                icon="refresh"
                size={20}
                onPress={() => handleRetryItem(item)}
                style={styles.retryButton}
              />
            )}
          </View>
        </View>
      </Card.Content>
    </Card>
  );

  const handleRetryItem = (item) => {
    Alert.alert(
      'Réessayer',
      'Réessayer la synchronisation de cet élément ?',
      [
        { text: 'Annuler', style: 'cancel' },
        {
          text: 'Réessayer',
          onPress: () => {
            // Logique retry spécifique
            // syncService.retryItem(item.id);
          }
        }
      ]
    );
  };

  const pendingCount = queueItems.filter(item => item.status === 'pending').length;
  const syncedCount = queueItems.filter(item => item.status === 'synced').length;
  const failedCount = queueItems.filter(item => item.status === 'failed').length;

  return (
    <View style={styles.container}>
      {/* En-tête avec statistiques */}
      <Card style={styles.headerCard}>
        <Card.Content>
          <Title style={styles.headerTitle}>File de Synchronisation</Title>
          
          <View style={styles.statsRow}>
            <View style={styles.statItem}>
              <Paragraph style={styles.statNumber}>{pendingCount}</Paragraph>
              <Paragraph style={styles.statLabel}>En attente</Paragraph>
            </View>
            <View style={styles.statItem}>
              <Paragraph style={styles.statNumber}>{syncedCount}</Paragraph>
              <Paragraph style={styles.statLabel}>Synchronisés</Paragraph>
            </View>
            <View style={styles.statItem}>
              <Paragraph style={styles.statNumber}>{failedCount}</Paragraph>
              <Paragraph style={styles.statLabel}>Échecs</Paragraph>
            </View>
          </View>

          <View style={styles.connectionStatus}>
            <Chip
              icon={networkStatus ? 'wifi' : 'wifi-off'}
              style={[
                styles.connectionChip,
                networkStatus ? styles.onlineChip : styles.offlineChip
              ]}
            >
              {networkStatus ? 'En ligne' : 'Hors ligne'}
            </Chip>
          </View>
        </Card.Content>
      </Card>

      {/* Barre de progression sync */}
      {syncing && (
        <Card style={styles.progressCard}>
          <Card.Content>
            <Paragraph>Synchronisation en cours...</Paragraph>
            <ProgressBar
              progress={syncProgress}
              style={styles.progressBar}
              color="#2E7D32"
            />
          </Card.Content>
        </Card>
      )}

      {/* Boutons d'action */}
      <View style={styles.actionsContainer}>
        <Button
          mode="contained"
          onPress={handleSyncAll}
          disabled={!networkStatus || syncing || pendingCount === 0}
          loading={syncing}
          style={styles.actionButton}
          icon="sync"
        >
          Synchroniser tout ({pendingCount})
        </Button>
        
        <Button
          mode="outlined"
          onPress={handleClearSynced}
          disabled={syncedCount === 0}
          style={styles.actionButton}
          icon="delete-sweep"
        >
          Nettoyer ({syncedCount})
        </Button>
      </View>

      {/* Liste des éléments */}
      <FlatList
        data={queueItems}
        renderItem={renderQueueItem}
        keyExtractor={item => item.id}
        contentContainerStyle={styles.listContainer}
        refreshing={loading}
        onRefresh={loadQueueData}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Avatar.Icon size={64} icon="sync" style={styles.emptyIcon} />
            <Paragraph style={styles.emptyText}>
              {loading ? 'Chargement...' : 'Aucune donnée en attente'}
            </Paragraph>
          </View>
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  // Styles combinés pour tous les écrans
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  headerCard: {
    margin: 16,
    elevation: 4,
  },
  headerTitle: {
    textAlign: 'center',
    marginBottom: 16,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 16,
  },
  statItem: {
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
  },
  connectionStatus: {
    alignItems: 'center',
  },
  connectionChip: {
    marginTop: 8,
  },
  onlineChip: {
    backgroundColor: '#E8F5E8',
  },
  offlineChip: {
    backgroundColor: '#FFEBEE',
  },
  progressCard: {
    marginHorizontal: 16,
    marginBottom: 16,
  },
  progressBar: {
    marginTop: 8,
    height: 8,
    borderRadius: 4,
  },
  actionsContainer: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    paddingBottom: 16,
    gap: 12,
  },
  actionButton: {
    flex: 1,
  },
  listContainer: {
    paddingHorizontal: 16,
    paddingBottom: 100,
  },
  queueCard: {
    marginBottom: 12,
    elevation: 2,
  },
  itemHeader: {
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  itemIcon: {
    marginRight: 12,
  },
  syncedIcon: {
    backgroundColor: '#4CAF50',
  },
  failedIcon: {
    backgroundColor: '#F44336',
  },
  itemInfo: {
    flex: 1,
  },
  itemTitle: {
    fontSize: 16,
    marginBottom: 4,
  },
  itemDetails: {
    fontSize: 12,
    color: '#666',
  },
  itemError: {
    fontSize: 12,
    color: '#F44336',
    marginTop: 4,
  },
  itemStatus: {
    alignItems: 'flex-end',
  },
  statusChip: {
    marginBottom: 4,
  },
  syncedChip: {
    backgroundColor: '#E8F5E8',
  },
  failedChip: {
    backgroundColor: '#FFEBEE',
  },
  pendingChip: {
    backgroundColor: '#FFF3E0',
  },
  retryButton: {
    margin: 0,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 50,
  },
  emptyIcon: {
    backgroundColor: '#E0E0E0',
    marginBottom: 16,
  },
  emptyText: {
    textAlign: 'center',
    color: '#666',
  },
});