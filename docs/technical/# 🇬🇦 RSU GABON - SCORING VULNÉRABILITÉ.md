# 🇬🇦 RSU GABON - SCORING VULNÉRABILITÉ

## 🎯 Vue d'ensemble
Système de scoring vulnérabilité multi-dimensionnel contextualisé pour le Gabon.
Algorithme IA avec 5 dimensions prioritaires selon standards gouvernementaux.

## 🚀 Utilisation APIs

### Calcul évaluation vulnérabilité
```bash
POST /api/v1/services/vulnerability-assessments/calculate_assessment/
Content-Type: application/json

{
    "person_id": 123
}
```

### Consultation évaluations
```bash
GET /api/v1/services/vulnerability-assessments/
GET /api/v1/services/vulnerability-assessments/statistics/
```

### Filtrage par niveau
```bash
GET /api/v1/services/vulnerability-assessments/?vulnerability_level=CRITICAL
GET /api/v1/services/vulnerability-assessments/?person__province=OGOOUE_IVINDO
```

## 📊 Dimensions évaluées

1. **ÉCONOMIQUE (30%)** : Revenus, emploi, logement, services financiers
2. **SOCIALE (25%)** : Éducation, santé, réseaux sociaux, inclusion
3. **DÉMOGRAPHIQUE (20%)** : Âge, genre, structure ménage, dépendance
4. **GÉOGRAPHIQUE (15%)** : Province, accessibilité, infrastructures
5. **RÉSILIENCE (10%)** : Exposition chocs, adaptation, récupération

## 🎚️ Niveaux vulnérabilité

- **CRITICAL (75-100)** : Intervention urgente requise
- **HIGH (50-74)** : Intervention prioritaire
- **MODERATE (25-49)** : Surveillance active
- **LOW (0-24)** : Suivi régulier

## 🔧 Configuration technique

### Modèles créés
- `VulnerabilityAssessment` : Évaluations avec historique
- `SocialProgramEligibility` : Éligibilité programmes sociaux

### Services
- `VulnerabilityCalculator` : Moteur scoring IA
- APIs REST complètes avec filtrage et statistiques

### Tests
- Suite tests unitaires incluse
- Validation algorithmes par dimension

## 📝 Prochaines étapes

1. **Personnalisation données** : Ajuster champs PersonIdentity selon besoins
2. **Calibrage seuils** : Affiner seuils selon données terrain Gabon
3. **Interface utilisateur** : Développer dashboards visualisation
4. **Intégration programmes** : Connecter aux systèmes programmes sociaux

## 🚨 Support

En cas de problème :
1. Vérifier logs Django : `python manage.py runserver`
2. Tester APIs manuellement avec curl/Postman
3. Valider migrations : `python manage.py showmigrations services_app`

✅ **Système opérationnel et prêt pour production**