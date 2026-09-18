"""Add Document Dialog with friendly non-technical guidance and automated text extraction."""

from pathlib import Path
from typing import Callable, Optional
from app.services.document_service import DocumentService
from app.ui.common import UITheme
from app.ui.tk_compat import tk, ttk, filedialog, messagebox
from app.ui.date_picker import open_date_picker


class AddDocumentDialog:
    """Modal dialog for selecting, organizing, and securing personal documents."""

    def __init__(self, parent: tk.Tk, user_id: int, doc_service: DocumentService, on_document_added: Callable[[], None]):
        self.parent = parent
        self.user_id = user_id
        self.doc_service = doc_service
        self.on_document_added = on_document_added

        self.selected_file_path: Optional[str] = None

        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Add Document — VAULTX")
        self.dialog.geometry("580x680")
        self.dialog.resizable(False, False)
        self.dialog.configure(bg=UITheme.BG_LIGHT)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        self._center_window()
        self._build_ui()

    def _center_window(self):
        self.dialog.update_idletasks()
        w = 580
        h = 680
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (w // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (h // 2)
        self.dialog.geometry(f"{w}x{h}+{max(0, x)}+{max(0, y)}")

    def _build_ui(self):
        # Header Banner
        header = tk.Frame(self.dialog, bg=UITheme.PRIMARY, height=60)
        header.pack(fill="x")
        tk.Label(
            header, text="➕ Add a New Document",
            font=UITheme.FONT_SUBTITLE, fg="white", bg=UITheme.PRIMARY, padx=20, pady=15
        ).pack(anchor="w")

        body = tk.Frame(self.dialog, bg=UITheme.BG_LIGHT, padx=25, pady=15)
        body.pack(fill="both", expand=True)

        # File Selection row
        tk.Label(body, text="Select File *", font=UITheme.FONT_BODY_BOLD, bg=UITheme.BG_LIGHT, fg=UITheme.TEXT_MAIN).pack(anchor="w", pady=(0, 2))
        file_frame = tk.Frame(body, bg=UITheme.BG_LIGHT)
        file_frame.pack(fill="x", pady=(0, 10))

        self.file_lbl_var = tk.StringVar(value="No file selected yet...")
        lbl_file = tk.Label(
            file_frame, textvariable=self.file_lbl_var, font=UITheme.FONT_SMALL,
            bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MUTED, anchor="w", relief="solid", bd=1, padx=8, pady=6
        )
        lbl_file.pack(side="left", fill="x", expand=True, padx=(0, 8))

        btn_browse = tk.Button(
            file_frame, text="Browse...", font=UITheme.FONT_BODY, bg=UITheme.SURFACE_ALT, fg=UITheme.TEXT_MAIN,
            relief="flat", cursor="hand2", padx=14, command=self._select_file
        )
        btn_browse.pack(side="right")

        # Document Title
        tk.Label(body, text="Document Title *", font=UITheme.FONT_BODY_BOLD, bg=UITheme.BG_LIGHT, fg=UITheme.TEXT_MAIN).pack(anchor="w", pady=(0, 2))
        self.title_var = tk.StringVar()
        ttk.Entry(body, textvariable=self.title_var, font=UITheme.FONT_BODY).pack(fill="x", pady=(0, 10))

        # Category Row
        tk.Label(body, text="Category *", font=UITheme.FONT_BODY_BOLD, bg=UITheme.BG_LIGHT, fg=UITheme.TEXT_MAIN).pack(anchor="w", pady=(0, 2))
        cat_frame = tk.Frame(body, bg=UITheme.BG_LIGHT)
        cat_frame.pack(fill="x", pady=(0, 10))

        self.categories = self.doc_service.get_categories(self.user_id)
        if not self.categories:
            self.categories = ["General", "Identity & Legal", "Academic & Certificates", "Finance & Tax"]
        self.category_var = tk.StringVar(value=self.categories[0])
        self.cat_combo = ttk.Combobox(cat_frame, textvariable=self.category_var, values=self.categories, state="readonly", font=UITheme.FONT_BODY)
        self.cat_combo.pack(side="left", fill="x", expand=True, padx=(0, 8))

        btn_new_cat = tk.Button(
            cat_frame, text="+ New Category", font=UITheme.FONT_SMALL, bg=UITheme.SURFACE_ALT, fg=UITheme.TEXT_MAIN,
            relief="flat", cursor="hand2", padx=8, command=self._prompt_new_category
        )
        btn_new_cat.pack(side="right")

        # Expiry Date (Valid Until)
        tk.Label(body, text="Valid Until (Optional)", font=UITheme.FONT_BODY_BOLD, bg=UITheme.BG_LIGHT, fg=UITheme.TEXT_MAIN).pack(anchor="w", pady=(0, 2))
        expiry_frame = tk.Frame(body, bg=UITheme.BG_LIGHT)
        expiry_frame.pack(fill="x", pady=(0, 10))
        self.expiry_var = tk.StringVar()
        ttk.Entry(expiry_frame, textvariable=self.expiry_var, font=UITheme.FONT_BODY).pack(side="left", fill="x", expand=True, padx=(0, 8))
        tk.Button(
            expiry_frame, text="📅 Choose date", font=UITheme.FONT_SMALL,
            bg=UITheme.SURFACE_ALT, fg=UITheme.TEXT_MAIN, relief="flat",
            cursor="hand2", padx=8, command=lambda: open_date_picker(self.dialog, self.expiry_var)
        ).pack(side="right")
        tk.Label(body, text="Choose a date from the calendar or leave it blank.", font=UITheme.FONT_SMALL, bg=UITheme.BG_LIGHT, fg=UITheme.TEXT_MUTED).pack(anchor="w", pady=(0, 8))

        # Tags
        tk.Label(body, text="Tags (comma-separated, e.g. college, bill, policy)", font=UITheme.FONT_BODY_BOLD, bg=UITheme.BG_LIGHT, fg=UITheme.TEXT_MAIN).pack(anchor="w", pady=(0, 2))
        self.tags_var = tk.StringVar()
        ttk.Entry(body, textvariable=self.tags_var, font=UITheme.FONT_BODY).pack(fill="x", pady=(0, 10))

        # Notes
        tk.Label(body, text="Notes (Optional)", font=UITheme.FONT_BODY_BOLD, bg=UITheme.BG_LIGHT, fg=UITheme.TEXT_MAIN).pack(anchor="w", pady=(0, 2))
        self.desc_text = tk.Text(body, height=4, font=UITheme.FONT_BODY, wrap="word", relief="solid", bd=1)
        self.desc_text.pack(fill="x", pady=(0, 10))

        # Checkboxes
        check_frame = tk.Frame(body, bg=UITheme.BG_LIGHT)
        check_frame.pack(fill="x", pady=(0, 15))

        self.fav_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(check_frame, text="⭐ Add to Favorites", variable=self.fav_var).pack(side="left", padx=(0, 15))

        self.ocr_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(check_frame, text="🔍 Make text inside document searchable", variable=self.ocr_var).pack(side="left")

        # Action Buttons
        btn_frame = tk.Frame(body, bg=UITheme.BG_LIGHT)
        btn_frame.pack(fill="x", pady=(10, 0))

        btn_cancel = tk.Button(
            btn_frame, text="Cancel", font=UITheme.FONT_BODY, bg=UITheme.SURFACE_ALT, fg=UITheme.TEXT_MAIN,
            relief="flat", cursor="hand2", padx=15, pady=8, command=self.dialog.destroy
        )
        btn_cancel.pack(side="right", padx=(8, 0))

        self.btn_submit = tk.Button(
            btn_frame, text="Save Document", font=UITheme.FONT_BODY_BOLD, bg=UITheme.PRIMARY, fg="white",
            relief="flat", cursor="hand2", padx=20, pady=8, command=self._save_document
        )
        self.btn_submit.pack(side="right")

    def _select_file(self):
        filetypes = [
            ("All Supported Files", "*.pdf;*.png;*.jpg;*.jpeg;*.txt;*.docx;*.csv;*.json;*.md"),
            ("PDF Documents (*.pdf)", "*.pdf"),
            ("Images (*.png;*.jpg;*.jpeg)", "*.png;*.jpg;*.jpeg;*.bmp"),
            ("Text Files (*.txt;*.md;*.csv)", "*.txt;*.md;*.csv"),
            ("All Files (*.*)", "*.*"),
        ]
        selected = filedialog.askopenfilename(parent=self.dialog, title="Select Document", filetypes=filetypes)
        if selected:
            self.selected_file_path = selected
            self.file_lbl_var.set(Path(selected).name)
            if not self.title_var.get().strip():
                clean_name = Path(selected).stem.replace("_", " ").title()
                self.title_var.set(clean_name)

    def _prompt_new_category(self):
        new_cat = simple_input_dialog(self.dialog, "New Category", "Enter category name:")
        if new_cat and new_cat.strip():
            clean_cat = new_cat.strip()
            self.doc_service.cat_repo.add_category(self.user_id, clean_cat)
            self.categories = self.doc_service.get_categories(self.user_id)
            self.cat_combo.configure(values=self.categories)
            self.category_var.set(clean_cat)

    def _save_document(self):
        if not self.selected_file_path or not Path(self.selected_file_path).exists():
            messagebox.showwarning("File Required", "Please select a file to save.", parent=self.dialog)
            return

        title = self.title_var.get().strip()
        if not title:
            messagebox.showwarning("Title Required", "Please enter a document title.", parent=self.dialog)
            return

        category = self.category_var.get().strip() or "General"
        tags = self.tags_var.get().strip()
        description = self.desc_text.get("1.0", "end-1c").strip()
        expiry_date = self.expiry_var.get().strip() or None

        if expiry_date:
            import re
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", expiry_date):
                messagebox.showerror(
                    "Invalid Date Format",
                    "Please enter date in YYYY-MM-DD format (e.g. 2026-10-15).",
                    parent=self.dialog,
                )
                return

        self.btn_submit.configure(text="Saving...", state="disabled")
        self.dialog.update()

        try:
            doc_id = self.doc_service.store_document(
                user_id=self.user_id,
                title=title,
                file_path=self.selected_file_path,
                category=category,
                tags=tags,
                description=description,
                expiry_date=expiry_date,
                perform_ocr=self.ocr_var.get(),
            )
            if self.fav_var.get():
                self.doc_service.toggle_favorite(doc_id, self.user_id)

            messagebox.showinfo(
                "Document Saved",
                f"'{title}' has been safely stored in your vault!",
                parent=self.dialog,
            )
            self.on_document_added()
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Save Failed", f"Could not save document: {str(e)}", parent=self.dialog)
            self.btn_submit.configure(text="Save Document", state="normal")


def simple_input_dialog(parent: tk.Toplevel, title: str, prompt: str) -> Optional[str]:
    inp_win = tk.Toplevel(parent)
    inp_win.title(title)
    inp_win.geometry("380x150")
    inp_win.resizable(False, False)
    inp_win.transient(parent)
    inp_win.grab_set()

    result = None

    def on_ok():
        nonlocal result
        result = val_var.get()
        inp_win.destroy()

    tk.Label(inp_win, text=prompt, font=UITheme.FONT_BODY, padx=15, pady=10).pack(anchor="w")
    val_var = tk.StringVar()
    ent = ttk.Entry(inp_win, textvariable=val_var, font=UITheme.FONT_BODY)
    ent.pack(fill="x", padx=15, pady=5)
    ent.focus()

    btn_box = tk.Frame(inp_win, padx=15, pady=10)
    btn_box.pack(fill="x")
    tk.Button(btn_box, text="OK", font=UITheme.FONT_BODY, bg=UITheme.PRIMARY, fg="white", padx=12, command=on_ok).pack(side="right")
    tk.Button(btn_box, text="Cancel", font=UITheme.FONT_BODY, padx=12, command=inp_win.destroy).pack(side="right", padx=(0, 8))

    inp_win.wait_window()
    return result
