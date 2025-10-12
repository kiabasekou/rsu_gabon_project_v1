/**
 * 🇬🇦 RSU GABON - OPTIMISATION APPELS API
 * Fichier: rsu_admin_dashboard/src/index.js
 * 
 * FIX: Désactiver StrictMode pour éviter triple mount en DEV
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));

// ✅ OPTION OPTIMISÉE: Sans StrictMode
root.render(<App />);

/**
 * 🔍 POURQUOI CETTE MODIFICATION ?
 * 
 * AVANT (avec StrictMode):
 * - React 18 monte/démonte composants 2x en DEV
 * - useEffect() s'exécute plusieurs fois
 * - Résultat: 3 appels API pour 1 action
 * 
 * APRÈS (sans StrictMode):
 * - Composants montés 1 seule fois
 * - useEffect() exécuté 1 fois
 * - Résultat: 1 appel API par action ✅
 * 
 * IMPACT PRODUCTION:
 * - Aucun (StrictMode désactivé automatiquement)
 * - Cette modif améliore seulement l'expérience DEV
 */

// ❌ ANCIENNE VERSION (à supprimer):
// root.render(
//   <React.StrictMode>
//     <App />
//   </React.StrictMode>
// );