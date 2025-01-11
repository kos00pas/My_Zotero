"""
goal : automate copy to the same format
"""

import sqlite3
import os
import shutil

import shutil

def copy_pdf_to_target(pdf_path, base_target_dir, hierarchy):
    """
    Copies the PDF to a dynamically generated target folder structure.
    :param pdf_path: Path of the PDF to copy.
    :param base_target_dir: Base directory for the target folders.
    :param hierarchy: List of folder levels to create for the target.
    """
    target_dir = generate_dynamic_target_dir(base_target_dir, hierarchy)
    target_path = os.path.join(target_dir, os.path.basename(pdf_path))
    try:
        shutil.copy2(pdf_path, target_path)
        print(f"[INFO] Copied PDF to: {target_path}")
    except Exception as e:
        print(f"[ERROR] Could not copy PDF '{pdf_path}' to '{target_dir}': {e}")


# Path to Zotero database directory
zotero_dir = r"C:\Users\kos00\OneDrive - University of Cyprus\Zeroto_Drive"

# Path to the Zotero database
original_db_path = os.path.join(zotero_dir, "zotero.sqlite")

# Function to create a copy of Zotero database
def create_zotero_copy(original_path):
    copy_path = os.path.join(zotero_dir, "zoteroCopy.sqlite")
    shutil.copy2(original_path, copy_path)
    print(f"[INFO] Created a copy of Zotero database at: {copy_path}")
    return copy_path

# Function to fetch folder and subfolder structure from SQLite
# Function to fetch folder and subfolder structure from SQLite
def fetch_structure_from_db(cursor):
    print("[INFO] Fetching collections and subcollections...")

    # Fetch all collections with parentCollectionID to identify the hierarchy
    cursor.execute("SELECT collectionName, collectionID, parentCollectionID FROM collections")
    all_collections = cursor.fetchall()

    # Separate top-level collections (parentCollectionID is NULL) and subfolders
    top_collections = [c for c in all_collections if c[2] is None]
    subfolder_map = {}

    for collection in top_collections:
        # Fetch subfolders for each top-level collection
        subfolders = [c[0] for c in all_collections if c[2] == collection[1]]
        subfolder_map[collection[0]] = subfolders
        print(f"[DEBUG] Subfolders for '{collection[0]}': {subfolders}")

    # Return only top-level collections and the subfolder map
    return top_collections, subfolder_map

def generate_dynamic_target_dir(base_target_dir, hierarchy):
    """
    Dynamically generates a folder structure based on the hierarchy.
    :param base_target_dir: Base directory for folders.
    :param hierarchy: List of folder levels to create.
    :return: Full path of the dynamically generated directory.
    """
    target_dir = base_target_dir
    for level in hierarchy:
        target_dir = os.path.join(target_dir, level)
    os.makedirs(target_dir, exist_ok=True)
    return target_dir

# Function to create folder structure dynamically
def create_folder_structure_dynamic(target_dir, collections, subfolder_map):
    print(f"[INFO] Creating folder structure in '{target_dir}'...")
    os.makedirs(target_dir, exist_ok=True)

    for collection in collections:
        # Generate folder for each collection
        top_folder = generate_dynamic_target_dir(target_dir, [collection[0]])

        print(f"[INFO] Created folder: {top_folder}")

        # Create subfolders dynamically
        subfolders = subfolder_map.get(collection[0], [])
        for subfolder in subfolders:
            subfolder_path = generate_dynamic_target_dir(top_folder, [subfolder])
            print(f"[INFO] Created subfolder: {subfolder_path}")

# Main code
try:
    print("[INFO] Checking if Zotero database exists...")
    if not os.path.exists(original_db_path):
        raise FileNotFoundError(f"[ERROR] Zotero database not found at {original_db_path}")

    print("[INFO] Creating a copy of the Zotero database...")
    db_path = create_zotero_copy(original_db_path)

    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    cursor = conn.cursor()

    print("[INFO] Fetching Zotero Library Structure...")
    collections, subfolder_map = fetch_structure_from_db(cursor)

    target_dir = r"C:\Users\kos00\OneDrive - University of Cyprus\Zeroto_Drive\My_Zotero\My_Library"
    create_folder_structure_dynamic(target_dir, collections, subfolder_map)

    conn.close()
    print("[INFO] Folder structure creation completed successfully!")

except Exception as e:
    print(f"[ERROR] {e}")

##################################################
##################################################
##################################################
##################################################

import sqlite3
import os

# Base storage directory for PDFs
base_storage_dir = r"C:\Users\kos00\OneDrive - University of Cyprus\Zeroto_Drive\storage"

# Path to Zotero SQLite database
db_path = r"C:\Users\kos00\OneDrive - University of Cyprus\Zeroto_Drive\zoteroCopy.sqlite"

def find_pdf_in_storage(file_name):
    """Search for the given file name in all subdirectories of the storage directory."""
    for root, _, files in os.walk(base_storage_dir):
        if file_name in files:
            return os.path.join(root, file_name)
    print("\t\tNONE NONE NONE\t")
    return None

try:
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    cursor = conn.cursor()

    print("Zotero Library Structure:")

    # List to track directories with no PDFs
    directories_without_pdfs = []

    # Fetch collections
    cursor.execute("SELECT collectionName, collectionID FROM collections")
    collections = cursor.fetchall()

    for collection in collections:
        print(f"Folder: {collection[0]} ... includes: " )
        pdf_found = False  # Track if PDFs are found in this directory

        # Fetch items within the collection
        cursor.execute("""
            SELECT items.itemID, itemDataValues.value
            FROM items
            JOIN collectionItems ON items.itemID = collectionItems.itemID
            JOIN itemData ON items.itemID = itemData.itemID
            JOIN itemDataValues ON itemData.valueID = itemDataValues.valueID
            WHERE collectionItems.collectionID = ?
              AND itemData.fieldID = (SELECT fieldID FROM fields WHERE fieldName = 'title')
        """, (collection[1],))
        items = cursor.fetchall()

        for item_id, title in items:
            print(f"  - {title}")

            # Fetch PDF attachments for each item
            cursor.execute("""
                SELECT itemAttachments.path
                FROM itemAttachments
                WHERE itemAttachments.parentItemID = ?
                  AND itemAttachments.path IS NOT NULL
            """, (item_id,))
            attachments = cursor.fetchall()

            for attachment in attachments:
                relative_path = attachment[0].replace("storage:", "").replace("\\", "")
                if relative_path.endswith(".pdf"):
                    file_path = find_pdf_in_storage(relative_path)
                    if file_path:
                        print(f"\t    PDF: '{file_path}'")
                        pdf_found = True
                        # Replace base_target_dir with target_dir
                        copy_pdf_to_target(file_path, target_dir, collection[0])

                    else:
                        print(f"[WARNING] PDF not found: {relative_path}")
                        # Attempt to find the file in base_storage_dir
                        actual_location = find_pdf_in_storage(relative_path.split('/')[-1])
                        if actual_location:
                            print(f"\t[INFO] Found actual location: {actual_location}")
                        else:
                            print(f"\t[ERROR] Unable to locate PDF: {relative_path}")

        # If no PDFs were found for the collection, add it to the list
        if not pdf_found:
            directories_without_pdfs.append(collection[0])

    conn.close()



except Exception as e:
    print(f"Error: {e}")