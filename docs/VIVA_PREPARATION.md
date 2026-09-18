# VAULTX — College Practical Examination & Viva Preparation Guide

**Subject**: Python Programming & Advanced Data Structures  
**Project Title**: VAULTX — Secure Personal Document Management System  
**Target Platform**: Windows Desktop (Python 3.11 / Tkinter / ttkbootstrap / SQLite)

---

## 1. Project Introduction & Overview

**VAULTX** is a secure, offline-first personal document management desktop application. It enables individuals to safely store, categorize, search, track, and export critical personal and academic documents (such as marksheets, identity cards, certificates, and tax records). 

Unlike standard cloud storage apps that require internet connectivity and expose data to external servers, VAULTX operates entirely offline on the local machine, applying authenticated AES-128-CBC encryption at rest, secure salted password derivation, and in-memory Computer Science Data Structures (Trie, Hash Table, Linked List, and Category Tree) to deliver high-performance search and priority tracking.

---

## 2. Key Objectives & Problem Statement

### Problem Statement
Students and professionals store sensitive personal documents (diploma marksheets, passport copies, insurance policies) scattered across unencrypted local folders, downloads, or messaging apps. This presents two major risks:
1. **Security Vulnerabilities**: Plaintext files are readable by any unauthorized local user or malware.
2. **Poor Organization & Missed Deadlines**: Finding documents by keywords is slow, and critical expiry dates (e.g. driving licenses, cert validity, policies) pass unnoticed.

### Objectives
- Provide **confidentiality at rest** using authenticated Fernet encryption.
- Ensure **instant searchability** across metadata and OCR text using an in-memory **Trie**.
- Provide **reliable deadline tracking** using chronological date sorting.
- Provide **in-memory caching** using a custom **Hash Table** and **LRU Linked List**.
- Feature a clean, modern **Technology & Data Structures** overview page detailing the software's engineering.

---

## 3. Object-Oriented Programming (OOP) Concepts Used

| OOP Concept | Where it is used in VAULTX | Explanation |
|---|---|---|
| **Encapsulation** | `EncryptionService`, `HashTable`, `Trie` | Internal details (e.g. cipher keys, raw array indices, bucket arrays) are kept private behind clean public methods like `encrypt_file()`, `get()`, `search_prefix()`. |
| **Separation of Concerns** | UI $\rightarrow$ Services $\rightarrow$ Repositories $\rightarrow$ SQLite | UI widgets never make raw SQL calls; Repositories never manage UI widgets. |
| **Composition** | `DocumentService` has a `SearchService`, `ExpiryService`, `HashTable`, etc. | Aggregates multiple specialized data structures and services to orchestrate complex document workflows. |
| **Data Modeling** | `Document` dataclass (`app/models/document.py`) | Strongly typed, immutable record representations that safely deserialize from SQLite rows. |
| **Polymorphism & Duck Typing** | `HashTable` and `LinkedList` implementing `__len__`, `__iter__`, `__getitem__` | Custom data structures integrate seamlessly with Python's native iterator and collection protocols. |

---

## 4. Summary of Data Structures Used

```
┌─────────────────┬───────────────────────────────┬───────────────────────────┬───────────────────────┐
│ Data Structure  │ Feature in VAULTX             │ Primary Advantage         │ Time Complexity       │
├─────────────────┼───────────────────────────────┼───────────────────────────┼───────────────────────┤
│ Trie (Prefix)   │ Search Engine & Autocomplete  │ Instant prefix matching   │ O(P) search, O(L) ins │
│ Hash Table      │ In-Memory Document Cache      │ O(1) primary key lookup   │ O(1) avg insert/find  │
│ Linked List     │ Recent Access History (LRU)   │ O(1) head insert/evict    │ O(1) head/tail ops    │
│ Category Tree   │ Hierarchical Classification   │ Multi-tier breadcrumbs    │ O(B) add, O(D) path   │
└─────────────────┴───────────────────────────────┴───────────────────────────┴───────────────────────┘
```

---

## 5. Top 30 Viva Questions & Model Answers

### General & Architecture
**Q1: What is the main purpose of VAULTX?**  
*Answer*: VAULTX is a secure, offline-first personal document management desktop application that encrypts sensitive files on disk, organizes them hierarchically, indexes them using custom data structures, and alerts users of upcoming expirations.

