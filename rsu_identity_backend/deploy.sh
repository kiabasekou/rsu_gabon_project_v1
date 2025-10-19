#!/bin/bash
# =============================================================================
# 🇬🇦 RSU GABON - Script de Déploiement Railway
# =============================================================================

echo "🚀 DÉPLOIEMENT RSU GABON BACKEND SUR RAILWAY"
echo "=============================================="

# =============================================================================
# ÉTAPE 1 : Vérification des fichiers modifiés
# =============================================================================
echo ""
echo "📋 ÉTAPE 1/5 : Vérification des fichiers..."
echo ""

# Liste des fichiers critiques
FILES_TO_CHECK=(
    "rsu_identity_backend/Dockerfile"
    "rsu_identity_backend/rsu_identity/settings/production.py"
    "rsu_identity_backend/rsu_identity/wsgi.py"
    "rsu_identity_backend/rsu_identity/asgi.py"
)

for file in "${FILES_TO_CHECK[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file trouvé"
    else
        echo "❌ $file manquant!"
        exit 1
    fi
done

# =============================================================================
# ÉTAPE 2 : Vérification des variables d'environnement Railway
# =============================================================================
echo ""
echo "📋 ÉTAPE 2/5 : Vérification des variables Railway..."
echo ""

railway variables | grep -E "DJANGO_SETTINGS_MODULE|SECRET_KEY|DEBUG|DATABASE_URL"

echo ""
read -p "Les variables ci-dessus sont-elles correctes? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "⚠️  Veuillez configurer les variables d'environnement:"
    echo ""
    echo "railway variables --set \"DJANGO_SETTINGS_MODULE=rsu_identity.settings.production\""
    echo "railway variables --set \"SECRET_KEY=$(openssl rand -base64 32)\""
    echo "railway variables --set \"DEBUG=False\""
    echo ""
    exit 1
fi

# =============================================================================
# ÉTAPE 3 : Git Commit
# =============================================================================
echo ""
echo "📋 ÉTAPE 3/5 : Commit des modifications..."
echo ""

git add rsu_identity_backend/Dockerfile \
        rsu_identity_backend/rsu_identity/settings/production.py

git commit -m "fix(deployment): Django 5.0 STORAGES + SECRET_KEY build compatibility

- Correction STATICFILES_STORAGE → STORAGES (Django 5.0)
- Gestion SECRET_KEY pour collectstatic pendant build
- Dockerfile multi-stage optimisé
- Configuration production robuste avec fallbacks
- Validation conditionnelle selon contexte (collectstatic vs runtime)
"

echo "✅ Commit créé"

# =============================================================================
# ÉTAPE 4 : Déploiement Railway
# =============================================================================
echo ""
echo "📋 ÉTAPE 4/5 : Déploiement sur Railway..."
echo ""

railway up

# =============================================================================
# ÉTAPE 5 : Surveillance des logs
# =============================================================================
echo ""
echo "📋 ÉTAPE 5/5 : Surveillance du déploiement..."
echo ""
echo "Appuyez sur Ctrl+C pour arrêter la surveillance des logs"
echo ""

sleep 5
railway logs --tail 100

# =============================================================================
# POST-DÉPLOIEMENT
# =============================================================================
echo ""
echo "=============================================="
echo "✅ DÉPLOIEMENT TERMINÉ"
echo "=============================================="
echo ""
echo "📌 Prochaines étapes :"
echo ""
echo "1. Vérifier que le service démarre correctement :"
echo "   railway logs"
echo ""
echo "2. Exécuter les migrations :"
echo "   railway run python manage.py migrate"
echo ""
echo "3. Créer un superutilisateur :"
echo "   railway run python manage.py createsuperuser"
echo ""
echo "4. Tester le healthcheck :"
echo "   curl https://votre-app.railway.app/health/"
echo ""
echo "5. Accéder à l'admin :"
echo "   https://votre-app.railway.app/admin/"
echo ""