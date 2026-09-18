"""Settings & Security Configuration Page designed with clean, friendly cards."""

import shutil
from pathlib import Path
from typing import Dict, Any
from app.database.auth_repository import AuthRepository
from app.database.connection import get_db_path
from app.services.document_service import DocumentService
from app.ui.common import UITheme, format_date, format_file_size
from app.ui.tk_compat import tk, ttk, filedialog, messagebox


class SettingsPage:
    """Provides user account controls, vault security status, and backup facilities."""

    def __init__(
        self,
        parent: tk.Frame,
        user_data: Dict[str, Any],
        auth_repo: AuthRepository,
        doc_service: DocumentService,
    ):
        self.parent = parent
        self.user_data = user_data
        self.auth_repo = auth_repo
        self.doc_service = doc_service

        self.frame = tk.Frame(self.parent, bg=UITheme.BG_LIGHT, padx=28, pady=22)
        self._build_ui()

    def _build_ui(self):
        header = tk.Frame(self.frame, bg=UITheme.BG_LIGHT)
        header.pack(fill="x", pady=(0, 15))

        tk.Label(
            header, text="⚙️ Settings & Security", font=UITheme.FONT_DISPLAY,
            bg=UITheme.BG_LIGHT, fg=UITheme.TEXT_MAIN
        ).pack(anchor="w")

        tk.Label(
            header, text="Manage your account profile, password, security settings, and local backups.",
            font=UITheme.FONT_SMALL, bg=UITheme.BG_LIGHT, fg=UITheme.TEXT_MUTED
        ).pack(anchor="w", pady=(3, 0))

        container = tk.Frame(self.frame, bg=UITheme.BG_LIGHT)
        container.pack(fill="both", expand=True)

        # Section 1: User Account Profile
        self._build_user_card(container)

        # Section 2: Vault Security Status (Friendly, Non-technical)
        self._build_security_card(container)

        # Section 3: Password Update
        self._build_password_card(container)

        # Section 4: Vault Backup
        self._build_backup_card(container)

    def _build_user_card(self, parent: tk.Frame):
        card = tk.Frame(parent, bg=UITheme.SURFACE_LIGHT, relief="solid", bd=1, padx=20, pady=16)
        card.pack(fill="x", pady=(0, 15))

        tk.Label(card, text="👤 Account Profile", font=UITheme.FONT_SUBTITLE, bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MAIN).pack(anchor="w", pady=(0, 10))

        rows = [
            ("Username:", self.user_data.get("username", "Unknown")),
            ("Email Address:", self.user_data.get("email") or "Not configured"),
            ("Account Created:", format_date(self.user_data.get("created_at"))),
        ]
        for lbl, val in rows:
            r = tk.Frame(card, bg=UITheme.SURFACE_LIGHT)
            r.pack(fill="x", pady=3)
            tk.Label(r, text=lbl, font=UITheme.FONT_BODY_BOLD, width=16, anchor="w", bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MUTED).pack(side="left")
            tk.Label(r, text=val, font=UITheme.FONT_BODY, anchor="w", bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MAIN).pack(side="left")

    def _build_security_card(self, parent: tk.Frame):
        card = tk.Frame(parent, bg=UITheme.SURFACE_LIGHT, relief="solid", bd=1, padx=20, pady=16)
        card.pack(fill="x", pady=(0, 15))

        tk.Label(card, text="🛡️ Security & Privacy", font=UITheme.FONT_SUBTITLE, bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MAIN).pack(anchor="w", pady=(0, 10))

        specs = [
            ("File Security:", "All uploaded documents are encrypted and protected at rest on your computer."),
            ("Password Protection:", "Passwords are salted and protected against unauthorized access."),
            ("Privacy Model:", "100% offline-first. Your files are never sent to external servers or cloud services."),
            ("Integrity Checking:", "Every document is verified for safety before being viewed or exported."),
        ]
        for lbl, val in specs:
            r = tk.Frame(card, bg=UITheme.SURFACE_LIGHT)
            r.pack(fill="x", pady=3)
            tk.Label(r, text=lbl, font=UITheme.FONT_BODY_BOLD, width=18, anchor="w", bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MUTED).pack(side="left")
            tk.Label(r, text=val, font=UITheme.FONT_BODY, anchor="w", bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MAIN).pack(side="left")

    def _build_password_card(self, parent: tk.Frame):
        card = tk.Frame(parent, bg=UITheme.SURFACE_LIGHT, relief="solid", bd=1, padx=20, pady=16)
        card.pack(fill="x", pady=(0, 15))

        tk.Label(card, text="🔑 Change Password", font=UITheme.FONT_SUBTITLE, bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MAIN).pack(anchor="w", pady=(0, 10))

        form = tk.Frame(card, bg=UITheme.SURFACE_LIGHT)
        form.pack(fill="x")

        tk.Label(form, text="Current Password:", font=UITheme.FONT_BODY_BOLD, bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MUTED).grid(row=0, column=0, sticky="w", pady=4)
        self.old_pass_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.old_pass_var, show="●", width=25).grid(row=0, column=1, sticky="w", padx=10, pady=4)

        tk.Label(form, text="New Password:", font=UITheme.FONT_BODY_BOLD, bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MUTED).grid(row=1, column=0, sticky="w", pady=4)
        self.new_pass_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.new_pass_var, show="●", width=25).grid(row=1, column=1, sticky="w", padx=10, pady=4)

        btn_chg = tk.Button(
            form, text="Update Password", font=UITheme.FONT_SMALL_BOLD, bg=UITheme.PRIMARY, fg="white",
            relief="flat", cursor="hand2", padx=14, pady=4, command=self._handle_password_change
        )
        btn_chg.grid(row=1, column=2, padx=10, pady=4)

    def _build_backup_card(self, parent: tk.Frame):
        card = tk.Frame(parent, bg=UITheme.SURFACE_LIGHT, relief="solid", bd=1, padx=20, pady=16)
        card.pack(fill="x")

        tk.Label(card, text="💾 Backup Vault Database", font=UITheme.FONT_SUBTITLE, bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MAIN).pack(anchor="w", pady=(0, 6))

        tk.Label(
            card, text="Export a backup of your personal database file to an external drive or backup folder.",
            font=UITheme.FONT_BODY, bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MUTED
        ).pack(anchor="w", pady=(0, 10))

        btn_backup = tk.Button(
            card, text="Export Database Backup...", font=UITheme.FONT_BODY, bg=UITheme.SURFACE_ALT, fg=UITheme.TEXT_MAIN,
            relief="flat", cursor="hand2", padx=14, pady=6, command=self._handle_backup_db
        )
        btn_backup.pack(anchor="w")

    def _handle_password_change(self):
        old_pass = self.old_pass_var.get()
        new_pass = self.new_pass_var.get()
        if not old_pass or not new_pass:
            messagebox.showwarning("Incomplete Fields", "Please enter both old and new passwords.", parent=self.frame)
            return

        identifier = self.user_data.get("email") or self.user_data["username"]
        success, msg = self.auth_repo.reset_password(identifier, old_pass, new_pass)
        if success:
            messagebox.showinfo("Success", msg, parent=self.frame)
            self.old_pass_var.set("")
            self.new_pass_var.set("")
        else:
            messagebox.showerror("Error", msg, parent=self.frame)

    def _handle_backup_db(self):
        src_db = get_db_path()
        dest = filedialog.asksaveasfilename(
            parent=self.frame,
            title="Backup Database File",
            initialfile="vaultx_backup.db",
            filetypes=[("SQLite Database (*.db)", "*.db"), ("All Files (*.*)", "*.*")],
        )
        if dest:
            try:
                shutil.copyfile(src_db, dest)
                messagebox.showinfo("Backup Completed", f"Database backed up safely to:\n{dest}", parent=self.frame)
            except Exception as e:
                messagebox.showerror("Backup Failed", f"Could not create backup: {str(e)}", parent=self.frame)
