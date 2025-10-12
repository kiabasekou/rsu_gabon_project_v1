/**
 * 🇬🇦 RSU Gabon - Dashboard Principal FUSIONNÉ
 * Standards Top 1% - Fichier: rsu_admin_dashboard/src/pages/Dashboard.jsx
 */

import React, { useState, useCallback } from 'react';
import Header from '../components/Layout/Header';
import TabNavigation from '../components/Dashboard/TabNavigation';
// OverviewTab n'est plus importé car il est défini localement
import BeneficiariesTab from '../components/Dashboard/BeneficiariesTab';
import ProgramsTab from '../components/Dashboard/ProgramsTab';
import { AlertCircle, CheckCircle, BarChart, PieChart, LineChart, RefreshCw } from 'lucide-react';
import { useDashboard, useBeneficiaries } from '../hooks/useDashboard';
import apiClient from '../services/api/apiClient';

// ================================================================================
// 1. COMPOSANTS HELPER (StatCard et VulnCard)
// ================================================================================

function StatCard({ title, value, icon, color }) {
  const colors = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    purple: 'bg-purple-100 text-purple-600',
    orange: 'bg-orange-100 text-orange-600'
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-500 text-sm">{title}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
        </div>
        <div className={`p-3 rounded-full ${colors[color]}`}>
          {icon}
        </div>
      </div>
    </div>
  );
}

function VulnCard({ level, count, color }) {
  const colors = {
    red: 'bg-red-100 text-red-800 border-red-300',
    orange: 'bg-orange-100 text-orange-800 border-orange-300',
    yellow: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    green: 'bg-green-100 text-green-800 border-green-300'
  };

  return (
    <div className={`p-4 rounded-lg border-2 ${colors[color]}`}>
      <p className="text-sm font-medium">{level}</p>
      <p className="text-3xl font-bold mt-1">{count}</p>
    </div>
  );
}

// ================================================================================
// 2. COMPOSANT OVERVIEW TAB (Fusionné)
// ================================================================================

