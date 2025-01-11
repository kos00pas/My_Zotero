"""
pdf location :
        -> only in OneDrive/My_Zotero
zotero/storage
    -> links only to each pdf
"""

"""if change -> take action 
    changes :{new key , deleted key , change structure }
    new key: save it in the corresponding folder 
    delete key : move into trash bin of my_zotero
    new structure:   
"""
"""
we have to have booth structures 
"""
"""
maybe make my database to trach the changes 
"""


#  https://github.com/zotero/zotero/blob/main/resource/schema/userdata.sql
from The_Functions import *


zeroto_storage = r"C:\Users\kos00\OneDrive - University of Cyprus\Zeroto_Drive"
# find sqllite , make copy
database = "zotero.sqlite"
zeroto_database = os.path.join(zeroto_storage, f"{database}")

"""copy sqllite"""
copy_zeroto_database = copy_sql(zeroto_database)

"""find sqllite"""
results = find_sqlite_collections(copy_zeroto_database)
print(results)
all_keys=[r['key'] for r in results]
print(all_keys)



