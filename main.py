# ── main.py ────────────────────────────────────────────────
"""
ISS Proximity Notifier
─────────────────────
Polls the ISS position every POLL_INTERVAL seconds.
Saves each reading to SQLite.
Fires a desktop alert when the ISS enters your alert radius.

Run:  python main.py
"""

import time
from datetime import datetime, timezone

import schedule

from config       import MY_CITY, MY_LAT, MY_LON, ALERT_RADIUS_KM, POLL_INTERVAL
from api_client   import get_iss_position
from distance     import haversine
from storage      import init_db, save_position, get_recent
from notifier     import notify
from predictor    import get_next_passes          # ← NEW


def check_iss():
    """One complete poll cycle: fetch → calculate → store → alert."""
    now = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
    print(f"\n[{now}] Checking ISS position…")

    pos = get_iss_position()
    if pos is None:
        return

    dist = haversine(MY_LAT, MY_LON, pos["latitude"], pos["longitude"])
    is_nearby = dist <= ALERT_RADIUS_KM

    print(f"  ISS  → lat {pos['latitude']:.2f}°  lon {pos['longitude']:.2f}°")
    print(f"  Alt  → {pos['altitude']:.1f} km   |   Speed → {pos['velocity']:.0f} km/h")
    print(f"  Dist → {dist:.0f} km from {MY_CITY}")

    save_position(
        pos["latitude"], pos["longitude"],
        pos["altitude"], pos["velocity"],
        dist, is_nearby
    )

    if is_nearby:
        msg = f"ISS is only {dist:.0f} km away! Look up at the sky!"
        print(f"  *** ALERT: {msg} ***")
        notify("ISS Overhead!", msg)
    else:
        print(f"  Status → outside alert radius ({ALERT_RADIUS_KM} km)")


def print_recent_log():
    """Print the last 5 rows from the database."""
    print("\n── Recent log ──────────────────────────────────────")
    print(f"{'Timestamp':<22} {'Lat':>7} {'Lon':>8} {'Dist(km)':>10} {'Near?':>6}")
    print("─" * 60)
    for row in get_recent(5):
        ts, lat, lon, dist, near = row
        flag = "YES ✓" if near else "no"
        print(f"{ts:<22} {lat:>7.2f} {lon:>8.2f} {dist:>10.0f} {flag:>6}")
    print("─" * 60)


def main():
    print("=" * 50)
    print("  ISS Proximity Notifier")
    print(f"  Watching for: {MY_CITY}")
    print(f"  Alert radius: {ALERT_RADIUS_KM} km")
    print(f"  Polling every: {POLL_INTERVAL}s")
    print("=" * 50)

    init_db()
    check_iss()          # run immediately on start
    get_next_passes()    # ← NEW: show predicted passes on startup

    schedule.every(POLL_INTERVAL).seconds.do(check_iss)
    schedule.every(5).minutes.do(print_recent_log)
    schedule.every(2).hours.do(get_next_passes)  # ← NEW: refresh every 2 hours

    print(f"\nRunning… (Ctrl+C to stop)\n")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopped. Final log:")
        print_recent_log()


if __name__ == "__main__":
    main()