function OverviewTab({ data, loading, error, onRefresh }) {
  if (loading) {
    return (
      <div className="flex items-center justify-center h-48 bg-white rounded-lg shadow">
        <p className="text-lg text-gray-600">Chargement des données du tableau de bord...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-8 bg-white rounded-lg shadow text-center">
        <AlertCircle className="text-red-500 mx-auto mb-4" size={30} />
        <p className="text-lg text-red-700">Impossible d'afficher l'aperçu: {error?.message || "Données manquantes."}</p>
        <button 
          onClick={onRefresh}
          className="mt-4 px-4 py-2 text-sm bg-gray-200 rounded hover:bg-gray-300 flex items-center mx-auto"
        >
          <RefreshCw size={16} className="mr-2" /> Réessayer
        </button>
      </div>
    );
  }

  // Utilisation des données du hook useDashboard
  const { overview, vulnerability, geographic } = data;
  
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">Aperçu Général des Données RSU</h1>
      
      {/* Statistiques Générales */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard 
          title="Total Personnes" 
          value={overview?.total_persons?.toLocaleString('fr-FR') || 0}
          icon={<BarChart />}
          color="blue"
        />
        <StatCard 
          title="Total Ménages" 
          value={overview?.total_households?.toLocaleString('fr-FR') || 0}
          icon={<PieChart />}
          color="green"
        />
        <StatCard 
          title="Taux Vérification" 
          value={`${overview?.verification_rate?.toFixed(1) || 0}%`}
          icon={<LineChart />}
          color="purple"
        />
        <StatCard 
          title="Complétude Moyenne" 
          value={`${overview?.avg_completeness?.toFixed(1) || 0}%`}
          icon={<BarChart />}
          color="orange"
        />
      </div>

      {/* Vulnérabilité */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Répartition Vulnérabilité</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <VulnCard level="Critique" count={vulnerability?.distribution?.CRITICAL?.toLocaleString('fr-FR') || 0} color="red" />
          <VulnCard level="Élevé" count={vulnerability?.distribution?.HIGH?.toLocaleString('fr-FR') || 0} color="orange" />
          <VulnCard level="Modéré" count={vulnerability?.distribution?.MODERATE?.toLocaleString('fr-FR') || 0} color="yellow" />
          <VulnCard level="Faible" count={vulnerability?.distribution?.LOW?.toLocaleString('fr-FR') || 0} color="green" />
        </div>
      </div>

      {/* Distribution Géographique */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Distribution par Province</h2>
        <div className="space-y-2">
          {geographic?.by_province?.map(prov => (
            <div key={prov.province} className="flex justify-between items-center p-3 bg-gray-50 rounded">
              <span className="font-medium">{prov.province}</span>
              <span className="text-gray-600">{prov.count?.toLocaleString('fr-FR') || 0} personnes</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}


// ================================================================================
// 3. COMPOSANT PRINCIPAL (Dashboard)
// ================================================================================

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  
  // Récupération de l'utilisateur
  const currentUser = apiClient.getCurrentUser() || {
    username: 'admin',
    user_type: 'ADMIN'
  };

  // HOOKS DE DONNÉES
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
    refresh: refreshBeneficiaries
  } = useBeneficiaries();

  // HANDLERS
  const handleSearch = useCallback((query) => {
    console.log('🔍 Search query:', query);
    if (activeTab === 'beneficiaries') {
      // Passer la query au hook pour filtrer
      refreshBeneficiaries({ query }); 
    }
  }, [activeTab, refreshBeneficiaries]);

  const handleExport = useCallback(() => {
    console.log('📥 Export requested for tab:', activeTab);
  }, [activeTab]);

  const handleRefresh = useCallback(() => {
    if (activeTab === 'overview') {
      refreshDashboard();
    } else if (activeTab === 'beneficiaries') {
      refreshBeneficiaries(); 
    }
  }, [activeTab, refreshDashboard, refreshBeneficiaries]);

  // GESTION ERREURS GLOBALES
  const hasError = dashboardError || beneficiariesError;
  const errorMessage = (dashboardError || beneficiariesError)?.toString() || "Une erreur inconnue est survenue.";

  // RENDER
  return (
    <div className="min-h-screen bg-gray-50">
      <Header user={currentUser} onRefresh={handleRefresh} />

      {/* Messages globaux */}
      {hasError && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-4">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
            <AlertCircle className="text-red-600 mt-0.5 flex-shrink-0" size={20} />
            <div>
              <h4 className="font-semibold text-red-800">Erreur de chargement</h4>
              <p className="text-sm text-red-700 mt-1">{errorMessage}</p>
            </div>
          </div>
        </div>
      )}

      {lastUpdate && activeTab === 'overview' && !hasError && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-4">
          <div className="bg-green-50 border border-green-200 rounded-lg p-3 flex items-center gap-3">
            <CheckCircle className="text-green-600 flex-shrink-0" size={18} />
            <p className="text-sm text-green-700">
              Dernière mise à jour du tableau de bord : {lastUpdate.toLocaleTimeString('fr-FR')}
            </p>
          </div>
        </div>
      )}

      {/* Navigation par onglets */}
      <TabNavigation activeTab={activeTab} onTabChange={setActiveTab} />

      {/* Contenu principal */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'overview' && (
          // Utilise le composant OverviewTab défini localement
          <OverviewTab
            data={dashboardData}
            loading={dashboardLoading}
            error={dashboardError} 
            onRefresh={refreshDashboard}
          />
        )}

        {activeTab === 'beneficiaries' && (
          <BeneficiariesTab
            beneficiaries={beneficiaries}
            loading={beneficiariesLoading}
            pagination={beneficiariesPagination}
            onSearch={handleSearch}
            onExport={handleExport}
            error={beneficiariesError}
            onPageChange={refreshBeneficiaries}
          />
        )}

        {activeTab === 'programs' && <ProgramsTab />}

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