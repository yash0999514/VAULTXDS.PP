# VAULTX — Data Structures Specification & Algorithmic Analysis

This document details the genuine Computer Science Data Structures engineered for VAULTX, their algorithmic complexities, and their real-world integration in the system.

---

## 1. Prefix Tree (Trie)

### Definition
A Trie (retrieval tree) is an $m$-ary tree data structure used for storing strings where nodes correspond to common prefixes. Each node represents a single character and contains pointers to child characters along with terminal markers and payload references.

### Why it is used in VAULTX
Traditional relational database `LIKE '%keyword%'` queries require an exhaustive full-table scan ($O(N)$ string comparisons). In contrast, a Trie provides instantaneous $O(P)$ prefix lookup and instant autocomplete search suggestions as the user types, regardless of database size.

### Implementation Details (`app/data_structures/trie.py`)
- **Node Structure**:
  ```python
  class TrieNode:
      def __init__(self):
          self.children: Dict[str, "TrieNode"] = {}
          self.is_end_of_word: bool = False
          self.document_ids: Set[int] = set()
  ```
- **Tokenization**: Input sentences, titles, and OCR blocks are sanitized into lowercase alphanumeric words.
- **Set Inversion**: Every character node along a word's path stores the `document_ids` containing that prefix, allowing constant-time prefix resolution.
- **Deletion Synchronization**: `remove_document(doc_id)` traverses the Trie to purge stale document IDs and prunes orphan nodes.

### Complexity Analysis
| Operation | Average Case | Worst Case | Space Complexity |
|---|---|---|---|
| **Insert** | $O(L)$ | $O(L)$ | $O(\Sigma \cdot L \cdot N)$ |
| **Prefix Search** | $O(P)$ | $O(P)$ | $O(1)$ auxiliary |
| **Autocomplete** | $O(P + K)$ | $O(P + K)$ | $O(K)$ results |
| **Document Removal** | $O(V \cdot L)$ | $O(V \cdot L)$ | $O(1)$ |

*(Where $L$ is word length, $P$ is prefix length, $K$ is number of descendant nodes in subtree, $V$ is vocabulary size).*

---

## 2. Custom Hash Table (Separate Chaining)

### Definition
A Hash Table maps arbitrary keys to values using a hashing function to compute an index into an array of buckets. Collisions are resolved using **Separate Chaining**, where each bucket points to a Linked List of key-value pairs.

### Why it is used in VAULTX
Used inside `DocumentService` as an in-memory document cache. Once a document is fetched from SQLite, it is cached in `HashTable` under `doc_id`. Subsequent reads hit the cache in $O(1)$ average time, bypassing disk I/O.

### Implementation Details (`app/data_structures/hash_table.py`)
- **Bucket Array**: Initialized to 31 buckets (prime number to distribute hashes evenly).
- **Hash Function**:
  ```python
  def _hash(self, key: Any) -> int:
      return abs(hash(str(key))) % self.capacity
  ```
- **Separate Chaining**: Each bucket is an instance of `LinkedList`.
- **Dynamic Resizing**: When load factor $\alpha = \frac{N}{M} \ge 0.75$, the table capacity is doubled ($2M + 1$) and all entries are rehashed to maintain $O(1)$ performance.
- **Diagnostic API**: Exposes bucket distribution, occupied bucket count, and collision metrics for educational analysis.

### Complexity Analysis
| Operation | Average Case | Worst Case (all keys collide) | Space Complexity |
|---|---|---|---|
| **Insert / Put** | $O(1)$ | $O(N)$ | $O(M + N)$ |
| **Lookup / Get** | $O(1)$ | $O(N)$ | $O(1)$ |
| **Delete / Remove** | $O(1)$ | $O(N)$ | $O(1)$ |

---

## 3. Doubly Linked List & Bounded LRU History

### Definition
A Linked List is a linear collection of data elements whose order is not given by their physical placement in memory. Instead, each node points to its next and previous neighbors.

### Why it is used in VAULTX
VAULTX maintains a bounded **Recent Document Access History** (`RecentDocumentHistory`). When a user views or edits a document, it is moved or inserted at the Head of the list. When capacity (e.g. 10 items) is reached, the oldest item at the Tail is evicted in $O(1)$ time.

### Implementation Details (`app/data_structures/linked_list.py`)
- **Node**:
  ```python
  class Node:
      def __init__(self, key, value):
          self.key = key
          self.value = value
          self.prev = None
          self.next = None
  ```
- **Operations**:
  - `insert()`: Prepends to `head` in $O(1)$ time.
  - `append()`: Appends to `tail` in $O(1)$ time.
  - `delete()`: Unlinks node pointers in $O(1)$ time once node is located.
  - `__iter__()`: Yields `(key, value)` tuples in chronological access order.

### Complexity Analysis
| Operation | Time Complexity | Space Complexity |
|---|---|---|
| **Insert at Head** | $O(1)$ | $O(1)$ |
| **Evict from Tail** | $O(1)$ | $O(1)$ |
| **Search by Key** | $O(N)$ | $O(1)$ |
| **Total Memory** | $O(K)$ bounded | $O(K)$ |

---

## 4. Category Tree (Hierarchical Tree)

### Definition
A tree is an acyclic connected graph where each child node has exactly one parent, starting from a single Root node.

### Why it is used in VAULTX
Personal documents naturally organize into taxonomic hierarchies:
```
Root
├── Academic & Certificates
│   ├── Transcripts
│   └── Degree Certificates
├── Identity & Legal
│   ├── Passports
│   └── Licenses
└── Finance & Tax
```
The Category Tree maintains this hierarchy in memory, supports path resolution (`Personal / Identity`), and tracks document count per subtree.

### Implementation Details (`app/data_structures/tree.py`)
- **Node**:
  ```python
  class CategoryTreeNode:
      def __init__(self, name, category_id=None, parent=None):
          self.name = name
          self.category_id = category_id
          self.parent = parent
          self.children = []
          self.document_count = 0
  ```
- **Path Resolution**: `get_full_path()` recursively traverses `parent` up to root in $O(D)$ time.
- **Visualizer**: `render_ascii_tree()` produces an ASCII branch diagram for display in technical overviews and console summaries.

### Complexity Analysis
| Operation | Time Complexity | Space Complexity |
|---|---|---|
| **Add Child Node** | $O(B)$ branching factor | $O(1)$ |
| **Find Node by Name** | $O(N)$ total nodes | $O(D)$ recursion stack |
| **Path Traversal** | $O(D)$ tree depth | $O(D)$ |
