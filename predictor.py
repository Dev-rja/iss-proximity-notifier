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
    """
    In Python 3.13 + pyorbital, max_elev is returned as a datetime (bug).
    That datetime IS the time of peak elevation.
    Use get_observer_look at that time and take abs() of elevation.
    """
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
    """Return passes as list of dicts for web dashboard."""
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