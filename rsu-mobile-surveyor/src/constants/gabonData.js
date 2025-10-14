// =============================================================================
// 1. DONNÉES GABON (constants/gabonData.js)
// =============================================================================
export const GABON_PROVINCES = {
  ESTUAIRE: {
    name: 'Estuaire',
    capital: 'Libreville',
    departments: [
      'Libreville',
      'Komo-Mondah',
      'Noya',
    ],
    vulnerability_level: 'LOW',
    urban_rate: 0.89,
  },
  HAUT_OGOOUE: {
    name: 'Haut-Ogooué',
    capital: 'Franceville',
    departments: [
      'Franceville',
      'Lekoko',
      'Lemboumbi-Leyou',
      'Mpassa',
      'Plateaux Batéké',
      'Sebe-Brikolo',
    ],
    vulnerability_level: 'MODERATE',
    urban_rate: 0.67,
  },
  MOYEN_OGOOUE: {
    name: 'Moyen-Ogooué',
    capital: 'Lambaréné',
    departments: [
      'Abanga-Bigne',
      'Lambaréné',
      'Ogooué et des Lacs',
    ],
    vulnerability_level: 'MODERATE',
    urban_rate: 0.54,
  },
  NGOUNIE: {
    name: 'Ngounié',
    capital: 'Mouila',
    departments: [
      'Boumi-Louetsi',
      'Douya-Onoye',
      'Dola',
      'Louetsi-Wano',
      'Lolo-Bouenguidi',
      'Mimongo',
      'Tsamba-Magotsi',
    ],
    vulnerability_level: 'HIGH',
    urban_rate: 0.43,
  },
  NYANGA: {
    name: 'Nyanga',
    capital: 'Tchibanga',
    departments: [
      'Basse-Banio',
      'Douigny',
      'Haute-Banio',
      'Mondah-Ndounga',
      'Mougoutsi',
      'Doutsila',
    ],
    vulnerability_level: 'CRITICAL',
    urban_rate: 0.31,
  },
  OGOOUE_IVINDO: {
    name: 'Ogooué-Ivindo',
    capital: 'Makokou',
    departments: [
      'Ivindo',
      'Lope',
      'Mvoung',
      'Zadie',
    ],
    vulnerability_level: 'HIGH',
    urban_rate: 0.38,
  },
  OGOOUE_LOLO: {
    name: 'Ogooué-Lolo',
    capital: 'Koulamoutou',
    departments: [
      'Booue',
      'Lolo',
      'Lombo-Bouenguidi',
      'Offoue-Onoye',
      'Mulundu',
    ],
    vulnerability_level: 'HIGH',
    urban_rate: 0.45,
  },
  OGOOUE_MARITIME: {
    name: 'Ogooué-Maritime',
    capital: 'Port-Gentil',
    departments: [
      'Bendje',
      'Etimboue',
      'Komo-Kango',
      'Ndougou',
      'Port-Gentil',
    ],
    vulnerability_level: 'MODERATE',
    urban_rate: 0.72,
  },
  WOLEU_NTEM: {
    name: 'Woleu-Ntem',
    capital: 'Oyem',
    departments: [
      'Haut-Como',
      'Haut-Ntem',
      'Okano',
      'Woleu',
    ],
    vulnerability_level: 'MODERATE',
    urban_rate: 0.56,
  },
};

