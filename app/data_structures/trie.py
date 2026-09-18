"""Prefix Tree (Trie) for instantaneous prefix matching, search suggestions, and full-text keyword indexing.

Academic Specifications:
- Time Complexity:
  - Insert: O(L) where L is the length of the word.
  - Search / Prefix Query: O(P) where P is the length of the prefix.
  - Autocomplete: O(P + K) where K is the number of nodes in the prefix subtree.
  - Document Deletion: O(N * L) where N is the total vocabulary count.
- Space Complexity: O(ALPHABET_SIZE * L * N).
"""

import re
from typing import Dict, List, Optional, Set


class TrieNode:
    """A node in the Trie representing a single character and associated matching document IDs."""

    def __init__(self):
        self.children: Dict[str, "TrieNode"] = {}
        self.is_end_of_word: bool = False
        self.document_ids: Set[int] = set()


class Trie:
    """Trie structure mapping text prefixes to sets of document IDs with autocomplete support."""

    def __init__(self):
        self.root = TrieNode()

    @staticmethod
    def _sanitize(text: str) -> List[str]:
        """Tokenize text into lowercase alphanumeric words."""
        if not text:
            return []
        return re.findall(r"\w+", text.lower())

    def insert(self, word: str, doc_id: int) -> None:
        """Index a word and associate it with a specific document ID in O(L) time."""
        clean_word = word.strip().lower()
        if not clean_word:
            return
        node = self.root
        for char in clean_word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
            node.document_ids.add(doc_id)
        node.is_end_of_word = True

    def insert_text(self, text: str, doc_id: int) -> None:
        """Tokenizes an entire title, tag string, category, or OCR block and indexes each word."""
        for word in self._sanitize(text):
            self.insert(word, doc_id)

    def search_prefix(self, prefix: str) -> Set[int]:
        """Return all document IDs that have tokens starting with the given prefix in O(P) time."""
        clean_prefix = prefix.strip().lower()
        if not clean_prefix:
            return set()
        node = self.root
        for char in clean_prefix:
            if char not in node.children:
                return set()
            node = node.children[char]
        return set(node.document_ids)

    def autocomplete(self, prefix: str, max_results: int = 6) -> List[str]:
        """Return alphabetical word suggestions matching the given prefix."""
        clean_prefix = prefix.strip().lower()
        if not clean_prefix:
            return []
        node = self.root
        for char in clean_prefix:
            if char not in node.children:
                return []
            node = node.children[char]

        results: List[str] = []

        def _dfs(curr_node: TrieNode, path: str):
            if len(results) >= max_results:
                return
            if curr_node.is_end_of_word:
                results.append(path)
            for ch, child_node in sorted(curr_node.children.items()):
                _dfs(child_node, path + ch)

        _dfs(node, clean_prefix)
        return results

    def remove_document(self, doc_id: int) -> int:
        """Purge a document ID from all Trie nodes to ensure strict synchronization on document deletion."""
        purged_count = 0

        def _clean_node(node: TrieNode) -> bool:
            nonlocal purged_count
            if doc_id in node.document_ids:
                node.document_ids.remove(doc_id)
                purged_count += 1

            # Recursively clean children
            to_remove = []
            for char, child in list(node.children.items()):
                _clean_node(child)
                # If child has no documents and no children, prune the node
                if not child.document_ids and not child.children:
                    to_remove.append(char)

            for char in to_remove:
                del node.children[char]

            return len(node.children) == 0 and not node.document_ids

        _clean_node(self.root)
        return purged_count

    def get_stats(self) -> Dict[str, int]:
        """Return total nodes and unique indexed words for academic exploration."""
        total_nodes = 0
        total_words = 0

        def _traverse(node: TrieNode):
            nonlocal total_nodes, total_words
            total_nodes += 1
            if node.is_end_of_word:
                total_words += 1
            for child in node.children.values():
                _traverse(child)

        _traverse(self.root)
        return {"total_nodes": total_nodes, "total_indexed_words": total_words}