**Q2: Why is the project designed offline-first?**  
*Answer*: Security and privacy. By operating offline without third-party cloud APIs, the user's sensitive documents and master encryption keys never traverse the network or sit on external servers.

**Q3: What architecture pattern does VAULTX follow?**  
*Answer*: A 4-tier layered architecture: Presentation Layer (Tkinter/ttkbootstrap UI), Service Layer (Business logic and DS synchronization), Repository Layer (Data Access Objects), and Persistence Layer (SQLite + encrypted file storage).

**Q4: How does the application prevent cross-user data access?**  
*Answer*: Every document row in the database has a `user_id` foreign key. All repository queries require `WHERE user_id = ?` parameters, strictly isolating each user's records.

---

### Data Structures Deep Dive
**Q5: Why did you use a Trie instead of SQLite `LIKE '%keyword%'` for search?**  
*Answer*: A relational `LIKE '%query%'` query with a leading wildcard cannot use standard B-Tree indexes and requires a slow $O(N)$ full table scan. A Trie provides instantaneous prefix lookup in $O(P)$ time (proportional only to the length of the prefix), and easily supports real-time autocomplete suggestions via Depth-First Search.

**Q6: How does the Trie handle multiple search keywords like "marksheet diploma"?**  
*Answer*: The `SearchService` splits the query into tokens, queries the Trie for each token's set of matching `document_ids`, and performs a set intersection ($S_1 \cap S_2$). Only documents containing all keywords are returned.

**Q7: How is the Trie kept synchronized when a document is deleted?**  
*Answer*: We implemented `remove_document(doc_id)` in the Trie. It recursively traverses nodes, removes the `doc_id` from each node's document set, and prunes any empty child branches.

**Q8: What collision resolution strategy does your custom Hash Table use?**  
*Answer*: Separate Chaining. Each bucket in the hash table contains a custom Doubly-Linked List. When two distinct keys hash to the same bucket index, the key-value pair is appended or updated within that bucket's linked list.

**Q9: What is the load factor in a Hash Table, and when does VAULTX resize?**  
*Answer*: The load factor is $\alpha = \frac{N}{M}$, where $N$ is the number of elements and $M$ is the bucket capacity. When $\alpha \ge 0.75$, `HashTable._resize()` doubles the capacity ($2M + 1$) and rehashes all entries to prevent performance degradation.

**Q10: Why is the Hash Table used for document caching?**  
*Answer*: Once a document is fetched from the database, it is cached in `doc_cache` (HashTable). Subsequent accesses (e.g. clicking View Details or editing tags) retrieve the document object in $O(1)$ average time without initiating a disk I/O query.

**Q11: How is the Linked List utilized in VAULTX?**  
*Answer*: It is used in two places:
1. As the collision bucket chain in the `HashTable`.
2. As a bounded LRU-style recent access history (`RecentDocumentHistory`). When a user views a document, it is moved to the head in $O(1)$ time, and if the list exceeds capacity (10 items), the tail item is evicted in $O(1)$ time.

**Q12: Why is a Doubly-Linked List preferred over a Singly-Linked List for LRU history?**  
*Answer*: A Doubly-Linked List maintains pointers to both `prev` and `next`, enabling $O(1)$ unlinking of any node when moving it to the head or deleting from the tail, provided we hold a reference to the node.

**Q13: How does the Category Tree organize document categories?**  
*Answer*: The `CategoryTreeNode` class models a general tree with parent and children pointers. It supports hierarchical subcategories (e.g. `Academic / Marksheets`), calculates breadcrumb paths in $O(D)$ depth, and computes document counts per subtree.

**Q14: How does the Category Tree synchronize with SQLite?**  
*Answer*: The `categories` table in SQLite stores `(id, user_id, name, parent_id)`. When the user logs in, `build_category_tree()` traverses these rows to reconstruct the full tree in memory.

---

### Database & SQL
**Q15: What database engine is used and why?**  
*Answer*: SQLite 3. It is embedded directly in Python via the `sqlite3` standard library, requires zero server setup, is ACID compliant, stores data in a single file (`data/vaultx.db`), and supports foreign keys and transactions.

