"""Cryptographic service using authenticated Fernet (AES-128-CBC with HMAC-SHA256).

Security Model:
- Algorithm: Fernet specification (128-bit AES in CBC mode with PKCS7 padding, authenticated via HMAC-SHA256).
- Keys: 256-bit cryptographically secure pseudorandom keys generated via os.urandom and stored in data/vault.key.
- At-rest Protection: Document contents are encrypted prior to being written to storage.
- Nonce/IV: Unique 128-bit IV generated for every individual encryption operation.
"""

import hashlib
import os
from pathlib import Path
from typing import Optional
from cryptography.fernet import Fernet, InvalidToken


class DecryptionError(Exception):
    """Raised when data cannot be decrypted due to key mismatch or corrupted ciphertext."""
    pass


class EncryptionService:
    """Provides high-level encryption and decryption for files and in-memory byte buffers."""

    def __init__(self, key_path: str = "data/vault.key"):
        self.key_path = Path(key_path)
        self.key = self._load_or_generate_key()
        self.cipher = Fernet(self.key)

    def _load_or_generate_key(self) -> bytes:
        """Load the master key from file or generate a fresh 256-bit cryptographically random key."""
        self.key_path.parent.mkdir(parents=True, exist_ok=True)
        if self.key_path.exists():
            content = self.key_path.read_bytes().strip()
            if content and len(content) == 44:  # standard base64 Fernet key length
                return content

        new_key = Fernet.generate_key()
        self.key_path.write_bytes(new_key)
        # Apply restrictive permissions where supported
        try:
            os.chmod(self.key_path, 0o600)
        except Exception:
            pass
        return new_key

    def encrypt_bytes(self, data: bytes) -> bytes:
        """Encrypt in-memory raw bytes into authenticated ciphertext."""
        return self.cipher.encrypt(data)

    def decrypt_bytes(self, token: bytes) -> bytes:
        """Decrypt authenticated ciphertext into original bytes, checking HMAC integrity."""
        try:
            return self.cipher.decrypt(token)
        except InvalidToken as e:
            raise DecryptionError("Decryption failed: Token is invalid, corrupted, or key does not match.") from e

    def encrypt_file(self, src_path: str, dest_path: str) -> None:
        """Encrypt a file from src_path to dest_path at rest."""
        src = Path(src_path)
        if not src.exists():
            raise FileNotFoundError(f"Source file does not exist: {src_path}")
        dest = Path(dest_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        raw_bytes = src.read_bytes()
        encrypted_data = self.cipher.encrypt(raw_bytes)
        dest.write_bytes(encrypted_data)

    def decrypt_file(self, encrypted_path: str, dest_path: str) -> None:
        """Decrypt an encrypted file from encrypted_path and write plaintext to dest_path."""
        enc_file = Path(encrypted_path)
        if not enc_file.exists():
            raise FileNotFoundError(f"Encrypted file does not exist: {encrypted_path}")
        dest = Path(dest_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            decrypted_data = self.cipher.decrypt(enc_file.read_bytes())
            dest.write_bytes(decrypted_data)
        except InvalidToken as e:
            raise DecryptionError(f"Failed to decrypt {encrypted_path}. File may be corrupted or key altered.") from e

    def get_key_fingerprint(self) -> str:
        """Return a non-sensitive SHA-256 fingerprint of the active master encryption key."""
        return hashlib.sha256(self.key).hexdigest()[:16]
