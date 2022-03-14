'''
1. Find Zot Collection key using passed arg, 'Collection name'
2. For each source where type!='attachment':
	a) Open Zot folder using item key
	b) select PDF as doc if available
	c) If not, convert HTML to PDF
3. Source object includes metadata and file location of PDF
	Attachment location: zotero/storage/[source_key]/[source_title].pdf
4. If project JSON already exists (where?):
	a) Run PDF annotate on each source attachment and update annots as needed
	b) If source key ! in JSON, add
5. If project JSON doesn't exist:
	a) Run PDF annotate on each and add 
'''
# Connect to Zotero
import sqlite3
import pandas as pd
import json
import os
import sys
import pdfkit
import shutil
# from weasyprint import html

import get_annots
import notes_app


def _html_to_pdf(source):
	# print('\tConverting attachment to PDF')
	# print('\t\t' + str(source['file_loc']))
	pdf_path = source['file_loc'][ : -4] + 'pdf'
	try:
		pdfkit.from_file(source['file_loc'], pdf_path, verbose=False, options=(
				{'disable-javascript': True, 
				'load-error-handling': 'ignore'}
			)
		)
	except OSError:
		print('\tWKHTML is complaining')
	source['file_loc'] = pdf_path
	return source

def _find_attachments(source):
	if os.path.exists(source['file_loc']):
		if str(source['file_loc']).endswith('.html'):
			print('\tZotero attachment is HTML. Files in dir:')
			for file in os.listdir(os.path.dirname(source['file_loc'])):
				if file.endswith('.pdf'):
					print('\tAttached PDF found. No need to convert')
					source['file_loc'] = source['file_loc'][ : -4] + 'pdf'
					break
			if str(source['file_loc']).endswith('.html'):
				print('\t No PDF found need to convert')
				source = _html_to_pdf(source)
	else:
		source['file_loc'] = None

	print('\tFile:' + str(source['file_loc']))
	return source


def _update_project(sources, collection_location, collection_name):
	print('Update existing project: ' + collection_name)

	with open(collection_location, 'r') as f:
		existing_sources = json.loads(f.read())

		for i, source in enumerate(sources):
			print('[{}/{}] {}'.format(i+1, len(sources),source['title']))
			included = 0
			for existing in existing_sources:
				if source['key'] == existing['key']:
					included = 1
					print('\tSource in project file')
					source['file_loc'] = existing['file_loc']
					source['annots'] = existing['annots']
					source['all_notes'] = existing['all_notes']
			if included == 0 and source['file_loc']!=None :
				print('\tAdding to project file')
				source = _find_attachments(source)
			
			if source['file_loc'] != '' and source['file_loc'] != None:
				source = get_annots._main(source)
			print('\n')

	sources.insert(0,existing_sources[0])
	return sources


def _create_project(sources, collection_name):
	# For each source:
	# 	1. associate attachments (if any)
	# 	2. convert attachments from HTML to PDF (if needed)
	# 	3. extract annotations and add to dictionary (if new)
	print('Creating new project: ' + collection_name)

	for i, source in enumerate(sources):
		print('[{}/{}] {}'.format(i+1, len(sources),source['title']))
		
		# For each source with an attachment, get annots from attachment
		if source['file_loc'] != None:
			source = _find_attachments(source)
		if source['file_loc'] != None:
			source = get_annots._main(source)
		print('\n')

	# Add general notes
	sources.insert(0, {
					'key': 0,
					'title': 'General notes',
					'short_title': 'General notes',
					'url': '',
					'file_loc': None,
					'annots': [],
					'all_notes': ''
					}
				)
	return sources


