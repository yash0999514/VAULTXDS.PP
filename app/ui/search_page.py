"""Search Documents Page designed with friendly labels and backed by custom Trie prefix indexing."""

from typing import Callable, List, Optional
from app.services.document_service import DocumentService
from app.ui.common import UITheme, format_date, format_file_size
from app.ui.tk_compat import tk, ttk, messagebox


class SearchPage:
    """Provides high-performance search across document titles, categories, tags, and text."""

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
        self.results: List[dict] = []

        self._build_ui()

    def _build_ui(self):
        # 1. Header section (Friendly Non-Technical Title)
        header = tk.Frame(self.frame, bg=UITheme.BG_LIGHT)
        header.pack(fill="x", pady=(0, 15))

        tk.Label(
            header, text="🔍 Search Documents", font=UITheme.FONT_DISPLAY,
            bg=UITheme.BG_LIGHT, fg=UITheme.TEXT_MAIN
        ).pack(anchor="w")

        tk.Label(
            header, text="Instantly search across your document titles, categories, tags, and notes.",
            font=UITheme.FONT_SMALL, bg=UITheme.BG_LIGHT, fg=UITheme.TEXT_MUTED
        ).pack(anchor="w", pady=(3, 0))

        # 2. Search Card
        search_card = tk.Frame(self.frame, bg=UITheme.SURFACE_LIGHT, relief="solid", bd=1, padx=20, pady=16)
        search_card.pack(fill="x", pady=(0, 16))

        # "What document are you looking for?"
        tk.Label(
            search_card, text="What document are you looking for?", font=UITheme.FONT_BODY_BOLD,
            bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MAIN
        ).pack(anchor="w", pady=(0, 6))

        input_row = tk.Frame(search_card, bg=UITheme.SURFACE_LIGHT)
        input_row.pack(fill="x", pady=(0, 6))

        self.query_var = tk.StringVar()
        self.search_entry = ttk.Entry(input_row, textvariable=self.query_var, font=UITheme.FONT_BODY)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self._on_key_release)
        self.search_entry.bind("<Return>", lambda e: self.perform_search())

        # "Search" Button
        btn_search = tk.Button(
            input_row, text="Search", font=UITheme.FONT_BODY_BOLD, bg=UITheme.PRIMARY, fg="white",
            relief="flat", cursor="hand2", padx=20, pady=6, command=self.perform_search
        )
        btn_search.pack(side="right")

        # Live Autocomplete Suggestions Box
        sugg_frame = tk.Frame(search_card, bg=UITheme.SURFACE_LIGHT)
        sugg_frame.pack(fill="x", pady=(4, 0))

        tk.Label(
            sugg_frame, text="Suggestions:", font=UITheme.FONT_SMALL,
            bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MUTED
        ).pack(side="left", padx=(0, 8))

        self.sugg_lbl_var = tk.StringVar(value="Type a few letters to see matching titles or tags...")
        self.sugg_lbl = tk.Label(
            sugg_frame, textvariable=self.sugg_lbl_var, font=UITheme.FONT_SMALL,
            bg=UITheme.PRIMARY_LIGHT, fg=UITheme.PRIMARY, padx=8, pady=2
        )
        self.sugg_lbl.pack(side="left")

        # 3. Status Line
        self.status_lbl_var = tk.StringVar(value="Enter a search term above and press Search.")
        tk.Label(
            self.frame, textvariable=self.status_lbl_var, font=UITheme.FONT_BODY_BOLD,
            bg=UITheme.BG_LIGHT, fg=UITheme.TEXT_MUTED
        ).pack(anchor="w", pady=(0, 10))

        # 4. Results Table
        table_frame = tk.Frame(self.frame, bg=UITheme.SURFACE_LIGHT, relief="solid", bd=1)
        table_frame.pack(fill="both", expand=True)

        columns = ("id", "title", "category", "tags", "expiry", "size")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="#")
        self.tree.heading("title", text="Document Title")
        self.tree.heading("category", text="Category")
        self.tree.heading("tags", text="Tags")
        self.tree.heading("expiry", text="Valid Until")
        self.tree.heading("size", text="Size")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("title", width=260, anchor="w")
        self.tree.column("category", width=140, anchor="w")
        self.tree.column("tags", width=190, anchor="w")
        self.tree.column("expiry", width=120, anchor="center")
        self.tree.column("size", width=90, anchor="center")

        scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", self._on_double_click)

        # 5. Footer: "View Document" Button
        footer = tk.Frame(self.frame, bg=UITheme.BG_LIGHT)
        footer.pack(fill="x", pady=(12, 0))

        btn_open = tk.Button(
            footer, text="🔍 View Document", font=UITheme.FONT_BODY_BOLD,
            bg=UITheme.PRIMARY, fg="white", relief="flat", cursor="hand2", padx=18, pady=7,
            command=self._on_open_selected
        )
        btn_open.pack(side="left")

    def _on_key_release(self, event):
        query = self.query_var.get().strip()
        if len(query) >= 2:
            last_word = query.split()[-1]
            suggestions = self.doc_service.search_service.autocomplete(last_word, max_results=5)
            if suggestions:
                self.sugg_lbl_var.set("  |  ".join(suggestions))
            else:
                self.sugg_lbl_var.set("No matching suggestions found")
        else:
            self.sugg_lbl_var.set("Type a few letters to see matching titles or tags...")

    def perform_search(self):
        query = self.query_var.get().strip()
        if not query:
            messagebox.showinfo("Search Query Required", "Please enter a word or title to search.", parent=self.frame)
            return

        self.results = self.doc_service.search_documents(self.user_id, query)

        for item in self.tree.get_children():
            self.tree.delete(item)

        for doc in self.results:
            self.tree.insert(
                "",
                "end",
                iid=str(doc["id"]),
                values=(
                    doc["id"],
                    doc["title"],
                    doc.get("category", "General"),
                    doc.get("tags") or "—",
                    format_date(doc.get("expiry_date")),
                    format_file_size(doc.get("file_size", 0)),
                ),
            )

        count = len(self.results)
        if count == 0:
            self.status_lbl_var.set(f"No documents matched '{query}'. Try searching by category or another keyword.")
        else:
            self.status_lbl_var.set(f"Found {count} matching document{'s' if count != 1 else ''} for '{query}'.")

    def _on_double_click(self, event):
        self._on_open_selected()

    def _on_open_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Selection Required", "Please select a document from the search results.", parent=self.frame)
            return
        doc_id = int(selected[0])
        self.open_doc_callback(doc_id)
