/**
 * 🇬🇦 RSU Gabon - Dashboard Principal
 * Standards Top 1% - Intégration APIs Django REST
 * Fichier: rsu_admin_dashboard/src/pages/Dashboard.jsx
 */

import React, { useState, useCallback } from 'react'; // Importer useCallback pour les handlers
import Header from '../components/Layout/Header';
import TabNavigation from '../components/Dashboard/TabNavigation';
import OverviewTab from '../components/Dashboard/OverviewTab';
import BeneficiariesTab from '../components/Dashboard/BeneficiariesTab';
import ProgramsTab from '../components/Dashboard/ProgramsTab'; // ✅ Import OK
import { AlertCircle, CheckCircle } from 'lucide-react';
import { useDashboard, useBeneficiaries } from '../hooks/useDashboard';
import { usePrograms } from '../hooks/usePrograms'; // ✅ Import OK
import apiClient from '../services/api/apiClient';


export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  // NOTE: Utiliser `useMemo` pour initialiser `currentUser` si la valeur est complexe ou
  // dépend de props/state, mais ici un simple `useState` avec une fonction d'initialisation
  // est acceptable pour un appel unique.
  const [currentUser] = useState(() => apiClient.getCurrentUser() || {
    username: 'admin',
    user_type: 'ADMIN'
  });

  // ================================================================================
  // HOOKS DE DONNÉES
  // ================================================================================

  // ✅ Hook pour le tableau de bord (résumé global)
  const {
    data: dashboardData,
    loading: dashboardLoading,
    error: dashboardError,
    refresh: refreshDashboard,
    lastUpdate
  } = useDashboard();

  // ✅ Hook pour la liste des bénéficiaires
  const {
    beneficiaries,
    loading: beneficiariesLoading,
    error: beneficiariesError, // Maintenir l'erreur pour la vue spécifique
    pagination: beneficiariesPagination,
    refresh: refreshBeneficiaries,
    setFilter: setBeneficiariesFilter // Ajout hypothétique pour la recherche
  } = useBeneficiaries();

  // 💡 NOUVEAU : Hook pour la liste des programmes
  const {
    programs,
    loading: programsLoading,
    error: programsError, // Maintenir l'erreur pour la vue spécifique
    pagination: programsPagination,
    refresh: refreshPrograms,
    setFilter: setProgramsFilter // Ajout hypothétique pour la recherche
  } = usePrograms();


  // ================================================================================
  // HANDLERS GLOBALES
  // ================================================================================

  /**
   * Gère la recherche globale/spécifique à l'onglet actif.
   * @param {Object} params - Paramètres de recherche/filtrage
   */
  const handleSearch = useCallback((params) => {
    console.log(`🔍 Recherche dans l'onglet ${activeTab} avec:`, params);
    
    // Dispatcher la recherche au hook approprié
    if (activeTab === 'beneficiaries' && setBeneficiariesFilter) {
      setBeneficiariesFilter(params);
    } else if (activeTab === 'programs' && setProgramsFilter) {
      setProgramsFilter(params);
    }
    // else: TODO: Implémenter la recherche API pour les autres onglets si nécessaire.
    
  }, [activeTab, setBeneficiariesFilter, setProgramsFilter]);


  const handleExport = useCallback(async () => {
    console.log('📥 Export des données...');
    // TODO: Implémenter export CSV/Excel pour l'onglet actif
  }, []);

  // Détermine la fonction de rafraîchissement et l'état de chargement en fonction de l'onglet
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
  // NOTE: On vérifie l'erreur la plus critique (Dashboard principal) pour le grand écran d'erreur

  // ================================================================================
  // RENDU D'ERREUR CRITIQUE (Dashboard principal)
  // ================================================================================

  if (dashboardError && !dashboardLoading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full text-center">
          <AlertCircle className="text-red-600 mx-auto mb-4" size={64} />
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Erreur de Connexion</h2>
          {/* Afficher l'erreur spécifique si elle est une chaîne, sinon un message générique */}
          <p className="text-gray-600 mb-4">{typeof dashboardError === 'string' ? dashboardError : "Une erreur inattendue est survenue lors du chargement."}</p>
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

  // Console log de débogage (peut être retiré en production)
  // console.log('📊 Dashboard state:');
  // console.log('   activeTab:', activeTab);
  // console.log('   programs:', programs);
  // console.log('   programs.length:', programs?.length);
  // console.log('   programsLoading:', programsLoading);

  // ================================================================================
  // RENDU PRINCIPAL
  // ================================================================================

  return (
    <div className="min-h-screen bg-gray-100">
      <Header 
        currentUser={currentUser}
        // Utiliser la fonction dynamique de rafraîchissement
        onRefresh={getCurrentRefresh()}
        loading={getCurrentLoading}
      />

      <TabNavigation 
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Indicateur de dernière mise à jour (Afficher uniquement si la vue principale a chargé) */}
        {lastUpdate && (
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

        {activeTab === 'overview' && (
          <OverviewTab 
            data={dashboardData} 
            loading={dashboardLoading}
            // L'erreur spécifique est gérée ici
            error={dashboardError} 
          />
        )}

        {activeTab === 'beneficiaries' && (
          <BeneficiariesTab
            beneficiaries={beneficiaries}
            loading={beneficiariesLoading}
            pagination={beneficiariesPagination}
            onSearch={handleSearch} // Utiliser le handler mis à jour
            onExport={handleExport}
            error={beneficiariesError} // Afficher l'erreur dans l'onglet
          />
        )}
        {activeTab === 'programs' && (
          <ProgramsTab />
        )}

        {/* 💡 NOUVEAU : Intégration de l'onglet ProgramsTab */}
        {activeTab === 'programs' && (
          <ProgramsTab
            programs={programs}
            loading={programsLoading}
            pagination={programsPagination}
            onSearch={handleSearch} // Utiliser le handler mis à jour
            onExport={handleExport}
            error={programsError} // Afficher l'erreur dans l'onglet
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