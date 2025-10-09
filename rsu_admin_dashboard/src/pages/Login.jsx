/**
 * 🇬🇦 RSU Gabon - Page Login
 * Standards Top 1% - Authentification Sécurisée
 * Fichier: rsu_admin_dashboard/src/pages/Login.jsx
 */

import React, { useState } from 'react';
import { Shield, AlertCircle, Loader } from 'lucide-react';
import apiClient from '../services/api/apiClient';
import ENDPOINTS from '../services/api/endpoints';

export default function Login() {
  const [credentials, setCredentials] = useState({
    username: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // 1. Appel API authentification
      const response = await fetch(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1'}${ENDPOINTS.AUTH.TOKEN}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(credentials)
        }
      );

      if (!response.ok) {
        throw new Error('Identifiants invalides');
      }

      const data = await response.json();

      // 2. Stockage tokens
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);

      // 3. Récupération profil utilisateur
      const userResponse = await apiClient.get(ENDPOINTS.CORE.CURRENT_USER);
      localStorage.setItem('user', JSON.stringify(userResponse));

      // 4. Redirection Dashboard
      window.location.href = '/dashboard';
    } catch (err) {
      console.error('Erreur login:', err);
      setError(err.message || 'Erreur de connexion');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 via-blue-700 to-blue-900 flex items-center justify-center p-4">
      <div className="max-w-md w-full space-y-8">
        {/* En-tête */}
        <div className="text-center">
          <div className="flex justify-center mb-4">
            <Shield size={64} className="text-white" />
          </div>
          <h1 className="text-4xl font-bold text-white mb-2">
            RSU Gabon
          </h1>
          <p className="text-blue-200 text-lg">
            Registre Social Unifié
          </p>
          <p className="text-blue-300 text-sm mt-2">
            République Gabonaise - Dashboard Administrateur
          </p>
        </div>

        {/* Formulaire Login */}
        <div className="bg-white rounded-2xl shadow-2xl p-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">
            Connexion Sécurisée
          </h2>

          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
              <AlertCircle className="text-red-600 flex-shrink-0 mt-0.5" size={20} />
              <div>
                <p className="text-red-800 font-semibold">Erreur d'authentification</p>
                <p className="text-red-600 text-sm">{error}</p>
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Username */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nom d'utilisateur
              </label>
              <input
                type="text"
                value={credentials.username}
                onChange={(e) => setCredentials(prev => ({ ...prev, username: e.target.value }))}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                placeholder="Votre identifiant"
                required
                disabled={loading}
                autoComplete="username"
              />
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Mot de passe
              </label>
              <input
                type="password"
                value={credentials.password}
                onChange={(e) => setCredentials(prev => ({ ...prev, password: e.target.value }))}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                placeholder="••••••••"
                required
                disabled={loading}
                autoComplete="current-password"
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading || !credentials.username || !credentials.password}
              className="w-full py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader className="animate-spin" size={20} />
                  Connexion en cours...
                </>
              ) : (
                <>
                  <Shield size={20} />
                  Se connecter
                </>
              )}
            </button>
          </form>

          {/* Footer */}
          <div className="mt-6 pt-6 border-t border-gray-200 text-center">
            <p className="text-xs text-gray-500">
              Authentification sécurisée JWT<br />
              Accès réservé au personnel autorisé
            </p>
          </div>
        </div>

        {/* Indicateurs environnement */}
        <div className="text-center text-blue-200 text-xs space-y-1">
          <p>Backend API: {process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1'}</p>
          <p>Version: 1.0.0 | Environnement: Development</p>
        </div>
      </div>
    </div>
  );
}