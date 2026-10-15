VAULTX — Personal Document Management System

A Python desktop application for organizing personal documents, managing expiry dates, and protecting stored files with encryption.

"Python" (https://img.shields.io/badge/Python-3.11+-blue)
"Platform" (https://img.shields.io/badge/Platform-Windows-lightgrey)
"Database" (https://img.shields.io/badge/Database-SQLite-blue)
"GUI" (https://img.shields.io/badge/GUI-Tkinter-orange)

1. Overview

VAULTX is an offline-first document management application developed as an academic project for Python Programming and Advanced Data Structures.

The application allows users to add, organize, search, view, and manage personal documents through a desktop interface. It also includes document expiry tracking, text extraction from supported files, and encrypted document storage.

The project combines Python application development, relational database management, file handling, cryptography, and custom data structures.

2. Problem Statement

Personal documents are often stored across multiple folders and applications, making them difficult to organize and retrieve. Important documents may also have expiry dates that are easy to overlook.

VAULTX addresses these problems by providing a single application for document organization, search, and expiry tracking, with encryption intended to protect stored document contents.

3. Features

Document Management

- Add and organize documents by category.
- Store document metadata in an SQLite database.
- View document details and manage favorites.
- Filter and search documents.
- Track document expiry dates and display status indicators.
- Export documents through the application.

Search and Text Extraction

- Prefix-based search using a custom Trie implementation.
- Search indexing for supported document metadata and extracted text.
- Extract text from PDFs using PyPDF.
- Extract text from supported images using Tesseract OCR.

Security

- Encrypt document contents using the Fernet implementation provided by the Python "cryptography" library.
- Derive password hashes using PBKDF2-HMAC-SHA256 with individual salts.
- Detect invalid or corrupted encrypted tokens during decryption.
- Keep document processing and storage on the local machine in the intended offline workflow.

Security note: Actual protection depends on key storage, file permissions, temporary-file handling, and the deployment environment. VAULTX is an academic project and has not been independently security-audited.

Data Structures

The application includes custom data structure implementations for specific tasks:

Data structure| Purpose
Trie| Prefix-based document search
Hash table| In-memory document lookup and caching
Doubly linked list| Recent-document access history
Category tree| Hierarchical category organization

These implementations provide an opportunity to study how data structures can be integrated into a practical Python application.

4. Technology Stack

- Language: Python 3.11+
- Desktop interface: Tkinter and ttkbootstrap
- Database: SQLite
- Encryption: Python "cryptography" library
- PDF processing: PyPDF
- Image processing: Pillow
- OCR: Tesseract OCR with pytesseract
- Testing: Python "unittest"

5. Project Structure

VAULTX/
├── app/
│   ├── data_structures/
│   │   ├── hash_table.py
│   │   ├── linked_list.py
│   │   ├── tree.py
│   │   └── trie.py
│   ├── database/
│   │   ├── auth_repository.py
│   │   ├── category_repository.py
│   │   ├── connection.py
│   │   ├── document_repository.py
│   │   └── schema.py
│   ├── models/
│   │   └── document.py
│   ├── services/
│   │   ├── document_service.py
│   │   ├── encryption_service.py
│   │   ├── expiry_service.py
│   │   ├── ocr_service.py
│   │   ├── search_service.py
│   │   └── viewer_service.py
│   ├── ui/
│   │   ├── auth_window.py
│   │   ├── documents_page.py
│   │   ├── expiry_page.py
│   │   ├── home_page.py
│   │   ├── search_page.py
│   │   └── settings_page.py
│   └── main.py
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DATA_STRUCTURES.md
│   ├── DATABASE.md
│   └── VIVA_PREPARATION.md
├── tests/
│   ├── test_data_structures.py
│   ├── test_ui_components.py
│   └── test_vaultx_features.py
├── requirements.txt
├── run.py
└── README.md

The structure separates the user interface, application services, database operations, data models, and data structure implementations. This separation helps keep related functionality organized and makes individual components easier to test.

6. Installation

Prerequisites

- Python 3.11 or later
- Git, if cloning the repository
- Tesseract OCR installed separately if OCR functionality is required

Step 1: Get the source code

Clone the repository or extract the project archive.

git clone https://github.com/yash0999514/VAULTXDS.PP.git
cd VAULTXDS.PP

Step 2: Create a virtual environment

python -m venv .venv

Activate it on Windows:

.venv\Scripts\activate

Step 3: Install Python dependencies

python -m pip install --upgrade pip
pip install -r requirements.txt

Step 4: Run the application

python run.py

To launch the command-line demonstration mode, if supported by the current version:

python run.py --cli

7. Testing

The project includes tests for data structures, application components, authentication, and document management workflows.

Run the test suite using:

python -m unittest discover -s tests -v

Review the output to confirm which tests pass or fail in your environment. Test results can vary depending on the installed dependencies and application configuration.

8. Application Architecture

VAULTX separates its main responsibilities into the following components:

1. Presentation layer: Handles desktop screens, user interactions, and navigation.
2. Service layer: Coordinates document operations, search, encryption, expiry tracking, and text extraction.
3. Data access layer: Handles authentication, categories, document records, and SQLite operations.
4. Data structure layer: Provides custom implementations for search indexing, caching, access history, and category organization.

This organization makes it easier to modify one part of the application without placing all application logic inside the user interface.

9. Limitations and Future Improvements

Potential improvements include:

- Stronger master-key protection and a documented recovery process.
- Additional automated tests for invalid files, encryption failures, and database errors.
- Better handling of temporary decrypted files.
- Continuous integration with GitHub Actions.
- Improved logging and error reporting.
- Performance testing for search and document retrieval.
- A documented backup and restore workflow.

These improvements would help make the application more reliable and easier to maintain.

10. Learning Outcomes

Working on VAULTX provides practical experience with:

- Python modules and object-oriented programming.
- SQLite and relational data management.
- File handling and encryption APIs.
- Custom data structures and algorithmic complexity.
- Desktop GUI development.
- Automated testing and debugging.
- Separation of concerns and modular application design.

11. Project Information

Project: VAULTX — Personal Document Management System
Type: Academic desktop application
Language: Python
Primary platform: Windows
Repository: "VAULTXDS.PP on GitHub" (https://github.com/yash0999514/VAULTXDS.PP)

This project is intended for academic learning and demonstration. It should not be used to store highly sensitive documents without further security review and testing.
