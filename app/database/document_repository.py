"""CRUD operations and analytical queries for document persistence in SQLite."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from app.database.connection import get_connection


class DocumentRepository:
    """Repository handling database operations for personal encrypted documents."""

    def add_document(
        self,
        user_id: int,
        title: str,
        filename: str,
        encrypted_path: str,
        category: str = "General",
        tags: str = "",
        description: str = "",
        expiry_date: Optional[str] = None,
        is_favorite: bool = False,
        ocr_text: str = "",
        file_size: int = 0,
    ) -> int:
        """Insert a new document record and return its primary key ID."""
        conn = get_connection()
        with conn:
            cursor = conn.execute(
                """
                INSERT INTO documents (
                    user_id, title, filename, encrypted_path, category, tags,
                    description, expiry_date, is_favorite, ocr_text, file_size
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    title.strip(),
                    filename,
                    encrypted_path,
                    category.strip() or "General",
                    tags.strip(),
                    description.strip(),
                    expiry_date.strip() if expiry_date else None,
                    1 if is_favorite else 0,
                    ocr_text,
                    file_size,
                ),
            )
            doc_id = cursor.lastrowid
        conn.close()
        return doc_id

    def get_document(self, doc_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a single document owned by the specified user."""
        conn = get_connection()
        cursor = conn.execute(
            "SELECT * FROM documents WHERE id = ? AND user_id = ?",
            (doc_id, user_id),
        )
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_user_documents(
        self,
        user_id: int,
        category: Optional[str] = None,
        favorites_only: bool = False,
        sort_by: str = "created_at_desc",
    ) -> List[Dict[str, Any]]:
        """Retrieve documents belonging to user with flexible filtering and sorting."""
        conn = get_connection()
        query = "SELECT * FROM documents WHERE user_id = ?"
        params: List[Any] = [user_id]

        if category and category.lower() != "all":
            query += " AND category = ?"
            params.append(category)

        if favorites_only:
            query += " AND is_favorite = 1"

        # Sorting rules
        sort_map = {
            "created_at_desc": " ORDER BY created_at DESC",
            "created_at_asc": " ORDER BY created_at ASC",
            "title_asc": " ORDER BY title COLLATE NOCASE ASC",
            "title_desc": " ORDER BY title COLLATE NOCASE DESC",
            "expiry_asc": " ORDER BY CASE WHEN expiry_date IS NULL OR expiry_date = '' THEN 1 ELSE 0 END, expiry_date ASC",
        }
        query += sort_map.get(sort_by, " ORDER BY created_at DESC")

        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def toggle_favorite(self, doc_id: int, user_id: int) -> bool:
        """Toggle favorite status for a document."""
        conn = get_connection()
        with conn:
            cursor = conn.execute(
                """
                UPDATE documents
                SET is_favorite = 1 - is_favorite, updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND user_id = ?
                """,
                (doc_id, user_id),
            )
            updated = cursor.rowcount > 0
        conn.close()
        return updated

    def update_document(self, doc_id: int, user_id: int, **kwargs) -> bool:
        """Update metadata fields for an existing document."""
        allowed_fields = {"title", "category", "tags", "description", "expiry_date", "is_favorite", "ocr_text"}
        updates = []
        params = []
        for k, v in kwargs.items():
            if k in allowed_fields:
                updates.append(f"{k} = ?")
                if k == "is_favorite":
                    params.append(1 if v else 0)
                elif k == "expiry_date" and v:
                    params.append(v.strip())
                elif isinstance(v, str):
                    params.append(v.strip())
                else:
                    params.append(v)

        if not updates:
            return False

        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.extend([doc_id, user_id])
        sql = f"UPDATE documents SET {', '.join(updates)} WHERE id = ? AND user_id = ?"

        conn = get_connection()
        with conn:
            cursor = conn.execute(sql, params)
            success = cursor.rowcount > 0
        conn.close()
        return success

    def delete_document(self, doc_id: int, user_id: int) -> Optional[str]:
        """Delete a document record and return its encrypted file path for cleanup."""
        doc = self.get_document(doc_id, user_id)
        if not doc:
            return None
        conn = get_connection()
        with conn:
            conn.execute("DELETE FROM documents WHERE id = ? AND user_id = ?", (doc_id, user_id))
        conn.close()
        return doc["encrypted_path"]

    def get_dashboard_stats(self, user_id: int) -> Dict[str, Any]:
        """Compute real, dynamic dashboard statistics for a user without hardcoding."""
        conn = get_connection()
        cursor = conn.cursor()

        # Total documents count
        cursor.execute("SELECT COUNT(*) FROM documents WHERE user_id = ?", (user_id,))
        total_docs = cursor.fetchone()[0]

        # Favorites count
        cursor.execute("SELECT COUNT(*) FROM documents WHERE user_id = ? AND is_favorite = 1", (user_id,))
        fav_docs = cursor.fetchone()[0]

        # Grouped by category count
        cursor.execute(
            """
            SELECT category, COUNT(*) as count
            FROM documents
            WHERE user_id = ?
            GROUP BY category
            ORDER BY count DESC
            """,
            (user_id,),
        )
        category_counts = {row["category"]: row["count"] for row in cursor.fetchall()}

        # Expired and expiring within 30 days
        today_str = datetime.now().strftime("%Y-%m-%d")
        cursor.execute(
            """
            SELECT COUNT(*) FROM documents
            WHERE user_id = ? AND expiry_date IS NOT NULL AND expiry_date != '' AND expiry_date < ?
            """,
            (user_id, today_str),
        )
        expired_count = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*) FROM documents
            WHERE user_id = ? AND expiry_date IS NOT NULL AND expiry_date != ''
              AND expiry_date >= ? AND julianday(expiry_date) - julianday(?) <= 30
            """,
            (user_id, today_str, today_str),
        )
        expiring_soon_count = cursor.fetchone()[0]

        # Recently added 5 documents
        cursor.execute(
            """
            SELECT id, title, category, expiry_date, is_favorite, created_at
            FROM documents
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 5
            """,
            (user_id,),
        )
        recent_docs = [dict(r) for r in cursor.fetchall()]

        conn.close()

        return {
            "total_documents": total_docs,
            "favorite_documents": fav_docs,
            "expired_documents": expired_count,
            "expiring_soon_documents": expiring_soon_count,
            "category_counts": category_counts,
            "recent_documents": recent_docs,
        }
