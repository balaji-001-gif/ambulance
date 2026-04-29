import frappe
from frappe.utils import today, date_diff
import math


def calculate_response_time(departure_time, arrival_time):
    """Calculate response time in minutes."""
    if departure_time and arrival_time:
        from frappe.utils import time_diff_in_seconds
        diff = time_diff_in_seconds(arrival_time, departure_time)
        return round(diff / 60, 2)
    return 0


def calculate_penalty(due_date, completion_date, penalty_per_day):
    """Calculate penalty for overdue tasks."""
    if not due_date:
        return 0
    reference = completion_date or today()
    days = date_diff(reference, due_date)
    return max(0, days) * (penalty_per_day or 0)


def get_nearest_ambulance(latitude, longitude, station=None):
    """
    Geo utils: find nearest available ambulance by GPS coordinates.
    Returns the closest ambulance name or None.
    """
    filters = {"operational_status": "Available", "current_gps_status": "Online"}
    if station:
        filters["home_station"] = station

    ambulances = frappe.get_all(
        "GPS Device Master",
        filters={"device_status": "Active"},
        fields=["assigned_ambulance", "last_known_lat", "last_known_lng"]
    )

    nearest = None
    min_dist = float("inf")

    for amb in ambulances:
        if amb.last_known_lat and amb.last_known_lng:
            dist = haversine(latitude, longitude, amb.last_known_lat, amb.last_known_lng)
            if dist < min_dist:
                min_dist = dist
                nearest = amb.assigned_ambulance

    return nearest


def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two GPS coordinates."""
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
