import sqlite3
import os
import shutil

# Path to Zotero database directory
zotero_dir = r"C:\Users\kos00\OneDrive - University of Cyprus\Zeroto_Drive"

# Path to the Zotero database
original_db_path = os.path.join(zotero_dir, "zotero.sqlite")

def create_zotero_copy(original_path):
    copy_path = os.path.join(zotero_dir, "zoteroCopy.sqlite")
    shutil.copy2(original_path, copy_path)
    print(f"[INFO] Created a copy of Zotero database at: {copy_path}")
    return copy_path

def fetch_structure_from_db(cursor):
    print("[INFO] Fetching collections and subcollections...")

    # Fetch all collections with parentCollectionID to identify the hierarchy
    cursor.execute("SELECT collectionName, collectionID, parentCollectionID FROM collections")
    all_collections = cursor.fetchall()

    # Build a dictionary to map parentCollectionID to subcollections
    collection_map = {}
    for collection in all_collections:
        collection_name, collection_id, parent_id = collection
        if parent_id not in collection_map:
            collection_map[parent_id] = []
        collection_map[parent_id].append((collection_name, collection_id))

    def find_end_folders(parent_id=None, path=""):
        end_folders = []
        subcollections = collection_map.get(parent_id, [])
        for sub_name, sub_id in subcollections:
            current_path = os.path.join(path, sub_name)
            # Recursively find subfolders
            if sub_id in collection_map:  # If the current collection has children
                end_folders.extend(find_end_folders(sub_id, current_path))
            else:  # If no children, it's an end-folder
                end_folders.append(current_path)
        return end_folders

    # Start from top-level collections (parent_id=None)
    end_folders = find_end_folders()
    return end_folders

try:
    print("[INFO] Checking if Zotero database exists...")
    if not os.path.exists(original_db_path):
        raise FileNotFoundError(f"[ERROR] Zotero database not found at {original_db_path}")

    print("[INFO] Creating a copy of the Zotero database...")
    db_path = create_zotero_copy(original_db_path)

    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    cursor = conn.cursor()

    print("[INFO] Fetching Zotero Library Structure...")
    end_folders = fetch_structure_from_db(cursor)

    print("[INFO] End folders (leaf collections):")
    for folder in end_folders:
        print(folder)

except Exception as e:
    print(f"[ERROR] {e}")
