"""Expiring Documents Page with user-friendly labels and chronological date sorting."""

from typing import Callable, List
from app.services.document_service import DocumentService
from app.ui.common import UITheme, format_date
from app.ui.tk_compat import tk, ttk, messagebox


class ExpiryPage:
    """Monitors upcoming and overdue document validity deadlines."""

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
        self.load_expirations()

    def _build_ui(self):
        # Header (Friendly Title)
        header = tk.Frame(self.frame, bg=UITheme.BG_LIGHT)
        header.pack(fill="x", pady=(0, 15))

        tk.Label(
            header, text="⏰ Expiring Documents", font=UITheme.FONT_DISPLAY,
            bg=UITheme.BG_LIGHT, fg=UITheme.TEXT_MAIN
        ).pack(anchor="w")

        tk.Label(
            header, text="Track validity periods and renew your personal documents, certificates, and policies on time.",
            font=UITheme.FONT_SMALL, bg=UITheme.BG_LIGHT, fg=UITheme.TEXT_MUTED
        ).pack(anchor="w", pady=(3, 0))

        # Filter bar
        filter_bar = tk.Frame(self.frame, bg=UITheme.SURFACE_LIGHT, relief="solid", bd=1, padx=16, pady=10)
        filter_bar.pack(fill="x", pady=(0, 16))

        # "Show:"
        tk.Label(
            filter_bar, text="Show:", font=UITheme.FONT_BODY_BOLD,
            bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MUTED
        ).pack(side="left", padx=(0, 8))

        self.filter_var = tk.StringVar(value="All Documents with Expiry")
        options = ["All Documents with Expiry", "Expiring Soon (< 30 Days)", "Expired Documents"]
        combo = ttk.Combobox(filter_bar, textvariable=self.filter_var, values=options, state="readonly", width=26)
        combo.pack(side="left", padx=(0, 12))
        combo.bind("<<ComboboxSelected>>", lambda e: self.load_expirations())

        btn_refresh = tk.Button(
            filter_bar, text="🔄 Refresh", font=UITheme.FONT_SMALL, bg=UITheme.SURFACE_ALT, fg=UITheme.TEXT_MAIN,
            relief="flat", cursor="hand2", padx=12, pady=4, command=self.load_expirations
        )
        btn_refresh.pack(side="left")

        # Table Frame
        table_frame = tk.Frame(self.frame, bg=UITheme.SURFACE_LIGHT, relief="solid", bd=1)
        table_frame.pack(fill="both", expand=True)

        columns = ("id", "status", "days", "expiry", "title", "category")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        # Headings: Status, Days Remaining, Valid Until, Document Title, Category
        self.tree.heading("id", text="#")
        self.tree.heading("status", text="Status")
        self.tree.heading("days", text="Days Remaining")
        self.tree.heading("expiry", text="Valid Until")
        self.tree.heading("title", text="Document Title")
        self.tree.heading("category", text="Category")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("status", width=130, anchor="center")
        self.tree.column("days", width=140, anchor="center")
        self.tree.column("expiry", width=120, anchor="center")
        self.tree.column("title", width=260, anchor="w")
        self.tree.column("category", width=150, anchor="w")

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
        btn_view.pack(side="left")

    def load_expirations(self):
        horizon = self.filter_var.get()
        if "30 Days" in horizon:
            items = self.doc_service.expiry_service.get_expiring_within_days(30)
        elif "Expired" in horizon:
            items = [x for x in self.doc_service.expiry_service.get_all_tracked() if x["days_left"] < 0]
        else:
            items = self.doc_service.expiry_service.get_all_tracked()

        for item in self.tree.get_children():
            self.tree.delete(item)

        for entry in items:
            doc_id = entry["doc_id"]
            days = entry["days_left"]
            meta = entry.get("metadata", {})
            title = meta.get("title", f"Document #{doc_id}")
            category = meta.get("category", "General")

            if days < 0:
                status_str = "🔴 EXPIRED"
                days_str = f"{abs(days)} days ago"
            elif days == 0:
                status_str = "🔴 EXPIRES TODAY"
                days_str = "Today"
            elif days <= 7:
                status_str = "🟠 URGENT"
                days_str = f"{days} days remaining"
            elif days <= 30:
                status_str = "🟡 WARNING"
                days_str = f"{days} days remaining"
            else:
                status_str = "🟢 ACTIVE"
                days_str = f"{days} days remaining"

            self.tree.insert(
                "",
                "end",
                iid=str(doc_id),
                values=(doc_id, status_str, days_str, entry["expiry_date"], title, category),
            )

    def _on_open_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Selection Required", "Please select a document from the table.", parent=self.frame)
            return
        self.open_doc_callback(int(selected[0]))
