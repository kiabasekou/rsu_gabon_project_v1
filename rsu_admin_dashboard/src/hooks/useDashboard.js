import { useState, useEffect } from 'react';
import apiClient from '../services/api/apiClient';
import ENDPOINTS from '../services/api/endpoints';

export function useDashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.get(ENDPOINTS.ANALYTICS.DASHBOARD);
      setData(response);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return {
    data,
    loading,
    error,
    refresh: loadData,
  };
}