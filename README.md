# ISS Proximity Notifier

Track the International Space Station in real-time and get notified when it flies over **Cagayan de Oro, Philippines**. Includes a live web dashboard with orbital map, pass predictions, and position logging.

**Live demo:** https://iss-proximity-notifier.vercel.app/

---

## Features

- Live ISS tracking — polls position every 60 seconds
- Desktop alert — notifies you when ISS enters 500 km radius
- Web dashboard — dark mission-control UI at `localhost:5000`
- Orbital map — live ISS dot moving on a world map with trail
- Pass predictor — shows next flyover times in Philippine Time (PHT)
- SQLite logging — stores every position reading to a local database

---

## Setup

```bash
# 1. Clone the project
git clone https://github.com/Dev-rja/iss-proximity-notifier.git
cd iss-notifier

# 2. Install dependencies
pip install -r requirements.txt

# 3a. Run terminal tracker only
python main.py

# 3b. Run web dashboard (recommended)
python app.py
# Then open http://localhost:5000 in your browser
```

> **Note:** Requires Python 3.10–3.12. Python 3.13 has a known compatibility issue with `pyorbital` pass prediction.

---

## Project Structure

```
iss-notifier/
├── app.py              ← Flask web dashboard server
├── main.py             ← terminal tracker & scheduler
├── api_client.py       ← calls the ISS REST API
├── predictor.py        ← ISS pass prediction (pyorbital)
├── distance.py         ← Haversine formula
├── storage.py          ← SQLite logging
├── notifier.py         ← desktop alert (Windows/Mac/Linux)
├── config.py           ← your city, coordinates & settings
├── requirements.txt    ← Python dependencies
└── templates/
    └── index.html      ← web dashboard UI
```

---

## Configuration

Edit `config.py` to change your city or alert settings:

```python
MY_CITY         = "Cagayan de Oro"
MY_LAT          = 8.4822
MY_LON          = 124.6472
ALERT_RADIUS_KM = 500     # alert when ISS is within this distance
POLL_INTERVAL   = 60      # seconds between each API call
```

---

## APIs Used

| API | Purpose | Cost |
|-----|---------|------|
| [wheretheiss.at](https://wheretheiss.at) | Live ISS position, altitude & velocity | Free, no key required |
| [live.ariss.org](https://live.ariss.org/iss.txt) | Live TLE data for pass prediction | Free |
| [celestrak.org](https://celestrak.org) | Fallback TLE source | Free |

---

## What You'll Learn

- Polling a public REST API on a schedule
- JSON parsing and data extraction
- Geospatial math (Haversine formula)
- SQLite database with Python's built-in `sqlite3`
- Flask web server with REST API endpoints
- Desktop notifications (cross-platform)
- Orbital mechanics and TLE data (via `pyorbital`)
- Pass prediction using real satellite data
- Deploying a Python/Flask app to Vercel

---

## Dependencies

```
requests     — HTTP calls to ISS API
schedule     — polling interval scheduler
pyorbital    — orbital mechanics & pass prediction
flask        — web dashboard server
plyer        — cross-platform desktop notifications
```

---

## Web Dashboard Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Main dashboard UI |
| `GET /api/iss` | Live ISS position, altitude, velocity, distance |
| `GET /api/passes` | Next ISS passes over CDO in PHT |
| `GET /api/log` | Last 20 position readings from the database |

---

## Web Dashboard Features

- **Live orbital track** — ISS dot moving on world map in real time with trail
- **Metric cards** — distance, lat/lon, altitude, speed
- **Alert banner** — turns red when ISS is within 500 km
- **Pass schedule** — next flyovers over CDO in PHT
- **Position log** — last 20 readings from the database
- **Auto-refresh** — updates every 60 seconds automatically

---

## Deployment (Vercel)

The web dashboard is deployed on Vercel as a serverless Flask app.

- SQLite writes to `/tmp/iss_log.db` on Vercel (ephemeral, resets on cold start)
- TLE data is fetched live from ARISS and CelesTrak on each request
- No environment variables required beyond `VERCEL=1` (set automatically)

---

## Verifying Accuracy

Cross-check your tracker against the live map at:
https://wheretheiss.at

The ISS travels at ~27,600 km/h so coordinates may differ slightly
between your fetch and the website due to time elapsed between requests.

---

Built as a **Public REST API Ingestion** project — polling, parsing, storing, and visualizing real-time satellite data.