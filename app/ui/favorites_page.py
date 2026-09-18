"""Favorites Page showing all starred documents with clean non-technical management."""

from typing import Callable, List
from app.services.document_service import DocumentService
from app.ui.common import UITheme, format_file_size, format_date
from app.ui.tk_compat import tk, ttk, messagebox


class FavoritesPage:
    """Displays user's starred favorite documents for instant access."""

    def __init__(
        self,
        parent: tk.Frame,
        user_id: int,
        doc_service: DocumentService,
        open_doc_callback: Callable[[int], None],
    ):
        self.parent = parent
        self.user_id = user_id
        self.doc_service = doc_service
        self.open_doc_callback = open_doc_callback

        self.frame = tk.Frame(self.parent, bg=UITheme.BG_LIGHT, padx=28, pady=22)
        self._build_ui()
        self.load_favorites()

    def _build_ui(self):
        header = tk.Frame(self.frame, bg=UITheme.BG_LIGHT)
        header.pack(fill="x", pady=(0, 15))

        tk.Label(
            header, text="⭐ Favorites", font=UITheme.FONT_DISPLAY,
            bg=UITheme.BG_LIGHT, fg=UITheme.TEXT_MAIN
        ).pack(anchor="w")

        tk.Label(
            header, text="Quick access to your most important starred documents.",
            font=UITheme.FONT_SMALL, bg=UITheme.BG_LIGHT, fg=UITheme.TEXT_MUTED
        ).pack(anchor="w", pady=(3, 0))

        table_frame = tk.Frame(self.frame, bg=UITheme.SURFACE_LIGHT, relief="solid", bd=1)
        table_frame.pack(fill="both", expand=True)

        columns = ("id", "title", "category", "expiry", "size", "added")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="#")
        self.tree.heading("title", text="Document Title")
        self.tree.heading("category", text="Category")
        self.tree.heading("expiry", text="Valid Until")
        self.tree.heading("size", text="File Size")
        self.tree.heading("added", text="Date Stored")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("title", width=270, anchor="w")
        self.tree.column("category", width=140, anchor="w")
        self.tree.column("expiry", width=120, anchor="center")
        self.tree.column("size", width=85, anchor="center")
        self.tree.column("added", width=120, anchor="center")

        scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", lambda e: self._on_open_selected())

        # Footer Actions
        footer = tk.Frame(self.frame, bg=UITheme.BG_LIGHT)
        footer.pack(fill="x", pady=(12, 0))

        btn_view = tk.Button(
            footer, text="🔍 View Document", font=UITheme.FONT_BODY_BOLD,
            bg=UITheme.PRIMARY, fg="white", relief="flat", cursor="hand2", padx=16, pady=7,
            command=self._on_open_selected
        )
        btn_view.pack(side="left", padx=(0, 8))

        btn_unfav = tk.Button(
            footer, text="⭐ Remove from Favorites", font=UITheme.FONT_BODY,
            bg=UITheme.SURFACE_ALT, fg=UITheme.TEXT_MAIN, relief="flat", cursor="hand2", padx=14, pady=7,
            command=self._on_remove_favorite
        )
        btn_unfav.pack(side="left")

    def load_favorites(self):
        docs = self.doc_service.repo.get_user_documents(self.user_id, favorites_only=True)
        for item in self.tree.get_children():
            self.tree.delete(item)

        for doc in docs:
            self.tree.insert(
                "",
                "end",
                iid=str(doc["id"]),
                values=(
                    doc["id"],
                    doc["title"],
                    doc.get("category", "General"),
                    format_date(doc.get("expiry_date")),
                    format_file_size(doc.get("file_size", 0)),
                    format_date(doc.get("created_at")),
                ),
            )

    def _on_open_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Selection Required", "Please select a document from your favorites.", parent=self.frame)
            return
        self.open_doc_callback(int(selected[0]))

    def _on_remove_favorite(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Selection Required", "Please select a document to unstar.", parent=self.frame)
            return
        doc_id = int(selected[0])
        self.doc_service.toggle_favorite(doc_id, self.user_id)
        self.load_favorites()
