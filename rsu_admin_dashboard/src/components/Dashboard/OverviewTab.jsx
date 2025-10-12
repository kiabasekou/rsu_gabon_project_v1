import React from 'react';
import { 
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from 'recharts';
import { Users, Home, CheckCircle, AlertCircle, Globe, Calendar, Activity, Shield, RefreshCw } from 'lucide-react'; 
import StatCard from './StatCard'; 

export default function OverviewTab({ data, loading = false, error = null, onRefresh }) {
  
  // LOGGING POUR DEBUG
  console.log('📊 OverviewTab received data:', data);
  console.log('📊 Province data:', data?.province_distribution);

  // AFFICHER ERREUR
  if (error) {
    const errorMessage = typeof error === 'object' && error !== null ? error.message || JSON.stringify(error) : error;
    
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <AlertCircle className="text-red-600 mx-auto mb-4" size={48} />
        <h3 className="text-lg font-bold text-red-800 mb-2">Erreur de chargement</h3>
        <p className="text-red-600">{errorMessage}</p>
        <button 
          onClick={onRefresh}
          className="mt-4 px-4 py-2 text-sm bg-gray-200 rounded hover:bg-gray-300 flex items-center mx-auto"
        >
          <RefreshCw size={16} className="mr-2" /> Réessayer
        </button>
      </div>
    );
  }

  // EXTRACTION DONNÉES - Structure API Django exacte
  const stats = data?.stats || {};
  const provinceData = data?.province_distribution || [];
  const monthlyData = data?.monthly_enrollments || [];
  const vulnerabilityData = data?.vulnerability_distribution || [];

  // AFFICHER SPINNER PENDANT CHARGEMENT
  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg">Chargement des statistiques...</p>
        </div>
      </div>
    );
  }

  // AFFICHER MESSAGE SI AUCUNE DONNÉE
  if (!data || Object.keys(data).length === 0) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
        <AlertCircle className="text-yellow-600 mx-auto mb-4" size={48} />
        <h3 className="text-lg font-bold text-yellow-800 mb-2">Aucune donnée disponible</h3>
        <p className="text-yellow-600">L'API a retourné une réponse vide</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats principales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Bénéficiaires Totaux"
          value={stats.total_beneficiaries?.toLocaleString('fr-FR') || '0'}
          icon={Users}
          trend={stats.beneficiaries_growth || '+0%'}
          color="#3b82f6"
          loading={loading}
        />
        <StatCard
          title="Ménages Enregistrés"
          value={stats.total_households?.toLocaleString('fr-FR') || '0'}
          icon={Home}
          trend={stats.households_growth || '+0%'}
          color="#8b5cf6"
          loading={loading}
        />
        <StatCard
          title="Programmes Actifs"
          value={stats.active_programs || '0'}
          icon={CheckCircle}
          color="#10b981"
          loading={loading}
        />
        <StatCard
          title="Score Vulnérabilité Moyen"
          value={stats.avg_vulnerability_score?.toFixed(1) || '0.0'}
          icon={AlertCircle}
          color="#f59e0b"
          loading={loading}
        />
      </div>

      {/* Graphiques */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Distribution géographique */}
        {provinceData.length > 0 ? (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-bold mb-4 text-gray-800 flex items-center gap-2">
              <Globe size={20} className="text-blue-600" />
              Distribution Géographique ({provinceData.length} provinces)
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={provinceData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => {
                    // L'API retourne déjà 'percentage' OU on le calcule
                    const pct = entry.percentage || 0;
                    const name = entry.name || entry.province || 'N/A';
                    return `${name} ${pct.toFixed(1)}%`;
                  }}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                  nameKey="name"
                >
                  {provinceData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={`hsl(${index * 40}, 70%, 50%)`} />
                  ))}
                </Pie>
                <Tooltip 
                  formatter={(value, name, props) => {
                    const pct = props.payload.percentage || 0;
                    return [
                      `${value.toLocaleString('fr-FR')} personnes (${pct.toFixed(1)}%)`,
                      props.payload.name || props.payload.province
                    ];
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
            <div className="mt-4 text-xs text-gray-500 text-center">
              📡 Source: GET /analytics/dashboard/ - {provinceData.reduce((sum, p) => sum + (p.value || 0), 0).toLocaleString('fr-FR')} total
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-md p-6 text-center">
            <Globe size={40} className="text-gray-400 mx-auto mb-2" />
            <p className="text-gray-600">Aucune donnée géographique disponible</p>
          </div>
        )}

        {/* Tendances mensuelles */}
        {monthlyData.length > 0 ? (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-bold mb-4 text-gray-800 flex items-center gap-2">
              <Calendar size={20} className="text-green-600" />
              Enrôlements Mensuels
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={monthlyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis allowDecimals={false} />
                <Tooltip 
                   formatter={(value, name) => [value.toLocaleString('fr-FR'), name]}
                />
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
        ) : (
          <div className="bg-white rounded-lg shadow-md p-6 text-center">
            <Calendar size={40} className="text-gray-400 mx-auto mb-2" />
            <p className="text-gray-600">Aucune donnée mensuelle disponible</p>
          </div>
        )}
      </div>

      {/* Distribution vulnérabilité */}
      {vulnerabilityData.length > 0 ? (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-bold mb-4 text-gray-800 flex items-center gap-2">
            <Activity size={20} className="text-orange-600" />
            Distribution Score Vulnérabilité ({vulnerabilityData.reduce((sum, v) => sum + (v.count || 0), 0).toLocaleString('fr-FR')} évaluations)
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={vulnerabilityData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="category" />
              <YAxis allowDecimals={false} />
              <Tooltip 
                  formatter={(value, name) => [value.toLocaleString('fr-FR'), name]}
              />
              <Legend />
              <Bar dataKey="count" name="Nombre de bénéficiaires">
                {vulnerabilityData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color || `hsl(${index * 40 + 20}, 70%, 50%)`} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <div className="mt-4 text-xs text-gray-500 text-center">
            📡 Source: GET /analytics/dashboard/
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-md p-6 text-center">
          <Activity size={40} className="text-gray-400 mx-auto mb-2" />
          <p className="text-gray-600">Aucune donnée de vulnérabilité disponible</p>
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
              <li>✅ GET /programs/programs/</li>
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
            <p className="text-gray-700 font-medium">Statistiques:</p>
            <ul className="text-gray-600 text-xs mt-1 space-y-1">
              <li>📊 {(stats.total_beneficiaries || 0).toLocaleString('fr-FR')} bénéficiaires</li>
              <li>🏠 {(stats.total_households || 0).toLocaleString('fr-FR')} ménages</li>
              <li>📈 {stats.active_programs || 0} programmes actifs</li>
            </ul>
          </div>
        </div>
      </div>

      {/* DEBUG: Structure données */}
      <details className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <summary className="cursor-pointer text-sm font-mono text-gray-700 hover:text-blue-600">
          🔍 Debug: Structure données API (cliquer pour voir)
        </summary>
        <pre className="mt-2 text-xs overflow-auto max-h-96 bg-white p-4 rounded border border-gray-300">
          {JSON.stringify(data, null, 2)}
        </pre>
      </details>
    </div>
  );
}