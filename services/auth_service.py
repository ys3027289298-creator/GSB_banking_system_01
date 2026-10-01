from getpass import getpass
from sqlite3 import Connection, Cursor

from models.account import UserAccount
from models.user import User


def register(conn: Connection, cursor: Cursor) -> None:
    """Register a new user."""
    username: str = input("Enter a username: ")
    password: str = getpass("Enter a password: ")
    confirm: str = getpass("Confirm password: ")

    if password != confirm:
        print("Passwords do not match. Registration failed.")
        return

    user = User(conn, cursor, username, password)
    if user.register():
        print("Registration successful!")
    else:
        print("Username already exists. Registration failed.")


def login(conn: Connection, cursor: Cursor) -> None:
    """Login flow + user menu."""
    username: str = input("Enter your username: ")
    user = User(conn, cursor, username)

    if not user.isRegistered():
        print("User does not exist. Login failed.")
        return

    if not user.isUnlocked():
        lockOut = user.getLoginLockout()
        if lockOut:
            print(
                f"Your account is locked until {lockOut.strftime('%Y-%m-%d %H:%M:%S')}"
            )
        return

    lockOut = user.getLoginLockout()
    if lockOut and user.isUnlocked():
        user.unlock()

    user.password = getpass("Enter your password: ")
    if not user.isAuthenticated():
        user.increaseLoginAttempts()
        attempts = user.getLoginAttempts()
        if attempts >= 3:
            user.lock()
            lockOut = user.getLoginLockout()
            if lockOut:
                print(
                    f"Your account is locked until {lockOut.strftime('%Y-%m-%d %H:%M:%S')}"
                )
        else:
            print(f"Invalid credentials. Attempts remaining: {3 - attempts}")
        return

    account = UserAccount(conn, cursor, username)
    print("Login successful!")
    print(f"Welcome, {username}!")

    while True:
        print("\n1. View balance")
        print("2. Deposit funds")
        print("3. Withdraw funds")
        print("4. Transfer funds")
        print("5. View transaction history")
        print("6. Logout")
        print("7. Exit")

        try:
            choice: str = input("Enter your choice: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            return

        match choice:
            case "1":
                print(f"Balance: {account.getBalance()}")

            case "2":
                amount = float(input("Enter the amount to deposit: "))
                if amount <= 0:
                    print("Invalid deposit amount.")
                    continue
                account.deposit(amount)
                print(f"Deposit successful. New balance: {account.getBalance()}")

            case "3":
                amount = float(input("Enter the amount to withdraw: "))
                if amount <= 0:
                    print("Invalid withdrawal amount.")
                    continue
                if account.withdraw(amount):
                    print(f"Withdrawal successful. New balance: {account.getBalance()}")
                else:
                    print("Insufficient funds.")

            case "4":
                target: str = input("Enter the username to transfer to: ")
                if target == account.username:
                    print("You cannot transfer to yourself.")
                    continue
                if not User(conn, cursor, target).isRegistered():
                    print("User does not exist.")
                    continue
                amount = float(input("Enter the amount to transfer: "))
                if amount <= 0:
                    print("Invalid transfer amount.")
                    continue
                if account.transfer(target, amount):
                    print(f"Transfer successful. New balance: {account.getBalance()}")
                else:
                    print("Insufficient funds.")

            case "5":
                for amt, typ, ts in account.getTransactionHistory():
                    print(f"Amount: {amt}, Type: {str(typ).capitalize()}, Date: {ts}")

            case "6":
                print("Logout successful.")
                return

            case "7":
                print("Goodbye!")
                conn.close()
                raise SystemExit(0)

            case _:
                print("Invalid choice.")
