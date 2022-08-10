# Import external modules
import sys
import os
from tendo import singleton

# Import internal modules
import zoresearch.sources_db
import zoresearch.gui



def open(zotero_folder, collection_name='all'):
	"""zoResearch main function
	Keword arguments:
	zotero_folder -- zotero folder filepath
	collection_name -- queried collection (default 'all')

	Creates zoResearch GUI based on Zotero data
	"""
	# Terminate program if other instance is running
	me = singleton.SingleInstance() 

	# Get queried collection name from user entry
	collection_name = collection_name.lower()
	print(f'OPENING COLLECTION: {collection_name.title()}')

	# Query Zotero database and return sources
	zotero_folder = zotero_folder.replace('"', '') # Remove any quotation marks
	zotero_folder = zotero_folder.replace("'", "") # Remove any quotation marks

	# Process Zotero data
	zotero_folder = os.path.normpath(zotero_folder)
	zotero_location = os.path.normpath(zotero_folder + '\\zotero.sqlite')
	zotero_data_raw = zoresearch.sources_db._sql_query(zotero_location)
	zotero_data_processed = zoresearch.sources_db._process_data(zotero_data_raw, zotero_folder)
	
	# Add/remove sources from local DB to match Zotero data
	app_data_location = os.path.normpath(zotero_folder + '\\zoresearch.json')
	app_data = zoresearch.sources_db._update_data(app_data_location, zotero_data_processed)

	# Start GUI
	zoresearch.gui._main(app_data, collection_name, app_data_location)


if __name__ == '__main__':
	"""Runs zoresearch.open when run as script"""
	zotero_folder = sys.argv[1]
	collection_name = ' '.join(sys.argv[2:]).strip()
	if not collection_name:
		collection_name = 'all'
	print(zotero_folder)
	print(collection_name)
	open(zotero_folder, collection_name)
