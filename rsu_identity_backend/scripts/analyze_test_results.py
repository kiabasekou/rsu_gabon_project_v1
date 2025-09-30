# ===================================================================
# Analyse Résultats Tests Données Terrain
# ===================================================================

from apps.services_app.models import VulnerabilityAssessment
from apps.identity_app.models import PersonIdentity
import statistics


def analyze_vulnerability_distribution():
    """Analyse distribution scores vulnérabilité"""
    
    assessments = VulnerabilityAssessment.objects.filter(is_active=True)
    scores = list(assessments.values_list('global_score', flat=True))
    scores_float = [float(s) for s in scores]
    
    print("\n" + "="*60)
    print("📊 ANALYSE DISTRIBUTION SCORES VULNÉRABILITÉ")
    print("="*60)
    
    print(f"\n📈 Statistiques Descriptives:")
    print(f"   Nombre évaluations: {len(scores)}")
    print(f"   Score moyen: {statistics.mean(scores_float):.2f}")
    print(f"   Médiane: {statistics.median(scores_float):.2f}")
    print(f"   Écart-type: {statistics.stdev(scores_float):.2f}")
    print(f"   Min: {min(scores_float):.2f}")
    print(f"   Max: {max(scores_float):.2f}")
    
    # Distribution par niveaux
    levels = assessments.values('vulnerability_level').annotate(
        count=Count('id')
    )
    
    print(f"\n📊 Distribution par Niveau:")
    for level in levels:
        percentage = (level['count'] / len(scores)) * 100
        print(f"   {level['vulnerability_level']}: {level['count']} ({percentage:.1f}%)")
    
    # Distribution par province
    print(f"\n🗺️ Top 5 Provinces Vulnérables:")
    province_stats = assessments.values('person__province').annotate(
        avg_score=Avg('global_score'),
        count=Count('id')
    ).order_by('-avg_score')[:5]
    
    for prov in province_stats:
        print(f"   {prov['person__province']}: {prov['avg_score']:.1f} (n={prov['count']})")
    
    # Vérifications cohérence
    print(f"\n✅ Vérifications Cohérence:")
    
    # Pas tous les scores identiques
    unique_scores = len(set(scores_float))
    print(f"   Scores uniques: {unique_scores}/{len(scores)}")
    if unique_scores < len(scores) * 0.5:
        print("   ⚠️ WARNING: Trop de scores identiques!")
    else:
        print("   ✅ Bonne diversité scores")
    
    # Distribution raisonnable
    critical = assessments.filter(vulnerability_level='CRITICAL').count()
    low = assessments.filter(vulnerability_level='LOW').count()
    
    if critical > len(scores) * 0.5:
        print("   ⚠️ WARNING: Trop de scores CRITICAL!")
    elif low > len(scores) * 0.5:
        print("   ⚠️ WARNING: Trop de scores LOW!")
    else:
        print("   ✅ Distribution équilibrée")


def analyze_economic_thresholds():
    """Valide pertinence seuils économiques"""
    
    print("\n" + "="*60)
    print("💰 VALIDATION SEUILS ÉCONOMIQUES")
    print("="*60)
    
    from apps.identity_app.models import Household
    
    households = Household.objects.all()
    incomes = list(households.values_list('monthly_income', flat=True))
    incomes_float = [float(i) if i else 0 for i in incomes]
    
    # Comptage par catégorie
    extreme_poverty = sum(1 for i in incomes_float if i < 50000)
    poverty = sum(1 for i in incomes_float if 50000 <= i < 100000)
    low_income = sum(1 for i in incomes_float if 100000 <= i < 300000)
    middle_class = sum(1 for i in incomes_float if i >= 300000)
    
    total = len(incomes_float)
    
    print(f"\n📊 Répartition Revenus:")
    print(f"   Extrême pauvreté (< 50k): {extreme_poverty} ({extreme_poverty/total*100:.1f}%)")
    print(f"   Pauvreté (50k-100k): {poverty} ({poverty/total*100:.1f}%)")
    print(f"   Revenus faibles (100k-300k): {low_income} ({low_income/total*100:.1f}%)")
    print(f"   Classe moyenne (> 300k): {middle_class} ({middle_class/total*100:.1f}%)")
    
    # Recommandations
    print(f"\n💡 Recommandations:")
    if extreme_poverty > total * 0.6:
        print("   ⚠️ Beaucoup d'extrême pauvreté → Valider seuil 50k")
    if middle_class > total * 0.4:
        print("   ⚠️ Beaucoup classe moyenne → Données test biaisées?")
    else:
        print("   ✅ Seuils semblent cohérents avec données")


def generate_calibration_recommendations():
    """Génère recommandations calibrage"""
    
    print("\n" + "="*60)
    print("🎯 RECOMMANDATIONS CALIBRAGE ALGORITHMES")
    print("="*60)
    
    from apps.services_app.models import VulnerabilityAssessment
    
    # Analyser scores par dimension
    assessments = VulnerabilityAssessment.objects.filter(is_active=True)
    
    dimensions = {
        'household': 'household_composition_score',
        'economic': 'economic_vulnerability_score',
        'social': 'social_vulnerability_score',
        'geographic': 'geographic_vulnerability_score',
        'contextual': 'contextual_vulnerability_score'
    }
    
    print(f"\n📊 Scores Moyens par Dimension:")
    for dim_name, field_name in dimensions.items():
        if hasattr(assessments.first(), field_name):
            avg = assessments.aggregate(avg=Avg(field_name))['avg']
            print(f"   {dim_name}: {avg:.1f}/100")
    
    # Recommandations basées sur analyse
    print(f"\n💡 Recommandations:")
    print("   1. Si dimension < 20: Augmenter pondération")
    print("   2. Si dimension > 80: Réduire pondération ou revoir scoring")
    print("   3. Objectif: Toutes dimensions contributives (30-70)")


# Lancer analyses
if __name__ == '__main__':
    from django.db.models import Avg, Count
    
    analyze_vulnerability_distribution()
    analyze_economic_thresholds()
    generate_calibration_recommendations()
    
    print("\n" + "="*60)
    print("✅ ANALYSE COMPLÈTE TERMINÉE")
    print("="*60)


# Exécuter:
# python manage.py shell < scripts/analyze_test_results.py