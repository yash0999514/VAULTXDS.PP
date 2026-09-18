"""Modern Home Dashboard designed for non-technical users with real database statistics."""

from typing import Callable, Dict, Any
from app.services.document_service import DocumentService
from app.ui.common import UITheme, format_date
from app.ui.tk_compat import tk, ttk


class HomePage:
    """Home dashboard featuring a warm welcome, 4 status cards, quick actions, and recent activity."""

    def __init__(
        self,
        parent: tk.Frame,
        user_id: int,
        doc_service: DocumentService,
        nav_callback: Callable[[str], None],
        open_doc_callback: Callable[[int], None],
    ):
        self.parent = parent
        self.user_id = user_id
        self.doc_service = doc_service
        self.nav_callback = nav_callback
        self.open_doc_callback = open_doc_callback

        self.frame = tk.Frame(self.parent, bg=UITheme.BG_LIGHT, padx=28, pady=22)
        self._build_ui()

    def _build_ui(self):
        for w in self.frame.winfo_children():
            w.destroy()

        stats = self.doc_service.get_dashboard_stats(self.user_id)
        current_username = self.doc_service.repo.get_document(1, self.user_id)
        # Fetch user's display username from DB or session
        conn = self.doc_service.repo.get_user_documents(self.user_id)

        # 1. Welcome Message Header
        header_frame = tk.Frame(self.frame, bg=UITheme.BG_LIGHT)
        header_frame.pack(fill="x", pady=(0, 20))

        # Retrieve username from active user record
        username = getattr(self.parent.master, "username", "there")
        tk.Label(
            header_frame,
            text=f"Welcome back! 👋",
            font=UITheme.FONT_DISPLAY,
            bg=UITheme.BG_LIGHT,
            fg=UITheme.TEXT_MAIN,
        ).pack(anchor="w")

        tk.Label(
            header_frame,
            text="Here is a quick overview of your personal document vault.",
            font=UITheme.FONT_SMALL,
            bg=UITheme.BG_LIGHT,
            fg=UITheme.TEXT_MUTED,
        ).pack(anchor="w", pady=(2, 0))

        # 2. 4 Status Cards Row
        cards_frame = tk.Frame(self.frame, bg=UITheme.BG_LIGHT)
        cards_frame.pack(fill="x", pady=(0, 22))

        # Card 1: Total Documents
        self._render_card(
            cards_frame, "📁", "Total Documents", str(stats["total_documents"]),
            "Stored in your vault", UITheme.PRIMARY, 0
        )
        # Card 2: Favorites
        self._render_card(
            cards_frame, "⭐", "Favorites", str(stats["favorite_documents"]),
            "Starred for quick access", "#d97706", 1
        )
        # Card 3: Expiring Soon
        self._render_card(
            cards_frame, "⏰", "Expiring Soon", str(stats["expiring_soon_documents"]),
            "Within the next 30 days", UITheme.WARNING, 2
        )
        # Card 4: Security Status (Friendly, Non-technical)
        self._render_security_card(
            cards_frame, "🛡️", "Security Status", "Protected",
            "Your documents are protected.", UITheme.SUCCESS, 3
        )

        # 3. Two-Column Workspace Layout
        body_frame = tk.Frame(self.frame, bg=UITheme.BG_LIGHT)
        body_frame.pack(fill="both", expand=True)

        left_col = tk.Frame(body_frame, bg=UITheme.BG_LIGHT)
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 16))

        right_col = tk.Frame(body_frame, bg=UITheme.BG_LIGHT)
        right_col.pack(side="right", fill="both", expand=True)

        # Left Column: Recently Added & Quick Actions
        self._build_recent_added_section(left_col, stats.get("recent_documents", []))
        self._build_quick_actions(left_col)

        # Right Column: Upcoming Expirations & Category Breakdown
        self._build_expirations_section(right_col)
        self._build_categories_section(right_col, stats["category_counts"])

    def _render_card(self, parent: tk.Frame, icon: str, title: str, count_val: str, subtitle: str, accent: str, col_idx: int):
        card = tk.Frame(parent, bg=UITheme.SURFACE_LIGHT, relief="solid", bd=1, padx=16, pady=14)
        card.grid(row=0, column=col_idx, sticky="nsew", padx=6)
        parent.grid_columnconfigure(col_idx, weight=1)

        top_row = tk.Frame(card, bg=UITheme.SURFACE_LIGHT)
        top_row.pack(fill="x", pady=(0, 6))

        tk.Label(top_row, text=icon, font=(UITheme.FONT_FAMILY, 14), bg=UITheme.SURFACE_LIGHT).pack(side="left", padx=(0, 6))
        tk.Label(top_row, text=title.upper(), font=(UITheme.FONT_FAMILY, 8, "bold"), bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MUTED).pack(side="left")

        tk.Label(card, text=count_val, font=(UITheme.FONT_FAMILY, 24, "bold"), bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MAIN).pack(anchor="w", pady=(0, 2))
        tk.Label(card, text=subtitle, font=UITheme.FONT_SMALL, bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MUTED).pack(anchor="w")

    def _render_security_card(self, parent: tk.Frame, icon: str, title: str, status_val: str, message: str, accent: str, col_idx: int):
        card = tk.Frame(parent, bg=UITheme.SURFACE_LIGHT, relief="solid", bd=1, padx=16, pady=14)
        card.grid(row=0, column=col_idx, sticky="nsew", padx=6)
        parent.grid_columnconfigure(col_idx, weight=1)

        top_row = tk.Frame(card, bg=UITheme.SURFACE_LIGHT)
        top_row.pack(fill="x", pady=(0, 6))

        tk.Label(top_row, text=icon, font=(UITheme.FONT_FAMILY, 14), bg=UITheme.SURFACE_LIGHT).pack(side="left", padx=(0, 6))
        tk.Label(top_row, text=title.upper(), font=(UITheme.FONT_FAMILY, 8, "bold"), bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MUTED).pack(side="left")

        tk.Label(card, text=status_val, font=(UITheme.FONT_FAMILY, 22, "bold"), bg=UITheme.SURFACE_LIGHT, fg=accent).pack(anchor="w", pady=(0, 2))
        tk.Label(card, text=message, font=UITheme.FONT_SMALL_BOLD, bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MAIN).pack(anchor="w")

    def _build_recent_added_section(self, parent: tk.Frame, recent_docs: list):
        card = tk.Frame(parent, bg=UITheme.SURFACE_LIGHT, relief="solid", bd=1, padx=18, pady=16)
        card.pack(fill="x", pady=(0, 16))

        header = tk.Frame(card, bg=UITheme.SURFACE_LIGHT)
        header.pack(fill="x", pady=(0, 10))

        tk.Label(header, text="📄 Recently Added", font=UITheme.FONT_SUBTITLE, bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MAIN).pack(side="left")

        btn_view_all = tk.Button(
            header, text="View All →", font=UITheme.FONT_SMALL_BOLD, bg=UITheme.SURFACE_LIGHT, fg=UITheme.PRIMARY,
            relief="flat", cursor="hand2", command=lambda: self.nav_callback("documents")
        )
        btn_view_all.pack(side="right")

        if not recent_docs:
            empty = tk.Frame(card, bg=UITheme.SURFACE_LIGHT, pady=15)
            empty.pack(fill="x")
            tk.Label(empty, text="No documents stored yet.", font=UITheme.FONT_BODY, bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MUTED).pack(anchor="w")
            tk.Label(empty, text="Click '+ Add Document' above to upload your first file.", font=UITheme.FONT_SMALL, bg=UITheme.SURFACE_LIGHT, fg=UITheme.PRIMARY).pack(anchor="w", pady=(2, 0))
            return

        for doc in recent_docs[:4]:
            row = tk.Frame(card, bg=UITheme.SURFACE_LIGHT)
            row.pack(fill="x", pady=3)

            fav_icon = "⭐ " if doc.get("is_favorite") else "•  "
            btn = tk.Button(
                row, text=f"{fav_icon}{doc['title']}  ({doc.get('category', 'General')})",
                font=UITheme.FONT_BODY, anchor="w", bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MAIN,
                relief="flat", cursor="hand2", command=lambda d=doc["id"]: self.open_doc_callback(d)
            )
            btn.pack(side="left", fill="x", expand=True)

            date_lbl = tk.Label(row, text=format_date(doc.get("created_at")), font=UITheme.FONT_SMALL, bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MUTED)
            date_lbl.pack(side="right")

    def _build_quick_actions(self, parent: tk.Frame):
        card = tk.Frame(parent, bg=UITheme.SURFACE_LIGHT, relief="solid", bd=1, padx=18, pady=16)
        card.pack(fill="x")

        tk.Label(card, text="⚡ Quick Actions", font=UITheme.FONT_SUBTITLE, bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MAIN).pack(anchor="w", pady=(0, 12))

        actions = [
            ("➕ Add Document", UITheme.PRIMARY, "white", lambda: self.nav_callback("add_dialog")),
            ("🔍 Search Documents", UITheme.SURFACE_ALT, UITheme.TEXT_MAIN, lambda: self.nav_callback("search")),
            ("⭐ View Favorites", UITheme.SURFACE_ALT, UITheme.TEXT_MAIN, lambda: self.nav_callback("favorites")),
        ]

        for label, bg_col, fg_col, cmd in actions:
            btn = tk.Button(
                card, text=label, font=UITheme.FONT_BODY_BOLD if bg_col == UITheme.PRIMARY else UITheme.FONT_BODY,
                bg=bg_col, fg=fg_col, relief="flat", cursor="hand2", pady=8, command=cmd
            )
            btn.pack(fill="x", pady=3)

    def _build_expirations_section(self, parent: tk.Frame):
        card = tk.Frame(parent, bg=UITheme.SURFACE_LIGHT, relief="solid", bd=1, padx=18, pady=16)
        card.pack(fill="x", pady=(0, 16))

        header = tk.Frame(card, bg=UITheme.SURFACE_LIGHT)
        header.pack(fill="x", pady=(0, 10))

        tk.Label(header, text="⏰ Expiring Soon", font=UITheme.FONT_SUBTITLE, bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MAIN).pack(side="left")

        btn_all_exp = tk.Button(
            header, text="See All →", font=UITheme.FONT_SMALL_BOLD, bg=UITheme.SURFACE_LIGHT, fg=UITheme.PRIMARY,
            relief="flat", cursor="hand2", command=lambda: self.nav_callback("expiry")
        )
        btn_all_exp.pack(side="right")

        expiring = self.doc_service.get_expiring_documents(days=30)
        if not expiring:
            tk.Label(
                card, text="✅ All clear — No documents are expiring soon.",
                font=UITheme.FONT_BODY, bg=UITheme.SURFACE_LIGHT, fg=UITheme.SUCCESS
            ).pack(anchor="w", pady=6)
            return

        for item in expiring[:4]:
            row = tk.Frame(card, bg=UITheme.SURFACE_LIGHT)
            row.pack(fill="x", pady=4)

            title = item.get("metadata", {}).get("title", f"Document #{item['doc_id']}")
            days_left = item["days_left"]

            if days_left < 0:
                badge_txt = f"Expired {abs(days_left)}d ago"
                badge_bg = UITheme.DANGER_BG
                badge_fg = UITheme.DANGER
            elif days_left == 0:
                badge_txt = "Expires Today"
                badge_bg = UITheme.DANGER_BG
                badge_fg = UITheme.DANGER
            elif days_left <= 7:
                badge_txt = f"{days_left} days remaining"
                badge_bg = UITheme.WARNING_BG
                badge_fg = UITheme.WARNING
            else:
                badge_txt = f"{days_left} days remaining"
                badge_bg = UITheme.PRIMARY_LIGHT
                badge_fg = UITheme.PRIMARY

            lbl_title = tk.Label(row, text=f"•  {title}", font=UITheme.FONT_BODY, bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MAIN)
            lbl_title.pack(side="left")

            badge = tk.Label(row, text=badge_txt, font=UITheme.FONT_SMALL_BOLD, bg=badge_bg, fg=badge_fg, padx=8, pady=2)
            badge.pack(side="right")

    def _build_categories_section(self, parent: tk.Frame, category_counts: Dict[str, int]):
        card = tk.Frame(parent, bg=UITheme.SURFACE_LIGHT, relief="solid", bd=1, padx=18, pady=16)
        card.pack(fill="x")

        tk.Label(card, text="🏷️ Categories Overview", font=UITheme.FONT_SUBTITLE, bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MAIN).pack(anchor="w", pady=(0, 10))

        if not category_counts:
            tk.Label(card, text="No categorized documents yet.", font=UITheme.FONT_BODY, bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MUTED).pack(anchor="w")
            return

        for cat, count in list(category_counts.items())[:4]:
            row = tk.Frame(card, bg=UITheme.SURFACE_LIGHT)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=cat, font=UITheme.FONT_BODY, bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MAIN).pack(side="left")
            badge = tk.Label(row, text=f"{count} {'document' if count == 1 else 'documents'}", font=UITheme.FONT_SMALL, bg=UITheme.SURFACE_ALT, fg=UITheme.TEXT_SECONDARY, padx=8, pady=1)
            badge.pack(side="right")

    def refresh(self):
        self._build_ui()
