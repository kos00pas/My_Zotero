"""
find structure
    1. OneDrive/My_zotero
    2. zoterosql

"""


import os
import shutil
import sqlite3

def copy_sql(original_db_path):
        try:
            if not os.path.exists(original_db_path):
                raise FileNotFoundError("File not found")

            copy_db_path = os.path.join(os.path.dirname(original_db_path), "zoteroCopy.sqlite")

            shutil.copy(original_db_path, copy_db_path)

            print("Copy successful")
            print(f"\tSource: {original_db_path}")
            print(f"\tDestination: {copy_db_path}")
            return copy_db_path
        except Exception as e:
            print("An error occurred")
            print(f"Error: {e}")
            return None

def find_sqlite_collections(db_path):
   if not os.path.exists(db_path):
        print(f"Not found : {db_path} ")
        return None
   try:
       con = sqlite3.connect(db_path)
       cur = con.cursor()
       cur.execute("""
            select * from (SELECT name 
            FROM sqlite_master
            WHERE type = 'table'
            AND name = 'collections') smn;
            """)

       if not cur.fetchone():
           print( "The 'collections' table does not exist.")
           return None
       else:
           # cur.execute("SELECT collectionName, collectionID, parentCollectionID FROM collections;")
           cur.execute("SELECT collectionName, collectionID, parentCollectionID,key FROM collections;")
           rows = cur.fetchall()
           # CREATE TABLE collections (
           #      collectionID INTEGER PRIMARY KEY,
           #      collectionName TEXT NOT NULL,
           #      parentCollectionID INT DEFAULT NULL,
           #      clientDateModified TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
           #      libraryID INT NOT NULL,
           #      key TEXT NOT NULL,
           #      version INT NOT NULL DEFAULT 0,
           #      synced INT NOT NULL DEFAULT 0,
           #      UNIQUE (libraryID, key),
           #      FOREIGN KEY (libraryID) REFERENCES libraries(libraryID) ON DELETE CASCADE,
           #      FOREIGN KEY (parentCollectionID) REFERENCES collections(collectionID) ON DELETE CASCADE
           #   );
           print(rows)
           parsed_data = [
                {"collectionName": row[0],
                 "collectionID": row[1],
                 "parentCollectionID": row[2],
                 "key":row[3]} for row in rows
                ]
           return parsed_data

   except sqlite3.Error as err:
       print(f"Error : {err}")