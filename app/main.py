"""Central Application entry point for VAULTX with both modern GUI and CLI demonstration modes."""

import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.auth_repository import AuthRepository
from app.database.schema import init_database
from app.services.document_service import DocumentService
from app.ui.tk_compat import is_gui_supported


def initialize_app():
    """Initialize database tables, cryptographic key, and core service layer."""
    init_database()
    auth_repo = AuthRepository()
    doc_service = DocumentService()
    return auth_repo, doc_service


def launch_gui():
    """Launch the Windows Desktop GUI interface (Tkinter / ttkbootstrap)."""
    if not is_gui_supported():
        print("[!] No graphical display environment or Tkinter detected.")
        print("[*] Automatically falling back to the interactive CLI demonstration mode...")
        launch_cli_demo()
        return

    from app.ui.auth_window import AuthWindow
    from app.ui.main_window import MainWindow

    auth_repo, doc_service = initialize_app()

    def show_auth():
        def on_login(user_data):
            main_win = MainWindow(
                user_data=user_data,
                auth_repo=auth_repo,
                doc_service=doc_service,
                on_logout=show_auth,
            )
            main_win.start()

        auth_win = AuthWindow(auth_repo=auth_repo, on_login_success=on_login)
        auth_win.start()

    show_auth()


def launch_cli_demo():
    """Interactive command-line demonstration runner for evaluation and headless verification."""
    auth_repo, doc_service = initialize_app()

    # Ensure demo student user exists
    auth_repo.register("student", "vaultx2026", "student@vaultx.local")
    ok, _, user_data = auth_repo.authenticate("student", "vaultx2026")
    user_id = user_data["id"]

    # Seed sample documents if user has none
    docs = doc_service.repo.get_user_documents(user_id)
    if not docs:
        print("[*] Seeding sample encrypted documents for demonstration...")
        tmp_dir = Path("data/samples")
        tmp_dir.mkdir(parents=True, exist_ok=True)

        sample1 = tmp_dir / "Diploma_Semester_Marksheet.txt"
        sample1.write_text(
            "State Board of Technical Education - Yash Shelar - Information Technology - GPA 9.4",
            encoding="utf-8",
        )
        doc_service.store_document(
            user_id=user_id,
            title="Diploma IT Semester Marksheet",
            file_path=str(sample1),
            category="Academic & Certificates",
            tags="diploma, msbte, semester, it",
            expiry_date="2027-06-30",
            description="Final semester transcript with official grade points.",
        )

        sample2 = tmp_dir / "Health_Insurance_Policy.txt"
        sample2.write_text(
            "Mediclaim Health Insurance Policy #MED-99418 - Annual Coverage [__redacted__]",
            encoding="utf-8",
        )
        doc_service.store_document(
            user_id=user_id,
            title="Health Insurance Policy Card",
            file_path=str(sample2),
            category="Medical & Health",
            tags="insurance, mediclaim, health",
            expiry_date="2026-10-25",
            description="Comprehensive family health insurance documentation.",
        )

    doc_service.sync_user_indexes(user_id)

    print("\n" + "=" * 65)
    print(" 🔒 VAULTX: Secure Personal Document Management System")
    print(" Production Prototype & Technical Demonstration Interface")
    print("=" * 65)
    print(f"Logged in as: {user_data['username']} (ID: {user_id})")
    print(f"Active Master Encryption Key: {doc_service.encryption.key_path}")
    print(f"Encryption Standard: Fernet (AES-128-CBC + HMAC-SHA256)")

    while True:
        print("\n--- Main Menu ---")
        print("1. 📊 View Dashboard & Statistics")
        print("2. 📁 List All Stored Documents")
        print("3. 🔍 Search Documents (Trie Prefix Engine)")
        print("4. ⏰ Check Expirations (Chronological Date Tracker)")
        print("5. 🕒 View Recent History (Doubly Linked List LRU)")
        print("6. 🧠 Technology & Data Structures Overview")
        print("7. ➕ Add New Document")
        print("8. 💾 Export & Decrypt Document")
        print("9. 🚪 Exit")

        choice = input("\nEnter choice [1-9]: ").strip()
        if choice == "1":
            stats = doc_service.get_dashboard_stats(user_id)
            print("\n--- Dashboard Statistics ---")
            print(f"Total Documents    : {stats['total_documents']}")
            print(f"Favorite Documents : {stats['favorite_documents']}")
            print(f"Expiring Soon (<30d): {stats['expiring_soon_documents']}")
            print("Category Breakdown :")
            for cat, count in stats["category_counts"].items():
                print(f"  • {cat}: {count}")

        elif choice == "2":
            user_docs = doc_service.repo.get_user_documents(user_id)
            print(f"\n--- Stored Documents ({len(user_docs)}) ---")
            for d in user_docs:
                fav = "⭐ " if d["is_favorite"] else "   "
                print(f"{fav}[#{d['id']:02d}] {d['title']} | Cat: {d['category']} | Exp: {d['expiry_date'] or 'None'}")

        elif choice == "3":
            prefix = input("Enter search word or prefix: ").strip()
            suggestions = doc_service.search_service.autocomplete(prefix)
            print(f"Trie Autocomplete Suggestions: {suggestions}")
            results = doc_service.search_documents(user_id, prefix)
            print(f"Search Results ({len(results)} matches):")
            for r in results:
                print(f"  • [#{r['id']}] {r['title']} (Category: {r['category']}, Tags: {r['tags']})")

        elif choice == "4":
            expiring = doc_service.get_expiring_documents(days=60)
            print(f"\n--- Upcoming Expirations (Chronological Order) ---")
            for item in expiring:
                title = item.get("metadata", {}).get("title", f"Doc #{item['doc_id']}")
                days = item["days_left"]
                status = "EXPIRED" if days < 0 else f"{days} days remaining"
                print(f"  • {title} -> Expiring on {item['expiry_date']} ({status})")

        elif choice == "5":
            history = doc_service.recent_history.get_recent()
            print("\n--- Recently Accessed Documents (Linked List LRU) ---")
            for item in history:
                print(f"  • Doc #{item['doc_id']}: {item.get('title')}")

        elif choice == "6":
            print("\n--- Technology & Data Structures Overview ---")
            print(f"1. Trie (Search Index) : {doc_service.search_service.trie.get_stats()}")
            print(f"2. HashTable (Cache)   : {doc_service.doc_cache.get_diagnostics()}")
            print(f"3. LinkedList (LRU)    : {len(doc_service.recent_history)} recent items recorded")
            print(f"4. Expiry Tracker      : {len(doc_service.expiry_service)} tracked deadlines")
            print("5. Category Tree Hierarchy (ASCII):")
            print(doc_service.category_tree.render_ascii_tree())

        elif choice == "7":
            title = input("Document Title: ").strip()
            path_str = input("File Path: ").strip()
            cat = input("Category [General]: ").strip() or "General"
            exp = input("Expiry Date (YYYY-MM-DD or blank): ").strip() or None
            if Path(path_str).exists():
                doc_id = doc_service.store_document(
                    user_id=user_id,
                    title=title,
                    file_path=path_str,
                    category=cat,
                    expiry_date=exp,
                )
                print(f"[+] Document encrypted and saved with ID: {doc_id}")
            else:
                print(f"[!] File not found: {path_str}")

        elif choice == "8":
            doc_id_str = input("Enter Document ID to export: ").strip()
            dest = input("Export destination path: ").strip()
            try:
                ok = doc_service.export_document(int(doc_id_str), user_id, dest)
                print("[+] Decrypted file exported successfully!" if ok else "[!] Export failed.")
            except Exception as e:
                print(f"[!] Error: {e}")

        elif choice == "9":
            print("Exiting VAULTX. Goodbye!")
            break


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        launch_cli_demo()
    else:
        launch_gui()
