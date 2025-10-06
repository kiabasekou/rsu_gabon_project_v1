## 5️⃣ SCRIPT DE DÉMARRAGE RAPIDE

### 📁 `start_development.sh` (Linux/Mac)
```bash
#!/bin/bash
# 🇬🇦 RSU Gabon - Script de démarrage développement
# Fichier: start_development.sh

echo "🇬🇦 RSU GABON - Démarrage environnement développement"
echo "=================================================="

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Démarrage Backend
echo -e "${BLUE}1. Démarrage Backend Django...${NC}"
cd rsu_identity_backend
source venv/bin/activate
python manage.py migrate --no-input
echo -e "${GREEN}✅ Migrations appliquées${NC}"

# Démarrage serveur en arrière-plan
python manage.py runserver &
BACKEND_PID=$!
echo -e "${GREEN}✅ Backend Django démarré (PID: $BACKEND_PID)${NC}"

# Attendre que backend soit prêt
sleep 5

# Démarrage Frontend
echo -e "${BLUE}2. Démarrage Frontend React...${NC}"
cd ../rsu_admin_dashboard
npm start &
FRONTEND_PID=$!
echo -e "${GREEN}✅ Frontend React démarré (PID: $FRONTEND_PID)${NC}"

echo ""
echo "=================================================="
echo -e "${GREEN}✅ Environnement démarré avec succès !${NC}"
echo ""
echo "📌 Backend:  http://localhost:8000"
echo "📌 Frontend: http://localhost:3000"
echo "📌 API Docs: http://localhost:8000/api/docs/"
echo ""
echo "Pour arrêter : Ctrl+C puis kill $BACKEND_PID $FRONTEND_PID"
echo "=================================================="

# Attendre Ctrl+C
wait