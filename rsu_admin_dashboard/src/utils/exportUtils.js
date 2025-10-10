/**
 * 🇬🇦 RSU Gabon - Export Utilities
 * Fichier: src/utils/exportUtils.js
 */

export const BENEFICIARIES_EXPORT_COLUMNS = [
  { key: 'rsu_id', label: 'RSU ID' },
  { key: 'first_name', label: 'Prénom' },
  { key: 'last_name', label: 'Nom' },
  { key: 'gender', label: 'Genre' },
  { key: 'birth_date', label: 'Date naissance' },
  { key: 'phone_number', label: 'Téléphone' },
  { key: 'province', label: 'Province' },
  { key: 'vulnerability_score', label: 'Score vulnérabilité' },
];

export function formatBeneficiariesForExport(beneficiaries, columns = BENEFICIARIES_EXPORT_COLUMNS) {
  return beneficiaries.map(b => {
    const row = {};
    columns.forEach(col => {
      let value = b[col.key];
      if (col.key === 'birth_date' && value) {
        value = new Date(value).toLocaleDateString('fr-FR');
      }
      row[col.label] = value || '';
    });
    return row;
  });
}

function arrayToCSV(data) {
  if (!data || data.length === 0) return '';
  const headers = Object.keys(data[0]);
  const rows = [headers.join(',')];
  data.forEach(row => {
    const values = headers.map(h => `"${String(row[h]).replace(/"/g, '""')}"`);
    rows.push(values.join(','));
  });
  return rows.join('\n');
}

export function downloadCSV(data, filename = 'export.csv', columns = BENEFICIARIES_EXPORT_COLUMNS) {
  const formatted = formatBeneficiariesForExport(data, columns);
  const csv = arrayToCSV(formatted);
  const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  link.click();
  console.log('✅ CSV téléchargé:', filename);
}

export function downloadExcel(data, filename = 'export.xlsx', columns = BENEFICIARIES_EXPORT_COLUMNS) {
  const formatted = formatBeneficiariesForExport(data, columns);
  const csv = arrayToCSV(formatted);
  const blob = new Blob(['\uFEFF' + csv], { type: 'application/vnd.ms-excel;charset=utf-8;' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  link.click();
  console.log('✅ Excel téléchargé:', filename);
}

export default {
  downloadCSV,
  downloadExcel,
  formatBeneficiariesForExport,
  BENEFICIARIES_EXPORT_COLUMNS,
};