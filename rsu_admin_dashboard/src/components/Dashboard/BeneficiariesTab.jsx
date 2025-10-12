/**
 * 🇬🇦 RSU Gabon - Onglet Bénéficiaires AMÉLIORÉ
 * Standards Top 1% - Filtres, Export, Pagination
 * Fichier: rsu_admin_dashboard/src/components/Dashboard/BeneficiariesTab.jsx
 */

import React, { useEffect } from 'react';
import { RefreshCw, MapPin, Eye, Edit, AlertTriangle } from 'lucide-react';
import BeneficiariesFilters from './BeneficiariesFilters';
import ExportButton from './ExportButton';
import Pagination from './Pagination';
import { useBeneficiaries } from '../../hooks/useBeneficiaries';
/**
 * Helper: Construire paramètres query
 */
const buildQueryParams = (filters) => {
  const params = {};
  
  if (filters.province) params.province = filters.province;
  if (filters.verification_status) params.verification_status = filters.verification_status;
  if (filters.search) params.search = filters.search;
  if (filters.vulnerability_min) params.vulnerability_score__gte = filters.vulnerability_min;
  if (filters.vulnerability_max) params.vulnerability_score__lte = filters.vulnerability_max;
  
  return params;
};

export default function BeneficiariesTab() {
  const {
    beneficiaries,
    loading,
    error,
    pagination,
    filters,
    applyFilters,
    resetFilters,
    changePage,
    changePageSize,
    refresh,
    loadBeneficiaries,
  } = useBeneficiaries();

  // Chargement initial
  useEffect(() => {
    loadBeneficiaries();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const getStatusBadge = (status) => {
    const styles = {
      'VERIFIED': 'bg-green-100 text-green-800',
      'PENDING': 'bg-yellow-100 text-yellow-800',
      'REVIEW': 'bg-orange-100 text-orange-800',
      'REJECTED': 'bg-red-100 text-red-800'
    };
    const labels = {
      'VERIFIED': 'Vérifié',
      'PENDING': 'En attente',
      'REVIEW': 'En révision',
      'REJECTED': 'Rejeté'
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status] || 'bg-gray-100 text-gray-800'}`}>
        {labels[status] || status}
      </span>
    );
  };

  // ✅ APRÈS - Avec gestion des valeurs nulles
  const getVulnerabilityBadge = (score) => {
    // Convertir en nombre et gérer null/undefined
    const numScore = score ? parseFloat(score) : 0;
    
    if (numScore >= 70) {
      return (
        <span className="px-2 py-1 bg-red-100 text-red-800 text-xs font-semibold rounded">
          EXTRÊME ({numScore.toFixed(1)})
        </span>
      );
    }
    if (numScore >= 50) {
      return (
        <span className="px-2 py-1 bg-orange-100 text-orange-800 text-xs font-semibold rounded">
          ÉLEVÉ ({numScore.toFixed(1)})
        </span>
      );
    }
    if (numScore >= 30) {
      return (
        <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs font-semibold rounded">
          MODÉRÉ ({numScore.toFixed(1)})
        </span>
      );
    }
    return (
      <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-semibold rounded">
        FAIBLE ({numScore.toFixed(1)})
      </span>
    );
  };

  return (
    <div className="space-y-6">
      {/* Barre d'actions */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">
            Bénéficiaires RSU
          </h2>
          <p className="text-gray-600 text-sm mt-1">
            {pagination.total.toLocaleString('fr-FR')} enregistrement{pagination.total > 1 ? 's' : ''} au total
          </p>
        </div>
        
        <div className="flex gap-3">
          <button
            onClick={refresh}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2 transition-colors"
          >
            <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
            <span className="hidden sm:inline">Actualiser</span>
          </button>

          <ExportButton 
            data={beneficiaries} 
            disabled={loading}
            filename="beneficiaires_rsu"
          />
        </div>
      </div>

      {/* Filtres */}
      <BeneficiariesFilters 
        onFilterChange={applyFilters}
        onReset={resetFilters}
      />

      {/* Erreur */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
          <AlertTriangle className="text-red-600 flex-shrink-0 mt-0.5" size={20} />
          <div>
            <p className="text-red-800 font-semibold">Erreur de chargement</p>
            <p className="text-red-600 text-sm">{error}</p>
            <button
              onClick={refresh}
              className="mt-2 text-sm text-red-700 underline hover:text-red-800"
            >
              Réessayer
            </button>
          </div>
        </div>
      )}

      {/* Tableau */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        {loading ? (
          <div className="p-8 text-center">
            <RefreshCw className="animate-spin text-blue-600 mx-auto mb-4" size={48} />
            <p className="text-gray-600">Chargement des bénéficiaires...</p>
          </div>
        ) : beneficiaries.length === 0 ? (
          <div className="p-8 text-center">
            <p className="text-gray-500 mb-4">Aucun bénéficiaire trouvé</p>
            {Object.keys(filters).some(k => filters[k]) && (
              <button
                onClick={resetFilters}
                className="text-blue-600 hover:text-blue-700 underline"
              >
                Réinitialiser les filtres
              </button>
            )}
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      RSU-ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Nom Complet
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Province
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Score Vulnérabilité
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Statut
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {beneficiaries.map((person) => (
                    <tr key={person.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm font-mono text-blue-600 font-medium">
                          {person.rsu_id}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {person.first_name} {person.last_name}
                        </div>
                        {person.phone_number && (
                          <div className="text-xs text-gray-500">{person.phone_number}</div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <span className="flex items-center gap-1">
                          <MapPin size={14} />
                          {person.province?.replace(/_/g, ' ')}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getVulnerabilityBadge(person.vulnerability_score)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getStatusBadge(person.status)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <div className="flex items-center gap-2">
                          <button
                            className="text-blue-600 hover:text-blue-800 p-1 rounded hover:bg-blue-50 transition-colors"
                            title="Voir détails"
                          >
                            <Eye size={18} />
                          </button>
                          <button
                            className="text-gray-600 hover:text-gray-800 p-1 rounded hover:bg-gray-100 transition-colors"
                            title="Modifier"
                          >
                            <Edit size={18} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <Pagination
              currentPage={pagination.page}
              pageSize={pagination.pageSize}
              total={pagination.total}
              onPageChange={changePage}
              onPageSizeChange={changePageSize}
            />
          </>
        )}
      </div>

      {/* Footer info */}
      <div className="text-xs text-gray-500 text-center">
        📡 Source: GET /api/v1/identity/persons/ (Données temps réel)
      </div>
    </div>
  );
}