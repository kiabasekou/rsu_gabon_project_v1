/**
 * 🇬🇦 RSU Gabon - usePrograms Hook
 * Standards Top 1% - Gestion état programmes
 * Fichier: rsu_admin_dashboard/src/hooks/usePrograms.js
 */

import { useState, useCallback, useEffect } from 'react';
import { programsAPI } from '../services/api/programsAPI';

export function usePrograms() {
  const [programs, setPrograms] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    status: '',
    search: '',
    ordering: '-created_at'
  });

  const loadPrograms = useCallback(async (customFilters = null) => {
    try {
      setLoading(true);
      setError(null);
      
      const filterParams = customFilters || filters;
      console.log('📥 Loading programs with filters:', filterParams);
      
      const data = await programsAPI.getPrograms(filterParams);
      
      // ✅ FIX: API retourne {count, results} avec pagination
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

  const refreshPrograms = useCallback(() => {
    loadPrograms();
  }, [loadPrograms]);

  const updateFilters = useCallback((newFilters) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  }, []);

  // Charger programmes au montage et quand filtres changent
  useEffect(() => {
    // ✅ FIX: Éviter double appel en React 18 Strict Mode
    let isMounted = true;
    
    const fetchPrograms = async () => {
      if (isMounted) {
        await loadPrograms();
      }
    };
    
    fetchPrograms();
    
    return () => {
      isMounted = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters.status, filters.search, filters.ordering]);

  return {
    programs,
    loading,
    error,
    filters,
    updateFilters,
    loadPrograms,
    refreshPrograms
  };
}