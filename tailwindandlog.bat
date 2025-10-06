@echo off
REM Fix Tailwind + Authentification React
REM RSU Gabon - Correction urgente

echo ========================================
echo CORRECTION 1: Tailwind Dependencies
echo ========================================
cd rsu_admin_dashboard

REM Supprimer node_modules et package-lock
rd /s /q node_modules 2>nul
del package-lock.json 2>nul

REM Installer versions compatibles Tailwind
npm install -D tailwindcss@3.4.1 postcss@8.4.31 autoprefixer@10.4.16
npm install -D @alloc/quick-lru

REM Reinstaller dependances projet
npm install

echo.
echo ========================================
echo CORRECTION 2: Authentification JWT
echo ========================================

REM Creer fichier correction apiClient
(
echo /**
echo  * FIX: apiClient.js - Correction Authorization header
echo  * Fichier: rsu_admin_dashboard/src/services/api/apiClient.js
echo  */
echo.
echo const API_BASE_URL = process.env.REACT_APP_API_URL ^|^| 'http://localhost:8000/api/v1';
echo.
echo class APIClient {
echo   constructor^(^) {
echo     this.baseURL = API_BASE_URL;
echo   }
echo.
echo   async request^(endpoint, options = {}^) {
echo     const token = localStorage.getItem^('access_token'^);
echo.    
echo     const config = {
echo       ...options,
echo       headers: {
echo         'Content-Type': 'application/json',
echo         ..^(token ^&^& { 'Authorization': `Bearer ${token}` }^),
echo         ...options.headers,
echo       },
echo     };
echo.
echo     const response = await fetch^(`${this.baseURL}${endpoint}`, config^);
echo     
echo     if ^(response.status === 401^) {
echo       console.error^('401 Unauthorized - Token:', token ? 'EXISTS' : 'MISSING'^);
echo       window.location.href = '/login';
echo       throw new Error^('Unauthorized'^);
echo     }
echo.
echo     if ^(!response.ok^) throw new Error^(`HTTP ${response.status}`^);
echo     return await response.json^(^);
echo   }
echo.
echo   get^(endpoint, params = {}^) {
echo     const query = new URLSearchParams^(params^).toString^(^);
echo     return this.request^(`${endpoint}${query ? `?${query}` : ''}`^);
echo   }
echo }
echo.
echo export default new APIClient^(^);
) > src\services\api\apiClient_fixed.js

echo apiClient_fixed.js cree - Remplacer manuellement apiClient.js

echo.
echo ========================================
echo CORRECTION 3: Page Login Temporaire
echo ========================================

REM Creer composant Login simple
mkdir src\pages 2>nul
(
echo import React, { useState } from 'react';
echo.
echo export default function Login^(^) {
echo   const [username, setUsername] = useState^('admin'^);
echo   const [password, setPassword] = useState^(''^);
echo.
echo   const handleLogin = async ^(e^) =^> {
echo     e.preventDefault^(^);
echo     const response = await fetch^('http://localhost:8000/api/v1/auth/token/', {
echo       method: 'POST',
echo       headers: { 'Content-Type': 'application/json' },
echo       body: JSON.stringify^({ username, password }^)
echo     }^);
echo     
echo     if ^(response.ok^) {
echo       const data = await response.json^(^);
echo       localStorage.setItem^('access_token', data.access^);
echo       localStorage.setItem^('refresh_token', data.refresh^);
echo       window.location.href = '/';
echo     }
echo   };
echo.
echo   return ^(
echo     ^<div style={{ padding: '50px', maxWidth: '400px', margin: 'auto' }}^>
echo       ^<h2^>RSU Gabon - Login^</h2^>
echo       ^<form onSubmit={handleLogin}^>
echo         ^<input 
echo           value={username} 
echo           onChange={e =^> setUsername^(e.target.value^)}
echo           placeholder="Username"
echo           style={{ display: 'block', width: '100%%', margin: '10px 0', padding: '10px' }}
echo         /^>
echo         ^<input 
echo           type="password"
echo           value={password} 
echo           onChange={e =^> setPassword^(e.target.value^)}
echo           placeholder="Password"
echo           style={{ display: 'block', width: '100%%', margin: '10px 0', padding: '10px' }}
echo         /^>
echo         ^<button type="submit" style={{ padding: '10px 20px' }}^>Login^</button^>
echo       ^</form^>
echo     ^</div^>
echo   ^);
echo }
) > src\pages\Login.jsx

echo Login.jsx cree

echo.
echo ========================================
echo INSTRUCTIONS MANUELLES
echo ========================================
echo.
echo 1. REMPLACER src/services/api/apiClient.js par apiClient_fixed.js
echo.
echo 2. MODIFIER src/App.js pour ajouter route login:
echo    import Login from './pages/Login';
echo    // Si pas de token, afficher Login
echo.
echo 3. TESTER:
echo    - Ouvrir http://localhost:3000
echo    - Login: admin / admin123
echo    - Token stocke dans localStorage
echo.
echo 4. DEMARRER:
echo    npm start
echo.
pause