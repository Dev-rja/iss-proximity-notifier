# predictor.py
import builtins
_builtin_round = builtins.round
def _safe_round(x, *args, **kwargs):
    try:
        return _builtin_round(x, *args, **kwargs)
    except TypeError:
        return x
builtins.round = _safe_round

from datetime import datetime, timezone, timedelta
from pyorbital.orbital import Orbital
import urllib.request
import math

from config import MY_CITY, MY_LAT, MY_LON

MY_ALT = 0.0
LOOK_AHEAD_HOURS = 24

TLE_SOURCES = [
    "https://live.ariss.org/iss.txt",
    "https://celestrak.org/NORAD/elements/gp.php?CATNR=25544&FORMAT=TLE",
    "https://celestrak.org/satcat/tle.php?CATNR=25544",
]

def fetch_tle():
    for url in TLE_SOURCES:
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0 (ISS Tracker)"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                lines = [l.strip() for l in resp.read().decode("utf-8").strip().splitlines() if l.strip()]
            l1 = next((l for l in lines if l.startswith("1 ")), None)
            l2 = next((l for l in lines if l.startswith("2 ")), None)
            if l1 and l2:
                print(f"  [TLE] Loaded from {url}")
                return l1, l2
        except Exception as e:
            print(f"  [TLE] {url} failed: {e}")
    return None, None


def get_orb():
    l1, l2 = fetch_tle()
    if l1 and l2:
        return Orbital("ISS (ZARYA)", line1=l1, line2=l2)
    print("  [TLE] All sources failed — using pyorbital built-in TLE")
    return Orbital("ISS (ZARYA)")


def get_max_elev(orb, max_elev_dt):
    try:
        az, el = orb.get_observer_look(max_elev_dt, MY_LON, MY_LAT, MY_ALT)
        return round(abs(float(el)), 1)
    except Exception:
        return 0.0


def get_next_passes():
    """Predict next ISS passes — prints to terminal."""
    try:
        orb = get_orb()
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        passes = orb.get_next_passes(now, LOOK_AHEAD_HOURS, MY_LAT, MY_LON, MY_ALT)
        if not passes:
            print(f"  [PREDICT] No passes over {MY_CITY} in next {LOOK_AHEAD_HOURS}h")
            return
        print(f"\n── Upcoming ISS passes over {MY_CITY} ──────────────────")
        print(f"  {'Rise Time (UTC)':<26} {'Max Elev':<12} {'Set Time (UTC)'}")
        print("  " + "─" * 60)
        for i, (rise, fall, max_elev_dt) in enumerate(passes[:5]):
            elev = get_max_elev(orb, max_elev_dt)
            tag = " ← NEXT" if i == 0 else ""
            print(f"  {str(rise):<26} {elev:6.1f}°      {str(fall)}{tag}")
        print("  " + "─" * 60)
        print(f"  (Add 8 hours to convert UTC → Philippine Time)\n")
    except Exception as e:
        print(f"  [PREDICT] Could not compute passes: {e}")


def get_next_passes_data():
    """Return visible passes as list of dicts for web dashboard."""
    try:
        orb = get_orb()
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        passes = orb.get_next_passes(now, LOOK_AHEAD_HOURS, MY_LAT, MY_LON, MY_ALT)
        result = []
        for rise, fall, max_elev_dt in passes[:6]:
            rise_pht = rise + timedelta(hours=8)
            duration_sec = int((fall - rise).total_seconds())
            mins = duration_sec // 60
            secs = duration_sec % 60
            elev = get_max_elev(orb, max_elev_dt)
            result.append({
                "rise_utc": str(rise),
                "rise_pht": rise_pht.strftime("%b %d %H:%M:%S"),
                "fall_utc": str(fall),
                "max_elev": elev,
                "duration": f"{mins}m {secs}s" if mins > 0 else f"{secs}s",
            })
        return result
    except Exception as e:
        print(f"  [PREDICT] get_next_passes_data error: {e}")
        return []


def _haversine(lat1, lon1, lat2, lon2):
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


def get_proximity_passes_data(radius_km=500):
    """
    Scan next 24 hours in 30s steps.
    Find windows where ISS ground track is within radius_km of CDO.
    Returns list of dicts with entry/closest/exit times and min distance.
    """
    try:
        from sgp4.api import Satrec, jday
        l1, l2 = fetch_tle()
        if not l1:
            return []
        sat = Satrec.twoline2rv(l1, l2)

        now = datetime.now(timezone.utc)
        end = now + timedelta(hours=LOOK_AHEAD_HOURS)
        step = timedelta(seconds=30)

        results = []
        in_pass = False
        pass_start = None
        pass_min_dist = float("inf")
        pass_min_time = None
        t = now

        while t <= end:
            jd, fr = jday(t.year, t.month, t.day, t.hour, t.minute, t.second + t.microsecond/1e6)
            e, r, _ = sat.sgp4(jd, fr)
            if e == 0:
                x, y, z = r
                # Apply GMST rotation to convert TEME → ECEF → lat/lon
                T = (jd + fr - 2451545.0) / 36525.0
                gmst = 280.46061837 + 360.98564736629 * (jd + fr - 2451545.0) + T*T*(0.000387933 - T/38710000)
                gmst = math.radians(gmst % 360)
                x_ecef =  x * math.cos(gmst) + y * math.sin(gmst)
                y_ecef = -x * math.sin(gmst) + y * math.cos(gmst)
                z_ecef = z
                lon = math.degrees(math.atan2(y_ecef, x_ecef))
                hyp = math.sqrt(x_ecef**2 + y_ecef**2)
                lat = math.degrees(math.atan2(z_ecef, hyp))
                dist = _haversine(MY_LAT, MY_LON, lat, lon)

                if dist < radius_km:
                    if not in_pass:
                        in_pass = True
                        pass_start = t
                        pass_min_dist = dist
                        pass_min_time = t
                    elif dist < pass_min_dist:
                        pass_min_dist = dist
                        pass_min_time = t
                else:
                    if in_pass:
                        in_pass = False
                        duration_sec = int((t - pass_start).total_seconds())
                        results.append({
                            "entry_pht":   (pass_start + timedelta(hours=8)).strftime("%b %d %H:%M:%S"),
                            "closest_pht": (pass_min_time + timedelta(hours=8)).strftime("%b %d %H:%M:%S"),
                            "min_dist":    round(pass_min_dist),
                            "duration":    f"{duration_sec//60}m {duration_sec%60}s",
                        })
            t += step

        return results[:6]

    except ImportError:
        print("  [PREDICT] sgp4 not installed — run: pip install sgp4")
        return []
    except Exception as e:
        print(f"  [PREDICT] get_proximity_passes_data error: {e}")
        return []