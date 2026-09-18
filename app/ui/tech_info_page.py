"""About VAULTX Information Page.

Presents a clear system overview for general users alongside a dedicated
technical and algorithmic architecture section for academic college evaluation.
"""

from app.ui.common import UITheme
from app.ui.tk_compat import tk, ttk


class TechInfoPage:
    """Displays user-friendly project details and academic data structure specifications."""

    def __init__(self, parent: tk.Frame):
        self.parent = parent
        self.frame = tk.Frame(self.parent, bg=UITheme.BG_LIGHT, padx=28, pady=22)
        self._build_ui()

    def _build_ui(self):
        # Header section
        header = tk.Frame(self.frame, bg=UITheme.BG_LIGHT)
        header.pack(fill="x", pady=(0, 15))

        tk.Label(
            header,
            text="ℹ️ About VAULTX",
            font=UITheme.FONT_DISPLAY,
            bg=UITheme.BG_LIGHT,
            fg=UITheme.TEXT_MAIN,
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Overview of your document vault, privacy guarantees, and software architecture.",
            font=UITheme.FONT_SMALL,
            bg=UITheme.BG_LIGHT,
            fg=UITheme.TEXT_MUTED,
        ).pack(anchor="w", pady=(3, 0))

        # Notebook tabs
        notebook = ttk.Notebook(self.frame)
        notebook.pack(fill="both", expand=True)

        self.tab_overview = tk.Frame(notebook, bg=UITheme.SURFACE_LIGHT)
        self.tab_ds = tk.Frame(notebook, bg=UITheme.SURFACE_LIGHT)
        self.tab_python = tk.Frame(notebook, bg=UITheme.SURFACE_LIGHT)

        notebook.add(self.tab_overview, text="   System Overview   ")
        notebook.add(self.tab_ds, text="   Data Structures (Academic)   ")
        notebook.add(self.tab_python, text="   Python Architecture   ")

        self._build_overview_tab()
        self._build_ds_tab()
        self._build_python_tab()

    def _build_overview_tab(self):
        canvas = tk.Canvas(self.tab_overview, bg=UITheme.SURFACE_LIGHT, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.tab_overview, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=UITheme.SURFACE_LIGHT, padx=20, pady=15)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Welcome Card
        welcome_card = tk.Frame(scrollable_frame, bg=UITheme.SURFACE_LIGHT, relief="solid", bd=1, padx=20, pady=16)
        welcome_card.pack(fill="x", pady=(0, 15))

        tk.Label(
            welcome_card,
            text="🔒 VAULTX: Secure Personal Document Management System",
            font=UITheme.FONT_SUBTITLE,
            bg=UITheme.SURFACE_LIGHT,
            fg=UITheme.PRIMARY,
        ).pack(anchor="w", pady=(0, 6))

        tk.Label(
            welcome_card,
            text="VAULTX is a secure personal document manager built for Windows. It provides you with a safe, organized place to store and track sensitive files such as academic marksheets, degree certificates, government IDs, insurance policies, and tax documents.",
            font=UITheme.FONT_BODY,
            bg=UITheme.SURFACE_LIGHT,
            fg=UITheme.TEXT_MAIN,
            wraplength=760,
            justify="left",
        ).pack(anchor="w", pady=(0, 8))

        # Highlights Grid
        pillars = [
            ("🛡️ 100% Offline & Private", "Your documents stay entirely on your computer. No cloud accounts, no tracking, and no external servers."),
            ("🔒 Secured at Rest", "Every file you upload is protected so that unauthorized local users or other software cannot read your sensitive information."),
            ("🔍 Instant Search", "Search documents by name, category, or tags with live suggestions as you type."),
            ("⏰ Deadline Tracking", "Keep track of renewal deadlines for driving licenses, insurance cards, and certificates with clear advance notices."),
        ]

        for title, desc in pillars:
            p_card = tk.Frame(scrollable_frame, bg=UITheme.SURFACE_LIGHT, relief="solid", bd=1, padx=18, pady=12)
            p_card.pack(fill="x", pady=(0, 10))
            tk.Label(p_card, text=title, font=UITheme.FONT_SUBTITLE, bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MAIN).pack(anchor="w", pady=(0, 3))
            tk.Label(p_card, text=desc, font=UITheme.FONT_BODY, bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MUTED, wraplength=760, justify="left").pack(anchor="w")

    def _build_ds_tab(self):
        canvas = tk.Canvas(self.tab_ds, bg=UITheme.SURFACE_LIGHT, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.tab_ds, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=UITheme.SURFACE_LIGHT, padx=20, pady=15)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Academic Introduction Banner
        banner = tk.Frame(scrollable_frame, bg="#eff6ff", relief="solid", bd=1, padx=16, pady=12)
        banner.pack(fill="x", pady=(0, 16))
        tk.Label(
            banner,
            text="Algorithmic Data Structures Implementation",
            font=UITheme.FONT_SUBTITLE,
            bg="#eff6ff",
            fg=UITheme.PRIMARY,
        ).pack(anchor="w")
        tk.Label(
            banner,
            text="VAULTX implements custom in-memory data structures in Python to deliver fast search, instant caching, and LRU navigation without relying solely on database queries.",
            font=UITheme.FONT_BODY,
            bg="#eff6ff",
            fg=UITheme.TEXT_MAIN,
            wraplength=780,
            justify="left",
        ).pack(anchor="w", pady=(4, 0))

        # 4 Genuine Data Structures Cards
        structures = [
            (
                "🗄️ Custom Hash Table (Separate Chaining)",
                "In-Memory Document Caching (DocumentService.doc_cache)",
                "Provides instantaneous O(1) average-time lookups for stored documents by their integer ID, eliminating repetitive SQLite disk queries during active sessions. Resolves collisions using Doubly Linked Lists and automatically doubles capacity when load factor α ≥ 0.75.",
                "When viewing document details, 'doc_cache.get(doc_id)' locates the cached Document dataclass in O(1) time without running an SQL SELECT query.",
                "O(1) Average Insert / Lookup / Delete",
                UITheme.PRIMARY,
            ),
            (
                "🔗 Doubly Linked List (Bounded LRU History)",
                "Recent Document Access History (RecentDocumentHistory)",
                "Maintains a chronological, bounded record of recently viewed files. Because each node maintains bidirectional pointers ('prev' and 'next'), items can be moved or prepended to the Head in O(1) time, and the oldest item at the Tail can be evicted in O(1) time when capacity is reached.",
                "Opening 'Diploma Marksheet' moves its node to the Head of the history list. After opening 10 subsequent documents, the oldest tail item is automatically evicted in O(1) time without list re-indexing.",
                "O(1) Head Insertion  |  O(1) Tail Eviction",
                "#059669",
            ),
            (
                "🌲 Prefix Tree (Trie)",
                "Full-Text Keyword Search & Live Autocomplete (SearchService.trie)",
                "Replaces slow SQL 'LIKE %keyword%' table scans with an m-ary character tree. Each node stores matching document IDs and child character pointers. Words in titles, categories, tags, and text are tokenized and inserted into the Trie for fast prefix lookup and auto-suggestions.",
                "Searching for 'pass' traverses edges 'p' -> 'a' -> 's' -> 's' in O(P) time (where P is prefix length) and instantly returns document IDs for 'passport', 'passbook', and 'password'.",
                "O(P) Prefix Search  |  O(L) Word Insertion",
                "#7c3aed",
            ),
            (
                "🌳 General Category Tree",
                "Hierarchical Document Classification (CategoryTreeNode)",
                "Models multi-tier category structures with parent-child links. Allows documents to inherit organizational taxonomies and supports dynamic breadcrumb path resolution from root to leaf.",
                "A document assigned to subcategory 'Transcripts' under 'Academic' traverses parent pointers up to root to resolve the full canonical path: 'Academic & Certificates / Transcripts'.",
                "O(B) Add Child  |  O(D) Breadcrumb Path Resolution",
                "#d97706",
            ),
        ]

        for name, used_in, why, eg, complexity, accent in structures:
            self._render_ds_card(scrollable_frame, name, used_in, why, eg, complexity, accent)

    def _render_ds_card(self, parent: tk.Frame, title: str, where_used: str, why_useful: str, example: str, complexity: str, accent: str):
        card = tk.Frame(parent, bg=UITheme.SURFACE_LIGHT, relief="solid", bd=1, padx=18, pady=14)
        card.pack(fill="x", pady=(0, 14))

        top_bar = tk.Frame(card, bg=UITheme.SURFACE_LIGHT)
        top_bar.pack(fill="x", pady=(0, 6))

        tk.Label(top_bar, text=title, font=UITheme.FONT_SUBTITLE, bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MAIN).pack(side="left")
        badge = tk.Label(top_bar, text=complexity, font=UITheme.FONT_SMALL_BOLD, bg="#f1f5f9", fg=accent, padx=8, pady=2)
        badge.pack(side="right")

        row_used = tk.Frame(card, bg=UITheme.SURFACE_LIGHT)
        row_used.pack(fill="x", pady=(0, 6))
        tk.Label(row_used, text="Component: ", font=UITheme.FONT_BODY_BOLD, bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MUTED).pack(side="left")
        tk.Label(row_used, text=where_used, font=UITheme.FONT_BODY, bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MAIN).pack(side="left")

        tk.Label(card, text="Algorithmic Advantage:", font=UITheme.FONT_BODY_BOLD, bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MUTED).pack(anchor="w", pady=(2, 1))
        tk.Label(card, text=why_useful, font=UITheme.FONT_BODY, bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MAIN, wraplength=760, justify="left").pack(anchor="w", pady=(0, 6))

        tk.Label(card, text="Application Example:", font=UITheme.FONT_BODY_BOLD, bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MUTED).pack(anchor="w", pady=(2, 1))
        tk.Label(card, text=example, font=UITheme.FONT_BODY, bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MAIN, wraplength=760, justify="left").pack(anchor="w")

    def _build_python_tab(self):
        canvas = tk.Canvas(self.tab_python, bg=UITheme.SURFACE_LIGHT, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.tab_python, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=UITheme.SURFACE_LIGHT, padx=20, pady=15)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        modules = [
            ("🖥️ Desktop GUI (Tkinter & ttkbootstrap)", "Presentation Layer", "Python's native Tkinter framework combined with modern ttkbootstrap theme styling powers the desktop interface. Features nested Frame hierarchies, dynamic page containers, modal dialogs, and responsive geometry management."),
            ("⚙️ Application & Business Logic (Service-Oriented Design)", "Service Layer", "Separates business logic from presentation and database operations. DocumentService coordinates encryption, database writes, Trie indexing, HashTable caching, and LRU history updates."),
            ("🗃️ Relational Storage & Persistence (SQLite3)", "Database Layer", "Integrated via Python's standard sqlite3 module with Row factories and parameterized queries. Features automatic table creation, non-destructive schema migrations, foreign keys, and indexes."),
            ("🔒 Authenticated Cryptography (Fernet / AES-128-CBC + HMAC-SHA256)", "Security Layer", "Implements authenticated symmetric file encryption using Python's cryptography library. Files are protected at rest, while user authentication uses PBKDF2 with 100,000 salt rounds."),
            ("🔍 In-Memory Prefix Search Engine (Custom Trie)", "Search Layer", "Tokenizes document titles, categories, tags, and notes into lowercase alphanumeric keywords, executing set intersections to return multi-keyword results and live autocomplete suggestions."),
            ("📄 Document Text Extraction (PyPDF & Tesseract)", "Ingestion Layer", "Extracts searchable text from text files, PDF documents, and scanned images using PyPDF and Tesseract OCR with graceful fallback if optional tools are missing."),
        ]

        for title, role, desc in modules:
            card = tk.Frame(scrollable_frame, bg=UITheme.SURFACE_LIGHT, relief="solid", bd=1, padx=18, pady=14)
            card.pack(fill="x", pady=(0, 12))

            top = tk.Frame(card, bg=UITheme.SURFACE_LIGHT)
            top.pack(fill="x", pady=(0, 4))
            tk.Label(top, text=title, font=UITheme.FONT_SUBTITLE, bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MAIN).pack(side="left")
            tk.Label(top, text=role, font=UITheme.FONT_SMALL_BOLD, bg="#f1f5f9", fg=UITheme.PRIMARY, padx=8, pady=2).pack(side="right")

            tk.Label(card, text=desc, font=UITheme.FONT_BODY, bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MAIN, wraplength=760, justify="left").pack(anchor="w")
