"""Document Details Dialog supporting metadata inspection, text preview, editing, and file export."""

import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional
from app.services.document_service import DocumentService
from app.ui.common import UITheme, format_file_size, format_date, sys_is_windows
from app.ui.tk_compat import tk, ttk, filedialog, messagebox
from app.ui.date_picker import open_date_picker


class DocumentDetailsDialog:
    """Comprehensive dialog for inspecting, previewing, editing, and exporting a saved document."""

    def __init__(
        self,
        parent: tk.Tk,
        doc_id: int,
        user_id: int,
        doc_service: DocumentService,
        on_updated: Callable[[], None],
        on_deleted: Callable[[], None],
    ):
        self.parent = parent
        self.doc_id = doc_id
        self.user_id = user_id
        self.doc_service = doc_service
        self.on_updated = on_updated
        self.on_deleted = on_deleted

        self.doc = self.doc_service.get_document(doc_id, user_id, record_access=True)
        if not self.doc:
            messagebox.showerror("Error", "Document could not be located.", parent=parent)
            return

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"VAULTX — {self.doc['title']}")
        self.dialog.geometry("640x720")
        self.dialog.configure(bg=UITheme.BG_LIGHT)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._center_window()
        self._build_ui()

    def _center_window(self):
        self.dialog.update_idletasks()
        w = 640
        h = 720
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (w // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (h // 2)
        self.dialog.geometry(f"{w}x{h}+{max(0, x)}+{max(0, y)}")

    def _build_ui(self):
        header = tk.Frame(self.dialog, bg=UITheme.PRIMARY, height=75)
        header.pack(fill="x")

        fav_symbol = "⭐ " if self.doc.get("is_favorite") else ""
        tk.Label(
            header, text=f"{fav_symbol}{self.doc['title']}",
            font=UITheme.FONT_SUBTITLE, fg="white", bg=UITheme.PRIMARY, padx=20
        ).pack(anchor="w", pady=(12, 2))

        tk.Label(
            header, text=f"Category: {self.doc.get('category')}   •   File: {self.doc.get('filename')}",
            font=UITheme.FONT_SMALL, fg="#bfdbfe", bg=UITheme.PRIMARY, padx=20
        ).pack(anchor="w", pady=(0, 10))

        # Notebook tabs
        container = tk.Frame(self.dialog, bg=UITheme.BG_LIGHT, padx=15, pady=10)
        container.pack(fill="both", expand=True)

        notebook = ttk.Notebook(container)
        notebook.pack(fill="both", expand=True)

        self.tab_info = tk.Frame(notebook, bg=UITheme.SURFACE_LIGHT, padx=20, pady=15)
        self.tab_preview = tk.Frame(notebook, bg=UITheme.SURFACE_LIGHT, padx=20, pady=15)
        self.tab_edit = tk.Frame(notebook, bg=UITheme.SURFACE_LIGHT, padx=20, pady=15)

        notebook.add(self.tab_info, text="   Overview   ")
        notebook.add(self.tab_preview, text="   Text & Preview   ")
        notebook.add(self.tab_edit, text="   Edit Details   ")

        self._build_info_tab()
        self._build_preview_tab()
        self._build_edit_tab()

        # Bottom action bar
        footer = tk.Frame(self.dialog, bg=UITheme.BG_LIGHT, padx=15, pady=10)
        footer.pack(fill="x")

        btn_del = tk.Button(
            footer, text="🗑️ Delete Document", font=UITheme.FONT_SMALL, bg=UITheme.DANGER_BG, fg=UITheme.DANGER,
            relief="flat", cursor="hand2", padx=12, pady=6, command=self._handle_delete
        )
        btn_del.pack(side="left")

        btn_close = tk.Button(
            footer, text="Close", font=UITheme.FONT_BODY, bg=UITheme.SURFACE_ALT, fg=UITheme.TEXT_MAIN,
            relief="flat", cursor="hand2", padx=16, pady=6, command=self.dialog.destroy
        )
        btn_close.pack(side="right")

        btn_export = tk.Button(
            footer, text="💾 Save a Copy (Export)...", font=UITheme.FONT_BODY_BOLD, bg=UITheme.PRIMARY, fg="white",
            relief="flat", cursor="hand2", padx=14, pady=6, command=self._handle_export
        )
        btn_export.pack(side="right", padx=(0, 10))

    def _build_info_tab(self):
        fields = [
            ("Title:", self.doc["title"]),
            ("Category:", self.doc.get("category", "General")),
            ("File Size:", format_file_size(self.doc.get("file_size", 0))),
            ("Tags:", self.doc.get("tags") or "None"),
            ("Valid Until:", self._format_expiry_status()),
            ("Favorite:", "Yes (Starred)" if self.doc.get("is_favorite") else "No"),
            ("Date Added:", format_date(self.doc.get("created_at"))),
            ("Last Modified:", format_date(self.doc.get("updated_at"))),
        ]

        for i, (lbl, val) in enumerate(fields):
            row = tk.Frame(self.tab_info, bg=UITheme.SURFACE_LIGHT)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=lbl, font=UITheme.FONT_BODY_BOLD, width=15, anchor="w", bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MUTED).pack(side="left")
            tk.Label(row, text=val, font=UITheme.FONT_BODY, anchor="w", bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MAIN).pack(side="left", fill="x", expand=True)

        # Description / Notes
        tk.Label(self.tab_info, text="Notes:", font=UITheme.FONT_BODY_BOLD, bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MUTED).pack(anchor="w", pady=(12, 4))
        notes_box = tk.Text(self.tab_info, height=5, font=UITheme.FONT_BODY, wrap="word", relief="solid", bd=1)
        notes_box.pack(fill="x")
        notes_box.insert("1.0", self.doc.get("description") or "(No notes recorded for this document)")
        notes_box.configure(state="disabled")

        # Open in default application
        btn_open = tk.Button(
            self.tab_info, text="↗️ Open in Default Viewer", font=UITheme.FONT_BODY, bg=UITheme.PRIMARY_LIGHT, fg=UITheme.PRIMARY,
            relief="solid", bd=1, cursor="hand2", padx=12, pady=6, command=self._open_in_system_viewer
        )
        btn_open.pack(anchor="w", pady=(15, 0))

    def _format_expiry_status(self) -> str:
        exp = self.doc.get("expiry_date")
        if not exp:
            return "No expiry set"
        try:
            dt = datetime.strptime(exp.strip()[:10], "%Y-%m-%d")
            days_left = (dt.date() - datetime.now().date()).days
            if days_left < 0:
                return f"{exp} (⚠️ Expired {abs(days_left)} days ago)"
            elif days_left == 0:
                return f"{exp} (⚠️ Expires today)"
            elif days_left <= 30:
                return f"{exp} (⚠️ {days_left} days remaining)"
            else:
                return f"{exp} ({days_left} days remaining)"
        except Exception:
            return exp

    def _build_preview_tab(self):
        tk.Label(
            self.tab_preview, text="Extracted Text & Document Content",
            font=UITheme.FONT_BODY_BOLD, bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MAIN
        ).pack(anchor="w", pady=(0, 8))

        ocr_content = self.doc.get("ocr_text", "").strip()
        if not ocr_content:
            ocr_content = "(No text was extracted for this file, or file is an image without detected text)"

        txt_preview = tk.Text(self.tab_preview, font=UITheme.FONT_MONO, wrap="word", relief="solid", bd=1)
        txt_preview.pack(fill="both", expand=True)
        txt_preview.insert("1.0", ocr_content)
        txt_preview.configure(state="disabled")

    def _build_edit_tab(self):
        # Title
        tk.Label(self.tab_edit, text="Title *", font=UITheme.FONT_BODY_BOLD, bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MAIN).pack(anchor="w", pady=(0, 2))
        self.edit_title_var = tk.StringVar(value=self.doc["title"])
        ttk.Entry(self.tab_edit, textvariable=self.edit_title_var, font=UITheme.FONT_BODY).pack(fill="x", pady=(0, 8))

        # Category
        tk.Label(self.tab_edit, text="Category *", font=UITheme.FONT_BODY_BOLD, bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MAIN).pack(anchor="w", pady=(0, 2))
        categories = self.doc_service.get_categories(self.user_id)
        self.edit_cat_var = tk.StringVar(value=self.doc.get("category", "General"))
        ttk.Combobox(self.tab_edit, textvariable=self.edit_cat_var, values=categories, state="readonly", font=UITheme.FONT_BODY).pack(fill="x", pady=(0, 8))

        # Expiry Date (Valid Until)
        tk.Label(self.tab_edit, text="Valid Until", font=UITheme.FONT_BODY_BOLD, bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MAIN).pack(anchor="w", pady=(0, 2))
        expiry_frame = tk.Frame(self.tab_edit, bg=UITheme.SURFACE_LIGHT)
        expiry_frame.pack(fill="x", pady=(0, 8))
        self.edit_expiry_var = tk.StringVar(value=self.doc.get("expiry_date") or "")
        ttk.Entry(expiry_frame, textvariable=self.edit_expiry_var, font=UITheme.FONT_BODY).pack(side="left", fill="x", expand=True, padx=(0, 8))
        tk.Button(
            expiry_frame, text="📅 Choose date", font=UITheme.FONT_SMALL,
            bg=UITheme.SURFACE_ALT, fg=UITheme.TEXT_MAIN, relief="flat",
            cursor="hand2", padx=8, command=lambda: open_date_picker(self.dialog, self.edit_expiry_var)
        ).pack(side="right")

        # Tags
        tk.Label(self.tab_edit, text="Tags", font=UITheme.FONT_BODY_BOLD, bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MAIN).pack(anchor="w", pady=(0, 2))
        self.edit_tags_var = tk.StringVar(value=self.doc.get("tags") or "")
        ttk.Entry(self.tab_edit, textvariable=self.edit_tags_var, font=UITheme.FONT_BODY).pack(fill="x", pady=(0, 8))

        # Notes
        tk.Label(self.tab_edit, text="Notes", font=UITheme.FONT_BODY_BOLD, bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MAIN).pack(anchor="w", pady=(0, 2))
        self.edit_desc_text = tk.Text(self.tab_edit, height=4, font=UITheme.FONT_BODY, wrap="word", relief="solid", bd=1)
        self.edit_desc_text.pack(fill="x", pady=(0, 8))
        self.edit_desc_text.insert("1.0", self.doc.get("description") or "")

        # Favorite checkbox
        self.edit_fav_var = tk.BooleanVar(value=bool(self.doc.get("is_favorite")))
        ttk.Checkbutton(self.tab_edit, text="⭐ Star as Favorite", variable=self.edit_fav_var).pack(anchor="w", pady=(0, 15))

        btn_save = tk.Button(
            self.tab_edit, text="Save Changes", font=UITheme.FONT_BODY_BOLD, bg=UITheme.PRIMARY, fg="white",
            relief="flat", cursor="hand2", padx=16, pady=6, command=self._handle_save_edit
        )
        btn_save.pack(anchor="w")

    def _open_in_system_viewer(self):
        preview_path = self.doc_service.get_decrypted_preview_path(self.doc_id, self.user_id)
        if not preview_path or not Path(preview_path).exists():
            messagebox.showerror("Error", "Could not prepare document for viewing.", parent=self.dialog)
            return

        try:
            if sys_is_windows():
                os.startfile(preview_path)
            else:
                subprocess.Popen(["xdg-open", preview_path])
        except Exception as e:
            messagebox.showinfo("Document Ready", f"Document opened from:\n{preview_path}", parent=self.dialog)

    def _handle_save_edit(self):
        title = self.edit_title_var.get().strip()
        if not title:
            messagebox.showwarning("Title Required", "Title cannot be empty.", parent=self.dialog)
            return

        category = self.edit_cat_var.get().strip() or "General"
        expiry = self.edit_expiry_var.get().strip() or None
        tags = self.edit_tags_var.get().strip()
        description = self.edit_desc_text.get("1.0", "end-1c").strip()
        is_favorite = self.edit_fav_var.get()

        if expiry:
            import re
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", expiry):
                messagebox.showerror("Invalid Date", "Please enter date in YYYY-MM-DD format.", parent=self.dialog)
                return

        success = self.doc_service.update_document(
            self.doc_id,
            self.user_id,
            title=title,
            category=category,
            expiry_date=expiry,
            tags=tags,
            description=description,
            is_favorite=is_favorite,
        )

        if success:
            messagebox.showinfo("Saved", "Document details updated successfully.", parent=self.dialog)
            self.on_updated()
            self.dialog.destroy()
        else:
            messagebox.showerror("Update Failed", "Could not update document.", parent=self.dialog)

    def _handle_export(self):
        orig_filename = self.doc.get("filename", "document")
        target_path = filedialog.asksaveasfilename(
            parent=self.dialog,
            title="Save a Copy (Export Document)",
            initialfile=orig_filename,
        )
        if target_path:
            success = self.doc_service.export_document(self.doc_id, self.user_id, target_path)
            if success:
                messagebox.showinfo("Export Successful", f"A copy has been saved to:\n{target_path}", parent=self.dialog)
            else:
                messagebox.showerror("Export Failed", "Could not export document.", parent=self.dialog)

    def _handle_delete(self):
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete '{self.doc['title']}'?\n\nThis will remove the document and its stored file from your vault.",
            parent=self.dialog,
        )
        if confirm:
            success = self.doc_service.delete_document(self.doc_id, self.user_id)
            if success:
                messagebox.showinfo("Document Deleted", "Document has been removed from your vault.", parent=self.dialog)
                self.on_deleted()
                self.dialog.destroy()
            else:
                messagebox.showerror("Delete Failed", "Could not delete document.", parent=self.dialog)
