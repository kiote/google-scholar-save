#!/usr/bin/env python3

import sqlite3
import csv
import sys
import os
import re

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
        # Journal
        return 'journal', get_field_value(conn, item_id, 'publicationTitle')
    elif item_type_name == 'conferencePaper':
        # Conference
        venue = get_field_value(conn, item_id, 'proceedingsTitle')
        if not venue:
            venue = get_field_value(conn, item_id, 'conferenceName')
        return 'conference', venue
    else:
        # For everything else, label as 'other'
        return 'other', None

def main():
    # Optional: read output.csv path from command line, otherwise default
    if len(sys.argv) > 1:
        output_csv = sys.argv[1]
    else:
        output_csv = 'output.csv'

    # Adjust to your actual Zotero database path
    db_path = os.path.expanduser("~/Zotero/zotero.sqlite")

    # Connect to the Zotero database
    conn = sqlite3.connect(db_path)

    # Prepare to store results
    results = []

    # Read titles from 'input.txt'
    input_file = 'input.txt'
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        title = line.strip()
        if not title:
            # Skip any empty lines
            continue

        # Find item(s) in Zotero
        item_ids = get_item_id_by_title(conn, title)

        if not item_ids:
            # If no match is found, write a row with minimal info or placeholders
            results.append({
                'title': title,
                'authors': 'not found',
                'year': '',
                'type': '',
                'venue': ''
            })
        else:
            # If we have matches, gather info for each matched item
            for item_id in item_ids:
                authors_list = get_authors(conn, item_id)
                authors_str = "; ".join(authors_list)

                zotero_date = get_field_value(conn, item_id, 'date')
                year_str = parse_year(zotero_date)

                item_type_name = get_item_type(conn, item_id)
                type_str, venue_str = determine_type_and_venue(item_type_name, conn, item_id)

                results.append({
                    'title': title,
                    'authors': authors_str,
                    'year': year_str if year_str else '',
                    'type': type_str,
                    'venue': venue_str if venue_str else ''
                })

    # Write out to CSV
    fieldnames = ['title', 'authors', 'year', 'type', 'venue']
    with open(output_csv, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)

    print(f"Wrote {len(results)} rows to '{output_csv}' from '{input_file}'.")

if __name__ == "__main__":
    main()
