/**
 * 🇬🇦 RSU Gabon - Hook Bénéficiaires Amélioré
 * Standards Top 1% - Filtres, Pagination, Recherche
 * Fichier: rsu_admin_dashboard/src/hooks/useBeneficiaries.js
 */

import { useState, useCallback, useRef } from 'react';
import apiClient from '../services/api/apiClient';
import ENDPOINTS from '../services/api/endpoints';

export function useBeneficiaries() {
  const [beneficiaries, setBeneficiaries] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 50,
    total: 0,
  });
  const [filters, setFilters] = useState({});
  
  // Utiliser ref pour éviter re-renders
  const filtersRef = useRef(filters);
  const abortControllerRef = useRef(null);

  const loadBeneficiaries = useCallback(async (page = pagination.page, pageSize = pagination.pageSize) => {
    // Annuler requête précédente si en cours
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    setLoading(true);
    setError(null);

    try {
      // Construire paramètres query
      const params = {
        page,
        page_size: pageSize,
        ...buildQueryParams(filtersRef.current)
      };

      const response = await apiClient.get(ENDPOINTS.IDENTITY.PERSONS, params);
      
      setBeneficiaries(response.results || []);
      setPagination(prev => ({
        ...prev,
        page,
        pageSize,
        total: response.count || 0,
      }));
      setLoading(false);
      
      console.log(`✅ ${response.results?.length} bénéficiaires chargés (page ${page}/${Math.ceil(response.count / pageSize)})`);
    } catch (err) {
      if (err.name === 'AbortError') {
        console.log('Requête annulée');
        return;
      }
      console.error('❌ Erreur chargement bénéficiaires:', err);
      setError(err.message);
      setLoading(false);
    }
  }, [pagination.page, pagination.pageSize]);

  // Appliquer filtres
  const applyFilters = useCallback((newFilters) => {
    filtersRef.current = newFilters;
    setFilters(newFilters);
    setPagination(prev => ({ ...prev, page: 1 })); // Reset à page 1
    loadBeneficiaries(1, pagination.pageSize);
  }, [loadBeneficiaries, pagination.pageSize]);

  // Changer page
  const changePage = useCallback((newPage) => {
    loadBeneficiaries(newPage, pagination.pageSize);
  }, [loadBeneficiaries, pagination.pageSize]);

  // Changer taille page
  const changePageSize = useCallback((newPageSize) => {
    loadBeneficiaries(1, newPageSize);
  }, [loadBeneficiaries]);

  // Reset filtres
  const resetFilters = useCallback(() => {
    filtersRef.current = {};
    setFilters({});
    setPagination(prev => ({ ...prev, page: 1 }));
    loadBeneficiaries(1, pagination.pageSize);
  }, [loadBeneficiaries, pagination.pageSize]);

  // Refresh manuel
  const refresh = useCallback(() => {
    loadBeneficiaries(pagination.page, pagination.pageSize);
  }, [loadBeneficiaries, pagination.page, pagination.pageSize]);

  return {
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
  };
}

/**
 * Construire paramètres query depuis filtres
 */
function buildQueryParams(filters) {
  const params = {};

  // Recherche textuelle
  if (filters.search) {
    params.search = filters.search;
  }

  // Province
  if (filters.province) {
    params.province = filters.province;
  }

  // Genre
  if (filters.gender) {
    params.gender = filters.gender;
  }

  // Score vulnérabilité
  if (filters.vulnerabilityMin) {
    params.vulnerability_min = filters.vulnerabilityMin;
  }
  if (filters.vulnerabilityMax) {
    params.vulnerability_max = filters.vulnerabilityMax;
  }

  // Âge
  if (filters.ageMin) {
    params.age_min = filters.ageMin;
  }
  if (filters.ageMax) {
    params.age_max = filters.ageMax;
  }

  // Statut
  if (filters.status) {
    params.status = filters.status;
  }

  return params;
}