/**
 * 🇬🇦 RSU Gabon - Tab Navigation
 * Standards Top 1% - Navigation Dashboard avec Programs
 * Fichier: src/components/Dashboard/TabNavigation.jsx
 */

import React from 'react';
import { Home, Users, Briefcase, TrendingUp } from 'lucide-react';

export default function TabNavigation({ activeTab, onTabChange }) {
  const tabs = [
    {
      id: 'overview',
      label: 'Vue d\'ensemble',
      icon: Home,
      description: 'Statistiques générales'
    },
    {
      id: 'beneficiaries',
      label: 'Bénéficiaires',
      icon: Users,
      description: 'Gestion des personnes'
    },
    {
      id: 'programs',
      label: 'Programmes',
      icon: Briefcase,
      description: 'Programmes sociaux',
      badge: 'NEW',
      badgeColor: 'bg-purple-600'
    },
    {
      id: 'analytics',
      label: 'Analytics',
      icon: TrendingUp,
      description: 'Analyses avancées'
    }
  ];

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex space-x-8 overflow-x-auto">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;

            return (
              <button
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                className={`
                  relative flex items-center gap-3 px-4 py-4 border-b-2 transition-all
                  whitespace-nowrap group
                  ${isActive
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
                  }
                `}
              >
                <Icon 
                  size={20} 
                  className={isActive ? 'text-blue-600' : 'text-gray-500 group-hover:text-gray-700'}
                />
                
                <div className="flex flex-col items-start">
                  <div className="flex items-center gap-2">
                    <span className={`font-semibold ${isActive ? 'text-blue-600' : 'text-gray-700'}`}>
                      {tab.label}
                    </span>
                    {tab.badge && (
                      <span className={`text-xs px-2 py-0.5 rounded-full text-white ${tab.badgeColor || 'bg-blue-600'} animate-pulse`}>
                        {tab.badge}
                      </span>
                    )}
                  </div>
                  <span className="text-xs text-gray-500">
                    {tab.description}
                  </span>
                </div>

                {/* Indicateur actif */}
                {isActive && (
                  <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600" />
                )}
              </button>
            );
          })}
        </div>
      </div>
    </nav>
  );
}