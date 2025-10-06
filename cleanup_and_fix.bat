@echo off
REM 🇬🇦 RSU Gabon - Correction Endpoint + Nettoyage Repository
REM Fichier: cleanup_and_fix.bat

echo ========================================
echo RSU GABON - CORRECTION URGENTE
echo ========================================
echo.

REM ============================================
REM PARTIE 1: CORRECTION ENDPOINT /api/v1/identity/persons/
REM ============================================
echo [ETAPE 1] Correction endpoint persons...
echo.
echo PROBLEME DETECTE: GET /api/v1/persons/ retourne 404
echo SOLUTION: L'endpoint correct est /api/v1/identity/persons/
echo.
echo Verification URLs configurees:
echo   - /api/v1/core/        [OK]
echo   - /api/v1/identity/    [OK]
echo   - /api/v1/services/    [OK]
echo   - /api/v1/analytics/   [OK]
echo.
echo CORRECTION: Mettre a jour apiClient.js et endpoints.js
pause

REM ============================================
REM PARTIE 2: NETTOYAGE BACKEND
REM ============================================
echo.
echo [ETAPE 2] Nettoyage Backend Django...
cd rsu_identity_backend

REM Cache Python
for /d /r %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc >nul 2>&1
del /s /q *.pyo >nul 2>&1

REM Logs
if exist logs rd /s /q logs
del /q *.log >nul 2>&1

REM Tests cache
if exist .pytest_cache rd /s /q .pytest_cache
if exist htmlcov rd /s /q htmlcov
del /q .coverage >nul 2>&1

REM Base de donnees dev
del /q db.sqlite3 >nul 2>&1
del /q db.sqlite3-journal >nul 2>&1

REM Scripts redondants
del /q run_test.sh >nul 2>&1

REM Dossiers temporaires apps
if exist apps\core_app\__pycache__ rd /s /q apps\core_app\__pycache__
if exist apps\identity_app\__pycache__ rd /s /q apps\identity_app\__pycache__
if exist apps\services_app\__pycache__ rd /s /q apps\services_app\__pycache__
if exist apps\analytics\__pycache__ rd /s /q apps\analytics\__pycache__

REM Documentation redondante
if exist docs\tests rd /s /q docs\tests
if exist docs\technical\CORRECTIONS_IMPORTS_CRITIQUES.md del /q docs\technical\CORRECTIONS_IMPORTS_CRITIQUES.md

echo Backend nettoye: Cache Python, logs, tests, db dev
echo.

REM ============================================
REM PARTIE 3: NETTOYAGE FRONTEND DASHBOARD
REM ============================================
echo [ETAPE 3] Nettoyage Frontend Dashboard...
cd ..\rsu_admin_dashboard

REM Node modules (sera reinstalle)
if exist node_modules rd /s /q node_modules

REM Build artifacts
if exist build rd /s /q build
if exist dist rd /s /q dist

REM Cache
if exist .cache rd /s /q .cache

REM Coverage
if exist coverage rd /s /q coverage

REM Logs
del /q npm-debug.log* >nul 2>&1
del /q yarn-debug.log* >nul 2>&1
del /q yarn-error.log* >nul 2>&1

REM OS files
del /q .DS_Store >nul 2>&1
del /q Thumbs.db >nul 2>&1

REM Fichiers redondants
del /q README.md >nul 2>&1

echo Frontend nettoye: node_modules, build, cache, logs
echo.

REM ============================================
REM PARTIE 4: NETTOYAGE MOBILE (si existe)
REM ============================================
if exist ..\rsu-mobile-surveyor (
    echo [ETAPE 4] Nettoyage Mobile App...
    cd ..\rsu-mobile-surveyor
    
    if exist node_modules rd /s /q node_modules
    if exist .expo rd /s /q .expo
    if exist dist rd /s /q dist
    if exist web-build rd /s /q web-build
    
    del /q npm-debug.log* >nul 2>&1
    del /q yarn-debug.log* >nul 2>&1
    
    echo Mobile nettoye: node_modules, expo cache
    echo.
    cd ..
) else (
    echo [ETAPE 4] Mobile App non trouvee - ignore
    echo.
    cd ..
)

REM ============================================
REM PARTIE 5: NETTOYAGE RACINE
REM ============================================
echo [ETAPE 5] Nettoyage racine projet...

REM Fichiers OS
del /q .DS_Store >nul 2>&1
del /q Thumbs.db >nul 2>&1

REM Dossiers vides ou redondants
if exist certificates rd /s /q certificates >nul 2>&1
if exist secrets rd /s /q secrets >nul 2>&1

echo Racine nettoyee
echo.

REM ============================================
REM PARTIE 6: REINSTALLATION FRONTEND
REM ============================================
echo [ETAPE 6] Reinstallation dependances Frontend...
cd rsu_admin_dashboard
call npm install
echo.

REM ============================================
REM RESUME
REM ============================================
cd ..
echo ========================================
echo NETTOYAGE TERMINE
echo ========================================
echo.
echo FICHIERS SUPPRIMES:
echo   Backend:
echo     - __pycache__/ (tous)
echo     - *.pyc, *.pyo
echo     - logs/, *.log
echo     - .pytest_cache/, htmlcov/, .coverage
echo     - db.sqlite3 (dev)
echo     - run_test.sh
echo     - docs/tests/
echo.
echo   Frontend Dashboard:
echo     - node_modules/ (reinstalle)
echo     - build/, dist/
echo     - cache/, coverage/
echo     - logs npm/yarn
echo     - README.md (redondant)
echo.
echo   Mobile App (si existe):
echo     - node_modules/
echo     - .expo/, dist/
echo.
echo   Racine:
echo     - Fichiers OS (.DS_Store, Thumbs.db)
echo.
echo ========================================
echo PROCHAINE ETAPE: CORRIGER ENDPOINTS
echo ========================================
echo.
echo PROBLEME AUTHENTIFICATION DETECTE:
echo   401 Unauthorized sur /api/v1/analytics/dashboard/
echo   401 Unauthorized sur /api/v1/identity/persons/
echo.
echo CAUSE: Token non envoye correctement depuis React
echo.
echo SOLUTION:
echo   1. Verifier apiClient.js ligne Authorization header
echo   2. Verifier localStorage contient access_token
echo   3. Tester avec token curl (fonctionne en ligne commande)
echo.
echo COMMANDES TEST:
echo   Backend: cd rsu_identity_backend ^& python manage.py runserver
echo   Frontend: cd rsu_admin_dashboard ^& npm start
echo.
echo ========================================
pause