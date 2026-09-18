# VAULTX — Database Schema & Storage Specification

VAULTX uses **SQLite 3** as its local relational database storage engine (`data/vaultx.db`). SQLite provides zero-configuration, robust ACID-compliant transactional persistence without requiring external database servers.

---

## 1. Relational Schema & Tables

### A. `users` Table
Stores authenticated user credentials and salted password hashes.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique user identifier |
| `username` | TEXT | UNIQUE NOT NULL | Unique login handle |
| `email` | TEXT | DEFAULT '' | Optional contact email |
| `password_hash` | TEXT | NOT NULL | 256-bit PBKDF2 HMAC-SHA256 hex string |
| `salt` | TEXT | NOT NULL | 16-byte cryptographically secure random salt hex |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |

---

### B. `documents` Table
Stores metadata for all encrypted personal documents.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique document identifier |
| `user_id` | INTEGER | NOT NULL, FK(users.id) ON DELETE CASCADE | Owning user ID |
| `title` | TEXT | NOT NULL | Human-readable document title |
| `filename` | TEXT | NOT NULL | Original unencrypted file name |
| `encrypted_path` | TEXT | NOT NULL | Path to ciphertext file on disk (`documents/*.enc`) |
| `category` | TEXT | DEFAULT 'General' | Assigned category name |
| `tags` | TEXT | DEFAULT '' | Comma-separated search tags |
| `description` | TEXT | DEFAULT '' | User notes / remarks |
| `expiry_date` | TEXT | NULL | ISO expiration date string (`YYYY-MM-DD`) |
| `is_favorite` | INTEGER | DEFAULT 0 | 1 if starred as favorite, 0 otherwise |
| `ocr_text` | TEXT | DEFAULT '' | Extracted searchable text content |
| `file_size` | INTEGER | DEFAULT 0 | Original file size in bytes |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Timestamp when document was stored |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Timestamp of last metadata edit |

---

### C. `categories` Table
Supports user-defined hierarchical category classification.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Category identifier |
| `user_id` | INTEGER | NOT NULL, FK(users.id) ON DELETE CASCADE | Owning user ID |
| `name` | TEXT | NOT NULL | Category name |
| `parent_id` | INTEGER | NULL, FK(categories.id) ON DELETE CASCADE | Parent category for hierarchy |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

---

### D. `activity_log` Table
Maintains audit logs of document operations.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Log entry identifier |
| `user_id` | INTEGER | NOT NULL, FK(users.id) ON DELETE CASCADE | User performing action |
| `action` | TEXT | NOT NULL | Action type (e.g. `STORE`, `DELETE`, `EXPORT`) |
| `document_id` | INTEGER | NULL | Related document ID |
| `details` | TEXT | DEFAULT '' | Operational remarks |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Action timestamp |

---

## 2. Performance Indexes

VAULTX establishes targeted indexes to accelerate lookups:
1. `idx_docs_user`: `CREATE INDEX idx_docs_user ON documents (user_id);`
   - Accelerates fetching all documents for a specific user session.
2. `idx_docs_expiry`: `CREATE INDEX idx_docs_expiry ON documents (expiry_date);`
   - Speeds up expiration queries and date range filtering.
3. `idx_docs_fav`: `CREATE INDEX idx_docs_fav ON documents (user_id, is_favorite);`
   - Composite index for instantaneous retrieval of starred documents.
4. `idx_docs_category`: `CREATE INDEX idx_docs_category ON documents (user_id, category);`
   - Accelerates category dropdown filtering.

---

## 3. Migration Strategy

When updating older databases without breaking existing user data, `init_database()` in `app/database/schema.py` executes non-destructive schema inspection and automated migrations:
```python
# Check for description column in documents
cursor = conn.execute("PRAGMA table_info(documents);")
columns = [row["name"] for row in cursor.fetchall()]
if "description" not in columns:
    conn.execute("ALTER TABLE documents ADD COLUMN description TEXT DEFAULT '';")
```
This guarantees forward-compatibility without data loss.
