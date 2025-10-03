# 🇬🇦 RSU GABON - Guidelines JSONField Filtering

## 🎯 Problème Rencontré

**Date**: 03 Octobre 2025  
**Erreur**: `AssertionError: AutoFilterSet resolved field 'assigned_provinces' with 'exact' lookup to an unrecognized field type JSONField`

**Contexte**: Tests API REST échouaient sur les endpoints Core App (`/api/v1/core/users/`)

---

## 🔍 Analyse Technique

### Cause Racine

```python
# ❌ CODE PROBLÉMATIQUE
class RSUUserViewSet(viewsets.ModelViewSet):
    filterset_fields = ['user_type', 'department', 'is_active', 'assigned_provinces']
    #                                                            ^^^^^^^^^^^^^^^^^^
    #                                                            JSONField → Erreur
```

**Explication**:
- `assigned_provinces` est un `JSONField` dans le modèle `RSUUser`
- `django-filter` génère automatiquement des filters pour `filterset_fields`
- Il n'existe pas de filter par défaut pour `JSONField` → `AssertionError`

### Impact

- ❌ Tous les tests API échouent sur `/api/v1/core/users/`
- ❌ Les endpoints `list` et `retrieve` sont inaccessibles
- ❌ Blocage complet du développement et des tests

---

## ✅ Solution Implémentée

### Étape 1 : Création du FilterSet Custom

**Fichier**: `apps/core_app/filters.py`

```python
import django_filters
from django.db.models import JSONField
from .models import RSUUser

class RSUUserFilter(django_filters.FilterSet):
    """FilterSet avec exclusion explicite des JSONFields"""
    
    user_type = django_filters.ChoiceFilter(choices=[...])
    department = django_filters.CharFilter(lookup_expr='icontains')
    is_active = django_filters.BooleanFilter()
    
    class Meta:
        model = RSUUser
        fields = {
            'user_type': ['exact'],
            'department': ['exact', 'icontains'],
            'is_active': ['exact'],
            'employee_id': ['exact', 'icontains'],
            # assigned_provinces EXCLU
        }
```

### Étape 2 : Modification du ViewSet

**Fichier**: `apps/core_app/views/user_views.py`

```python
from apps.core_app.filters import RSUUserFilter

class RSUUserViewSet(viewsets.ModelViewSet):
    # ❌ AVANT
    # filterset_fields = ['user_type', 'department', 'is_active', 'assigned_provinces']
    
    # ✅ APRÈS
    filterset_class = RSUUserFilter
```

---

## 📜 Règles de Prévention (Standards Top 1%)

### ⚠️ Règle #1 : Ne JAMAIS Inclure JSONField dans `filterset_fields`

```python
# ❌ INTERDIT
class MyViewSet(viewsets.ModelViewSet):
    filterset_fields = ['name', 'json_data']  # json_data est JSONField → Erreur
```

```python
# ✅ CORRECT
class MyViewSet(viewsets.ModelViewSet):
    filterset_class = MyCustomFilter  # Filter explicite sans JSONField
```

### ⚠️ Règle #2 : Toujours Créer un FilterSet pour Modèles avec Champs Complexes

**Champs complexes concernés**:
- `JSONField`
- `ArrayField` (PostgreSQL)
- `HStoreField` (PostgreSQL)
- Champs custom avec validators complexes

### ⚠️ Règle #3 : Documenter l'Exclusion des Champs Non-Filtrables

```python
class MyFilter(django_filters.FilterSet):
    class Meta:
        model = MyModel
        fields = ['field1', 'field2']
        # NOTE: json_data exclu car JSONField non filtrable par défaut
```

---

## 🔮 Filtrage Avancé JSONField (Optionnel)

Si le filtrage sur JSONField est **vraiment nécessaire**, implémenter un filter custom :

### Pour PostgreSQL (Recommandé)

```python
class RSUUserFilter(django_filters.FilterSet):
    assigned_provinces = django_filters.CharFilter(
        method='filter_assigned_provinces',
        help_text="Filtrer par province assignée"
    )
    
    def filter_assigned_provinces(self, queryset, name, value):
        """Filtrage dans tableau JSON avec PostgreSQL"""
        return queryset.filter(assigned_provinces__contains=[value])
    
    class Meta:
        model = RSUUser
        fields = ['user_type', 'department', 'is_active']
```

### Pour MySQL/SQLite (Moins performant)

```python
def filter_assigned_provinces(self, queryset, name, value):
    """Filtrage avec recherche textuelle dans JSON"""
    import json
    ids = []
    for user in queryset:
        if value in (user.assigned_provinces or []):
            ids.append(user.id)
    return queryset.filter(id__in=ids)
```

⚠️ **Attention**: Cette approche charge TOUTES les données en mémoire → Non scalable

---

## 🧪 Tests de Validation

### Test 1 : Vérifier Absence d'Erreur

```bash
python test_real_api_endpoints.py
```

**Résultat attendu**: 
- ✅ Test 5 (Liste utilisateurs) : `200 OK`
- ✅ Test 6 (Détails utilisateur) : `200 OK`

### Test 2 : Vérifier Filtrage Fonctionnel

```bash
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/v1/core/users/?user_type=ADMIN"
```

**Résultat attendu**: Liste filtrée des admins

---

## 🎓 Leçons Apprises

### Conformité aux Consignes Projet

| Consigne | Application |
|----------|-------------|
| **#1 : SSOT** | Noms de champs copiés exactement du modèle |
| **#3 : Typage Strict** | Respect des limitations du type JSONField |
| **#4 : Schema First** | Filter créé AVANT tests pour éviter erreurs |

### Principe Général

> **"Explicit is better than implicit"** (PEP 20)
> 
> Pour les types de données complexes, toujours définir explicitement
> le comportement attendu au lieu de compter sur l'auto-génération.

---

## 📚 Références

- [Django Filter Documentation](https://django-filter.readthedocs.io/)
- [Django JSONField](https://docs.djangoproject.com/en/4.2/ref/models/fields/#jsonfield)
- [PostgreSQL JSON Operations](https://www.postgresql.org/docs/current/functions-json.html)

---

**Auteur**: Équipe Développement RSU Gabon  
**Version**: 1.0  
**Date**: 03 Octobre 2025