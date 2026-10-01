from datetime import datetime
from sqlite3 import Connection, Cursor
from utils.security import hashPassword


class User:
    """User auth + lockout state."""

    def __init__(self, conn: Connection, cursor: Cursor, username: str, password: str | None = None) -> None:
        self.conn = conn
        self.cursor = cursor
        self.username = username
        self.password = password

    def _requirePassword(self) -> None:
        if self.password is None:
            raise ValueError("Password is required")

    def isRegistered(self) -> bool:
        """Check if user exists."""
        self.cursor.execute("SELECT 1 FROM users WHERE username = ?", (self.username,))
        return self.cursor.fetchone() is not None

    def register(self) -> bool:
        """Create user if not exists."""
        self._requirePassword()
        if self.isRegistered():
            return False
        self.cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (self.username, hashPassword(self.password)),  # type: ignore[arg-type]
        )
        self.conn.commit()
        return True

    def isAuthenticated(self) -> bool:
        """Verify username/password."""
        self._requirePassword()
        self.cursor.execute(
            "SELECT 1 FROM users WHERE username = ? AND password = ?",
            (self.username, hashPassword(self.password)),  # type: ignore[arg-type]
        )
        return self.cursor.fetchone() is not None

    # ---- Lockout controls ----
    def increaseLoginAttempts(self) -> None:
        self.cursor.execute(
            "UPDATE users SET login_attempts = login_attempts + 1 WHERE username = ?",
            (self.username,),
        )
        self.conn.commit()

    def getLoginAttempts(self) -> int:
        self.cursor.execute("SELECT login_attempts FROM users WHERE username = ?", (self.username,))
        row = self.cursor.fetchone()
        return int(row[0]) if row else 0

    def lock(self) -> None:
        self.cursor.execute(
            "UPDATE users SET login_lockout = datetime('now','localtime','+60 seconds') WHERE username = ?",
            (self.username,),
        )
        self.conn.commit()

    def unlock(self) -> None:
        self.cursor.execute(
            "UPDATE users SET login_attempts = 0, login_lockout = NULL WHERE username = ?",
            (self.username,),
        )
        self.conn.commit()

    def getLoginLockout(self) -> datetime | None:
        row = self.cursor.execute(
            "SELECT login_lockout FROM users WHERE username = ?",
            (self.username,),
        ).fetchone()
        if row and row[0]:
            return datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
        return None

    def isUnlocked(self) -> bool:
        row = self.cursor.execute(
            "SELECT login_lockout FROM users WHERE username = ?",
            (self.username,),
        ).fetchone()
        if not row or row[0] is None:
            return True
        return datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S") < datetime.now()
