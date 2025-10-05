// components/enrollment/PhotoCapture.jsx
import React, { useState, useRef } from 'react';
import { Camera } from 'lucide-react';

export default function PhotoCapture({ onCapture, documentType }) {
  const [preview, setPreview] = useState(null);
  const [capturing, setCapturing] = useState(false);
  const fileInputRef = useRef(null);

  const handleCapture = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validation
    if (!file.type.startsWith('image/')) {
      alert('Fichier doit être une image');
      return;
    }

    if (file.size > 5 * 1024 * 1024) { // 5MB max
      alert('Image trop volumineuse (max 5MB)');
      return;
    }

    // Preview
    const reader = new FileReader();
    reader.onload = (e) => {
      setPreview(e.target.result);
      
      // Callback avec données
      onCapture({
        file,
        preview: e.target.result,
        documentType,
        timestamp: new Date().toISOString()
      });
    };
    reader.readAsDataURL(file);
  };

  const handleRetake = () => {
    setPreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-4 border-2 border-dashed border-gray-300">
      <div className="text-center">
        <p className="font-semibold text-gray-700 mb-2">{documentType}</p>
        
        {!preview ? (
          <>
            <div className="mb-4">
              <Camera size={48} className="mx-auto text-gray-400 mb-2" />
              <p className="text-sm text-gray-500">Cliquez pour capturer</p>
            </div>
            
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              capture="environment"
              onChange={handleCapture}
              className="hidden