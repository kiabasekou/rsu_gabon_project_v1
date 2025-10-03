# =============================================================================
# FICHIER: apps/identity_app/migrations/0015_fix_employment_index.py
# CORRECTION: Fake la suppression d'index inexistant
# =============================================================================

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('identity_app', '0014_add_phone_number_alt'),
    ]

    operations = [
        # ✅ CORRECTION: Utiliser RunSQL avec noop pour éviter l'erreur
        migrations.RunSQL(
            sql=migrations.RunSQL.noop,  # Ne rien faire
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]


# =============================================================================
# EXPLICATION:
# =============================================================================
"""
PROBLÈME:
---------
Migration 0015 essaie de supprimer l'index 'identity_employm_idx' qui n'existe pas.
Erreur: sqlite3.OperationalError: no such index: identity_employm_idx

CAUSE:
------
La migration 0015 a été générée automatiquement par Django et suppose que
l'index existe, mais il n'a jamais été créé dans les migrations précédentes.

SOLUTION:
---------
Remplacer l'opération RemoveIndex par RunSQL.noop pour que la migration
passe sans erreur. C'est une opération "fake" qui ne fait rien.

ALTERNATIVE SI VOUS VOULEZ SUPPRIMER LA MIGRATION:
---------------------------------------------------
Si cette migration n'est pas encore appliquée en production, vous pouvez
simplement la supprimer:

    rm apps/identity_app/migrations/0015_*.py

Puis régénérer une migration propre si nécessaire.
"""