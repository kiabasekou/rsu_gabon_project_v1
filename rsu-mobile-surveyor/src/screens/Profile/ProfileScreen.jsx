// =============================================================================
// 3. PROFILE SCREEN (screens/Profile/ProfileScreen.jsx)
// =============================================================================
import React, { useState, useEffect } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  Alert,
} from 'react-native';
import {
  Card,
  Title,
  Paragraph,
  Button,
  TextInput,
  Avatar,
  List,
  Divider,
  Switch,
  Chip,
  Surface,
} from 'react-native-paper';
import { Formik } from 'formik';
import * as Yup from 'yup';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';

import authService from '../../services/auth/authService';
import apiClient from '../../services/api/apiClient';
import syncService from '../../services/sync/syncService';
import { GABON_PROVINCES } from '../../constants/gabonData';

const ProfileSchema = Yup.object().shape({
  first_name: Yup.string()
    .min(2, 'Prénom trop court')
    .required('Prénom requis'),
  last_name: Yup.string()
    .min(2, 'Nom trop court')
    .required('Nom requis'),
  email: Yup.string()
    .email('Email invalide')
    .required('Email requis'),
  phone: Yup.string()
    .matches(/^(\+241|241)?[0-9]{8}$/, 'Format téléphone gabonais invalide'),
});

const PasswordSchema = Yup.object().shape({
  current_password: Yup.string()
    .required('Mot de passe actuel requis'),
  new_password: Yup.string()
    .min(8, 'Minimum 8 caractères')
    .matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/, 'Doit contenir majuscule, minuscule et chiffre')
    .required('Nouveau mot de passe requis'),
  confirm_password: Yup.string()
    .oneOf([Yup.ref('new_password')], 'Mots de passe différents')
    .required('Confirmation requise'),
});

