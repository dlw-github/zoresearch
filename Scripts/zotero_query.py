from pathlib import Path
import sqlite3
import json
import os
import shutil
import pandas as pd
import pdfkit
import numpy as np


def _sql_query(zotero_location):
	'''Creates a copy of the Zotero DB and queries for source metadata. Returns two DB 
	which have to be merged
	'''
	zotero_copy = os.path.dirname(zotero_location) + '\\zotero_copy.sqlite'
	shutil.copyfile(zotero_location, zotero_copy)
	con = sqlite3.connect(zotero_copy)

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
	os.remove(zotero_copy)
	return ([df_1, df_2])


# TASK: figure out a way to get rid of this
def _lower(collections):
	'''Lower case for all collections'''
	# print(collections)
	new_list = []
	for collection in collections:
		new_list.append(collection.lower())
	return new_list


def _process_data(zotero_data_raw):
	df_1 = zotero_data_raw[0]
	df_2 = zotero_data_raw[1]

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
	# df_merge['annots'] = ''
	# df_merge['annots'] = df_merge['annots'].apply(list)
	# df_merge['all_notes'] = ''
	# df_merge['read'] = False

	df_merge['collections'] = df_merge['collections'].apply(lambda x: _lower(x))
	zotero_data_processed = df_merge.to_dict('records')

	return zotero_data_processed

