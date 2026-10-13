"""
Qibla bearing and distance calculations.
Pure trigonometric algorithms using spherical earth model.
"""

from dataclasses import dataclass
import math
from typing import Dict, Union


# Coordinates of the Holy Kaaba in Mecca
KAABA_LATITUDE = 21.4225
KAABA_LONGITUDE = 39.8262
EARTH_RADIUS_KM = 6371.0


@dataclass(frozen=True)
class QiblaResult:
    """Result of Qibla direction and distance calculation."""
    latitude: float
    longitude: float
    bearing: float              # Azimuth angle in degrees from True North (0° - 360°)
    direction: str              # Cardinal direction (e.g. "N", "NE", "SE", etc.)
    distance_km: float          # Great-circle distance to Mecca in kilometers
    kaaba_latitude: float = KAABA_LATITUDE
    kaaba_longitude: float = KAABA_LONGITUDE

    def to_dict(self, lang: str = "en") -> Dict[str, Union[float, str, dict]]:
        desc_en = f"Qibla is {round(self.bearing, 1)}° from True North ({self.direction})"
        desc_ar = f"اتجاه القبلة {round(self.bearing, 1)} درجة من الشمال الحقيقي ({self.direction})"
        return {
            "location": {"latitude": self.latitude, "longitude": self.longitude},
            "bearing": round(self.bearing, 2),
            "direction": self.direction,
            "distance_km": round(self.distance_km, 2),
            "description": desc_ar if lang == "ar" else desc_en,
            "kaaba": {"latitude": self.kaaba_latitude, "longitude": self.kaaba_longitude}
        }


def calculate_bearing(lat: float, lng: float) -> float:
    """
    Calculate the initial forward azimuth (bearing) from user coordinates to the Kaaba.
    Formula:
      θ = atan2( sin(Δlong) * cos(lat2), cos(lat1)*sin(lat2) − sin(lat1)*cos(lat2)*cos(Δlong) )
    """
    lat1 = math.radians(lat)
    lat2 = math.radians(KAABA_LATITUDE)
    delta_lng = math.radians(KAABA_LONGITUDE - lng)

    x = math.sin(delta_lng) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(delta_lng)

    bearing_deg = math.degrees(math.atan2(x, y))
    return (bearing_deg + 360.0) % 360.0


def calculate_distance(lat: float, lng: float) -> float:
    """
    Calculate great-circle distance to the Kaaba using the Haversine formula.
    """
    lat1 = math.radians(lat)
    lat2 = math.radians(KAABA_LATITUDE)
    delta_lat = math.radians(KAABA_LATITUDE - lat)
    delta_lng = math.radians(KAABA_LONGITUDE - lng)

    a = (math.sin(delta_lat / 2.0) ** 2) + math.cos(lat1) * math.cos(lat2) * (math.sin(delta_lng / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1.0 - a)))
    return EARTH_RADIUS_KM * c


def bearing_to_direction(bearing: float) -> str:
    """Convert bearing angle to one of the 8 cardinal directions."""
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    index = round(bearing / 45.0) % 8
    return directions[index]


def calculate_qibla(latitude: float, longitude: float) -> QiblaResult:
    """
    Calculate full Qibla information for a geographic location.
    
    Args:
        latitude: -90 to +90 degrees
        longitude: -180 to +180 degrees
    """
    if not (-90.0 <= latitude <= 90.0):
        raise ValueError(f"Latitude {latitude} out of bounds [-90, 90]")
    if not (-180.0 <= longitude <= 180.0):
        raise ValueError(f"Longitude {longitude} out of bounds [-180, 180]")

    bearing = calculate_bearing(latitude, longitude)
    distance = calculate_distance(latitude, longitude)
    direction = bearing_to_direction(bearing)

    return QiblaResult(
        latitude=latitude,
        longitude=longitude,
        bearing=bearing,
        direction=direction,
        distance_km=distance
    )
