# ── api_client.py ──────────────────────────────────────────
import requests

ISS_API_URL = "https://api.wheretheiss.at/v1/satellites/25544"

def get_iss_position():
    """Fetch current ISS latitude and longitude."""
    try:
        response = requests.get(ISS_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        return {
            "latitude":  float(data["latitude"]),
            "longitude": float(data["longitude"]),
            "altitude":  float(data["altitude"]),
            "velocity":  float(data["velocity"]),
        }
    except requests.RequestException as e:
        print(f"[ERROR] Could not reach ISS API: {e}")
        return None