export default function ProfileScreen({ navigation }) {
  const [user, setUser] = useState(null);
  const [stats, setStats] = useState({
    totalEnrollments: 0,
    totalSurveys: 0,
    lastSync: null,
    offlineItems: 0,
  });
  const [settings, setSettings] = useState({
    autoSync: true,
    gpsEnabled: true,
    notifications: true,
    offlineMode: false,
  });
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    loadUserProfile();
    loadUserStats();
    loadSettings();
  }, []);

  const loadUserProfile = async () => {
    try {
      const currentUser = await authService.getCurrentUser();
      if (currentUser) {
        // Charger profil complet depuis API
        const response = await apiClient.get('/core/users/me/');
        setUser(response.data);
      } else {
        setUser(currentUser);
      }
    } catch (error) {
      console.error('Erreur chargement profil:', error);
      // Fallback vers données locales
      const currentUser = await authService.getCurrentUser();
      setUser(currentUser);
    } finally {
      setLoading(false);
    }
  };

  const loadUserStats = async () => {
    try {
      // Stats depuis API
      const response = await apiClient.get('/dashboard/surveyor-stats/');
      setStats(prevStats => ({
        ...prevStats,
        totalEnrollments: response.data.total_enrollments || 0,
        totalSurveys: response.data.total_surveys || 0,
        lastSync: response.data.last_sync,
      }));
    } catch (error) {
      console.error('Erreur stats:', error);
    }

    // Stats locales
    try {
      const offlineCount = await syncService.getPendingCount();
      setStats(prevStats => ({
        ...prevStats,
        offlineItems: offlineCount,
      }));
    } catch (error) {
      console.error('Erreur stats locales:', error);
    }
  };

  const loadSettings = () => {
    // Charger paramètres depuis AsyncStorage ou défauts
    // TODO: Implémenter persistance settings
  };

  const handleProfileUpdate = async (values) => {
    setUpdating(true);
    try {
      const response = await apiClient.patch('/core/users/me/', values);
      setUser(response.data);
      
      // Mettre à jour stockage local
      await authService.updateUserInfo(response.data);
      
      Alert.alert('Succès', 'Profil mis à jour avec succès');
    } catch (error) {
      Alert.alert('Erreur', 'Impossible de mettre à jour le profil');
      console.error('Erreur update profil:', error);
    } finally {
      setUpdating(false);
    }
  };

  const handlePasswordChange = async (values) => {
    setUpdating(true);
    try {
      await apiClient.post('/core/users/change_password/', {
        old_password: values.current_password,
        new_password: values.new_password,
      });
      
      Alert.alert('Succès', 'Mot de passe modifié avec succès');
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Erreur lors du changement de mot de passe';
      Alert.alert('Erreur', errorMsg);
    } finally {
      setUpdating(false);
    }
  };

  const handleLogout = async () => {
    Alert.alert(
      'Déconnexion',
      'Êtes-vous sûr de vouloir vous déconnecter ?',
      [
        { text: 'Annuler', style: 'cancel' },
        {
          text: 'Déconnexion',
          style: 'destructive',
          onPress: async () => {
            try {
              await authService.logout();
              navigation.reset({
                index: 0,
                routes: [{ name: 'Login' }],
              });
            } catch (error) {
              console.error('Erreur déconnexion:', error);
            }
          }
        }
      ]
    );
  };

  const handleSyncNow = async () => {
    try {
      const result = await syncService.syncPendingData();
      Alert.alert(
        'Synchronisation',
        `✅ ${result.success} réussies\n❌ ${result.failed} échecs`
      );
      loadUserStats();
    } catch (error) {
      Alert.alert('Erreur', 'Synchronisation échouée');
    }
  };

  const handleSettingChange = (key, value) => {
    setSettings(prev => ({
      ...prev,
      [key]: value,
    }));
    // TODO: Persister dans AsyncStorage
  };

  if (loading || !user) {
    return (
      <View style={styles.loadingContainer}>
        <Avatar.Icon size={64} icon="loading" />
        <Paragraph>Chargement du profil...</Paragraph>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      {/* En-tête profil */}
      <Card style={styles.headerCard}>
        <Card.Content>
          <View style={styles.headerContent}>
            <Avatar.Text
              size={80}
              label={`${user.first_name[0]}${user.last_name[0]}`}
              style={styles.avatar}
            />
            <View style={styles.userInfo}>
              <Title style={styles.userName}>
                {user.first_name} {user.last_name}
              </Title>
              <Paragraph style={styles.userRole}>
                {user.user_type === 'SURVEYOR' ? 'Enquêteur Terrain' :
                 user.user_type === 'SUPERVISOR' ? 'Superviseur' : 'Administrateur'}
              </Paragraph>
              <Paragraph style={styles.userEmail}>
                {user.email}
              </Paragraph>
              <View style={styles.userTags}>
                <Chip mode="outlined" style={styles.statusChip}>
                  {user.is_active ? 'Actif' : 'Inactif'}
                </Chip>
                {user.employee_id && (
                  <Chip mode="outlined" style={styles.idChip}>
                    ID: {user.employee_id}
                  </Chip>
                )}
              </View>
            </View>
          </View>
        </Card.Content>
      </Card>

      {/* Statistiques activité */}
      <Card style={styles.statsCard}>
        <Card.Content>
          <Title style={styles.sectionTitle}>📊 Statistiques d'activité</Title>
          
          <View style={styles.statsGrid}>
            <View style={styles.statItem}>
              <Icon name="person-add" size={32} color="#2E7D32" />
              <View style={styles.statInfo}>
                <Title style={styles.statValue}>{stats.totalEnrollments}</Title>
                <Paragraph style={styles.statLabel}>Inscriptions</Paragraph>
              </View>
            </View>
            
            <View style={styles.statItem}>
              <Icon name="assignment" size={32} color="#1976D2" />
              <View style={styles.statInfo}>
                <Title style={styles.statValue}>{stats.totalSurveys}</Title>
                <Paragraph style={styles.statLabel}>Enquêtes</Paragraph>
              </View>
            </View>
            
            <View style={styles.statItem}>
              <Icon name="sync" size={32} color={stats.offlineItems > 0 ? "#FF9800" : "#4CAF50"} />
              <View style={styles.statInfo}>
                <Title style={styles.statValue}>{stats.offlineItems}</Title>
                <Paragraph style={styles.statLabel}>En attente</Paragraph>
              </View>
            </View>
          </View>
          
          {stats.lastSync && (
            <Paragraph style={styles.lastSync}>
              Dernière synchronisation: {format(
                new Date(stats.lastSync),
                'dd/MM/yyyy HH:mm',
                { locale: fr }
              )}
            </Paragraph>
          )}
          
          {stats.offlineItems > 0 && (
            <Button
              mode="contained"
              onPress={handleSyncNow}
              style={styles.syncButton}
              icon="sync"
            >
              Synchroniser maintenant ({stats.offlineItems})
            </Button>
          )}
        </Card.Content>
      </Card>

      {/* Informations personnelles */}
      <Card style={styles.sectionCard}>
        <Card.Content>
          <Title style={styles.sectionTitle}>👤 Informations personnelles</Title>
          
          <Formik
            initialValues={{
              first_name: user.first_name || '',
              last_name: user.last_name || '',
              email: user.email || '',
              phone: user.phone || '',
            }}
            validationSchema={ProfileSchema}
            onSubmit={handleProfileUpdate}
          >
            {({ handleChange, handleBlur, handleSubmit, values, errors, touched }) => (
              <View>
                <TextInput
                  label="Prénom"
                  value={values.first_name}
                  onChangeText={handleChange('first_name')}
                  onBlur={handleBlur('first_name')}
                  error={touched.first_name && errors.first_name}
                  style={styles.input}
                  mode="outlined"
                />
                
                <TextInput
                  label="Nom"
                  value={values.last_name}
                  onChangeText={handleChange('last_name')}
                  onBlur={handleBlur('last_name')}
                  error={touched.last_name && errors.last_name}
                  style={styles.input}
                  mode="outlined"
                />
                
                <TextInput
                  label="Email"
                  value={values.email}
                  onChangeText={handleChange('email')}
                  onBlur={handleBlur('email')}
                  error={touched.email && errors.email}
                  style={styles.input}
                  mode="outlined"
                  keyboardType="email-address"
                  autoCapitalize="none"
                />
                
                <TextInput
                  label="Téléphone"
                  value={values.phone}
                  onChangeText={handleChange('phone')}
                  onBlur={handleBlur('phone')}
                  error={touched.phone && errors.phone}
                  style={styles.input}
                  mode="outlined"
                  keyboardType="phone-pad"
                  placeholder="+241 XX XX XX XX"
                />
                
                <Button
                  mode="contained"
                  onPress={handleSubmit}
                  loading={updating}
                  disabled={updating}
                  style={styles.updateButton}
                  icon="check"
                >
                  Mettre à jour le profil
                </Button>
              </View>
            )}
          </Formik>
        </Card.Content>
      </Card>

      {/* Changement mot de passe */}
      <Card style={styles.sectionCard}>
        <Card.Content>
          <Title style={styles.sectionTitle}>🔒 Sécurité</Title>
          
          <Formik
            initialValues={{
              current_password: '',
              new_password: '',
              confirm_password: '',
            }}
            validationSchema={PasswordSchema}
            onSubmit={(values, { resetForm }) => {
              handlePasswordChange(values).then(() => {
                resetForm();
              });
            }}
          >
            {({ handleChange, handleBlur, handleSubmit, values, errors, touched }) => (
              <View>
                <TextInput
                  label="Mot de passe actuel"
                  value={values.current_password}
                  onChangeText={handleChange('current_password')}
                  onBlur={handleBlur('current_password')}
                  error={touched.current_password && errors.current_password}
                  style={styles.input}
                  mode="outlined"
                  secureTextEntry
                />
                
                <TextInput
                  label="Nouveau mot de passe"
                  value={values.new_password}
                  onChangeText={handleChange('new_password')}
                  onBlur={handleBlur('new_password')}
                  error={touched.new_password && errors.new_password}
                  style={styles.input}
                  mode="outlined"
                  secureTextEntry
                />
                
                <TextInput
                  label="Confirmer nouveau mot de passe"
                  value={values.confirm_password}
                  onChangeText={handleChange('confirm_password')}
                  onBlur={handleBlur('confirm_password')}
                  error={touched.confirm_password && errors.confirm_password}
                  style={styles.input}
                  mode="outlined"
                  secureTextEntry
                />
                
                <Button
                  mode="outlined"
                  onPress={handleSubmit}
                  loading={updating}
                  disabled={updating}
                  style={styles.passwordButton}
                  icon="lock-reset"
                >
                  Changer le mot de passe
                </Button>
              </View>
            )}
          </Formik>
        </Card.Content>
      </Card>

      {/* Paramètres application */}
      <Card style={styles.sectionCard}>
        <Card.Content>
          <Title style={styles.sectionTitle}>⚙️ Paramètres</Title>
          
          <List.Item
            title="Synchronisation automatique"
            description="Synchroniser automatiquement quand en ligne"
            left={() => <Icon name="sync" size={24} color="#2E7D32" />}
            right={() => (
              <Switch
                value={settings.autoSync}
                onValueChange={(value) => handleSettingChange('autoSync', value)}
              />
            )}
          />
          <Divider />
          
          <List.Item
            title="GPS activé"
            description="Permettre la capture de position GPS"
            left={() => <Icon name="location-on" size={24} color="#2E7D32" />}
            right={() => (
              <Switch
                value={settings.gpsEnabled}
                onValueChange={(value) => handleSettingChange('gpsEnabled', value)}
              />
            )}
          />
          <Divider />
          
          <List.Item
            title="Notifications"
            description="Recevoir des notifications push"
            left={() => <Icon name="notifications" size={24} color="#2E7D32" />}
            right={() => (
              <Switch
                value={settings.notifications}
                onValueChange={(value) => handleSettingChange('notifications', value)}
              />
            )}
          />
          <Divider />
          
          <List.Item
            title="Mode hors ligne"
            description="Privilégier le fonctionnement offline"
            left={() => <Icon name="offline-bolt" size={24} color="#FF9800" />}
            right={() => (
              <Switch
                value={settings.offlineMode}
                onValueChange={(value) => handleSettingChange('offlineMode', value)}
              />
            )}
          />
        </Card.Content>
      </Card>

      {/* Informations système */}
      <Card style={styles.sectionCard}>
        <Card.Content>
          <Title style={styles.sectionTitle}>ℹ️ Informations</Title>
          
          <View style={styles.infoList}>
            <View style={styles.infoItem}>
              <Paragraph style={styles.infoLabel}>Version application</Paragraph>
              <Paragraph style={styles.infoValue}>1.0.0</Paragraph>
            </View>
            
            <View style={styles.infoItem}>
              <Paragraph style={styles.infoLabel}>Département</Paragraph>
              <Paragraph style={styles.infoValue}>
                {user.department || 'Non assigné'}
              </Paragraph>
            </View>
            
            <View style={styles.infoItem}>
              <Paragraph style={styles.infoLabel}>Provinces assignées</Paragraph>
              <View style={styles.provincesContainer}>
                {user.assigned_provinces && user.assigned_provinces.length > 0 ? (
                  user.assigned_provinces.map(province => (
                    <Chip key={province} mode="outlined" style={styles.provinceChip}>
                      {GABON_PROVINCES[province]?.name || province}
                    </Chip>
                  ))
                ) : (
                  <Paragraph style={styles.infoValue}>Toutes provinces</Paragraph>
                )}
              </View>
            </View>
            
            <View style={styles.infoItem}>
              <Paragraph style={styles.infoLabel}>Date création compte</Paragraph>
              <Paragraph style={styles.infoValue}>
                {format(new Date(user.date_joined), 'dd MMMM yyyy', { locale: fr })}
              </Paragraph>
            </View>
          </View>
        </Card.Content>
      </Card>

      {/* Actions rapides */}
      <Card style={styles.sectionCard}>
        <Card.Content>
          <Title style={styles.sectionTitle}>🔧 Actions</Title>
          
          <View style={styles.actionsList}>
            <Button
              mode="outlined"
              onPress={() => navigation.navigate('Sync')}
              style={styles.actionButton}
              icon="sync"
            >
              Gestion synchronisation
            </Button>
            
            <Button
              mode="outlined"
              onPress={() => {
                Alert.alert(
                  'Support technique',
                  'Pour toute assistance, contactez:\n\nEmail: support-rsu@gouv.ga\nTél: +241 XX XX XX XX'
                );
              }}
              style={styles.actionButton}
              icon="help"
            >
              Support technique
            </Button>
            
            <Button
              mode="outlined"
              onPress={() => {
                Alert.alert(
                  'À propos',
                  'RSU Gabon - Enquêteur Mobile\nVersion 1.0.0\n\nMinistère de l\'Économie\nRépublique Gabonaise\n\nFinancé par la Banque Mondiale'
                );
              }}
              style={styles.actionButton}
              icon="info"
            >
              À propos
            </Button>
          </View>
        </Card.Content>
      </Card>

      {/* Déconnexion */}
      <Card style={styles.logoutCard}>
        <Card.Content>
          <Button
            mode="contained"
            onPress={handleLogout}
            style={styles.logoutButton}
            buttonColor="#F44336"
            icon="logout"
          >
            Se déconnecter
          </Button>
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
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  headerCard: {
    margin: 16,
    marginBottom: 12,
    elevation: 4,
  },
  headerContent: {
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
    fontSize: 22,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  userRole: {
    color: '#666',
    fontSize: 16,
    marginBottom: 2,
  },
  userEmail: {
    color: '#888',
    fontSize: 14,
    marginBottom: 8,
  },
  userTags: {
    flexDirection: 'row',
    gap: 8,
  },
  statusChip: {
    backgroundColor: '#E8F5E8',
  },
  idChip: {
    backgroundColor: '#E3F2FD',
  },
  statsCard: {
    marginHorizontal: 16,
    marginBottom: 12,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  statsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 16,
  },
  statItem: {
    alignItems: 'center',
    flex: 1,
  },
  statInfo: {
    alignItems: 'center',
    marginTop: 8,
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
  lastSync: {
    textAlign: 'center',
    fontSize: 12,
    color: '#666',
    marginBottom: 12,
  },
  syncButton: {
    alignSelf: 'center',
  },
  sectionCard: {
    marginHorizontal: 16,
    marginBottom: 12,
    elevation: 2,
  },
  input: {
    marginBottom: 12,
  },
  updateButton: {
    marginTop: 8,
  },
  passwordButton: {
    marginTop: 8,
  },
  infoList: {
    gap: 16,
  },
  infoItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  infoLabel: {
    fontWeight: 'bold',
    flex: 1,
    color: '#333',
  },
  infoValue: {
    flex: 1,
    textAlign: 'right',
    color: '#666',
  },
  provincesContainer: {
    flex: 1,
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'flex-end',
    gap: 4,
  },
  provinceChip: {
    marginBottom: 4,
  },
  actionsList: {
    gap: 12,
  },
  actionButton: {
    marginBottom: 8,
  },
  logoutCard: {
    margin: 16,
    marginBottom: 100,
    elevation: 2,
  },
  logoutButton: {
    paddingVertical: 4,
  },
});