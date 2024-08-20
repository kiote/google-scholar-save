import sqlite3
import os
from pathlib import Path

# Path to Zotero database
zotero_path = Path.home() / "Zotero" / "zotero.sqlite"

# Backup the database
backup_path = zotero_path.with_suffix('.sqlite.backup')
os.system(f"cp {zotero_path} {backup_path}")

print(f"Backup created at {backup_path}")

# Connect to the database
conn = sqlite3.connect(str(zotero_path))
cursor = conn.cursor()

# Get the itemTypeID for 'journalArticle'
cursor.execute("SELECT itemTypeID FROM itemTypes WHERE typeName = 'journalArticle'")
journal_article_type_id = cursor.fetchone()[0]

# Update all items to 'journalArticle' type
cursor.execute("UPDATE items SET itemTypeID = ?", (journal_article_type_id,))

# Commit changes and close connection
conn.commit()
conn.close()

print("All items have been changed to 'journalArticle' type.")
print("Please restart Zotero for changes to take effect.")
