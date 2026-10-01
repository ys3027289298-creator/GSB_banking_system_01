from hashlib import sha512

# Simple constant to avoid hardcoding in code paths
ADMIN_PASSWORD: str = "password"


def hashPassword(password: str) -> str:
    """Return SHA-512 hash of password."""
    return sha512(password.encode()).hexdigest()


def verifyPassword(password: str, hashed: str) -> bool:
    """Compare clear password with stored hash."""
    return hashPassword(password) == hashed
