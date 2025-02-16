#!/usr/bin/env python3

"""
Download a PDF attachment from Zotero by DOI.
Save the PDF to a local directory.
"""

import sys
import sqlite3
import os
import shutil

ZOTERO_DB_PATH = os.path.expanduser("~/Zotero/zotero.sqlite")
ZOTERO_STORAGE_DIR = os.path.expanduser("~/Zotero/storage")

def sanitize_filename(s: str) -> str:
    """
    Replace characters that are invalid on most filesystems
    (like slashes, colons, etc.) with underscores or another safe character.
    """
    return s.replace("/", "_").replace("\\", "_").replace(":", "_")

def get_item_id_by_doi(conn, doi):
    query = """
    SELECT items.itemID
      FROM items
      JOIN itemData       ON items.itemID = itemData.itemID
      JOIN itemDataValues ON itemData.valueID = itemDataValues.valueID
      JOIN fields         ON itemData.fieldID = fields.fieldID
     WHERE fields.fieldName = 'DOI'
       AND itemDataValues.value = ?
    """
    cur = conn.cursor()
    cur.execute(query, (doi,))
    row = cur.fetchone()
    return row[0] if row else None

def get_pdf_attachment_path(conn, parent_item_id):
    """
    Example for linkMode=0 scenario with the path stored as 'storage:Filename.pdf'
    and the actual folder name in items.key. Adjust as needed.
    """
    query = """
    SELECT items.key,
           itemAttachments.path
      FROM itemAttachments
      JOIN items ON items.itemID = itemAttachments.itemID
     WHERE itemAttachments.parentItemID = ?
       AND itemAttachments.linkMode = 0
       AND itemAttachments.path LIKE '%.pdf'
    """
    cur = conn.cursor()
    cur.execute(query, (parent_item_id,))
    row = cur.fetchone()
    if not row:
        return None  # No PDF found

    child_key, raw_path = row
    # If raw_path includes 'storage:', strip it
    filename = raw_path
    if filename.startswith("storage:"):
        filename = filename[len("storage:"):]
    # Construct the on-disk path
    full_path = os.path.join(ZOTERO_STORAGE_DIR, child_key, filename)
    return full_path

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scriptname.py <DOI>")
        sys.exit(1)

    doi = sys.argv[1].strip()
    if not doi:
        print("Error: DOI cannot be empty.")
        sys.exit(1)

    if not os.path.isfile(ZOTERO_DB_PATH):
        print(f"Error: Zotero DB not found at {ZOTERO_DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(ZOTERO_DB_PATH)

    # 1. Look up item by DOI
    item_id = get_item_id_by_doi(conn, doi)
    if not item_id:
        print(f"No Zotero item found with DOI = {doi}")
        sys.exit(0)

    # 2. Find PDF path
    pdf_path = get_pdf_attachment_path(conn, item_id)
    if not pdf_path:
        print(f"No PDF attachment found for DOI = {doi}")
        sys.exit(0)

    if not os.path.isfile(pdf_path):
        print(f"Expected PDF file not found on disk: {pdf_path}")
        sys.exit(0)

    # 3. Copy PDF to docs/{safe_doi}.pdf
    safe_doi = sanitize_filename(doi)
    output_dir = "docs"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{safe_doi}.pdf")

    shutil.copyfile(pdf_path, output_file)
    print(f"Copied PDF to {output_file}")

    conn.close()

if __name__ == "__main__":
    main()
