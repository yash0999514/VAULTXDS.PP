"""Main Application Window with clean, user-friendly labels and Notion-inspired design."""

from typing import Callable, Dict, Any, Optional
from app.database.auth_repository import AuthRepository
from app.services.document_service import DocumentService
from app.ui.add_document_dialog import AddDocumentDialog
from app.ui.common import UITheme
from app.ui.document_details_dialog import DocumentDetailsDialog
from app.ui.documents_page import DocumentsPage
from app.ui.expiry_page import ExpiryPage
from app.ui.favorites_page import FavoritesPage
from app.ui.home_page import HomePage
from app.ui.search_page import SearchPage
from app.ui.settings_page import SettingsPage
from app.ui.tech_info_page import TechInfoPage
from app.ui.tk_compat import tk, ttk, messagebox


class MainWindow:
    """The central desktop shell hosting friendly navigation, pages, and session lifecycle."""

    def __init__(
        self,
        user_data: Dict[str, Any],
        auth_repo: AuthRepository,
        doc_service: DocumentService,
        on_logout: Callable[[], None],
    ):
        self.user_data = user_data
        self.user_id = user_data["id"]
        self.username = user_data["username"]
        self.auth_repo = auth_repo
        self.doc_service = doc_service
        self.on_logout = on_logout

        # Synchronize in-memory user indexes
        self.doc_service.sync_user_indexes(self.user_id)

        self.root = tk.Tk()
        self.root.title(f"VAULTX — Secure Document Management System [{self.username}]")
        self.root.geometry("1160x760")
        self.root.minsize(1020, 640)
        self.root.configure(bg=UITheme.BG_LIGHT)

        self._center_window()

        self.active_page = "home"
        self.pages: Dict[str, Any] = {}

        self._build_shell()
        self.navigate("home")

    def _center_window(self):
        self.root.update_idletasks()
        w = 1160
        h = 760
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{max(0, x)}+{max(0, y)}")

    def _build_shell(self):
        # 1. Top Header Bar
        self.header = tk.Frame(self.root, bg=UITheme.SURFACE_LIGHT, height=58, relief="solid", bd=1)
        self.header.pack(fill="x", side="top")
        self.header.pack_propagate(False)

        # Brand Badge Pill
        brand_frame = tk.Frame(self.header, bg=UITheme.SURFACE_LIGHT)
        brand_frame.pack(side="left", padx=20, pady=10)

        tk.Label(
            brand_frame, text="🔒", font=(UITheme.FONT_FAMILY, 14),
            bg=UITheme.SURFACE_LIGHT
        ).pack(side="left", padx=(0, 6))

        tk.Label(
            brand_frame, text="VAULTX", font=(UITheme.FONT_FAMILY, 14, "bold"),
            fg=UITheme.BRAND_NAVY, bg=UITheme.SURFACE_LIGHT
        ).pack(side="left")

        sub_pill = tk.Label(
            brand_frame, text="Personal Document Vault", font=UITheme.FONT_SMALL,
            fg=UITheme.PRIMARY, bg=UITheme.PRIMARY_LIGHT, padx=8, pady=2
        )
        sub_pill.pack(side="left", padx=(10, 0))

        # Right Controls: Add Document, User Profile Pill, Logout
        right_frame = tk.Frame(self.header, bg=UITheme.SURFACE_LIGHT)
        right_frame.pack(side="right", padx=20, pady=10)

        # Prominent Add Document Button
        btn_add = tk.Button(
            right_frame, text="+ Add Document", font=UITheme.FONT_BODY_BOLD,
            bg=UITheme.PRIMARY, fg="white", activebackground=UITheme.PRIMARY_HOVER, activeforeground="white",
            relief="flat", cursor="hand2", padx=14, pady=5, command=self.open_add_dialog
        )
        btn_add.pack(side="left", padx=(0, 14))

        # User Profile Pill
        user_pill = tk.Frame(right_frame, bg=UITheme.SURFACE_ALT, padx=10, pady=4, relief="solid", bd=1)
        user_pill.pack(side="left", padx=(0, 10))

        tk.Label(user_pill, text="👤", font=UITheme.FONT_SMALL, bg=UITheme.SURFACE_ALT).pack(side="left", padx=(0, 4))
        tk.Label(
            user_pill, text=self.username, font=UITheme.FONT_SMALL_BOLD,
            fg=UITheme.TEXT_MAIN, bg=UITheme.SURFACE_ALT
        ).pack(side="left")

        # Sign Out Button
        btn_logout = tk.Button(
            right_frame, text="Sign Out", font=UITheme.FONT_SMALL,
            bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MUTED, activebackground=UITheme.DANGER_BG, activeforeground=UITheme.DANGER,
            relief="solid", bd=1, cursor="hand2", padx=10, pady=4, command=self._handle_logout
        )
        btn_logout.pack(side="left")

        # 2. Middle Body: Left Sidebar + Central Dynamic Container
        middle = tk.Frame(self.root, bg=UITheme.BG_LIGHT)
        middle.pack(fill="both", expand=True)

        self._build_sidebar(middle)

        self.content_container = tk.Frame(middle, bg=UITheme.BG_LIGHT)
        self.content_container.pack(side="left", fill="both", expand=True)

        # 3. Clean, Non-Technical Bottom Status Bar
        self._build_statusbar()

    def _build_sidebar(self, parent: tk.Frame):
        sidebar = tk.Frame(parent, bg=UITheme.SIDEBAR_BG, width=230)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Main Navigation Section
        tk.Label(
            sidebar, text="MAIN MENU", font=(UITheme.FONT_FAMILY, 8, "bold"),
            fg=UITheme.TEXT_ON_DARK_MUTED, bg=UITheme.SIDEBAR_BG, padx=22
        ).pack(anchor="w", pady=(18, 8))

        # Non-Technical Friendly Navigation Labels:
        # Dashboard → Home
        # All Documents → My Documents
        # Prefix Search → Search Documents
        # Favorites → Favorites
        # Expiry Tracker → Expiring Documents
        nav_items = [
            ("home", "🏠", "Home"),
            ("documents", "📁", "My Documents"),
            ("search", "🔍", "Search Documents"),
            ("favorites", "⭐", "Favorites"),
            ("expiry", "⏰", "Expiring Documents"),
        ]

        self.nav_buttons: Dict[str, tk.Button] = {}
        for page_id, icon, label in nav_items:
            btn = tk.Button(
                sidebar, text=f"  {icon}   {label}", font=UITheme.FONT_BODY, anchor="w",
                bg=UITheme.SIDEBAR_BG, fg=UITheme.TEXT_ON_DARK,
                activebackground=UITheme.SIDEBAR_ACTIVE, activeforeground="white",
                relief="flat", cursor="hand2", padx=16, pady=9,
                command=lambda pid=page_id: self.navigate(pid)
            )
            btn.pack(fill="x", padx=10, pady=1)
            self.nav_buttons[page_id] = btn

        # General Section
        tk.Label(
            sidebar, text="MORE", font=(UITheme.FONT_FAMILY, 8, "bold"),
            fg=UITheme.TEXT_ON_DARK_MUTED, bg=UITheme.SIDEBAR_BG, padx=22
        ).pack(anchor="w", pady=(20, 8))

        # Tech & Data Structures → About VAULTX
        # Settings & Security → Settings & Security
        more_items = [
            ("tech_info", "ℹ️", "About VAULTX"),
            ("settings", "⚙️", "Settings & Security"),
        ]

        for page_id, icon, label in more_items:
            btn = tk.Button(
                sidebar, text=f"  {icon}   {label}", font=UITheme.FONT_BODY, anchor="w",
                bg=UITheme.SIDEBAR_BG, fg=UITheme.TEXT_ON_DARK,
                activebackground=UITheme.SIDEBAR_ACTIVE, activeforeground="white",
                relief="flat", cursor="hand2", padx=16, pady=9,
                command=lambda pid=page_id: self.navigate(pid)
            )
            btn.pack(fill="x", padx=10, pady=1)
            self.nav_buttons[page_id] = btn

    def _build_statusbar(self):
        status_bar = tk.Frame(self.root, bg=UITheme.SURFACE_LIGHT, height=28, relief="solid", bd=1)
        status_bar.pack(fill="x", side="bottom")

        # Friendly non-technical status line as requested
        lbl_status = tk.Label(
            status_bar,
            text="🟢 VAULTX is ready  ·  Your documents are protected.",
            font=UITheme.FONT_SMALL,
            fg=UITheme.TEXT_MUTED,
            bg=UITheme.SURFACE_LIGHT,
            padx=16,
            pady=3,
        )
        lbl_status.pack(side="left")

        lbl_user = tk.Label(
            status_bar,
            text=f"Signed in as {self.username}",
            font=UITheme.FONT_SMALL,
            fg=UITheme.TEXT_MUTED,
            bg=UITheme.SURFACE_LIGHT,
            padx=16,
        )
        lbl_user.pack(side="right")

    def navigate(self, page_id: str):
        """Switch active page and update sidebar highlight."""
        if page_id == "add_dialog":
            self.open_add_dialog()
            return

        self.active_page = page_id

        # Update sidebar styling
        for pid, btn in self.nav_buttons.items():
            if pid == page_id:
                btn.configure(
                    bg=UITheme.PRIMARY,
                    fg="white",
                    font=UITheme.FONT_BODY_BOLD,
                )
            else:
                btn.configure(
                    bg=UITheme.SIDEBAR_BG,
                    fg=UITheme.TEXT_ON_DARK,
                    font=UITheme.FONT_BODY,
                )

        # Clear container
        for child in self.content_container.winfo_children():
            child.pack_forget()

        # Route to selected page
        if page_id == "home":
            page = HomePage(
                self.content_container,
                self.user_id,
                self.doc_service,
                nav_callback=self.navigate,
                open_doc_callback=self.open_document_details,
            )
            page.frame.pack(fill="both", expand=True)
            self.pages["home"] = page

        elif page_id == "documents":
            page = DocumentsPage(
                self.content_container,
                self.user_id,
                self.doc_service,
                open_doc_callback=self.open_document_details,
                add_doc_callback=self.open_add_dialog,
            )
            page.frame.pack(fill="both", expand=True)
            self.pages["documents"] = page

        elif page_id == "search":
            page = SearchPage(
                self.content_container,
                self.user_id,
                self.doc_service,
                open_doc_callback=self.open_document_details,
            )
            page.frame.pack(fill="both", expand=True)
            self.pages["search"] = page

        elif page_id == "favorites":
            page = FavoritesPage(
                self.content_container,
                self.user_id,
                self.doc_service,
                open_doc_callback=self.open_document_details,
            )
            page.frame.pack(fill="both", expand=True)
            self.pages["favorites"] = page

        elif page_id == "expiry":
            page = ExpiryPage(
                self.content_container,
                self.user_id,
                self.doc_service,
                open_doc_callback=self.open_document_details,
            )
            page.frame.pack(fill="both", expand=True)
            self.pages["expiry"] = page

        elif page_id == "tech_info":
            page = TechInfoPage(
                self.content_container,
            )
            page.frame.pack(fill="both", expand=True)
            self.pages["tech_info"] = page

        elif page_id == "settings":
            page = SettingsPage(
                self.content_container,
                self.user_data,
                self.auth_repo,
                self.doc_service,
            )
            page.frame.pack(fill="both", expand=True)
            self.pages["settings"] = page

    def open_add_dialog(self):
        """Launch Add Document modal."""
        AddDocumentDialog(
            parent=self.root,
            user_id=self.user_id,
            doc_service=self.doc_service,
            on_document_added=self._on_data_mutated,
        )

    def open_document_details(self, doc_id: int):
        """Launch Document Details modal for the given document ID."""
        DocumentDetailsDialog(
            parent=self.root,
            doc_id=doc_id,
            user_id=self.user_id,
            doc_service=self.doc_service,
            on_updated=self._on_data_mutated,
            on_deleted=self._on_data_mutated,
        )

    def _on_data_mutated(self):
        """Called whenever a document is added, edited, or deleted to refresh active view."""
        self.doc_service.sync_user_indexes(self.user_id)
        if self.active_page in self.pages:
            self.navigate(self.active_page)

    def _handle_logout(self):
        confirm = messagebox.askyesno("Sign Out", "Are you sure you want to sign out of your vault?", parent=self.root)
        if confirm:
            self.root.destroy()
            self.on_logout()

    def start(self):
        self.root.mainloop()
