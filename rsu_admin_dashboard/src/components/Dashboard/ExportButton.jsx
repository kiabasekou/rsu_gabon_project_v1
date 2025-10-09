/**
 * 🇬🇦 RSU Gabon - Bouton Export
 * Standards Top 1% - Export Multiple Formats
 * Fichier: rsu_admin_dashboard/src/components/Dashboard/ExportButton.jsx
 */

import React, { useState } from 'react';
import { Download, FileText, FileSpreadsheet, ChevronDown, Loader } from 'lucide-react';
import { 
  downloadCSV, 
  downloadExcel, 
  formatBeneficiariesForExport,
  BENEFICIARIES_EXPORT_COLUMNS 
} from '../../utils/exportUtils';

export default function ExportButton({ data, filename = 'beneficiaires_rsu', disabled }) {
  const [showMenu, setShowMenu] = useState(false);
  const [exporting, setExporting] = useState(false);

  const handleExport = async (format) => {
    setShowMenu(false);
    setExporting(true);

    try {
      // Simulation délai (pour UX)
      await new Promise(resolve => setTimeout(resolve, 500));

      const formattedData = formatBeneficiariesForExport(data);
      const timestamp = new Date().toISOString().split('T')[0];
      const fullFilename = `${filename}_${timestamp}`;

      if (format === 'csv') {
        downloadCSV(formattedData, `${fullFilename}.csv`, BENEFICIARIES_EXPORT_COLUMNS);
      } else if (format === 'excel') {
        downloadExcel(formattedData, `${fullFilename}.xlsx`, BENEFICIARIES_EXPORT_COLUMNS);
      }

      console.log(`✅ Export ${format.toUpperCase()} réussi: ${data.length} enregistrements`);
    } catch (error) {
      console.error('❌ Erreur export:', error);
      alert('Erreur lors de l\'export. Veuillez réessayer.');
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="relative">
      <button
        onClick={() => setShowMenu(!showMenu)}
        disabled={disabled || exporting || data.length === 0}
        className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-colors"
        title={data.length === 0 ? 'Aucune donnée à exporter' : 'Exporter les données'}
      >
        {exporting ? (
          <>
            <Loader className="animate-spin" size={18} />
            <span className="hidden sm:inline">Export...</span>
          </>
        ) : (
          <>
            <Download size={18} />
            <span className="hidden sm:inline">Exporter</span>
            <ChevronDown size={16} />
          </>
        )}
      </button>

      {/* Menu dropdown */}
      {showMenu && !exporting && (
        <>
          {/* Overlay pour fermer le menu */}
          <div 
            className="fixed inset-0 z-10" 
            onClick={() => setShowMenu(false)}
          />

          {/* Menu */}
          <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 z-20 overflow-hidden">
            <div className="px-4 py-3 bg-gray-50 border-b border-gray-200">
              <p className="text-sm font-semibold text-gray-700">
                Exporter {data.length} enregistrement{data.length > 1 ? 's' : ''}
              </p>
            </div>

            {/* Option CSV */}
            <button
              onClick={() => handleExport('csv')}
              className="w-full px-4 py-3 flex items-center gap-3 hover:bg-gray-50 transition-colors text-left"
            >
              <FileText size={20} className="text-blue-600" />
              <div>
                <p className="font-medium text-gray-800">Format CSV</p>
                <p className="text-xs text-gray-500">
                  Compatible Excel, Google Sheets
                </p>
              </div>
            </button>

            {/* Option Excel */}
            <button
              onClick={() => handleExport('excel')}
              className="w-full px-4 py-3 flex items-center gap-3 hover:bg-gray-50 transition-colors text-left border-t border-gray-100"
            >
              <FileSpreadsheet size={20} className="text-green-600" />
              <div>
                <p className="font-medium text-gray-800">Format Excel</p>
                <p className="text-xs text-gray-500">
                  Fichier .xlsx natif
                </p>
              </div>
            </button>

            {/* Info */}
            <div className="px-4 py-3 bg-blue-50 border-t border-gray-200">
              <p className="text-xs text-blue-800">
                💡 Les données sont filtrées selon vos critères de recherche
              </p>
            </div>
          </div>
        </>
      )}
    </div>
  );
}