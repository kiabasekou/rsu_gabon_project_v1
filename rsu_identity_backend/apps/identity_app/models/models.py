# Identity App - Modèle principal
cat > apps/identity_app/models.py << 'EOF'
"""
🇬🇦 RSU Gabon - Modèles Identité
Modèles pour la gestion des identités et RSU-ID
"""
from django.db import models
from django.core.validators import RegexValidator
import uuid

class PersonIdentity(models.Model):
    """Identité principale d'une personne dans le RSU"""
    GENDER_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
        ('O', 'Autre'),
    ]
    
    VERIFICATION_STATUS = [
        ('PENDING', 'En Attente'),
        ('VERIFIED', 'Vérifié'),
        ('REJECTED', 'Rejeté'),
    ]
    
    # Identifiants
    rsu_id = models.CharField(max_length=50, primary_key=True)
    nip = models.CharField(max_length=13, unique=True, null=True, blank=True)
    national_id = models.CharField(max_length=50, null=True, blank=True)
    
    # Informations personnelles
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    
    # Contact
    phone_validator = RegexValidator(regex=r'^\+241[0-9]{8}$', message="Format: +241XXXXXXXX")
    phone_number = models.CharField(validators=[phone_validator], max_length=13, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    
    # Localisation
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    province = models.CharField(max_length=50, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    
    # Validation
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='PENDING')
    rbpp_synchronized = models.BooleanField(default=False)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.rsu_id:
            self.rsu_id = f"RSU-GA-{str(uuid.uuid4())[:8].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.rsu_id})"
    
    class Meta:
        verbose_name = "Identité Personne"
        verbose_name_plural = "Identités Personnes"