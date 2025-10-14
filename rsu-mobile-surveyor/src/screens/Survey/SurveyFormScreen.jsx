// =============================================================================
// 2. SURVEY FORM SCREEN (screens/Survey/SurveyFormScreen.jsx)
// =============================================================================
import React, { useState, useEffect } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  Alert,
} from 'react-native';
import {
  Card,
  Title,
  Paragraph,
  Button,
  TextInput,
  RadioButton,
  Checkbox,
  Chip,
  FAB,
  List,
  Avatar,
  ProgressBar,
  Surface,
} from 'react-native-paper';
import { Formik } from 'formik';
import * as Yup from 'yup';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';

import apiClient from '../../services/api/apiClient';
import gpsService from '../../services/gps/gpsService';
import syncService from '../../services/sync/syncService';

const SURVEY_TEMPLATES = {
  HOUSEHOLD_VERIFICATION: {
    id: 'household_verification',
    title: '🏠 Vérification Ménage',
    description: 'Vérification données ménage sur terrain',
    sections: [
      {
        id: 'composition',
        title: 'Composition Ménage',
        fields: [
          {
            id: 'members_count',
            type: 'number',
            label: 'Nombre réel de membres du ménage',
            required: true,
            validation: { min: 1, max: 20 },
          },
          {
            id: 'head_present',
            type: 'radio',
            label: 'Chef de ménage présent ?',
            required: true,
            options: [
              { value: 'yes', label: 'Oui, présent' },
              { value: 'no', label: 'Non, absent' },
              { value: 'changed', label: 'Changement de chef' },
            ],
          },
          {
            id: 'members_changes',
            type: 'textarea',
            label: 'Changements depuis dernière visite',
            required: false,
          },
        ],
      },
      {
        id: 'living_conditions',
        title: 'Conditions de Vie',
        fields: [
          {
            id: 'housing_state',
            type: 'radio',
            label: 'État du logement',
            required: true,
            options: [
              { value: 'good', label: 'Bon état' },
              { value: 'fair', label: 'État moyen' },
              { value: 'poor', label: 'Mauvais état' },
              { value: 'critical', label: 'État critique' },
            ],
          },
          {
            id: 'utilities',
            type: 'checkbox',
            label: 'Services disponibles',
            required: false,
            options: [
              { value: 'electricity', label: 'Électricité' },
              { value: 'water', label: 'Eau courante' },
              { value: 'internet', label: 'Internet' },
              { value: 'phone', label: 'Téléphone fixe' },
            ],
          },
        ],
      },
    ],
  },
  VULNERABILITY_UPDATE: {
    id: 'vulnerability_update',
    title: '⚠️ Mise à jour Vulnérabilité',
    description: 'Évaluation terrain facteurs vulnérabilité',
    sections: [
      {
        id: 'economic_status',
        title: 'Situation Économique',
        fields: [
          {
            id: 'employment_change',
            type: 'radio',
            label: 'Changement situation emploi ?',
            required: true,
            options: [
              { value: 'improved', label: 'Amélioration' },
              { value: 'same', label: 'Inchangée' },
              { value: 'worsened', label: 'Dégradation' },
            ],
          },
          {
            id: 'income_sources',
            type: 'checkbox',
            label: 'Sources de revenus actuelles',
            required: true,
            options: [
              { value: 'salary', label: 'Salaire fixe' },
              { value: 'informal', label: 'Activités informelles' },
              { value: 'agriculture', label: 'Agriculture' },
              { value: 'assistance', label: 'Aide sociale' },
              { value: 'remittances', label: 'Transferts famille' },
              { value: 'none', label: 'Aucun revenu' },
            ],
          },
        ],
      },
      {
        id: 'social_situation',
        title: 'Situation Sociale',
        fields: [
          {
            id: 'health_issues',
            type: 'radio',
            label: 'Problèmes de santé dans le ménage ?',
            required: true,
            options: [
              { value: 'none', label: 'Aucun' },
              { value: 'minor', label: 'Problèmes mineurs' },
              { value: 'serious', label: 'Problèmes graves' },
              { value: 'chronic', label: 'Maladies chroniques' },
            ],
          },
          {
            id: 'education_access',
            type: 'radio',
            label: 'Enfants scolarisés ?',
            required: false,
            options: [
              { value: 'all', label: 'Tous scolarisés' },
              { value: 'partial', label: 'Partiellement' },
              { value: 'none', label: 'Aucun scolarisé' },
              { value: 'no_children', label: 'Pas d\'enfants' },
            ],
          },
        ],
      },
    ],
  },
  PROGRAM_IMPACT: {
    id: 'program_impact',
    title: '📊 Impact Programmes',
    description: 'Évaluation impact programmes sociaux reçus',
    sections: [
      {
        id: 'program_reception',
        title: 'Réception Programmes',
        fields: [
          {
            id: 'received_programs',
            type: 'checkbox',
            label: 'Programmes sociaux reçus',
            required: true,
            options: [
              { value: 'cash_transfer', label: 'Transferts monétaires' },
              { value: 'food_assistance', label: 'Aide alimentaire' },
              { value: 'health_coverage', label: 'Couverture santé' },
              { value: 'education_support', label: 'Aide éducation' },
              { value: 'housing_assistance', label: 'Aide logement' },
              { value: 'none', label: 'Aucun programme reçu' },
            ],
          },
          {
            id: 'program_satisfaction',
            type: 'radio',
            label: 'Satisfaction globale programmes',
            required: false,
            options: [
              { value: 'very_satisfied', label: 'Très satisfait' },
              { value: 'satisfied', label: 'Satisfait' },
              { value: 'neutral', label: 'Neutre' },
              { value: 'dissatisfied', label: 'Insatisfait' },
              { value: 'very_dissatisfied', label: 'Très insatisfait' },
            ],
          },
        ],
      },
      {
        id: 'impact_assessment',
        title: 'Évaluation Impact',
        fields: [
          {
            id: 'life_improvement',
            type: 'radio',
            label: 'Les programmes ont-ils amélioré votre situation ?',
            required: true,
            options: [
              { value: 'significantly', label: 'Amélioration significative' },
              { value: 'moderately', label: 'Amélioration modérée' },
              { value: 'slightly', label: 'Légère amélioration' },
              { value: 'no_change', label: 'Aucun changement' },
              { value: 'worsened', label: 'Situation dégradée' },
            ],
          },
          {
            id: 'priority_needs',
            type: 'checkbox',
            label: 'Besoins prioritaires actuels',
            required: true,
            options: [
              { value: 'food', label: 'Alimentation' },
              { value: 'healthcare', label: 'Soins de santé' },
              { value: 'housing', label: 'Logement' },
              { value: 'education', label: 'Éducation enfants' },
              { value: 'employment', label: 'Emploi/Formation' },
              { value: 'utilities', label: 'Électricité/Eau' },
            ],
          },
          {
            id: 'additional_comments',
            type: 'textarea',
            label: 'Commentaires additionnels',
            required: false,
            placeholder: 'Observations, suggestions, difficultés rencontrées...',
          },
        ],
      },
    ],
  },
};

