/**
 * 🇬🇦 RSU Gabon - usePrograms Hook
 * Standards Top 1% - Gestion état programmes
 * Fichier: rsu_admin_dashboard/src/hooks/usePrograms.js
 */

import { useState, useEffect, useCallback } from 'react';
import apiClient from '../services/api/apiClient';
import ENDPOINTS from '../services/api/endpoints';

// ✅ Supprimer l'import programsAPI si utilisation d'apiClient direct
// OU créer programsAPI.js et importer
import { programsAPI } from '../services/api/programsAPI';

export function usePrograms(filters = {}) {
  const [programs, setPrograms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 50,
    total: 0,
  });

  const loadPrograms = useCallback(async (customFilters = null) => {
    try {
      setLoading(true);
      setError(null);
      
      const filterParams = customFilters || filters;
      console.log('📥 Loading programs with filters:', filterParams);
      
      // ✅ OPTION A: Utiliser programsAPI
      const data = await programsAPI.getPrograms(filterParams);
      
      // ✅ OPTION B: Appel direct apiClient
      // const data = await apiClient.get(ENDPOINTS.PROGRAMS.PROGRAMS, filterParams);
      
      const programsList = data.results || [];
      
      setPrograms(programsList);
      console.log(`✅ Programs loaded: ${programsList.length}`);
    } catch (err) {
      setError(err.message);
      console.error('❌ Programs error:', err);
    } finally {
      setLoading(false);
    }
  }, [filters]);
  useEffect(() => {
    loadPrograms();
  }, [loadPrograms]);

  const refresh = useCallback(() => {
    return loadPrograms();
  }, [loadPrograms]);

  const setFilter = useCallback((newFilters) => {
    setPagination(prev => ({ ...prev, page: 1 }));
    loadPrograms();
  }, [loadPrograms]);

  return {
    programs,
    loading,
    error,
    pagination,
    refresh,
    setFilter,
  };
}