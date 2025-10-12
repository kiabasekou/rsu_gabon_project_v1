/**
 * 🇬🇦 RSU Gabon - Program Detail ENRICHI
 * Standards Top 1% - Vue Détaillée avec 4 Onglets Fonctionnels
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
  Edit, Pause, Play, StopCircle, Download, Search,
  Filter, Check, X, FileText, CreditCard
} from 'lucide-react';
import { programsAPI } from '../../services/api/programsAPI';

export default function ProgramDetail({ programId, onBack }) {
  const [program, setProgram] = useState(null);
  const [statistics, setStatistics] = useState(null);
  const [enrollments, setEnrollments] = useState([]);
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  
  // Filtres onglet Bénéficiaires
  const [enrollmentFilters, setEnrollmentFilters] = useState({
    status: '',
    search: ''
  });

  useEffect(() => {
    loadProgramDetails();
  }, [programId]);

  useEffect(() => {
    if (activeTab === 'beneficiaries') {
      loadEnrollments();
    } else if (activeTab === 'payments') {
      loadPayments();
    }
  }, [activeTab, enrollmentFilters]);

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

  const loadEnrollments = async () => {
    try {
      const data = await programsAPI.getEnrollments(programId, enrollmentFilters);
      setEnrollments(data.results || data || []);
      console.log(`✅ ${data.results?.length || data.length || 0} inscriptions chargées`);
    } catch (error) {
      console.error('Erreur chargement inscriptions:', error);
      setEnrollments([]);
    }
  };

  const loadPayments = async () => {
    try {
      const data = await programsAPI.getPayments(programId);
      setPayments(data.results || data || []);
      console.log(`✅ ${data.results?.length || data.length || 0} paiements chargés`);
    } catch (error) {
      console.error('Erreur chargement paiements:', error);
      setPayments([]);
    }
  };

  const handleEnrollmentAction = async (enrollmentId, action) => {
    try {
      if (action === 'approve') {
        await programsAPI.approveEnrollment(enrollmentId);
        console.log('✅ Inscription approuvée');
      } else if (action === 'reject') {
        await programsAPI.rejectEnrollment(enrollmentId);
        console.log('✅ Inscription rejetée');
      }
      loadEnrollments(); // Rafraîchir liste
    } catch (error) {
      console.error(`❌ Erreur ${action}:`, error);
    }
  };

  // === HELPERS ===
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'XAF',
      minimumFractionDigits: 0
    }).format(amount);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: 'long',
      year: 'numeric'
    });
  };

  const getStatusBadge = (status) => {
    const styles = {
      ACTIVE: 'bg-green-100 text-green-800 border-green-300',
      DRAFT: 'bg-blue-100 text-blue-800 border-blue-300',
      PAUSED: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      CLOSED: 'bg-gray-100 text-gray-800 border-gray-300',
      PENDING: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      APPROVED: 'bg-green-100 text-green-800 border-green-300',
      REJECTED: 'bg-red-100 text-red-800 border-red-300',
      COMPLETED: 'bg-blue-100 text-blue-800 border-blue-300'
    };
    const labels = {
      ACTIVE: 'Actif', DRAFT: 'Brouillon', PAUSED: 'Suspendu', CLOSED: 'Clôturé',
      PENDING: 'En attente', APPROVED: 'Approuvé', REJECTED: 'Rejeté',
      COMPLETED: 'Terminé', SUSPENDED: 'Suspendu'
    };
    return (
      <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${styles[status] || styles.DRAFT}`}>
        {labels[status] || status}
      </span>
    );
  };

  // === LOADING STATE ===
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

  if (!program) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="mx-auto text-gray-400 mb-4" size={48} />
        <h3 className="text-xl font-semibold text-gray-700">Programme introuvable</h3>
        <button onClick={onBack} className="mt-4 text-blue-600 hover:underline">
          ← Retour à la liste
        </button>
      </div>
    );
  }

  // === RENDER TABS CONTENT ===
  const renderOverviewTab = () => {
    const budgetData = [
      { name: 'Dépensé', value: parseFloat(program.budget_spent || 0), color: '#3b82f6' },
      { name: 'Disponible', value: parseFloat(program.total_budget || 0) - parseFloat(program.budget_spent || 0), color: '#e5e7eb' }
    ];

    const capacityData = [
      { name: 'Bénéficiaires', value: program.current_beneficiaries || 0, color: '#10b981' },
      { name: 'Places restantes', value: (program.max_beneficiaries || 0) - (program.current_beneficiaries || 0), color: '#e5e7eb' }
    ];

    return (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 p-6">
        {/* Graphique Budget */}
        <div className="bg-white rounded-lg border p-6">
          <h4 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <DollarSign size={20} className="text-blue-600" />
            Répartition Budget
          </h4>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={budgetData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={(entry) => `${entry.name}: ${formatCurrency(entry.value)}`}
                outerRadius={80}
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
          <div className="mt-4 text-center">
            <p className="text-sm text-gray-600">
              Taux d'exécution: <span className="font-bold text-blue-600">
                {((parseFloat(program.budget_spent) / parseFloat(program.total_budget)) * 100).toFixed(1)}%
              </span>
            </p>
          </div>
        </div>

        {/* Graphique Capacité */}
        <div className="bg-white rounded-lg border p-6">
          <h4 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <Users size={20} className="text-green-600" />
            Capacité Bénéficiaires
          </h4>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={capacityData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={(entry) => `${entry.name}: ${entry.value}`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {capacityData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <div className="mt-4 text-center">
            <p className="text-sm text-gray-600">
              Taux de remplissage: <span className="font-bold text-green-600">
                {((program.current_beneficiaries / program.max_beneficiaries) * 100).toFixed(1)}%
              </span>
            </p>
          </div>
        </div>

        {/* Objectifs */}
        <div className="bg-white rounded-lg border p-6 lg:col-span-2">
          <h4 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
            <TrendingUp size={20} className="text-purple-600" />
            Objectifs du Programme
          </h4>
          <p className="text-gray-700 whitespace-pre-line">
            {program.objectives || 'Aucun objectif défini'}
          </p>
        </div>
      </div>
    );
  };

  const renderBeneficiariesTab = () => {
    return (
      <div className="p-6">
        {/* Filtres */}
        <div className="bg-white rounded-lg border p-4 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
              <input
                type="text"
                placeholder="Rechercher par nom..."
                className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                value={enrollmentFilters.search}
                onChange={(e) => setEnrollmentFilters(prev => ({ ...prev, search: e.target.value }))}
              />
            </div>
            <select
              className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              value={enrollmentFilters.status}
              onChange={(e) => setEnrollmentFilters(prev => ({ ...prev, status: e.target.value }))}
            >
              <option value="">Tous les statuts</option>
              <option value="PENDING">En attente</option>
              <option value="APPROVED">Approuvé</option>
              <option value="REJECTED">Rejeté</option>
              <option value="ACTIVE">Actif</option>
              <option value="SUSPENDED">Suspendu</option>
              <option value="COMPLETED">Terminé</option>
            </select>
            <button
              onClick={() => setEnrollmentFilters({ status: '', search: '' })}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
            >
              <Filter size={18} className="inline mr-2" />
              Réinitialiser
            </button>
          </div>
        </div>

        {/* Table Inscriptions */}
        <div className="bg-white rounded-lg border overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    Bénéficiaire
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    Date Inscription
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    Statut
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {enrollments.length === 0 ? (
                  <tr>
                    <td colSpan="4" className="px-6 py-8 text-center text-gray-500">
                      <Users className="mx-auto mb-2 text-gray-400" size={32} />
                      Aucune inscription trouvée
                    </td>
                  </tr>
                ) : (
                  enrollments.map((enrollment) => (
                    <tr key={enrollment.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div className="font-medium text-gray-900">
                          {enrollment.beneficiary_name || `ID: ${enrollment.beneficiary}`}
                        </div>
                        <div className="text-sm text-gray-500">
                          NIP: {enrollment.beneficiary_nip || 'N/A'}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-700">
                        {formatDate(enrollment.enrollment_date)}
                      </td>
                      <td className="px-6 py-4">
                        {getStatusBadge(enrollment.status)}
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex gap-2">
                          {enrollment.status === 'PENDING' && (
                            <>
                              <button
                                onClick={() => handleEnrollmentAction(enrollment.id, 'approve')}
                                className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                                title="Approuver"
                              >
                                <Check size={18} />
                              </button>
                              <button
                                onClick={() => handleEnrollmentAction(enrollment.id, 'reject')}
                                className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                                title="Rejeter"
                              >
                                <X size={18} />
                              </button>
                            </>
                          )}
                          <button
                            className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                            title="Voir détails"
                          >
                            <FileText size={18} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Statistiques */}
        {enrollments.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
            {['PENDING', 'APPROVED', 'REJECTED', 'ACTIVE'].map(status => {
              const count = enrollments.filter(e => e.status === status).length;
              return (
                <div key={status} className="bg-white rounded-lg border p-4">
                  <div className="text-sm text-gray-600 mb-1">
                    {status === 'PENDING' ? 'En attente' :
                     status === 'APPROVED' ? 'Approuvés' :
                     status === 'REJECTED' ? 'Rejetés' : 'Actifs'}
                  </div>
                  <div className="text-2xl font-bold text-gray-900">{count}</div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    );
  };

  const renderPaymentsTab = () => {
    return (
      <div className="p-6">
        {/* Timeline Paiements */}
        <div className="bg-white rounded-lg border p-6">
          <h4 className="font-semibold text-gray-800 mb-6 flex items-center gap-2">
            <CreditCard size={20} className="text-green-600" />
            Historique des Paiements
          </h4>

          {payments.length === 0 ? (
            <div className="text-center py-12">
              <CreditCard className="mx-auto mb-4 text-gray-400" size={48} />
              <p className="text-gray-500">Aucun paiement effectué</p>
            </div>
          ) : (
            <div className="space-y-4">
              {payments.map((payment, index) => (
                <div key={payment.id} className="flex items-start gap-4 pb-4 border-b last:border-0">
                  <div className="flex-shrink-0">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                      payment.status === 'COMPLETED' ? 'bg-green-100 text-green-600' :
                      payment.status === 'PENDING' ? 'bg-yellow-100 text-yellow-600' :
                      'bg-red-100 text-red-600'
                    }`}>
                      {payment.status === 'COMPLETED' ? <CheckCircle size={20} /> :
                       payment.status === 'PENDING' ? <Clock size={20} /> :
                       <XCircle size={20} />}
                    </div>
                  </div>
                  <div className="flex-grow">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-medium text-gray-900">
                          Paiement #{payment.reference || payment.id}
                        </p>
                        <p className="text-sm text-gray-500">
                          {formatDate(payment.payment_date || payment.created_at)}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-lg text-gray-900">
                          {formatCurrency(payment.amount)}
                        </p>
                        {getStatusBadge(payment.status)}
                      </div>
                    </div>
                    {payment.beneficiary_name && (
                      <p className="text-sm text-gray-600 mt-1">
                        Bénéficiaire: {payment.beneficiary_name}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Statistiques Paiements */}
        {payments.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
            <div className="bg-white rounded-lg border p-4">
              <div className="text-sm text-gray-600 mb-1">Total Payé</div>
              <div className="text-2xl font-bold text-gray-900">
                {formatCurrency(payments.reduce((sum, p) => sum + parseFloat(p.amount || 0), 0))}
              </div>
            </div>
            <div className="bg-white rounded-lg border p-4">
              <div className="text-sm text-gray-600 mb-1">Nombre de Paiements</div>
              <div className="text-2xl font-bold text-gray-900">{payments.length}</div>
            </div>
            <div className="bg-white rounded-lg border p-4">
              <div className="text-sm text-gray-600 mb-1">Taux de Succès</div>
              <div className="text-2xl font-bold text-green-600">
                {((payments.filter(p => p.status === 'COMPLETED').length / payments.length) * 100).toFixed(0)}%
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderAnalyticsTab = () => {
    return (
      <div className="p-6">
        <div className="bg-white rounded-lg border p-8 text-center">
          <Activity className="mx-auto mb-4 text-purple-600" size={48} />
          <h3 className="text-xl font-bold text-gray-800 mb-2">
            Analytics Avancées
          </h3>
          <p className="text-gray-600 mb-4">
            Prédictions ML, détection fraude, et recommandations IA
          </p>
          <p className="text-sm text-gray-500">
            Module en développement - Disponible prochainement
          </p>
        </div>
      </div>
    );
  };

  // === MAIN RENDER ===
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <button
          onClick={onBack}
          className="mb-4 flex items-center gap-2 text-blue-600 hover:text-blue-800 transition-colors"
        >
          <ArrowLeft size={20} />
          Retour à la liste
        </button>

        <div className="flex justify-between items-start">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h2 className="text-2xl font-bold text-gray-800">{program.name}</h2>
              {getStatusBadge(program.status)}
            </div>
            <p className="text-gray-600 mb-1">Code: <span className="font-mono font-semibold">{program.code}</span></p>
            <p className="text-gray-600">Catégorie: {program.category_name || 'N/A'}</p>
          </div>

          <div className="flex gap-2">
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

        {/* Infos clés */}
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

      {/* Tabs Navigation */}
      <div className="bg-white rounded-lg shadow-md">
        <div className="border-b border-gray-200">
          <nav className="flex gap-8 px-6" role="tablist">
            {[
              { id: 'overview', label: 'Vue d\'ensemble', icon: Activity },
              { id: 'beneficiaries', label: 'Bénéficiaires', icon: Users },
              { id: 'payments', label: 'Paiements', icon: CreditCard },
              { id: 'analytics', label: 'Analytics', icon: TrendingUp }
            ].map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setActiveTab(id)}
                className={`py-4 border-b-2 font-medium text-sm transition-colors flex items-center gap-2 ${
                  activeTab === id
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
                role="tab"
                aria-selected={activeTab === id}
              >
                <Icon size={18} />
                {label}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        <div role="tabpanel">
          {activeTab === 'overview' && renderOverviewTab()}
          {activeTab === 'beneficiaries' && renderBeneficiariesTab()}
          {activeTab === 'payments' && renderPaymentsTab()}
          {activeTab === 'analytics' && renderAnalyticsTab()}
        </div>
      </div>
    </div>
  );
}