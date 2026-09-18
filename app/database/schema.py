"""Database schema initialization and safe migration manager for VAULTX."""

import sqlite3
from app.database.connection import get_connection


def init_database() -> None:
    """Create all required tables, indexes, and run non-destructive schema migrations."""
    conn = get_connection()
    with conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            filename TEXT NOT NULL,
            encrypted_path TEXT NOT NULL,
            category TEXT DEFAULT 'General',
            tags TEXT DEFAULT '',
            description TEXT DEFAULT '',
            expiry_date TEXT,
            is_favorite INTEGER DEFAULT 0,
            ocr_text TEXT DEFAULT '',
            file_size INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            parent_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (parent_id) REFERENCES categories (id) ON DELETE CASCADE,
            UNIQUE(user_id, name, parent_id)
        );

        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            document_id INTEGER,
            details TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_docs_user ON documents (user_id);
        CREATE INDEX IF NOT EXISTS idx_docs_expiry ON documents (expiry_date);
        CREATE INDEX IF NOT EXISTS idx_docs_fav ON documents (user_id, is_favorite);
        CREATE INDEX IF NOT EXISTS idx_docs_category ON documents (user_id, category);
        CREATE INDEX IF NOT EXISTS idx_cat_user ON categories (user_id);
        CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users (email);
        """)

        # Migration: ensure description column exists in documents
        cursor = conn.execute("PRAGMA table_info(documents);")
        columns = [row["name"] for row in cursor.fetchall()]
        if "description" not in columns:
            conn.execute("ALTER TABLE documents ADD COLUMN description TEXT DEFAULT '';")

        # Migration: ensure email column exists in users
        cursor_users = conn.execute("PRAGMA table_info(users);")
        user_columns = [row["name"] for row in cursor_users.fetchall()]
        if "email" not in user_columns:
            conn.execute("ALTER TABLE users ADD COLUMN email TEXT DEFAULT '';")

    conn.close()
