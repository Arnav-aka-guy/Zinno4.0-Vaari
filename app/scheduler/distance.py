"""Distance calculations: Haversine multiplied by road factor, rounded to 0.1 km."""

import math


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Straight-line great-circle distance between two points in km."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(d_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


def estimated_distance_km(
    lat1: float | None,
    lon1: float | None,
    lat2: float | None,
    lon2: float | None,
    road_factor: float = 1.3,
) -> float:
    """Estimated road distance in km. Returns 0.0 if any coordinate is missing."""
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return 0.0
    dist = haversine_km(lat1, lon1, lat2, lon2) * road_factor
    return round(dist, 1)
