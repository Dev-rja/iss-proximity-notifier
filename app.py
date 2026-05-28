# app.py
"""
ISS Proximity Notifier — Web Dashboard
Run:  python app.py
Then open: http://localhost:5000
"""

import monkey_patch  # MUST be first — fixes Python 3.13 + pyorbital round() bug
from dotenv import load_dotenv
load_dotenv()
from config import MY_CITY, MY_LAT, MY_LON, ALERT_RADIUS_KM, PROXIMITY_RADIUS, POLL_INTERVAL
from flask import Flask, jsonify, render_template_string, request
from datetime import datetime, timezone
import os

from api_client import get_iss_position
from distance   import haversine
from storage    import init_db, save_position, get_recent
from predictor  import get_next_passes_data, get_proximity_passes_data
from mailer     import send_iss_alert

app = Flask(__name__)

# Alert cooldown
_alert_sent = False
_was_nearby = False

# HTML template
HTML = open("templates/index.html", encoding="utf-8").read()

@app.route("/")
def index():
    return render_template_string(HTML, 
    alert_radius=ALERT_RADIUS_KM, 
    proximity_radius=PROXIMITY_RADIUS, 
    city=MY_CITY,
    lat=MY_LAT,
    lon=MY_LON,
    poll_interval=POLL_INTERVAL
)

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

    if is_nearby and not _alert_sent:
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
    return jsonify(get_next_passes_data())

@app.route("/api/proximity")
def proximity_data():
    return jsonify(get_proximity_passes_data(radius_km=PROXIMITY_RADIUS))

@app.route("/api/log")
def log_data():
    rows = get_recent(20)
    return jsonify([{
        "timestamp": r[0], "latitude": r[1], "longitude": r[2],
        "distance":  r[3], "is_nearby": r[4] in (1, "1", True)
    } for r in rows])

@app.route("/api/trail")
def trail_data():
    from storage import get_trail
    limit = int(request.args.get('limit', 288))
    rows = get_trail(limit)
    return jsonify([{"lat": r[0], "lon": r[1]} for r in rows])

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)