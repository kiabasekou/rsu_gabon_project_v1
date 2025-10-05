import React, { useState, useEffect } from 'react';
import Header from '../components/Layout/Header';
import TabNavigation from '../components/Dashboard/TabNavigation';
import OverviewTab from '../components/Dashboard/OverviewTab';
import BeneficiariesTab from '../components/Dashboard/BeneficiariesTab';
import { Activity, AlertCircle } from 'lucide-react';

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dashboardData, setDashboardData] = useState(null);
  const [currentUser] = useState({
    username: 'admin',
    user_type: 'ADMIN'
  });

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    setError(null);

    try {
      await new Promise(resolve => setTimeout(resolve, 800));
      
      setDashboardData({
        stats: {
          total_beneficiaries: 45820,
          total_households: 12450,
          active_programs: 8,
          avg_vulnerability_score: 42.3,
          beneficiaries_growth: '+12.5% ce mois',
          households_growth: '+8.3% ce mois',
        }
      });
      
      setLoading(false);
    } catch (err) {
      setError('Erreur de connexion au backend Django');
      setLoading(false);
    }
  };

  const handleSearch = (params) => {
    console.log('Recherche avec paramètres:', params);
  };

  const handleExport = () => {
    console.log('Export des données');
  };

  if (error && !loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full text-center">
          <AlertCircle className="text-red-600 mx-auto mb-4" size={64} />
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Erreur</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={loadDashboardData}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Réessayer
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <Header 
        currentUser={currentUser}
        onRefresh={loadDashboardData}
        loading={loading}
      />

      <TabNavigation 
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'overview' && (
          <OverviewTab 
            data={dashboardData}
            loading={loading}
          />
        )}
        
        {activeTab === 'beneficiaries' && (
          <BeneficiariesTab 
            loading={loading}
            onSearch={handleSearch}
            onExport={handleExport}
          />
        )}
        
        {activeTab === 'analytics' && (
          <div className="bg-white rounded-lg shadow-md p-8 text-center">
            <Activity className="text-blue-600 mx-auto mb-4" size={64} />
            <h3 className="text-xl font-bold text-gray-800 mb-2">
              Analytics IA Avancées
            </h3>
            <p className="text-gray-600 mb-4">
              Scoring vulnérabilité • Prédictions éligibilité • ML insights
            </p>
            <div className="text-sm text-gray-500">
              📡 Endpoints: /services/vulnerability-assessment/statistics/
            </div>
          </div>
        )}
      </main>

      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-center text-sm text-gray-500">
            RSU Gabon © 2025 - Dashboard Admin Modulaire • Django REST Framework • Standards Top 1%
          </p>
        </div>
      </footer>
    </div>
  );
}