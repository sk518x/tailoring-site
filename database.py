import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path("instance") / "tailoring.db"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS enquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            message TEXT NOT NULL,
            source TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL
        )
        """
    )
    return connection


def save_enquiry(name, phone, message, source=""):
    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    connection = get_connection()
    with connection:
        connection.execute(
            "INSERT INTO enquiries (name, phone, message, source, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (name, phone, message, source, created_at),
        )
    connection.close()


def get_enquiries():
    connection = get_connection()
    rows = connection.execute(
        "SELECT id, name, phone, message, source, created_at "
        "FROM enquiries ORDER BY id DESC"
    ).fetchall()
    connection.close()
    return [dict(row) for row in rows]