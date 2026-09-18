"""My Documents Page providing structured table view, filtering, sorting, and management controls."""

from typing import Callable, List, Optional
from app.services.document_service import DocumentService
from app.ui.common import UITheme, format_file_size, format_date
from app.ui.tk_compat import tk, ttk, messagebox


class DocumentsPage:
    """Displays user documents in a clean, searchable, and sortable table."""

    def __init__(
        self,
        parent: tk.Frame,
        user_id: int,
        doc_service: DocumentService,
        open_doc_callback: Callable[[int], None],
        add_doc_callback: Callable[[], None],
    ):
        self.parent = parent
        self.user_id = user_id
        self.doc_service = doc_service
        self.open_doc_callback = open_doc_callback
        self.add_doc_callback = add_doc_callback

        self.frame = tk.Frame(self.parent, bg=UITheme.BG_LIGHT, padx=24, pady=18)
        self.current_docs: List[dict] = []

        self._build_ui()
        self.load_documents()

    def _build_ui(self):
        # 1. Top toolbar
        toolbar = tk.Frame(self.frame, bg=UITheme.BG_LIGHT)
        toolbar.pack(fill="x", pady=(0, 12))

        # Title: "My Documents"
        tk.Label(
            toolbar, text="📁 My Documents", font=UITheme.FONT_DISPLAY,
            bg=UITheme.BG_LIGHT, fg=UITheme.TEXT_MAIN
        ).pack(side="left")

        btn_add = tk.Button(
            toolbar, text="+ Add Document", font=UITheme.FONT_BODY_BOLD,
            bg=UITheme.PRIMARY, fg="white", activebackground=UITheme.PRIMARY_HOVER, activeforeground="white",
            relief="flat", cursor="hand2", padx=14, pady=6, command=self.add_doc_callback
        )
        btn_add.pack(side="right")

        # 2. Filters Bar
        filter_bar = tk.Frame(self.frame, bg=UITheme.SURFACE_LIGHT, relief="solid", bd=1, padx=14, pady=10)
        filter_bar.pack(fill="x", pady=(0, 12))

        # Category Filter
        tk.Label(filter_bar, text="Category:", font=UITheme.FONT_BODY_BOLD, bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MUTED).pack(side="left", padx=(0, 5))
        self.cat_var = tk.StringVar(value="All")
        self.cat_combo = ttk.Combobox(filter_bar, textvariable=self.cat_var, state="readonly", width=18)
        self.cat_combo.pack(side="left", padx=(0, 15))
        self.cat_combo.bind("<<ComboboxSelected>>", lambda e: self.load_documents())

        # Sort Order
        tk.Label(filter_bar, text="Sort By:", font=UITheme.FONT_BODY_BOLD, bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MUTED).pack(side="left", padx=(0, 5))
        self.sort_var = tk.StringVar(value="created_at_desc")
        sort_options = [
            ("created_at_desc", "Date Added (Newest)"),
            ("created_at_asc", "Date Added (Oldest)"),
            ("title_asc", "Title (A-Z)"),
            ("expiry_asc", "Valid Until (Nearest)"),
        ]
        sort_combo = ttk.Combobox(filter_bar, textvariable=self.sort_var, values=[k for k, _ in sort_options], state="readonly", width=18)
        sort_combo.pack(side="left", padx=(0, 15))
        sort_combo.bind("<<ComboboxSelected>>", lambda e: self.load_documents())

        # Filter by name
        tk.Label(filter_bar, text="Filter:", font=UITheme.FONT_BODY_BOLD, bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MUTED).pack(side="left", padx=(0, 5))
        self.filter_var = tk.StringVar()
        ent_search = ttk.Entry(filter_bar, textvariable=self.filter_var, width=20)
        ent_search.pack(side="left", padx=(0, 8))
        ent_search.bind("<Return>", lambda e: self.load_documents())

        btn_apply = tk.Button(
            filter_bar, text="Filter", font=UITheme.FONT_SMALL, bg=UITheme.SURFACE_ALT, fg=UITheme.TEXT_MAIN,
            relief="flat", cursor="hand2", padx=10, pady=2, command=self.load_documents
        )
        btn_apply.pack(side="left")

        # 3. Table Frame
        table_frame = tk.Frame(self.frame, bg=UITheme.SURFACE_LIGHT, relief="solid", bd=1)
        table_frame.pack(fill="both", expand=True)

        columns = ("id", "fav", "title", "category", "expiry", "size", "created_at")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="#")
        self.tree.heading("fav", text="⭐")
        self.tree.heading("title", text="Document Title")
        self.tree.heading("category", text="Category")
        self.tree.heading("expiry", text="Valid Until")
        self.tree.heading("size", text="File Size")
        self.tree.heading("created_at", text="Date Stored")

        self.tree.column("id", width=45, anchor="center")
        self.tree.column("fav", width=45, anchor="center")
        self.tree.column("title", width=260, anchor="w")
        self.tree.column("category", width=140, anchor="w")
        self.tree.column("expiry", width=120, anchor="center")
        self.tree.column("size", width=85, anchor="center")
        self.tree.column("created_at", width=120, anchor="center")

        scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", self._on_double_click)

        # 4. Action Buttons Footer
        action_footer = tk.Frame(self.frame, bg=UITheme.BG_LIGHT)
        action_footer.pack(fill="x", pady=(10, 0))

        btn_view = tk.Button(
            action_footer, text="🔍 View Document", font=UITheme.FONT_BODY_BOLD,
            bg=UITheme.PRIMARY, fg="white", relief="flat", cursor="hand2", padx=14, pady=6,
            command=self._on_view_selected
        )
        btn_view.pack(side="left", padx=(0, 8))

        btn_fav = tk.Button(
            action_footer, text="⭐ Toggle Favorite", font=UITheme.FONT_BODY,
            bg="#fef08a", fg="#854d0e", relief="flat", cursor="hand2", padx=12, pady=6,
            command=self._on_toggle_fav
        )
        btn_fav.pack(side="left", padx=(0, 8))

        btn_del = tk.Button(
            action_footer, text="🗑️ Delete Document", font=UITheme.FONT_BODY,
            bg=UITheme.DANGER_BG, fg=UITheme.DANGER, relief="flat", cursor="hand2", padx=12, pady=6,
            command=self._on_delete_selected
        )
        btn_del.pack(side="left")

    def load_documents(self):
        cats = ["All"] + self.doc_service.get_categories(self.user_id)
        self.cat_combo.configure(values=cats)

        cat_filter = self.cat_var.get()
        if cat_filter == "All":
            cat_filter = None

        search_query = self.filter_var.get().strip()
        sort_by = self.sort_var.get()

        if search_query:
            self.current_docs = self.doc_service.search_documents(self.user_id, search_query, category=cat_filter)
        else:
            self.current_docs = self.doc_service.repo.get_user_documents(
                self.user_id, category=cat_filter, sort_by=sort_by
            )

        for item in self.tree.get_children():
            self.tree.delete(item)

        for doc in self.current_docs:
            fav_char = "⭐" if doc.get("is_favorite") else "—"
            self.tree.insert(
                "",
                "end",
                iid=str(doc["id"]),
                values=(
                    doc["id"],
                    fav_char,
                    doc["title"],
                    doc.get("category", "General"),
                    format_date(doc.get("expiry_date")),
                    format_file_size(doc.get("file_size", 0)),
                    format_date(doc.get("created_at")),
                ),
            )

    def _get_selected_id(self) -> Optional[int]:
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Selection Required", "Please select a document from the table.", parent=self.frame)
            return None
        return int(selected[0])

    def _on_double_click(self, event):
        doc_id = self._get_selected_id()
        if doc_id:
            self.open_doc_callback(doc_id)

    def _on_view_selected(self):
        doc_id = self._get_selected_id()
        if doc_id:
            self.open_doc_callback(doc_id)

    def _on_toggle_fav(self):
        doc_id = self._get_selected_id()
        if doc_id:
            self.doc_service.toggle_favorite(doc_id, self.user_id)
            self.load_documents()

    def _on_delete_selected(self):
        doc_id = self._get_selected_id()
        if not doc_id:
            return
        doc = self.doc_service.get_document(doc_id, self.user_id, record_access=False)
        title = doc["title"] if doc else f"Document #{doc_id}"
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete '{title}' from your vault?\n\nThis will safely remove the document and its stored file.",
            parent=self.frame,
        )
        if confirm:
            self.doc_service.delete_document(doc_id, self.user_id)
            self.load_documents()
            messagebox.showinfo("Document Removed", "The document has been removed from your vault.", parent=self.frame)
