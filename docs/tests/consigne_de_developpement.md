
Voici le résumé des erreurs et les consignes de développement correspondantes pour garantir la qualité et la robustesse de votre code.

---

## 📝 Résumé des Erreurs et Consignes de Développement

Les erreurs rencontrées se concentrent sur deux problèmes principaux : **le décalage entre le code et les modèles (nommage)** et **le non-respect des règles d'intégrité de la base de données et des retours de fonctions (typologie)**.

### 1. Synthèse des Erreurs Clés

| Catégorie de Problème | Description Détaillée | Conséquence Majeure |
| :--- | :--- | :--- |
| **Incohérence de Nommage** | Mots-clés incorrects dans les tests par rapport aux modèles (ex: `date_of_birth` vs `birth_date`, `global_score` vs `vulnerability_score`). | Nombreuses `AttributeError` et `TypeError` dans tous les fichiers testés. |
| **Intégrité des Données** | Non-respect des contraintes `NOT NULL` (ex: `head_of_household_id` manquant) et dépendances circulaires. | Blocage complet de la création des objets de test (`IntegrityError`). |
| **Typage et ORM** | Erreur d'accès aux résultats (traiter une instance d'objet Django comme un dictionnaire) et syntaxe ORM incorrecte (agrégations). | Erreurs silencieuses ou plantages de l'application lors de l'accès aux données de service. |
| **Synchronisation Modèles/Services** | Champs cruciaux pour les services (`vulnerability_score`, `risk_level`) non définis ou non migrés sur les modèles avant l'exécution des tests. | `ValueError` lors de l'accès à des champs censés exister. |

---

## 🚀 Consignes de Développement pour la Prévention

Pour éviter que les erreurs ne se reproduisent, l'équipe doit adopter des pratiques standard de développement logiciel qui renforcent la **cohérence** et la **prévisibilité** du code.

### Consigne 1 : Définir et Suivre des Standards de Nommage Strict (The Single Source of Truth)

**Problème résolu :** Erreurs 1.1, 1.2, 1.3.

* **Règle :** Établissez une **"Source Unique de Vérité" (SSOT)** pour les noms de champs. Le modèle Django est la SSOT.
* **Action :** Pour tout nouveau service ou test qui dépend d'un modèle, faites un **copier-coller du nom exact du champ** (ex: `vulnerability_score`) au lieu de le taper de mémoire.
* **Recommandation Technique :** Si possible, utilisez des outils de **linter** (comme Pylint ou Flake8) et des **type checkers** (comme Mypy) qui peuvent détecter les incohérences de nommage avant l'exécution des tests.

### Consigne 2 : Utiliser la Création en Deux Phases pour les Dépendances (Breaking the Cycle)

**Problème résolu :** Erreur 2.1 (Dépendance circulaire).

* **Règle :** Pour toutes les relations `ForeignKey` qui créent des dépendances mutuelles (A a besoin de B, B a besoin de A), ne créez jamais les deux objets en même temps.
* **Action :**
    1.  Créez l'objet **enfant** ou l'objet **cible** (ex: `PersonIdentity`) avec le strict minimum.
    2.  Créez l'objet **parent** ou l'objet **source** (ex: `Household`) en pointant vers l'objet créé en (1).
    3.  Mettez à jour l'objet (1) pour pointer vers l'objet (2) et **sauvegardez-le (`.save()`)**.
    * `person = PersonIdentity.objects.create(...)`
    * `household = Household.objects.create(head_of_household=person, ...)`
    * `person.household = household; person.save()`

### Consigne 3 : Typage Stricte des Retours et Accès aux Données

**Problème résolu :** Erreur 3.1 (Accès dict vs objet).

* **Règle :** Documentez et respectez le type de retour des méthodes de service.
* **Action :**
    * Si une méthode de service retourne une **instance de modèle** (standard Django), utilisez l'accès par attribut : **`result.field_name`** et vérifiez l'existence avec **`hasattr(result, 'field_name')`**.
    * Si elle retourne un `dict` ou une `list` Python, utilisez l'accès par clé : **`result['key_name']`**.
* **Recommandation Technique :** Utilisez les **annotations de type Python** (`from typing import Dict, List, Optional`) dans la signature de vos méthodes de service pour clarifier le type de retour attendu.

### Consigne 4 : Intégrer les Migrations au Cycle de Développement (Testing Data Schema First)

**Problème résolu :** Erreur 2.2 (Champs manquants sur `PersonIdentity`).

* **Règle :** Le schéma de données requis par un service doit exister **avant** que le service ne soit testé.
* **Action :**
    * Dès qu'un nouveau service nécessite un champ persistant (`vulnerability_score`, `risk_level`), la **migration doit être la première étape** de la tâche.
    * Vérifiez que toutes les migrations sont appliquées sur la base de données de test **avant** d'écrire la logique de création de vos objets de test.

En appliquant ces quatre consignes, vous transformerez les leçons tirées de ces erreurs en une **"Checklist Qualité"** robuste pour vos futures phases de développement.