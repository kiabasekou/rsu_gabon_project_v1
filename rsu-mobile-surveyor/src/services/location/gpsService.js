
// =============================================================================
// 6. GPS SERVICE (services/location/gpsService.js)
// =============================================================================
import * as Location from 'expo-location';

class GPSService {
  async requestPermissions() {
    const { status } = await Location.requestForegroundPermissionsAsync();
    return status === 'granted';
  }

  async getCurrentLocation() {
    const hasPermission = await this.requestPermissions();
    if (!hasPermission) {
      throw new Error('Permission GPS refusée');
    }

    const location = await Location.getCurrentPositionAsync({
      accuracy: Location.Accuracy.High,
    });

    return {
      latitude: location.coords.latitude,
      longitude: location.coords.longitude,
      accuracy: location.coords.accuracy,
      timestamp: location.timestamp,
    };
  }

  // Vérifier si coordonnées dans Gabon
  isInGabon(latitude, longitude) {
    // Limites approximatives du Gabon
    const GABON_BOUNDS = {
      minLat: -4.0,
      maxLat: 2.3,
      minLng: 8.7,
      maxLng: 14.5,
    };

    return (
      latitude >= GABON_BOUNDS.minLat &&
      latitude <= GABON_BOUNDS.maxLat &&
      longitude >= GABON_BOUNDS.minLng &&
      longitude <= GABON_BOUNDS.maxLng
    );
  }

  // Obtenir province depuis coordonnées (simplifié)
  async getProvinceFromCoordinates(latitude, longitude) {
    // Dans production, utiliser reverse geocoding API
    // Pour MVP, retour manuel basé sur zones
    if (!this.isInGabon(latitude, longitude)) {
      throw new Error('Coordonnées hors du Gabon');
    }

    // Logique simplifiée (à affiner avec données réelles)
    if (latitude > 0 && longitude < 10) return 'Estuaire';
    if (latitude < -2) return 'Nyanga';
    if (longitude > 13) return 'Haut-Ogooué';
    // ... autres provinces

    return 'Province Inconnue';
  }
}

export default new GPSService();