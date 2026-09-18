"""Common UI theme constants, layout helpers, and formatting utilities."""

import platform
from datetime import datetime
from typing import Optional


def sys_is_windows() -> bool:
    """Return True if running on a Windows operating system."""
    return platform.system().lower().startswith("win")


class UITheme:
    """Premium color palette and visual styling configuration for VAULTX.

    Inspired by modern desktop productivity software (Notion, Linear, OneDrive).
    """

    # Primary & Accents
    PRIMARY = "#2563eb"        # Modern Royal Blue
    PRIMARY_HOVER = "#1d4ed8"  # Darker Blue
    PRIMARY_LIGHT = "#eff6ff"  # Soft Blue Tint

    # Neutral Dark (Sidebar / Branding / Headings)
    BRAND_NAVY = "#0f172a"     # Deepest Slate 900
    SIDEBAR_BG = "#1e293b"     # Slate 800
    SIDEBAR_ACTIVE = "#334155" # Slate 700 active item
    SIDEBAR_HOVER = "#243247"

    # Neutral Surfaces & Backgrounds
    BG_LIGHT = "#f8fafc"       # Soft Canvas Off-White (Slate 50)
    SURFACE_LIGHT = "#ffffff"  # Clean White Card
    SURFACE_ALT = "#f1f5f9"    # Light Pill Background (Slate 100)

    # Borders & Dividers
    BORDER_LIGHT = "#e2e8f0"   # Subtle Slate 200 Border
    BORDER_DARK = "#cbd5e1"    # Slate 300

    # Typography Colors
    TEXT_MAIN = "#0f172a"      # High-contrast Slate 900
    TEXT_SECONDARY = "#334155" # Slate 700
    TEXT_MUTED = "#64748b"     # Slate 500
    TEXT_ON_DARK = "#f8fafc"   # White / Slate 50
    TEXT_ON_DARK_MUTED = "#94a3b8" # Slate 400

    # Semantic Status Colors
    SUCCESS = "#10b981"        # Emerald Green
    SUCCESS_BG = "#ecfdf5"
    WARNING = "#f59e0b"        # Amber
    WARNING_BG = "#fffbeb"
    DANGER = "#ef4444"         # Crimson Red
    DANGER_BG = "#fef2f2"
    INFO = "#0284c7"           # Sky Blue
    INFO_BG = "#f0f9ff"

    # Typography Hierarchy (Windows Segoe UI / Fallback)
    FONT_FAMILY = "Segoe UI" if sys_is_windows() else "Helvetica"
    FONT_DISPLAY = (FONT_FAMILY, 18, "bold")
    FONT_TITLE = (FONT_FAMILY, 15, "bold")
    FONT_SUBTITLE = (FONT_FAMILY, 12, "bold")
    FONT_BODY = (FONT_FAMILY, 10)
    FONT_BODY_BOLD = (FONT_FAMILY, 10, "bold")
    FONT_SMALL = (FONT_FAMILY, 9)
    FONT_SMALL_BOLD = (FONT_FAMILY, 9, "bold")
    FONT_MONO = ("Consolas", 9)


def format_file_size(size_bytes: int) -> str:
    """Format byte size into human-readable representation."""
    if size_bytes <= 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB"]
    size = float(size_bytes)
    unit_idx = 0
    while size >= 1024 and unit_idx < len(units) - 1:
        size /= 1024.0
        unit_idx += 1
    return f"{size:.1f} {units[unit_idx]}" if unit_idx > 0 else f"{int(size)} B"


def format_date(date_str: Optional[str]) -> str:
    """Format ISO date string (YYYY-MM-DD) into readable date."""
    if not date_str or not date_str.strip():
        return "None"
    try:
        dt = datetime.strptime(date_str.strip()[:10], "%Y-%m-%d")
        return dt.strftime("%b %d, %Y")
    except ValueError:
        return date_str
