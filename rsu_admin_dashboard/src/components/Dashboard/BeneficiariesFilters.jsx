/**
 * 🇬🇦 RSU Gabon - Filtres Avancés Bénéficiaires
 * Standards Top 1% - UX Optimisée
 * Fichier: rsu_admin_dashboard/src/components/Dashboard/BeneficiariesFilters.jsx
 */

import React, { useState } from 'react';
import { Search, Filter, X, ChevronDown } from 'lucide-react';

export default function BeneficiariesFilters({ onFilterChange, onReset }) {
  const [filters, setFilters] = useState({
    search: '',
    province: '',
    gender: '',
    vulnerabilityMin: '',
    vulnerabilityMax: '',
    ageMin: '',
    ageMax: '',
    status: ''
  });

  const [showAdvanced, setShowAdvanced] = useState(false);

  const provinces = [
    'ESTUAIRE', 'HAUT_OGOOUE', 'MOYEN_OGOOUE', 'NGOUNIE',
    'NYANGA', 'OGOOUE_IVINDO', 'OGOOUE_LOLO', 'OGOOUE_MARITIME', 'WOLEU_NTEM'
  ];

  const handleChange = (field, value) => {
    const newFilters = { ...filters, [field]: value };
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  const handleReset = () => {
    const emptyFilters = {
      search: '',
      province: '',
      gender: '',
      vulnerabilityMin: '',
      vulnerabilityMax: '',
      ageMin: '',
      ageMax: '',
      status: ''
    };
    setFilters(emptyFilters);
    onReset();
  };

  const activeFiltersCount = Object.values(filters).filter(v => v !== '').length;

  return (
    <div className="bg-white rounded-lg shadow-md p-4 space-y-4">
      {/* Barre de recherche principale */}
      <div className="flex gap-3">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
          <input
            type="text"
            placeholder="Rechercher par nom, prénom, RSU-ID, téléphone..."
            value={filters.search}
            onChange={(e) => handleChange('search', e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-colors ${
            showAdvanced 
              ? 'bg-blue-600 text-white' 
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          <Filter size={18} />
          <span className="hidden sm:inline">Filtres</span>
          {activeFiltersCount > 0 && (
            <span className="bg-white text-blue-600 text-xs font-bold px-2 py-0.5 rounded-full">
              {activeFiltersCount}
            </span>
          )}
          <ChevronDown size={16} className={`transition-transform ${showAdvanced ? 'rotate-180' : ''}`} />
        </button>

        {activeFiltersCount > 0 && (
          <button
            onClick={handleReset}
            className="px-4 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 flex items-center gap-2 transition-colors"
            title="Réinitialiser les filtres"
          >
            <X size={18} />
            <span className="hidden sm:inline">Reset</span>
          </button>
        )}
      </div>

      {/* Filtres avancés */}
      {showAdvanced && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 pt-4 border-t border-gray-200">
          {/* Province */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Province
            </label>
            <select
              value={filters.province}
              onChange={(e) => handleChange('province', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Toutes les provinces</option>
              {provinces.map(prov => (
                <option key={prov} value={prov}>
                  {prov.replace(/_/g, ' ')}
                </option>
              ))}
            </select>
          </div>

          {/* Genre */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Genre
            </label>
            <select
              value={filters.gender}
              onChange={(e) => handleChange('gender', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Tous</option>
              <option value="M">Masculin</option>
              <option value="F">Féminin</option>
              <option value="OTHER">Autre</option>
            </select>
          </div>

          {/* Score Vulnérabilité Min */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Score Vulnérabilité Min
            </label>
            <input
              type="number"
              min="0"
              max="100"
              placeholder="0"
              value={filters.vulnerabilityMin}
              onChange={(e) => handleChange('vulnerabilityMin', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Score Vulnérabilité Max */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Score Vulnérabilité Max
            </label>
            <input
              type="number"
              min="0"
              max="100"
              placeholder="100"
              value={filters.vulnerabilityMax}
              onChange={(e) => handleChange('vulnerabilityMax', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Âge Min */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Âge Minimum
            </label>
            <input
              type="number"
              min="0"
              max="120"
              placeholder="0"
              value={filters.ageMin}
              onChange={(e) => handleChange('ageMin', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Âge Max */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Âge Maximum
            </label>
            <input
              type="number"
              min="0"
              max="120"
              placeholder="120"
              value={filters.ageMax}
              onChange={(e) => handleChange('ageMax', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Statut */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Statut
            </label>
            <select
              value={filters.status}
              onChange={(e) => handleChange('status', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Tous les statuts</option>
              <option value="VERIFIED">Vérifié</option>
              <option value="PENDING">En attente</option>
              <option value="REVIEW">En révision</option>
              <option value="REJECTED">Rejeté</option>
            </select>
          </div>

          {/* Placeholder pour alignement */}
          <div className="hidden lg:block"></div>
        </div>
      )}

      {/* Résumé filtres actifs */}
      {activeFiltersCount > 0 && (
        <div className="flex flex-wrap gap-2 pt-2">
          {Object.entries(filters).map(([key, value]) => {
            if (!value) return null;
            
            let label = key;
            let displayValue = value;
            
            // Formatage labels
            if (key === 'vulnerabilityMin') label = 'Score min';
            if (key === 'vulnerabilityMax') label = 'Score max';
            if (key === 'ageMin') label = 'Âge min';
            if (key === 'ageMax') label = 'Âge max';
            if (key === 'province') displayValue = value.replace(/_/g, ' ');
            
            return (
              <span
                key={key}
                className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-700 text-sm rounded-full"
              >
                <span className="font-medium">{label}:</span>
                <span>{displayValue}</span>
                <button
                  onClick={() => handleChange(key, '')}
                  className="hover:bg-blue-200 rounded-full p-0.5"
                >
                  <X size={14} />
                </button>
              </span>
            );
          })}
        </div>
      )}
    </div>
  );
}