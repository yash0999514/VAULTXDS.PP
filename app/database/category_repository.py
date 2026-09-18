"""Category repository for managing hierarchical categories in SQLite."""

from typing import Any, Dict, List, Optional, Tuple
from app.database.connection import get_connection


class CategoryRepository:
    """Handles CRUD operations for user-defined hierarchical document categories."""

    def add_category(self, user_id: int, name: str, parent_id: Optional[int] = None) -> Tuple[bool, str, Optional[int]]:
        clean_name = name.strip()
        if not clean_name:
            return False, "Category name cannot be empty.", None

        conn = get_connection()
        try:
            with conn:
                cursor = conn.execute(
                    "INSERT INTO categories (user_id, name, parent_id) VALUES (?, ?, ?)",
                    (user_id, clean_name, parent_id),
                )
                return True, "Category added successfully.", cursor.lastrowid
        except Exception:
            return False, f"Category '{clean_name}' already exists in this hierarchy.", None
        finally:
            conn.close()

    def get_categories(self, user_id: int) -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.execute(
            "SELECT * FROM categories WHERE user_id = ? ORDER BY COALESCE(parent_id, 0), name ASC, id ASC",
            (user_id,),
        )
        rows = cursor.fetchall()
        conn.close()

        # Return each category name only once in the user interface.
        # This also protects older databases that may already contain
        # duplicate rows from before the UNIQUE constraint was added.
        unique_categories = []
        seen_names = set()
        for row in rows:
            category = dict(row)
            key = category["name"].strip().casefold()
            if key in seen_names:
                continue
            seen_names.add(key)
            unique_categories.append(category)

        return unique_categories

    def delete_category(self, category_id: int, user_id: int) -> bool:
        conn = get_connection()
        with conn:
            cursor = conn.execute(
                "DELETE FROM categories WHERE id = ? AND user_id = ?",
                (category_id, user_id),
            )
            deleted = cursor.rowcount > 0
        conn.close()
        return deleted

    def ensure_default_categories(self, user_id: int) -> None:
        defaults = [
            ("Identity & Legal", None),
            ("Academic & Certificates", None),
            ("Finance & Tax", None),
            ("Medical & Health", None),
            ("Work & Career", None),
            ("General", None),
        ]
        for name, parent in defaults:
            self.add_category(user_id, name, parent)
