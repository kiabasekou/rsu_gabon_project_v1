import React, { useState, useEffect } from 'react';
import { 
  User, Home, MapPin, Camera, CheckCircle, AlertCircle, 
  Wifi, WifiOff, Upload, Download, Search, Plus, 
  ClipboardList, TrendingUp, Save, X, ChevronRight
} from 'lucide-react';

// Configuration API Backend
const API_BASE_URL = 'http://localhost:8000/api/v1';

// Provinces du Gabon (basé sur votre backend)
const GABON_PROVINCES = [
  'Estuaire', 'Haut-Ogooué', 'Moyen-Ogooué', 'Ngounié',
  'Nyanga', 'Ogooué-Ivindo', 'Ogooué-Lolo', 'Ogooué-Maritime', 'Woleu-Ntem'
];

// App Mobile Principale
export default function RSUSurveyorApp() {
  const [currentScreen, setCurrentScreen] = useState('dashboard');
  const [isOnline, setIsOnline] = useState(true);
  const [surveyor, setSurveyor] = useState({
    name: 'Jean MBOUMBA',
    id: 'SUR-GA-2025-001',
    province: 'Estuaire',
    department: 'Libreville'
  });
  const [pendingSync, setPendingSync] = useState(12);
  const [todayStats, setTodayStats] = useState({
    enrolled: 8,
    validated: 5,
    pending: 3
  });

  // Simulation changement connexion
  useEffect(() => {
    const interval = setInterval(() => {
      setIsOnline(Math.random() > 0.2); // 80% online
    }, 15000);
    return () => clearInterval(interval);
  }, []);

  // Header commun
  const AppHeader = () => (
    <div className="bg-gradient-to-r from-green-600 to-yellow-500 text-white p-4 shadow-lg">
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center text-green-600 font-bold text-xl">
            🇬🇦
          </div>
          <div>
            <h1 className="font-bold text-lg">RSU Gabon Mobile</h1>
            <p className="text-xs opacity-90">Enquêteur Terrain</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {isOnline ? (
            <div className="flex items-center gap-1 bg-green-500 px-2 py-1 rounded-full text-xs">
              <Wifi size={14} />
              En ligne
            </div>
          ) : (
            <div className="flex items-center gap-1 bg-red-500 px-2 py-1 rounded-full text-xs">
              <WifiOff size={14} />
              Hors ligne
            </div>
          )}
          {pendingSync > 0 && (
            <div className="bg-yellow-500 px-2 py-1 rounded-full text-xs font-semibold">
              {pendingSync} à sync
            </div>
          )}
        </div>
      </div>
    </div>
  );

  // Navigation Bottom
  const BottomNav = () => (
    <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-lg">
      <div className="flex justify-around">
        {[
          { id: 'dashboard', icon: Home, label: 'Accueil' },
          { id: 'enroll', icon: Plus, label: 'Enrôler' },
          { id: 'search', icon: Search, label: 'Rechercher' },
          { id: 'sync', icon: Upload, label: 'Sync' },
        ].map(({ id, icon: Icon, label }) => (
          <button
            key={id}
            onClick={() => setCurrentScreen(id)}
            className={`flex-1 py-3 flex flex-col items-center gap-1 ${
              currentScreen === id ? 'text-green-600' : 'text-gray-500'
            }`}
          >
            <Icon size={24} />
            <span className="text-xs font-medium">{label}</span>
          </button>
        ))}
      </div>
    </div>
  );

  // Screen: Dashboard
  const DashboardScreen = () => (
    <div className="p-4 pb-20 space-y-4">
      {/* Info enquêteur */}
      <div className="bg-white rounded-lg shadow-md p-4 border-l-4 border-green-600">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
            <User size={24} className="text-green-600" />
          </div>
          <div className="flex-1">
            <h3 className="font-bold text-gray-800">{surveyor.name}</h3>
            <p className="text-sm text-gray-600">{surveyor.id}</p>
            <p className="text-xs text-gray-500 flex items-center gap-1 mt-1">
              <MapPin size={12} />
              {surveyor.province} - {surveyor.department}
            </p>
          </div>
        </div>
      </div>

      {/* Stats du jour */}
      <div className="grid grid-cols-3 gap-3">
        <div className="bg-blue-50 rounded-lg p-3 border-l-4 border-blue-600">
          <p className="text-xs text-gray-600">Enrôlés</p>
          <p className="text-2xl font-bold text-blue-600">{todayStats.enrolled}</p>
        </div>
        <div className="bg-green-50 rounded-lg p-3 border-l-4 border-green-600">
          <p className="text-xs text-gray-600">Validés</p>
          <p className="text-2xl font-bold text-green-600">{todayStats.validated}</p>
        </div>
        <div className="bg-yellow-50 rounded-lg p-3 border-l-4 border-yellow-600">
          <p className="text-xs text-gray-600">En attente</p>
          <p className="text-2xl font-bold text-yellow-600">{todayStats.pending}</p>
        </div>
      </div>

      {/* Actions rapides */}
      <div className="bg-white rounded-lg shadow-md p-4">
        <h3 className="font-bold text-gray-800 mb-3">Actions Rapides</h3>
        <div className="space-y-2">
          <button 
            onClick={() => setCurrentScreen('enroll')}
            className="w-full bg-green-600 text-white py-3 rounded-lg flex items-center justify-center gap-2 hover:bg-green-700"
          >
            <Plus size={20} />
            Nouvel Enrôlement
          </button>
          <button 
            onClick={() => setCurrentScreen('search')}
            className="w-full bg-blue-600 text-white py-3 rounded-lg flex items-center justify-center gap-2 hover:bg-blue-700"
          >
            <Search size={20} />
            Rechercher Bénéficiaire
          </button>
        </div>
      </div>

      {/* Dernières activités */}
      <div className="bg-white rounded-lg shadow-md p-4">
        <h3 className="font-bold text-gray-800 mb-3">Activités Récentes</h3>
        <div className="space-y-3">
          {[
            { name: 'Marie OBIANG', action: 'Enrôlement validé', time: '10:45', status: 'success' },
            { name: 'Paul NZAMBA', action: 'En attente validation', time: '09:30', status: 'pending' },
            { name: 'Claire IDIATA', action: 'Enrôlement complété', time: '08:15', status: 'success' }
          ].map((activity, i) => (
            <div key={i} className="flex items-center gap-3 pb-3 border-b border-gray-100 last:border-0">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                activity.status === 'success' ? 'bg-green-100' : 'bg-yellow-100'
              }`}>
                {activity.status === 'success' ? 
                  <CheckCircle size={16} className="text-green-600" /> : 
                  <AlertCircle size={16} className="text-yellow-600" />
                }
              </div>
              <div className="flex-1">
                <p className="font-semibold text-sm text-gray-800">{activity.name}</p>
                <p className="text-xs text-gray-600">{activity.action}</p>
              </div>
              <span className="text-xs text-gray-500">{activity.time}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  // Screen: Enrollment Form
  const EnrollmentScreen = () => {
    const [formData, setFormData] = useState({
      firstName: '',
      lastName: '',
      nip: '',
      birthDate: '',
      gender: '',
      province: 'Estuaire',
      phone: '',
      hasElectricity: '',
      hasWater: '',
      householdSize: ''
    });

    const handleSubmit = () => {
      alert('Enrôlement enregistré localement!\n\nSera synchronisé avec le backend dès connexion disponible.');
      setPendingSync(prev => prev + 1);
      setTodayStats(prev => ({ ...prev, enrolled: prev.enrolled + 1, pending: prev.pending + 1 }));
      setCurrentScreen('dashboard');
    };

    return (
      <div className="p-4 pb-24 space-y-4">
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-800">Nouvel Enrôlement</h2>
            <button onClick={() => setCurrentScreen('dashboard')}>
              <X size={24} className="text-gray-600" />
            </button>
          </div>

          <div className="space-y-4">
            {/* Identité */}
            <div className="bg-blue-50 p-3 rounded-lg">
              <h3 className="font-semibold text-sm text-gray-700 mb-2 flex items-center gap-2">
                <User size={16} />
                Identité Personnelle
              </h3>
              <div className="space-y-2">
                <input
                  type="text"
                  placeholder="Prénom *"
                  value={formData.firstName}
                  onChange={(e) => setFormData({...formData, firstName: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
                <input
                  type="text"
                  placeholder="Nom *"
                  value={formData.lastName}
                  onChange={(e) => setFormData({...formData, lastName: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
                <input
                  type="text"
                  placeholder="NIP (Numéro d'Identification Personnel)"
                  value={formData.nip}
                  onChange={(e) => setFormData({...formData, nip: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
                <div className="grid grid-cols-2 gap-2">
                  <input
                    type="date"
                    value={formData.birthDate}
                    onChange={(e) => setFormData({...formData, birthDate: e.target.value})}
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                  <select
                    value={formData.gender}
                    onChange={(e) => setFormData({...formData, gender: e.target.value})}
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Sexe *</option>
                    <option value="M">Masculin</option>
                    <option value="F">Féminin</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Localisation */}
            <div className="bg-green-50 p-3 rounded-lg">
              <h3 className="font-semibold text-sm text-gray-700 mb-2 flex items-center gap-2">
                <MapPin size={16} />
                Localisation
              </h3>
              <div className="space-y-2">
                <select
                  value={formData.province}
                  onChange={(e) => setFormData({...formData, province: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                >
                  {GABON_PROVINCES.map(p => (
                    <option key={p} value={p}>{p}</option>
                  ))}
                </select>
                <input
                  type="tel"
                  placeholder="Téléphone (+241)"
                  value={formData.phone}
                  onChange={(e) => setFormData({...formData, phone: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                />
                <button className="w-full bg-green-600 text-white py-2 rounded-lg flex items-center justify-center gap-2 hover:bg-green-700">
                  <MapPin size={16} />
                  Capturer GPS
                </button>
              </div>
            </div>

            {/* Conditions de vie */}
            <div className="bg-yellow-50 p-3 rounded-lg">
              <h3 className="font-semibold text-sm text-gray-700 mb-2 flex items-center gap-2">
                <Home size={16} />
                Conditions de Vie
              </h3>
              <div className="space-y-2">
                <input
                  type="number"
                  placeholder="Taille du ménage"
                  value={formData.householdSize}
                  onChange={(e) => setFormData({...formData, householdSize: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500"
                />
                <div className="grid grid-cols-2 gap-2">
                  <select
                    value={formData.hasElectricity}
                    onChange={(e) => setFormData({...formData, hasElectricity: e.target.value})}
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500"
                  >
                    <option value="">Électricité</option>
                    <option value="yes">Oui</option>
                    <option value="no">Non</option>
                  </select>
                  <select
                    value={formData.hasWater}
                    onChange={(e) => setFormData({...formData, hasWater: e.target.value})}
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500"
                  >
                    <option value="">Eau courante</option>
                    <option value="yes">Oui</option>
                    <option value="no">Non</option>
                  </select>
                </div>
                <button className="w-full bg-yellow-600 text-white py-2 rounded-lg flex items-center justify-center gap-2 hover:bg-yellow-700">
                  <Camera size={16} />
                  Photo Logement
                </button>
              </div>
            </div>

            {/* Score vulnérabilité (calculé) */}
            <div className="bg-purple-50 p-3 rounded-lg border-2 border-purple-300">
              <h3 className="font-semibold text-sm text-gray-700 mb-2 flex items-center gap-2">
                <TrendingUp size={16} />
                Score Vulnérabilité Estimé
              </h3>
              <div className="flex items-center justify-between">
                <div className="text-3xl font-bold text-purple-600">52.5</div>
                <div className="text-right">
                  <span className="px-3 py-1 bg-orange-100 text-orange-800 text-xs font-semibold rounded-full">
                    MODÉRÉE
                  </span>
                  <p className="text-xs text-gray-600 mt-1">Calcul automatique IA</p>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="space-y-2">
              <button 
                onClick={handleSubmit}
                className="w-full bg-green-600 text-white py-3 rounded-lg flex items-center justify-center gap-2 hover:bg-green-700 font-semibold"
              >
                <Save size={20} />
                Enregistrer Localement
              </button>
              <button 
                onClick={() => setCurrentScreen('dashboard')}
                className="w-full bg-gray-200 text-gray-700 py-3 rounded-lg hover:bg-gray-300 font-semibold"
              >
                Annuler
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Screen: Search
  const SearchScreen = () => {
    const [searchTerm, setSearchTerm] = useState('');
    const [results] = useState([
      { id: 'RSU-GA-001', name: 'Marie OBIANG', province: 'Estuaire', score: 68.5, status: 'validated' },
      { id: 'RSU-GA-002', name: 'Jean MBOUMBA', province: 'Haut-Ogooué', score: 45.2, status: 'pending' },
      { id: 'RSU-GA-003', name: 'Sylvie KOUMBA', province: 'Ngounié', score: 72.1, status: 'validated' }
    ]);

    return (
      <div className="p-4 pb-20 space-y-4">
        <div className="bg-white rounded-lg shadow-md p-4">
          <h2 className="text-xl font-bold text-gray-800 mb-4">Rechercher Bénéficiaire</h2>
          
          <div className="relative mb-4">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="RSU-ID, NIP, nom..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="space-y-3">
            {results.map((person) => (
              <div key={person.id} className="border border-gray-200 rounded-lg p-3 hover:bg-gray-50">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <p className="font-bold text-gray-800">{person.name}</p>
                    <p className="text-sm text-blue-600 font-mono">{person.id}</p>
                  </div>
                  <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                    person.status === 'validated' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {person.status === 'validated' ? 'Validé' : 'En attente'}
                  </span>
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-gray-600 flex items-center gap-1">
                    <MapPin size={14} />
                    {person.province}
                  </span>
                  <span className="text-gray-600">Score: <span className="font-semibold">{person.score}</span></span>
                  <button className="text-blue-600 hover:text-blue-800 flex items-center gap-1">
                    Voir
                    <ChevronRight size={16} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  // Screen: Synchronisation
  const SyncScreen = () => (
    <div className="p-4 pb-20 space-y-4">
      <div className="bg-white rounded-lg shadow-md p-4">
        <h2 className="text-xl font-bold text-gray-800 mb-4">Synchronisation</h2>
        
        {/* Status connexion */}
        <div className={`p-4 rounded-lg mb-4 ${isOnline ? 'bg-green-50 border-2 border-green-300' : 'bg-red-50 border-2 border-red-300'}`}>
          <div className="flex items-center gap-3">
            {isOnline ? <Wifi size={24} className="text-green-600" /> : <WifiOff size={24} className="text-red-600" />}
            <div>
              <p className={`font-semibold ${isOnline ? 'text-green-800' : 'text-red-800'}`}>
                {isOnline ? 'Connexion Active' : 'Hors Ligne'}
              </p>
              <p className="text-sm text-gray-600">
                {isOnline ? 'Prêt pour synchronisation' : 'Données stockées localement'}
              </p>
            </div>
          </div>
        </div>

        {/* Statistiques sync */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="bg-yellow-50 p-4 rounded-lg border-l-4 border-yellow-600">
            <p className="text-sm text-gray-600">En attente</p>
            <p className="text-3xl font-bold text-yellow-600">{pendingSync}</p>
          </div>
          <div className="bg-green-50 p-4 rounded-lg border-l-4 border-green-600">
            <p className="text-sm text-gray-600">Synchronisés</p>
            <p className="text-3xl font-bold text-green-600">47</p>
          </div>
        </div>

        {/* Actions */}
        <div className="space-y-2">
          <button 
            disabled={!isOnline}
            className={`w-full py-3 rounded-lg flex items-center justify-center gap-2 font-semibold ${
              isOnline 
                ? 'bg-blue-600 text-white hover:bg-blue-700' 
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            <Upload size={20} />
            Synchroniser Maintenant
          </button>
          <button className="w-full bg-green-600 text-white py-3 rounded-lg flex items-center justify-center gap-2 hover:bg-green-700 font-semibold">
            <Download size={20} />
            Télécharger Données de Référence
          </button>
        </div>

        {/* Liste en attente */}
        <div className="mt-6">
          <h3 className="font-semibold text-gray-700 mb-3">Données en Attente de Sync</h3>
          <div className="space-y-2">
            {[
              { type: 'Enrôlement', name: 'Marie OBIANG', date: "Aujourd'hui 10:45" },
              { type: 'Enrôlement', name: 'Paul NZAMBA', date: "Aujourd'hui 09:30" },
              { type: 'Modification', name: 'Claire IDIATA', date: 'Hier 16:20' }
            ].map((item, i) => (
              <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <ClipboardList size={20} className="text-gray-600" />
                  <div>
                    <p className="font-semibold text-sm text-gray-800">{item.name}</p>
                    <p className="text-xs text-gray-600">{item.type}</p>
                  </div>
                </div>
                <span className="text-xs text-gray-500">{item.date}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-100">
      <AppHeader />
      
      {currentScreen === 'dashboard' && <DashboardScreen />}
      {currentScreen === 'enroll' && <EnrollmentScreen />}
      {currentScreen === 'search' && <SearchScreen />}
      {currentScreen === 'sync' && <SyncScreen />}
      
      <BottomNav />
    </div>
  );
}