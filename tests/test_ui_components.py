"""Tests verifying UI modules structure, imports, and layout contracts."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.ui.common import UITheme, format_file_size, format_date


class TestUIModules(unittest.TestCase):

    def test_ui_common_utilities(self):
        # File size formatting
        self.assertEqual(format_file_size(0), "0 B")
        self.assertEqual(format_file_size(500), "500 B")
        self.assertEqual(format_file_size(2048), "2.0 KB")
        self.assertEqual(format_file_size(1048576 * 3), "3.0 MB")

        # Date formatting
        self.assertEqual(format_date(""), "None")
        self.assertEqual(format_date(None), "None")
        self.assertEqual(format_date("2026-10-15"), "Oct 15, 2026")

        # Palette colors existence
        self.assertTrue(UITheme.PRIMARY.startswith("#"))
        self.assertTrue(UITheme.SUCCESS.startswith("#"))
        self.assertTrue(UITheme.DANGER.startswith("#"))
        self.assertTrue(UITheme.SIDEBAR_BG.startswith("#"))

    def test_ui_modules_import_cleanly(self):
        """Ensure all UI modules import without syntax or circular dependency errors."""
        import app.ui.auth_window
        import app.ui.auth_screen
        import app.ui.main_window
        import app.ui.home_page
        import app.ui.documents_page
        import app.ui.add_document_dialog
        import app.ui.document_details_dialog
        import app.ui.search_page
        import app.ui.favorites_page
        import app.ui.expiry_page
        import app.ui.settings_page
        import app.ui.tech_info_page

        self.assertIsNotNone(app.ui.auth_window.AuthWindow)
        self.assertIsNotNone(app.ui.main_window.MainWindow)
        self.assertIsNotNone(app.ui.home_page.HomePage)
        self.assertIsNotNone(app.ui.tech_info_page.TechInfoPage)


if __name__ == "__main__":
    unittest.main()
