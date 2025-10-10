/**
 * 🇬🇦 RSU Gabon - Dashboard Principal
 * Standards Top 1% - Intégration APIs Django REST
 * Fichier: rsu_admin_dashboard/src/pages/Dashboard.jsx
 */

import React, { useState } from 'react';
import Header from '../components/Layout/Header';
import TabNavigation from '../components/Dashboard/TabNavigation';
import OverviewTab from '../components/Dashboard/OverviewTab';
import BeneficiariesTab from '../components/Dashboard/BeneficiariesTab';
import ProgramsTab from '../components/Dashboard/ProgramsTab';  // ← AJOUTER
import { AlertCircle, CheckCircle } from 'lucide-react';
import { useDashboard, useBeneficiaries } from '../hooks/useDashboard';
import { usePrograms } from '../hooks/usePrograms';  // ← AJOUTER
import apiClient from '../services/api/apiClient';

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const [currentUser] = useState(() => apiClient.getCurrentUser() || {
    username: 'admin',
    user_type: 'ADMIN'
  });

  // ✅ Hook connecté aux vraies APIs
  const {
    data: dashboardData,
    loading: dashboardLoading,
    error: dashboardError,
    refresh: refreshDashboard,
    lastUpdate
  } = useDashboard();

  // ✅ Hook pour bénéficiaires
  const {
    beneficiaries,
    loading: beneficiariesLoading,
    error: beneficiariesError,
    pagination,
    refresh: refreshBeneficiaries
  } = useBeneficiaries();

  const handleSearch = (params) => {
    console.log('🔍 Recherche avec paramètres:', params);
    // TODO: Implémenter recherche API
  };

  const handleExport = async () => {
    console.log('📥 Export des données...');
    // TODO: Implémenter export CSV/Excel
  };

  // Gestion erreur
  if (dashboardError && !dashboardLoading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full text-center">
          <AlertCircle className="text-red-600 mx-auto mb-4" size={64} />
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Erreur de Connexion</h2>
          <p className="text-gray-600 mb-4">{dashboardError}</p>
          <div className="space-y-2">
            <button
              onClick={refreshDashboard}
              className="w-full px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Réessayer
            </button>
            <p className="text-xs text-gray-500">
              Vérifiez que le backend Django est démarré sur http://localhost:8000
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Dans Dashboard.jsx, juste avant le return
console.log('📊 Dashboard state:');
console.log('   activeTab:', activeTab);
console.log('   programs:', programs);
console.log('   programs.length:', programs?.length);
console.log('   programsLoading:', programsLoading);

  return (
    <div className="min-h-screen bg-gray-100">
      <Header 
        currentUser={currentUser}
        onRefresh={activeTab === 'overview' ? refreshDashboard : refreshBeneficiaries}
        loading={dashboardLoading || beneficiariesLoading}
      />

      <TabNavigation 
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Indicateur de dernière mise à jour */}
        {lastUpdate && (
          <div className="mb-4 flex items-center justify-between bg-blue-50 border border-blue-200 rounded-lg p-3">
            <div className="flex items-center gap-2">
              <CheckCircle size={18} className="text-blue-600" />
              <span className="text-sm text-blue-800">
                Données actualisées : {lastUpdate.toLocaleTimeString('fr-FR')}
              </span>
            </div>
            <span className="text-xs text-blue-600 font-mono">
              Backend: {process.env.REACT_APP_API_URL}
            </span>
          </div>
        )}

        {activeTab === 'overview' && (
          <OverviewTab 
            data={dashboardData} 
            loading={dashboardLoading}
          />
        )}

        {activeTab === 'beneficiaries' && (
          <BeneficiariesTab
            beneficiaries={beneficiaries}
            loading={beneficiariesLoading}
            pagination={pagination}
            onSearch={handleSearch}
            onExport={handleExport}
          />
        )}

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