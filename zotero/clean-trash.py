import sqlite3
import os
from datetime import datetime
import shutil

def clean_zotero_trash(zotero_db_path, backup=True):
    """
    Clean the Zotero trash folder by removing deleted items from the SQLite database.
    
    Parameters:
    zotero_db_path (str): Path to the zotero.sqlite file
    backup (bool): Whether to create a backup of the database before cleaning
    
    Returns:
    tuple: (number of items deleted, list of deleted item names)
    """
    # Create backup if requested
    if backup:
        backup_path = f"zotero_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sqlite"
        shutil.copy2(zotero_db_path, backup_path)
        print(f"Created backup at: {backup_path}")

    # Connect to the database
    conn = sqlite3.connect(zotero_db_path)
    cursor = conn.cursor()

    try:
        # First, let's get all items in trash with their titles
        cursor.execute("""
            SELECT i.itemID, fields.fieldName, itemDataValues.value
            FROM items i
            JOIN deletedItems d ON i.itemID = d.itemID
            LEFT JOIN itemData ON i.itemID = itemData.itemID
            LEFT JOIN fields ON itemData.fieldID = fields.fieldID
            LEFT JOIN itemDataValues ON itemData.valueID = itemDataValues.valueID
            WHERE fields.fieldName = 'title' OR fields.fieldName IS NULL
        """)
        
        trash_items = cursor.fetchall()
        deleted_items = set()
        item_names = []

        # Get names of items to be deleted
        for item in trash_items:
            if item[1] == 'title' and item[2]:
                item_names.append(item[2])
            deleted_items.add(item[0])

        # Delete in the correct order to respect foreign key constraints
        delete_queries = [
            # Remove from itemAttachments
            """
            DELETE FROM itemAttachments 
            WHERE itemID IN (SELECT itemID FROM deletedItems)
            """,
            
            # Remove from itemNotes
            """
            DELETE FROM itemNotes 
            WHERE itemID IN (SELECT itemID FROM deletedItems)
            """,
            
            # Remove from itemTags
            """
            DELETE FROM itemTags 
            WHERE itemID IN (SELECT itemID FROM deletedItems)
            """,
            
            # Remove from itemData
            """
            DELETE FROM itemData 
            WHERE itemID IN (SELECT itemID FROM deletedItems)
            """,
            
            # Remove from collections_items if it exists
            """
            DELETE FROM collections_items 
            WHERE itemID IN (SELECT itemID FROM deletedItems)
            """,
            
            # Remove the actual items
            """
            DELETE FROM items 
            WHERE itemID IN (SELECT itemID FROM deletedItems)
            """,
            
            # Finally clear the deletedItems table
            """
            DELETE FROM deletedItems
            """
        ]

        # Execute delete queries
        for query in delete_queries:
            try:
                cursor.execute(query)
            except sqlite3.Error as e:
                # Skip if table doesn't exist
                if "no such table" not in str(e):
                    print(f"Warning: {e}")

        # Commit changes
        conn.commit()
        
        return len(deleted_items), item_names

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()
        return 0, []

    finally:
        conn.close()

def main():
    # Example usage
    zotero_path = os.path.expanduser("~/Zotero/zotero.sqlite")
    
    if not os.path.exists(zotero_path):
        print("Zotero database not found at the default location.")
        zotero_path = input("Please enter the path to your zotero.sqlite file: ")
    
    if os.path.exists(zotero_path):
        # Make sure Zotero is closed
        input("Please ensure Zotero is closed before continuing. Press Enter to proceed...")
        
        # Clean trash
        deleted_count, deleted_items = clean_zotero_trash(zotero_path)
        
        print(f"\nCleaned {deleted_count} items from trash.")
        if deleted_items:
            print("\nDeleted items:")
            for item in deleted_items:
                print(f"- {item}")
        else:
            print("\nNo items found in trash.")
    else:
        print("Could not find Zotero database. Please check the path and try again.")

if __name__ == "__main__":
    main()
