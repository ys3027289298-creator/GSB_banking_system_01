from sqlite3 import Connection, Cursor, connect

from database.db_setup import ensureSchema
from services.admin_service import adminMenu
from services.auth_service import login, register


def main() -> None:
    """App entry: opens DB, ensures schema, shows menu."""
    conn: Connection = connect(".database.db")
    cursor: Cursor = conn.cursor()
    ensureSchema(conn, cursor)

    while True:
        print()
        print("1. Register")
        print("2. Login")
        print("3. Admin")
        print("4. Exit")

        try:
            choice: str = input("Enter your choice: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        match choice:
            case "1":
                register(conn, cursor)
            case "2":
                login(conn, cursor)
            case "3":
                adminMenu(conn, cursor)
            case "4":
                print("Goodbye!")
                break
            case _:
                print("Invalid choice. Try again.")

    conn.close()


if __name__ == "__main__":
    main()
