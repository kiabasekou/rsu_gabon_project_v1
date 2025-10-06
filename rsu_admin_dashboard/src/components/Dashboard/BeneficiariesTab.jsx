/**
 * 🇬🇦 RSU Gabon - Onglet Bénéficiaires
 * Standards Top 1% - Intégration données réelles
 * Fichier: rsu_admin_dashboard/src/components/Dashboard/BeneficiariesTab.jsx
 */

import React, { useState } from 'react';
import { Search, Filter, Download, RefreshCw, MapPin, Eye, Edit, ChevronLeft, ChevronRight } from 'lucide-react';

export default function BeneficiariesTab({ 
  beneficiaries = [],
  loading = false,
  pagination = { page: 1, pageSize: 50, total: 0 },
  onSearch,
  onExport 
}) {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterProvince, setFilterProvince] = useState('all');

  const provinces = [
    'Estuaire', 'Haut-Ogooué', 'Moyen-Ogooué', 'Ngounié',
    'Nyanga', 'Ogooué-Ivindo', 'Ogooué-Lolo', 'Ogooué-Maritime', 'Woleu-Ntem'
  ];

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    onSearch?.({
      search: searchTerm,
      province: filterProvince !== 'all' ? filterProvince : undefined
    });
  };

  const getStatusBadge = (status) => {
    const styles = {
      'VERIFIED': 'bg-green-100 text-green-800',
      'PENDING': 'bg-yellow-100 text-yellow-800',
      'REVIEW': 'bg-orange-100 text-orange-800',
      'REJECTED': 'bg-red-100 text-red-800'
    };
    return styles[status] || 'bg-gray-100 text-gray-800';
  };

  const getVulnerabilityColor = (score) => {
    if (score >= 75) return 'bg-red-100 text-red-800';
    if (score >= 50) return 'bg-orange-100 text-orange-800';
    if (score >= 25) return 'bg-yellow-100 text-yellow-800';
    return 'bg-green-100 text-green-800';
  };

  return (
    <div className="space-y-6">
      {/* Barre de recherche et filtres */}
      <div className="bg-white rounded-lg shadow-md p-4">
        <form onSubmit={handleSearchSubmit} className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Rechercher par RSU-ID, nom, prénom..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <div className="flex gap-2">
            <select
              value={filterProvince}
              onChange={(e) => setFilterProvince(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">Toutes les provinces</option>
              {provinces.map(province => (
                <option key={province} value={province}>{province}</option>
              ))}
            </select>

            <button
              type="submit"
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2 transition-colors"
            >
              <Filter size={18} />
              Filtrer
            </button>

            <button
              type="button"
              onClick={onExport}
              className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2 transition-colors"
            >
              <Download size={18} />
              Export
            </button>
          </div>
        </form>
      </div>

      {/* Tableau des bénéficiaires */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        {loading ? (
          <div className="p-8 text-center">
            <RefreshCw className="animate-spin text-blue-600 mx-auto mb-4" size={48} />
            <p className="text-gray-600">Chargement des bénéficiaires...</p>
          </div>
        ) : beneficiaries.length === 0 ? (
          <div className="p-8 text-center">
            <p className="text-gray-500">Aucun bénéficiaire trouvé</p>
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
                          {person.province}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {person.vulnerability_score ? (
                          <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getVulnerabilityColor(person.vulnerability_score)}`}>
                            {person.vulnerability_score.toFixed(1)}
                          </span>
                        ) : (
                          <span className="text-xs text-gray-400">N/A</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusBadge(person.verification_status)}`}>
                          {person.verification_status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex gap-2">
                          <button
                            className="text-blue-600 hover:text-blue-800"
                            title="Voir détails"
                          >
                            <Eye size={18} />
                          </button>
                          <button
                            className="text-gray-600 hover:text-gray-800"
                            title="Éditer"
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
            <div className="bg-gray-50 px-6 py-4 border-t border-gray-200 flex items-center justify-between">
              <div className="text-sm text-gray-600">
                Affichage {((pagination.page - 1) * pagination.pageSize) + 1} à {Math.min(pagination.page * pagination.pageSize, pagination.total)} sur {pagination.total} bénéficiaires
              </div>
              <div className="flex gap-2">
                <button
                  disabled={pagination.page === 1}
                  className="px-3 py-1 border border-gray-300 rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronLeft size={18} />
                </button>
                <span className="px-4 py-1 bg-blue-600 text-white rounded-lg">
                  Page {pagination.page}
                </span>
                <button
                  disabled={pagination.page * pagination.pageSize >= pagination.total}
                  className="px-3 py-1 border border-gray-300 rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronRight size={18} />
                </button>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Indicateur source données */}
      <div className="text-xs text-gray-500 text-center">
        📡 Source: GET /api/v1/identity/persons/ (Données temps réel)
      </div>
    </div>
  );
}