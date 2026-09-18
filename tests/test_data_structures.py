"""Comprehensive Unit Tests for Genuine Custom Data Structures in VAULTX.

Covers:
1. Doubly Linked List & Bounded LRU History (LinkedList, RecentDocumentHistory)
2. Hash Table with Separate Chaining & Dynamic Resizing (HashTable)
3. Prefix Tree (Trie) with deletion synchronization & autocomplete
4. Category Tree (CategoryTreeNode, build_category_tree)
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.data_structures.linked_list import LinkedList, RecentDocumentHistory
from app.data_structures.hash_table import HashTable
from app.data_structures.trie import Trie
from app.data_structures.tree import CategoryTreeNode, build_category_tree


class TestDataStructuresComprehensive(unittest.TestCase):

    # ---------------- 1. LINKED LIST & LRU HISTORY ----------------
    def test_linked_list_crud_and_edge_cases(self):
        ll = LinkedList()
        self.assertEqual(len(ll), 0)
        self.assertEqual(ll.to_list(), [])
        self.assertFalse(ll.delete("nonexistent"))

        # Insert operations (prepend to head)
        ll.insert("k1", "v1")
        ll.insert("k2", "v2")
        self.assertEqual(len(ll), 2)
        self.assertEqual(ll.find("k1"), "v1")
        self.assertEqual(ll.find("k2"), "v2")
        self.assertIsNone(ll.find("k3"))

        # Update existing key
        ll.insert("k1", "v1_updated")
        self.assertEqual(ll.find("k1"), "v1_updated")
        self.assertEqual(len(ll), 2)

        # Append to tail
        ll.append("k3", "v3")
        self.assertEqual(len(ll), 3)
        self.assertEqual(ll.tail.key, "k3")

        # Delete head, middle, tail
        self.assertTrue(ll.delete("k2"))
        self.assertIsNone(ll.find("k2"))
        self.assertEqual(len(ll), 2)

        # Clear
        ll.clear()
        self.assertEqual(len(ll), 0)
        self.assertIsNone(ll.head)
        self.assertIsNone(ll.tail)

    def test_recent_history_lru_behavior(self):
        history = RecentDocumentHistory(capacity=3)
        self.assertEqual(len(history), 0)

        # Record accesses
        history.record_access(1, "Passport", "Identity")
        history.record_access(2, "Marksheet", "Academic")
        history.record_access(3, "Resume", "Career")
        self.assertEqual(len(history), 3)

        # Verify most recent is at index 0 (Head)
        recent = history.get_recent()
        self.assertEqual(recent[0]["doc_id"], 3)
        self.assertEqual(recent[1]["doc_id"], 2)
        self.assertEqual(recent[2]["doc_id"], 1)

        # Access existing document: moves it to head
        history.record_access(1, "Passport", "Identity")
        self.assertEqual(len(history), 3)
        self.assertEqual(history.get_recent()[0]["doc_id"], 1)

        # Exceed capacity: oldest (Doc 2) should be evicted
        history.record_access(4, "Tax Return", "Finance")
        self.assertEqual(len(history), 3)
        ids = [x["doc_id"] for x in history.get_recent()]
        self.assertIn(4, ids)
        self.assertIn(1, ids)
        self.assertIn(3, ids)
        self.assertNotIn(2, ids)

        # Explicit removal
        self.assertTrue(history.remove(4))
        self.assertEqual(len(history), 2)

    # ---------------- 2. HASH TABLE ----------------
    def test_hash_table_operations_and_resizing(self):
        ht = HashTable(initial_capacity=7, load_factor_threshold=0.75)
        self.assertEqual(len(ht), 0)
        self.assertEqual(ht.load_factor, 0.0)

        # Insert items triggering dynamic resize
        for i in range(25):
            ht.put(f"doc_{i}", f"Data {i}")
            ht[f"num_{i}"] = i * 100

        self.assertEqual(len(ht), 50)
        self.assertTrue(ht.capacity > 7)
        self.assertTrue(ht.load_factor < 0.75)

        # Verification & dict-like access
        self.assertEqual(ht.get("doc_10"), "Data 10")
        self.assertEqual(ht["num_5"], 500)
        self.assertTrue(ht.contains("doc_24"))
        self.assertIn("doc_24", ht)
        self.assertFalse(ht.contains("nonexistent"))

        # Diagnostics metrics
        diag = ht.get_diagnostics()
        self.assertEqual(diag["size"], 50)
        self.assertTrue(diag["occupied_buckets"] > 0)
        self.assertIsInstance(diag["total_collisions"], int)

        # Delete operations
        self.assertTrue(ht.remove("doc_10"))
        self.assertIsNone(ht.get("doc_10"))
        self.assertEqual(len(ht), 49)
        del ht["num_5"]
        self.assertEqual(len(ht), 48)

        # Clear
        ht.clear()
        self.assertEqual(len(ht), 0)

    # ---------------- 3. TRIE ----------------
    def test_trie_prefix_matching_and_deletion(self):
        trie = Trie()
        self.assertEqual(trie.search_prefix("test"), set())
        self.assertEqual(trie.autocomplete("test"), [])

        # Insert words
        trie.insert("passport", 1)
        trie.insert("password", 2)
        trie.insert("passbook", 3)
        trie.insert("pan", 4)

        # Prefix search
        self.assertEqual(trie.search_prefix("pass"), {1, 2, 3})
        self.assertEqual(trie.search_prefix("passb"), {3})
        self.assertEqual(trie.search_prefix("pan"), {4})
        self.assertEqual(trie.search_prefix("xyz"), set())

        # Autocomplete
        suggestions = trie.autocomplete("pass")
        self.assertIn("passport", suggestions)
        self.assertIn("password", suggestions)
        self.assertIn("passbook", suggestions)

        # Multi-word sentence indexing
        trie.insert_text("Semester 3 Engineering Marksheet Pune", 10)
        self.assertIn(10, trie.search_prefix("sem"))
        self.assertIn(10, trie.search_prefix("eng"))
        self.assertIn(10, trie.search_prefix("mark"))

        # Deletion synchronization
        trie.remove_document(1)
        self.assertEqual(trie.search_prefix("passport"), set())
        self.assertEqual(trie.search_prefix("pass"), {2, 3})

        trie.remove_document(10)
        self.assertNotIn(10, trie.search_prefix("mark"))

    # ---------------- 4. CATEGORY TREE ----------------
    def test_category_tree_hierarchy(self):
        root = CategoryTreeNode("Root")
        personal = root.add_child("Personal")
        identity = personal.add_child("Identity")
        finance = root.add_child("Finance")

        self.assertEqual(identity.get_full_path(), "Personal/Identity")
        self.assertEqual(finance.get_full_path(), "Finance")

        # Find
        found = root.find("Identity")
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "Identity")

        # List all paths
        paths = root.list_all_paths()
        self.assertIn("Personal", paths)
        self.assertIn("Personal/Identity", paths)
        self.assertIn("Finance", paths)

        # ASCII tree render check
        ascii_tree = root.render_ascii_tree()
        self.assertIn("Personal", ascii_tree)
        self.assertIn("Finance", ascii_tree)

        # Test build from database records
        records = [
            {"id": 1, "name": "Work", "parent_id": None},
            {"id": 2, "name": "Projects", "parent_id": 1},
        ]
        built_root = build_category_tree(records)
        self.assertIsNotNone(built_root.find("Projects"))


if __name__ == "__main__":
    unittest.main()
