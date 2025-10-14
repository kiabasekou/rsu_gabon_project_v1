// =============================================================================
// RSU GABON - APPLICATION MOBILE COLLECTE TERRAIN
// Fichier: rsu-mobile-surveyor/App.jsx
// =============================================================================

import React, { useEffect, useState } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Provider as PaperProvider, MD3DarkTheme } from 'react-native-paper';
import Icon from 'react-native-vector-icons/MaterialIcons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';
import * as Sentry from '@sentry/react-native';

// Services
import authService from './src/services/auth/authService';
import syncService from './src/services/sync/syncService';

// Screens
import LoginScreen from './src/screens/Auth/LoginScreen';
import DashboardScreen from './src/screens/Dashboard/DashboardScreen';
import EnrollmentFormScreen from './src/screens/Enrollment/EnrollmentFormScreen';
import PersonListScreen from './src/screens/Person/PersonListScreen';
import PersonDetailScreen from './src/screens/Person/PersonDetailScreen';
import SurveyFormScreen from './src/screens/Survey/SurveyFormScreen';
import OfflineQueueScreen from './src/screens/Sync/OfflineQueueScreen';
import ProfileScreen from './src/screens/Profile/ProfileScreen';

// Configuration Sentry (monitoring erreurs production)
Sentry.init({
  dsn: 'YOUR_SENTRY_DSN', // À configurer
  environment: __DEV__ ? 'development' : 'production',
});

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

// Thème personnalisé RSU Gabon
const theme = {
  ...MD3DarkTheme,
  colors: {
    ...MD3DarkTheme.colors,
    primary: '#2E7D32', // Vert drapeau Gabon
    secondary: '#FFB300', // Jaune drapeau Gabon
    tertiary: '#1976D2', // Bleu gouvernemental
    surface: '#1E1E1E',
    background: '#121212',
    onPrimary: '#FFFFFF',
  },
};

// Navigation principale avec tabs
function MainTabs() {
  const [offlineCount, setOfflineCount] = useState(0);

  useEffect(() => {
    // Surveiller queue offline
    const checkOfflineQueue = async () => {
      const count = await syncService.getPendingCount();
      setOfflineCount(count);
    };
    
    checkOfflineQueue();
    const interval = setInterval(checkOfflineQueue, 30000); // Check every 30s
    
    return () => clearInterval(interval);
  }, []);

  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;

          switch (route.name) {
            case 'Dashboard':
              iconName = 'dashboard';
              break;
            case 'Enrollment':
              iconName = 'person-add';
              break;
            case 'Persons':
              iconName = 'people';
              break;
            case 'Surveys':
              iconName = 'assignment';
              break;
            case 'Sync':
              iconName = 'sync';
              break;
            default:
              iconName = 'help';
          }

          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: theme.colors.primary,
        tabBarInactiveTintColor: '#666',
        tabBarStyle: {
          backgroundColor: theme.colors.surface,
        },
        headerStyle: {
          backgroundColor: theme.colors.primary,
        },
        headerTintColor: '#fff',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      })}
    >
      <Tab.Screen 
        name="Dashboard" 
        component={DashboardScreen}
        options={{
          title: '🏠 Tableau de Bord',
          headerTitle: 'RSU Gabon - Enquêteur',
        }}
      />
      
      <Tab.Screen 
        name="Enrollment" 
        component={EnrollmentFormScreen}
        options={{
          title: '➕ Inscription',
          headerTitle: 'Nouvelle Inscription',
        }}
      />
      
      <Tab.Screen 
        name="Persons" 
        component={PersonListScreen}
        options={{
          title: '👥 Personnes',
          headerTitle: 'Liste des Personnes',
        }}
      />
      
      <Tab.Screen 
        name="Surveys" 
        component={SurveyFormScreen}
        options={{
          title: '📋 Enquêtes',
          headerTitle: 'Enquêtes Terrain',
        }}
      />
      
      <Tab.Screen 
        name="Sync" 
        component={OfflineQueueScreen}
        options={{
          title: offlineCount > 0 ? `🔄 Sync (${offlineCount})` : '🔄 Sync',
          headerTitle: 'Synchronisation',
          tabBarBadge: offlineCount > 0 ? offlineCount : undefined,
        }}
      />
    </Tab.Navigator>
  );
}

// Navigation Stack principale
function AppNavigator() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerStyle: {
          backgroundColor: theme.colors.primary,
        },
        headerTintColor: '#fff',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      }}
    >
      <Stack.Screen 
        name="Main" 
        component={MainTabs}
        options={{ headerShown: false }}
      />
      
      <Stack.Screen 
        name="PersonDetail" 
        component={PersonDetailScreen}
        options={{
          title: 'Détail Personne',
          presentation: 'modal',
        }}
      />
      
      <Stack.Screen 
        name="Profile" 
        component={ProfileScreen}
        options={{
          title: 'Mon Profil',
          presentation: 'modal',
        }}
      />
    </Stack.Navigator>
  );
}

// Application principale
export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [networkStatus, setNetworkStatus] = useState(true);

  useEffect(() => {
    // Vérifier authentification au démarrage
    checkAuthStatus();
    
    // Surveiller connexion réseau
    const unsubscribe = NetInfo.addEventListener(state => {
      setNetworkStatus(state.isConnected);
      
      // Tentative de sync automatique quand connexion restaurée
      if (state.isConnected) {
        syncService.syncPendingData();
      }
    });

    return () => unsubscribe();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const authenticated = await authService.isAuthenticated();
      setIsAuthenticated(authenticated);
    } catch (error) {
      console.error('Erreur vérification auth:', error);
      Sentry.captureException(error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogin = (success) => {
    if (success) {
      setIsAuthenticated(true);
    }
  };

  const handleLogout = async () => {
    await authService.logout();
    setIsAuthenticated(false);
  };

  if (isLoading) {
    return (
      <PaperProvider theme={theme}>
        <NavigationContainer>
          <Stack.Navigator>
            <Stack.Screen 
              name="Loading" 
              component={() => (
                <div style={{
                  flex: 1,
                  justifyContent: 'center',
                  alignItems: 'center',
                  backgroundColor: theme.colors.background
                }}>
                  <Icon name="sync" size={50} color={theme.colors.primary} />
                  <text style={{ color: theme.colors.onBackground, marginTop: 16 }}>
                    Chargement RSU Gabon...
                  </text>
                </div>
              )}
              options={{ headerShown: false }}
            />
          </Stack.Navigator>
        </NavigationContainer>
      </PaperProvider>
    );
  }

  return (
    <PaperProvider theme={theme}>
      <NavigationContainer>
        {isAuthenticated ? (
          <AppNavigator />
        ) : (
          <Stack.Navigator>
            <Stack.Screen 
              name="Login" 
              options={{ headerShown: false }}
            >
              {props => <LoginScreen {...props} onLogin={handleLogin} />}
            </Stack.Screen>
          </Stack.Navigator>
        )}
      </NavigationContainer>
    </PaperProvider>
  );
}// Navigation principale 
