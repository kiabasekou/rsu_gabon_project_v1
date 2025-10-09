/**
 * 🇬🇦 RSU Gabon - Header Complet avec Logout
 * Standards Top 1% - Intégration Déconnexion
 * Fichier: rsu_admin_dashboard/src/components/Layout/Header.jsx
 */

import React from 'react';
import { Shield, RefreshCw, LogOut, User } from 'lucide-react';
import apiClient from '../../services/api/apiClient';

export default function Header({ currentUser, onRefresh, loading }) {
  const handleLogout = () => {
    if (window.confirm('Voulez-vous vraiment vous déconnecter ?')) {
      apiClient.logout();
    }
  };

  return (
    <header className="bg-gradient-to-r from-blue-600 to-blue-800 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          {/* Logo et titre */}
          <div className="flex items-center gap-3">
            <Shield size={40} className="text-white" />
            <div>
              <h1 className="text-2xl font-bold text-white">
                RSU Gabon Dashboard
              </h1>
              <p className="text-blue-200 text-sm">
                Registre Social Unifié - Administration
              </p>
            </div>
          </div>

          {/* Actions utilisateur */}
          <div className="flex items-center gap-4">
            {/* Bouton Refresh */}
            <button
              onClick={onRefresh}
              disabled={loading}
              className="px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              title="Rafraîchir les données"
            >
              <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
              <span className="hidden sm:inline">Actualiser</span>
            </button>

            {/* Info utilisateur */}
            <div className="flex items-center gap-3 bg-white/10 px-4 py-2 rounded-lg">
              <User size={20} className="text-white" />
              <div className="hidden sm:block">
                <p className="text-white font-semibold text-sm">
                  {currentUser?.username || 'Utilisateur'}
                </p>
                <p className="text-blue-200 text-xs">
                  {currentUser?.user_type || 'ADMIN'}
                </p>
              </div>
            </div>

            {/* Bouton Déconnexion */}
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors flex items-center gap-2"
              title="Se déconnecter"
            >
              <LogOut size={18} />
              <span className="hidden sm:inline">Déconnexion</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}