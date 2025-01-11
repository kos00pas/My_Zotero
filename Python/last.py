import sqlite3
import os
import shutil

# Paths
zotero_dir = r"C:\Users\kos00\OneDrive - University of Cyprus\Zeroto_Drive"
original_db_path = os.path.join(zotero_dir, "zotero.sqlite")
base_storage_dir = r"C:\Users\kos00\OneDrive - University of Cyprus\Zeroto_Drive\storage"
target_dir = r"C:\Users\kos00\OneDrive - University of Cyprus\Zeroto_Drive\My_Zotero\My_Library"

def create_folder_structure_with_print(original_db_path, zotero_dir, target_dir):
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

        # Recursive function to traverse hierarchy and collect folders
        def traverse_and_collect_folders(parent_id=None, path=""):
            folder_list = []
            subcollections = collection_map.get(parent_id, [])
            if parent_id is not None:  # Add parent folder
                folder_name = id_to_name_map[parent_id]
                current_path = os.path.join(path, folder_name)
                folder_list.append(current_path)
            else:
                current_path = path

            for sub_name, sub_id in subcollections:
                folder_list.extend(traverse_and_collect_folders(sub_id, current_path))
            return folder_list

        # Start traversal and collect folder paths
        all_folders = traverse_and_collect_folders()

        # Print all folders
        print("[INFO] All folders (including parent folders):")
        for folder in all_folders:
            print(folder)

        # Create folders on the filesystem
        print("\n[INFO] Creating folders in the target directory...")
        for folder in all_folders:
            folder_path = os.path.join(target_dir, folder)
            os.makedirs(folder_path, exist_ok=True)
            print(f"[INFO] Created folder: {folder_path}")

        print("[INFO] Folder structure created successfully!\n")
        return all_folders, conn, cursor  # Return the database connection for further use
    except Exception as e:
        print(f"[ERROR] {e}")

# Function to find PDFs in the Zotero storage directory
def find_pdf_in_storage(file_name):
    for root, _, files in os.walk(base_storage_dir):
        if file_name in files:
            return os.path.join(root, file_name)
    return None

# Function to copy PDFs to the appropriate target folder
def copy_pdf_to_target(pdf_path, target_dir, collection_name):
    target_collection_dir = os.path.join(target_dir, collection_name)
    os.makedirs(target_collection_dir, exist_ok=True)  # Ensure the collection directory exists
    target_pdf_path = os.path.join(target_collection_dir, os.path.basename(pdf_path))
    shutil.copy2(pdf_path, target_pdf_path)  # Copy the PDF
    return target_pdf_path

# Call the function to create folder structure
all_folders, conn, cursor = create_folder_structure_with_print(original_db_path, zotero_dir, target_dir)

# Fetch and process PDFs for each collection
try:
    directories_without_pdfs = []

    for folder in all_folders:
        collection_name = os.path.basename(folder)
        print(f"\n --------------------------------------------------------------- ")
        print(f"[INFO] Processing collection: {collection_name} ...")
        pdf_found = False  # Track if PDFs are found in this directory

        # Fetch items within the collection
        cursor.execute("""
            SELECT items.itemID, itemDataValues.value
            FROM items
            JOIN collectionItems ON items.itemID = collectionItems.itemID
            JOIN itemData ON items.itemID = itemData.itemID
            JOIN itemDataValues ON itemData.valueID = itemDataValues.valueID
            WHERE collectionItems.collectionID = (
                SELECT collectionID FROM collections WHERE collectionName = ?
            )
              AND itemData.fieldID = (SELECT fieldID FROM fields WHERE fieldName = 'title')
        """, (collection_name,))
        items = cursor.fetchall()

        for item_id, title in items:
            # Fetch PDF attachments for each item
            cursor.execute("""
                SELECT itemAttachments.path
                FROM itemAttachments
                WHERE itemAttachments.parentItemID = ?
                  AND itemAttachments.path IS NOT NULL
            """, (item_id,))
            attachments = cursor.fetchall()

            for attachment in attachments:
                relative_path = attachment[0].replace("storage:", "").replace("\\", "/")
                if relative_path.endswith(".pdf"):
                    file_path = find_pdf_in_storage(relative_path.split('/')[-1])
                    if file_path:
                        target_path = copy_pdf_to_target(file_path, target_dir, collection_name)
                        # Updated print message
                        print(f" - [{relative_path}, {title}] -> [{target_path}]")
                        pdf_found = True
                    else:
                        print(f"[WARNING] PDF not found for item: {title} ({relative_path})")

        if not pdf_found:
            directories_without_pdfs.append(collection_name)

    # Print directories without PDFs
    if directories_without_pdfs:
        print("\n ======================== \n[INFO] Collections with no PDFs:")
        for collection_name in directories_without_pdfs:
            print(f"  - {collection_name}")

    conn.close()

except Exception as e:
    print(f"[ERROR] {e}")