export default function SurveyFormScreen({ navigation }) {
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [surveyData, setSurveyData] = useState({});
  const [currentSection, setCurrentSection] = useState(0);
  const [gpsData, setGpsData] = useState(null);
  const [gpsLoading, setGpsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [savedSurveys, setSavedSurveys] = useState([]);

  useEffect(() => {
    loadSavedSurveys();
  }, []);

  const loadSavedSurveys = async () => {
    try {
      // Charger enquêtes sauvegardées localement
      const pendingData = await syncService.getPendingData();
      const surveys = pendingData.filter(item => item.type === 'survey');
      setSavedSurveys(surveys);
    } catch (error) {
      console.error('Erreur chargement enquêtes:', error);
    }
  };

  const captureGPS = async () => {
    setGpsLoading(true);
    try {
      const location = await gpsService.getCurrentPosition();
      setGpsData(location);
      Alert.alert('GPS Capturé', 'Position enregistrée avec succès');
    } catch (error) {
      Alert.alert('Erreur GPS', 'Impossible de capturer la position');
    } finally {
      setGpsLoading(false);
    }
  };

  const handleTemplateSelect = (template) => {
    setSelectedTemplate(template);
    setSurveyData({});
    setCurrentSection(0);
    setGpsData(null);
  };

  const handleFieldChange = (fieldId, value) => {
    setSurveyData(prev => ({
      ...prev,
      [fieldId]: value,
    }));
  };

  const nextSection = () => {
    if (currentSection < selectedTemplate.sections.length - 1) {
      setCurrentSection(currentSection + 1);
    }
  };

  const prevSection = () => {
    if (currentSection > 0) {
      setCurrentSection(currentSection - 1);
    }
  };

  const validateCurrentSection = () => {
    const section = selectedTemplate.sections[currentSection];
    const requiredFields = section.fields.filter(field => field.required);
    
    for (const field of requiredFields) {
      if (!surveyData[field.id] || 
          (Array.isArray(surveyData[field.id]) && surveyData[field.id].length === 0)) {
        Alert.alert('Validation', `Le champ "${field.label}" est requis`);
        return false;
      }
    }
    return true;
  };

  const handleNext = () => {
    if (validateCurrentSection()) {
      nextSection();
    }
  };

  const submitSurvey = async () => {
    if (!validateCurrentSection()) return;
    if (!gpsData) {
      Alert.alert('GPS Requis', 'Veuillez capturer votre position GPS avant de soumettre');
      return;
    }

    setIsSubmitting(true);
    try {
      const surveyPayload = {
        template_id: selectedTemplate.id,
        template_title: selectedTemplate.title,
        data: surveyData,
        gps_data: gpsData,
        timestamp: new Date().toISOString(),
        surveyor_notes: surveyData.additional_comments || '',
      };

      // Tentative soumission en ligne ou sauvegarde offline
      try {
        const response = await apiClient.post('/surveys/submit/', surveyPayload);
        Alert.alert(
          'Enquête Soumise',
          'L\'enquête a été enregistrée avec succès',
          [
            {
              text: 'Nouvelle Enquête',
              onPress: () => {
                setSelectedTemplate(null);
                setSurveyData({});
                setGpsData(null);
              }
            },
            {
              text: 'Retour',
              onPress: () => navigation.goBack()
            }
          ]
        );
      } catch (error) {
        // Sauvegarde offline
        await syncService.saveOffline({
          type: 'survey',
          data: surveyPayload,
        });
        
        Alert.alert(
          'Enquête Sauvegardée',
          'L\'enquête a été sauvegardée hors ligne et sera synchronisée dès la reconnexion',
          [{ text: 'OK', onPress: () => setSelectedTemplate(null) }]
        );
      }
    } catch (error) {
      Alert.alert('Erreur', 'Impossible de sauvegarder l\'enquête');
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderField = (field) => {
    switch (field.type) {
      case 'text':
      case 'number':
        return (
          <TextInput
            key={field.id}
            label={field.label + (field.required ? ' *' : '')}
            value={surveyData[field.id] || ''}
            onChangeText={(value) => handleFieldChange(field.id, value)}
            keyboardType={field.type === 'number' ? 'numeric' : 'default'}
            mode="outlined"
            style={styles.fieldInput}
            placeholder={field.placeholder}
          />
        );

      case 'textarea':
        return (
          <TextInput
            key={field.id}
            label={field.label + (field.required ? ' *' : '')}
            value={surveyData[field.id] || ''}
            onChangeText={(value) => handleFieldChange(field.id, value)}
            mode="outlined"
            multiline
            numberOfLines={3}
            style={styles.fieldInput}
            placeholder={field.placeholder}
          />
        );

      case 'radio':
        return (
          <View key={field.id} style={styles.fieldContainer}>
            <Paragraph style={styles.fieldLabel}>
              {field.label}{field.required && ' *'}
            </Paragraph>
            <RadioButton.Group
              onValueChange={(value) => handleFieldChange(field.id, value)}
              value={surveyData[field.id] || ''}
            >
              {field.options.map(option => (
                <View key={option.value} style={styles.radioOption}>
                  <RadioButton value={option.value} />
                  <Paragraph style={styles.radioLabel}>{option.label}</Paragraph>
                </View>
              ))}
            </RadioButton.Group>
          </View>
        );

      case 'checkbox':
        return (
          <View key={field.id} style={styles.fieldContainer}>
            <Paragraph style={styles.fieldLabel}>
              {field.label}{field.required && ' *'}
            </Paragraph>
            {field.options.map(option => (
              <View key={option.value} style={styles.checkboxOption}>
                <Checkbox
                  status={(surveyData[field.id] || []).includes(option.value) ? 'checked' : 'unchecked'}
                  onPress={() => {
                    const currentValues = surveyData[field.id] || [];
                    const newValues = currentValues.includes(option.value)
                      ? currentValues.filter(v => v !== option.value)
                      : [...currentValues, option.value];
                    handleFieldChange(field.id, newValues);
                  }}
                />
                <Paragraph style={styles.checkboxLabel}>{option.label}</Paragraph>
              </View>
            ))}
          </View>
        );

      default:
        return null;
    }
  };

  if (!selectedTemplate) {
    return (
      <View style={styles.container}>
        <ScrollView style={styles.templatesContainer}>
          <Title style={styles.pageTitle}>📋 Enquêtes Terrain</Title>
          
          <Paragraph style={styles.pageDescription}>
            Sélectionnez le type d'enquête à réaliser sur le terrain
          </Paragraph>

          {Object.values(SURVEY_TEMPLATES).map(template => (
            <Card key={template.id} style={styles.templateCard} onPress={() => handleTemplateSelect(template)}>
              <Card.Content>
                <Title style={styles.templateTitle}>{template.title}</Title>
                <Paragraph style={styles.templateDescription}>
                  {template.description}
                </Paragraph>
                <View style={styles.templateInfo}>
                  <Chip mode="outlined" style={styles.sectionsChip}>
                    {template.sections.length} sections
                  </Chip>
                  <Chip mode="outlined" style={styles.fieldsChip}>
                    {template.sections.reduce((total, section) => total + section.fields.length, 0)} questions
                  </Chip>
                </View>
              </Card.Content>
            </Card>
          ))}

          {/* Enquêtes sauvegardées */}
          {savedSurveys.length > 0 && (
            <Card style={styles.savedSurveysCard}>
              <Card.Content>
                <Title style={styles.savedTitle}>💾 Enquêtes en attente</Title>
                <Paragraph style={styles.savedDescription}>
                  {savedSurveys.length} enquête{savedSurveys.length > 1 ? 's' : ''} à synchroniser
                </Paragraph>
                {savedSurveys.slice(0, 3).map((survey, index) => (
                  <Surface key={survey.id} style={styles.savedSurveyItem}>
                    <View style={styles.savedSurveyContent}>
                      <Icon name="assignment" size={24} color="#FF9800" />
                      <View style={styles.savedSurveyInfo}>
                        <Paragraph style={styles.savedSurveyTitle}>
                          {survey.data.template_title}
                        </Paragraph>
                        <Paragraph style={styles.savedSurveyDate}>
                          {format(new Date(survey.timestamp), 'dd/MM/yyyy HH:mm', { locale: fr })}
                        </Paragraph>
                      </View>
                      <Chip mode="outlined" style={styles.pendingChip}>
                        En attente
                      </Chip>
                    </View>
                  </Surface>
                ))}
                <Button
                  mode="outlined"
                  onPress={() => navigation.navigate('Sync')}
                  style={styles.syncButton}
                  icon="sync"
                >
                  Synchroniser ({savedSurveys.length})
                </Button>
              </Card.Content>
            </Card>
          )}
        </ScrollView>
      </View>
    );
  }

  const currentSectionData = selectedTemplate.sections[currentSection];
  const progress = (currentSection + 1) / selectedTemplate.sections.length;

  return (
    <View style={styles.container}>
      {/* En-tête avec progression */}
      <Surface style={styles.header}>
        <View style={styles.headerContent}>
          <View style={styles.headerInfo}>
            <Title style={styles.surveyTitle}>{selectedTemplate.title}</Title>
            <Paragraph style={styles.sectionTitle}>
              {currentSectionData.title} ({currentSection + 1}/{selectedTemplate.sections.length})
            </Paragraph>
          </View>
          <Button
            mode="text"
            onPress={() => setSelectedTemplate(null)}
            icon="close"
          >
            Annuler
          </Button>
        </View>
        <ProgressBar
          progress={progress}
          style={styles.progressBar}
          color="#2E7D32"
        />
      </Surface>

      {/* Contenu section */}
      <ScrollView style={styles.formContainer}>
        <Card style={styles.sectionCard}>
          <Card.Content>
            {currentSectionData.fields.map(field => renderField(field))}
          </Card.Content>
        </Card>

        {/* GPS Section */}
        <Card style={styles.gpsCard}>
          <Card.Content>
            <Title style={styles.gpsTitle}>📍 Localisation GPS</Title>
            {gpsData ? (
              <View style={styles.gpsSuccess}>
                <Icon name="check-circle" size={24} color="#4CAF50" />
                <View style={styles.gpsInfo}>
                  <Paragraph>Position capturée</Paragraph>
                  <Paragraph style={styles.gpsCoords}>
                    {gpsData.latitude.toFixed(6)}, {gpsData.longitude.toFixed(6)}
                  </Paragraph>
                  <Paragraph style={styles.gpsAccuracy}>
                    Précision: {Math.round(gpsData.accuracy)}m
                  </Paragraph>
                </View>
              </View>
            ) : (
              <Button
                mode="contained"
                onPress={captureGPS}
                loading={gpsLoading}
                disabled={gpsLoading}
                style={styles.gpsButton}
                icon="my-location"
              >
                {gpsLoading ? 'Capture GPS...' : 'Capturer Position'}
              </Button>
            )}
          </Card.Content>
        </Card>
      </ScrollView>

      {/* Navigation */}
      <Surface style={styles.navigation}>
        <Button
          mode="outlined"
          onPress={prevSection}
          disabled={currentSection === 0}
          style={styles.navButton}
          icon="chevron-left"
        >
          Précédent
        </Button>

        {currentSection < selectedTemplate.sections.length - 1 ? (
          <Button
            mode="contained"
            onPress={handleNext}
            style={styles.navButton}
            icon="chevron-right"
          >
            Suivant
          </Button>
        ) : (
          <Button
            mode="contained"
            onPress={submitSurvey}
            loading={isSubmitting}
            disabled={isSubmitting || !gpsData}
            style={styles.navButton}
            icon="send"
          >
            {isSubmitting ? 'Soumission...' : 'Soumettre'}
          </Button>
        )}
      </Surface>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  templatesContainer: {
    flex: 1,
    padding: 16,
  },
  pageTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 8,
  },
  pageDescription: {
    textAlign: 'center',
    color: '#666',
    marginBottom: 24,
  },
  templateCard: {
    marginBottom: 16,
    elevation: 3,
  },
  templateTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  templateDescription: {
    color: '#666',
    marginBottom: 12,
  },
  templateInfo: {
    flexDirection: 'row',
    gap: 8,
  },
  sectionsChip: {
    backgroundColor: '#E3F2FD',
  },
  fieldsChip: {
    backgroundColor: '#E8F5E8',
  },
  savedSurveysCard: {
    marginTop: 24,
    marginBottom: 16,
    elevation: 2,
  },
  savedTitle: {
    fontSize: 18,
    marginBottom: 8,
  },
  savedDescription: {
    color: '#666',
    marginBottom: 16,
  },
  savedSurveyItem: {
    padding: 12,
    marginBottom: 8,
    borderRadius: 8,
    elevation: 1,
  },
  savedSurveyContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  savedSurveyInfo: {
    flex: 1,
    marginLeft: 12,
  },
  savedSurveyTitle: {
    fontWeight: 'bold',
    marginBottom: 2,
  },
  savedSurveyDate: {
    fontSize: 12,
    color: '#666',
  },
  pendingChip: {
    backgroundColor: '#FFF3E0',
  },
  syncButton: {
    marginTop: 12,
  },
  header: {
    elevation: 4,
    paddingHorizontal: 16,
    paddingTop: 16,
    paddingBottom: 8,
  },
  headerContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  headerInfo: {
    flex: 1,
  },
  surveyTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  sectionTitle: {
    color: '#666',
    fontSize: 14,
  },
  progressBar: {
    height: 6,
    borderRadius: 3,
  },
  formContainer: {
    flex: 1,
    padding: 16,
  },
  sectionCard: {
    marginBottom: 16,
    elevation: 2,
  },
  fieldContainer: {
    marginBottom: 20,
  },
  fieldLabel: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 12,
    color: '#333',
  },
  fieldInput: {
    marginBottom: 16,
  },
  radioOption: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  radioLabel: {
    marginLeft: 8,
    flex: 1,
  },
  checkboxOption: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  checkboxLabel: {
    marginLeft: 8,
    flex: 1,
  },
  gpsCard: {
    marginBottom: 16,
    elevation: 2,
  },
  gpsTitle: {
    fontSize: 16,
    marginBottom: 12,
  },
  gpsSuccess: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  gpsInfo: {
    marginLeft: 12,
    flex: 1,
  },
  gpsCoords: {
    fontFamily: 'monospace',
    fontSize: 12,
    color: '#666',
  },
  gpsAccuracy: {
    fontSize: 12,
    color: '#666',
  },
  gpsButton: {
    alignSelf: 'flex-start',
  },
  navigation: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    padding: 16,
    elevation: 8,
  },
  navButton: {
    flex: 0.45,
  },
});