"""Doubly and Singly Linked List implementations.

Used for:
1. Separate chaining buckets in custom HashTable.
2. Bounded Recent Document Access & Navigation History with O(1) head insertion and tail eviction.
"""

from typing import Any, Iterator, List, Optional, Tuple


class Node:
    """A node in a linked list holding key, value, and bidirectional pointers."""

    def __init__(self, key: Any, value: Any):
        self.key = key
        self.value = value
        self.prev: Optional["Node"] = None
        self.next: Optional["Node"] = None

    def __repr__(self) -> str:
        return f"Node({self.key}: {self.value})"


class LinkedList:
    """Doubly Linked List supporting insertion, lookup, deletion, and iteration."""

    def __init__(self):
        self.head: Optional[Node] = None
        self.tail: Optional[Node] = None
        self._size: int = 0

    def insert(self, key: Any, value: Any) -> None:
        """Insert or update a key-value pair at the head of the list."""
        current = self.head
        while current:
            if current.key == key:
                current.value = value
                return
            current = current.next

        # New key: prepend to head
        new_node = Node(key, value)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node
        self._size += 1

    def append(self, key: Any, value: Any) -> None:
        """Append a key-value pair to the tail of the list."""
        new_node = Node(key, value)
        if self.tail is None:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            new_node.prev = self.tail
            self.tail = new_node
        self._size += 1

    def find(self, key: Any) -> Optional[Any]:
        """Find value associated with key in O(N) time."""
        current = self.head
        while current:
            if current.key == key:
                return current.value
            current = current.next
        return None

    def delete(self, key: Any) -> bool:
        """Delete a node by key in O(N) search and O(1) unlinking."""
        current = self.head
        while current:
            if current.key == key:
                if current.prev:
                    current.prev.next = current.next
                else:
                    self.head = current.next

                if current.next:
                    current.next.prev = current.prev
                else:
                    self.tail = current.prev

                self._size -= 1
                return True
            current = current.next
        return False

    def to_list(self) -> List[Tuple[Any, Any]]:
        """Return list of (key, value) tuples."""
        return [(k, v) for k, v in self]

    def clear(self) -> None:
        """Clear all nodes."""
        self.head = None
        self.tail = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Iterator[Tuple[Any, Any]]:
        current = self.head
        while current:
            yield (current.key, current.value)
            current = current.next


class RecentDocumentHistory:
    """Bounded LRU-style Linked List tracking recently opened documents in O(1) time."""

    def __init__(self, capacity: int = 10):
        self.capacity = capacity
        self.list = LinkedList()

    def record_access(self, doc_id: int, title: str, category: str = "General") -> None:
        """Record document access by moving or inserting at the head."""
        # If already present, delete old occurrence
        self.list.delete(doc_id)
        # Prepend to head
        self.list.insert(doc_id, {"title": title, "category": category})
        # Evict oldest tail item if capacity exceeded
        if len(self.list) > self.capacity and self.list.tail:
            oldest_key = self.list.tail.key
            self.list.delete(oldest_key)

    def get_recent(self) -> List[dict]:
        """Return list of recently accessed document items from newest to oldest."""
        return [{"doc_id": k, **v} for k, v in self.list]

    def remove(self, doc_id: int) -> bool:
        """Remove document from history when deleted."""
        return self.list.delete(doc_id)

    def clear(self) -> None:
        self.list.clear()

    def __len__(self) -> int:
        return len(self.list)