**Q16: Why is `PRAGMA foreign_keys = ON;` necessary in SQLite?**  
*Answer*: SQLite disables foreign key enforcement by default for backward compatibility. Executing this PRAGMA on every connection ensures cascading deletes work (`ON DELETE CASCADE`), deleting associated records when a user or parent category is removed.

**Q17: How do you prevent SQL Injection in VAULTX?**  
*Answer*: By using parameterized SQL queries with `?` placeholders for all user inputs (e.g., `cursor.execute("SELECT * FROM users WHERE username = ?", (username,))`), ensuring that inputs are treated strictly as literal data, never executable SQL code.

**Q18: What indexes did you create and why?**  
*Answer*:
- `idx_docs_user` on `documents(user_id)` for quick user scoping.
- `idx_docs_expiry` on `documents(expiry_date)` for fast date filtering.
- `idx_docs_fav` on `documents(user_id, is_favorite)` for fast favorites list retrieval.
- `idx_docs_category` on `documents(user_id, category)` for fast category filtering.

---

### Cybersecurity & Encryption
**Q19: How are stored documents encrypted?**  
*Answer*: Using the **Fernet** specification from Python's `cryptography` library. Fernet uses 128-bit AES in Cipher Block Chaining (CBC) mode with PKCS7 padding, authenticated using HMAC with SHA-256 to ensure ciphertext integrity.

**Q20: Why is AES-CBC combined with an HMAC?**  
*Answer*: Authenticated encryption prevents tampering. AES-CBC encrypts the data for confidentiality, while HMAC-SHA256 signs the ciphertext. If an attacker modifies even a single bit of the file on disk, Fernet detects the invalid HMAC and raises `InvalidToken`, preventing decryption of corrupted data.

**Q21: How are user passwords stored?**  
*Answer*: Passwords are never stored in plaintext. We use **PBKDF2** (Password-Based Key Derivation Function 2) with **HMAC-SHA256**, a unique 16-byte random salt per user, and 100,000 iterations to resist brute-force and dictionary attacks.

**Q22: Why is a salt necessary in password hashing?**  
*Answer*: A salt ensures that even if two users choose identical passwords, their stored hashes will be completely different, preventing precomputed Rainbow Table attacks.

**Q23: How do you prevent timing attacks during password authentication?**  
*Answer*: We compare hashes in constant time using `hashlib.sha256(computed).digest() == hashlib.sha256(stored).digest()`, ensuring that comparison time does not leak information about how many initial characters matched.

**Q24: Where is the master encryption key stored?**  
*Answer*: In `data/vault.key` with restricted operating system read permissions. In production environments, this can be integrated with Windows DPAPI or TPM hardware modules.

---

### Practical Demonstration & Engineering
**Q25: What happens if Tesseract OCR is not installed on the system?**  
*Answer*: The application degrades gracefully. `OCRService` checks `pytesseract` and `PIL` availability at runtime. If unavailable, it notifies the user, extracts text from plain files and PDFs via `pypdf`, and avoids crashing.

**Q26: What happens when an encrypted file is corrupted or tampered with?**  
*Answer*: When `EncryptionService.decrypt_file()` detects an altered ciphertext or invalid HMAC signature, it catches `InvalidToken` and raises a clean, descriptive `DecryptionError`, protecting the application from crashes.

**Q27: How does the application handle documents without an expiry date?**  
*Answer*: In the database, `expiry_date` is stored as `NULL`. In the Expiry Tracker and dashboard, documents without expiry dates are not flagged as expiring, and display "None" in tables.

**Q28: How does the Technology & Data Structures page work?**  
*Answer*: It is an informative card-based documentation screen in the UI that explains Python's role in the architecture (GUI, Services, SQLite, Cryptography, Search, OCR) and provides real-world explanations and complexities for the four genuine data structures used in the project.

**Q29: What are the current limitations of VAULTX?**  
*Answer*:
1. Currently a single-machine desktop application; no cloud sync.
2. OCR text extraction depends on the local installation of Tesseract OCR for image scanning.
3. Master key is currently stored locally in `data/vault.key`.

**Q30: What is the future scope of the project?**  
*Answer*:
1. Windows DPAPI integration to tie key storage directly to the Windows user login credential.
2. Biometric authentication (Windows Hello / fingerprint scanning).
3. Automated cloud backup with zero-knowledge client-side encryption.
4. Mobile companion app using Flutter with end-to-end encrypted sync.
