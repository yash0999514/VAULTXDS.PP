"""Custom Hash Table implementation with separate chaining collision resolution.

Academic Specifications:
- Time Complexity (Average): O(1) for Insert, Search, and Delete.
- Time Complexity (Worst): O(N) when all keys hash to the same bucket.
- Space Complexity: O(M + N), where M is bucket count and N is total entries.
- Collision Resolution: Separate chaining via Doubly-Linked Lists.
- Dynamic Resizing: Rehashes to 2*Capacity + 1 when load factor >= 0.75.
"""

from typing import Any, Dict, Iterator, List, Optional, Tuple
from app.data_structures.linked_list import LinkedList


class HashTable:
    """A generic key-value store using separate chaining for high-performance in-memory caching."""

    def __init__(self, initial_capacity: int = 31, load_factor_threshold: float = 0.75):
        self.capacity = initial_capacity
        self.load_factor_threshold = load_factor_threshold
        self.size = 0
        self.buckets: List[LinkedList] = [LinkedList() for _ in range(self.capacity)]

    def _hash(self, key: Any) -> int:
        """Hash key using Python's built-in hash combined with capacity modulo."""
        return abs(hash(str(key))) % self.capacity

    @property
    def load_factor(self) -> float:
        """Calculate current load factor (alpha = N / M)."""
        return self.size / self.capacity if self.capacity > 0 else 0.0

    def put(self, key: Any, value: Any) -> None:
        """Insert or update a key-value pair, triggering a resize if load factor exceeds threshold."""
        if (self.size + 1) / self.capacity >= self.load_factor_threshold:
            self._resize()

        idx = self._hash(key)
        bucket = self.buckets[idx]
        initial_len = len(bucket)
        bucket.insert(key, value)
        if len(bucket) > initial_len:
            self.size += 1

    def get(self, key: Any, default: Optional[Any] = None) -> Optional[Any]:
        """Retrieve value by key in O(1) average time."""
        idx = self._hash(key)
        val = self.buckets[idx].find(key)
        return val if val is not None else default

    def remove(self, key: Any) -> bool:
        """Delete key from hash table in O(1) average time."""
        idx = self._hash(key)
        if self.buckets[idx].delete(key):
            self.size -= 1
            return True
        return False

    def contains(self, key: Any) -> bool:
        """Check if key exists in table."""
        return self.get(key) is not None

    def keys(self) -> List[Any]:
        """Return list of all keys."""
        return [k for k, _ in self]

    def values(self) -> List[Any]:
        """Return list of all values."""
        return [v for _, v in self]

    def items(self) -> List[Tuple[Any, Any]]:
        """Return list of all (key, value) pairs."""
        return list(self)

    def clear(self) -> None:
        """Reset hash table to initial empty state."""
        self.buckets = [LinkedList() for _ in range(self.capacity)]
        self.size = 0

    def _resize(self) -> None:
        """Double table capacity and rehash all active entries."""
        old_buckets = self.buckets
        self.capacity = self.capacity * 2 + 1
        self.buckets = [LinkedList() for _ in range(self.capacity)]
        self.size = 0
        for bucket in old_buckets:
            for k, v in bucket:
                self.put(k, v)

    def get_diagnostics(self) -> Dict[str, Any]:
        """Return statistical diagnostic data for academic demonstrations."""
        bucket_lengths = [len(b) for b in self.buckets]
        collisions = sum(max(0, length - 1) for length in bucket_lengths)
        occupied_buckets = sum(1 for length in bucket_lengths if length > 0)
        max_bucket_depth = max(bucket_lengths) if bucket_lengths else 0

        return {
            "capacity": self.capacity,
            "size": self.size,
            "load_factor": round(self.load_factor, 4),
            "occupied_buckets": occupied_buckets,
            "empty_buckets": self.capacity - occupied_buckets,
            "total_collisions": collisions,
            "max_chain_depth": max_bucket_depth,
            "bucket_lengths": bucket_lengths,
        }

    def __getitem__(self, key: Any) -> Any:
        val = self.get(key)
        if val is None:
            raise KeyError(f"Key '{key}' not found in HashTable.")
        return val

    def __setitem__(self, key: Any, value: Any) -> None:
        self.put(key, value)

    def __delitem__(self, key: Any) -> None:
        if not self.remove(key):
            raise KeyError(f"Key '{key}' not found in HashTable.")

    def __contains__(self, key: Any) -> bool:
        return self.contains(key)

    def __len__(self) -> int:
        return self.size

    def __iter__(self) -> Iterator[Tuple[Any, Any]]:
        for bucket in self.buckets:
            for k, v in bucket:
                yield (k, v)
