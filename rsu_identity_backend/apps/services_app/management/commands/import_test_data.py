# ===================================================================
# Management Command - Import Données Test
# ===================================================================

# management/commands/import_test_data.py - VERSION CORRIGÉE

# management/commands/import_test_data.py - VERSION ADAPTÉE AU CSV RÉEL
# management/commands/import_test_data.py - VERSION ADAPTÉE AU CSV RÉEL

import csv
import json
from decimal import Decimal
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.identity_app.models import PersonIdentity, Household

class Command(BaseCommand):
    help = 'Import données test depuis CSV (format: age au lieu de birth_date)'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Chemin fichier CSV')

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        
        self.stdout.write("📥 Import données test...")
        
        created_count = 0
        error_count = 0
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for i, row in enumerate(reader, start=1):
                try:
                    with transaction.atomic():
                        # 1. Calculer birth_date depuis age
                        age = int(row.get('age', 30))
                        birth_date = datetime.now().date() - timedelta(days=age*365)
                        
                        # 2. Générer NIP unique
                        nip = f"NIP{i:06d}"
                        
                        # 3. Créer PersonIdentity (TOUS LES CHAMPS VALIDES)
                        person = PersonIdentity.objects.create(
                            first_name=row.get('first_name', 'Unknown').strip(),
                            last_name=row.get('last_name', 'Unknown').strip(),
                            birth_date=birth_date,
                            gender=row.get('gender', 'M').strip(),
                            province=row.get('province', 'ESTUAIRE').strip(),
                            phone_number=f"+241{77000000 + i}",
                            nip=nip,
                            
                            # Champs additionnels existants
                            education_level=row.get('education_level', 'NONE'),
                            has_disability=(row.get('has_disability', '0') == '1'),
                            is_household_head=True,  # CORRECT: is_household_head
                            monthly_income=Decimal(row.get('monthly_income', '0')),
                            
                            # Compléter l'adresse basique
                            address=f"{row.get('province', 'ESTUAIRE')}, Gabon"
                        )
                        
                        # 4. Créer Household
                        household_size = int(row.get('household_size', 1))
                        children_count = int(row.get('children_count', 0))
                        monthly_income = row.get('monthly_income', '0')
                        
                        household_data = {
                            'head_of_household': person,  # CORRECTION: instance au lieu de string
                            'head_person': person,
                            'household_type': 'NUCLEAR' if household_size <= 5 else 'EXTENDED',
                            'household_size': household_size,
                            
                            # MAPPING REVENU
                            'total_monthly_income': Decimal(monthly_income),
                            
                            # MAPPING ENFANTS
                            'members_under_15': children_count,
                            'has_children_under_5': children_count > 0,
                            
                            # Distribution membres par âge (estimation)
                            'members_15_64': max(1, household_size - children_count - 1),
                            'members_over_64': 1 if household_size > 5 else 0,
                            
                            # Logement (valeurs par défaut raisonnables)
                            'housing_type': 'OWNED' if int(monthly_income) > 200000 else 'RENTED',
                            'number_of_rooms': min(household_size, 5),
                            'water_access': 'PIPED' if row.get('province') in ['ESTUAIRE', 'HAUT_OGOOUE'] else 'WELL',
                            'electricity_access': 'GRID' if int(monthly_income) > 100000 else 'NO',
                            'has_toilet': int(monthly_income) > 100000,
                            'has_bank_account': int(monthly_income) > 200000,
                            
                            'province': row.get('province', 'ESTUAIRE').strip(),
                            
                            # SOURCE REVENU dans assets
                            'assets': json.dumps({
                                'primary_income_source': row.get('primary_income_source', 'UNKNOWN')
                            }),
                            
                            # Indicateurs vulnérabilité
                            'has_disabled_members': (row.get('has_disability', '0') == '1'),
                        }
                        
                        household = Household.objects.create(**household_data)
                        
                        # 5. Lier person au household
                        person.household = household
                        person.save()
                        
                        created_count += 1
                        
                        if created_count % 20 == 0:
                            self.stdout.write(f"  ✅ {created_count} enregistrements créés...")
                
                except Exception as e:
                    error_count += 1
                    self.stdout.write(
                        self.style.ERROR(f"❌ Erreur ligne {i}: {str(e)}")
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Import terminé: {created_count} créés, {error_count} erreurs"
            )
        )
        
        # Afficher statistiques
        if created_count > 0:
            self.stdout.write("\n📊 Statistiques importées:")
            self.stdout.write(f"  • Personnes: {created_count}")
            self.stdout.write(f"  • Ménages: {created_count}")
            
            # Stats par province
            from django.db.models import Count
            stats = PersonIdentity.objects.values('province').annotate(count=Count('id'))
            self.stdout.write("\n📍 Répartition par province:")
            for stat in stats:
                self.stdout.write(f"  • {stat['province']}: {stat['count']} personnes")
# Utilisation:
# python manage.py import_test_data data/test_data_gabon_synthetic.csv