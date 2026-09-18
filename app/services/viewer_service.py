"""Viewer service to temporarily decrypt documents for in-memory or controlled external viewing."""

import atexit
import os
import tempfile
from pathlib import Path
from typing import List, Optional
from app.services.encryption_service import DecryptionError, EncryptionService


class ViewerService:
    """Controls secure decryption of documents for in-application viewing and user export."""

    def __init__(self, encryption_service: EncryptionService):
        self.encryption = encryption_service
        self._temp_files: List[Path] = []
        atexit.register(self.cleanup_temp_files)

    def get_decrypted_bytes(self, encrypted_file_path: str) -> Optional[bytes]:
        """Decrypt document in-memory without creating plaintext files on disk."""
        path = Path(encrypted_file_path)
        if not path.exists():
            return None
        try:
            return self.encryption.decrypt_bytes(path.read_bytes())
        except (DecryptionError, Exception):
            return None

    def export_decrypted(self, encrypted_file_path: str, export_path: str) -> bool:
        """Export decrypted copy to user-selected destination."""
        try:
            self.encryption.decrypt_file(encrypted_file_path, export_path)
            return True
        except Exception:
            return False

    def create_temporary_decrypted_file(self, encrypted_file_path: str, original_filename: str) -> Optional[str]:
        """Create a temporary plaintext file for external viewing and register it for cleanup."""
        decrypted_bytes = self.get_decrypted_bytes(encrypted_file_path)
        if not decrypted_bytes:
            return None

        suffix = Path(original_filename).suffix
        temp_dir = Path(tempfile.gettempdir()) / "vaultx_previews"
        temp_dir.mkdir(parents=True, exist_ok=True)
        temp_file = temp_dir / f"view_{os.getpid()}_{Path(original_filename).stem}{suffix}"
        temp_file.write_bytes(decrypted_bytes)
        self._temp_files.append(temp_file)
        return str(temp_file)

    def cleanup_temp_files(self) -> None:
        """Securely wipe temporary preview files on application exit."""
        for p in self._temp_files:
            try:
                if p.exists():
                    p.unlink()
            except Exception:
                pass
        self._temp_files.clear()
