/**
 * 🇬🇦 RSU Gabon - Page Login
 * FIX: URL correcte sans duplication
 * Fichier: src/pages/Login.jsx
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Lock, User, AlertCircle } from 'lucide-react';

// ✅ Importer endpoints depuis le bon fichier
import API_ENDPOINTS from '../services/api/endpoints';

export default function Login() {
  const navigate = useNavigate();
  const [credentials, setCredentials] = useState({
    username: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // 🔍 DEBUG - À retirer après test
    console.log('🔍 DEBUG endpoints.js:');
    console.log('   API_ENDPOINTS:', API_ENDPOINTS);
    console.log('   AUTH.TOKEN:', API_ENDPOINTS.AUTH.TOKEN);
    console.log('   Contient duplication?', API_ENDPOINTS.AUTH.TOKEN.includes('/api/v1/api/v1'));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // ✅ CORRECTION: Ne PAS ajouter /api/v1 dans l'URL
      // Car il est déjà dans API_ENDPOINTS.AUTH.TOKEN
      const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      console.log('🔍 API_BASE_URL:', API_BASE_URL);  // ← AJOUTER CETTE LIGNE
      console.log('🔍 process.env:', process.env.REACT_APP_API_URL);  // ← ET CELLE-CI
      const fullUrl = `${API_BASE_URL}${API_ENDPOINTS.AUTH.TOKEN}`;
      
      console.log('🔐 Tentative login:', fullUrl);
      
      const response = await fetch(fullUrl, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json' 
        },
        body: JSON.stringify(credentials)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Identifiants invalides');
      }

      const data = await response.json();

      // Stockage tokens
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);

      // Stocker info utilisateur si disponible
      if (data.user) {
        localStorage.setItem('current_user', JSON.stringify(data.user));
      }

      console.log('✅ Login réussi');

      // Redirection vers dashboard
      navigate('/dashboard');

    } catch (err) {
      console.error('❌ Erreur login:', err);
      setError(err.message || 'Erreur de connexion');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 to-indigo-800 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8">
        {/* Logo et titre */}
        <div className="text-center mb-8">
          <div className="bg-blue-600 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
            <Lock className="text-white" size={32} />
          </div>
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            RSU Gabon
          </h1>
          <p className="text-gray-600">
            Registre Social Unifié
          </p>
        </div>

        {/* Formulaire */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Erreur */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
              <AlertCircle className="text-red-600 flex-shrink-0" size={20} />
              <div className="text-sm text-red-800">{error}</div>
            </div>
          )}

          {/* Username */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Nom d'utilisateur
            </label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                value={credentials.username}
                onChange={(e) => setCredentials({ ...credentials, username: e.target.value })}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="admin"
                required
                autoFocus
              />
            </div>
          </div>

          {/* Password */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Mot de passe
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="password"
                value={credentials.password}
                onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="••••••••"
                required
              />
            </div>
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
            className={`
              w-full py-3 rounded-lg font-semibold text-white transition-colors
              ${loading 
                ? 'bg-gray-400 cursor-not-allowed' 
                : 'bg-blue-600 hover:bg-blue-700'
              }
            `}
          >
            {loading ? 'Connexion...' : 'Se connecter'}
          </button>
        </form>

        {/* Info */}
        <div className="mt-6 text-center text-sm text-gray-500">
          <p>Projet Digital Gabon</p>
          <p className="text-xs mt-1">Financé par la Banque Mondiale</p>
        </div>

        {/* Debug info (à retirer en production) */}
        <div className="mt-4 p-3 bg-gray-50 rounded text-xs text-gray-600">
          <div className="font-semibold mb-1">Debug Info:</div>
          <div>Backend: {process.env.REACT_APP_API_URL || 'http://localhost:8000'}</div>
          <div>Endpoint: {API_ENDPOINTS.AUTH.TOKEN}</div>
        </div>
      </div>
    </div>
  );
}