import sqlite3
import os

def clean_zotero_database(zotero_db_path):
    conn = sqlite3.connect(zotero_db_path)
    conn.execute("PRAGMA foreign_keys = OFF")
    cursor = conn.cursor()
    
    tables = [
        "itemAttachments", "itemNotes", "itemTags", "itemData",
        "collections_items", "deletedItems", "items", "collections",
        "tags", "itemDataValues"
    ]
    
    deleted = 0
    for table in tables:
        try:
            cursor.execute(f"DELETE FROM {table}")
            conn.commit()
            deleted += cursor.rowcount
        except sqlite3.Error:
            continue

    conn.close()
    return deleted

def main():
    zotero_path = os.path.expanduser("~/Zotero/zotero.sqlite")
    if not os.path.exists(zotero_path):
        zotero_path = input("Enter path to zotero.sqlite: ")

    if os.path.exists(zotero_path):
        input("WARNING: This will delete ALL items. Press Enter to proceed...")
        deleted_count = clean_zotero_database(zotero_path)
        print(f"\nRemoved {deleted_count} items")
    else:
        print("Database not found")

if __name__ == "__main__":
    main()
