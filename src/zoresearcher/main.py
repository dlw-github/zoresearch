# Import external modules
import sys
import os
from tendo import singleton

# Import internal modules
import zoresearcher.sources_db
import zoresearcher.gui



def open(zotero_folder, collection_name='all'):
	# Terminate program if other instance is running
	me = singleton.SingleInstance() 

	# Get queried collection name from user entry
	# if len(collection_name.split()) > 1:
	# 	collection_name = ' '.join(str(entry.lower()) for entry in collection_name) 
	collection_name = collection_name.lower()
	# collection_name = collection_name.replace('"', '') # Remove any quotation marks
	print(f'OPENING COLLECTION: {collection_name.title()}')

	# Query Zotero database and return sources
	zotero_folder = zotero_folder.replace('"', '') # Remove any quotation marks
	zotero_folder = zotero_folder.replace("'", "") # Remove any quotation marks

	zotero_folder = os.path.normpath(zotero_folder)
	zotero_location = os.path.normpath(zotero_folder + '\\zotero.sqlite')
	zotero_data_raw = zoresearcher.sources_db._sql_query(zotero_location)
	zotero_data_processed = zoresearcher.sources_db._process_data(zotero_data_raw, zotero_folder)

	# Add/remove sources from local DB to match Zotero data
	app_data_location = os.path.normpath(zotero_folder + '\\app_data.json')
	app_data = zoresearcher.sources_db._update_data(app_data_location, zotero_data_processed)

	# Start GUI
	zoresearcher.gui._main(app_data, collection_name, app_data_location)


if __name__ == '__main__':
	print("This is my file to test Python's execution methods.")
	print("The variable __name__ tells me which context this file is running in.")
	print("The value of __name__ is:", repr(__name__))
	zotero_folder = sys.argv[1]
	collection_name = ' '.join(sys.argv[2:]).strip()
	if not collection_name:
		collection_name = 'all'
	print(zotero_folder)
	print(collection_name)
	open(zotero_folder, collection_name)