// Facteurs de vulnérabilité contextualisés Gabon
export const VULNERABILITY_FACTORS = {
  ECONOMIC: {
    UNEMPLOYMENT: {
      label: 'Chômage',
      weight: 0.25,
      threshold: 'occupationStatus === "UNEMPLOYED"',
    },
    LOW_INCOME: {
      label: 'Revenu faible',
      weight: 0.20,
      threshold: 'monthlyIncome < 100000', // FCFA
    },
    INFORMAL_WORK: {
      label: 'Emploi informel',
      weight: 0.15,
      threshold: 'occupationStatus === "INFORMAL"',
    },
    NO_SAVINGS: {
      label: 'Pas d\'épargne',
      weight: 0.10,
      threshold: 'hasSavings === "no"',
    },
    POOR_HOUSING: {
      label: 'Logement précaire',
      weight: 0.15,
      threshold: 'housingType === "PRECARIOUS"',
    },
    NO_ELECTRICITY: {
      label: 'Pas d\'électricité',
      weight: 0.10,
      threshold: 'hasElectricity === "no"',
    },
    NO_WATER: {
      label: 'Pas d\'eau courante',
      weight: 0.05,
      threshold: 'hasRunningWater === "no"',
    },
  },
  SOCIAL: {
    NO_EDUCATION: {
      label: 'Aucune éducation',
      weight: 0.30,
      threshold: 'educationLevel === "NONE"',
    },
    PRIMARY_ONLY: {
      label: 'Primaire seulement',
      weight: 0.20,
      threshold: 'educationLevel === "PRIMARY"',
    },
    FEMALE_HEAD: {
      label: 'Chef de ménage féminine',
      weight: 0.15,
      threshold: 'gender === "F" && isHouseholdHead === true',
    },
    YOUNG_PARENT: {
      label: 'Parent jeune (<25 ans)',
      weight: 0.15,
      threshold: 'age < 25 && dependents > 0',
    },
    ELDERLY: {
      label: 'Personne âgée (>65 ans)',
      weight: 0.20,
      threshold: 'age > 65',
    },
  },
  DEMOGRAPHIC: {
    LARGE_HOUSEHOLD: {
      label: 'Ménage nombreux (>6)',
      weight: 0.25,
      threshold: 'householdSize > 6',
    },
    HIGH_DEPENDENCY: {
      label: 'Ratio dépendance élevé',
      weight: 0.30,
      threshold: '(dependents / householdSize) > 0.6',
    },
    LOW_INCOME_PER_CAPITA: {
      label: 'Revenu/personne faible',
      weight: 0.25,
      threshold: '(totalIncome / householdSize) < 50000',
    },
    SINGLE_PARENT: {
      label: 'Parent isolé',
      weight: 0.20,
      threshold: 'maritalStatus === "SINGLE" && dependents > 0',
    },
  },
  GEOGRAPHIC: {
    RURAL_REMOTE: {
      label: 'Zone rurale isolée',
      weight: 0.40,
      threshold: 'province IN ["NYANGA", "OGOOUE_IVINDO", "OGOOUE_LOLO"]',
    },
    LIMITED_ACCESS: {
      label: 'Accès limité services',
      weight: 0.30,
      threshold: 'distanceToServices > 50', // km
    },
    POOR_INFRASTRUCTURE: {
      label: 'Infrastructure déficiente',
      weight: 0.30,
      threshold: 'infrastructureScore < 40',
    },
  },
  RESILIENCE: {
    NO_SOCIAL_NETWORK: {
      label: 'Pas de réseau social',
      weight: 0.25,
      threshold: 'hasSocialSupport === "no"',
    },
    FOOD_INSECURITY: {
      label: 'Insécurité alimentaire',
      weight: 0.35,
      threshold: 'hasFoodSecurity === "no"',
    },
    NO_EMERGENCY_FUND: {
      label: 'Pas de fonds d\'urgence',
      weight: 0.20,
      threshold: 'hasEmergencyFund === "no"',
    },
    HEALTH_ISSUES: {
      label: 'Problèmes de santé',
      weight: 0.20,
      threshold: 'hasHealthIssues === "yes"',
    },
  },
};

// Configuration scoring selon standards RSU Gabon
export const SCORING_CONFIG = {
  WEIGHTS: {
    economic: 0.30,
    social: 0.25,
    demographic: 0.20,
    geographic: 0.15,
    resilience: 0.10,
  },
  THRESHOLDS: {
    CRITICAL: 75,
    HIGH: 50,
    MODERATE: 25,
    LOW: 0,
  },
  INCOME_THRESHOLDS: {
    EXTREME_POVERTY: 30000,   // FCFA/mois
    POVERTY: 60000,
    LOW_INCOME: 150000,
    MIDDLE_CLASS: 400000,
    HIGH_INCOME: 1000000,
  },
  AGE_VULNERABILITY: {
    CHILD: { min: 0, max: 5, weight: 0.8 },
    YOUTH: { min: 15, max: 24, weight: 0.6 },
    ADULT: { min: 25, max: 54, weight: 0.3 },
    ELDERLY: { min: 65, max: 120, weight: 0.9 },
  },
};
