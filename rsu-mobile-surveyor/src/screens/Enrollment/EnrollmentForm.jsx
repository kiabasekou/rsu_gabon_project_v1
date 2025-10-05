import React, { useState, useEffect } from 'react';
import { 
  User, Home, MapPin, Camera, CheckCircle, AlertTriangle, 
  Save, X, TrendingUp, Phone, Calendar, Globe, Zap, Droplet,
  DollarSign, GraduationCap, Users, Shield, ChevronDown, Info
} from 'lucide-react';

// Services importés (simulés ici)
const validationService = {
  validateNIP: (nip) => {
    if (!nip) return { valid: false, error: 'NIP requis' };
    const nipRegex = /^\d{10,14}$/;
    return nipRegex.test(nip) 
      ? { valid: true } 
      : { valid: false, error: 'NIP invalide (10-14 chiffres)' };
  },
  validatePhone: (phone) => {
    if (!phone) return { valid: true };
    const cleaned = phone.replace(/\s/g, '');
    const phoneRegex = /^(\+241|0)[1-7]\d{7}$/;
    return phoneRegex.test(cleaned)
      ? { valid: true, normalized: cleaned }
      : { valid: false, error: 'Format: +241 XX XX XX XX' };
  },
  validateBirthDate: (dateString) => {
    if (!dateString) return { valid: false, error: 'Date requise' };
    const date = new Date(dateString);
    const now = new Date();
    const age = (now - date) / (1000 * 60 * 60 * 24 * 365.25);
    if (isNaN(date.getTime())) return { valid: false, error: 'Date invalide' };
    if (age < 0) return { valid: false, error: 'Date dans le futur' };
    if (age > 120) return { valid: false, error: 'Âge trop élevé' };
    return { valid: true, age: Math.floor(age) };
  }
};

const scoringService = {
  calculateLocalVulnerabilityScore: (personData, householdData) => {
    let score = 0;
    const factors = [];

    if (!householdData.hasElectricity) {
      score += 15;
      factors.push({ dimension: 'Économique', factor: "Pas d'électricité", points: 15 });
    }
    if (!householdData.hasWater) {
      score += 10;
      factors.push({ dimension: 'Économique', factor: "Pas d'eau courante", points: 10 });
    }
    if (parseInt(householdData.monthlyIncome || 0) < 100000) {
      score += 10;
      factors.push({ dimension: 'Économique', factor: 'Revenu faible', points: 10 });
    }

    const birthValidation = validationService.validateBirthDate(personData.birthDate);
    if (birthValidation.valid) {
      const age = birthValidation.age;
      if (age < 5 || age > 65) {
        score += 10;
        factors.push({ dimension: 'Démographique', factor: age < 5 ? 'Enfant jeune' : 'Senior', points: 10 });
      }
    }

    if (parseInt(householdData.size || 0) > 7) {
      score += 10;
      factors.push({ dimension: 'Démographique', factor: 'Grande famille', points: 10 });
    }

    if (!personData.educationLevel || personData.educationLevel === 'NONE') {
      score += 12;
      factors.push({ dimension: 'Social', factor: 'Pas de scolarisation', points: 12 });
    }

    if (householdData.hasDisabledMember === 'yes') {
      score += 13;
      factors.push({ dimension: 'Social', factor: 'Membre handicapé', points: 13 });
    }

    if (['Rural_Remote', 'Forest'].includes(householdData.zoneType)) {
      score += 15;
      factors.push({ dimension: 'Géographique', factor: 'Zone isolée', points: 15 });
    }

    const normalizedScore = Math.min(score, 100);
    const category = normalizedScore >= 70 ? 'EXTRÊME' : 
                     normalizedScore >= 50 ? 'ÉLEVÉE' : 
                     normalizedScore >= 30 ? 'MODÉRÉE' : 'FAIBLE';

    return { score: normalizedScore, category, factors };
  }
};

// Provinces du Gabon
const GABON_PROVINCES = [
  'Estuaire', 'Haut-Ogooué', 'Moyen-Ogooué', 'Ngounié',
  'Nyanga', 'Ogooué-Ivindo', 'Ogooué-Lolo', 'Ogooué-Maritime', 'Woleu-Ntem'
];

