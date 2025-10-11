/**
 * 🇬🇦 RSU Gabon - Programs Tab Enhanced
 * Standards Top 1% - Liste et Détails Programmes
 * Fichier: rsu_admin_dashboard/src/components/Dashboard/ProgramsTab.jsx
 */

import React, { useState, useEffect } from 'react';
import {
  Plus, Search, Filter, RefreshCw, Grid, List,
  DollarSign, Users, Calendar, TrendingUp, Eye
} from 'lucide-react';
import { programsAPI } from '../../services/api/programsAPI';
import ProgramDetail from './ProgramDetail';

export default function ProgramsTab() {
  const [programs, setPrograms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'
  const [selectedProgram, setSelectedProgram] = useState(null);
  const [filters, setFilters] = useState({
    status: '',
    search: '',
    ordering: '-created_at'
  });

  useEffect(() => {
    loadPrograms();
  }, [filters]);

  const loadPrograms = async () => {
    try {
      setLoading(true);
      const data = await programsAPI.getPrograms(filters);
      
      // ✅ FIX: API retourne {count, results} avec pagination
      const programsList = data.results || [];
      
      setPrograms(programsList);
      console.log(`✅ Programs loaded: ${programsList.length}`);
    } catch (error) {
      console.error('Erreur chargement programmes:', error);
      setPrograms([]); // ✅ Éviter les doublons en cas d'erreur
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const handleViewProgram = (programId) => {
    setSelectedProgram(programId);
  };

  const handleBackToList = () => {
    setSelectedProgram(null);
    loadPrograms(); // Rafraîchir la liste
  };

  // Si un programme est sélectionné, afficher les détails
  if (selectedProgram) {
    return <ProgramDetail programId={selectedProgram} onBack={handleBackToList} />;
  }

  const getStatusBadge = (status) => {
    const styles = {
      ACTIVE: 'bg-green-100 text-green-800 border-green-300',
      DRAFT: 'bg-blue-100 text-blue-800 border-blue-300',
      PAUSED: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      CLOSED: 'bg-gray-100 text-gray-800 border-gray-300'
    };
    const labels = {
      ACTIVE: 'Actif',
      DRAFT: 'Brouillon',
      PAUSED: 'Suspendu',
      CLOSED: 'Clôturé'
    };
    return (
      <span className={`px-3 py-1 rounded-full text-xs font-medium border ${styles[status] || 'bg-gray-100 text-gray-800'}`}>
        {labels[status] || status}
      </span>
    );
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'XAF',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Programmes Sociaux</h2>
          <p className="text-gray-600 text-sm mt-1">
            {programs.length} programme{programs.length > 1 ? 's' : ''} enregistré{programs.length > 1 ? 's' : ''}
          </p>
        </div>

        <div className="flex gap-3">
          <button
            onClick={loadPrograms}
            disabled={loading}
            className="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2 transition-colors disabled:opacity-50"
          >
            <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
            Actualiser
          </button>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2 transition-colors">
            <Plus size={18} />
            Nouveau Programme
          </button>
        </div>
      </div>

      {/* Filtres et recherche */}
      <div className="bg-white rounded-lg shadow-md p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Recherche */}
          <div className="md:col-span-2">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Rechercher par nom ou code..."
                value={filters.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Filtre statut */}
          <div>
            <select
              value={filters.status}
              onChange={(e) => handleFilterChange('status', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Tous les statuts</option>
              <option value="ACTIVE">Actif</option>
              <option value="DRAFT">Brouillon</option>
              <option value="PAUSED">Suspendu</option>
              <option value="CLOSED">Clôturé</option>
            </select>
          </div>

          {/* Tri */}
          <div>
            <select
              value={filters.ordering}
              onChange={(e) => handleFilterChange('ordering', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="-created_at">Plus récent</option>
              <option value="created_at">Plus ancien</option>
              <option value="name">Nom (A-Z)</option>
              <option value="-name">Nom (Z-A)</option>
              <option value="-total_budget">Budget (décroissant)</option>
              <option value="total_budget">Budget (croissant)</option>
            </select>
          </div>
        </div>

        {/* Bascule vue */}
        <div className="flex justify-end mt-4 gap-2">
          <button
            onClick={() => setViewMode('grid')}
            className={`p-2 rounded-lg transition-colors ${
              viewMode === 'grid' ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            <Grid size={20} />
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`p-2 rounded-lg transition-colors ${
              viewMode === 'list' ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            <List size={20} />
          </button>
        </div>
      </div>

      {/* Liste programmes */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Chargement des programmes...</p>
          </div>
        </div>
      ) : programs.length === 0 ? (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <Filter className="mx-auto text-gray-400 mb-4" size={48} />
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Aucun programme trouvé</h3>
          <p className="text-gray-500">Essayez de modifier vos filtres ou créez un nouveau programme</p>
        </div>
      ) : viewMode === 'grid' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {programs.map((program) => (
            <div
              key={program.id}
              className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow overflow-hidden group"
            >
              {/* En-tête card */}
              <div className="bg-gradient-to-r from-blue-600 to-blue-700 p-4 text-white">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <h3 className="font-bold text-lg mb-1 line-clamp-2">{program.name}</h3>
                    <p className="text-blue-100 text-sm font-mono">{program.code}</p>
                  </div>
                  {getStatusBadge(program.status)}
                </div>
              </div>

              {/* Corps card */}
              <div className="p-4 space-y-4">
                {/* Budget */}
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-600 flex items-center gap-1">
                      <DollarSign size={16} />
                      Budget
                    </span>
                    <span className="text-xs font-medium text-gray-500">
                      {((program.budget_spent / program.total_budget) * 100).toFixed(0)}% utilisé
                    </span>
                  </div>
                  <div className="space-y-1">
                    <p className="text-lg font-bold text-gray-800">
                      {formatCurrency(program.total_budget)}
                    </p>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all"
                        style={{ width: `${Math.min((program.budget_spent / program.total_budget) * 100, 100)}%` }}
                      ></div>
                    </div>
                    <div className="flex justify-between text-xs text-gray-500">
                      <span>Utilisé: {formatCurrency(program.budget_spent)}</span>
                      <span>Reste: {formatCurrency(program.budget_remaining)}</span>
                    </div>
                  </div>
                </div>

                {/* Statistiques */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-purple-50 rounded-lg p-3">
                    <div className="flex items-center gap-2 mb-1">
                      <Users size={16} className="text-purple-600" />
                      <span className="text-xs text-purple-600 font-medium">Bénéficiaires</span>
                    </div>
                    <p className="text-xl font-bold text-purple-800">
                      {program.current_beneficiaries}
                    </p>
                    {program.max_beneficiaries && (
                      <p className="text-xs text-purple-600">
                        / {program.max_beneficiaries} max
                      </p>
                    )}
                  </div>

                  <div className="bg-green-50 rounded-lg p-3">
                    <div className="flex items-center gap-2 mb-1">
                      <TrendingUp size={16} className="text-green-600" />
                      <span className="text-xs text-green-600 font-medium">Montant</span>
                    </div>
                    <p className="text-xl font-bold text-green-800">
                      {formatCurrency(program.benefit_amount)}
                    </p>
                    <p className="text-xs text-green-600">
                      {program.frequency === 'MONTHLY' ? '/mois' :
                       program.frequency === 'QUARTERLY' ? '/trimestre' :
                       program.frequency === 'ANNUAL' ? '/an' : 'unique'}
                    </p>
                  </div>
                </div>

                {/* Dates */}
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Calendar size={16} />
                  <span>
                    Du {formatDate(program.start_date)}
                    {program.end_date && ` au ${formatDate(program.end_date)}`}
                  </span>
                </div>

                {/* Actions */}
                <button
                  onClick={() => handleViewProgram(program.id)}
                  className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center justify-center gap-2 transition-colors group-hover:bg-blue-700"
                >
                  <Eye size={18} />
                  Voir les détails
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        /* Vue liste */
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Programme
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Statut
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Budget
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Bénéficiaires
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Dates
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {programs.map((program) => (
                <tr key={program.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">{program.name}</div>
                      <div className="text-sm text-gray-500 font-mono">{program.code}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {getStatusBadge(program.status)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {formatCurrency(program.total_budget)}
                      </div>
                      <div className="text-sm text-gray-500">
                        {((program.budget_spent / program.total_budget) * 100).toFixed(0)}% utilisé
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {program.current_beneficiaries}
                      {program.max_beneficiaries && ` / ${program.max_beneficiaries}`}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {formatDate(program.start_date)}
                    </div>
                    {program.end_date && (
                      <div className="text-sm text-gray-500">
                        → {formatDate(program.end_date)}
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      onClick={() => handleViewProgram(program.id)}
                      className="text-blue-600 hover:text-blue-900 flex items-center gap-1 ml-auto"
                    >
                      <Eye size={16} />
                      Détails
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Information API */}
      <div className="bg-blue-50 border-l-4 border-blue-600 p-4 rounded text-sm">
        <p className="font-semibold text-blue-800 mb-2">📡 Source de données:</p>
        <p className="text-blue-700">
          ✅ GET /api/v1/programs/programs/ 
          {filters.status && ` (filtre: ${filters.status})`}
          {filters.search && ` (recherche: "${filters.search}")`}
        </p>
        <p className="text-blue-600 text-xs mt-1">
          {programs.length} programme{programs.length > 1 ? 's' : ''} chargé{programs.length > 1 ? 's' : ''}
        </p>
      </div>
    </div>
  );
}