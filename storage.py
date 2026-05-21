# ── storage.py ─────────────────────────────────────────────
import sqlite3
from datetime import datetime, timezone
from config import DB_FILE

def init_db():
    """Create the database and table if they don't exist."""
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
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
    """)
    conn.commit()
    conn.close()
    print(f"[DB] Database ready: {DB_FILE}")

def save_position(lat, lon, altitude, velocity, distance, is_nearby):
    """Insert one ISS observation into the database."""
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
        INSERT INTO iss_log (timestamp, latitude, longitude, altitude, velocity, distance, is_nearby)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        lat, lon, altitude, velocity,
        round(distance, 2),
        1 if is_nearby else 0
    ))
    conn.commit()
    conn.close()

def get_recent(limit=10):
    """Fetch the most recent ISS observations."""
    conn = sqlite3.connect(DB_FILE)
    rows = conn.execute("""
        SELECT timestamp, latitude, longitude, distance, is_nearby
        FROM iss_log ORDER BY id DESC LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return rows