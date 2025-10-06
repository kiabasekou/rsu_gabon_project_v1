/**
 * 🇬🇦 RSU Gabon - Dashboard Hook
 * Standards Top 1% - Gestion état Dashboard
 * Fichier: rsu_admin_dashboard/src/hooks/useDashboard.js
 */

import { useState, useEffect, useCallback } from 'react';
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
      // ✅ VRAIE REQUÊTE API au lieu de données simulées
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
  }, []);

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
 * Hook pour bénéficiaires
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

  const loadBeneficiaries = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.get(ENDPOINTS.IDENTITY.PERSONS, {
        page: pagination.page,
        page_size: pagination.pageSize,
        ...filters,
      });
      
      setBeneficiaries(response.results || []);
      setPagination(prev => ({
        ...prev,
        total: response.count || 0,
      }));
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  }, [filters, pagination.page, pagination.pageSize]);

  useEffect(() => {
    loadBeneficiaries();
  }, [loadBeneficiaries]);

  return {
    beneficiaries,
    loading,
    error,
    pagination,
    refresh: loadBeneficiaries,
  };
}