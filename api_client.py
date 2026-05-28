# api_client.py
import requests

ISS_API_URL = "https://api.wheretheiss.at/v1/satellites/25544"
ISS_API_FALLBACK = "https://api.open-notify.org/iss-now.json"

def get_iss_position():
    # Try primary API
    try:
        response = requests.get(ISS_API_URL, timeout=20)  # ← 10 to 20
        response.raise_for_status()
        data = response.json()
        return {
            "latitude":  float(data["latitude"]),
            "longitude": float(data["longitude"]),
            "altitude":  float(data["altitude"]),
            "velocity":  float(data["velocity"]),
        }
    except requests.RequestException as e:
        print(f"[ERROR] Primary ISS API failed: {e}")

    # Try fallback API
    try:
        print("[INFO] Trying fallback ISS API...")
        response = requests.get(ISS_API_FALLBACK, timeout=20)
        response.raise_for_status()
        data = response.json()
        return {
            "latitude":  float(data["iss_position"]["latitude"]),
            "longitude": float(data["iss_position"]["longitude"]),
            "altitude":  420.0,
            "velocity":  27600.0,
        }
    except requests.RequestException as e:
        print(f"[ERROR] Fallback ISS API also failed: {e}")
        return None
