"""Authentication Window supporting compulsory Email registration and dual Email/Username Login."""

from typing import Callable, Optional
from app.database.auth_repository import AuthRepository, is_valid_email
from app.ui.common import UITheme
from app.ui.tk_compat import TKINTER_AVAILABLE, tk, ttk, messagebox


class AuthWindow:
    """Provides modern card-based Login and Registration dialogs."""

    def __init__(self, auth_repo: AuthRepository, on_login_success: Callable[[dict], None]):
        self.auth_repo = auth_repo
        self.on_login_success = on_login_success
        self.root: Optional[tk.Tk] = None

    def start(self):
        """Display the authentication interface."""
        if not TKINTER_AVAILABLE:
            raise RuntimeError("Tkinter is required to launch the graphical desktop interface.")

        self.root = tk.Tk()
        self.root.title("VAULTX — Secure Document Management System")
        self.root.geometry("500x610")
        self.root.resizable(False, False)
        self.root.configure(bg=UITheme.BG_LIGHT)

        # Center on screen
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

        self._build_ui()
        self.root.mainloop()

    def _build_ui(self):
        # Header banner
        header = tk.Frame(self.root, bg=UITheme.PRIMARY, height=92)
        header.pack(fill="x")

        title_lbl = tk.Label(
            header,
            text="🔒 VAULTX",
            font=(UITheme.FONT_FAMILY, 20, "bold"),
            fg="white",
            bg=UITheme.PRIMARY,
        )
        title_lbl.pack(pady=(14, 2))

        subtitle_lbl = tk.Label(
            header,
            text="Secure Personal Document Management System",
            font=UITheme.FONT_SMALL,
            fg="#bfdbfe",
            bg=UITheme.PRIMARY,
        )
        subtitle_lbl.pack(pady=(0, 14))

        # Card container
        container = tk.Frame(self.root, bg=UITheme.BG_LIGHT, padx=25, pady=15)
        container.pack(fill="both", expand=True)

        self.notebook = ttk.Notebook(container)
        self.notebook.pack(fill="both", expand=True)

        self.login_tab = tk.Frame(self.notebook, bg=UITheme.SURFACE_LIGHT, padx=22, pady=18)
        self.register_tab = tk.Frame(self.notebook, bg=UITheme.SURFACE_LIGHT, padx=22, pady=18)

        self.notebook.add(self.login_tab, text="   Sign In   ")
        self.notebook.add(self.register_tab, text="   Create Account   ")

        self._build_login_tab()
        self._build_register_tab()

    def _build_login_tab(self):
        tk.Label(
            self.login_tab,
            text="Sign in to your Vault",
            font=UITheme.FONT_SUBTITLE,
            bg=UITheme.SURFACE_LIGHT,
            fg=UITheme.TEXT_MAIN,
        ).pack(anchor="w", pady=(0, 14))

        # Email / Username identifier
        tk.Label(
            self.login_tab, text="Email Address or Username *", font=UITheme.FONT_BODY_BOLD,
            bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MUTED
        ).pack(anchor="w", pady=(4, 2))
        self.login_id_var = tk.StringVar()
        user_ent = ttk.Entry(self.login_tab, textvariable=self.login_id_var, font=UITheme.FONT_BODY)
        user_ent.pack(fill="x", pady=(0, 10))

        # Password
        tk.Label(
            self.login_tab, text="Password *", font=UITheme.FONT_BODY_BOLD,
            bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MUTED
        ).pack(anchor="w", pady=(4, 2))
        self.login_pass_var = tk.StringVar()
        self.login_pass_ent = ttk.Entry(
            self.login_tab, textvariable=self.login_pass_var, font=UITheme.FONT_BODY, show="●"
        )
        self.login_pass_ent.pack(fill="x", pady=(0, 5))

        # Show password toggle
        self.show_pass_login = tk.BooleanVar(value=False)
        chk = ttk.Checkbutton(
            self.login_tab, text="Show password", variable=self.show_pass_login,
            command=lambda: self.login_pass_ent.configure(show="" if self.show_pass_login.get() else "●")
        )
        chk.pack(anchor="w", pady=(0, 14))

        # Login button
        btn_login = tk.Button(
            self.login_tab, text="Sign In with Email / Username", bg=UITheme.PRIMARY, fg="white",
            font=UITheme.FONT_BODY_BOLD, relief="flat", cursor="hand2",
            padx=10, pady=8, command=self._handle_login
        )
        btn_login.pack(fill="x", pady=(5, 10))

        # Demo button
        btn_demo = tk.Button(
            self.login_tab, text="⚡ Quick College Demo Login (student@vaultx.local)",
            bg=UITheme.SURFACE_ALT, fg=UITheme.TEXT_MAIN, font=UITheme.FONT_SMALL,
            relief="solid", bd=1, cursor="hand2", pady=5, command=self._handle_demo_login
        )
        btn_demo.pack(fill="x", pady=(4, 0))

    def _build_register_tab(self):
        tk.Label(
            self.register_tab,
            text="Create a New Secure Vault",
            font=UITheme.FONT_SUBTITLE,
            bg=UITheme.SURFACE_LIGHT,
            fg=UITheme.TEXT_MAIN,
        ).pack(anchor="w", pady=(0, 10))

        # Username
        tk.Label(
            self.register_tab, text="Username *", font=UITheme.FONT_BODY_BOLD,
            bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MUTED
        ).pack(anchor="w", pady=(2, 2))
        self.reg_user_var = tk.StringVar()
        ttk.Entry(self.register_tab, textvariable=self.reg_user_var, font=UITheme.FONT_BODY).pack(fill="x", pady=(0, 6))

        # Email (COMPULSORY)
        tk.Label(
            self.register_tab, text="Email Address * (Compulsory)", font=UITheme.FONT_BODY_BOLD,
            bg=UITheme.SURFACE_LIGHT, fg=UITheme.PRIMARY
        ).pack(anchor="w", pady=(2, 2))
        self.reg_email_var = tk.StringVar()
        ttk.Entry(self.register_tab, textvariable=self.reg_email_var, font=UITheme.FONT_BODY).pack(fill="x", pady=(0, 6))

        # Password
        tk.Label(
            self.register_tab, text="Password (min 6 chars) *", font=UITheme.FONT_BODY_BOLD,
            bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MUTED
        ).pack(anchor="w", pady=(2, 2))
        self.reg_pass_var = tk.StringVar()
        self.reg_pass_ent = ttk.Entry(self.register_tab, textvariable=self.reg_pass_var, font=UITheme.FONT_BODY, show="●")
        self.reg_pass_ent.pack(fill="x", pady=(0, 6))

        # Confirm Password
        tk.Label(
            self.register_tab, text="Confirm Password *", font=UITheme.FONT_BODY_BOLD,
            bg=UITheme.SURFACE_LIGHT, fg=UITheme.TEXT_MUTED
        ).pack(anchor="w", pady=(2, 2))
        self.reg_confirm_var = tk.StringVar()
        self.reg_confirm_ent = ttk.Entry(self.register_tab, textvariable=self.reg_confirm_var, font=UITheme.FONT_BODY, show="●")
        self.reg_confirm_ent.pack(fill="x", pady=(0, 6))

        # Show password toggle for registration
        self.show_pass_register = tk.BooleanVar(value=False)
        chk_register = ttk.Checkbutton(
            self.register_tab,
            text="Show password",
            variable=self.show_pass_register,
            command=lambda: self._toggle_register_passwords()
        )
        chk_register.pack(anchor="w", pady=(0, 10))

        btn_reg = tk.Button(
            self.register_tab, text="Create Account & Initialize Vault",
            bg=UITheme.SUCCESS, fg="white", font=UITheme.FONT_BODY_BOLD,
            relief="flat", cursor="hand2", padx=10, pady=8, command=self._handle_register
        )
        btn_reg.pack(fill="x", pady=(4, 0))

    def _toggle_register_passwords(self):
        show_value = "" if self.show_pass_register.get() else "●"
        self.reg_pass_ent.configure(show=show_value)
        self.reg_confirm_ent.configure(show=show_value)

    def _handle_login(self):
        identifier = self.login_id_var.get().strip()
        password = self.login_pass_var.get()
        if not identifier:
            messagebox.showwarning("Email Required", "Please enter your email address or username to sign in.")
            return
        if not password:
            messagebox.showwarning("Password Required", "Please enter your password.")
            return

        success, msg, user_data = self.auth_repo.authenticate(identifier, password)
        if success and user_data:
            if self.root:
                self.root.destroy()
            self.on_login_success(user_data)
        else:
            messagebox.showerror("Authentication Failed", msg or "Invalid email/username or password.")

    def _handle_demo_login(self):
        demo_user = "student"
        demo_email = "student@vaultx.local"
        demo_pass = "vaultx2026"
        # Ensure demo user is registered with valid email
        self.auth_repo.register(demo_user, demo_pass, demo_email)
        success, msg, user_data = self.auth_repo.authenticate(demo_email, demo_pass)
        if success and user_data:
            if self.root:
                self.root.destroy()
            self.on_login_success(user_data)

    def _handle_register(self):
        username = self.reg_user_var.get().strip()
        email = self.reg_email_var.get().strip()
        password = self.reg_pass_var.get()
        confirm = self.reg_confirm_var.get()

        if not username:
            messagebox.showwarning("Validation Error", "Username is required.")
            return
        if not email:
            messagebox.showwarning("Validation Error", "Email address is compulsory for account registration.")
            return
        if not is_valid_email(email):
            messagebox.showerror("Invalid Email", "Please provide a valid email format (e.g. yourname@domain.com).")
            return
        if len(password) < 6:
            messagebox.showwarning("Validation Error", "Password must be at least 6 characters long.")
            return
        if password != confirm:
            messagebox.showerror("Validation Error", "Passwords do not match.")
            return

        success, msg, user_id = self.auth_repo.register(username, password, email)
        if success:
            messagebox.showinfo("Account Created", f"{msg} You may now sign in using your email address.")
            self.login_id_var.set(email)
            self.login_pass_var.set("")
            self.notebook.select(self.login_tab)
        else:
            messagebox.showerror("Registration Failed", msg)
