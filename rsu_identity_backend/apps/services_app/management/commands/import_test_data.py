# ===================================================================
# Management Command - Import Données Test
# ===================================================================

from django.core.management.base import BaseCommand
from django.db import transaction
import csv
from decimal import Decimal
from apps.identity_app.models import PersonIdentity, Household


class Command(BaseCommand):
    help = 'Importe données test depuis CSV'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Chemin vers fichier CSV'
        )
    
    def handle(self, *args, **options):
        csv_file = options['csv_file']
        
        self.stdout.write("📥 Import données test...")
        
        created_count = 0
        error_count = 0
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                try:
                    with transaction.atomic():
                        # Créer ménage
                        household = Household.objects.create(
                            household_size=int(row['household_size']),
                            children_count=int(row['children_count']),
                            monthly_income=Decimal(row['monthly_income']),
                            primary_income_source=row['primary_income_source']
                        )
                        
                        # Créer personne
                        person = PersonIdentity.objects.create(
                            first_name=row['first_name'],
                            last_name=row['last_name'],
                            age=int(row['age']),
                            gender=row['gender'],
                            province=row['province'],
                            education_level=row['education_level'],
                            has_disability=bool(int(row['has_disability'])),
                            household=household
                        )
                        
                        created_count += 1
                        
                except Exception as e:
                    error_count += 1
                    self.stdout.write(
                        self.style.ERROR(f"❌ Erreur ligne {created_count + error_count}: {e}")
                    )
        
        self.stdout.write(
            self.style.SUCCESS(f"\n✅ Import terminé: {created_count} créés, {error_count} erreurs")
        )


# Utilisation:
# python manage.py import_test_data data/test_data_gabon_synthetic.csv