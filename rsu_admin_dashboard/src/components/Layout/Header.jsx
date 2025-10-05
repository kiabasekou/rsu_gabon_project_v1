import React from 'react';
import { RefreshCw } from 'lucide-react';

export default function Header({ currentUser, onRefresh, loading = false }) {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-br from-green-600 to-yellow-500 rounded-lg flex items-center justify-center text-white font-bold text-xl">
              🇬🇦
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                RSU Gabon - Dashboard Admin
              </h1>
              <p className="text-sm text-gray-500">
                Registre Social Unifié - Production Module
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {currentUser && (
              <div className="hidden sm:block text-right">
                <p className="text-sm font-semibold text-gray-700">
                  {currentUser.username}
                </p>
                <p className="text-xs text-gray-500">
                  {currentUser.user_type}
                </p>
              </div>
            )}

            <button
              onClick={onRefresh}
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 flex items-center gap-2 transition-colors"
            >
              <RefreshCw 
                size={16} 
                className={loading ? 'animate-spin' : ''} 
              />
              <span className="hidden sm:inline">Actualiser</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}