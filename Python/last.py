import sqlite3
import os
import shutil

# Path to Zotero database directory
zotero_dir = r"C:\Users\kos00\OneDrive - University of Cyprus\Zeroto_Drive"

# Path to the Zotero database
original_db_path = os.path.join(zotero_dir, "zotero.sqlite")

# Target directory to create folder structure
target_dir = r"C:\Users\kos00\OneDrive - University of Cyprus\Zeroto_Drive\My_Zotero\My_Library"

def create_folder_structure(original_db_path, zotero_dir, target_dir):
    try:
        # Check if Zotero database exists
        print("[INFO] Checking if Zotero database exists...")
        if not os.path.exists(original_db_path):
            raise FileNotFoundError(f"[ERROR] Zotero database not found at {original_db_path}")

        # Create a copy of the database
        print("[INFO] Creating a copy of the Zotero database...")
        copy_path = os.path.join(zotero_dir, "zoteroCopy.sqlite")
        shutil.copy2(original_db_path, copy_path)
        print(f"[INFO] Created a copy of Zotero database at: {copy_path}")

        # Connect to the copied database
        conn = sqlite3.connect(f"file:{copy_path}?mode=ro", uri=True)
        cursor = conn.cursor()

        # Fetch collections and build hierarchy
        print("[INFO] Fetching collections and subcollections...")
        cursor.execute("SELECT collectionName, collectionID, parentCollectionID FROM collections")
        all_collections = cursor.fetchall()

        # Build mappings
        collection_map = {}
        id_to_name_map = {}
        for collection in all_collections:
            collection_name, collection_id, parent_id = collection
            if parent_id not in collection_map:
                collection_map[parent_id] = []
            collection_map[parent_id].append((collection_name, collection_id))
            id_to_name_map[collection_id] = collection_name

        # Recursive function to traverse hierarchy and create folders
        def traverse_and_create_folders(parent_id=None, path=target_dir):
            subcollections = collection_map.get(parent_id, [])
            if parent_id is not None:  # Add parent folder
                folder_name = id_to_name_map[parent_id]
                current_path = os.path.join(path, folder_name)
                # Create the folder if it doesn't exist
                os.makedirs(current_path, exist_ok=True)
                print(f"[INFO] Created folder: {current_path}")
            else:
                current_path = path

            for sub_name, sub_id in subcollections:
                traverse_and_create_folders(sub_id, current_path)

        # Start traversal and folder creation from the top-level collections
        traverse_and_create_folders()

        print("[INFO] Folder structure created successfully!")

    except Exception as e:
        print(f"[ERROR] {e}")

# Call the function
create_folder_structure(original_db_path, zotero_dir, target_dir)
