import React, { useState } from 'react';
import { Search, Filter, Download, RefreshCw, MapPin, Eye, Edit } from 'lucide-react';

export default function BeneficiariesTab({ 
  beneficiaries: initialBeneficiaries = [],
  loading = false,
  onSearch,
  onExport 
}) {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterProvince, setFilterProvince] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);

  const demoBeneficiaries = [
    { id: '1', rsu_id: 'RSU-GA-2025-045820', first_name: 'Marie', last_name: 'OBIANG', province: 'Estuaire', vulnerability_score: 68.5, verification_status: 'VERIFIED' },
    { id: '2', rsu_id: 'RSU-GA-2025-045819', first_name: 'Jean', last_name: 'MBOUMBA', province: 'Haut-Ogooué', vulnerability_score: 45.2, verification_status: 'PENDING' },
    { id: '3', rsu_id: 'RSU-GA-2025-045818', first_name: 'Sylvie', last_name: 'KOUMBA', province: 'Ngounié', vulnerability_score: 72.1, verification_status: 'VERIFIED' },
    { id: '4', rsu_id: 'RSU-GA-2025-045817', first_name: 'Paul', last_name: 'NZAMBA', province: 'Estuaire', vulnerability_score: 38.9, verification_status: 'REVIEW' },
    { id: '5', rsu_id: 'RSU-GA-2025-045816', first_name: 'Claire', last_name: 'IDIATA', province: 'Moyen-Ogooué', vulnerability_score: 55.4, verification_status: 'VERIFIED' }
  ];

  const beneficiaries = initialBeneficiaries.length > 0 ? initialBeneficiaries : demoBeneficiaries;
  const totalPages = 458;

  const provinces = [
    'Estuaire', 'Haut-Ogooué', 'Moyen-Ogooué', 'Ngounié',
    'Nyanga', 'Ogooué-Ivindo', 'Ogooué-Lolo', 'Ogooué-Maritime', 'Woleu-Ntem'
  ];

  const handleSearch = () => {
    if (onSearch) onSearch({ search: searchTerm, province: filterProvince, page: currentPage });
  };

  const handleExport = () => {
    if (onExport) {
      onExport();
    } else {
      alert('Export - Connecter au backend /analytics/reports/');
    }
  };

  return (
    <div className="space-y-4">
      {/* Barre de recherche */}
      <div className="bg-white rounded-lg shadow-md p-4">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Rechercher par RSU-ID, nom, NIP..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
          </div>

          <select
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            value={filterProvince}
            onChange={(e) => setFilterProvince(e.target.value)}
          >
            <option value="all">Toutes les provinces</option>
            {provinces.map(p => (
              <option key={p} value={p}>{p}</option>
            ))}
          </select>

          <button
            onClick={handleSearch}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2 whitespace-nowrap"
          >
            <Filter size={20} />
            Filtrer
          </button>
          <button
            onClick={handleExport}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2 whitespace-nowrap"
          >
            <Download size={20} />
            Export
          </button>
        </div>
        <div className="mt-2 text-xs text-gray-500">
          📡 API: GET /identity/persons/?search={searchTerm}&province={filterProvince}
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        {loading ? (
          <div className="p-8 text-center">
            <RefreshCw className="animate-spin text-blue-600 mx-auto mb-4" size={48} />
            <p className="text-gray-600">Chargement...</p>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">RSU-ID</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nom</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Province</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Score</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Statut</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {beneficiaries.map((person) => (
                    <tr key={person.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-blue-600">{person.rsu_id}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{person.first_name} {person.last_name}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <span className="flex items-center gap-1">
                          <MapPin size={14} />
                          {person.province}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                          person.vulnerability_score >= 60 ? 'bg-red-100 text-red-800' :
                          person.vulnerability_score >= 40 ? 'bg-orange-100 text-orange-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {person.vulnerability_score.toFixed(1)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                          person.verification_status === 'VERIFIED' ? 'bg-green-100 text-green-800' :
                          person.verification_status === 'PENDING' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {person.verification_status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <div className="flex gap-2">
                          <button className="text-blue-600 hover:text-blue-800 transition-colors">
                            <Eye size={18} />
                          </button>
                          <button className="text-green-600 hover:text-green-800 transition-colors">
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
            <div className="bg-gray-50 px-6 py-3 flex items-center justify-between border-t border-gray-200">
              <div className="text-sm text-gray-700">
                Page <span className="font-semibold">{currentPage}</span> sur{' '}
                <span className="font-semibold">{totalPages}</span>
              </div>
              <div className="flex gap-2">
                <button
                  disabled={currentPage === 1}
                  onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                  className="px-4 py-2 bg-white border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Précédent
                </button>
                <button
                  disabled={currentPage === totalPages}
                  onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                  className="px-4 py-2 bg-white border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Suivant
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}