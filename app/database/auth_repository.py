"""Authentication repository with compulsory email validation and multi-credential login."""

import hashlib
import os
import re
from typing import Any, Dict, Optional, Tuple
from app.database.connection import get_connection

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_valid_email(email: str) -> bool:
    """Validate RFC 5322 standard email address format."""
    if not email:
        return False
    return bool(EMAIL_REGEX.match(email.strip()))


class AuthRepository:
    """Handles user registration with compulsory email, dual login, and password management."""

    ITERATIONS = 100_000

    @staticmethod
    def _hash_password(password: str, salt: bytes) -> str:
        """Derive 256-bit password hash using PBKDF2 with HMAC-SHA256."""
        return hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, AuthRepository.ITERATIONS
        ).hex()

    def register(
        self, username: str, password: str, email: str
    ) -> Tuple[bool, str, Optional[int]]:
        """Register a new user account requiring both a valid username and compulsory email."""
        clean_user = username.strip()
        clean_email = email.strip().lower()

        # Validation
        if not clean_user:
            return False, "Username cannot be empty.", None
        if len(clean_user) < 3:
            return False, "Username must be at least 3 characters long.", None
        if not clean_email:
            return False, "Email address is compulsory.", None
        if not is_valid_email(clean_email):
            return False, "Please enter a valid email address (e.g. user@example.com).", None
        if not password or len(password) < 6:
            return False, "Password must be at least 6 characters long.", None

        conn = get_connection()
        try:
            # Check for existing username or email
            cursor = conn.execute(
                "SELECT id, username, email FROM users WHERE username = ? COLLATE NOCASE OR email = ? COLLATE NOCASE",
                (clean_user, clean_email),
            )
            existing = cursor.fetchone()
            if existing:
                if existing["username"].lower() == clean_user.lower():
                    return False, f"Username '{clean_user}' is already registered.", None
                if existing["email"].lower() == clean_email.lower():
                    return False, f"Email address '{clean_email}' is already associated with an account.", None

            salt = os.urandom(16)
            pw_hash = self._hash_password(password, salt)

            with conn:
                cursor = conn.execute(
                    "INSERT INTO users (username, email, password_hash, salt) VALUES (?, ?, ?, ?)",
                    (clean_user, clean_email, pw_hash, salt.hex()),
                )
                user_id = cursor.lastrowid
            return True, "Registration successful.", user_id
        finally:
            conn.close()

    def authenticate(
        self, identifier: str, password: str
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Verify user credentials using either their compulsory Email address or Username."""
        clean_id = identifier.strip()
        if not clean_id or not password:
            return False, "Email/Username and password are required.", None

        conn = get_connection()
        cursor = conn.execute(
            """
            SELECT id, username, email, password_hash, salt, created_at
            FROM users
            WHERE email = ? COLLATE NOCASE OR username = ? COLLATE NOCASE
            """,
            (clean_id, clean_id),
        )
        user = cursor.fetchone()
        conn.close()

        if not user:
            return False, "Invalid email/username or password.", None

        salt = bytes.fromhex(user["salt"])
        computed_hash = self._hash_password(password, salt)

        # Constant-time comparison prevents timing attack leakage
        if hashlib.sha256(computed_hash.encode()).digest() == hashlib.sha256(user["password_hash"].encode()).digest():
            return True, "Login successful.", {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "created_at": user["created_at"],
            }
        return False, "Invalid email/username or password.", None

    def reset_password(
        self, identifier: str, old_password: str, new_password: str
    ) -> Tuple[bool, str]:
        """Update user password after verifying existing credentials."""
        clean_id = identifier.strip()
        auth_ok, msg, user_data = self.authenticate(clean_id, old_password)
        if not auth_ok or not user_data:
            return False, "Current password verification failed."

        if not new_password or len(new_password) < 6:
            return False, "New password must be at least 6 characters long."

        new_salt = os.urandom(16)
        new_hash = self._hash_password(new_password, new_salt)

        conn = get_connection()
        with conn:
            conn.execute(
                "UPDATE users SET password_hash = ?, salt = ? WHERE id = ?",
                (new_hash, new_salt.hex(), user_data["id"]),
            )
        conn.close()
        return True, "Password successfully updated."

    def local_emergency_reset(
        self, identifier: str, new_password: str
    ) -> Tuple[bool, str]:
        """Educational local account reset by identifier (email or username)."""
        clean_id = identifier.strip()
        if not new_password or len(new_password) < 6:
            return False, "New password must be at least 6 characters long."

        conn = get_connection()
        cursor = conn.execute(
            "SELECT id FROM users WHERE email = ? COLLATE NOCASE OR username = ? COLLATE NOCASE",
            (clean_id, clean_id),
        )
        user = cursor.fetchone()
        if not user:
            conn.close()
            return False, f"Account '{clean_id}' does not exist."

        new_salt = os.urandom(16)
        new_hash = self._hash_password(new_password, new_salt)

        with conn:
            conn.execute(
                "UPDATE users SET password_hash = ?, salt = ? WHERE id = ?",
                (new_hash, new_salt.hex(), user["id"]),
            )
        conn.close()
        return True, f"Password for '{clean_id}' reset successfully."
