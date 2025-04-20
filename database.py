import sqlite3
import hashlib

DB_PATH = 'users.db'

def get_connection():
    return sqlite3.connect(DB_PATH)

def create_user_table():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT    UNIQUE,
                password TEXT,
                email    TEXT
            )
        ''')
        conn.commit()

def create_images_table():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id   INTEGER,
                filename  TEXT,
                data      BLOB,
                uploaded  DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        conn.commit()

def init_db():
    """Call this once at app startup to ensure all tables exist."""
    create_user_table()
    create_images_table()

# --------------------
# User functions
# --------------------
def add_user(username, password, email):
    hashed = hashlib.sha256(password.encode()).hexdigest()
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                (username, hashed, email)
            )
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        # username already exists
        return False

def authenticate_user(username, password):
    hashed = hashlib.sha256(password.encode()).hexdigest()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, email FROM users WHERE username = ? AND password = ?",
            (username, hashed)
        )
        return cursor.fetchone()  # (id, username, email) or None

# --------------------
# Image functions
# --------------------
def add_image(user_id: int, filename: str, data: bytes):
    """Store a new image blob for a given user."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO images (user_id, filename, data) VALUES (?, ?, ?)",
            (user_id, filename, data)
        )
        conn.commit()

def get_images_for_user(user_id: int):
    """Fetch (filename, data) of all images for this user."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT filename, data FROM images WHERE user_id = ? ORDER BY uploaded DESC",
            (user_id,)
        )
        return cursor.fetchall()  # list of (filename, blob)
