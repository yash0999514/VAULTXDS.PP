"""Comprehensive Integration Tests for all VAULTX core services, persistence, and data structure synchronization."""

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.connection import set_db_path
from app.database.schema import init_database
from app.database.auth_repository import AuthRepository
from app.database.category_repository import CategoryRepository
from app.database.document_repository import DocumentRepository
from app.services.encryption_service import DecryptionError, EncryptionService
from app.services.document_service import DocumentService


class TestVAULTXFeaturesComprehensive(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.dir_path = Path(self.temp_dir.name)

        # Isolated test database
        self.test_db = self.dir_path / "test_vaultx.db"
        set_db_path(self.test_db)
        init_database()

        # Isolated keys and storage directories
        self.key_path = self.dir_path / "test_vault.key"
        self.storage_dir = self.dir_path / "test_documents"

        self.auth_repo = AuthRepository()
        self.cat_repo = CategoryRepository()
        self.doc_repo = DocumentRepository()
        self.doc_service = DocumentService(
            storage_dir=str(self.storage_dir),
            key_path=str(self.key_path),
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    # ---------------- 1. AUTHENTICATION & SECURITY ----------------
    def test_authentication_workflow_and_password_reset(self):
        # Registration with compulsory email
        success, msg, user_id = self.auth_repo.register("testuser", "securepass123", "test@example.com")
        self.assertTrue(success)
        self.assertIsNotNone(user_id)

        # Duplicate username rejection
        dup_success, dup_msg, _ = self.auth_repo.register("testuser", "anotherpass", "other@example.com")
        self.assertFalse(dup_success)

        # Duplicate email rejection
        dup_email_success, _, _ = self.auth_repo.register("uniqueuser", "anotherpass", "test@example.com")
        self.assertFalse(dup_email_success)

        # Compulsory email missing
        empty_email_success, _, _ = self.auth_repo.register("user2", "securepass123", "")
        self.assertFalse(empty_email_success)

        # Invalid email format
        bad_email_success, _, _ = self.auth_repo.register("user3", "securepass123", "invalid-email")
        self.assertFalse(bad_email_success)

        # Password length validation (minimum 6 characters)
        short_success, _, _ = self.auth_repo.register("user4", "12345", "user4@example.com")
        self.assertFalse(short_success)

        # Empty username rejection
        empty_success, _, _ = self.auth_repo.register("", "securepass123", "empty@example.com")
        self.assertFalse(empty_success)

        # Successful login using Email
        login_email_ok, login_msg, user_data = self.auth_repo.authenticate("test@example.com", "securepass123")
        self.assertTrue(login_email_ok)
        self.assertEqual(user_data["username"], "testuser")
        self.assertEqual(user_data["email"], "test@example.com")

        # Successful login using Username
        login_user_ok, _, user_data = self.auth_repo.authenticate("testuser", "securepass123")
        self.assertTrue(login_user_ok)

        # Failed login with bad password
        bad_login, _, _ = self.auth_repo.authenticate("test@example.com", "wrongpassword")
        self.assertFalse(bad_login)

        # Non-existent email / user
        no_user, _, _ = self.auth_repo.authenticate("ghost@example.com", "pass1234")
        self.assertFalse(no_user)

        # Password update / reset using email
        reset_ok, _ = self.auth_repo.reset_password("test@example.com", "securepass123", "brandnewpass999")
        self.assertTrue(reset_ok)

        # Verify old password no longer works
        old_login, _, _ = self.auth_repo.authenticate("test@example.com", "securepass123")
        self.assertFalse(old_login)

        # Verify new password works
        new_login, _, _ = self.auth_repo.authenticate("test@example.com", "brandnewpass999")
        self.assertTrue(new_login)

    # ---------------- 2. CRYPTOGRAPHIC ENCRYPTION ----------------
    def test_encryption_at_rest_and_tamper_rejection(self):
        enc_service = EncryptionService(key_path=str(self.key_path))
        secret_payload = b"Engineering Subject Data Structures Final Exam 2026"

        # Byte encryption & decryption roundtrip
        ciphertext = enc_service.encrypt_bytes(secret_payload)
        self.assertNotEqual(ciphertext, secret_payload)
        plaintext = enc_service.decrypt_bytes(ciphertext)
        self.assertEqual(plaintext, secret_payload)

        # File encryption & decryption roundtrip
        src_file = self.dir_path / "raw_secret.txt"
        src_file.write_bytes(secret_payload)
        enc_file = self.dir_path / "raw_secret.txt.enc"
        dec_file = self.dir_path / "raw_secret.dec.txt"

        enc_service.encrypt_file(str(src_file), str(enc_file))
        self.assertTrue(enc_file.exists())
        self.assertNotEqual(enc_file.read_bytes(), secret_payload)

        enc_service.decrypt_file(str(enc_file), str(dec_file))
        self.assertEqual(dec_file.read_bytes(), secret_payload)

        # Tampered / Corrupted ciphertext must raise DecryptionError
        corrupted_bytes = bytearray(enc_file.read_bytes())
        corrupted_bytes[20] ^= 0xFF  # Flip bit
        corrupted_file = self.dir_path / "corrupted.enc"
        corrupted_file.write_bytes(bytes(corrupted_bytes))

        with self.assertRaises(DecryptionError):
            enc_service.decrypt_file(str(corrupted_file), str(self.dir_path / "fail.txt"))

        # Missing file handling
        with self.assertRaises(FileNotFoundError):
            enc_service.encrypt_file(str(self.dir_path / "missing.txt"), str(self.dir_path / "out.enc"))

    # ---------------- 3. END-TO-END DOCUMENT LIFECYCLE & DATA STRUCTURE SYNC ----------------
    def test_document_lifecycle_and_data_structure_synchronization(self):
        # 1. Register test user with email
        _, _, user_id = self.auth_repo.register("student1", "pass123456", "student1@example.com")
        self.doc_service.sync_user_indexes(user_id)

        # 2. Prepare sample document file
        sample_file = self.dir_path / "Diploma_Marksheet.txt"
        file_content = "Government Polytechnic Thane - Yash Yogesh Shelar - Diploma in IT"
        sample_file.write_text(file_content, encoding="utf-8")

        # 3. Store document with description and expiry date
        doc_id = self.doc_service.store_document(
            user_id=user_id,
            title="Diploma Semester 3 Marksheet",
            file_path=str(sample_file),
            category="Academic",
            tags="msbte, marksheet, diploma, transcript",
            description="Official semester grade report for direct second year engineering.",
            expiry_date="2026-10-15",
            perform_ocr=True,
        )
        self.assertIsNotNone(doc_id)

        # 4. Verify in-memory HashTable Cache lookup
        cached_doc = self.doc_service.doc_cache.get(doc_id)
        self.assertIsNotNone(cached_doc)
        self.assertEqual(cached_doc.title, "Diploma Semester 3 Marksheet")
        self.assertEqual(cached_doc.description, "Official semester grade report for direct second year engineering.")

        # 5. Verify retrieval updates Doubly-Linked List Recent Access History
        fetched = self.doc_service.get_document(doc_id, user_id, record_access=True)
        self.assertEqual(fetched["title"], "Diploma Semester 3 Marksheet")
        history = self.doc_service.recent_history.get_recent()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["doc_id"], doc_id)

        # 6. Verify Trie Prefix Search
        res_prefix = self.doc_service.search_documents(user_id, "diplo")
        self.assertEqual(len(res_prefix), 1)
        self.assertEqual(res_prefix[0]["id"], doc_id)

        res_tag = self.doc_service.search_documents(user_id, "trans")
        self.assertEqual(len(res_tag), 1)

        res_desc = self.doc_service.search_documents(user_id, "engineering")
        self.assertEqual(len(res_desc), 1)

        res_empty = self.doc_service.search_documents(user_id, "passport")
        self.assertEqual(len(res_empty), 0)

        # 7. Verify Expiry Tracking
        expiring = self.doc_service.get_expiring_documents(days=60)
        self.assertTrue(any(item["doc_id"] == doc_id for item in expiring))

        # 8. Favorite toggle
        self.assertTrue(self.doc_service.toggle_favorite(doc_id, user_id))
        updated_doc = self.doc_service.get_document(doc_id, user_id, record_access=False)
        self.assertTrue(updated_doc["is_favorite"])

        # 9. Update document: verify synchronization across DB, HashTable, and Trie
        update_ok = self.doc_service.update_document(
            doc_id,
            user_id,
            title="Updated Marksheet Certificate",
            tags="updated_tag",
            description="Updated notes without old words",
            expiry_date="2027-01-01",
        )
        self.assertTrue(update_ok)

        # HashTable cache has new title
        self.assertEqual(self.doc_service.doc_cache.get(doc_id).title, "Updated Marksheet Certificate")

        # Trie search matches new title and tag, but not old words
        self.assertEqual(len(self.doc_service.search_documents(user_id, "updated")), 1)
        self.assertEqual(len(self.doc_service.search_documents(user_id, "semester")), 0)

        # 10. Export Decrypted
        export_path = self.dir_path / "Exported_Marksheet.txt"
        export_success = self.doc_service.export_document(doc_id, user_id, str(export_path))
        self.assertTrue(export_success)
        self.assertEqual(export_path.read_text(encoding="utf-8"), file_content)

        # 11. Delete document: verify clean purge across all data structures and disk
        enc_path = Path(self.doc_repo.get_document(doc_id, user_id)["encrypted_path"])
        self.assertTrue(enc_path.exists())

        del_ok = self.doc_service.delete_document(doc_id, user_id)
        self.assertTrue(del_ok)
        self.assertFalse(enc_path.exists())

        # Purged from DB
        self.assertIsNone(self.doc_repo.get_document(doc_id, user_id))
        # Purged from HashTable
        self.assertIsNone(self.doc_service.doc_cache.get(doc_id))
        # Purged from Trie
        self.assertEqual(len(self.doc_service.search_documents(user_id, "updated")), 0)
        # Purged from Expiry Tracker
        self.assertFalse(any(i["doc_id"] == doc_id for i in self.doc_service.get_expiring_documents(days=365)))
        # Purged from LinkedList Recent History
        self.assertEqual(len(self.doc_service.recent_history), 0)

    # ---------------- 4. CATEGORIES & TREE INTEGRATION ----------------
    def test_category_crud_and_tree_sync(self):
        _, _, user_id = self.auth_repo.register("cattester", "pass123456", "cattester@example.com")
        self.cat_repo.ensure_default_categories(user_id)

        cats = self.cat_repo.get_categories(user_id)
        self.assertTrue(len(cats) >= 5)

        # Add custom subcategory
        ok, msg, cat_id = self.cat_repo.add_category(user_id, "Insurance Policies")
        self.assertTrue(ok)
        self.assertIsNotNone(cat_id)

        # Rebuild tree
        self.doc_service.sync_user_indexes(user_id)
        found_node = self.doc_service.category_tree.find("Insurance Policies")
        self.assertIsNotNone(found_node)

        # Delete category
        del_cat = self.cat_repo.delete_category(cat_id, user_id)
        self.assertTrue(del_cat)


if __name__ == "__main__":
    unittest.main()
