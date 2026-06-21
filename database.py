import sqlite3
import os

DB_PATH = "calendar.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            date TEXT NOT NULL,
            time_start TEXT,
            time_end TEXT,
            repeat TEXT DEFAULT 'none',
            reminder TEXT DEFAULT 'none',
            description TEXT,
            color TEXT DEFAULT '#7C5CBF',
            emoji TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            datetime TEXT NOT NULL,
            category TEXT DEFAULT 'Личное',
            color TEXT DEFAULT '#22C55E',
            emoji TEXT DEFAULT '',
            is_done INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
    """)

    defaults = [
        ("theme", "light"),
        ("first_day", "monday"),
        ("timezone", "UTC+03:00"),
        ("time_format", "24"),
        ("event_reminder", "30min"),
        ("reminder_notify", "attime"),
    ]
    for key, value in defaults:
        cur.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, value))

    conn.commit()
    conn.close()
