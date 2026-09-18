"""Tkinter and ttkbootstrap compatibility layer with safe fallback stubs for headless environments."""

import sys

TKINTER_AVAILABLE = False
TTKBOOTSTRAP_AVAILABLE = False

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    TKINTER_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    class _TkMock:
        def __getattr__(self, name):
            return object

    tk = _TkMock()
    tk.Tk = object
    tk.Frame = object
    tk.Toplevel = object
    tk.Button = object
    tk.Label = object
    tk.Text = object
    tk.StringVar = object
    tk.BooleanVar = object

    ttk = _TkMock()
    ttk.Entry = object
    ttk.Combobox = object
    ttk.Notebook = object
    ttk.Treeview = object
    ttk.Checkbutton = object
    ttk.Scrollbar = object

    messagebox = _TkMock()
    filedialog = _TkMock()

if TKINTER_AVAILABLE:
    try:
        import ttkbootstrap as tb
        from ttkbootstrap.constants import *
        TTKBOOTSTRAP_AVAILABLE = True
    except (ImportError, ModuleNotFoundError):
        tb = None
else:
    tb = None


def is_gui_supported() -> bool:
    """Check if the current runtime environment has Tkinter and graphical display available."""
    if not TKINTER_AVAILABLE:
        return False
    try:
        root = tk.Tk()
        root.withdraw()
        root.destroy()
        return True
    except Exception:
        return False
