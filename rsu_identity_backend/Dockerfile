# =============================================================================
# 🇬🇦 RSU GABON - Dockerfile Production Optimisé
# Standards Top 1% - Multi-stage Build
# =============================================================================

FROM python:3.11-slim as base

# Variables d'environnement pour éviter les warnings Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# =============================================================================
# STAGE 1: Dependencies
# =============================================================================
FROM base as dependencies

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# =============================================================================
# STAGE 2: Application
# =============================================================================
FROM base as application

# Copier les dépendances Python depuis le stage précédent
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Installation PostgreSQL client uniquement (sans build tools)
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copier le code de l'application
COPY . .

# =============================================================================
# Configuration PRODUCTION pour collectstatic
# =============================================================================
# ✅ Utiliser ARG pour passer SECRET_KEY au build (sera écrasée au runtime)
ARG SECRET_KEY=dummy-build-secret-key-will-be-replaced-at-runtime

# ✅ Définir explicitement DJANGO_SETTINGS_MODULE pour collectstatic
ENV DJANGO_SETTINGS_MODULE=rsu_identity.settings.production \
    SECRET_KEY=${SECRET_KEY}

# Collecte des fichiers statiques avec les bons settings
RUN python manage.py collectstatic --noinput --verbosity 2

# ⚠️ Nettoyer la variable après collectstatic (sécurité)
ENV SECRET_KEY=""

# Création des répertoires nécessaires
RUN mkdir -p /var/log/rsu /app/media

# =============================================================================
# Sécurité : Utilisateur non-root
# =============================================================================
RUN useradd --create-home --shell /bin/bash rsu && \
    chown -R rsu:rsu /app /var/log/rsu

USER rsu

# =============================================================================
# Configuration Runtime
# =============================================================================
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health/', timeout=5)" || exit 1

# Commande de démarrage avec gunicorn optimisé
CMD ["gunicorn", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "--threads", "2", \
     "--worker-class", "sync", \
     "--worker-tmp-dir", "/dev/shm", \
     "--timeout", "120", \
     "--graceful-timeout", "30", \
     "--keep-alive", "5", \
     "--log-level", "info", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "rsu_identity.wsgi:application"]