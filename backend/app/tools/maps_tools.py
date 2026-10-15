"""Geographic and distance calculation tools."""
from __future__ import annotations

import math

# Major Indian city coordinates for realistic distance approximation
CITY_COORDINATES: dict[str, tuple[float, float]] = {
    "hyderabad": (17.3850, 78.4867),
    "goa": (15.2993, 74.1240),
    "delhi": (28.6139, 77.2090),
    "mumbai": (19.0760, 72.8777),
    "bangalore": (12.9716, 77.5946),
    "bengaluru": (12.9716, 77.5946),
    "chennai": (13.0827, 80.2707),
    "kolkata": (22.5726, 88.3639),
    "jaipur": (26.9124, 75.7873),
    "agra": (27.1767, 78.0081),
    "varanasi": (25.3176, 82.9739),
    "manali": (32.2432, 77.1892),
    "shimla": (31.1048, 77.1734),
    "kerala": (10.8505, 76.2711),
    "kochi": (9.9312, 76.2673),
    "paris": (48.8566, 2.3522),
    "london": (51.5074, -0.1278),
}


def calculate_distance(origin: str, destination: str) -> float:
    """Calculate haversine distance in km between two locations."""
    coord1 = CITY_COORDINATES.get(origin.lower().strip())
    coord2 = CITY_COORDINATES.get(destination.lower().strip())

    if not coord1 or not coord2:
        return 500.0  # Sensible default distance for intercity transit

    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371.0  # Earth's radius in kilometers

    return round(c * r, 1)


def calculate_travel_time(distance_km: float, mode: str) -> int:
    """Calculate estimated travel time in minutes based on transit mode."""
    mode_speed_kmh = {
        "flight": 600.0,
        "train": 70.0,
        "bus": 50.0,
        "car": 60.0,
    }
    speed = mode_speed_kmh.get(mode.lower(), 60.0)
    transit_minutes = int((distance_km / speed) * 60)
    # Add buffer for check-in / boarding
    buffer_minutes = {"flight": 120, "train": 30, "bus": 20}.get(mode.lower(), 15)
    return transit_minutes + buffer_minutes
