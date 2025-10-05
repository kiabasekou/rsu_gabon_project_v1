import React from 'react';
import { TrendingUp } from 'lucide-react';

export default function StatCard({ 
  title, 
  value, 
  icon: Icon, 
  trend, 
  color = '#3b82f6',
  loading = false 
}) {
  return (
    <div 
      className="bg-white rounded-lg shadow-md p-6 border-l-4 transition-transform hover:scale-105"
      style={{ borderLeftColor: color }}
    >
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <p className="text-gray-600 text-sm font-medium mb-2">{title}</p>
          
          {loading ? (
            <div className="h-8 bg-gray-200 rounded animate-pulse w-24" />
          ) : (
            <h3 className="text-3xl font-bold mt-2 mb-1" style={{ color }}>
              {value}
            </h3>
          )}
          
          {trend && !loading && (
            <p className="text-sm text-green-600 mt-2 flex items-center gap-1">
              <TrendingUp size={16} />
              {trend}
            </p>
          )}
        </div>

        <div className="p-3 rounded-full" style={{ backgroundColor: `${color}20` }}>
          {Icon && <Icon size={24} style={{ color }} />}
        </div>
      </div>
    </div>
  );
}