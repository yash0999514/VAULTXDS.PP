"""Search service integrating custom Trie prefix tree for multi-field search and autocomplete."""

from typing import Any, Dict, List, Optional, Set
from app.data_structures.trie import Trie


class SearchService:
    """Provides fast tokenized prefix and multi-keyword search backed by a custom Trie."""

    def __init__(self):
        self.trie = Trie()

    def index_document(
        self,
        doc_id: int,
        title: str,
        category: str = "",
        tags: str = "",
        ocr_text: str = "",
        description: str = "",
    ) -> None:
        """Tokenize and index all document metadata fields into the Trie."""
        if title:
            self.trie.insert_text(title, doc_id)
        if category:
            self.trie.insert_text(category, doc_id)
        if tags:
            self.trie.insert_text(tags, doc_id)
        if description:
            self.trie.insert_text(description, doc_id)
        if ocr_text:
            # Index first 2000 chars of OCR text to keep in-memory footprint optimal
            self.trie.insert_text(ocr_text[:2000], doc_id)

    def remove_document(self, doc_id: int) -> int:
        """Purge document from Trie index when deleted or updated."""
        return self.trie.remove_document(doc_id)

    def search(self, query: str) -> Set[int]:
        """Search across all indexed fields using tokenized prefix queries with set intersection (AND)."""
        tokens = query.strip().split()
        if not tokens:
            return set()

        result_ids = self.trie.search_prefix(tokens[0])
        for token in tokens[1:]:
            result_ids &= self.trie.search_prefix(token)
            if not result_ids:
                break
        return result_ids

    def autocomplete(self, prefix: str, max_results: int = 6) -> List[str]:
        """Return keyword autocomplete suggestions for user search queries."""
        return self.trie.autocomplete(prefix, max_results=max_results)

    def clear(self) -> None:
        """Reset search index."""
        self.trie = Trie()
