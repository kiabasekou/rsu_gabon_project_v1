/**
 * RSU Gabon - Protected Route
 * Avec validation JWT simplifiée
 */

import React, { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';

export default function ProtectedRoute({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(null); // null = loading
  
  useEffect(() => {
    validateAuth();
  }, []);

  const validateAuth = async () => {
    try {
      // Vérifier présence token
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        console.log('⚠️ No token found');
        setIsAuthenticated(false);
        return;
      }

      // Token présent = authentifié
      // (Validation complète peut être ajoutée plus tard)
      console.log('✅ Token found, user authenticated');
      setIsAuthenticated(true);
      
    } catch (error) {
      console.error('Token validation failed:', error);
      setIsAuthenticated(false);
    }
  };

  // Loading
  if (isAuthenticated === null) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Vérification...</p>
        </div>
      </div>
    );
  }

  // Not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Authenticated
  return children;
}