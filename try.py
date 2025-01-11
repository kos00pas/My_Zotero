import sqlite3
import os
import shutil

# Path to the SQLite database and storage directory
db_path = r"C:\Users\kos00\OneDrive - University of Cyprus\Zeroto_Drive\zotero.sqlite"
zotero_dir = r"C:\Users\kos00\OneDrive - University of Cyprus\Zeroto_Drive"
storage_dir = os.path.join(zotero_dir, "storage")


def create_zotero_copy(original_db_path, zotero_dir):
    try:
        copy_path = os.path.join(zotero_dir, "zoteroCopy.sqlite")
        shutil.copy2(original_db_path, copy_path)
        print(f"[INFO] Created a copy of Zotero database at: {copy_path}")
        return copy_path
    except Exception as e:
        print(f"[ERROR] Failed to create Zotero copy: {e}")
        return None


def search_instances_with_parent_collection(db_path, parent_collection_name):
    try:
        # Check if the database exists
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"[ERROR] Zotero database not found at {db_path}")

        print("[INFO] Connecting to the Zotero database...")
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        cursor = conn.cursor()

        # Find the collection ID of the specified parent collection
        print(f"[INFO] Searching for collection ID with name: {parent_collection_name}...")
        cursor.execute(
            """
            SELECT collectionID FROM collections WHERE collectionName = ?
            """,
            (parent_collection_name,),
        )
        result = cursor.fetchone()

        if not result:
            print(f"[INFO] Collection with name '{parent_collection_name}' not found.")
            return

        parent_collection_id = result[0]
        print(f"[INFO] Found collection ID: {parent_collection_id} for '{parent_collection_name}'")

        # Find all instances (items) with the specified parent collection
        print(f"[INFO] Searching for items in collections with parent: {parent_collection_name}...")
        cursor.execute(
            """
            SELECT items.itemID, itemDataValues.value AS title, itemAttachments.path, collections.collectionName
            FROM items
            LEFT JOIN itemAttachments ON items.itemID = itemAttachments.parentItemID
            LEFT JOIN itemData ON items.itemID = itemData.itemID
            LEFT JOIN itemDataValues ON itemData.valueID = itemDataValues.valueID
            LEFT JOIN collectionItems ON items.itemID = collectionItems.itemID
            LEFT JOIN collections ON collectionItems.collectionID = collections.collectionID
            WHERE collections.parentCollectionID = ?
            """,
            (parent_collection_id,),
        )

        results = cursor.fetchall()

        if not results:
            print(f"[INFO] No items found for collections under '{parent_collection_name}'")
        else:
            print(f"[INFO] Found {len(results)} items for collections under '{parent_collection_name}'")
            for item in results:
                item_id, title, path, collection_name = item
                print("\nItem Details:")
                print(f" - Item ID: {item_id}")
                print(f" - Title: {title if title else 'N/A'}")
                print(f" - File Path: {path if path else 'N/A'}")
                print(f" - Collection: {collection_name if collection_name else 'N/A'}")

        conn.close()

    except Exception as e:
        print(f"[ERROR] {e}")


# Create a copy of the Zotero database
zotero_copy_path = create_zotero_copy(db_path, zotero_dir)

if zotero_copy_path:
    # Call the function to search for instances with the specified parent collection
    search_instances_with_parent_collection(zotero_copy_path, "Clean_Code")
