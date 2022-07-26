# Import external modules
import sys
import os
from tendo import singleton

# Import internal modules
import sources_db
import get_annots
import notes_app
import gui


# Terminate program if other instance is running
me = singleton.SingleInstance() 

# Get queried collection name from user entry
collection_name = ' '.join(str(entry.lower()) for entry in sys.argv[1:]) 
collection_name = collection_name.replace('"', '') # Remove any quotation marks
print(f'OPENING COLLECTION: {collection_name.title()}')

# Query Zotero database and return sources
zotero_folder = os.path.normpath('C:\\Users\\dlwal\\Zotero')
zotero_location = os.path.normpath(zotero_folder + '\\zotero.sqlite')
zotero_data_raw = sources_db._sql_query(zotero_location)
zotero_data_processed = sources_db._process_data(zotero_data_raw)

# Add/remove sources from local DB to match Zotero data
app_data_location = os.path.normpath(zotero_folder + '\\app_data.json')
app_data = sources_db._update_data(app_data_location, zotero_data_processed)

# Start GUI
print(app_data[0])
gui._main(app_data, collection_name, app_data_location)