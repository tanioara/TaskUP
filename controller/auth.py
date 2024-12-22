import sqlite3
from hashlib import sha256

def hash_password(password):
    """Hash the password using SHA256."""
    return sha256(password.encode()).hexdigest()

def check_credentials(username, password):
    """Check if the username and password are correct."""
    conn = sqlite3.connect('./tasks.db')
    cursor = conn.cursor()

    # Search for the user in the database
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?",
                   (username, hash_password(password)))
    user = cursor.fetchone()
    conn.close()

    return user is not None

def register_user(username, password):
    """Register a new user."""
    conn = sqlite3.connect('./tasks.db')
    cursor = conn.cursor()

    # Check if the username already exists
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    if cursor.fetchone() is not None:
        conn.close()
        return False  # Username already exists

    # Insert the new user into the database
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                   (username, hash_password(password)))
    conn.commit()
    conn.close()
    return True
