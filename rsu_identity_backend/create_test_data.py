"""
🇬🇦 RSU Gabon - Création Données Test
Standards Top 1% - Populate DB avec inscriptions & paiements
Fichier: rsu_identity_backend/create_test_data.py
"""

import os
import django
from datetime import date, timedelta
from decimal import Decimal
import random
# Importer Sum pour l'agrégation de base de données
from django.db.models import Sum 

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rsu_identity.settings.development')
django.setup()

from apps.programs_app.models import SocialProgram, ProgramEnrollment, Payment
from apps.identity_app.models import PersonIdentity, Household
from apps.core_app.models import RSUUser

def create_test_enrollments_and_payments():
    """Créer inscriptions et paiements de test pour TOUS les programmes"""
    
    print("🚀 Création données test RSU Gabon...")
    print("=" * 50)
    
    # Vérifier bénéficiaires disponibles
    total_persons = PersonIdentity.objects.count()
    total_households = Household.objects.count()
    
    print(f"📊 Population actuelle:")
    print(f"  - {total_persons} personnes")
    print(f"  - {total_households} ménages")
    print()
    
    if total_persons < 20:
        print("❌ ERREUR: Pas assez de bénéficiaires")
        print("  Minimum requis: 20 personnes")
        print()
        print("🔧 SOLUTION:")
        print("  Exécuter d'abord: python create_realistic_gabon_data.py")
        print("  Ce script créera 100 personnes + 25 ménages")
        return
    
    # Récupérer tous les programmes
    programs = SocialProgram.objects.all()
    
    if not programs.exists():
        print("❌ Aucun programme trouvé")
        print("  Créer d'abord avec: python setup_programs.py")
        return
    
    print(f"✅ {programs.count()} programmes trouvés")
    print()
    
    # Compteurs globaux
    total_enrollments = 0
    total_payments = 0
    
    # Pour chaque programme
    for program in programs:
        print(f"📋 Programme: {program.name} ({program.code})")
        print("-" * 50)
        
        # S'assurer qu'on peut inscrire des gens
        if program.max_beneficiaries <= 0 or program.benefit_amount is None:
             print("⚠️ Programme ignoré: Capacité ou montant de prestation invalide.")
             continue
        
        # Nombre d'inscriptions à tenter
        target_enrollments = min(
            random.randint(10, 30),
            program.max_beneficiaries,
            total_persons
        )
        
        # Sélectionner bénéficiaires aléatoires (un seul queryset pour les tests)
        all_persons = list(PersonIdentity.objects.all().order_by('?'))
        
        beneficiaries_to_enroll = []
        
        # Tenter d'inscrire le nombre cible de personnes
        for person in all_persons:
            # Vérifier si l'inscription existe déjà pour ce programme
            if not ProgramEnrollment.objects.filter(program=program, beneficiary=person).exists():
                 beneficiaries_to_enroll.append(person)
            
            if len(beneficiaries_to_enroll) >= target_enrollments:
                break
        
        target_enrollments = len(beneficiaries_to_enroll)
        
        if target_enrollments == 0:
            print("❌ Aucun nouveau bénéficiaire éligible trouvé pour l'inscription.")
            print("-" * 50)
            continue
            
        print(f"  → Objectif: {target_enrollments} nouvelles inscriptions")

        # Statuts à distribuer
        statuses_distribution = {
            'PENDING': int(target_enrollments * 0.2),
            'APPROVED': int(target_enrollments * 0.25),
            'REJECTED': int(target_enrollments * 0.15),
            'ACTIVE': int(target_enrollments * 0.3),
            'COMPLETED': int(target_enrollments * 0.1),
        }
        
        # Créer liste de statuts
        statuses_list = []
        for status, count in statuses_distribution.items():
            statuses_list.extend([status] * count)
        
        # Compléter si manquant (le reste va à 'ACTIVE')
        while len(statuses_list) < target_enrollments:
            statuses_list.append('ACTIVE')
        
        random.shuffle(statuses_list)
        
        program_enrollments = 0
        program_payments = 0
        
        # Créer inscriptions
        for idx, beneficiary in enumerate(beneficiaries_to_enroll):
            status = statuses_list[idx]
            
            # Pas besoin de vérifier l'existence ici, c'est fait pendant la sélection.
            
            # Date inscription (entre 6 mois et aujourd'hui)
            days_ago = random.randint(1, 180)
            enrollment_date = date.today() - timedelta(days=days_ago)
            
            # Dates selon statut
            approval_date = None
            start_date = None
            end_date = None
            
            if status in ['APPROVED', 'ACTIVE', 'COMPLETED']:
                approval_date = enrollment_date + timedelta(days=random.randint(1, 15))
            
            if status in ['ACTIVE', 'COMPLETED']:
                # S'assurer que start_date est après approval_date
                start_date = (approval_date or enrollment_date) + timedelta(days=random.randint(1, 7))
            
            if status == 'COMPLETED':
                if start_date:
                    end_date = start_date + timedelta(days=random.randint(90, 180))
                    # S'assurer que la date de fin n'est pas dans le futur
                    if end_date > date.today(): 
                        end_date = date.today() - timedelta(days=1)
                else:
                    # Cas de secours pour les COMPLETED sans start_date réaliste
                    end_date = date.today() - timedelta(days=random.randint(1, 10))
            
            # Créer inscription
            enrollment = ProgramEnrollment.objects.create(
                program=program,
                beneficiary=beneficiary,
                status=status,
                enrollment_date=enrollment_date,
                approval_date=approval_date,
                start_date=start_date,
                end_date=end_date
            )
            
            program_enrollments += 1
            
            # Emoji selon statut
            emoji = {
                'PENDING': '⏳',
                'APPROVED': '✅',
                'REJECTED': '❌',
                'ACTIVE': '🟢',
                'COMPLETED': '🔵'
            }.get(status, '⚪')
            
            print(f"  {emoji} {beneficiary.full_name} → {status}")
            
            # Créer paiements pour ACTIVE et COMPLETED
            if status in ['ACTIVE', 'COMPLETED'] and start_date:
                
                if program.frequency == 'ONE_TIME':
                    num_payments = 1
                    payment_interval = 0
                else: 
                    if status == 'COMPLETED':
                        num_payments = random.randint(3, 6)
                    else:  # ACTIVE
                        num_payments = random.randint(1, 3)

                    if program.frequency == 'MONTHLY':
                        payment_interval = 30
                    elif program.frequency == 'QUARTERLY':
                        payment_interval = 90
                    elif program.frequency == 'ANNUAL':
                        payment_interval = 365
                    else: 
                        payment_interval = 0
                
                # Créer paiements
                for payment_idx in range(num_payments):
                    
                    if program.frequency == 'ONE_TIME':
                        payment_date = start_date + timedelta(days=random.randint(1, 30))
                    else:
                        payment_date = start_date + timedelta(days=payment_idx * payment_interval)
                    
                    # Vérifier que date n'est pas dans le futur
                    if payment_date > date.today():
                        continue
                    
                    # Statut paiement
                    if status == 'COMPLETED' or payment_date < date.today() - timedelta(days=30):
                        payment_status = 'COMPLETED'
                    else:
                        payment_status = random.choice(['COMPLETED', 'PENDING'])
                    
                    # Créer paiement
                    Payment.objects.create(
                        program=program,
                        enrollment=enrollment,
                        beneficiary=beneficiary,
                        amount=program.benefit_amount,
                        status=payment_status,
                        payment_date=payment_date,
                        reference=f"PAY-{program.code}-{enrollment.id}-{payment_idx + 1:03d}"
                    )
                    
                    program_payments += 1
                    print(f"      💰 Paiement {payment_idx + 1}: {program.benefit_amount} FCFA ({payment_status})")
        
        # =========================================================================
        # ✅ CORRECTION CRITIQUE: Mise à jour des compteurs du programme
        # =========================================================================
        
        # 1. Mise à jour des bénéficiaires actuels (ACTIVE ou COMPLETED sont les 'current_beneficiaries')
        program.current_beneficiaries = ProgramEnrollment.objects.filter(
            program=program,
            status__in=['ACTIVE', 'COMPLETED']
        ).count()
        
        # 2. Correction du calcul de budget dépensé via agrégation DB (plus précis et performant)
        spent_aggregate = Payment.objects.filter(
            program=program,
            status='COMPLETED'
        ).aggregate(total_spent=Sum('amount'))
        
        # Utiliser Decimal('0.00') si l'agrégation renvoie None (aucun paiement)
        program.budget_spent = spent_aggregate['total_spent'] or Decimal('0.00')
        
        # 3. Calcul du budget restant
        program.budget_remaining = program.total_budget - program.budget_spent
        
        program.save()
        
        total_enrollments += program_enrollments
        total_payments += program_payments
        
        print(f"  ✅ {program_enrollments} inscriptions | {program_payments} paiements")
        print(f"  📊 Budget dépensé mis à jour: {program.budget_spent} FCFA")
        print("-" * 50)
    
    print("=" * 50)
    print("✅ CRÉATION TERMINÉE")
    print("=" * 50)
    print(f"📊 Résumé global:")
    print(f"  - {programs.count()} programmes enrichis")
    print(f"  - {total_enrollments} inscriptions créées")
    print(f"  - {total_payments} paiements créés")
    print()
    
    # Statistiques détaillées
    print("📈 Statistiques par programme:")
    for program in programs:
        enrollments_count = ProgramEnrollment.objects.filter(program=program).count()
        payments_count = Payment.objects.filter(program=program).count()
        print(f"  • {program.code}: {enrollments_count} inscriptions, {payments_count} paiements, {program.budget_spent} dépensé")
    print()
    
    print("🧪 TESTER MAINTENANT:")
    print("  1. Ouvrir http://localhost:3000")
    print("  2. Se connecter (admin / admin123)")
    print("  3. Aller dans Programmes")
    print("  4. Cliquer sur n'importe quel programme")
    print("  5. Onglets enrichis:")
    print("      ✅ Vue d'ensemble → Graphiques budget/capacité")
    print("      ✅ Bénéficiaires → Table avec inscriptions")
    print("      ✅ Paiements → Timeline complète")
    print("      ✅ Analytics → Placeholder")
    print()

if __name__ == '__main__':
    create_test_enrollments_and_payments()