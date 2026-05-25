# storage.py
import sqlite3
import os
import requests
from datetime import datetime, timezone
from config import DB_FILE

# Turso (cloud) or local SQLite
TURSO_URL   = os.environ.get("TURSO_DATABASE_URL", "")
TURSO_TOKEN = os.environ.get("TURSO_AUTH_TOKEN", "")
USE_TURSO   = bool(TURSO_URL and TURSO_TOKEN)

# Local fallback path
_DB = "/tmp/iss_log.db" if os.environ.get("VERCEL") else DB_FILE

CREATE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS iss_log (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT    NOT NULL,
        latitude  REAL    NOT NULL,
        longitude REAL    NOT NULL,
        altitude  REAL,
        velocity  REAL,
        distance  REAL    NOT NULL,
        is_nearby INTEGER NOT NULL DEFAULT 0
    )
"""

# Turso HTTP API
def turso_execute(sql, args=None):
    """Execute a SQL statement via Turso HTTP API."""
    http_url = TURSO_URL.replace("libsql://", "https://")
    payload = {
        "requests": [
            {
                "type": "execute",
                "stmt": {
                    "sql": sql,
                    "args": [{"type": "text", "value": str(a)} for a in (args or [])]
                }
            },
            {"type": "close"}
        ]
    }
    resp = requests.post(
        f"{http_url}/v2/pipeline",
        headers={
            "Authorization": f"Bearer {TURSO_TOKEN}",
            "Content-Type": "application/json"
        },
        json=payload,
        timeout=10
    )
    resp.raise_for_status()
    return resp.json()


def turso_query(sql, args=None):
    """Execute a SELECT via Turso HTTP API, return list of row dicts."""
    result = turso_execute(sql, args)
    try:
        cols = [c["name"] for c in result["results"][0]["response"]["result"]["cols"]]
        rows = result["results"][0]["response"]["result"]["rows"]
        return [tuple(cell["value"] for cell in row) for row in rows]
    except Exception:
        return []


# Public API
def init_db():
    """Create the table if it doesn't exist."""
    if USE_TURSO:
        turso_execute(CREATE_TABLE_SQL)
        print("[DB] Using Turso cloud database")
    else:
        conn = sqlite3.connect(_DB)
        conn.execute(CREATE_TABLE_SQL)
        conn.commit()
        conn.close()
        print(f"[DB] Using local SQLite: {_DB}")


def save_position(lat, lon, altitude, velocity, distance, is_nearby):
    """Insert one ISS observation."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    args = [ts, lat, lon, altitude, velocity, round(distance, 2), 1 if is_nearby else 0]
    sql = """
        INSERT INTO iss_log (timestamp, latitude, longitude, altitude, velocity, distance, is_nearby)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    if USE_TURSO:
        turso_execute(CREATE_TABLE_SQL)
        turso_execute(sql, args)
    else:
        conn = sqlite3.connect(_DB)
        conn.execute(CREATE_TABLE_SQL)
        conn.execute(sql, args)
        conn.commit()
        conn.close()


def get_recent(limit=20):
    """Fetch the most recent ISS observations."""
    sql = "SELECT timestamp, latitude, longitude, distance, is_nearby FROM iss_log ORDER BY id DESC LIMIT ?"
    if USE_TURSO:
        turso_execute(CREATE_TABLE_SQL)
        return turso_query(sql, [limit])
    else:
        conn = sqlite3.connect(_DB)
        conn.execute(CREATE_TABLE_SQL)
        rows = conn.execute(sql, (limit,)).fetchall()
        conn.close()
        return rows
 
    
def get_trail(limit=60):
    """Fetch the last N positions for the orbital trail."""
    sql = "SELECT latitude, longitude FROM iss_log ORDER BY id DESC LIMIT ?"
    if USE_TURSO:
        turso_execute(CREATE_TABLE_SQL)
        rows = turso_query(sql, [limit])
    else:
        conn = sqlite3.connect(_DB)
        conn.execute(CREATE_TABLE_SQL)
        rows = conn.execute(sql, (limit,)).fetchall()
        conn.close()
    # Reverse so oldest first (trail draws in correct direction)
    return list(reversed(rows))