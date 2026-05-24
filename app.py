# app.py
import monkey_patch  # MUST be first — fixes Python 3.13 + pyorbital round() bug
"""
ISS Proximity Notifier — Web Dashboard
Run:  python app.py
Then open: http://localhost:5000
"""

from flask import Flask, jsonify, render_template_string
from datetime import datetime, timezone
import os

from api_client import get_iss_position
from distance   import haversine
from storage    import init_db, save_position, get_recent
from predictor  import get_next_passes_data
from mailer     import send_iss_alert
from config     import MY_CITY, MY_LAT, MY_LON, ALERT_RADIUS_KM

app = Flask(__name__)

# Alert cooldown
# Prevents sending duplicate emails during the same pass.
# Resets when ISS leaves the alert radius.
_alert_sent    = False   # was alert sent for the current pass?
_was_nearby    = False   # was ISS nearby on the previous poll?

# HTML template
HTML = open("templates/index.html", encoding="utf-8").read()

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/api/iss")
def iss_data():
    global _alert_sent, _was_nearby

    pos = get_iss_position()
    if not pos:
        return jsonify({"error": "Could not fetch ISS position"}), 500

    dist      = haversine(MY_LAT, MY_LON, pos["latitude"], pos["longitude"])
    is_nearby = dist <= ALERT_RADIUS_KM

    save_position(
        pos["latitude"], pos["longitude"],
        pos["altitude"], pos["velocity"],
        dist, is_nearby
    )

    # Email alert logic
    if is_nearby and not _alert_sent:
        # ISS just entered the radius — send one alert
        success = send_iss_alert(
            distance_km = dist,
            latitude    = pos["latitude"],
            longitude   = pos["longitude"],
            altitude    = pos["altitude"],
            velocity    = pos["velocity"],
            city        = MY_CITY,
        )
        if success:
            _alert_sent = True

    elif not is_nearby and _was_nearby:
        # ISS left the radius — reset so next pass triggers a new alert
        _alert_sent = False

    _was_nearby = is_nearby

    return jsonify({
        "latitude":  pos["latitude"],
        "longitude": pos["longitude"],
        "altitude":  pos["altitude"],
        "velocity":  pos["velocity"],
        "distance":  round(dist, 1),
        "is_nearby": is_nearby,
        "city":      MY_CITY,
        "threshold": ALERT_RADIUS_KM,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    })

@app.route("/api/passes")
def passes_data():
    passes = get_next_passes_data()
    return jsonify(passes)

@app.route("/api/log")
def log_data():
    rows = get_recent(20)
    return jsonify([{
        "timestamp": r[0], "latitude": r[1], "longitude": r[2],
        "distance":  r[3], "is_nearby": r[4] in (1, "1", True)
    } for r in rows])

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)