# 🇬🇦 RSU Gabon - Commandes Automatisées

.PHONY: help setup backend-dev mobile-dev test deploy

help: ## Affiche cette aide
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

setup: ## Installation complète environnement
	@echo "🚀 Installation environnement RSU Gabon..."
	docker-compose up -d postgres redis
	cd rsu_identity_backend && pip install -r requirements.txt
	cd rsu_mobile_app && npm install

backend-dev: ## Démarre backend développement
	@echo "🔧 Démarrage backend Django..."
	cd rsu_identity_backend && python manage.py runserver

mobile-dev: ## Démarre app mobile développement  
	@echo "📱 Démarrage app mobile..."
	cd rsu_mobile_app && expo start

test: ## Lance tous les tests
	@echo "🧪 Exécution tests..."
	cd rsu_identity_backend && python manage.py test
	cd rsu_mobile_app && npm test

deploy-staging: ## Déploiement staging
	@echo "🚢 Déploiement staging..."
	./scripts/deployment/deploy-staging.sh

deploy-production: ## Déploiement production
	@echo "🚀 Déploiement production..."
	./scripts/deployment/deploy-production.sh
