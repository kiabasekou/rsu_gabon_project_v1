// =============================================================================
// 7. VALIDATION SERVICE (services/validation/validationService.js)
// =============================================================================

class ValidationService {
  // Valider NIP gabonais
  validateNIP(nip) {
    if (!nip) return { valid: false, error: 'NIP requis' };

    // Format: 10-14 chiffres
    const nipRegex = /^\d{10,14}$/;
    if (!nipRegex.test(nip)) {
      return {
        valid: false,
        error: 'NIP invalide (10-14 chiffres requis)',
      };
    }

    return { valid: true };
  }

  // Valider téléphone gabonais
  validatePhone(phone) {
    if (!phone) return { valid: true }; // Optionnel

    // Format: +241 XX XX XX XX ou 0X XX XX XX XX
    const phoneRegex = /^(\+241|0)[1-7]\d{7}$/;
    const cleaned = phone.replace(/\s/g, '');

    if (!phoneRegex.test(cleaned)) {
      return {
        valid: false,
        error: 'Téléphone invalide (format: +241 XX XX XX XX)',
      };
    }

    return { valid: true, normalized: cleaned };
  }

  // Valider date de naissance
  validateBirthDate(dateString) {
    if (!dateString) return { valid: false, error: 'Date requise' };

    const date = new Date(dateString);
    const now = new Date();

    if (isNaN(date.getTime())) {
      return { valid: false, error: 'Date invalide' };
    }

    const age = (now - date) / (1000 * 60 * 60 * 24 * 365.25);

    if (age < 0) {
      return { valid: false, error: 'Date dans le futur' };
    }

    if (age > 120) {
      return { valid: false, error: 'Âge trop élevé' };
    }

    return { valid: true, age: Math.floor(age) };
  }

  // Valider formulaire complet
  validateEnrollmentForm(formData) {
    const errors = {};

    // Champs obligatoires
    if (!formData.firstName?.trim()) {
      errors.firstName = 'Prénom requis';
    }

    if (!formData.lastName?.trim()) {
      errors.lastName = 'Nom requis';
    }

    if (!formData.gender) {
      errors.gender = 'Sexe requis';
    }

    // Validation NIP
    if (formData.nip) {
      const nipValidation = this.validateNIP(formData.nip);
      if (!nipValidation.valid) {
        errors.nip = nipValidation.error;
      }
    }

    // Validation date naissance
    const birthValidation = this.validateBirthDate(formData.birthDate);
    if (!birthValidation.valid) {
      errors.birthDate = birthValidation.error;
    }

    // Validation téléphone
    if (formData.phone) {
      const phoneValidation = this.validatePhone(formData.phone);
      if (!phoneValidation.valid) {
        errors.phone = phoneValidation.error;
      }
    }

    // Validation province
    const validProvinces = [
      'Estuaire',
      'Haut-Ogooué',
      'Moyen-Ogooué',
      'Ngounié',
      'Nyanga',
      'Ogooué-Ivindo',
      'Ogooué-Lolo',
      'Ogooué-Maritime',
      'Woleu-Ntem',
    ];

    if (!validProvinces.includes(formData.province)) {
      errors.province = 'Province invalide';
    }

    return {
      isValid: Object.keys(errors).length === 0,
      errors,
    };
  }
}

export default new ValidationService();