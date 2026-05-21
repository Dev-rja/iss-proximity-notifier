# ISS Proximity Notifier

Track the International Space Station in real-time and get notified
when it flies over Cagayan de Oro.

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run!
python main.py
```

## Project structure

```
iss-notifier/
├── main.py          ← entry point & scheduler
├── api_client.py    ← calls the ISS REST API
├── distance.py      ← Haversine formula
├── storage.py       ← SQLite logging
├── notifier.py      ← desktop alert
├── config.py        ← your city & settings
└── requirements.txt
```

## What you'll learn

- Polling a public REST API on a schedule
- JSON parsing
- Geospatial math (Haversine formula)
- SQLite with Python's built-in sqlite3
- Desktop notifications cross-platform

## API used

**Where the ISS at?** — https://wheretheiss.at  
Free, no API key required.
