from datetime import datetime
from sqlite3 import Connection, Cursor
from typing import Literal

TxType = Literal["deposit", "withdrawal", "transfer", "receive"]


class UserAccount:
    """Balance ops + transactions."""

    def __init__(self, conn: Connection, cursor: Cursor, username: str) -> None:
        self.conn = conn
        self.cursor = cursor
        self.username = username

    def getBalance(self) -> float:
        self.cursor.execute("SELECT balance FROM users WHERE username = ?", (self.username,))
        row = self.cursor.fetchone()
        return float(row[0]) if row else 0.0

    def _addTx(self, username: str, amount: float, txType: str) -> None:
        self.cursor.execute(
            "INSERT INTO transactions (username, amount, type) VALUES (?, ?, ?)",
            (username, amount, txType),
        )

    def deposit(self, amount: float) -> None:
        self.cursor.execute(
            "UPDATE users SET balance = balance + ? WHERE username = ?",
            (amount, self.username),
        )
        self._addTx(self.username, amount, "deposit")
        self.conn.commit()

    def withdraw(self, amount: float) -> bool:
        if self.getBalance() < amount:
            return False
        self.cursor.execute(
            "UPDATE users SET balance = balance - ? WHERE username = ?",
            (amount, self.username),
        )
        self._addTx(self.username, amount, "withdrawal")
        self.conn.commit()
        return True

    def transfer(self, target: str, amount: float) -> bool:
        if self.getBalance() < amount:
            return False
        # credit target
        self.cursor.execute(
            "UPDATE users SET balance = balance + ? WHERE username = ?",
            (amount, target),
        )
        # debit self
        self.cursor.execute(
            "UPDATE users SET balance = balance - ? WHERE username = ?",
            (amount, self.username),
        )
        # tx logs
        self._addTx(target, amount, f"receive from {self.username}")
        self._addTx(self.username, amount, f"transfer to {target}")
        self.conn.commit()
        return True

    def getTransactionHistory(self) -> list[tuple[float, TxType | str, datetime]]:
        self.cursor.execute(
            "SELECT amount, type, timestamp FROM transactions WHERE username = ? ORDER BY id ASC",
            (self.username,),
        )
        rows = self.cursor.fetchall()
        return [(float(r[0]), r[1], datetime.strptime(r[2], "%Y-%m-%d %H:%M:%S")) for r in rows]
