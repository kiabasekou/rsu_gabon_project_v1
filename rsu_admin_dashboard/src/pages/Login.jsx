/**
 * 🇬🇦 RSU Gabon - Login Component FIX DÉFINITIF
 * FIX: URL hardcodée car .env non lu
 * Fichier: rsu_admin_dashboard/src/pages/Login.jsx
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { LogIn, AlertCircle } from 'lucide-react';

export default function Login() {
  const navigate = useNavigate();
  const [credentials, setCredentials] = useState({
    username: 'admin',
    password: 'admin123'
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // ✅ FIX DÉFINITIF: URL hardcodée avec /api/v1
      const loginUrl = 'http://localhost:8000/api/v1/auth/token/';
      
      console.log('🔐 URL complète tentative login:', loginUrl);

      const response = await fetch(loginUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Identifiants invalides');
      }

      const data = await response.json();
      
      console.log('✅ Login réussi');

      // Stocker tokens
      localStorage.setItem('access_token', data.access);
      if (data.refresh) {
        localStorage.setItem('refresh_token', data.refresh);
      }

      // Stocker info utilisateur si disponible
      if (data.user) {
        localStorage.setItem('user', JSON.stringify(data.user));
      }

      // Redirection
      navigate('/dashboard');
    } catch (err) {
      console.error('❌ Erreur login:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 to-blue-800 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-2xl w-full max-w-md p-8">
        {/* Logo et titre */}
        <div className="text-center mb-8">
          <div className="inline-block p-3 bg-blue-100 rounded-full mb-4">
            <LogIn className="text-blue-600" size={40} />
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
              <AlertCircle className="text-red-600 flex-shrink-0 mt-0.5" size={20} />
              <div>
                <p className="text-sm font-medium text-red-800">Erreur de connexion</p>
                <p className="text-sm text-red-600 mt-1">{error}</p>
              </div>
            </div>
          )}

          {/* Username */}
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
              Nom d'utilisateur
            </label>
            <input
              id="username"
              type="text"
              value={credentials.username}
              onChange={(e) => setCredentials({ ...credentials, username: e.target.value })}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="admin"
              required
              autoComplete="username"
            />
          </div>

          {/* Password */}
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
              Mot de passe
            </label>
            <input
              id="password"
              type="password"
              value={credentials.password}
              onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="••••••••"
              required
              autoComplete="current-password"
            />
          </div>

          {/* Bouton submit */}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                Connexion...
              </>
            ) : (
              <>
                <LogIn size={20} />
                Se connecter
              </>
            )}
          </button>
        </form>

        {/* Info développement */}
        <div className="mt-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
          <p className="text-xs text-gray-600 text-center">
            <span className="font-semibold">Environnement:</span> Développement
          </p>
          <p className="text-xs text-gray-500 text-center mt-1">
            Backend: http://localhost:8000/api/v1
          </p>
        </div>

        {/* Identifiants par défaut */}
        <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
          <p className="text-xs text-blue-800 text-center font-medium">
            💡 Identifiants par défaut
          </p>
          <p className="text-xs text-blue-600 text-center mt-1">
            Username: <code className="font-mono bg-white px-1 rounded">admin</code>
          </p>
          <p className="text-xs text-blue-600 text-center">
            Password: <code className="font-mono bg-white px-1 rounded">admin123</code>
          </p>
        </div>
      </div>
    </div>
  );
}