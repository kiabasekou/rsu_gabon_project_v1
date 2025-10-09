/**
 * 🇬🇦 RSU Gabon - Utilitaires Export Données
 * Standards Top 1% - Export CSV/Excel
 * Fichier: rsu_admin_dashboard/src/utils/exportUtils.js
 */

/**
 * Convertit tableau d'objets en CSV
 */
export function convertToCSV(data, columns) {
  if (!data || data.length === 0) {
    return '';
  }

  // Headers
  const headers = columns.map(col => col.label).join(',');
  
  // Rows
  const rows = data.map(item => {
    return columns.map(col => {
      let value = item[col.key];
      
      // Gestion valeurs nulles
      if (value === null || value === undefined) {
        value = '';
      }
      
      // Échapper guillemets et virgules
      value = String(value).replace(/"/g, '""');
      
      // Entourer de guillemets si contient virgule ou guillemet
      if (value.includes(',') || value.includes('"') || value.includes('\n')) {
        value = `"${value}"`;
      }
      
      return value;
    }).join(',');
  }).join('\n');
  
  return `${headers}\n${rows}`;
}

/**
 * Télécharge un fichier CSV
 */
export function downloadCSV(data, filename = 'export.csv', columns) {
  const csv = convertToCSV(data, columns);
  const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' }); // UTF-8 BOM
  const link = document.createElement('a');
  
  if (link.download !== undefined) {
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
}

/**
 * Télécharge Excel (format TSV compatible Excel)
 */
export function downloadExcel(data, filename = 'export.xlsx', columns) {
  // Pour Excel, on utilise des tabulations au lieu de virgules
  if (!data || data.length === 0) {
    return;
  }

  const headers = columns.map(col => col.label).join('\t');
  
  const rows = data.map(item => {
    return columns.map(col => {
      let value = item[col.key];
      if (value === null || value === undefined) value = '';
      return String(value).replace(/\t/g, ' '); // Remplacer tabs
    }).join('\t');
  }).join('\n');
  
  const tsv = `${headers}\n${rows}`;
  const blob = new Blob(['\uFEFF' + tsv], { type: 'application/vnd.ms-excel;charset=utf-8;' });
  const link = document.createElement('a');
  
  if (link.download !== undefined) {
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
}

/**
 * Colonnes par défaut pour export bénéficiaires
 */
export const BENEFICIARIES_EXPORT_COLUMNS = [
  { key: 'rsu_id', label: 'RSU-ID' },
  { key: 'first_name', label: 'Prénom' },
  { key: 'last_name', label: 'Nom' },
  { key: 'birth_date', label: 'Date naissance' },
  { key: 'gender', label: 'Genre' },
  { key: 'province', label: 'Province' },
  { key: 'department', label: 'Département' },
  { key: 'commune', label: 'Commune' },
  { key: 'phone_number', label: 'Téléphone' },
  { key: 'email', label: 'Email' },
  { key: 'vulnerability_score', label: 'Score Vulnérabilité' },
  { key: 'status', label: 'Statut' },
  { key: 'monthly_income', label: 'Revenu mensuel' },
  { key: 'household_size', label: 'Taille ménage' },
  { key: 'created_at', label: 'Date création' },
];

/**
 * Formater données pour export
 */
export function formatBeneficiariesForExport(beneficiaries) {
  return beneficiaries.map(b => ({
    ...b,
    // Formatage dates
    birth_date: b.birth_date ? new Date(b.birth_date).toLocaleDateString('fr-FR') : '',
    created_at: b.created_at ? new Date(b.created_at).toLocaleDateString('fr-FR') : '',
    
    // Formatage genre
    gender: b.gender === 'M' ? 'Masculin' : b.gender === 'F' ? 'Féminin' : 'Autre',
    
    // Formatage province
    province: b.province ? b.province.replace(/_/g, ' ') : '',
    
    // Formatage montants
    monthly_income: b.monthly_income ? `${b.monthly_income.toLocaleString('fr-FR')} FCFA` : '',
    
    // Formatage statut
    status: formatStatus(b.status),
  }));
}

function formatStatus(status) {
  const statusMap = {
    'VERIFIED': 'Vérifié',
    'PENDING': 'En attente',
    'REVIEW': 'En révision',
    'REJECTED': 'Rejeté'
  };
  return statusMap[status] || status;
}