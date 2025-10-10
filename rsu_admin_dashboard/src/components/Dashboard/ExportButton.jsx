/**
 * 🇬🇦 RSU Gabon - Export Button
 * Standards Top 1% - Export CSV/Excel avec imports corrigés
 * Fichier: src/components/Dashboard/ExportButton.jsx
 */

import React, { useState } from 'react';
import { Download, FileText, Table } from 'lucide-react';
import { 
  downloadCSV, 
  downloadExcel, 
  formatBeneficiariesForExport,
  BENEFICIARIES_EXPORT_COLUMNS 
} from '../../utils/exportUtils';

export default function ExportButton({ 
  data = [], 
  filename = 'export', 
  disabled = false,
  type = 'beneficiaries' // 'beneficiaries' ou 'programs'
}) {
  const [showMenu, setShowMenu] = useState(false);
  const [exporting, setExporting] = useState(false);

  const handleExport = async (format) => {
    if (!data || data.length === 0) {
      alert('Aucune donnée à exporter');
      return;
    }

    setExporting(true);
    setShowMenu(false);

    try {
      const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
      const finalFilename = `${filename}_${timestamp}.${format === 'excel' ? 'xlsx' : 'csv'}`;

      if (format === 'csv') {
        downloadCSV(data, finalFilename, BENEFICIARIES_EXPORT_COLUMNS);
      } else {
        downloadExcel(data, finalFilename, BENEFICIARIES_EXPORT_COLUMNS);
      }

      console.log(`✅ Export ${format.toUpperCase()} réussi: ${data.length} lignes`);
    } catch (error) {
      console.error('❌ Erreur export:', error);
      alert('Erreur lors de l\'export. Vérifiez la console.');
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="relative">
      <button
        onClick={() => setShowMenu(!showMenu)}
        disabled={disabled || exporting}
        className={`
          flex items-center gap-2 px-4 py-2 rounded-lg font-semibold transition-colors
          ${disabled || exporting
            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
            : 'bg-green-600 text-white hover:bg-green-700'
          }
        `}
      >
        <Download size={18} className={exporting ? 'animate-bounce' : ''} />
        {exporting ? 'Export en cours...' : 'Exporter'}
      </button>

      {/* Menu déroulant */}
      {showMenu && !disabled && !exporting && (
        <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
          <button
            onClick={() => handleExport('csv')}
            className="w-full flex items-center gap-3 px-4 py-3 hover:bg-gray-50 transition-colors text-left"
          >
            <FileText size={18} className="text-blue-600" />
            <div>
              <div className="font-semibold text-gray-800">CSV</div>
              <div className="text-xs text-gray-500">Format Excel simple</div>
            </div>
          </button>

          <div className="border-t border-gray-200"></div>

          <button
            onClick={() => handleExport('excel')}
            className="w-full flex items-center gap-3 px-4 py-3 hover:bg-gray-50 transition-colors text-left rounded-b-lg"
          >
            <Table size={18} className="text-green-600" />
            <div>
              <div className="font-semibold text-gray-800">Excel</div>
              <div className="text-xs text-gray-500">Format XLSX</div>
            </div>
          </button>
        </div>
      )}

      {/* Overlay pour fermer menu */}
      {showMenu && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setShowMenu(false)}
        />
      )}
    </div>
  );
}