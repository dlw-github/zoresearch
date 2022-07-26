import sys
import sqlite3
import json
import os
import shutil
import pandas as pd
import pdfkit
import numpy as np
import threading 
import time
from tendo import singleton


import get_annots
import notes_app


def _add_sources(source):
	if source['_merge'] == 'right_only':
		print('\t\t{}'.format(source['title_zot']))
		title = source['title_zot']
		short_title = source['short_title_zot']
		url = source['url_zot']
		attachment = source['attachment_zot']
		date_added = source['date_added_zot']
		annots = source['annots_zot']
		all_notes = source['all_notes_zot']
		read = source['read_zot']
	else:
		title = source['title']
		short_title = source['short_title']
		url = source['url']
		attachment = source['attachment']
		date_added = source['date_added']
		annots = source['annots']
		all_notes = source['all_notes']
		read = source['read']

	collections=[]
	try:
		for collection in source['collections']:
			collections.append(collection.lower())
	except TypeError:
		print('\t\tError altering collections: {}'.format(source['title']))

	return pd.Series([source['key'], title, short_title, url, attachment, date_added, collections, annots, all_notes, read])


def _update_dataset(zotero_data, data_path):
	print('1. UPDATING SOURCES IN DATASET')
	with open(data_path, 'r') as f:
		notes_data = pd.read_json(f)
	print('\t{} sources in notes dataset\n\t{} sources in Zotero dataset\n'.format(len(notes_data),len(zotero_data)))
	
	notes_data = notes_data.merge(zotero_data, how='outer', on='key', suffixes=('', '_zot'), indicator=True)
	# print(notes_data['_merge'].value_counts())

	# Add new sources
	print('\ta) ADDING NEW SOURCES:')

	notes_data['collections'] = notes_data['collections_zot']
	notes_data[['key', 'title', 'short_title', 'url', 'attachment', 'date_added', 'collections', 'annots', 'all_notes', 'read']] = notes_data.apply(lambda source: _add_sources(source), axis=1)


	# Remove deleted sources
	print('\tb) REMOVING DELETED SOURCES:')
	if notes_data[notes_data['_merge']=='left_only']['title'].shape[0]>0:
		for key, value in notes_data[notes_data['_merge']=='left_only']['title'].iteritems():
			print('\t\t' + value)
	else:
		print()
	notes_data = notes_data[notes_data['_merge']!='left_only']

	# Remove unneeded columns
	notes_data = notes_data[['key', 'title', 'short_title', 'url', 'attachment', 'date_added', 'collections', 'annots', 'all_notes', 'read']]
	notes_data = notes_data.to_dict('records')

	return notes_data

