
@echo off
REM 🇬🇦 RSU Gabon - Script de démarrage développement Windows
REM Fichier: start_development.bat

echo 🇬🇦 RSU GABON - Demarrage environnement developpement
echo ==================================================

REM Demarrage Backend
echo [1/2] Demarrage Backend Django...
cd rsu_identity_backend
call venv\Scripts\activate
python manage.py migrate --no-input
echo ✅ Migrations appliquees

start "RSU Backend" python manage.py runserver
timeout /t 5

REM Demarrage Frontend
echo [2/2] Demarrage Frontend React...
cd ..\rsu_admin_dashboard
start "RSU Frontend" npm start

echo.
echo ==================================================
echo ✅ Environnement demarre avec succes !
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/api/docs/
echo ==================================================
pause