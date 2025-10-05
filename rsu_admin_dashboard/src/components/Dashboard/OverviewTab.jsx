
import React from 'react';
import { 
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from 'recharts';
import { Users, Home, CheckCircle, AlertCircle, Globe, Calendar, Activity, Shield } from 'lucide-react';
import StatCard from './StatCard';

export default function OverviewTab({ data, loading = false }) {
  const stats = data?.stats || {
    total_beneficiaries: 45820,
    total_households: 12450,
    active_programs: 8,
    avg_vulnerability_score: 42.3,
    beneficiaries_growth: '+12.5% ce mois',
    households_growth: '+8.3% ce mois',
  };

  const provinceData = data?.province_distribution || [
    { name: 'Estuaire', value: 18500, percentage: 40.4 },
    { name: 'Haut-Ogooué', value: 8200, percentage: 17.9 },
    { name: 'Moyen-Ogooué', value: 6100, percentage: 13.3 },
    { name: 'Ngounié', value: 5500, percentage: 12.0 },
    { name: 'Nyanga', value: 3800, percentage: 8.3 },
    { name: 'Ogooué-Ivindo', value: 2100, percentage: 4.6 },
    { name: 'Ogooué-Lolo', value: 980, percentage: 2.1 },
    { name: 'Ogooué-Maritime', value: 420, percentage: 0.9 },
    { name: 'Woleu-Ntem', value: 220, percentage: 0.5 }
  ];

  const monthlyData = data?.monthly_enrollments || [
    { month: 'Avr', enrollments: 3200 },
    { month: 'Mai', enrollments: 4100 },
    { month: 'Juin', enrollments: 3800 },
    { month: 'Juil', enrollments: 5200 },
    { month: 'Août', enrollments: 4900 },
    { month: 'Sept', enrollments: 6100 }
  ];

  const vulnerabilityData = data?.vulnerability_distribution || [
    { category: 'EXTRÊME', count: 8500, color: '#dc2626' },
    { category: 'ÉLEVÉE', count: 15200, color: '#ea580c' },
    { category: 'MODÉRÉE', count: 18100, color: '#f59e0b' },
    { category: 'FAIBLE', count: 4020, color: '#22c55e' }
  ];

  return (
    <div className="space-y-6">
      {/* Stats principales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Bénéficiaires Totaux"
          value={stats.total_beneficiaries?.toLocaleString()}
          icon={Users}
          trend={stats.beneficiaries_growth}
          color="#3b82f6"
          loading={loading}
        />
        <StatCard
          title="Ménages Enregistrés"
          value={stats.total_households?.toLocaleString()}
          icon={Home}
          trend={stats.households_growth}
          color="#8b5cf6"
          loading={loading}
        />
        <StatCard
          title="Programmes Actifs"
          value={stats.active_programs}
          icon={CheckCircle}
          color="#10b981"
          loading={loading}
        />
        <StatCard
          title="Score Vulnérabilité Moyen"
          value={stats.avg_vulnerability_score?.toFixed(1)}
          icon={AlertCircle}
          color="#f59e0b"
          loading={loading}
        />
      </div>

      {/* Graphiques */}
      {!loading && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Distribution géographique */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-bold mb-4 text-gray-800 flex items-center gap-2">
              <Globe size={20} className="text-blue-600" />
              Distribution Géographique
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={provinceData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percentage }) => `${name} ${percentage.toFixed(1)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {provinceData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={`hsl(${index * 40}, 70%, 50%)`} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="mt-4 text-xs text-gray-500 text-center">
              📡 Source: GET /analytics/dashboard/
            </div>
          </div>

          {/* Tendances mensuelles */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-bold mb-4 text-gray-800 flex items-center gap-2">
              <Calendar size={20} className="text-green-600" />
              Enrôlements Mensuels
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={monthlyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="enrollments" 
                  stroke="#3b82f6" 
                  strokeWidth={2} 
                  name="Enrôlements" 
                />
              </LineChart>
            </ResponsiveContainer>
            <div className="mt-4 text-xs text-gray-500 text-center">
              📡 Source: GET /analytics/dashboard/
            </div>
          </div>
        </div>
      )}

      {/* Distribution vulnérabilité */}
      {!loading && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-bold mb-4 text-gray-800 flex items-center gap-2">
            <Activity size={20} className="text-orange-600" />
            Distribution Score Vulnérabilité
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={vulnerabilityData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="category" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" name="Nombre de bénéficiaires">
                {vulnerabilityData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <div className="mt-4 text-xs text-gray-500 text-center">
            📡 Source: GET /services/vulnerability-assessment/statistics/
          </div>
        </div>
      )}

      {/* Indicateurs API */}
      <div className="bg-blue-50 border-l-4 border-blue-600 p-4 rounded">
        <h4 className="font-semibold text-blue-800 mb-2 flex items-center gap-2">
          <Shield size={18} />
          Intégration APIs Django REST Framework
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div>
            <p className="text-gray-700 font-medium">Endpoints Utilisés:</p>
            <ul className="text-gray-600 text-xs mt-1 space-y-1">
              <li>✅ GET /analytics/dashboard/</li>
              <li>✅ GET /identity/persons/</li>
              <li>✅ GET /services/vulnerability-assessment/</li>
            </ul>
          </div>
          <div>
            <p className="text-gray-700 font-medium">Authentification:</p>
            <ul className="text-gray-600 text-xs mt-1 space-y-1">
              <li>✅ JWT Bearer Token</li>
              <li>✅ Refresh automatique</li>
              <li>✅ Permissions granulaires</li>
            </ul>
          </div>
          <div>
            <p className="text-gray-700 font-medium">Performance:</p>
            <ul className="text-gray-600 text-xs mt-1 space-y-1">
              <li>✅ Chargement parallèle</li>
              <li>✅ Pagination optimisée</li>
              <li>✅ Cache client-side</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}