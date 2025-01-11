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

def fetch_structure_with_all_folders(cursor):
    print("[INFO] Fetching collections and subcollections...")

    # Fetch all collections with parentCollectionID to identify the hierarchy
    cursor.execute("SELECT collectionName, collectionID, parentCollectionID FROM collections")
    all_collections = cursor.fetchall()

    # Build a dictionary to map parentCollectionID to subcollections
    collection_map = {}
    id_to_name_map = {}
    for collection in all_collections:
        collection_name, collection_id, parent_id = collection
        if parent_id not in collection_map:
            collection_map[parent_id] = []
        collection_map[parent_id].append((collection_name, collection_id))
        id_to_name_map[collection_id] = collection_name

    def traverse_and_collect(parent_id=None, path=""):
        folder_list = []
        subcollections = collection_map.get(parent_id, [])
        if parent_id is not None:  # Add the parent folder itself
            folder_name = id_to_name_map[parent_id]
            current_path = os.path.join(path, folder_name)
            folder_list.append(current_path)
        else:
            current_path = path

        for sub_name, sub_id in subcollections:
            folder_list.extend(traverse_and_collect(sub_id, current_path))
        return folder_list

    # Start from top-level collections (parent_id=None)
    all_folders = traverse_and_collect()
    return all_folders

try:
    print("[INFO] Checking if Zotero database exists...")
    if not os.path.exists(original_db_path):
        raise FileNotFoundError(f"[ERROR] Zotero database not found at {original_db_path}")

    print("[INFO] Creating a copy of the Zotero database...")
    db_path = create_zotero_copy(original_db_path)

    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    cursor = conn.cursor()

    print("[INFO] Fetching Zotero Library Structure...")
    all_folders = fetch_structure_with_all_folders(cursor)

    print("[INFO] All folders (including parent folders):")
    for folder in all_folders:
        print(folder)

except Exception as e:
    print(f"[ERROR] {e}")

#
# # Base storage directory for PDFs
# base_storage_dir = r"C:\Users\kos00\OneDrive - University of Cyprus\Zeroto_Drive\storage"
#
# # Path to Zotero SQLite database
# db_path = r"C:\Users\kos00\OneDrive - University of Cyprus\Zeroto_Drive\zoteroCopy.sqlite"
#
# def find_pdf_in_storage(file_name):
#     """Search for the given file name in all subdirectories of the storage directory."""
#     for root, _, files in os.walk(base_storage_dir):
#         if file_name in files:
#             return os.path.join(root, file_name)
#     print("\t\tNONE NONE NONE\t")
#     return None
#
# try:
#     conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
#     cursor = conn.cursor()
#
#     print("Zotero Library Structure:")
#
#     # List to track directories with no PDFs
#     directories_without_pdfs = []
#
#     # Fetch collections
#     cursor.execute("SELECT collectionName, collectionID FROM collections")
#     collections = cursor.fetchall()
#
#     for collection in collections:
#         print(f"Folder: {collection[0]} ... includes: " )
#         pdf_found = False  # Track if PDFs are found in this directory
#
#         # Fetch items within the collection
#         cursor.execute("""
#             SELECT items.itemID, itemDataValues.value
#             FROM items
#             JOIN collectionItems ON items.itemID = collectionItems.itemID
#             JOIN itemData ON items.itemID = itemData.itemID
#             JOIN itemDataValues ON itemData.valueID = itemDataValues.valueID
#             WHERE collectionItems.collectionID = ?
#               AND itemData.fieldID = (SELECT fieldID FROM fields WHERE fieldName = 'title')
#         """, (collection[1],))
#         items = cursor.fetchall()
#
#         for item_id, title in items:
#             print(f"  - {title}")
#
#             # Fetch PDF attachments for each item
#             cursor.execute("""
#                 SELECT itemAttachments.path
#                 FROM itemAttachments
#                 WHERE itemAttachments.parentItemID = ?
#                   AND itemAttachments.path IS NOT NULL
#             """, (item_id,))
#             attachments = cursor.fetchall()
#
#             for attachment in attachments:
#                 relative_path = attachment[0].replace("storage:", "").replace("\\", "")
#                 if relative_path.endswith(".pdf"):
#                     file_path = find_pdf_in_storage(relative_path)
#                     if file_path:
#                         print(f"\t    PDF: '{file_path}'")
#                         pdf_found = True
#                         # Replace base_target_dir with target_dir
#                         copy_pdf_to_target(file_path, target_dir, collection[0])
#
#                     else:
#                         print(f"[WARNING] PDF not found: {relative_path}")
#                         # Attempt to find the file in base_storage_dir
#                         actual_location = find_pdf_in_storage(relative_path.split('/')[-1])
#                         if actual_location:
#                             print(f"\t[INFO] Found actual location: {actual_location}")
#                         else:
#                             print(f"\t[ERROR] Unable to locate PDF: {relative_path}")
#
#         # If no PDFs were found for the collection, add it to the list
#         if not pdf_found:
#             directories_without_pdfs.append(collection[0])
#
#     conn.close()
#
#
#
# except Exception as e:
#     print(f"Error: {e}")