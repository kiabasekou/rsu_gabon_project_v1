/**
 * 🇬🇦 RSU Gabon - Dashboard Hook CORRIGÉ
 * Standards Top 1% - FIX Boucle Infinie
 * Fichier: rsu_admin_dashboard/src/hooks/useDashboard.js
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import apiClient from '../services/api/apiClient';
import ENDPOINTS from '../services/api/endpoints';

export function useDashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  /**
   * Chargement données Dashboard depuis API Django
   */
  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.get(ENDPOINTS.ANALYTICS.DASHBOARD);
      
      setData(response);
      setLastUpdate(new Date());
      setLoading(false);
      
      console.log('✅ Dashboard data loaded:', response);
    } catch (err) {
      console.error('❌ Dashboard error:', err);
      setError(err.message || 'Erreur de connexion au backend');
      setLoading(false);
    }
  }, []); // ✅ Pas de dépendances - stable

  /**
   * Chargement initial
   */
  useEffect(() => {
    loadData();
  }, [loadData]);

  /**
   * Rechargement manuel
   */
  const refresh = useCallback(() => {
    return loadData();
  }, [loadData]);

  return {
    data,
    loading,
    error,
    lastUpdate,
    refresh,
  };
}

/**
 * Hook pour bénéficiaires - CORRIGÉ
 */
export function useBeneficiaries(filters = {}) {
  const [beneficiaries, setBeneficiaries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 50,
    total: 0,
  });

  // ✅ Utiliser useRef pour éviter re-création fonction à chaque render
  const filtersRef = useRef(filters);
  
  // ✅ Mettre à jour ref seulement si filters change vraiment
  useEffect(() => {
    filtersRef.current = filters;
  }, [filters]);

  const loadBeneficiaries = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.get(ENDPOINTS.IDENTITY.PERSONS, {
        page: pagination.page,
        page_size: pagination.pageSize,
        ...filtersRef.current, // ✅ Utiliser ref au lieu de dépendance
      });
      
      setBeneficiaries(response.results || []);
      setPagination(prev => ({
        ...prev,
        total: response.count || 0,
      }));
      setLoading(false);
      
      console.log('✅ Beneficiaries loaded:', response.results?.length);
    } catch (err) {
      console.error('❌ Beneficiaries error:', err);
      setError(err.message);
      setLoading(false);
    }
  }, [pagination.page, pagination.pageSize]); // ✅ Seulement pagination, pas filters

  // ✅ Chargement initial - SEULEMENT au montage du composant
  useEffect(() => {
    loadBeneficiaries();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // ✅ Tableau vide = exécution unique

  // ✅ Fonction refresh manuelle
  const refresh = useCallback(() => {
    return loadBeneficiaries();
  }, [loadBeneficiaries]);

  return {
    beneficiaries,
    loading,
    error,
    pagination,
    refresh,
  };
}