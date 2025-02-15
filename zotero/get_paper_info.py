#!/usr/bin/env python3

import sqlite3
import csv
import sys
import os

def get_item_id_by_title(conn, title):
    """
    Return a list of itemIDs matching a given title (exact match).
    """
    query = """
    SELECT items.itemID
    FROM items
    JOIN itemData ON items.itemID = itemData.itemID
    JOIN itemDataValues ON itemData.valueID = itemDataValues.valueID
    JOIN fields ON itemData.fieldID = fields.fieldID
    WHERE fields.fieldName = 'title'
      AND itemDataValues.value = ?
    """
    cur = conn.cursor()
    cur.execute(query, (title,))
    rows = cur.fetchall()
    return [r[0] for r in rows]

def get_item_type(conn, item_id):
    """
    Return the typeName (e.g. 'journalArticle', 'conferencePaper') for a given itemID.
    """
    query = """
    SELECT itemTypes.typeName
    FROM items
    JOIN itemTypes ON items.itemTypeID = itemTypes.itemTypeID
    WHERE items.itemID = ?
    """
    cur = conn.cursor()
    cur.execute(query, (item_id,))
    row = cur.fetchone()
    return row[0] if row else None

def get_authors(conn, item_id):
    """
    Return a list of author names for a given itemID.
    """
    query = """
    SELECT creators.lastName, creators.firstName
    FROM itemCreators
    JOIN creators ON itemCreators.creatorID = creators.creatorID
    JOIN creatorTypes ON itemCreators.creatorTypeID = creatorTypes.creatorTypeID
    WHERE itemCreators.itemID = ?
      AND creatorTypes.creatorType = 'author'
    ORDER BY itemCreators.orderIndex
    """
    cur = conn.cursor()
    cur.execute(query, (item_id,))
    authors = []
    for last_name, first_name in cur.fetchall():
        # Adjust how you want to display the name:
        if first_name:
            authors.append(f"{first_name} {last_name}")
        else:
            authors.append(last_name)
    return authors

def get_field_value(conn, item_id, field_name):
    """
    Return the value of a specific Zotero field (e.g. 'publicationTitle', 'date') for a given itemID.
    """
    query = """
    SELECT itemDataValues.value
    FROM itemData
    JOIN itemDataValues ON itemData.valueID = itemDataValues.valueID
    JOIN fields ON itemData.fieldID = fields.fieldID
    WHERE itemData.itemID = ?
      AND fields.fieldName = ?
    """
    cur = conn.cursor()
    cur.execute(query, (item_id, field_name))
    row = cur.fetchone()
    return row[0] if row else None

def parse_year(zotero_date):
    """
    Attempt to extract a 4-digit year from the Zotero 'date' field.
    Zotero 'date' fields can be messy, e.g. "2023-05-01" or "May 2023", etc.
    """
    if not zotero_date:
        return None
    import re
    match = re.search(r"\b(\d{4})\b", zotero_date)
    if match:
        return match.group(1)
    return None

def determine_type_and_venue(item_type_name, conn, item_id):
    """
    Determine whether the item is a 'conference' or 'journal' based on typeName,
    and extract a relevant 'venue' from the appropriate Zotero field.
    """
    if item_type_name == 'journalArticle':
        return 'journal', get_field_value(conn, item_id, 'publicationTitle')
    elif item_type_name == 'conferencePaper':
        # Some references might store 'conferenceName' instead of 'proceedingsTitle'—adjust as needed.
        venue = get_field_value(conn, item_id, 'proceedingsTitle')
        if not venue:
            venue = get_field_value(conn, item_id, 'conferenceName')
        return 'conference', venue
    else:
        # If you want to handle other types, add them here.
        # For simplicity, mark everything else as 'other'
        return 'other', None

def main():
    if len(sys.argv) < 2:
        print("Usage: python get_paper_info.py 'Title of the Paper' [/path/to/output.csv]")
        sys.exit(1)

    db_path = os.path.expanduser("~/Zotero/zotero.sqlite")
    title = sys.argv[1]
    # Optional output CSV path, default to 'output.csv'
    output_csv = sys.argv[3] if len(sys.argv) > 3 else 'output.csv'

    conn = sqlite3.connect(db_path)

    # 1. Lookup the item(s) by title
    item_ids = get_item_id_by_title(conn, title)
    if not item_ids:
        print(f"No item found matching title: {title}")
        sys.exit(0)

    # 2. For each matched item, collect metadata
    results = []
    for item_id in item_ids:
        # Get authors
        authors_list = get_authors(conn, item_id)
        authors_str = "; ".join(authors_list)

        # Get year (parsed from Zotero date)
        zotero_date = get_field_value(conn, item_id, 'date')
        year_str = parse_year(zotero_date)

        # Get item type (journalArticle, conferencePaper, etc.)
        item_type_name = get_item_type(conn, item_id)

        # Convert to simpler "journal"/"conference" plus a venue
        type_str, venue_str = determine_type_and_venue(item_type_name, conn, item_id)

        results.append({
            'title': title,
            'authors': authors_str,
            'year': year_str,
            'type': type_str,
            'venue': venue_str if venue_str else ''
        })

    # 3. Write out CSV
    fieldnames = ['title', 'authors', 'year', 'type', 'venue']
    with open(output_csv, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)

    print(f"Found {len(results)} item(s) matching '{title}' and wrote data to {output_csv}.")

if __name__ == "__main__":
    main()
