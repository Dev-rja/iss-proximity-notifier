# ISS Proximity Notifier

Track the International Space Station in real-time and receive notifications when it flies over a configured city. Includes a live web dashboard with orbital map, pass predictions, position logging, and automatic email alerts.

**Live demo:** https://iss-proximity-notifier.vercel.app/


## Features

- Live ISS tracking — polls position every 60 seconds
- Gmail email alert — sends a notification when ISS enters the alert radius
- cron-job.org — pings ISS API every minute automatically, no browser needed
- Cloud database — position log stored in Turso (SQLite-compatible, hosted)
- Web dashboard — dark mission-control UI
- Orbital map — live ISS image marker moving on a satellite world map with trail
- ISS proximity panel — shows when ISS will be within the configured proximity radius
- Pass predictor — shows when ISS is visible above the horizon in local time
- Position logging — stores every position reading to the database


## Local vs Deployed

**Running locally (simplest):**
Clone the project, configure your credentials, and run `python app.py` or `python main.py`. Email alerts and the web dashboard work as long as the script is running. No Vercel or Turso needed.

**Deploying to Vercel (24/7):**
Deploy to Vercel + set up Turso + cron-job.org for fully autonomous tracking and alerts even when the machine is off. See the Deployment section below.

**Just viewing the live tracker:**
Visit https://iss-proximity-notifier.vercel.app — no setup needed.


## Setup

```bash
# 1. Clone the project
git clone https://github.com/Dev-rja/iss-proximity-notifier.git
cd iss-notifier

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure your credentials (see Gmail SMTP Setup)

# 4a. Run terminal tracker only
python main.py

# 4b. Run web dashboard (recommended)
python app.py
# Then open http://localhost:5000
```

> **Note:** Requires Python 3.10–3.12. Python 3.13 has a known compatibility issue with `pyorbital` pass prediction.


## Configuration

All settings are in `config.py`:

```python
# Target city and coordinates
MY_CITY         = "Cagayan de Oro"   # set to the target city name
MY_LAT          = 8.4822             # latitude of the target city
MY_LON          = 124.6472           # longitude of the target city

# Email alert radius — how close the ISS must be to trigger an email
# Recommended values:
#   500  km — city area only, triggers a few times per week
#   1000 km — regional coverage, triggers once or twice daily
#   1500 km — country-wide coverage, triggers 3-5 times daily
ALERT_RADIUS_KM = 500

# Proximity panel radius — distance shown in the dashboard panel
# Set wider than ALERT_RADIUS_KM to see upcoming passes
# before they trigger an alert
PROXIMITY_RADIUS = 1500

# How often to poll the ISS API (in seconds)
# Do NOT go below 10 — you risk getting rate limited by wheretheiss.at
POLL_INTERVAL = 15

# Local database file (used when running locally)
DB_FILE = "iss_log.db"
```

To track a different city, update `MY_CITY`, `MY_LAT`, and `MY_LON` with the target coordinates. Coordinates can be found at https://latlong.net


## Gmail SMTP Setup

The project sends email alerts via Gmail. To enable this:

**Step 1 — Enable 2-Factor Authentication**
Go to https://myaccount.google.com/security and enable 2-Step Verification.

**Step 2 — Create an App Password**
Go to https://myaccount.google.com/apppasswords and create an app password for this project. Copy the 16-character password generated.

**Step 3 — Store your credentials securely**
Create a `.env` file in the project root and add your Gmail credentials there.

> **Important:** The `.env` file is listed in `.gitignore` and must never be committed to GitHub.

**For Vercel deployment**, add your credentials under **Settings → Environment Variables** instead of using a `.env` file.


## Deployment (Vercel + Turso + cron-job.org)

Follow these steps for a fully autonomous 24/7 deployment:

**Step 1 — Deploy to Vercel**
Push the repo to GitHub, go to https://vercel.com and import the repository. Vercel will auto-detect the Flask app and deploy it.

**Step 2 — Set up Turso (cloud database)**
Go to https://app.turso.tech, create a free account, and create a new database. Generate a read/write token and add the database URL and token to Vercel Environment Variables.

**Step 3 — Set up cron-job.org (auto-ping)**
Go to https://cron-job.org, create a free account, and set up a cronjob that pings your `/api/iss` endpoint every minute. This keeps the position log updating 24/7 even when no one visits the site.

**Step 4 — Add all required credentials to Vercel Environment Variables**
Add your Gmail credentials and Turso credentials under Vercel project Settings → Environment Variables.

**Step 5 — Redeploy**
Push any change to GitHub and Vercel will redeploy automatically.


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
├── config.py           <- target city, coordinates & settings
├── requirements.txt    <- Python dependencies
├── vercel.json         <- Vercel deployment config
├── .env                <- local credentials (never commit this)
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


## Web Dashboard Features

- Live orbital track — ISS image moving on satellite world map with trail
- Metric cards — distance, lat/lon, altitude, speed, alert radius
- Alert banner — turns red when ISS is within alert radius
- ISS proximity panel — exact entry/closest/exit times within proximity radius
- Pass schedule — when ISS is visible above the horizon from the target city
- Position log — last 20 readings from the database
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
requests         — HTTP calls to ISS API and Turso HTTP API
schedule         — polling interval scheduler
pyorbital        — orbital mechanics & pass prediction
sgp4             — precise proximity pass scanning
flask            — web dashboard server
plyer            — cross-platform desktop notifications
python-dotenv    — loads .env file for local credential management
```


## Verifying Accuracy

Cross-check the tracker against the live map at https://wheretheiss.at

The ISS travels at ~27,600 km/h so coordinates may differ slightly between fetches due to time elapsed between requests.


Built as a **Public REST API Ingestion** project — polling, parsing, storing, and visualizing real-time satellite data.