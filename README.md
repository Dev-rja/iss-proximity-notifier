# ISS Proximity Notifier

Track the International Space Station in real-time and get notified when it flies over **Cagayan de Oro, Philippines**. Includes a live web dashboard with orbital map, pass predictions, position logging, and automatic email alerts.

**Live demo:** https://iss-proximity-notifier.vercel.app/


## Features

- Live ISS tracking — polls position every 60 seconds
- Gmail email alert — sends a notification when ISS enters the alert radius
- cron-job.org — pings ISS API every minute automatically, no browser needed
- Cloud database — position log stored in Turso (SQLite-compatible, hosted)
- Web dashboard — dark mission-control UI
- Orbital map — live ISS image marker moving on a satellite world map with trail
- ISS proximity panel — shows when ISS will be within your proximity radius
- Pass predictor — shows when ISS is visible above the horizon in PHT
- Position logging — stores every position reading to Turso cloud database


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
```

> **Note:** Requires Python 3.10–3.12. Python 3.13 has a known compatibility issue with `pyorbital` pass prediction.


## Configuration

All settings are in `config.py`:

```python
# Your city and coordinates
MY_CITY         = "Cagayan de Oro"   # change to your city
MY_LAT          = 8.4822             # your latitude
MY_LON          = 124.6472           # your longitude

# Email alert radius — how close the ISS must be to trigger an email
# Recommended values:
#   500  km — CDO area only, triggers a few times per week
#   1000 km — entire Philippines, triggers once or twice daily
#   1500 km — Philippines + nearby countries, triggers 3-5 times daily
ALERT_RADIUS_KM = 500

# Proximity panel radius — what distance to show in the dashboard panel
# This is wider than ALERT_RADIUS_KM so you can see upcoming passes
# even before they trigger an alert
PROXIMITY_RADIUS = 1500

# How often to poll the ISS API (in seconds)
POLL_INTERVAL = 60

# Local database file (used when running locally)
DB_FILE = "iss_log.db"
```

To watch a different city, update `MY_CITY`, `MY_LAT`, and `MY_LON` with your coordinates. You can find your coordinates at https://latlong.net


## Gmail SMTP Setup

The project sends email alerts via Gmail. To enable this:

**Step 1 — Enable 2-Factor Authentication on your Google account**
Go to https://myaccount.google.com/security and enable 2-Step Verification.

**Step 2 — Create an App Password**
- Go to https://myaccount.google.com/apppasswords
- Select app: **Mail**, device: **Other** (name it "ISS Notifier")
- Copy the 16-character password generated

**Step 3 — Set environment variables**

For local use, create a `.env` file or set them in your terminal:
```bash
GMAIL_USER=your.email@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx   # the 16-char app password
ALERT_EMAIL=recipient@email.com          # who receives the alert
```

For Vercel deployment, add these under **Settings → Environment Variables**:
```
GMAIL_USER
GMAIL_APP_PASSWORD
ALERT_EMAIL
TURSO_DATABASE_URL
TURSO_AUTH_TOKEN
```

> **Note:** Never commit your Gmail credentials to GitHub. Use environment variables only.


## Project Structure

```
iss-notifier/
├── app.py              <- Flask web dashboard server
├── main.py             <- terminal tracker & scheduler
├── api_client.py       <- calls the ISS REST API
├── predictor.py        <- ISS pass prediction (pyorbital + sgp4)
├── distance.py         <- Haversine formula
├── storage.py          <- Turso cloud DB (SQLite locally)
├── notifier.py         <- desktop alert (Windows/Mac/Linux)
├── mailer.py           <- Gmail SMTP email alert
├── monkey_patch.py     <- Python 3.13 pyorbital compatibility fix
├── config.py           <- your city, coordinates & settings
├── requirements.txt    <- Python dependencies
├── vercel.json         <- Vercel deployment config
└── templates/
    ├── index.html      <- web dashboard UI
    └── static/
        └── iss.png     <- ISS image marker
```


## APIs Used

| API | Purpose | Cost |
|-----|---------|------|
| [wheretheiss.at](https://wheretheiss.at) | Live ISS position, altitude & velocity | Free, no key required |
| [live.ariss.org](https://live.ariss.org/iss.txt) | Live TLE data for pass prediction | Free |
| [celestrak.org](https://celestrak.org) | Fallback TLE source | Free |


## Web Dashboard Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Main dashboard UI |
| `GET /api/iss` | Live ISS position, altitude, velocity, distance |
| `GET /api/passes` | Next ISS passes above the horizon in PHT |
| `GET /api/proximity` | Next ISS passes within proximity radius in PHT |
| `GET /api/log` | Last 20 position readings from the database |


## Web Dashboard Features

- Live orbital track — ISS image moving on satellite world map with trail
- Metric cards — distance, lat/lon, altitude, speed, alert radius
- Alert banner — turns red when ISS is within alert radius
- ISS proximity panel — exact entry/closest/exit times within proximity radius
- Pass schedule — when ISS is visible above the horizon from CDO
- Position log — last 20 readings from Turso cloud database
- Auto-refresh — updates every 60 seconds automatically


## Key Concepts

- Polling a public REST API on a schedule
- JSON parsing and data extraction
- Geospatial math (Haversine formula)
- Orbital mechanics with TEME to ECEF geodetic conversion (GMST rotation)
- Cloud database with Turso (SQLite-compatible, no Rust required)
- Flask web server with REST API endpoints
- Desktop and email notifications (cross-platform)
- TLE data and pass prediction (via `pyorbital` and `sgp4`)
- Deploying a Python/Flask app to Vercel
- Automated scheduling with cron-job.org


## Dependencies

```
requests     — HTTP calls to ISS API and Turso HTTP API
schedule     — polling interval scheduler
pyorbital    — orbital mechanics & pass prediction
sgp4         — precise proximity pass scanning
flask        — web dashboard server
plyer        — cross-platform desktop notifications
```


## Deployment (Vercel)

The web dashboard is deployed on Vercel as a serverless Flask app.

- Position data is stored in **Turso** cloud database — persists across requests and cold starts
- TLE data is fetched live from ARISS and CelesTrak on each request
- **cron-job.org** calls `/api/iss` every minute automatically — no visitor needed to keep the log fresh
- Add all required environment variables under Vercel **Settings → Environment Variables**


## Verifying Accuracy

Cross-check your tracker against the live map at https://wheretheiss.at

The ISS travels at ~27,600 km/h so coordinates may differ slightly between your fetch and the website due to time elapsed between requests.


Built as a **Public REST API Ingestion** project — polling, parsing, storing, and visualizing real-time satellite data.