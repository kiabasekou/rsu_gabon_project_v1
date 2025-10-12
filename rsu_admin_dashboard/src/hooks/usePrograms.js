/**
 * 🇬🇦 RSU Gabon - usePrograms Hook CORRIGÉ
 * Standards Top 1% - FIX Boucle Infinie
 * Fichier: rsu_admin_dashboard/src/hooks/usePrograms.js
 */

import { useState, useCallback, useEffect, useRef } from 'react';
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

  // ✅ Utiliser useRef pour éviter re-renders
  const filtersRef = useRef(filters);
  const hasMounted = useRef(false);

  // ✅ Mettre à jour ref quand filters change
  useEffect(() => {
    filtersRef.current = filters;
  }, [filters]);

  const loadPrograms = useCallback(async (customFilters = null) => {
    try {
      setLoading(true);
      setError(null);
      
      const filterParams = customFilters || filtersRef.current;
      console.log('📥 Loading programs with filters:', filterParams);
      
      const data = await programsAPI.getPrograms(filterParams);
      
      // ✅ Gérer structure pagination Django
      const programsList = data.results || [];
      
      setPrograms(programsList);
      console.log(`✅ Programs loaded: ${programsList.length}`);
    } catch (err) {
      setError(err.message);
      console.error('❌ Programs error:', err);
    } finally {
      setLoading(false);
    }
  }, []); // ✅ Pas de dépendances - fonction stable

  const refreshPrograms = useCallback(() => {
    return loadPrograms();
  }, [loadPrograms]);

  const updateFilters = useCallback((newFilters) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  }, []);

  // ✅ Charger programmes SEULEMENT au montage initial
  useEffect(() => {
    if (!hasMounted.current) {
      hasMounted.current = true;
      loadPrograms();
    }
  }, [loadPrograms]);

  // ✅ Recharger SEULEMENT si filtres changent (mais pas au montage initial)
  useEffect(() => {
    if (hasMounted.current) {
      // Petit délai pour éviter appels multiples rapides
      const timeoutId = setTimeout(() => {
        loadPrograms();
      }, 300);

      return () => clearTimeout(timeoutId);
    }
  }, [filters.status, filters.search, filters.ordering, loadPrograms]);

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