/**
 * 🇬🇦 RSU Gabon - Program Detail Component
 * Standards Top 1% - Vue Détaillée Programme avec Graphiques Recharts
 * Fichier: rsu_admin_dashboard/src/components/Dashboard/ProgramDetail.jsx
 */

import React, { useState, useEffect } from 'react';
import {
  PieChart, Pie, Cell, BarChart, Bar, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import {
  ArrowLeft, DollarSign, Users, TrendingUp, Calendar,
  CheckCircle, Clock, XCircle, AlertTriangle, Activity,
  Edit, Pause, Play, StopCircle, Download
} from 'lucide-react';
import { programsAPI } from '../../services/api/programsAPI';

export default function ProgramDetail({ programId, onBack }) {
  const [program, setProgram] = useState(null);
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadProgramDetails();
  }, [programId]);

  const loadProgramDetails = async () => {
    try {
      setLoading(true);
      const [programData, statsData] = await Promise.all([
        programsAPI.getProgramById(programId),
        programsAPI.getProgramStatistics(programId)
      ]);
      setProgram(programData);
      setStatistics(statsData);
    } catch (error) {
      console.error('Erreur chargement programme:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Chargement des détails...</p>
        </div>
      </div>
    );
  }

  if (!program || !statistics) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="mx-auto text-red-600 mb-4" size={48} />
        <p className="text-gray-600">Programme introuvable</p>
      </div>
    );
  }

  // Couleurs statuts
  const statusColors = {
    ACTIVE: 'bg-green-100 text-green-800 border-green-300',
    DRAFT: 'bg-blue-100 text-blue-800 border-blue-300',
    PAUSED: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    CLOSED: 'bg-gray-100 text-gray-800 border-gray-300'
  };

  const statusLabels = {
    ACTIVE: 'Actif',
    DRAFT: 'Brouillon',
    PAUSED: 'Suspendu',
    CLOSED: 'Clôturé'
  };

  // Données graphiques budget
  const budgetData = [
    { name: 'Utilisé', value: parseFloat(statistics.budget.spent), color: '#ef4444' },
    { name: 'Disponible', value: parseFloat(statistics.budget.remaining), color: '#22c55e' }
  ];

  // Données graphiques inscriptions
  const enrollmentsData = [
    { name: 'En attente', count: statistics.enrollments.pending, color: '#f59e0b' },
    { name: 'Approuvées', count: statistics.enrollments.approved, color: '#3b82f6' },
    { name: 'Actives', count: statistics.enrollments.active, color: '#22c55e' },
    { name: 'Complétées', count: statistics.enrollments.completed, color: '#6b7280' },
    { name: 'Rejetées', count: statistics.enrollments.rejected, color: '#ef4444' }
  ];

  // Données graphiques paiements
  const paymentsData = [
    { name: 'Complétés', count: statistics.payments.completed, color: '#22c55e' },
    { name: 'En attente', count: statistics.payments.pending, color: '#f59e0b' },
    { name: 'Échoués', count: statistics.payments.failed, color: '#ef4444' }
  ];

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'XAF',
      minimumFractionDigits: 0
    }).format(amount);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <div className="space-y-6">
      {/* En-tête avec navigation */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <button
          onClick={onBack}
          className="mb-4 flex items-center gap-2 text-blue-600 hover:text-blue-700 transition-colors"
        >
          <ArrowLeft size={20} />
          <span>Retour à la liste</span>
        </button>

        <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold text-gray-800">{program.name}</h1>
              <span className={`px-3 py-1 rounded-full text-sm font-medium border ${statusColors[program.status]}`}>
                {statusLabels[program.status]}
              </span>
            </div>
            <p className="text-gray-600 mb-2">Code: <span className="font-mono font-semibold">{program.code}</span></p>
            {program.description && (
              <p className="text-gray-600 mt-3">{program.description}</p>
            )}
            {program.objectives && (
              <div className="mt-3">
                <p className="text-sm font-semibold text-gray-700">Objectifs:</p>
                <p className="text-sm text-gray-600">{program.objectives}</p>
              </div>
            )}
          </div>

          {/* Actions rapides */}
          <div className="flex flex-col gap-2">
            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2 transition-colors">
              <Edit size={18} />
              Modifier
            </button>
            {program.status === 'ACTIVE' ? (
              <button className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 flex items-center gap-2 transition-colors">
                <Pause size={18} />
                Suspendre
              </button>
            ) : program.status === 'PAUSED' ? (
              <button className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2 transition-colors">
                <Play size={18} />
                Réactiver
              </button>
            ) : null}
            <button className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 flex items-center gap-2 transition-colors">
              <Download size={18} />
              Exporter
            </button>
          </div>
        </div>

        {/* Informations clés */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-6 border-t">
          <div>
            <p className="text-sm text-gray-500">Date de début</p>
            <p className="font-semibold text-gray-800">{formatDate(program.start_date)}</p>
          </div>
          {program.end_date && (
            <div>
              <p className="text-sm text-gray-500">Date de fin</p>
              <p className="font-semibold text-gray-800">{formatDate(program.end_date)}</p>
            </div>
          )}
          <div>
            <p className="text-sm text-gray-500">Montant bénéfice</p>
            <p className="font-semibold text-gray-800">{formatCurrency(program.benefit_amount)}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Fréquence</p>
            <p className="font-semibold text-gray-800">
              {program.frequency === 'MONTHLY' ? 'Mensuel' :
               program.frequency === 'QUARTERLY' ? 'Trimestriel' :
               program.frequency === 'ANNUAL' ? 'Annuel' : 'Ponctuel'}
            </p>
          </div>
        </div>
      </div>

      {/* Onglets navigation */}
      <div className="bg-white rounded-lg shadow-md">
        <div className="border-b border-gray-200">
          <nav className="flex gap-8 px-6" role="tablist">
            {['overview', 'beneficiaries', 'payments', 'analytics'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-4 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                {tab === 'overview' && 'Vue d\'ensemble'}
                {tab === 'beneficiaries' && 'Bénéficiaires'}
                {tab === 'payments' && 'Paiements'}
                {tab === 'analytics' && 'Analytics'}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Statistiques Budget */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-6 border border-blue-200">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-sm font-semibold text-blue-800">Budget Total</h3>
                    <DollarSign className="text-blue-600" size={24} />
                  </div>
                  <p className="text-3xl font-bold text-blue-900">
                    {formatCurrency(statistics.budget.total)}
                  </p>
                </div>

                <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-lg p-6 border border-red-200">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-sm font-semibold text-red-800">Budget Utilisé</h3>
                    <TrendingUp className="text-red-600" size={24} />
                  </div>
                  <p className="text-3xl font-bold text-red-900">
                    {formatCurrency(statistics.budget.spent)}
                  </p>
                  <p className="text-sm text-red-600 mt-2">
                    {statistics.budget.percentage_used.toFixed(1)}% utilisé
                  </p>
                </div>

                <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-6 border border-green-200">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-sm font-semibold text-green-800">Budget Disponible</h3>
                    <CheckCircle className="text-green-600" size={24} />
                  </div>
                  <p className="text-3xl font-bold text-green-900">
                    {formatCurrency(statistics.budget.remaining)}
                  </p>
                </div>
              </div>

              {/* Graphiques Budget et Inscriptions */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Graphique Budget */}
                <div className="bg-white border rounded-lg p-6">
                  <h3 className="text-lg font-bold mb-4 text-gray-800 flex items-center gap-2">
                    <DollarSign size={20} className="text-blue-600" />
                    Utilisation Budget
                  </h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={budgetData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        outerRadius={100}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {budgetData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value) => formatCurrency(value)} />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="mt-4 p-4 bg-gray-50 rounded">
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div
                        className="bg-blue-600 h-3 rounded-full transition-all"
                        style={{ width: `${statistics.budget.percentage_used}%` }}
                      ></div>
                    </div>
                    <p className="text-sm text-gray-600 mt-2 text-center">
                      Taux d'utilisation: <span className="font-semibold">{statistics.budget.percentage_used.toFixed(1)}%</span>
                    </p>
                  </div>
                </div>

                {/* Graphique Inscriptions */}
                <div className="bg-white border rounded-lg p-6">
                  <h3 className="text-lg font-bold mb-4 text-gray-800 flex items-center gap-2">
                    <Users size={20} className="text-purple-600" />
                    Statut Inscriptions
                  </h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={enrollmentsData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" angle={-15} textAnchor="end" height={80} />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="count" name="Inscriptions">
                        {enrollmentsData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                  <div className="mt-4 grid grid-cols-3 gap-2 text-sm">
                    <div className="text-center p-2 bg-green-50 rounded">
                      <p className="font-semibold text-green-800">{statistics.enrollments.active}</p>
                      <p className="text-gray-600">Actives</p>
                    </div>
                    <div className="text-center p-2 bg-yellow-50 rounded">
                      <p className="font-semibold text-yellow-800">{statistics.enrollments.pending}</p>
                      <p className="text-gray-600">En attente</p>
                    </div>
                    <div className="text-center p-2 bg-gray-50 rounded">
                      <p className="font-semibold text-gray-800">{statistics.enrollments.total}</p>
                      <p className="text-gray-600">Total</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Capacité Bénéficiaires */}
              <div className="bg-white border rounded-lg p-6">
                <h3 className="text-lg font-bold mb-4 text-gray-800 flex items-center gap-2">
                  <Users size={20} className="text-indigo-600" />
                  Capacité Bénéficiaires
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="text-center">
                    <p className="text-4xl font-bold text-indigo-600">{statistics.beneficiaries.current}</p>
                    <p className="text-gray-600 mt-2">Bénéficiaires actuels</p>
                  </div>
                  <div className="text-center">
                    <p className="text-4xl font-bold text-gray-700">{statistics.beneficiaries.max || '∞'}</p>
                    <p className="text-gray-600 mt-2">Capacité maximum</p>
                  </div>
                  <div className="text-center">
                    <p className="text-4xl font-bold text-green-600">
                      {statistics.beneficiaries.remaining || '∞'}
                    </p>
                    <p className="text-gray-600 mt-2">Places restantes</p>
                  </div>
                </div>
                {statistics.beneficiaries.max && (
                  <div className="mt-6">
                    <div className="w-full bg-gray-200 rounded-full h-4">
                      <div
                        className={`h-4 rounded-full transition-all ${
                          statistics.beneficiaries.is_full ? 'bg-red-600' :
                          (statistics.beneficiaries.current / statistics.beneficiaries.max) > 0.8 ? 'bg-orange-600' :
                          'bg-green-600'
                        }`}
                        style={{
                          width: `${Math.min((statistics.beneficiaries.current / statistics.beneficiaries.max * 100), 100)}%`
                        }}
                      ></div>
                    </div>
                    <p className="text-sm text-gray-600 mt-2 text-center">
                      Taux de remplissage: <span className="font-semibold">
                        {((statistics.beneficiaries.current / statistics.beneficiaries.max) * 100).toFixed(1)}%
                      </span>
                      {statistics.beneficiaries.is_full && (
                        <span className="ml-2 text-red-600 font-semibold">⚠️ Programme complet</span>
                      )}
                    </p>
                  </div>
                )}
              </div>

              {/* Statistiques Paiements */}
              <div className="bg-white border rounded-lg p-6">
                <h3 className="text-lg font-bold mb-4 text-gray-800 flex items-center gap-2">
                  <Activity size={20} className="text-emerald-600" />
                  Statistiques Paiements
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-gray-600">Total</span>
                      <Calendar className="text-gray-400" size={18} />
                    </div>
                    <p className="text-2xl font-bold text-gray-800">{statistics.payments.total_count}</p>
                  </div>
                  <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-green-700">Complétés</span>
                      <CheckCircle className="text-green-600" size={18} />
                    </div>
                    <p className="text-2xl font-bold text-green-800">{statistics.payments.completed}</p>
                  </div>
                  <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-yellow-700">En attente</span>
                      <Clock className="text-yellow-600" size={18} />
                    </div>
                    <p className="text-2xl font-bold text-yellow-800">{statistics.payments.pending}</p>
                  </div>
                  <div className="bg-red-50 p-4 rounded-lg border border-red-200">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-red-700">Échoués</span>
                      <XCircle className="text-red-600" size={18} />
                    </div>
                    <p className="text-2xl font-bold text-red-800">{statistics.payments.failed}</p>
                  </div>
                </div>
                <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <p className="text-sm text-blue-700 mb-1">Montant total versé:</p>
                  <p className="text-3xl font-bold text-blue-900">
                    {formatCurrency(statistics.payments.total_amount)}
                  </p>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'beneficiaries' && (
            <div className="text-center py-12">
              <Users className="mx-auto text-gray-400 mb-4" size={48} />
              <p className="text-gray-600">Liste détaillée des bénéficiaires à implémenter</p>
              <p className="text-sm text-gray-500 mt-2">
                Endpoint disponible: GET /programs/programs/{programId}/enrollments/
              </p>
            </div>
          )}

          {activeTab === 'payments' && (
            <div className="text-center py-12">
              <DollarSign className="mx-auto text-gray-400 mb-4" size={48} />
              <p className="text-gray-600">Historique des paiements à implémenter</p>
              <p className="text-sm text-gray-500 mt-2">
                Endpoint disponible: GET /programs/payments/?program={programId}
              </p>
            </div>
          )}

          {activeTab === 'analytics' && (
            <div className="text-center py-12">
              <Activity className="mx-auto text-gray-400 mb-4" size={48} />
              <p className="text-gray-600">Analytics avancés à implémenter</p>
              <p className="text-sm text-gray-500 mt-2">
                Prévisions ML, tendances, recommandations
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Informations API */}
      <div className="bg-blue-50 border-l-4 border-blue-600 p-4 rounded text-sm">
        <p className="font-semibold text-blue-800 mb-2">📡 Sources de données:</p>
        <ul className="text-blue-700 space-y-1">
          <li>✅ GET /api/v1/programs/programs/{programId}/</li>
          <li>✅ GET /api/v1/programs/programs/{programId}/statistics/</li>
          <li className="text-blue-500">🔄 Rafraîchissement automatique toutes les 30s</li>
        </ul>
      </div>
    </div>
  );
}