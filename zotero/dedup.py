'''
Delete duplicates by DOI
'''
import sqlite3
import os
from pathlib import Path
import time

def log(message):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}")

# Path to Zotero database
zotero_path = Path.home() / "Zotero" / "zotero.sqlite"

# Backup the database
backup_path = zotero_path.with_suffix('.sqlite.backup')
os.system(f"cp {zotero_path} {backup_path}")
log(f"Backup created at {backup_path}")

# Connect to the database
conn = sqlite3.connect(str(zotero_path))
cursor = conn.cursor()

log("Fetching items with DOIs from the database...")
# Get all items with their DOIs
cursor.execute("""
    SELECT i.itemID, idv.value as doi
    FROM items i
    JOIN itemData id ON i.itemID = id.itemID
    JOIN itemDataValues idv ON id.valueID = idv.valueID
    JOIN fields f ON id.fieldID = f.fieldID
    WHERE f.fieldName = 'DOI' AND i.itemTypeID != 14
""")
items = cursor.fetchall()
log(f"Fetched {len(items)} items with DOIs")

# Group items by DOI
log("Grouping items by DOI...")
groups = {}
items_with_doi = 0
for item_id, doi in items:
    if doi:
        items_with_doi += 1
        doi = doi.strip().lower()  # Normalize DOI
        if doi in groups:
            groups[doi].append(item_id)
        else:
            groups[doi] = [item_id]

log(f"Found {items_with_doi} items with non-empty DOIs")
log(f"Identified {len(groups)} unique DOIs")

# Process duplicate groups
log("Processing duplicate groups...")
total_duplicates = 0
total_deleted = 0

for doi, item_ids in groups.items():
    if len(item_ids) > 1:
        total_duplicates += 1
        item_to_keep = min(item_ids)
        items_to_delete = set(item_ids) - {item_to_keep}
        total_deleted += len(items_to_delete)
        
        log(f"Duplicate set found for DOI '{doi}':")
        log(f"  Keeping item {item_to_keep}")
        log(f"  Deleting items {items_to_delete}")
        
        # Delete the duplicate items
        cursor.execute("""
            DELETE FROM items WHERE itemID IN ({})
        """.format(','.join('?' * len(items_to_delete))), list(items_to_delete))
        
        # Delete associated itemData entries
        cursor.execute("""
            DELETE FROM itemData WHERE itemID IN ({})
        """.format(','.join('?' * len(items_to_delete))), list(items_to_delete))

# Commit changes and close connection
log("Committing changes to the database...")
conn.commit()
conn.close()

log(f"Duplicate removal complete. Found {total_duplicates} sets of duplicates.")
log(f"Deleted {total_deleted} duplicate items.")
log("Please restart Zotero for changes to take effect.")
