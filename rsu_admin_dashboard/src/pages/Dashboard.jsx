/**
 * 🇬🇦 RSU Gabon - Dashboard Principal CORRIGÉ
 * Standards Top 1% - Intégration APIs Django REST
 * Fichier: rsu_admin_dashboard/src/pages/Dashboard.jsx
 */

import React, { useState, useCallback } from 'react';
import Header from '../components/Layout/Header';
import TabNavigation from '../components/Dashboard/TabNavigation';
import OverviewTab from '../components/Dashboard/OverviewTab'; // ✅ IMPORT DU BON COMPOSANT
import BeneficiariesTab from '../components/Dashboard/BeneficiariesTab';
import ProgramsTab from '../components/Dashboard/ProgramsTab';
import { AlertCircle, CheckCircle } from 'lucide-react';
import { useDashboard, useBeneficiaries } from '../hooks/useDashboard';
import { usePrograms } from '../hooks/usePrograms';
import apiClient from '../services/api/apiClient';

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const [currentUser] = useState(() => apiClient.getCurrentUser() || {
    username: 'admin',
    user_type: 'ADMIN'
  });

  // ================================================================================
  // HOOKS DE DONNÉES
  // ================================================================================

  const {
    data: dashboardData,
    loading: dashboardLoading,
    error: dashboardError,
    refresh: refreshDashboard,
    lastUpdate
  } = useDashboard();

  const {
    beneficiaries,
    loading: beneficiariesLoading,
    error: beneficiariesError,
    pagination: beneficiariesPagination,
    refresh: refreshBeneficiaries,
  } = useBeneficiaries();

  const {
    programs,
    loading: programsLoading,
    error: programsError,
    refresh: refreshPrograms,
  } = usePrograms();

  // ================================================================================
  // HANDLERS
  // ================================================================================

  const handleSearch = useCallback((params) => {
    console.log(`🔍 Recherche dans l'onglet ${activeTab} avec:`, params);
  }, [activeTab]);

  const handleExport = useCallback(async () => {
    console.log('📥 Export des données...');
  }, []);

  const getCurrentRefresh = () => {
    switch (activeTab) {
      case 'overview':
        return refreshDashboard;
      case 'beneficiaries':
        return refreshBeneficiaries;
      case 'programs':
        return refreshPrograms;
      default:
        return () => console.log('No refresh action for this tab.');
    }
  };

  const getCurrentLoading = dashboardLoading || beneficiariesLoading || programsLoading;

  // ================================================================================
  // GESTION ERREUR GLOBALE
  // ================================================================================

  if (dashboardError && !dashboardLoading && activeTab === 'overview') {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full text-center">
          <AlertCircle className="text-red-600 mx-auto mb-4" size={64} />
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Erreur de Connexion</h2>
          <p className="text-gray-600 mb-4">
            {typeof dashboardError === 'string' ? dashboardError : "Une erreur inattendue est survenue."}
          </p>
          <div className="space-y-2">
            <button
              onClick={refreshDashboard}
              className="w-full px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Réessayer
            </button>
            <p className="text-xs text-gray-500">
              Vérifiez que le backend Django est démarré sur {process.env.REACT_APP_API_URL || 'http://localhost:8000'}
            </p>
          </div>
        </div>
      </div>
    );
  }

  // ================================================================================
  // RENDU PRINCIPAL
  // ================================================================================

  return (
    <div className="min-h-screen bg-gray-100">
      <Header 
        currentUser={currentUser}
        onRefresh={getCurrentRefresh()}
        loading={getCurrentLoading}
      />

      <TabNavigation 
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Indicateur mise à jour */}
        {lastUpdate && activeTab === 'overview' && (
          <div className="mb-4 flex items-center justify-between bg-blue-50 border border-blue-200 rounded-lg p-3">
            <div className="flex items-center gap-2">
              <CheckCircle size={18} className="text-blue-600" />
              <span className="text-sm text-blue-800">
                Données actualisées : {lastUpdate.toLocaleTimeString('fr-FR')}
              </span>
            </div>
            <span className="text-xs text-blue-600 font-mono">
              Backend: {process.env.REACT_APP_API_URL || 'http://localhost:8000'}
            </span>
          </div>
        )}

        {/* ✅ ONGLET VUE D'ENSEMBLE - CORRECTION ICI */}
        {activeTab === 'overview' && (
          <OverviewTab 
            data={dashboardData}
            loading={dashboardLoading}
            error={dashboardError}
          />
        )}

        {/* ✅ ONGLET BÉNÉFICIAIRES */}
        {activeTab === 'beneficiaries' && (
          <BeneficiariesTab />
        )}

        {/* ✅ ONGLET PROGRAMMES */}
        {activeTab === 'programs' && (
          <ProgramsTab />
        )}

        {/* ✅ ONGLET ANALYTICS */}
        {activeTab === 'analytics' && (
          <div className="bg-white rounded-lg shadow-md p-8 text-center">
            <h3 className="text-xl font-bold text-gray-800 mb-2">
              🤖 Module Analytics IA
            </h3>
            <p className="text-gray-600">
              Fonctionnalités avancées d'analyse prédictive en développement
            </p>
          </div>
        )}
      </main>
    </div>
  );
}