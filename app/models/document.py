"""Document data model for VAULTX."""

from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any


@dataclass
class Document:
    """Represents a secured personal document record in VAULTX."""

    id: Optional[int]
    user_id: int
    title: str
    filename: str
    encrypted_path: str
    category: str = "General"
    tags: str = ""
    description: str = ""
    expiry_date: Optional[str] = None
    is_favorite: bool = False
    ocr_text: str = ""
    file_size: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert the document model to a standard dictionary."""
        return asdict(self)

    @classmethod
    def from_row(cls, row) -> Optional["Document"]:
        """Instantiate Document from a SQLite Row or dictionary."""
        if not row:
            return None
        d = dict(row)
        return cls(
            id=d.get("id"),
            user_id=d.get("user_id", 0),
            title=d.get("title", ""),
            filename=d.get("filename", ""),
            encrypted_path=d.get("encrypted_path", ""),
            category=d.get("category") or "General",
            tags=d.get("tags") or "",
            description=d.get("description") or "",
            expiry_date=d.get("expiry_date"),
            is_favorite=bool(d.get("is_favorite", 0)),
            ocr_text=d.get("ocr_text") or "",
            file_size=d.get("file_size") or 0,
            created_at=d.get("created_at"),
            updated_at=d.get("updated_at"),
        )
