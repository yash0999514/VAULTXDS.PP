"""Small, dependency-free calendar picker for VAULTX date fields."""

import calendar
from datetime import date, datetime
from typing import Optional

from app.ui.common import UITheme
from app.ui.tk_compat import tk


def open_date_picker(parent, variable, title: str = "Choose a date") -> None:
    """Open a compact calendar and place the selected date in a StringVar.

    Dates are stored in the existing VAULTX format: YYYY-MM-DD.
    """
    popup = tk.Toplevel(parent)
    popup.title(title)
    popup.resizable(False, False)
    popup.configure(bg=UITheme.BG_LIGHT)
    popup.transient(parent)
    popup.grab_set()

    today = date.today()
    selected: Optional[date] = None
    raw_value = (variable.get() or "").strip()

    if raw_value:
        try:
            selected = datetime.strptime(raw_value[:10], "%Y-%m-%d").date()
        except ValueError:
            selected = None

    current_year = (selected or today).year
    current_month = (selected or today).month

    header = tk.Frame(popup, bg=UITheme.PRIMARY, padx=12, pady=10)
    header.pack(fill="x")

    month_label = tk.Label(
        header,
        text="",
        font=UITheme.FONT_BODY_BOLD,
        bg=UITheme.PRIMARY,
        fg="white",
        width=18
    )
    month_label.pack(side="left", expand=True)

    calendar_frame = tk.Frame(
        popup,
        bg=UITheme.BG_LIGHT,
        padx=12,
        pady=10
    )
    calendar_frame.pack(fill="both", expand=True)

    def choose_day(day: int):
        variable.set(
            f"{current_year:04d}-{current_month:02d}-{day:02d}"
        )
        popup.destroy()

    def clear_date():
        variable.set("")
        popup.destroy()

    def change_month(offset: int):
        nonlocal current_year, current_month

        current_month += offset

        if current_month < 1:
            current_month = 12
            current_year -= 1
        elif current_month > 12:
            current_month = 1
            current_year += 1

        render_calendar()

    tk.Button(
        header,
        text="‹",
        font=UITheme.FONT_BODY_BOLD,
        width=3,
        bg=UITheme.PRIMARY,
        fg="white",
        relief="flat",
        cursor="hand2",
        command=lambda: change_month(-1)
    ).pack(side="left", before=month_label)

    tk.Button(
        header,
        text="›",
        font=UITheme.FONT_BODY_BOLD,
        width=3,
        bg=UITheme.PRIMARY,
        fg="white",
        relief="flat",
        cursor="hand2",
        command=lambda: change_month(1)
    ).pack(side="right")

    def render_calendar():
        for child in calendar_frame.winfo_children():
            child.destroy()

        for child in popup.winfo_children():
            if child not in (header, calendar_frame):
                child.destroy()

        month_label.configure(
            text=f"{calendar.month_name[current_month]} {current_year}"
        )

        weekdays = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]

        for col, name in enumerate(weekdays):
            tk.Label(
                calendar_frame,
                text=name,
                width=4,
                font=UITheme.FONT_SMALL_BOLD,
                bg=UITheme.BG_LIGHT,
                fg=UITheme.TEXT_MUTED
            ).grid(
                row=0,
                column=col,
                padx=1,
                pady=(0, 5)
            )

        for row, week in enumerate(
            calendar.monthcalendar(current_year, current_month),
            start=1
        ):
            for col, day_number in enumerate(week):
                if day_number == 0:
                    tk.Label(
                        calendar_frame,
                        text="",
                        width=4,
                        bg=UITheme.BG_LIGHT
                    ).grid(
                        row=row,
                        column=col,
                        padx=1,
                        pady=1
                    )
                    continue

                is_today = (
                    current_year,
                    current_month,
                    day_number
                ) == (
                    today.year,
                    today.month,
                    today.day
                )

                is_selected = selected and (
                    current_year,
                    current_month,
                    day_number
                ) == (
                    selected.year,
                    selected.month,
                    selected.day
                )

                bg = (
                    UITheme.PRIMARY
                    if is_selected
                    else UITheme.SURFACE_ALT
                )

                fg = (
                    "white"
                    if is_selected
                    else UITheme.TEXT_MAIN
                )

                if is_today and not is_selected:
                    bg = "#dbeafe"

                tk.Button(
                    calendar_frame,
                    text=str(day_number),
                    width=4,
                    font=UITheme.FONT_SMALL,
                    bg=bg,
                    fg=fg,
                    relief="flat",
                    cursor="hand2",
                    command=lambda d=day_number: choose_day(d)
                ).grid(
                    row=row,
                    column=col,
                    padx=1,
                    pady=1
                )

        footer = tk.Frame(
            popup,
            bg=UITheme.BG_LIGHT,
            padx=12,
            pady=10
        )
        footer.pack(fill="x")

        tk.Button(
            footer,
            text="Clear date",
            font=UITheme.FONT_SMALL,
            bg=UITheme.SURFACE_ALT,
            fg=UITheme.TEXT_MAIN,
            relief="flat",
            cursor="hand2",
            command=clear_date
        ).pack(side="left")

        tk.Button(
            footer,
            text="Today",
            font=UITheme.FONT_SMALL_BOLD,
            bg=UITheme.PRIMARY,
            fg="white",
            relief="flat",
            cursor="hand2",
            command=lambda: choose_specific_date(today)
        ).pack(side="right")

    def choose_specific_date(chosen: date):
        variable.set(chosen.strftime("%Y-%m-%d"))
        popup.destroy()

    render_calendar()
    popup.update_idletasks()

    # Position the date picker near the parent application window
    parent.update_idletasks()

    popup_width = popup.winfo_width()
    popup_height = popup.winfo_height()

    parent_x = parent.winfo_rootx()
    parent_y = parent.winfo_rooty()
    parent_width = parent.winfo_width()
    parent_height = parent.winfo_height()

    x = parent_x + (parent_width - popup_width) // 2
    y = parent_y + (parent_height - popup_height) // 2

    popup.geometry(f"+{x}+{y}")