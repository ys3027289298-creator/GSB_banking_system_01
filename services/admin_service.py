from getpass import getpass
from sqlite3 import Connection, Cursor

from models.account import UserAccount
from models.user import User
from utils.security import ADMIN_PASSWORD


def adminMenu(conn: Connection, cursor: Cursor) -> None:
    """Admin panel: view users and transactions."""
    if getpass("Enter the admin password: ") != ADMIN_PASSWORD:
        print("Invalid admin password. Access denied.")
        return

    print("Welcome, admin!")
    while True:
        print("\n1. View all users")
        print("2. View transactions for a user")
        print("3. Logout")
        print("4. Exit")

        try:
            choice: str = input("Enter your choice: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            return

        match choice:
            case "1":
                cursor.execute(
                    "SELECT username, balance FROM users ORDER BY username ASC"
                )
                rows = cursor.fetchall()
                if not rows:
                    print("No users found.")
                for u, b in rows:
                    print(f"Username: {u}, Balance: {b}")

            case "2":
                username: str = input("Enter username: ").strip()
                user = User(conn, cursor, username)
                if not user.isRegistered():
                    print("User does not exist.")
                    continue
                account = UserAccount(conn, cursor, username)
                print(f"User: {username}, Balance: {account.getBalance()}")
                for amt, typ, ts in account.getTransactionHistory():
                    print(f"Amount: {amt}, Type: {str(typ).capitalize()}, Date: {ts}")

            case "3":
                print("Logout successful.")
                return

            case "4":
                print("Goodbye!")
                conn.close()
                raise SystemExit(0)  # For exiting the program

            case _:
                print("Invalid choice.")
