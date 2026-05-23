# app.py
import monkey_patch  # MUST be first — fixes Python 3.13 + pyorbital round() bug
"""
ISS Proximity Notifier — Web Dashboard
Run:  python app.py
Then open: http://localhost:5000
"""

from flask import Flask, jsonify, render_template_string
from datetime import datetime, timezone
import sqlite3

from api_client import get_iss_position
from distance   import haversine
from storage    import init_db, save_position
from predictor  import get_next_passes_data
from config     import MY_CITY, MY_LAT, MY_LON, ALERT_RADIUS_KM, DB_FILE

app = Flask(__name__)

# HTML template
HTML = open("templates/index.html", encoding="utf-8").read()

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/api/iss")
def iss_data():
    pos = get_iss_position()
    if not pos:
        return jsonify({"error": "Could not fetch ISS position"}), 500

    dist = haversine(MY_LAT, MY_LON, pos["latitude"], pos["longitude"])
    is_nearby = dist <= ALERT_RADIUS_KM

    save_position(
        pos["latitude"], pos["longitude"],
        pos["altitude"], pos["velocity"],
        dist, is_nearby
    )

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
    conn = sqlite3.connect(DB_FILE)
    rows = conn.execute("""
        SELECT timestamp, latitude, longitude, altitude, velocity, distance, is_nearby
        FROM iss_log ORDER BY id DESC LIMIT 20
    """).fetchall()
    conn.close()
    return jsonify([{
        "timestamp": r[0], "latitude": r[1], "longitude": r[2],
        "altitude": r[3],  "velocity": r[4], "distance":  r[5],
        "is_nearby": bool(r[6])
    } for r in rows])

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)