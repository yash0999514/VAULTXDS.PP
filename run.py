#!/usr/bin/env python3
"""Main startup launcher for VAULTX — Secure Personal Document Management System."""

import os
import sys

# Ensure package root is in python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.main import launch_gui, launch_cli_demo


def main():
    """Startup routine."""
    if len(sys.argv) > 1 and sys.argv[1] in ("--cli", "-c", "--demo"):
        launch_cli_demo()
    else:
        launch_gui()


if __name__ == "__main__":
    main()
