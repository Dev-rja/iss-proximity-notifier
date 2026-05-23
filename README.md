# ISS Proximity Notifier

Track the International Space Station in real-time and get notified when it flies over **Cagayan de Oro, Philippines**. Includes a live web dashboard with orbital map, pass predictions, position logging, and automatic email alerts.

**Live demo:** https://iss-proximity-notifier.vercel.app/


## Features

- Live ISS tracking — polls position every 60 seconds
- Gmail email alert — sends a notification when ISS enters 500 km radius
- Vercel cron job — checks ISS position every 5 minutes automatically, no browser needed
- Web dashboard — dark mission-control UI
- Orbital map — live ISS dot moving on a world map with trail
- Pass predictor — shows next flyover times in Philippine Time (PHT)
- SQLite logging — stores every position reading to a local database


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


## Project Structure

```
iss-notifier/
├── app.py              <- Flask web dashboard server
├── main.py             <- terminal tracker & scheduler
├── api_client.py       <- calls the ISS REST API
├── predictor.py        <- ISS pass prediction (pyorbital)
├── distance.py         <- Haversine formula
├── storage.py          <- SQLite logging
├── notifier.py         <- desktop alert (Windows/Mac/Linux)
├── mailer.py           <- Gmail SMTP email alert
├── monkey_patch.py     <- Python 3.13 pyorbital compatibility fix
├── config.py           <- your city, coordinates & settings
├── requirements.txt    <- Python dependencies
├── vercel.json         <- Vercel cron job config
└── templates/
    └── index.html      <- web dashboard UI
```


## Configuration

Edit `config.py` to change your city or alert settings:

```python
MY_CITY         = "Cagayan de Oro"
MY_LAT          = 8.4822
MY_LON          = 124.6472
ALERT_RADIUS_KM = 500     # alert when ISS is within this distance
POLL_INTERVAL   = 60      # seconds between each API call
```


## Email Alerts (Gmail)

The app sends an email alert when the ISS enters the 500 km alert radius. Set these environment variables to enable it:

```bash
GMAIL_USER         = your@gmail.com
GMAIL_APP_PASSWORD = your16charapppassword   # from myaccount.google.com/apppasswords
ALERT_EMAIL        = your@gmail.com
```

To get a Gmail app password, enable 2-Step Verification at myaccount.google.com/security, then go to myaccount.google.com/apppasswords and create one named "ISS Notifier".

On Vercel, add these under Settings > Environment Variables. Locally, set them in PowerShell before running:

```powershell
$env:GMAIL_USER = "your@gmail.com"
$env:GMAIL_APP_PASSWORD = "your16charapppassword"
$env:ALERT_EMAIL = "your@gmail.com"
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
| `GET /api/passes` | Next ISS passes over CDO in PHT |
| `GET /api/log` | Last 20 position readings from the database |


## Web Dashboard Features

- Live orbital track — ISS dot moving on world map in real time with trail
- Metric cards — distance, lat/lon, altitude, speed
- Alert banner — turns red when ISS is within 500 km
- Pass schedule — next flyovers over CDO in PHT
- Position log — last 20 readings from the database
- Auto-refresh — updates every 60 seconds automatically


## Key Concepts

- Polling a public REST API on a schedule
- JSON parsing and data extraction
- Geospatial math (Haversine formula)
- SQLite database with Python's built-in `sqlite3`
- Flask web server with REST API endpoints
- Desktop and email notifications (cross-platform)
- Orbital mechanics and TLE data (via `pyorbital`)
- Pass prediction using real satellite data
- Deploying a Python/Flask app to Vercel
- Serverless cron jobs with Vercel


## Dependencies

```
requests     — HTTP calls to ISS API
schedule     — polling interval scheduler
pyorbital    — orbital mechanics & pass prediction
flask        — web dashboard server
plyer        — cross-platform desktop notifications
```


## Deployment (Vercel)

The web dashboard is deployed on Vercel as a serverless Flask app.

- SQLite writes to `/tmp/iss_log.db` on Vercel (ephemeral, resets on cold start)
- TLE data is fetched live from ARISS and CelesTrak on each request
- A Vercel cron job calls `/api/iss` every 5 minutes automatically
- Add `GMAIL_USER`, `GMAIL_APP_PASSWORD`, and `ALERT_EMAIL` under Vercel Environment Variables to enable email alerts


## Verifying Accuracy

Cross-check your tracker against the live map at https://wheretheiss.at

The ISS travels at ~27,600 km/h so coordinates may differ slightly between your fetch and the website due to time elapsed between requests.


Built as a **Public REST API Ingestion** project — polling, parsing, storing, and visualizing real-time satellite data.