/**
 * 🇬🇦 RSU Gabon - Programs Hook
 * Hook pour gestion des programmes sociaux
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import programsAPI from '../services/api/programsAPI';

export function usePrograms(options = {}) {
  const { autoLoad = true, initialFilters = {} } = options;

  const [programs, setPrograms] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 10,
    total: 0
  });

  const filtersRef = useRef(initialFilters);

  const loadPrograms = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await programsAPI.getPrograms({
        page: pagination.page,
        page_size: pagination.pageSize,
        ...filtersRef.current
      });

      setPrograms(response.results || []);
      setPagination(prev => ({
        ...prev,
        total: response.count || 0
      }));

      console.log('✅ Programs loaded:', response.results?.length);
    } catch (err) {
      console.error('❌ Programs error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [pagination.page, pagination.pageSize]);

  useEffect(() => {
    if (autoLoad) {
      loadPrograms();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const setFilters = useCallback((newFilters) => {
    filtersRef.current = { ...filtersRef.current, ...newFilters };
    setPagination(prev => ({ ...prev, page: 1 }));
    loadPrograms();
  }, [loadPrograms]);

  const refresh = useCallback(() => {
    return loadPrograms();
  }, [loadPrograms]);

  return {
    programs,
    loading,
    error,
    pagination,
    setFilters,
    refresh
  };
}