"""Central Document Service coordinating repositories, encryption, and custom data structures."""

import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.data_structures.hash_table import HashTable
from app.data_structures.linked_list import RecentDocumentHistory
from app.data_structures.tree import CategoryTreeNode, build_category_tree
from app.database.category_repository import CategoryRepository
from app.database.document_repository import DocumentRepository
from app.models.document import Document
from app.services.encryption_service import EncryptionService
from app.services.expiry_service import ExpiryService
from app.services.ocr_service import OCRService
from app.services.search_service import SearchService
from app.services.viewer_service import ViewerService


class DocumentService:
    """Master coordinator for document management, security, and custom data structure indexing."""

    def __init__(self, storage_dir: str = "documents", key_path: str = "data/vault.key"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.repo = DocumentRepository()
        self.cat_repo = CategoryRepository()
        self.encryption = EncryptionService(key_path=key_path)
        self.search_service = SearchService()
        self.expiry_service = ExpiryService()
        self.ocr_service = OCRService()
        self.viewer_service = ViewerService(self.encryption)

        # Custom Data Structures integrated into the operational core:
        # 1. HashTable: Fast in-memory document caching by ID
        self.doc_cache = HashTable(initial_capacity=31)
        # 2. LinkedList: Bounded LRU-style recent document access history
        self.recent_history = RecentDocumentHistory(capacity=10)
        # 3. CategoryTree: Hierarchical category tree structure
        self.category_tree = CategoryTreeNode("Root")
        self._current_user_id: Optional[int] = None

    def sync_user_indexes(self, user_id: int) -> None:
        """Hydrate in-memory data structures (Trie, ExpiryTracker, HashTable, Tree) from DB for active user."""
        self._current_user_id = user_id
        self.search_service.clear()
        self.expiry_service.clear()
        self.doc_cache.clear()
        self.recent_history.clear()

        # Seed categories if brand new user
        self.cat_repo.ensure_default_categories(user_id)
        cat_records = self.cat_repo.get_categories(user_id)
        self.category_tree = build_category_tree(cat_records)

        # Load and index all user documents
        docs = self.repo.get_user_documents(user_id)
        for doc in docs:
            doc_id = doc["id"]
            doc_obj = Document.from_row(doc)
            # 1. Store in custom HashTable cache
            self.doc_cache.put(doc_id, doc_obj)

            # 2. Index in custom Trie for instant prefix search
            self.search_service.index_document(
                doc_id=doc_id,
                title=doc["title"],
                category=doc.get("category", ""),
                tags=doc.get("tags", ""),
                ocr_text=doc.get("ocr_text", ""),
                description=doc.get("description", ""),
            )

            # 3. Index in custom ExpiryTracker for priority expiration tracking
            if doc.get("expiry_date"):
                self.expiry_service.add_expiry(
                    doc_id,
                    doc["expiry_date"],
                    {"title": doc["title"], "category": doc.get("category")},
                )

            # 4. Update category document counts in CategoryTree
            cat_node = self.category_tree.find(doc.get("category", "General"))
            if cat_node:
                cat_node.document_count += 1

    def store_document(
        self,
        user_id: int,
        title: str,
        file_path: str,
        category: str = "General",
        tags: str = "",
        description: str = "",
        expiry_date: Optional[str] = None,
        perform_ocr: bool = True,
    ) -> int:
        """Encrypt source file, store on disk, persist metadata, and index in all data structures."""
        src = Path(file_path)
        if not src.exists():
            raise FileNotFoundError(f"Source file not found: {file_path}")

        filename = src.name
        file_size = src.stat().st_size

        # 1. Searchable Text Extraction (OCR / PDF / Text parsing)
        ocr_text = ""
        if perform_ocr:
            ocr_text = self.ocr_service.extract_text(str(src))

        # 2. Encrypt at rest into documents/ directory
        clean_title_slug = "".join(c for c in title if c.isalnum() or c in (" ", "_", "-")).strip().replace(" ", "_")
        enc_filename = f"{user_id}_{int(time.time() * 1000)}_{clean_title_slug}_{filename}.enc"
        dest_path = self.storage_dir / enc_filename
        self.encryption.encrypt_file(str(src), str(dest_path))

        # 3. SQLite Database record
        doc_id = self.repo.add_document(
            user_id=user_id,
            title=title,
            filename=filename,
            encrypted_path=str(dest_path),
            category=category,
            tags=tags,
            description=description,
            expiry_date=expiry_date,
            ocr_text=ocr_text,
            file_size=file_size,
        )

        # 4. Hydrate in-memory Document model
        doc_dict = self.repo.get_document(doc_id, user_id)
        doc_obj = Document.from_row(doc_dict)

        # 5. Populate custom Data Structures:
        # A. HashTable cache
        self.doc_cache.put(doc_id, doc_obj)
        # B. Trie search index
        self.search_service.index_document(
            doc_id=doc_id,
            title=title,
            category=category,
            tags=tags,
            ocr_text=ocr_text,
            description=description,
        )
        # C. ExpiryTracker expiration queue
        if expiry_date:
            self.expiry_service.add_expiry(doc_id, expiry_date, {"title": title, "category": category})
        # D. LinkedList access history
        self.recent_history.record_access(doc_id, title, category)
        # E. CategoryTree update
        cat_node = self.category_tree.find(category)
        if cat_node:
            cat_node.document_count += 1

        return doc_id

    def get_document(self, doc_id: int, user_id: int, record_access: bool = True) -> Optional[Dict[str, Any]]:
        """Retrieve document metadata, consulting custom HashTable cache first."""
        cached_doc: Optional[Document] = self.doc_cache.get(doc_id)
        if cached_doc and cached_doc.user_id == user_id:
            if record_access:
                self.recent_history.record_access(doc_id, cached_doc.title, cached_doc.category)
            return cached_doc.to_dict()

        # Database fallback
        doc_dict = self.repo.get_document(doc_id, user_id)
        if doc_dict:
            doc_obj = Document.from_row(doc_dict)
            self.doc_cache.put(doc_id, doc_obj)
            if record_access:
                self.recent_history.record_access(doc_id, doc_obj.title, doc_obj.category)
            return doc_dict
        return None

    def update_document(self, doc_id: int, user_id: int, **kwargs) -> bool:
        """Update document metadata across SQLite and synchronize all custom data structures."""
        success = self.repo.update_document(doc_id, user_id, **kwargs)
        if not success:
            return False

        fresh_dict = self.repo.get_document(doc_id, user_id)
        if not fresh_dict:
            return False

        fresh_doc = Document.from_row(fresh_dict)

        # 1. Synchronize custom HashTable cache
        self.doc_cache.put(doc_id, fresh_doc)

        # 2. Synchronize custom Trie: purge old entries for this doc and re-index
        self.search_service.remove_document(doc_id)
        self.search_service.index_document(
            doc_id=doc_id,
            title=fresh_doc.title,
            category=fresh_doc.category,
            tags=fresh_doc.tags,
            ocr_text=fresh_doc.ocr_text,
            description=fresh_doc.description,
        )

        # 3. Synchronize custom ExpiryTracker
        self.expiry_service.update_expiry(
            doc_id, fresh_doc.expiry_date, {"title": fresh_doc.title, "category": fresh_doc.category}
        )

        return True

    def delete_document(self, doc_id: int, user_id: int) -> bool:
        """Delete document from DB, remove encrypted file, and purge from all data structures."""
        doc = self.repo.get_document(doc_id, user_id)
        if not doc:
            return False

        enc_path = self.repo.delete_document(doc_id, user_id)
        if enc_path and Path(enc_path).exists():
            try:
                Path(enc_path).unlink()
            except Exception:
                pass

        # Synchronize custom Data Structures:
        # A. Evict from HashTable cache
        self.doc_cache.remove(doc_id)
        # B. Purge from Trie search index
        self.search_service.remove_document(doc_id)
        # C. Remove from ExpiryTracker expiry queue
        self.expiry_service.remove_expiry(doc_id)
        # D. Remove from LinkedList history
        self.recent_history.remove(doc_id)
        # E. Decrement CategoryTree count
        cat_node = self.category_tree.find(doc.get("category", "General"))
        if cat_node and cat_node.document_count > 0:
            cat_node.document_count -= 1

        return True

    def toggle_favorite(self, doc_id: int, user_id: int) -> bool:
        """Toggle favorite status in SQLite and refresh HashTable cache."""
        updated = self.repo.toggle_favorite(doc_id, user_id)
        if updated:
            cached_doc: Optional[Document] = self.doc_cache.get(doc_id)
            if cached_doc:
                cached_doc.is_favorite = not cached_doc.is_favorite
        return updated

    def search_documents(self, user_id: int, query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search documents using Trie prefix matching combined with optional category filtering."""
        clean_query = query.strip()
        if not clean_query:
            return self.repo.get_user_documents(user_id, category=category)

        # Trie search returns matching document IDs
        matching_ids = self.search_service.search(clean_query)
        if not matching_ids:
            return []

        all_user_docs = self.repo.get_user_documents(user_id, category=category)
        return [d for d in all_user_docs if d["id"] in matching_ids]

    def get_expiring_documents(self, days: int = 30) -> List[Dict[str, Any]]:
        """Retrieve upcoming expirations prioritized by the custom ExpiryTracker."""
        return self.expiry_service.get_expiring_within_days(days)

    def export_document(self, doc_id: int, user_id: int, export_dest: str) -> bool:
        """Decrypt document safely to user-specified destination path."""
        doc = self.repo.get_document(doc_id, user_id)
        if not doc:
            return False
        return self.viewer_service.export_decrypted(doc["encrypted_path"], export_dest)

    def get_decrypted_preview_path(self, doc_id: int, user_id: int) -> Optional[str]:
        """Produce a temporary plaintext file for viewing in external or native viewer."""
        doc = self.repo.get_document(doc_id, user_id)
        if not doc:
            return None
        return self.viewer_service.create_temporary_decrypted_file(
            doc["encrypted_path"], doc["filename"]
        )

    def get_dashboard_stats(self, user_id: int) -> Dict[str, Any]:
        """Return dynamic stats for dashboard display."""
        stats = self.repo.get_dashboard_stats(user_id)
        # Augment with in-memory LinkedList recent access history
        recent_accessed = self.recent_history.get_recent()
        if recent_accessed:
            stats["recently_viewed"] = recent_accessed
        return stats

    def get_categories(self, user_id: int) -> List[str]:
        """Return list of distinct categories available to the user."""
        records = self.cat_repo.get_categories(user_id)
        if not records:
            self.cat_repo.ensure_default_categories(user_id)
            records = self.cat_repo.get_categories(user_id)
        return [r["name"] for r in records]
