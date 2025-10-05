import React from 'react';

export default function TabNavigation({ activeTab, onTabChange }) {
  const tabs = [
    { id: 'overview', label: "Vue d'ensemble" },
    { id: 'beneficiaries', label: 'Bénéficiaires' },
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
              className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                activeTab === tab.id
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
              role="tab"
              aria-selected={activeTab === tab.id}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>
    </div>
  );
}