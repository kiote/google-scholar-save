import sqlite3
import os
import re
from pathlib import Path
import time
from difflib import SequenceMatcher

def log(message):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def normalize_title(title):
    # Convert to lowercase
    title = title.lower()
    # Remove punctuation and special characters
    title = re.sub(r'[^\w\s]', '', title)
    # Remove extra whitespace
    title = ' '.join(title.split())
    return title

def similar(a, b, threshold=0.9):
    return SequenceMatcher(None, a, b).ratio() > threshold

# Path to Zotero database
zotero_path = Path.home() / "Zotero" / "zotero.sqlite"

# Backup the database
backup_path = zotero_path.with_suffix('.sqlite.backup')
os.system(f"cp {zotero_path} {backup_path}")
log(f"Backup created at {backup_path}")

# Connect to the database
conn = sqlite3.connect(str(zotero_path))
cursor = conn.cursor()

log("Fetching items with titles from the database...")
# Get all items with their titles
cursor.execute("""
    SELECT i.itemID, idv.value as title
    FROM items i
    JOIN itemData id ON i.itemID = id.itemID
    JOIN itemDataValues idv ON id.valueID = idv.valueID
    JOIN fields f ON id.fieldID = f.fieldID
    WHERE f.fieldName = 'title' AND i.itemTypeID != 14
""")
items = cursor.fetchall()
log(f"Fetched {len(items)} items with titles")

# Normalize titles and group similar items
log("Normalizing titles and grouping similar items...")
groups = {}
items_processed = 0
for item_id, title in items:
    if title:
        items_processed += 1
        normalized_title = normalize_title(title)
        found = False
        for key in groups:
            if similar(key, normalized_title):
                groups[key].append((item_id, title))
                found = True
                break
        if not found:
            groups[normalized_title] = [(item_id, title)]

    if items_processed % 100 == 0:
        log(f"Processed {items_processed} items...")

log(f"Processed {items_processed} items with non-empty titles")
log(f"Identified {len(groups)} unique normalized titles")

# Process duplicate groups
log("Processing duplicate groups...")
total_duplicates = 0
total_deleted = 0

for normalized_title, items in groups.items():
    if len(items) > 1:
        total_duplicates += 1
        item_to_keep = min(items, key=lambda x: x[0])  # Keep the item with the lowest itemID
        items_to_delete = set(item[0] for item in items) - {item_to_keep[0]}
        total_deleted += len(items_to_delete)

        log(f"Potential duplicate set found for normalized title '{normalized_title}':")
        log(f"  Keeping item {item_to_keep[0]} with title '{item_to_keep[1]}'")
        log(f"  Potential duplicates to delete: {items_to_delete}")
        log(f"  Original titles of potential duplicates:")
        for item in items:
            if item[0] in items_to_delete:
                log(f"    - ItemID {item[0]}: '{item[1]}'")

        cursor.execute("""
            DELETE FROM items WHERE itemID IN ({})
        """.format(','.join('?' * len(items_to_delete))), list(items_to_delete))

        cursor.execute("""
            DELETE FROM itemData WHERE itemID IN ({})
        """.format(','.join('?' * len(items_to_delete))), list(items_to_delete))

# Commit changes and close connection
log("Committing changes to the database...")
conn.commit()
conn.close()

log(f"Duplicate identification complete. Found {total_duplicates} sets of potential duplicates.")
log(f"Identified {total_deleted} items as potential duplicates.")
log("Please review the log and uncomment the deletion lines in the script to actually remove duplicates.")
log("Remember to restart Zotero after making any changes for them to take effect.")
