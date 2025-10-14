// =============================================================================
// 1. PERSON DETAIL SCREEN (screens/Person/PersonDetailScreen.jsx)
// =============================================================================
import React, { useState, useEffect } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  Alert,
  RefreshControl,
} from 'react-native';
import {
  Card,
  Title,
  Paragraph,
  Button,
  Chip,
  Avatar,
  List,
  Divider,
  ProgressBar,
  Surface,
  IconButton,
} from 'react-native-paper';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';

import apiClient from '../../services/api/apiClient';
import { GABON_PROVINCES } from '../../constants/gabonData';

export default function PersonDetailScreen({ route, navigation }) {
  const { person: initialPerson } = route.params;
  const [person, setPerson] = useState(initialPerson);
  const [assessments, setAssessments] = useState([]);
  const [household, setHousehold] = useState(null);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadPersonDetails();
  }, []);

  const loadPersonDetails = async () => {
    setLoading(true);
    try {
      // Charger détails complets personne
      const personResponse = await apiClient.get(`/identity/persons/${person.id}/`);
      setPerson(personResponse.data);

      // Charger historique assessments vulnérabilité
      const assessmentsResponse = await apiClient.get(
        `/services/vulnerability-assessments/?person=${person.id}&ordering=-assessment_date`
      );
      setAssessments(assessmentsResponse.data.results || []);

      // Charger ménage associé
      if (personResponse.data.household_id) {
        const householdResponse = await apiClient.get(
          `/identity/households/${personResponse.data.household_id}/`
        );
        setHousehold(householdResponse.data);
      }
    } catch (error) {
      console.error('Erreur chargement détails:', error);
      Alert.alert('Erreur', 'Impossible de charger les détails');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = () => {
    setRefreshing(true);
    loadPersonDetails();
  };

  const handleNewAssessment = async () => {
    try {
      const response = await apiClient.post(
        '/services/vulnerability-assessments/calculate_assessment/',
        { person_id: person.id }
      );
      
      Alert.alert(
        'Nouvel Assessment',
        `Score: ${response.data.vulnerability_score}/100\nNiveau: ${response.data.risk_level}`,
        [{ text: 'OK', onPress: loadPersonDetails }]
      );
    } catch (error) {
      Alert.alert('Erreur', 'Impossible de calculer le nouvel assessment');
    }
  };

  const getVulnerabilityColor = (score) => {
    if (score >= 75) return '#F44336';
    if (score >= 50) return '#FF9800';
    if (score >= 25) return '#4CAF50';
    return '#9C27B0';
  };

  const getVulnerabilityIcon = (level) => {
    switch (level) {
      case 'CRITICAL': return 'warning';
      case 'HIGH': return 'error-outline';
      case 'MODERATE': return 'info-outline';
      case 'LOW': return 'check-circle-outline';
      default: return 'help-outline';
    }
  };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
      }
    >
      {/* En-tête personne */}
      <Card style={styles.headerCard}>
        <Card.Content>
          <View style={styles.headerContent}>
            <Avatar.Text
              size={70}
              label={`${person.first_name[0]}${person.last_name[0]}`}
              style={styles.avatar}
            />
            <View style={styles.headerInfo}>
              <Title style={styles.personName}>
                {person.first_name} {person.last_name}
              </Title>
              <Paragraph style={styles.personDetails}>
                RSU-ID: {person.rsu_id}
              </Paragraph>
              <Paragraph style={styles.personDetails}>
                NIP: {person.nip} • {person.phone}
              </Paragraph>
              <View style={styles.statusContainer}>
                <Chip
                  mode="outlined"
                  style={[
                    styles.statusChip,
                    person.verification_status === 'VERIFIED' && styles.verifiedChip,
                  ]}
                >
                  {person.verification_status === 'VERIFIED' ? 'Vérifié' : 'En attente'}
                </Chip>
              </View>
            </View>
          </View>
        </Card.Content>
      </Card>

      {/* Informations personnelles */}
      <Card style={styles.sectionCard}>
        <Card.Content>
          <Title style={styles.sectionTitle}>📋 Informations Personnelles</Title>
          
          <View style={styles.infoGrid}>
            <View style={styles.infoItem}>
              <Paragraph style={styles.infoLabel}>Date de naissance</Paragraph>
              <Paragraph style={styles.infoValue}>
                {format(new Date(person.birth_date), 'dd MMMM yyyy', { locale: fr })}
              </Paragraph>
            </View>
            
            <View style={styles.infoItem}>
              <Paragraph style={styles.infoLabel}>Genre</Paragraph>
              <Paragraph style={styles.infoValue}>
                {person.gender === 'M' ? 'Masculin' : 'Féminin'}
              </Paragraph>
            </View>
            
            <View style={styles.infoItem}>
              <Paragraph style={styles.infoLabel}>Province</Paragraph>
              <Paragraph style={styles.infoValue}>
                {GABON_PROVINCES[person.province]?.name || person.province}
              </Paragraph>
            </View>
            
            <View style={styles.infoItem}>
              <Paragraph style={styles.infoLabel}>District</Paragraph>
              <Paragraph style={styles.infoValue}>
                {person.district || 'Non renseigné'}
              </Paragraph>
            </View>
            
            <View style={styles.infoItem}>
              <Paragraph style={styles.infoLabel}>Niveau d'éducation</Paragraph>
              <Paragraph style={styles.infoValue}>
                {person.education_level || 'Non renseigné'}
              </Paragraph>
            </View>
            
            <View style={styles.infoItem}>
              <Paragraph style={styles.infoLabel}>Statut professionnel</Paragraph>
              <Paragraph style={styles.infoValue}>
                {person.occupation_status || 'Non renseigné'}
              </Paragraph>
            </View>
          </View>
        </Card.Content>
      </Card>

      {/* Score vulnérabilité actuel */}
      {person.vulnerability_score && (
        <Card style={styles.vulnerabilityCard}>
          <Card.Content>
            <View style={styles.vulnerabilityHeader}>
              <Title style={styles.sectionTitle}>🛡️ Score Vulnérabilité</Title>
              <Button
                mode="outlined"
                onPress={handleNewAssessment}
                style={styles.recalculateButton}
                icon="refresh"
              >
                Recalculer
              </Button>
            </View>
            
            <View style={styles.scoreDisplay}>
              <Avatar.Icon
                size={80}
                icon={getVulnerabilityIcon(person.vulnerability_level)}
                style={[
                  styles.scoreIcon,
                  { backgroundColor: getVulnerabilityColor(person.vulnerability_score) }
                ]}
              />
              <View style={styles.scoreInfo}>
                <Title style={styles.scoreValue}>
                  {Math.round(person.vulnerability_score)}/100
                </Title>
                <Paragraph style={styles.scoreLevel}>
                  {person.vulnerability_level === 'CRITICAL' ? 'Critique' :
                   person.vulnerability_level === 'HIGH' ? 'Élevée' :
                   person.vulnerability_level === 'MODERATE' ? 'Modérée' : 'Faible'}
                </Paragraph>
                <ProgressBar
                  progress={person.vulnerability_score / 100}
                  style={styles.scoreProgress}
                  color={getVulnerabilityColor(person.vulnerability_score)}
                />
              </View>
            </View>
            
            {person.last_vulnerability_assessment && (
              <Paragraph style={styles.lastAssessment}>
                Dernière évaluation: {format(
                  new Date(person.last_vulnerability_assessment),
                  'dd/MM/yyyy HH:mm',
                  { locale: fr }
                )}
              </Paragraph>
            )}
          </Card.Content>
        </Card>
      )}

      {/* Informations ménage */}
      {household && (
        <Card style={styles.sectionCard}>
          <Card.Content>
            <Title style={styles.sectionTitle}>🏠 Informations Ménage</Title>
            
            <View style={styles.householdGrid}>
              <View style={styles.householdItem}>
                <Icon name="people" size={24} color="#2E7D32" />
                <View style={styles.householdInfo}>
                  <Paragraph style={styles.householdLabel}>Taille ménage</Paragraph>
                  <Paragraph style={styles.householdValue}>
                    {household.household_size} personnes
                  </Paragraph>
                </View>
              </View>
              
              <View style={styles.householdItem}>
                <Icon name="account-child" size={24} color="#FF9800" />
                <View style={styles.householdInfo}>
                  <Paragraph style={styles.householdLabel}>Personnes à charge</Paragraph>
                  <Paragraph style={styles.householdValue}>
                    {household.dependents || 0}
                  </Paragraph>
                </View>
              </View>
              
              <View style={styles.householdItem}>
                <Icon name="attach-money" size={24} color="#4CAF50" />
                <View style={styles.householdInfo}>
                  <Paragraph style={styles.householdLabel}>Revenu mensuel</Paragraph>
                  <Paragraph style={styles.householdValue}>
                    {household.total_monthly_income?.toLocaleString()} FCFA
                  </Paragraph>
                </View>
              </View>
              
              <View style={styles.householdItem}>
                <Icon name="home" size={24} color="#9C27B0" />
                <View style={styles.householdInfo}>
                  <Paragraph style={styles.householdLabel}>Type logement</Paragraph>
                  <Paragraph style={styles.householdValue}>
                    {household.housing_type || 'Non renseigné'}
                  </Paragraph>
                </View>
              </View>
            </View>
          </Card.Content>
        </Card>
      )}

      {/* Historique assessments */}
      <Card style={styles.sectionCard}>
        <Card.Content>
          <View style={styles.historyHeader}>
            <Title style={styles.sectionTitle}>📊 Historique Assessments</Title>
            <Paragraph style={styles.historyCount}>
              {assessments.length} évaluation{assessments.length > 1 ? 's' : ''}
            </Paragraph>
          </View>
          
          {assessments.length === 0 ? (
            <View style={styles.emptyHistory}>
              <Icon name="assessment" size={48} color="#ccc" />
              <Paragraph style={styles.emptyText}>
                Aucun assessment enregistré
              </Paragraph>
              <Button
                mode="contained"
                onPress={handleNewAssessment}
                style={styles.newAssessmentButton}
                icon="add"
              >
                Premier Assessment
              </Button>
            </View>
          ) : (
            assessments.map((assessment, index) => (
              <Surface key={assessment.id} style={styles.assessmentItem}>
                <View style={styles.assessmentHeader}>
                  <View style={styles.assessmentInfo}>
                    <Title style={styles.assessmentScore}>
                      {Math.round(assessment.vulnerability_score)}/100
                    </Title>
                    <Paragraph style={styles.assessmentDate}>
                      {format(
                        new Date(assessment.assessment_date),
                        'dd MMM yyyy HH:mm',
                        { locale: fr }
                      )}
                    </Paragraph>
                  </View>
                  
                  <Chip
                    mode="outlined"
                    style={[
                      styles.riskChip,
                      { backgroundColor: `${getVulnerabilityColor(assessment.vulnerability_score)}20` }
                    ]}
                  >
                    {assessment.risk_level === 'CRITICAL' ? 'Critique' :
                     assessment.risk_level === 'HIGH' ? 'Élevée' :
                     assessment.risk_level === 'MODERATE' ? 'Modérée' : 'Faible'}
                  </Chip>
                </View>
                
                {/* Détail dimensions */}
                <View style={styles.dimensionsContainer}>
                  {[
                    { key: 'economic', label: 'Économique', score: assessment.economic_vulnerability_score },
                    { key: 'social', label: 'Social', score: assessment.social_vulnerability_score },
                    { key: 'household', label: 'Ménage', score: assessment.household_composition_score },
                  ].map(dimension => (
                    <View key={dimension.key} style={styles.dimensionItem}>
                      <Paragraph style={styles.dimensionLabel}>
                        {dimension.label}
                      </Paragraph>
                      <View style={styles.dimensionScore}>
                        <ProgressBar
                          progress={dimension.score / 100}
                          style={styles.dimensionProgress}
                          color={getVulnerabilityColor(dimension.score)}
                        />
                        <Paragraph style={styles.dimensionValue}>
                          {Math.round(dimension.score)}
                        </Paragraph>
                      </View>
                    </View>
                  ))}
                </View>
                
                {/* Facteurs identifiés */}
                {assessment.vulnerability_factors && assessment.vulnerability_factors.length > 0 && (
                  <View style={styles.factorsContainer}>
                    <Paragraph style={styles.factorsTitle}>Facteurs identifiés:</Paragraph>
                    <View style={styles.factorsList}>
                      {assessment.vulnerability_factors.slice(0, 3).map((factor, idx) => (
                        <Chip
                          key={idx}
                          mode="outlined"
                          style={styles.factorChip}
                        >
                          {factor}
                        </Chip>
                      ))}
                      {assessment.vulnerability_factors.length > 3 && (
                        <Chip mode="outlined" style={styles.factorChip}>
                          +{assessment.vulnerability_factors.length - 3}
                        </Chip>
                      )}
                    </View>
                  </View>
                )}
                
                {index < assessments.length - 1 && <Divider style={styles.assessmentDivider} />}
              </Surface>
            ))
          )}
        </Card.Content>
      </Card>

      {/* Actions */}
      <Card style={styles.actionsCard}>
        <Card.Content>
          <Title style={styles.sectionTitle}>⚡ Actions</Title>
          
          <View style={styles.actionsList}>
            <Button
              mode="contained"
              onPress={handleNewAssessment}
              style={styles.actionButton}
              icon="assessment"
            >
              Nouvel Assessment
            </Button>
            
            <Button
              mode="outlined"
              onPress={() => navigation.navigate('Enrollment', { person })}
              style={styles.actionButton}
              icon="edit"
            >
              Modifier Informations
            </Button>
            
            <Button
              mode="outlined"
              onPress={() => {/* Exporter données */}}
              style={styles.actionButton}
              icon="file-export"
            >
              Exporter Données
            </Button>
          </View>
        </Card.Content>
      </Card>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  headerCard: {
    margin: 16,
    marginBottom: 12,
    elevation: 4,
  },
  headerContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  avatar: {
    backgroundColor: '#2E7D32',
    marginRight: 16,
  },
  headerInfo: {
    flex: 1,
  },
  personName: {
    fontSize: 22,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  personDetails: {
    color: '#666',
    marginBottom: 2,
  },
  statusContainer: {
    marginTop: 8,
  },
  statusChip: {
    alignSelf: 'flex-start',
  },
  verifiedChip: {
    backgroundColor: '#E8F5E8',
  },
  sectionCard: {
    marginHorizontal: 16,
    marginBottom: 12,
    elevation: 2,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  infoGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  infoItem: {
    width: '48%',
    marginBottom: 16,
  },
  infoLabel: {
    fontSize: 12,
    color: '#666',
    fontWeight: 'bold',
    marginBottom: 4,
  },
  infoValue: {
    fontSize: 14,
    color: '#333',
  },
  vulnerabilityCard: {
    marginHorizontal: 16,
    marginBottom: 12,
    elevation: 3,
  },
  vulnerabilityHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  recalculateButton: {
    alignSelf: 'flex-end',
  },
  scoreDisplay: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  scoreIcon: {
    marginRight: 20,
  },
  scoreInfo: {
    flex: 1,
  },
  scoreValue: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  scoreLevel: {
    fontSize: 16,
    color: '#666',
    marginBottom: 8,
  },
  scoreProgress: {
    height: 8,
    borderRadius: 4,
  },
  lastAssessment: {
    fontSize: 12,
    color: '#666',
    fontStyle: 'italic',
    textAlign: 'center',
  },
  householdGrid: {
    gap: 12,
  },
  householdItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
  },
  householdInfo: {
    marginLeft: 12,
    flex: 1,
  },
  householdLabel: {
    fontSize: 12,
    color: '#666',
    fontWeight: 'bold',
  },
  householdValue: {
    fontSize: 14,
    color: '#333',
    marginTop: 2,
  },
  historyHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  historyCount: {
    color: '#666',
    fontSize: 12,
  },
  emptyHistory: {
    alignItems: 'center',
    paddingVertical: 32,
  },
  emptyText: {
    color: '#666',
    marginVertical: 16,
  },
  newAssessmentButton: {
    marginTop: 8,
  },
  assessmentItem: {
    padding: 16,
    marginBottom: 8,
    borderRadius: 8,
    elevation: 1,
  },
  assessmentHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  assessmentInfo: {
    flex: 1,
  },
  assessmentScore: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  assessmentDate: {
    fontSize: 12,
    color: '#666',
  },
  riskChip: {
    marginLeft: 12,
  },
  dimensionsContainer: {
    marginBottom: 12,
  },
  dimensionItem: {
    marginBottom: 8,
  },
  dimensionLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  dimensionScore: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  dimensionProgress: {
    flex: 1,
    height: 6,
    borderRadius: 3,
    marginRight: 8,
  },
  dimensionValue: {
    fontSize: 12,
    fontWeight: 'bold',
    width: 30,
  },
  factorsContainer: {
    marginTop: 8,
  },
  factorsTitle: {
    fontSize: 12,
    color: '#666',
    marginBottom: 8,
  },
  factorsList: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  factorChip: {
    margin: 2,
  },
  assessmentDivider: {
    marginTop: 12,
  },
  actionsCard: {
    margin: 16,
    marginTop: 12,
    marginBottom: 100,
    elevation: 2,
  },
  actionsList: {
    gap: 12,
  },
  actionButton: {
    marginBottom: 8,
  },
});