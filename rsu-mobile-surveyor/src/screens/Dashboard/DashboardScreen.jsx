// =============================================================================
// 1. DASHBOARD SCREEN (screens/Dashboard/DashboardScreen.jsx)
// =============================================================================
import React, { useState, useEffect } from 'react';
import {
  View,
  ScrollView,
  RefreshControl,
  StyleSheet,
} from 'react-native';
import {
  Card,
  Title,
  Paragraph,
  Button,
  Avatar,
  Chip,
  List,
  Divider,
  ProgressBar,
} from 'react-native-paper';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';

import authService from '../../services/auth/authService';
import syncService from '../../services/sync/syncService';
import apiClient from '../../services/api/apiClient';

export default function DashboardScreen({ navigation }) {
  const [user, setUser] = useState(null);
  const [stats, setStats] = useState({
    todayEnrollments: 0,
    totalEnrollments: 0,
    pendingSync: 0,
    lastSync: null,
  });
  const [recentActivity, setRecentActivity] = useState([]);
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      // Charger utilisateur actuel
      const currentUser = await authService.getCurrentUser();
      setUser(currentUser);

      // Charger statistiques
      await loadStats();
      
      // Charger activité récente
      await loadRecentActivity();
    } catch (error) {
      console.error('Erreur chargement dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      // Statistiques locales (offline)
      const pendingCount = await syncService.getPendingCount();
      
      // Tentative récupération stats serveur
      try {
        const response = await apiClient.get('/dashboard/surveyor-stats/');
        setStats({
          todayEnrollments: response.data.today_enrollments || 0,
          totalEnrollments: response.data.total_enrollments || 0,
          pendingSync: pendingCount,
          lastSync: response.data.last_sync || null,
        });
      } catch {
        // Fallback stats locales
        setStats(prev => ({
          ...prev,
          pendingSync: pendingCount,
        }));
      }
    } catch (error) {
      console.error('Erreur stats:', error);
    }
  };

  const loadRecentActivity = async () => {
    try {
      // Charger données depuis cache local ou serveur
      const pendingData = await syncService.getPendingData();
      const recentItems = pendingData
        .slice(-5)
        .reverse()
        .map(item => ({
          id: item.id,
          type: item.type,
          title: item.type === 'enrollment' 
            ? `${item.data.person.firstName} ${item.data.person.lastName}`
            : item.type,
          subtitle: format(new Date(item.timestamp), 'dd/MM/yyyy HH:mm', { locale: fr }),
          status: item.status,
        }));
      
      setRecentActivity(recentItems);
    } catch (error) {
      console.error('Erreur activité récente:', error);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
  };

  const handleSync = async () => {
    try {
      const result = await syncService.syncPendingData();
      await loadStats(); // Recharger stats après sync
      
      if (result.success > 0) {
        // Afficher notification de succès
      }
    } catch (error) {
      console.error('Erreur synchronisation:', error);
    }
  };

  if (loading && !user) {
    return (
      <View style={styles.loadingContainer}>
        <Avatar.Icon size={64} icon="loading" />
        <Paragraph>Chargement...</Paragraph>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.contentContainer}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
      }
    >
      {/* En-tête utilisateur */}
      <Card style={styles.userCard}>
        <Card.Content style={styles.userContent}>
          <Avatar.Icon
            size={60}
            icon="account-circle"
            style={styles.avatar}
          />
          <View style={styles.userInfo}>
            <Title style={styles.userName}>
              {user?.first_name} {user?.last_name}
            </Title>
            <Paragraph style={styles.userRole}>
              Enquêteur Terrain • {user?.province || 'Toutes provinces'}
            </Paragraph>
            <Paragraph style={styles.userEmail}>
              {user?.email}
            </Paragraph>
          </View>
        </Card.Content>
      </Card>

      {/* Statistiques rapides */}
      <View style={styles.statsContainer}>
        <Card style={styles.statCard}>
          <Card.Content style={styles.statContent}>
            <Icon name="today" size={32} color="#2E7D32" />
            <Title style={styles.statNumber}>{stats.todayEnrollments}</Title>
            <Paragraph style={styles.statLabel}>Aujourd'hui</Paragraph>
          </Card.Content>
        </Card>

        <Card style={styles.statCard}>
          <Card.Content style={styles.statContent}>
            <Icon name="people" size={32} color="#1976D2" />
            <Title style={styles.statNumber}>{stats.totalEnrollments}</Title>
            <Paragraph style={styles.statLabel}>Total</Paragraph>
          </Card.Content>
        </Card>

        <Card style={styles.statCard}>
          <Card.Content style={styles.statContent}>
            <Icon name="sync" size={32} color={stats.pendingSync > 0 ? '#FF9800' : '#4CAF50'} />
            <Title style={styles.statNumber}>{stats.pendingSync}</Title>
            <Paragraph style={styles.statLabel}>En attente</Paragraph>
          </Card.Content>
        </Card>
      </View>

      {/* Synchronisation */}
      {stats.pendingSync > 0 && (
        <Card style={styles.syncCard}>
          <Card.Content>
            <View style={styles.syncHeader}>
              <Icon name="cloud-upload" size={24} color="#FF9800" />
              <Title style={styles.syncTitle}>
                Synchronisation requise
              </Title>
            </View>
            <Paragraph style={styles.syncDescription}>
              {stats.pendingSync} éléments en attente de synchronisation avec le serveur RSU.
            </Paragraph>
            <Button
              mode="contained"
              onPress={handleSync}
              style={styles.syncButton}
              icon="sync"
            >
              Synchroniser maintenant
            </Button>
          </Card.Content>
        </Card>
      )}

      {/* Actions rapides */}
      <Card style={styles.actionsCard}>
        <Card.Content>
          <Title style={styles.actionsTitle}>Actions rapides</Title>
          
          <View style={styles.actionsList}>
            <Button
              mode="contained"
              onPress={() => navigation.navigate('Enrollment')}
              style={styles.actionButton}
              contentStyle={styles.actionButtonContent}
              icon="person-add"
            >
              Nouvelle Inscription
            </Button>

            <Button
              mode="outlined"
              onPress={() => navigation.navigate('Persons')}
              style={styles.actionButton}
              contentStyle={styles.actionButtonContent}
              icon="people"
            >
              Consulter Personnes
            </Button>

            <Button
              mode="outlined"
              onPress={() => navigation.navigate('Surveys')}
              style={styles.actionButton}
              contentStyle={styles.actionButtonContent}
              icon="assignment"
            >
              Enquêtes Terrain
            </Button>

            <Button
              mode="outlined"
              onPress={() => navigation.navigate('Sync')}
              style={styles.actionButton}
              contentStyle={styles.actionButtonContent}
              icon="sync"
            >
              Synchronisation
            </Button>
          </View>
        </Card.Content>
      </Card>

      {/* Activité récente */}
      <Card style={styles.activityCard}>
        <Card.Content>
          <Title style={styles.activityTitle}>Activité récente</Title>
          
          {recentActivity.length === 0 ? (
            <Paragraph style={styles.noActivity}>
              Aucune activité récente
            </Paragraph>
          ) : (
            recentActivity.map((item, index) => (
              <View key={item.id}>
                <List.Item
                  title={item.title}
                  description={item.subtitle}
                  left={() => (
                    <Avatar.Icon
                      size={40}
                      icon={item.type === 'enrollment' ? 'person-add' : 'assignment'}
                      style={styles.activityIcon}
                    />
                  )}
                  right={() => (
                    <Chip
                      mode="outlined"
                      style={[
                        styles.statusChip,
                        item.status === 'synced' && styles.syncedChip,
                        item.status === 'failed' && styles.failedChip,
                      ]}
                    >
                      {item.status === 'pending' ? 'En attente' :
                       item.status === 'synced' ? 'Synchronisé' : 'Échec'}
                    </Chip>
                  )}
                />
                {index < recentActivity.length - 1 && <Divider />}
              </View>
            ))
          )}
        </Card.Content>
      </Card>

      {/* Informations système */}
      <Card style={styles.systemCard}>
        <Card.Content>
          <Title style={styles.systemTitle}>Informations système</Title>
          
          <View style={styles.systemInfo}>
            <Paragraph>
              <Icon name="info" size={16} /> Version: 1.0.0
            </Paragraph>
            <Paragraph>
              <Icon name="schedule" /> Dernière sync: {
                stats.lastSync
                  ? format(new Date(stats.lastSync), 'dd/MM/yyyy HH:mm', { locale: fr })
                  : 'Jamais'
              }
            </Paragraph>
            <Paragraph>
              <Icon name="storage" /> Stockage local: {stats.pendingSync} éléments
            </Paragraph>
          </View>
        </Card.Content>
      </Card>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  contentContainer: {
    padding: 16,
    paddingBottom: 100,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  userCard: {
    marginBottom: 16,
    elevation: 4,
  },
  userContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  avatar: {
    backgroundColor: '#2E7D32',
    marginRight: 16,
  },
  userInfo: {
    flex: 1,
  },
  userName: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  userRole: {
    color: '#666',
    marginBottom: 2,
  },
  userEmail: {
    fontSize: 12,
    color: '#888',
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  statCard: {
    flex: 1,
    marginHorizontal: 4,
    elevation: 2,
  },
  statContent: {
    alignItems: 'center',
    paddingVertical: 16,
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    marginVertical: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
  syncCard: {
    marginBottom: 16,
    backgroundColor: '#FFF8E1',
    elevation: 3,
  },
  syncHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  syncTitle: {
    marginLeft: 8,
    fontSize: 16,
    color: '#F57F17',
  },
  syncDescription: {
    marginBottom: 12,
    color: '#666',
  },
  syncButton: {
    backgroundColor: '#FF9800',
  },
  actionsCard: {
    marginBottom: 16,
    elevation: 3,
  },
  actionsTitle: {
    marginBottom: 16,
  },
  actionsList: {
    gap: 12,
  },
  actionButton: {
    marginBottom: 8,
  },
  actionButtonContent: {
    paddingVertical: 8,
  },
  activityCard: {
    marginBottom: 16,
    elevation: 2,
  },
  activityTitle: {
    marginBottom: 12,
  },
  noActivity: {
    textAlign: 'center',
    color: '#666',
    fontStyle: 'italic',
    paddingVertical: 20,
  },
  activityIcon: {
    backgroundColor: '#E3F2FD',
  },
  statusChip: {
    marginTop: 8,
  },
  syncedChip: {
    backgroundColor: '#E8F5E8',
  },
  failedChip: {
    backgroundColor: '#FFEBEE',
  },
  systemCard: {
    marginBottom: 16,
    elevation: 1,
  },
  systemTitle: {
    fontSize: 16,
    marginBottom: 12,
  },
  systemInfo: {
    gap: 4,
  },
});
