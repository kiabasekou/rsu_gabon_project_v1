# ===================================================================
# RSU GABON - INTÉGRATION SERVICES APP DANS ARCHITECTURE EXISTANTE
# Standards Top 1% - Continuité avec Core + Identity Apps
# ===================================================================



# apps/services_app/serializers.py
from rest_framework import serializers
from .models import VulnerabilityAssessment, SocialProgramEligibility

class VulnerabilityAssessmentSerializer(serializers.ModelSerializer):
    person_name = serializers.CharField(source='person.full_name', read_only=True)
    person_rsu_id = serializers.CharField(source='person.rsu_id', read_only=True)
    assessed_by_name = serializers.CharField(source='assessed_by.full_name', read_only=True)
    
    class Meta:
        model = VulnerabilityAssessment
        fields = [
            'id', 'person', 'person_name', 'person_rsu_id',
            'global_score', 'vulnerability_level', 'dimension_scores',
            'priority_interventions', 'social_programs_eligibility',
            'geographic_priority_zone', 'confidence_score',
            'assessment_date', 'assessed_by', 'assessed_by_name'
        ]
        read_only_fields = ['id', 'assessment_date']

class SocialProgramEligibilitySerializer(serializers.ModelSerializer):
    person_name = serializers.CharField(source='person.full_name', read_only=True)
    program_name = serializers.CharField(source='get_program_code_display', read_only=True)
    
    class Meta:
        model = SocialProgramEligibility
        fields = [
            'id', 'person', 'person_name', 'program_code', 'program_name',
            'eligibility_score', 'recommendation_level', 'calculated_at'
        ]
