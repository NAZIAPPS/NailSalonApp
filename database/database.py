import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "nails.db"


def connect():
    return sqlite3.connect(DB_PATH)


def create_database():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_date TEXT NOT NULL,
            client_name TEXT,
            phone TEXT,
            service_name TEXT NOT NULL,
            amount REAL DEFAULT 0,
            tip REAL DEFAULT 0,
            payment_method TEXT,
            notes TEXT
        )
    """)

    conn.commit()
    conn.close()