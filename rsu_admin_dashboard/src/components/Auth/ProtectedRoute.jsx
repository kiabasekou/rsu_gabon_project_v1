/**
 * 🇬🇦 RSU Gabon - Protected Route Component
 * Standards Top 1% - Sécurisation Navigation
 * Fichier: rsu_admin_dashboard/src/components/Auth/ProtectedRoute.jsx
 */

import React, { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { Loader, AlertCircle } from 'lucide-react';
import apiClient from '../../services/api/apiClient';
import ENDPOINTS from '../../services/api/endpoints';

export default function ProtectedRoute({ children }) {
  const [authState, setAuthState] = useState({
    isAuthenticated: false,
    isLoading: true,
    error: null
  });

  useEffect(() => {
    validateAuth();
  }, []);

  const validateAuth = async () => {
    const token = localStorage.getItem('access_token');

    // Pas de token → Redirection login
    if (!token) {
      setAuthState({ isAuthenticated: false, isLoading: false, error: null });
      return;
    }

    try {
      // Validation token via endpoint /me
      await apiClient.get(ENDPOINTS.CORE.CURRENT_USER);
      
      setAuthState({ isAuthenticated: true, isLoading: false, error: null });
    } catch (error) {
      // Token invalide ou expiré
      console.error('Token validation failed:', error);
      
      // Tentative refresh token
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          await refreshAccessToken(refreshToken);
          setAuthState({ isAuthenticated: true, isLoading: false, error: null });
        } catch (refreshError) {
          // Refresh échoué → Logout
          clearAuth();
          setAuthState({ isAuthenticated: false, isLoading: false, error: 'Session expirée' });
        }
      } else {
        clearAuth();
        setAuthState({ isAuthenticated: false, isLoading: false, error: 'Authentification requise' });
      }
    }
  };

  const refreshAccessToken = async (refreshToken) => {
    const response = await fetch(
      `${process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1'}${ENDPOINTS.AUTH.REFRESH}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: refreshToken })
      }
    );

    if (!response.ok) {
      throw new Error('Refresh token invalide');
    }

    const data = await response.json();
    localStorage.setItem('access_token', data.access);
    
    // Certains backends retournent un nouveau refresh token
    if (data.refresh) {
      localStorage.setItem('refresh_token', data.refresh);
    }
  };

  const clearAuth = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  };

  // État: Chargement
  if (authState.isLoading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <Loader className="animate-spin text-blue-600 mx-auto mb-4" size={48} />
          <p className="text-gray-600">Vérification de l'authentification...</p>
        </div>
      </div>
    );
  }

  // État: Non authentifié → Redirection
  if (!authState.isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // État: Authentifié → Affichage contenu
  return <>{children}</>;
}