def _get_zotero_data():
	data = os.path.normpath('C:\\Users\\dlwal\\Zotero\\zotero.sqlite')
	data_copy = os.path.normpath('C:\\Users\\dlwal\\Zotero\\zotero_notes_app.sqlite')

	shutil.copyfile(data, data_copy)

	con = sqlite3.connect(data_copy)

	df_1 = pd.read_sql_query('''
			SELECT 
				*
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
				(itemData.fieldID = 1
				OR itemData.fieldID = 8 
				OR itemData.fieldID = 13
				)
				AND collections.libraryID = 1
				'''
			, con,
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
				collections.libraryID = 1
			''',
		con,
		)

	con.close()
	os.remove(data_copy)

	return ([df_1, df_2])

def _process_zotero_data(zotero_raw):
	df_1 = zotero_raw[0]
	df_2 = zotero_raw[1]

	# Change all data types to strings
	df_1 = df_1.astype(str)
	df_2 = df_2.astype(str)

	# Keep necessary columns
	df_1.columns.values[22] = "key_2" # disambiguate 'key' column
	df_1 = df_1[['value', 'itemID', 'clientDateModified', 'key', 'collectionName', 'fieldID']]
	df_1 = df_1.iloc[:, [0, 1, 4, 6, 7, 8]] # get rid of dupulicate cols (not sure why cols get duplicated)

	# Unstack metadata by fieldID ('title', 'short_title', 'url')
	unstacked = df_1.groupby(['key', 'fieldID'])['value'].aggregate('first').unstack()
	unstacked = unstacked.reset_index()
	unstacked = unstacked.rename(columns={'1': 'title', '8': 'short_title', '13': 'url'})
	df_1 = df_1.merge(unstacked,on='key')
	df_1 = df_1[['key', 'itemID', 'title', 'url', 'short_title', 'collectionName', 'clientDateModified']]

	#Remove sources without attachments from attachments dataset and remove 'storage:' prefix
	df_2 = df_2[df_2['path']!='None'].reset_index()
	df_2['path'] = df_2['path'].str.slice(start=8)

	# Label attachments by filetype ('pdf', 'html') and keep only 1 per source (prioritize 'pdf')
	df_2['attach_num'] = df_2.groupby('parentItemID')['attachkey'].transform('nunique')
	df_2['pdf'] = df_2['path'].str.endswith('pdf')
	df_2['html'] = df_2['path'].str.endswith('html')
	df_2 = df_2.drop(df_2[(df_2['attach_num'] > 1) & (df_2['pdf'] == False) & (df_2['html'] == False)].index) # catch any sources w/o attachments
	
	# Repeat labeling and remove HTML sources if PDF is available
	df_2['attach_num'] = df_2.groupby('parentItemID')['attachkey'].transform('nunique')
	df_2 = df_2.drop(df_2[(df_2['attach_num'] > 1) & (df_2['pdf'] == False) & (df_2['html'] == True)].index)

	# Merge datasets
	df_merge = pd.merge(df_1, df_2, how='left', left_on=df_1['itemID'], right_on=df_2['parentItemID'])
	df_merge['attachment'] = 'C:\\Users\\dlwal\\Zotero\\storage\\' + df_merge['attachkey'] + '\\'
	df_merge = df_merge[['key', 'title',  'short_title', 'url', 'attachment', 'collectionName', 'clientDateModified']]
	df_merge = df_merge.rename(columns={"clientDateModified": "date_added"})
	df_merge = df_merge.drop_duplicates()
	collections = df_merge.groupby(['key'])['collectionName'].apply(lambda x: list(x.unique())).reset_index(name='collections')
	df_merge = df_merge.merge(collections, on='key')
	df_merge = df_merge.drop(['collectionName'], axis=1)
	df_merge.sort_values(by=['title'], inplace=True)
	df_merge.reset_index(inplace=True)
	df_merge = df_merge.groupby('key').first().reset_index()
	df_merge = df_merge.drop('index', axis=1)


	# Add new elements for each source
	df_merge['annots'] = ''
	df_merge['annots'] = df_merge['annots'].apply(list)
	df_merge['all_notes'] = ''
	df_merge['read'] = False

	return df_merge


def _html_to_pdf(attachment, html):
	print('\t\tConverting HTML file to PDF: {}'.format(html))
	html = attachment + html
	pdf_path = html[ : -4] + 'pdf'
	try:
		attachment = pdfkit.from_file(html, pdf_path, verbose=False, options=(
				{
				'disable-javascript': True
				, 'load-error-handling': 'ignore'
				}
			)
		)
	
	except OSError:
		print('\t\t\tWKHTML is complaining')
	return pdf_path


def _find_attachments(attachment):
	# print('\t\tInitial attachment value: {}'.format(attachment))

	# Return if PDF is already located or if no attachment exists
	if attachment is None:
		return attachment

	if attachment.endswith('.pdf'):
		# print('\t\tPDF already exists or no attachment: {}'.format(attachment))
		return attachment


	# Otherwise, attachment points to directory. Convert HTML to PDF if needed
	else:
		# print('\t\t\tSearching for file in folder {}'.format(attachment))
		try:
			directory = os.listdir(attachment)
			pdf = [match for match in directory if '.pdf' in match]
			if pdf:
				# print('\t\tPDF found in source folder: {}'.format(pdf[0]))
				attachment = attachment + pdf[0]
				return attachment
			else:
				html = [match for match in directory if '.html' in match]
				if html:
					attachment = _html_to_pdf(attachment, html[0])
					return attachment
				else:
					# print('\t\tNo attachment found in folder; return none')
					return None
		except FileNotFoundError:
			return None


def _background_update(passed_var):
	print('3. BACKGROUND FUNCTION: UPDATING ATTACHMENTS & ANNOTATIONS FOR OTHER SOURCES')
	for i in range(0,100000):
		print(i)

	passed_var = 'cat'
	return

	# other_sources = [source for source in notes_data if collection_name not in source['collections']]
	
	# for i, source in enumerate(other_sources):
	# 	print('\t[{}/{}] {}'.format(i+1, len(other_sources), source['title']))
	# 	# source['attachment'] = _find_attachments(source['attachment'])
	# 	# print('\t\t{}'.format(source['attachment']))
	# 	# source = get_annots._main(source)
	# 	# print('\t\t\tAll notes: {}'.format(source['all_notes']))
	# 	print()
	# return 'animals'

def update_data(notes_data, collection_name, dummy):
	print('3. BACKGROUND FUNCTION: UPDATING ATTACHMENTS & ANNOTATIONS FOR OTHER SOURCES')
	other_sources = [source for source in notes_data if collection_name not in source['collections']]
	
	for i, source in enumerate(other_sources):
		print('\t[{}/{}] {}'.format(i+1, len(other_sources), source['title']))
		source['attachment'] = _find_attachments(source['attachment'])
		print('\t\t{}'.format(source['attachment']))
		source = get_annots._main(source)
		print('\t\t\tAll notes: {}'.format(source['all_notes']))
		print()
	dummy.append(True)

	print('BACKGROUND FUNCTION COMPLETE')

def _lower(collections):
	print(collections)
	new_list = []
	for collection in collections:
		new_list.append(collection.lower())
	return new_list


def _main(collection_name):	
	
	# Print collection name
	collection_name = collection_name.lower()
	print('OPENING COLLECTION: {}'.format(collection_name.upper()))
	
	# Get Zotero library sources
	zotero_raw = _get_zotero_data()
	zotero_processed = _process_zotero_data(zotero_raw)

	# Check for existing notes dataset
	data_path = os.path.normpath('C:\\Users\\dlwal\\Zotero\\notes_app_data.json')
	
	# If notes dataset exists, update it
	if os.path.exists(data_path):
		notes_data = _update_dataset(zotero_processed, data_path)
	
	# If notes dataset hasn't already been created, save Zotero data as notes dataset 
	else:
		print('No dataset exists. Creating from Zotero data')
		print(zotero_processed['collections'].head())
		zotero_processed['collections'] = zotero_processed['collections'].apply(lambda x: _lower(x))
		notes_data = zotero_processed.to_dict('records')

		print(notes_data[0])
	
	# Update attachments and annotations for selected collection
	print('2. {} COLLECTION: UPDATING ATTACHMENTS & ANNOTATIONS'.format(collection_name.upper()))
	print()
	selected_collection = [source for source in notes_data if collection_name in source['collections']]
	print(len(selected_collection))
	print()

	for i, source in enumerate(selected_collection):
		print('\t[{}/{}] {}'.format(i+1, len(selected_collection), source['title']))
		source['attachment'] = _find_attachments(source['attachment'])
		print('\t\t{}'.format(source['attachment']))
		source = get_annots._main(source)
		print('\t\t\tAll notes: {}'.format(source['all_notes']))
		print()

	# Open GUI
	notes_app._main(notes_data, collection_name)



if __name__ == '__main__':
	me = singleton.SingleInstance() # will sys.exit(-1) if other instance is running

	if len(sys.argv)>2:
		collection_name=''
		for word in sys.argv[1:]:
			collection_name += (' ' + word)
		_main(collection_name[1: ].replace("'",""))
	else:
		_main(sys.argv[1])

