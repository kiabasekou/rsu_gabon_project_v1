// =============================================================================
// 8. VULNERABILITY SCORING SERVICE (services/scoring/scoringService.js)
// =============================================================================

class ScoringService {
  // Calculer score vulnérabilité local (avant sync backend)
  calculateLocalVulnerabilityScore(personData, householdData) {
    let score = 0;
    const factors = [];

    // 1. Facteurs économiques (30%)
    if (!householdData.hasElectricity) {
      score += 15;
      factors.push({ dimension: 'Économique', factor: 'Pas d\'électricité', points: 15 });
    }

    if (!householdData.hasWater) {
      score += 10;
      factors.push({ dimension: 'Économique', factor: 'Pas d\'eau courante', points: 10 });
    }

    if (householdData.monthlyIncome < 100000) {
      // < 100k FCFA
      score += 5;
      factors.push({ dimension: 'Économique', factor: 'Revenu très faible', points: 5 });
    }

    // 2. Facteurs démographiques (20%)
    const age = this.calculateAge(personData.birthDate);
    if (age < 5 || age > 65) {
      score += 10;
      factors.push({ dimension: 'Démographique', factor: age < 5 ? 'Enfant jeune' : 'Senior', points: 10 });
    }

    if (householdData.size > 7) {
      score += 10;
      factors.push({ dimension: 'Démographique', factor: 'Grande famille', points: 10 });
    }

    // 3. Facteurs sociaux (25%)
    if (personData.educationLevel === 'NONE' || !personData.educationLevel) {
      score += 12;
      factors.push({ dimension: 'Social', factor: 'Pas de scolarisation', points: 12 });
    }

    if (householdData.hasDisabledMember) {
      score += 13;
      factors.push({ dimension: 'Social', factor: 'Membre handicapé', points: 13 });
    }

    // 4. Facteurs géographiques (15%)
    if (['Rural_Remote', 'Forest'].includes(householdData.zoneType)) {
      score += 15;
      factors.push({ dimension: 'Géographique', factor: 'Zone isolée', points: 15 });
    }

    // 5. Facteurs de résilience (10%)
    if (!householdData.hasSavings) {
      score += 5;
      factors.push({ dimension: 'Résilience', factor: 'Pas d\'épargne', points: 5 });
    }

    if (!householdData.hasFoodSecurity) {
      score += 5;
      factors.push({ dimension: 'Résilience', factor: 'Insécurité alimentaire', points: 5 });
    }

    // Normaliser sur 100
    const normalizedScore = Math.min(score, 100);

    return {
      score: normalizedScore,
      category: this.getVulnerabilityCategory(normalizedScore),
      factors,
      breakdown: {
        economic: this.getFactorSum(factors, 'Économique'),
        demographic: this.getFactorSum(factors, 'Démographique'),
        social: this.getFactorSum(factors, 'Social'),
        geographic: this.getFactorSum(factors, 'Géographique'),
        resilience: this.getFactorSum(factors, 'Résilience'),
      },
    };
  }

  calculateAge(birthDate) {
    const diff = Date.now() - new Date(birthDate).getTime();
    return Math.floor(diff / (1000 * 60 * 60 * 24 * 365.25));
  }

  getVulnerabilityCategory(score) {
    if (score >= 70) return 'EXTRÊME';
    if (score >= 50) return 'ÉLEVÉE';
    if (score >= 30) return 'MODÉRÉE';
    return 'FAIBLE';
  }

  getFactorSum(factors, dimension) {
    return factors
      .filter((f) => f.dimension === dimension)
      .reduce((sum, f) => sum + f.points, 0);
  }
}

export default new ScoringService();