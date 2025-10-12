/**
 * 🇬🇦 RSU Gabon - Program Form Modal
 * Standards Top 1% - Formulaire Création/Édition Programme
 * Fichier: rsu_admin_dashboard/src/components/Dashboard/ProgramFormModal.jsx
 */

import React, { useState, useEffect } from 'react';
import { X, Save, AlertCircle } from 'lucide-react';
import { programsAPI } from '../../services/api/programsAPI';

export default function ProgramFormModal({ isOpen, onClose, programId = null, onSuccess }) {
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [categories, setCategories] = useState([]);
  
  const [formData, setFormData] = useState({
    code: '',
    name: '',
    category: '',
    description: '',
    objectives: '',
    status: 'DRAFT',
    start_date: '',
    end_date: '',
    total_budget: '',
    benefit_amount: '',
    frequency: 'MONTHLY',
    max_beneficiaries: ''
  });

  useEffect(() => {
    if (isOpen) {
      loadCategories();
      if (programId) {
        loadProgramData();
      } else {
        resetForm();
      }
    }
  }, [isOpen, programId]);

  const loadCategories = async () => {
    try {
      const data = await programsAPI.getCategories();
      setCategories(data.results || data || []);
    } catch (error) {
      console.error('Erreur chargement catégories:', error);
    }
  };

  const loadProgramData = async () => {
    try {
      setLoading(true);
      const data = await programsAPI.getProgramById(programId);
      setFormData({
        code: data.code || '',
        name: data.name || '',
        category: data.category || '',
        description: data.description || '',
        objectives: data.objectives || '',
        status: data.status || 'DRAFT',
        start_date: data.start_date || '',
        end_date: data.end_date || '',
        total_budget: data.total_budget || '',
        benefit_amount: data.benefit_amount || '',
        frequency: data.frequency || 'MONTHLY',
        max_beneficiaries: data.max_beneficiaries || ''
      });
    } catch (error) {
      console.error('Erreur chargement programme:', error);
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      code: '',
      name: '',
      category: '',
      description: '',
      objectives: '',
      status: 'DRAFT',
      start_date: '',
      end_date: '',
      total_budget: '',
      benefit_amount: '',
      frequency: 'MONTHLY',
      max_beneficiaries: ''
    });
    setErrors({});
  };

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Effacer erreur du champ modifié
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: null }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    // Champs obligatoires
    if (!formData.code) newErrors.code = 'Code requis';
    if (!formData.name) newErrors.name = 'Nom requis';
    if (!formData.category) newErrors.category = 'Catégorie requise';
    if (!formData.start_date) newErrors.start_date = 'Date de début requise';
    if (!formData.total_budget) newErrors.total_budget = 'Budget total requis';
    if (!formData.benefit_amount) newErrors.benefit_amount = 'Montant bénéfice requis';
    if (!formData.max_beneficiaries) newErrors.max_beneficiaries = 'Capacité maximale requise';

    // Validation format code (lettres majuscules + tirets)
    if (formData.code && !/^[A-Z0-9-]+$/.test(formData.code)) {
      newErrors.code = 'Code invalide (ex: TMC-2025)';
    }

    // Validation dates
    if (formData.end_date && formData.start_date) {
      if (new Date(formData.end_date) < new Date(formData.start_date)) {
        newErrors.end_date = 'Date de fin doit être après date de début';
      }
    }

    // Validation nombres positifs
    if (formData.total_budget && parseFloat(formData.total_budget) <= 0) {
      newErrors.total_budget = 'Budget doit être positif';
    }
    if (formData.benefit_amount && parseFloat(formData.benefit_amount) <= 0) {
      newErrors.benefit_amount = 'Montant doit être positif';
    }
    if (formData.max_beneficiaries && parseInt(formData.max_beneficiaries) <= 0) {
      newErrors.max_beneficiaries = 'Capacité doit être positive';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      console.log('❌ Validation échouée:', errors);
      return;
    }

    try {
      setLoading(true);

      if (programId) {
        // Mise à jour
        await programsAPI.updateProgram(programId, formData);
        console.log('✅ Programme mis à jour');
      } else {
        // Création
        await programsAPI.createProgram(formData);
        console.log('✅ Programme créé');
      }

      onSuccess && onSuccess();
      onClose();
    } catch (error) {
      console.error('❌ Erreur sauvegarde:', error);
      
      // Gérer erreurs backend
      if (error.response?.data) {
        const backendErrors = {};
        Object.keys(error.response.data).forEach(key => {
          backendErrors[key] = error.response.data[key][0] || error.response.data[key];
        });
        setErrors(backendErrors);
      } else {
        setErrors({ general: 'Erreur lors de la sauvegarde' });
      }
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex justify-between items-center px-6 py-4 border-b">
          <h2 className="text-xl font-bold text-gray-800">
            {programId ? 'Modifier le Programme' : 'Nouveau Programme'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="overflow-y-auto max-h-[calc(90vh-140px)]">
          <div className="px-6 py-4 space-y-6">
            {/* Erreur générale */}
            {errors.general && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
                <AlertCircle className="text-red-600 mt-0.5 flex-shrink-0" size={20} />
                <p className="text-sm text-red-700">{errors.general}</p>
              </div>
            )}

            {/* Section 1: Informations de base */}
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Informations de base</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Code Programme <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={formData.code}
                    onChange={(e) => handleChange('code', e.target.value.toUpperCase())}
                    placeholder="TMC-2025"
                    className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.code ? 'border-red-500' : 'border-gray-300'
                    }`}
                    disabled={programId !== null} // Code non modifiable
                  />
                  {errors.code && <p className="text-red-500 text-xs mt-1">{errors.code}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Nom Programme <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => handleChange('name', e.target.value)}
                    placeholder="Transfert Monétaire Conditionnel"
                    className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.name ? 'border-red-500' : 'border-gray-300'
                    }`}
                  />
                  {errors.name && <p className="text-red-500 text-xs mt-1">{errors.name}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Catégorie <span className="text-red-500">*</span>
                  </label>
                  <select
                    value={formData.category}
                    onChange={(e) => handleChange('category', e.target.value)}
                    className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.category ? 'border-red-500' : 'border-gray-300'
                    }`}
                  >
                    <option value="">Sélectionner...</option>
                    {categories.map(cat => (
                      <option key={cat.id} value={cat.id}>{cat.name}</option>
                    ))}
                  </select>
                  {errors.category && <p className="text-red-500 text-xs mt-1">{errors.category}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Statut
                  </label>
                  <select
                    value={formData.status}
                    onChange={(e) => handleChange('status', e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="DRAFT">Brouillon</option>
                    <option value="ACTIVE">Actif</option>
                    <option value="PAUSED">Suspendu</option>
                    <option value="CLOSED">Clôturé</option>
                  </select>
                </div>
              </div>

              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => handleChange('description', e.target.value)}
                  placeholder="Description détaillée du programme..."
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Objectifs
                </label>
                <textarea
                  value={formData.objectives}
                  onChange={(e) => handleChange('objectives', e.target.value)}
                  placeholder="Objectifs principaux du programme..."
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Section 2: Dates */}
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Dates</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Date de début <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="date"
                    value={formData.start_date}
                    onChange={(e) => handleChange('start_date', e.target.value)}
                    className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.start_date ? 'border-red-500' : 'border-gray-300'
                    }`}
                  />
                  {errors.start_date && <p className="text-red-500 text-xs mt-1">{errors.start_date}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Date de fin
                  </label>
                  <input
                    type="date"
                    value={formData.end_date}
                    onChange={(e) => handleChange('end_date', e.target.value)}
                    className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.end_date ? 'border-red-500' : 'border-gray-300'
                    }`}
                  />
                  {errors.end_date && <p className="text-red-500 text-xs mt-1">{errors.end_date}</p>}
                </div>
              </div>
            </div>

            {/* Section 3: Budget */}
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Budget</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Budget Total (FCFA) <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    value={formData.total_budget}
                    onChange={(e) => handleChange('total_budget', e.target.value)}
                    placeholder="1000000000"
                    className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.total_budget ? 'border-red-500' : 'border-gray-300'
                    }`}
                  />
                  {errors.total_budget && <p className="text-red-500 text-xs mt-1">{errors.total_budget}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Montant Bénéfice (FCFA) <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    value={formData.benefit_amount}
                    onChange={(e) => handleChange('benefit_amount', e.target.value)}
                    placeholder="50000"
                    className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.benefit_amount ? 'border-red-500' : 'border-gray-300'
                    }`}
                  />
                  {errors.benefit_amount && <p className="text-red-500 text-xs mt-1">{errors.benefit_amount}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Fréquence
                  </label>
                  <select
                    value={formData.frequency}
                    onChange={(e) => handleChange('frequency', e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="ONE_TIME">Ponctuel</option>
                    <option value="MONTHLY">Mensuel</option>
                    <option value="QUARTERLY">Trimestriel</option>
                    <option value="ANNUAL">Annuel</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Section 4: Capacité */}
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Capacité</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Nombre Max Bénéficiaires <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    value={formData.max_beneficiaries}
                    onChange={(e) => handleChange('max_beneficiaries', e.target.value)}
                    placeholder="5000"
                    className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.max_beneficiaries ? 'border-red-500' : 'border-gray-300'
                    }`}
                  />
                  {errors.max_beneficiaries && <p className="text-red-500 text-xs mt-1">{errors.max_beneficiaries}</p>}
                </div>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="flex justify-end gap-3 px-6 py-4 border-t bg-gray-50">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors"
              disabled={loading}
            >
              Annuler
            </button>
            <button
              type="submit"
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={loading}
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Sauvegarde...
                </>
              ) : (
                <>
                  <Save size={18} />
                  {programId ? 'Mettre à jour' : 'Créer'}
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}