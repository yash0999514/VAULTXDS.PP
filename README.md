# 🔒 VAULTX — Secure Personal Document Management System

[![Python Version](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Academic%20Evaluation-green.svg)]()
[![Platform](https://img.shields.io/badge/Platform-Windows%20Desktop-lightgrey.svg)]()
[![Security](https://img.shields.io/badge/Encryption-AES--128--CBC%20%2B%20HMAC--SHA256-red.svg)]()

> **Academic Project Submission**: Python Programming & Advanced Data Structures  
> **Topic**: Secure Offline-First Personal Document Manager with Custom Algorithmic Data Structures

---

## 📖 1. Project Overview

**VAULTX** is a secure, offline-first personal document management desktop application designed for Windows. It provides authenticated users with a private encrypted vault to store, categorize, search, track, and export vital documents (such as academic marksheets, degree certificates, passports, government IDs, insurance policies, and tax returns).

VAULTX features custom Computer Science Data Structures (Prefix Tree Trie, Hash Table with Separate Chaining, Doubly Linked List with LRU Eviction, and Hierarchical Category Trees) that directly power the core features of the software.

---

## 🎯 2. Problem Statement & Key Features

### The Problem
Sensitive personal documents are commonly scattered in unencrypted folders, email attachments, and messaging apps. This leads to severe security risks (unencrypted access by unauthorized users or malware) and missed renewal deadlines (expired driving licenses, passports, or insurance policies).

### Core Features
- **🔒 AES-128-CBC Authenticated Encryption**: Document contents are encrypted at rest using the Fernet specification. Plaintext files never persist on disk unencrypted.
- **🛡️ Salted PBKDF2 Authentication**: Passwords hashed with HMAC-SHA256 using unique 16-byte random salts and 100,000 rounds.
- **🔍 Instant Trie Prefix Search**: Custom Prefix Tree indexes document titles, categories, tags, and OCR text for instantaneous search and live autocomplete suggestions.
- **⏰ Chronological Expiry Tracker**: Reliable date-sorted deadline tracker with visual status badges (`EXPIRED`, `URGENT`, `WARNING`, `ACTIVE`).
- **⚡ In-Memory Hash Table Cache**: Custom separate-chaining Hash Table caches document models in RAM for $O(1)$ instantaneous retrieval by ID.
- **🕒 Bounded LRU Access History**: Doubly-Linked List records recently viewed documents with $O(1)$ head insertion and tail eviction.
- **📁 Hierarchical Category Tree**: Multi-level document organization with automatic path resolution.
- **📄 OCR & Searchable Text Extraction**: Automatic text extraction from PDFs and images via Tesseract OCR and PyPDF.
- **🧠 Technology & Data Structures Information Page**: Modern card-based technical documentation screen explaining Python architecture and algorithmic complexities.

---

## 🛠️ 3. Technologies Used

- **Language**: Python 3.11+
- **Desktop GUI**: Tkinter & `ttkbootstrap` (Modern Windows styling inspired by Notion and Linear)
- **Database**: SQLite 3 (ACID-compliant relational database with foreign keys)
- **Cryptography**: `cryptography` (Fernet specification / AES-128-CBC with HMAC-SHA256)
- **Document OCR / Parsing**: `pypdf`, `Pillow`, `pytesseract`

---

## 📂 4. Project Directory Structure

```
VAULTX/
│
├── app/
│   ├── data_structures/          # Genuine Computer Science Data Structures
│   │   ├── __init__.py
│   │   ├── hash_table.py         # Custom Separate-Chaining Hash Table & Cache
│   │   ├── linked_list.py        # Doubly Linked List & Bounded LRU History
│   │   ├── tree.py               # Hierarchical Category Tree
│   │   └── trie.py               # Prefix Tree with Autocomplete & Deletion Sync
│   │
│   ├── database/                 # SQLite Persistence Layer
│   │   ├── __init__.py
│   │   ├── auth_repository.py    # PBKDF2 Password Hashing & Authentication
│   │   ├── category_repository.py# Category CRUD Operations
│   │   ├── connection.py         # Thread-safe SQLite Connection Provider
│   │   ├── document_repository.py# Parameterized Document CRUD & Analytics
│   │   └── schema.py             # DDL Schema Creation & Non-Destructive Migrations
│   │
│   ├── models/                   # Strongly Typed Data Models
│   │   ├── __init__.py
│   │   └── document.py           # Document Dataclass
│   │
│   ├── services/                 # Business Logic Tier
│   │   ├── __init__.py
│   │   ├── document_service.py   # Central Coordinator uniting DB & Data Structures
│   │   ├── encryption_service.py # Fernet File & Byte Encryption at Rest
│   │   ├── expiry_service.py     # Chronological Date Deadline Tracking
│   │   ├── ocr_service.py        # PDF & Image Searchable Text Extraction
│   │   ├── search_service.py     # Trie Prefix & Keyword Indexing
│   │   └── viewer_service.py     # Secure In-Memory Decryption & Export
│   │
│   ├── ui/                       # Desktop Presentation Layer (Notion/Linear Inspired)
│   │   ├── __init__.py
│   │   ├── add_document_dialog.py# Add Document Modal with File Picker
│   │   ├── auth_screen.py        # AuthWindow alias
│   │   ├── auth_window.py        # Login & Registration Card
│   │   ├── common.py             # UI Theme, Fonts, Colors, Formatting
│   │   ├── document_details_dialog.py # View, Decrypt, Edit, & Export Dialog
│   │   ├── documents_page.py     # Documents Table, Filtering, & Actions
│   │   ├── expiry_page.py        # Date-Sorted Expiry Tracker
│   │   ├── favorites_page.py     # Starred Documents Manager
│   │   ├── home_page.py          # Dashboard Overview with Dynamic Metrics
│   │   ├── search_page.py        # Trie Prefix Search Engine
│   │   ├── settings_page.py      # Security Info, Key Fingerprint, Backup
│   │   ├── tech_info_page.py     # Technology & Data Structures Information Page
│   │   └── tk_compat.py          # Tkinter / Headless Compatibility Layer
│   │
│   └── main.py                   # Central Application Controller
│
├── data/                         # Persistent Storage (SQLite & Master Keys)
│   ├── vault.key                 # Generated 256-bit Master Key
│   └── vaultx.db                 # SQLite Relational Database
│
├── documents/                    # Encrypted Document Ciphertext Files (.enc)
│
├── docs/                         # Academic Evaluation & Technical Documentation
│   ├── ARCHITECTURE.md           # 4-Tier System Architecture & Data Flows
│   ├── DATA_STRUCTURES.md        # Algorithmic Complexity & DS Walkthroughs
│   ├── DATABASE.md               # SQLite Schema, Constraints, & Indexes
│   └── VIVA_PREPARATION.md       # Top 30 Viva Questions & Comprehensive Answers
│
├── tests/                        # Automated Test Suite (11 Comprehensive Tests)
│   ├── __init__.py
│   ├── test_data_structures.py   # Unit Tests for Genuine Custom Data Structures
│   ├── test_ui_components.py     # UI Import & Layout Contract Tests
│   └── test_vaultx_features.py   # End-to-End Integration Tests
│
├── requirements.txt              # Production Dependencies
├── run.py                        # Primary Executable Startup Script
└── README.md                     # Comprehensive Project Guide
```

---

## 🚀 5. Installation & Setup Instructions (Windows)

### Prerequisites
- Python 3.11 or newer installed from [python.org](https://www.python.org/).  
  *(Make sure to check the box **"Add python.exe to PATH"** during installation).*

### Step 1: Extract the Project Folder
Extract the `VAULTX` archive into your desired folder (e.g. `C:\Projects\VAULTX`).

### Step 2: Open Command Prompt or PowerShell in the Folder
```powershell
cd C:\Projects\VAULTX
```

### Step 3: Create and Activate a Python Virtual Environment
```powershell
python -m venv .venv
.venv\Scripts\activate
```

### Step 4: Install Dependencies
```powershell
pip install -r requirements.txt
```

---

## 🖥️ 6. How to Run the Application

### Option A: Standard Windows Desktop GUI
Run the main startup script:
```powershell
python run.py
```
- **Login Screen**: Click **"⚡ Quick College Demo Login (student)"** or register a new user account.
- **Dashboard**: Explore real-time statistics cards, category breakdown, upcoming expirations, and recent history.
- **Add Document**: Click **"+ Add Document"** in the top bar to upload and encrypt any PDF, image, or text file.
- **Prefix Search**: Navigate to the **Prefix Search** tab to test Trie autocomplete suggestions.
- **Expiry Tracker**: View documents prioritized chronologically by expiry date.
- **Technology & Data Structures**: Open the **Tech & Data Structures** tab to view the architectural breakdown and algorithmic complexity cards.

### Option B: Interactive CLI Demonstration Mode
If running in a terminal, via SSH, or during a quick practical exam demonstration without opening the full desktop window:
```powershell
python run.py --cli
```

---

## 🧪 7. Running the Automated Test Suite

To run the complete automated test suite:
```powershell
python -m unittest discover -s tests
```
Output:
```
Ran 11 tests in 2.753s

OK
```

---

## 🛡️ 8. Security Architecture & Cryptographic Model

1. **Authenticated Encryption at Rest**:
   - Every file uploaded is encrypted using the **Fernet** authenticated symmetric cipher specification (`AES-128-CBC` with PKCS7 padding and `HMAC-SHA256` integrity signing).
   - Tampered or corrupted ciphertext files are automatically detected via HMAC validation, preventing malicious payloads or data corruption.
2. **Master Key Management**:
   - Master keys are cryptographically generated using `os.urandom(32)` and saved in `data/vault.key` with restricted access permissions.
3. **Password Security**:
   - Plaintext passwords are never stored. The system derives salted password hashes using **PBKDF2-HMAC-SHA256** with 100,000 iterations and 16-byte random salts.
   - Hash comparisons utilize constant-time verification to eliminate timing attack vectors.

---

## 📜 9. Academic Evaluation Material

For detailed viva preparation notes, complexity breakdowns, and architectural diagrams, refer to the documentation files in the `docs/` folder:
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)**: Layered architecture, component responsibilities, and execution data flows.
- **[docs/DATA_STRUCTURES.md](docs/DATA_STRUCTURES.md)**: Mathematical complexity and custom data structure implementations.
- **[docs/DATABASE.md](docs/DATABASE.md)**: SQLite relational schema, indexing, and migration strategies.
- **[docs/VIVA_PREPARATION.md](docs/VIVA_PREPARATION.md)**: Top 30 college viva questions and comprehensive model answers.
