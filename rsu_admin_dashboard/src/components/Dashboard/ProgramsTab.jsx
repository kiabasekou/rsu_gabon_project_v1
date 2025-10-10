/**
 * 🇬🇦 RSU Gabon - Programs Tab
 * Gestion complète des programmes sociaux
 * Fichier: src/components/Dashboard/ProgramsTab.jsx
 */

import React, { useState } from 'react';
import { 
  Folder, DollarSign, Users, Calendar, CheckCircle, 
  XCircle, Clock, AlertCircle, TrendingUp, Filter,
  Plus, Eye, Edit, Trash2, Play, Pause, Lock
} from 'lucide-react';

export default function ProgramsTab({ programs, loading, onRefresh }) {
  console.log('🎯 ProgramsTab rendered');
  console.log('   programs prop:', programs);
  console.log('   loading prop:', loading);
  

    // ================================================================================
    // COMPOSANT PRINCIPAL
    // ================================================================================


  const [selectedProgram, setSelectedProgram] = useState(null);
  const [filters, setFilters] = useState({
    status: 'ALL',
    category: 'ALL',
    search: ''
  });
  const [view, setView] = useState('list'); // 'list' | 'details' | 'create'

  // Données mock pour démo (à remplacer par API)
  const mockPrograms = programs.length > 0 ? programs : [
    {
      id: 1,
      code: 'TMC-2025',
      name: 'Transfert Monétaire Conditionnel',
      category: { name: 'Transferts Monétaires', icon: '💰' },
      status: 'ACTIVE',
      total_budget: 1000000000,
      budget_spent: 450000000,
      budget_remaining: 550000000,
      benefit_amount: 50000,
      frequency: 'MONTHLY',
      max_beneficiaries: 1000,
      current_beneficiaries: 456,
      start_date: '2025-01-01',
      end_date: '2025-12-31',
      is_active: true,
      is_full: false,
      managed_by_name: 'Jean Dupont',
      enrollments_count: 456,
      active_enrollments_count: 445,
    },
    {
      id: 2,
      code: 'BOURSE-EDU-2025',
      name: 'Bourse Éducation Primaire',
      category: { name: 'Éducation', icon: '🎓' },
      status: 'ACTIVE',
      total_budget: 500000000,
      budget_spent: 180000000,
      budget_remaining: 320000000,
      benefit_amount: 75000,
      frequency: 'MONTHLY',
      max_beneficiaries: 500,
      current_beneficiaries: 234,
      start_date: '2025-01-15',
      end_date: '2025-06-30',
      is_active: true,
      is_full: false,
      managed_by_name: 'Marie Martin',
      enrollments_count: 234,
      active_enrollments_count: 230,
    },
    {
      id: 3,
      code: 'AMU-2025',
      name: 'Assurance Maladie Universelle',
      category: { name: 'Santé', icon: '🏥' },
      status: 'PAUSED',
      total_budget: 2000000000,
      budget_spent: 850000000,
      budget_remaining: 1150000000,
      benefit_amount: 25000,
      frequency: 'MONTHLY',
      max_beneficiaries: 5000,
      current_beneficiaries: 3200,
      start_date: '2024-06-01',
      end_date: null,
      is_active: false,
      is_full: false,
      managed_by_name: 'Dr. Amina Ndong',
      enrollments_count: 3200,
      active_enrollments_count: 0,
    }
  ];

  const filteredPrograms = mockPrograms.filter(p => {
    if (filters.status !== 'ALL' && p.status !== filters.status) return false;
    if (filters.search && !p.name.toLowerCase().includes(filters.search.toLowerCase()) && 
        !p.code.toLowerCase().includes(filters.search.toLowerCase())) return false;
    return true;
  });

  const getStatusBadge = (status) => {
    const styles = {
      ACTIVE: 'bg-green-100 text-green-800 border-green-300',
      PAUSED: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      CLOSED: 'bg-gray-100 text-gray-800 border-gray-300',
      DRAFT: 'bg-blue-100 text-blue-800 border-blue-300'
    };
    const icons = {
      ACTIVE: <CheckCircle size={14} />,
      PAUSED: <Pause size={14} />,
      CLOSED: <Lock size={14} />,
      DRAFT: <Edit size={14} />
    };
    const labels = {
      ACTIVE: 'Actif',
      PAUSED: 'Suspendu',
      CLOSED: 'Clôturé',
      DRAFT: 'Brouillon'
    };
    
    return (
      <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold border ${styles[status]}`}>
        {icons[status]}
        {labels[status]}
      </span>
    );
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'XAF',
      minimumFractionDigits: 0
    }).format(value);
  };

  const calculateBudgetPercentage = (spent, total) => {
    return total > 0 ? Math.round((spent / total) * 100) : 0;
  };

  const calculateCapacityPercentage = (current, max) => {
    return max > 0 ? Math.round((current / max) * 100) : 0;
  };

  // ================================================================================
  // STATISTIQUES GLOBALES
  // ================================================================================

  const globalStats = {
    total_programs: mockPrograms.length,
    active_programs: mockPrograms.filter(p => p.status === 'ACTIVE').length,
    total_budget: mockPrograms.reduce((sum, p) => sum + p.total_budget, 0),
    budget_spent: mockPrograms.reduce((sum, p) => sum + p.budget_spent, 0),
    total_beneficiaries: mockPrograms.reduce((sum, p) => sum + p.current_beneficiaries, 0),
  };

  // ================================================================================
  // RENDU CONDITIONNEL PAR VUE
  // ================================================================================

  if (view === 'details' && selectedProgram) {
    return <ProgramDetails program={selectedProgram} onBack={() => setView('list')} />;
  }

  if (view === 'create') {
    return <ProgramForm onBack={() => setView('list')} onSuccess={() => { setView('list'); onRefresh?.(); }} />;
  }

  // ================================================================================
  // VUE LISTE (DÉFAUT)
  // ================================================================================

  return (
    <div className="space-y-6">
      {/* En-tête avec statistiques */}
      <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-lg shadow-lg p-6 text-white">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold mb-2">Programmes Sociaux</h2>
            <p className="text-purple-100">Gestion des programmes d'aide gouvernementale</p>
          </div>
          <button
            onClick={() => setView('create')}
            className="flex items-center gap-2 px-4 py-2 bg-white text-purple-600 rounded-lg hover:bg-purple-50 transition-colors font-semibold"
          >
            <Plus size={20} />
            Nouveau Programme
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <StatCard
            icon={<Folder size={24} />}
            label="Total Programmes"
            value={globalStats.total_programs}
            bgColor="bg-purple-500"
          />
          <StatCard
            icon={<CheckCircle size={24} />}
            label="Programmes Actifs"
            value={globalStats.active_programs}
            bgColor="bg-green-500"
          />
          <StatCard
            icon={<DollarSign size={24} />}
            label="Budget Total"
            value={formatCurrency(globalStats.total_budget).replace('XAF', 'Mds FCFA').replace(/\s/g, '')}
            bgColor="bg-blue-500"
          />
          <StatCard
            icon={<TrendingUp size={24} />}
            label="Budget Utilisé"
            value={`${calculateBudgetPercentage(globalStats.budget_spent, globalStats.total_budget)}%`}
            bgColor="bg-orange-500"
          />
          <StatCard
            icon={<Users size={24} />}
            label="Bénéficiaires"
            value={globalStats.total_beneficiaries.toLocaleString()}
            bgColor="bg-indigo-500"
          />
        </div>
      </div>

      {/* Filtres */}
      <div className="bg-white rounded-lg shadow-md p-4">
        <div className="flex items-center gap-4 flex-wrap">
          <div className="flex items-center gap-2">
            <Filter size={20} className="text-gray-500" />
            <span className="font-semibold text-gray-700">Filtres:</span>
          </div>
          
          <select
            value={filters.status}
            onChange={(e) => setFilters({ ...filters, status: e.target.value })}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          >
            <option value="ALL">Tous les statuts</option>
            <option value="ACTIVE">Actif</option>
            <option value="PAUSED">Suspendu</option>
            <option value="DRAFT">Brouillon</option>
            <option value="CLOSED">Clôturé</option>
          </select>

          <input
            type="text"
            placeholder="Rechercher un programme..."
            value={filters.search}
            onChange={(e) => setFilters({ ...filters, search: e.target.value })}
            className="flex-1 min-w-[200px] px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Liste des programmes */}
      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Chargement des programmes...</p>
        </div>
      ) : filteredPrograms.length === 0 ? (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <AlertCircle size={64} className="text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-gray-800 mb-2">Aucun programme trouvé</h3>
          <p className="text-gray-600">Essayez de modifier vos filtres ou créez un nouveau programme</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {filteredPrograms.map(program => (
            <ProgramCard
              key={program.id}
              program={program}
              onView={() => {
                setSelectedProgram(program);
                setView('details');
              }}
              formatCurrency={formatCurrency}
              getStatusBadge={getStatusBadge}
              calculateBudgetPercentage={calculateBudgetPercentage}
              calculateCapacityPercentage={calculateCapacityPercentage}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// ================================================================================
// COMPOSANTS ENFANTS
// ================================================================================

function StatCard({ icon, label, value, bgColor }) {
  return (
    <div className={`${bgColor} rounded-lg p-4 text-white`}>
      <div className="flex items-center justify-between mb-2">
        {icon}
      </div>
      <div className="text-2xl font-bold mb-1">{value}</div>
      <div className="text-sm opacity-90">{label}</div>
    </div>
  );
}

function ProgramCard({ program, onView, formatCurrency, getStatusBadge, calculateBudgetPercentage, calculateCapacityPercentage }) {
  const budgetPct = calculateBudgetPercentage(program.budget_spent, program.total_budget);
  const capacityPct = calculateCapacityPercentage(program.current_beneficiaries, program.max_beneficiaries);

  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-6">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <span className="text-3xl">{program.category.icon}</span>
            <div>
              <h3 className="text-xl font-bold text-gray-800">{program.name}</h3>
              <p className="text-sm text-gray-600">{program.code} • {program.category.name}</p>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {getStatusBadge(program.status)}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        {/* Budget */}
        <div className="bg-blue-50 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <DollarSign size={18} className="text-blue-600" />
            <span className="text-sm font-semibold text-blue-900">Budget</span>
          </div>
          <div className="text-2xl font-bold text-blue-900 mb-1">
            {formatCurrency(program.budget_remaining)}
          </div>
          <div className="w-full bg-blue-200 rounded-full h-2 mb-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all"
              style={{ width: `${budgetPct}%` }}
            />
          </div>
          <div className="text-xs text-blue-700">
            {budgetPct}% utilisé • {formatCurrency(program.benefit_amount)}/{program.frequency === 'MONTHLY' ? 'mois' : 'ponctuel'}
          </div>
        </div>

        {/* Bénéficiaires */}
        <div className="bg-green-50 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Users size={18} className="text-green-600" />
            <span className="text-sm font-semibold text-green-900">Bénéficiaires</span>
          </div>
          <div className="text-2xl font-bold text-green-900 mb-1">
            {program.current_beneficiaries} / {program.max_beneficiaries}
          </div>
          <div className="w-full bg-green-200 rounded-full h-2 mb-2">
            <div
              className="bg-green-600 h-2 rounded-full transition-all"
              style={{ width: `${capacityPct}%` }}
            />
          </div>
          <div className="text-xs text-green-700">
            {capacityPct}% capacité • {program.max_beneficiaries - program.current_beneficiaries} places disponibles
          </div>
        </div>

        {/* Dates */}
        <div className="bg-purple-50 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Calendar size={18} className="text-purple-600" />
            <span className="text-sm font-semibold text-purple-900">Période</span>
          </div>
          <div className="text-sm text-purple-900 mb-1">
            <strong>Début:</strong> {new Date(program.start_date).toLocaleDateString('fr-FR')}
          </div>
          <div className="text-sm text-purple-900">
            <strong>Fin:</strong> {program.end_date ? new Date(program.end_date).toLocaleDateString('fr-FR') : 'Indéterminée'}
          </div>
          <div className="text-xs text-purple-700 mt-2">
            Géré par: {program.managed_by_name}
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between pt-4 border-t border-gray-200">
        <div className="flex items-center gap-4 text-sm text-gray-600">
          <span className="flex items-center gap-1">
            <Users size={14} />
            {program.enrollments_count} inscriptions
          </span>
          <span className="flex items-center gap-1">
            <CheckCircle size={14} />
            {program.active_enrollments_count} actives
          </span>
        </div>
        
        <div className="flex gap-2">
          <button
            onClick={onView}
            className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            <Eye size={16} />
            Détails
          </button>
        </div>
      </div>
    </div>
  );
}

function ProgramDetails({ program, onBack }) {
  return (
    <div className="space-y-6">
      <button
        onClick={onBack}
        className="flex items-center gap-2 text-purple-600 hover:text-purple-700 font-semibold"
      >
        ← Retour à la liste
      </button>

      <div className="bg-white rounded-lg shadow-lg p-8">
        <h2 className="text-3xl font-bold text-gray-800 mb-6">{program.name}</h2>
        <p className="text-gray-600 mb-4">Détails complets du programme à implémenter...</p>
        {/* TODO: Ajouter graphiques, historique paiements, liste bénéficiaires */}
      </div>
    </div>
  );
}

function ProgramForm({ onBack, onSuccess }) {
  return (
    <div className="space-y-6">
      <button
        onClick={onBack}
        className="flex items-center gap-2 text-purple-600 hover:text-purple-700 font-semibold"
      >
        ← Retour à la liste
      </button>

      <div className="bg-white rounded-lg shadow-lg p-8">
        <h2 className="text-3xl font-bold text-gray-800 mb-6">Nouveau Programme</h2>
        <p className="text-gray-600 mb-4">Formulaire de création à implémenter...</p>
        {/* TODO: Formulaire complet avec validation */}
      </div>
    </div>
  );
}