const ZONE_TYPES = [
  { value: 'Urban_Center', label: 'Centre Urbain' },
  { value: 'Urban_Periphery', label: 'Périphérie Urbaine' },
  { value: 'Rural_Accessible', label: 'Rural Accessible' },
  { value: 'Rural_Remote', label: 'Rural Isolé' },
  { value: 'Coastal', label: 'Zone Côtière' },
  { value: 'Forest', label: 'Zone Forestière' },
  { value: 'Mining', label: 'Zone Minière' }
];

const EDUCATION_LEVELS = [
  { value: 'NONE', label: 'Aucune' },
  { value: 'PRIMARY', label: 'Primaire' },
  { value: 'SECONDARY', label: 'Secondaire' },
  { value: 'HIGHER', label: 'Supérieur' }
];

// Composant principal
export default function RSUEnrollmentScreen() {
  const [currentStep, setCurrentStep] = useState(1);
  const [errors, setErrors] = useState({});
  const [vulnerabilityScore, setVulnerabilityScore] = useState(null);
  const [showScoreDetails, setShowScoreDetails] = useState(false);

  // Données personnelles
  const [personData, setPersonData] = useState({
    firstName: '',
    lastName: '',
    nip: '',
    birthDate: '',
    gender: '',
    phone: '',
    educationLevel: '',
    province: 'Estuaire'
  });

  // Données ménage
  const [householdData, setHouseholdData] = useState({
    size: '',
    hasElectricity: '',
    hasWater: '',
    monthlyIncome: '',
    hasDisabledMember: '',
    zoneType: '',
    hasSavings: '',
    hasFoodSecurity: ''
  });

  // Localisation GPS
  const [gpsData, setGpsData] = useState(null);
  const [gpsLoading, setGpsLoading] = useState(false);

  // Calcul automatique du score
  useEffect(() => {
    if (currentStep === 3) {
      const result = scoringService.calculateLocalVulnerabilityScore(
        personData,
        householdData
      );
      setVulnerabilityScore(result);
    }
  }, [currentStep, personData, householdData]);

  // Validation temps réel
  const validateField = (field, value) => {
    const newErrors = { ...errors };

    switch (field) {
      case 'nip':
        const nipValidation = validationService.validateNIP(value);
        if (!nipValidation.valid) {
          newErrors.nip = nipValidation.error;
        } else {
          delete newErrors.nip;
        }
        break;

      case 'phone':
        const phoneValidation = validationService.validatePhone(value);
        if (!phoneValidation.valid) {
          newErrors.phone = phoneValidation.error;
        } else {
          delete newErrors.phone;
        }
        break;

      case 'birthDate':
        const birthValidation = validationService.validateBirthDate(value);
        if (!birthValidation.valid) {
          newErrors.birthDate = birthValidation.error;
        } else {
          delete newErrors.birthDate;
        }
        break;

      default:
        break;
    }

    setErrors(newErrors);
  };

  // Capturer GPS
  const captureGPS = async () => {
    setGpsLoading(true);
    // Simulation capture GPS
    setTimeout(() => {
      setGpsData({
        latitude: 0.4162,
        longitude: 9.4673,
        accuracy: 12,
        timestamp: new Date().toISOString()
      });
      setGpsLoading(false);
    }, 1500);
  };

  // Validation étape
  const validateStep = (step) => {
    const newErrors = {};

    if (step === 1) {
      if (!personData.firstName?.trim()) newErrors.firstName = 'Prénom requis';
      if (!personData.lastName?.trim()) newErrors.lastName = 'Nom requis';
      if (!personData.gender) newErrors.gender = 'Sexe requis';
      
      const birthValidation = validationService.validateBirthDate(personData.birthDate);
      if (!birthValidation.valid) newErrors.birthDate = birthValidation.error;
    }

    if (step === 2) {
      if (!householdData.size) newErrors.size = 'Taille ménage requise';
      if (!householdData.zoneType) newErrors.zoneType = 'Type zone requis';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Navigation étapes
  const goToNextStep = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(prev => Math.min(prev + 1, 4));
    }
  };

  const goToPrevStep = () => {
    setCurrentStep(prev => Math.max(prev - 1, 1));
  };

  // Sauvegarde
  const handleSave = () => {
    const enrollmentData = {
      person: personData,
      household: householdData,
      gps: gpsData,
      vulnerabilityScore: vulnerabilityScore?.score,
      timestamp: new Date().toISOString()
    };

    console.log('Enrôlement sauvegardé:', enrollmentData);
    alert('✅ Enrôlement enregistré localement!\n\nSera synchronisé avec le backend dès connexion disponible.');
  };

  // Indicateur progression
  const ProgressBar = () => (
    <div className="mb-6">
      <div className="flex justify-between mb-2">
        {[1, 2, 3, 4].map(step => (
          <div key={step} className="flex flex-col items-center flex-1">
            <div className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold ${
              step === currentStep ? 'bg-green-600 text-white' :
              step < currentStep ? 'bg-green-200 text-green-800' :
              'bg-gray-200 text-gray-500'
            }`}>
              {step < currentStep ? <CheckCircle size={20} /> : step}
            </div>
            <span className="text-xs mt-1 text-gray-600 text-center">
              {step === 1 ? 'Identité' : step === 2 ? 'Ménage' : step === 3 ? 'Score' : 'Confirmer'}
            </span>
          </div>
        ))}
      </div>
      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div 
          className="h-full bg-green-600 transition-all duration-300"
          style={{ width: `${(currentStep / 4) * 100}%` }}
        />
      </div>
    </div>
  );

  // Composant champ avec erreur
  const InputField = ({ label, error, icon: Icon, ...props }) => (
    <div className="mb-4">
      <label className="block text-sm font-semibold text-gray-700 mb-1">
        {label} {props.required && <span className="text-red-500">*</span>}
      </label>
      <div className="relative">
        {Icon && (
          <Icon className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
        )}
        <input
          {...props}
          className={`w-full ${Icon ? 'pl-10' : 'pl-3'} pr-3 py-2.5 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent ${
            error ? 'border-red-500 bg-red-50' : 'border-gray-300'
          }`}
        />
      </div>
      {error && (
        <p className="mt-1 text-sm text-red-600 flex items-center gap-1">
          <AlertTriangle size={14} />
          {error}
        </p>
      )}
    </div>
  );

  const SelectField = ({ label, error, icon: Icon, options, ...props }) => (
    <div className="mb-4">
      <label className="block text-sm font-semibold text-gray-700 mb-1">
        {label} {props.required && <span className="text-red-500">*</span>}
      </label>
      <div className="relative">
        {Icon && (
          <Icon className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
        )}
        <select
          {...props}
          className={`w-full ${Icon ? 'pl-10' : 'pl-3'} pr-10 py-2.5 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent appearance-none ${
            error ? 'border-red-500 bg-red-50' : 'border-gray-300'
          }`}
        >
          {options.map(opt => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
        <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 pointer-events-none" size={18} />
      </div>
      {error && (
        <p className="mt-1 text-sm text-red-600 flex items-center gap-1">
          <AlertTriangle size={14} />
          {error}
        </p>
      )}
    </div>
  );

  // ÉTAPE 1: Identité personnelle
  const Step1Personal = () => (
    <div className="bg-white rounded-lg shadow-md p-5">
      <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
        <User className="text-blue-600" size={24} />
        Identité Personnelle
      </h3>

      <div className="grid grid-cols-2 gap-3">
        <div className="col-span-2">
          <InputField
            label="Prénom"
            icon={User}
            required
            value={personData.firstName}
            onChange={(e) => setPersonData({...personData, firstName: e.target.value})}
            error={errors.firstName}
            placeholder="Ex: Marie"
          />
        </div>

        <div className="col-span-2">
          <InputField
            label="Nom"
            icon={User}
            required
            value={personData.lastName}
            onChange={(e) => setPersonData({...personData, lastName: e.target.value})}
            error={errors.lastName}
            placeholder="Ex: OBIANG"
          />
        </div>

        <div className="col-span-2">
          <InputField
            label="NIP (Numéro Identification Gabonais)"
            icon={Shield}
            type="text"
            value={personData.nip}
            onChange={(e) => {
              setPersonData({...personData, nip: e.target.value});
              validateField('nip', e.target.value);
            }}
            error={errors.nip}
            placeholder="10-14 chiffres"
          />
        </div>

        <InputField
          label="Date de Naissance"
          icon={Calendar}
          type="date"
          required
          value={personData.birthDate}
          onChange={(e) => {
            setPersonData({...personData, birthDate: e.target.value});
            validateField('birthDate', e.target.value);
          }}
          error={errors.birthDate}
        />

        <SelectField
          label="Sexe"
          icon={User}
          required
          value={personData.gender}
          onChange={(e) => setPersonData({...personData, gender: e.target.value})}
          error={errors.gender}
          options={[
            { value: '', label: 'Sélectionner...' },
            { value: 'M', label: 'Masculin' },
            { value: 'F', label: 'Féminin' }
          ]}
        />

        <div className="col-span-2">
          <InputField
            label="Téléphone"
            icon={Phone}
            type="tel"
            value={personData.phone}
            onChange={(e) => {
              setPersonData({...personData, phone: e.target.value});
              validateField('phone', e.target.value);
            }}
            error={errors.phone}
            placeholder="+241 XX XX XX XX"
          />
        </div>

        <div className="col-span-2">
          <SelectField
            label="Niveau d'Éducation"
            icon={GraduationCap}
            value={personData.educationLevel}
            onChange={(e) => setPersonData({...personData, educationLevel: e.target.value})}
            options={[{ value: '', label: 'Sélectionner...' }, ...EDUCATION_LEVELS]}
          />
        </div>

        <div className="col-span-2">
          <SelectField
            label="Province"
            icon={MapPin}
            required
            value={personData.province}
            onChange={(e) => setPersonData({...personData, province: e.target.value})}
            options={GABON_PROVINCES.map(p => ({ value: p, label: p }))}
          />
        </div>
      </div>
    </div>
  );

  // ÉTAPE 2: Données ménage
  const Step2Household = () => (
    <div className="bg-white rounded-lg shadow-md p-5">
      <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
        <Home className="text-purple-600" size={24} />
        Conditions de Vie du Ménage
      </h3>

      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <InputField
            label="Taille du Ménage"
            icon={Users}
            type="number"
            required
            value={householdData.size}
            onChange={(e) => setHouseholdData({...householdData, size: e.target.value})}
            error={errors.size}
            placeholder="Nombre de personnes"
          />

          <InputField
            label="Revenu Mensuel (FCFA)"
            icon={DollarSign}
            type="number"
            value={householdData.monthlyIncome}
            onChange={(e) => setHouseholdData({...householdData, monthlyIncome: e.target.value})}
            placeholder="Ex: 150000"
          />
        </div>

        <SelectField
          label="Type de Zone"
          icon={Globe}
          required
          value={householdData.zoneType}
          onChange={(e) => setHouseholdData({...householdData, zoneType: e.target.value})}
          error={errors.zoneType}
          options={[{ value: '', label: 'Sélectionner...' }, ...ZONE_TYPES]}
        />

        <div className="bg-blue-50 p-4 rounded-lg border-l-4 border-blue-600">
          <p className="text-sm font-semibold text-gray-700 mb-3">Services & Équipements</p>
          
          <div className="grid grid-cols-2 gap-3">
            <SelectField
              label="Électricité"
              icon={Zap}
              value={householdData.hasElectricity}
              onChange={(e) => setHouseholdData({...householdData, hasElectricity: e.target.value})}
              options={[
                { value: '', label: 'Sélectionner...' },
                { value: 'yes', label: 'Oui' },
                { value: 'no', label: 'Non' }
              ]}
            />

            <SelectField
              label="Eau Courante"
              icon={Droplet}
              value={householdData.hasWater}
              onChange={(e) => setHouseholdData({...householdData, hasWater: e.target.value})}
              options={[
                { value: '', label: 'Sélectionner...' },
                { value: 'yes', label: 'Oui' },
                { value: 'no', label: 'Non' }
              ]}
            />
          </div>
        </div>

        <div className="bg-yellow-50 p-4 rounded-lg border-l-4 border-yellow-600">
          <p className="text-sm font-semibold text-gray-700 mb-3">Vulnérabilités Spécifiques</p>
          
          <SelectField
            label="Membre Handicapé dans le Ménage"
            icon={Shield}
            value={householdData.hasDisabledMember}
            onChange={(e) => setHouseholdData({...householdData, hasDisabledMember: e.target.value})}
            options={[
              { value: '', label: 'Sélectionner...' },
              { value: 'yes', label: 'Oui' },
              { value: 'no', label: 'Non' }
            ]}
          />

          <div className="grid grid-cols-2 gap-3">
            <SelectField
              label="Épargne"
              value={householdData.hasSavings}
              onChange={(e) => setHouseholdData({...householdData, hasSavings: e.target.value})}
              options={[
                { value: '', label: 'Sélectionner...' },
                { value: 'yes', label: 'Oui' },
                { value: 'no', label: 'Non' }
              ]}
            />

            <SelectField
              label="Sécurité Alimentaire"
              value={householdData.hasFoodSecurity}
              onChange={(e) => setHouseholdData({...householdData, hasFoodSecurity: e.target.value})}
              options={[
                { value: '', label: 'Sélectionner...' },
                { value: 'yes', label: 'Oui' },
                { value: 'no', label: 'Non' }
              ]}
            />
          </div>
        </div>

        <div className="bg-green-50 p-4 rounded-lg border-l-4 border-green-600">
          <p className="text-sm font-semibold text-gray-700 mb-2">Géolocalisation</p>
          {!gpsData ? (
            <button
              onClick={captureGPS}
              disabled={gpsLoading}
              className="w-full bg-green-600 text-white py-2.5 rounded-lg flex items-center justify-center gap-2 hover:bg-green-700 disabled:bg-gray-400"
            >
              <MapPin size={18} />
              {gpsLoading ? 'Capture en cours...' : 'Capturer Position GPS'}
            </button>
          ) : (
            <div className="text-sm">
              <p className="text-green-800 font-semibold flex items-center gap-1 mb-1">
                <CheckCircle size={16} />
                Position GPS capturée
              </p>
              <p className="text-gray-600">Lat: {gpsData.latitude.toFixed(4)}, Lng: {gpsData.longitude.toFixed(4)}</p>
              <p className="text-gray-500 text-xs">Précision: {gpsData.accuracy}m</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  // ÉTAPE 3: Score vulnérabilité
  const Step3Score = () => (
    <div className="bg-white rounded-lg shadow-md p-5">
      <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
        <TrendingUp className="text-orange-600" size={24} />
        Score de Vulnérabilité
      </h3>

      {vulnerabilityScore ? (
        <div>
          <div className={`p-6 rounded-xl border-4 mb-4 ${
            vulnerabilityScore.category === 'EXTRÊME' ? 'bg-red-50 border-red-500' :
            vulnerabilityScore.category === 'ÉLEVÉE' ? 'bg-orange-50 border-orange-500' :
            vulnerabilityScore.category === 'MODÉRÉE' ? 'bg-yellow-50 border-yellow-500' :
            'bg-green-50 border-green-500'
          }`}>
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-2">Score Calculé par IA</p>
              <div className={`text-6xl font-bold mb-2 ${
                vulnerabilityScore.category === 'EXTRÊME' ? 'text-red-600' :
                vulnerabilityScore.category === 'ÉLEVÉE' ? 'text-orange-600' :
                vulnerabilityScore.category === 'MODÉRÉE' ? 'text-yellow-600' :
                'text-green-600'
              }`}>
                {vulnerabilityScore.score.toFixed(1)}
              </div>
              <span className={`px-4 py-2 rounded-full font-semibold text-sm ${
                vulnerabilityScore.category === 'EXTRÊME' ? 'bg-red-200 text-red-800' :
                vulnerabilityScore.category === 'ÉLEVÉE' ? 'bg-orange-200 text-orange-800' :
                vulnerabilityScore.category === 'MODÉRÉE' ? 'bg-yellow-200 text-yellow-800' :
                'bg-green-200 text-green-800'
              }`}>
                Vulnérabilité {vulnerabilityScore.category}
              </span>
            </div>
          </div>

          <button
            onClick={() => setShowScoreDetails(!showScoreDetails)}
            className="w-full bg-gray-100 text-gray-700 py-2 rounded-lg flex items-center justify-center gap-2 hover:bg-gray-200 mb-4"
          >
            <Info size={18} />
            {showScoreDetails ? 'Masquer' : 'Voir'} Détails du Calcul
          </button>

          {showScoreDetails && vulnerabilityScore.factors.length > 0 && (
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="font-semibold text-gray-700 mb-3">Facteurs Identifiés:</p>
              <div className="space-y-2">
                {vulnerabilityScore.factors.map((factor, i) => (
                  <div key={i} className="flex justify-between items-center p-2 bg-white rounded border-l-4 border-blue-500">
                    <div>
                      <p className="text-sm font-semibold text-gray-800">{factor.factor}</p>
                      <p className="text-xs text-gray-500">{factor.dimension}</p>
                    </div>
                    <span className="text-blue-600 font-bold">+{factor.points}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="mt-4 bg-blue-50 p-3 rounded-lg">
            <p className="text-xs text-gray-600">
              <strong>Note:</strong> Ce score sera validé par le backend Django lors de la synchronisation. 
              Le moteur IA GabonVulnerabilityScoringEngine effectuera un calcul complet avec toutes les dimensions.
            </p>
          </div>
        </div>
      ) : (
        <div className="text-center text-gray-500 py-8">
          Calcul en cours...
        </div>
      )}
    </div>
  );

  // ÉTAPE 4: Confirmation
  const Step4Confirm = () => (
    <div className="space-y-4">
      <div className="bg-white rounded-lg shadow-md p-5">
        <h3 className="text-lg font-bold text-gray-800 mb-4">Récapitulatif</h3>
        
        <div className="space-y-3">
          <div className="pb-3 border-b border-gray-200">
            <p className="text-xs text-gray-500 mb-1">IDENTITÉ</p>
            <p className="font-bold text-gray-800">{personData.firstName} {personData.lastName}</p>
            <p className="text-sm text-gray-600">
              {personData.gender === 'M' ? 'Masculin' : 'Féminin'} • 
              {personData.birthDate ? ` Né(e) le ${new Date(personData.birthDate).toLocaleDateString('fr-FR')}` : ''}
            </p>
            {personData.nip && <p className="text-sm text-blue-600 font-mono">NIP: {personData.nip}</p>}
          </div>

          <div className="pb-3 border-b border-gray-200">
            <p className="text-xs text-gray-500 mb-1">LOCALISATION</p>
            <p className="text-sm text-gray-600 flex items-center gap-1">
              <MapPin size={14} />
              {personData.province}
            </p>
            {personData.phone && (
              <p className="text-sm text-gray-600 flex items-center gap-1">
                <Phone size={14} />
                {personData.phone}
              </p>
            )}
          </div>

          <div className="pb-3 border-b border-gray-200">
            <p className="text-xs text-gray-500 mb-1">MÉNAGE</p>
            <p className="text-sm text-gray-600">
              {householdData.size} personnes • 
              {householdData.hasElectricity === 'yes' ? ' Électricité ✓' : ' Pas d\'électricité'} •
              {householdData.hasWater === 'yes' ? ' Eau ✓' : ' Pas d\'eau'}
            </p>
          </div>

          {vulnerabilityScore && (
            <div className={`p-3 rounded-lg ${
              vulnerabilityScore.category === 'EXTRÊME' ? 'bg-red-50' :
              vulnerabilityScore.category === 'ÉLEVÉE' ? 'bg-orange-50' :
              vulnerabilityScore.category === 'MODÉRÉE' ? 'bg-yellow-50' :
              'bg-green-50'
            }`}>
              <p className="text-xs text-gray-500 mb-1">SCORE VULNÉRABILITÉ</p>
              <p className="text-2xl font-bold">
                {vulnerabilityScore.score.toFixed(1)} 
                <span className="text-sm font-normal ml-2">({vulnerabilityScore.category})</span>
              </p>
            </div>
          )}
        </div>
      </div>

      <div className="bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded">
        <p className="text-sm text-yellow-800">
          <strong>Mode Offline:</strong> Ces données seront enregistrées localement et synchronisées 
          automatiquement avec le serveur RSU dès connexion disponible.
        </p>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-100 p-4 pb-24">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-600 to-yellow-500 text-white p-4 rounded-lg shadow-lg mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold">Nouvel Enrôlement</h1>
            <p className="text-sm opacity-90">Enregistrement bénéficiaire RSU</p>
          </div>
          <button className="text-white hover:bg-white hover:bg-opacity-20 p-2 rounded-lg">
            <X size={24} />
          </button>
        </div>
      </div>

      {/* Progression */}
      <ProgressBar />

      {/* Contenu étapes */}
      <div className="space-y-4">
        {currentStep === 1 && <Step1Personal />}
        {currentStep === 2 && <Step2Household />}
        {currentStep === 3 && <Step3Score />}
        {currentStep === 4 && <Step4Confirm />}
      </div>

      {/* Navigation */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 p-4 shadow-lg">
        <div className="flex gap-3 max-w-2xl mx-auto">
          {currentStep > 1 && (
            <button
              onClick={goToPrevStep}
              className="flex-1 bg-gray-200 text-gray-700 py-3 rounded-lg font-semibold hover:bg-gray-300"
            >
              Précédent
            </button>
          )}
          {currentStep < 4 ? (
            <button
              onClick={goToNextStep}
              className="flex-1 bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 flex items-center justify-center gap-2"
            >
              Suivant
              <ChevronDown className="rotate-[-90deg]" size={20} />
            </button>
          ) : (
            <button
              onClick={handleSave}
              className="flex-1 bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 flex items-center justify-center gap-2"
            >
              <Save size={20} />
              Enregistrer
            </button>
          )}
        </div>
      </div>
    </div>
  );
}