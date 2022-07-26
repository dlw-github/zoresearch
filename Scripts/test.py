
source_type= 'starred'
selected_collection = (23, 7, 9, 14)


selected_collection = [source for source in selected_collection if source>10]

	
if source_type == 'starred':
	print('yah')
	selected_collection = [source for source in selected_collection if source>20]

if source_type == 'unread':
	selected_collection = [source for source in selected_collection if source.read==False]

print(selected_collection)