/**
 * 🇬🇦 RSU Gabon - Tab Navigation
 * Standards Top 1% - Navigation Dashboard
 * Fichier: rsu_admin_dashboard/src/components/Dashboard/TabNavigation.jsx
 */

import React from 'react';

export default function TabNavigation({ activeTab, onTabChange }) {
  const tabs = [
    { id: 'overview', label: "Vue d'ensemble" },
    { id: 'beneficiaries', label: 'Bénéficiaires' },
    { id: 'programs', label: 'Programmes', badge: 'NEW' },  // ✅ NOUVEAU
    { id: 'analytics', label: 'Analytics IA' },
  ];

  return (
    <div className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <nav className="flex gap-8" role="tablist">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors relative ${
                activeTab === tab.id
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
              role="tab"
              aria-selected={activeTab === tab.id}
            >
              {tab.label}
              {tab.badge && (
                <span className="ml-2 px-2 py-0.5 text-xs bg-green-100 text-green-700 rounded-full font-semibold">
                  {tab.badge}
                </span>
              )}
            </button>
          ))}
        </nav>
      </div>
    </div>
  );
}