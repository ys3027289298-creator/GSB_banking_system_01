from sqlite3 import Connection, Cursor


def ensureSchema(conn: Connection, cursor: Cursor) -> None:
    """Create tables if they do not exist."""
    cursor.executescript(
        """
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT(128) NOT NULL,
            balance REAL DEFAULT 0.0,
            login_attempts INTEGER DEFAULT 0,
            login_lockout TEXT
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            amount REAL NOT NULL,
            type TEXT NOT NULL,
            timestamp TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (username) REFERENCES users (username)
        );
        """
    )
    conn.commit()