def _get_sources(collection_name):

	data = os.path.normpath('C:\\Users\\dlwal\\Zotero\\zotero.sqlite')
	data_copy = os.path.normpath('C:\\Users\\dlwal\\Zotero\\zotero_notes_app.sqlite')

	shutil.copyfile(data, data_copy)

	con = sqlite3.connect(data_copy)
	
	df_1 = pd.read_sql_query('''
				SELECT  
					itemData.itemID,
					items.key,
					max(itemDataValues.value) filter(where itemData.fieldID = 1) title,
					max(itemDataValues.value) filter(where itemData.fieldID = 8) short_title,
					max(itemDataValues.value) filter(where itemData.fieldID = 13) url
				FROM itemDataValues
				INNER JOIN itemData ON 
					itemDataValues.valueID = itemData.valueID
				INNER JOIN collectionItems ON
					itemData.itemID = collectionItems.itemID
				INNER JOIN items ON 
					items.itemID = collectionItems.itemID
				INNER JOIN collections ON 
					collections.collectionID = collectionItems.collectionID
				WHERE 
					collectionName = ?
					AND (
						itemData.fieldID = 8 
						OR itemData.fieldID = 13 
						OR itemData.fieldID = 1
						)
				GROUP BY 
					items.key
				'''
			, con,
			params=[collection_name]
			)

	df_2 = pd.read_sql_query('''
			SELECT
				itemAttachments.itemID as attachID,
				itemAttachments.parentItemID,
				itemAttachments.path,
				items.key as attachkey
			FROM 
				items
			INNER JOIN
				itemAttachments
			ON
				items.itemID = itemAttachments.itemID
			INNER JOIN 
				collectionItems
			ON 
				itemAttachments.parentItemID = collectionItems.itemID
			INNER JOIN 
				collections 
			ON 
				collections.collectionID = collectionItems.collectionID
			WHERE 
				collectionName = ?
			''',
		con,
		params=[collection_name]
		)

	con.close()
	os.remove(data_copy)

	df_1 = df_1.astype(str)
	
	df_2 = df_2[df_2['path'].isnull()==False]
	df_2['path'] = df_2['path'].astype(str)
	df_2['path'] = df_2['path'].str.slice(start=8)
	df_2['attach_num'] = df_2.groupby('parentItemID')['attachkey'].transform('nunique')
	df_2['pdf'] = df_2['path'].str.endswith('pdf')
	df_2['html'] = df_2['path'].str.endswith('html')
	df_2 = df_2.drop(df_2[(df_2['attach_num'] > 1) & (df_2['pdf'] == False) & (df_2['html'] == False)].index)
	df_2['attach_num'] = df_2.groupby('parentItemID')['attachkey'].transform('nunique')
	df_2 = df_2.drop(df_2[(df_2['attach_num'] > 1) & (df_2['pdf'] == False) & (df_2['html'] == True)].index)
	df_2 = df_2.astype(str)

	df_merge = pd.merge(df_1, df_2, how='left', left_on=df_1['itemID'], right_on=df_2['parentItemID'])
	df_merge['file_loc'] = 'C:\\Users\\dlwal\\Zotero\\storage\\' + df_merge['attachkey'] + '\\' + df_merge['path']
	df_merge = df_merge[['key', 'title',  'short_title', 'url', 'file_loc']]
	df_merge = df_merge.where(pd.notnull(df_merge), None)
	df_merge.sort_values(by=['title'], inplace=True)
	
	sources = df_merge.to_dict('records')

	for i, source in enumerate(sources):
		source['annots'] = []
		source['all_notes'] = ''
		# print(str(i+1) + ': ' + source['title'])
		# print('\tFile loc: ' + str(source['file_loc']))
		# print('\n')


	return sources


def _main(collection_name):	
	
	# Get list of Zotero sources in collection
	sources = _get_sources(collection_name)

	# Check if project file exists
	collection_location = 'C:\\Users\\dlwal\\Dropbox\\research_projects\\' + collection_name + '.json'
	if os.path.exists(collection_location):
		sources = _update_project(sources, collection_location, collection_name)
	else:
		sources = _create_project(sources, collection_name)


	print('Opening project in Notes App')
	with open(collection_location, 'w', encoding='utf-8') as f:
		json.dump(sources, f, indent=4)
	notes_app._main(collection_location)
	

if __name__ == '__main__':
	if len(sys.argv)>2:
		collection_name=''
		for word in sys.argv[1:]:
			collection_name += (' ' + word)
		_main(collection_name[1: ].replace("'",""))
	else:
		_main(sys.argv[1])

