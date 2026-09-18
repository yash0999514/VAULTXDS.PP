# VAULTX — System Architecture & Design Documentation

## 1. Architectural Overview

VAULTX is structured as a layered, modular, offline-first desktop application engineered in Python 3.11+. The architecture strictly enforces Separation of Concerns (SoC) across four distinct vertical tiers:

```
┌─────────────────────────────────────────────────────────────┐
│                 Presentation Layer (UI)                     │
│  - Tkinter / ttkbootstrap modern Windows desktop frames     │
│  - MainWindow, AuthWindow, HomePage, DocumentsPage, etc.    │
│  - Technology & Data Structures Information Page            │
└──────────────────────────────┬──────────────────────────────┘
                               │ (Calls Services)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   Service Layer (Business)                  │
│  - DocumentService (Master Coordinator)                     │
│  - SearchService (Custom Trie Prefix Engine)                │
│  - ExpiryService (Chronological Date Sorting Tracker)       │
│  - EncryptionService (Fernet AES-128-CBC + HMAC-SHA256)     │
│  - OCRService (Tesseract & PyPDF text extraction)           │
│  - ViewerService (Secure In-Memory Decryption & Export)     │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
               │ (Cache & Indexes)            │ (Data Persistence)
               ▼                              ▼
┌──────────────────────────────┐  ┌───────────────────────────┐
│ In-Memory Data Structures    │  │ Repository Layer          │
│ - HashTable (Document Cache) │  │ - AuthRepository          │
│ - Trie (Search Index)        │  │ - DocumentRepository      │
│ - LinkedList (LRU History)   │  │ - CategoryRepository      │
│ - CategoryTree (Hierarchy)   │  │                           │
└──────────────────────────────┘  └─────────────┬─────────────┘
                                                │
                                                ▼
                                  ┌───────────────────────────┐
                                  │ Persistence Layer         │
                                  │ - SQLite (data/vaultx.db) │
                                  │ - Encrypted Files (docs/) │
                                  │ - Master Key (vault.key)  │
                                  └───────────────────────────┘
```

---

## 2. Component Responsibilities

### Presentation Layer (`app/ui/`)
- **`tk_compat.py`**: Provides seamless runtime abstraction across Windows desktop environments (standard Tkinter + ttkbootstrap) and headless/test environments.
- **`auth_window.py` & `auth_screen.py`**: Manages credential capture, input validation, salted PBKDF2 authentication, and session handoff.
- **`main_window.py`**: Hosts navigation sidebar, user badge, active view routing, top action bar, and status bar.
- **`home_page.py`**: Dashboard displaying dynamic metrics (total docs, favorites, categories), recent LRU history, and urgent upcoming expirations.
- **`documents_page.py`**: Document table with category dropdown filtering, title sorting, favorite toggles, and metadata inspection.
- **`add_document_dialog.py`**: File chooser, metadata inputs, tags, expiry date validation, category selector, and automatic OCR trigger.
- **`document_details_dialog.py`**: Tabbed viewer presenting metadata, decrypted in-memory plaintext/OCR preview, metadata modification, and safe decrypted export.
- **`search_page.py`**: Live Trie-powered search bar with instant autocomplete suggestions and token-intersection search.
- **`expiry_page.py`**: Date-sorted expiry tracker with visual status alerts (`EXPIRED`, `URGENT`, `WARNING`, `ACTIVE`).
- **`favorites_page.py`**: Dedicated manager for starred documents.
- **`settings_page.py`**: Displays cryptographic key fingerprint, cipher algorithm, password reset form, and database backup utility.
- **`tech_info_page.py`**: Technology & Data Structures information page offering an architectural overview of Python modules and the four genuine data structures used in the application.

### Service Layer (`app/services/`)
- **`document_service.py`**: Central coordinator. When documents are stored, updated, or deleted, it persists data in SQLite and synchronizes all in-memory data structures (HashTable, Trie, LinkedList, CategoryTree).
- **`encryption_service.py`**: Symmetric authenticated encryption using the Fernet specification. Handles byte-level and file-level encryption/decryption at rest.
- **`search_service.py`**: Maintains the custom Trie index. Tokenizes text and executes set intersection across token prefixes.
- **`expiry_service.py`**: Maintains date-based deadline tracking. Converts ISO expiry strings into Unix timestamps and orders items chronologically.
- **`ocr_service.py`**: Extracts text from PDFs and scanned images using PyPDF and Tesseract OCR with graceful fallback if binaries are missing.
- **`viewer_service.py`**: Decrypts documents into memory or isolated temporary files for preview, guaranteeing cleanup on process exit.

### Repository Layer (`app/database/`)
- **`connection.py`**: Manages thread-safe SQLite connections with `PRAGMA foreign_keys = ON;` and fallback handling.
- **`schema.py`**: Creates tables, constraints, and indexes, running idempotent non-destructive migrations.
- **`auth_repository.py`**: Implements salted PBKDF2-HMAC-SHA256 password hashing and offline verification.
- **`document_repository.py`**: Handles parameterized CRUD operations and real-time dashboard aggregation queries.
- **`category_repository.py`**: Manages user-defined category hierarchies.

---

## 3. Core Workflows

### A. Authentication Flow
1. User enters username and password in `AuthWindow`.
2. `AuthRepository` queries `users` by username.
3. Salt is extracted and combined with input password through 100,000 iterations of PBKDF2-HMAC-SHA256.
4. The derived hash is compared against the stored hash in constant time (`hashlib.sha256().digest()`).
5. On match, session payload `{"id": user_id, "username": username}` is dispatched to `MainWindow`.

### B. Document Storage & Encryption Flow
1. User selects a local file and enters title, category, tags, notes, and expiry date in `AddDocumentDialog`.
2. `OCRService` parses plain text, PDF pages, or image OCR text.
3. `EncryptionService` generates a unique 128-bit IV, encrypts file bytes with master key via AES-128-CBC, appends HMAC-SHA256 signature, and writes `documents/{user_id}_{timestamp}_{filename}.enc`.
4. `DocumentRepository` executes parameterized `INSERT INTO documents (...)`.
5. In-Memory Data Structures are updated:
   - `HashTable`: Caches `Document` model under `doc_id`.
   - `Trie`: Tokenizes and indexes title, category, tags, notes, and OCR text.
   - `ExpiryService`: Records expiry date for chronological deadline tracking.
   - `CategoryTree`: Increments document count for target category.

### C. Search Flow (Trie Prefix Engine)
1. User types in search bar on `SearchPage`.
2. As user types, `SearchService.autocomplete(prefix)` performs DFS from prefix node in Trie to return suggestions.
3. Upon submit, query is split into whitespace tokens (e.g. `['diplo', 'sem']`).
4. For each token, `Trie.search_prefix(token)` traverses character edges in $O(P)$ time to retrieve matching document IDs.
5. Sets of matching IDs are intersected ($S_1 \cap S_2$).
6. Documents corresponding to resultant IDs are returned.

### D. Expiry Tracking Flow
1. On startup or login, documents with expiry dates are loaded into `ExpiryService`.
2. Deadlines are evaluated relative to current time: $(\text{expiry\_date} - \text{today})$.
3. `ExpiryService.get_expiring_within_days(days)` filters deadlines and sorts items chronologically.
4. UI classifies items:
   - Days < 0: 🔴 Expired
   - Days $\le$ 7: 🟠 Urgent
   - Days $\le$ 30: 🟡 Warning
   - Days > 30: 🟢 Active
