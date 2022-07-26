'''
!/usr/bin/env python
coding: utf-8

DESCRIPTION:
Opens GUI to view/edit research projects

INPUTS:
Project JSON

OUTPUTS:
Updated Project JSON
'''

# IMPORTS
import fitz
import sys
import os
import json
from tkinter import *
from tkinter import Tk, font
import webbrowser
from tkPDFViewer import tkPDFViewer as pdf
import time
from threading import Thread

import db

def _save_data(data):
	with open(data['file_path'], 'w') as f:
		json.dump(data['all_sources'], f, indent=4)
	print("Saved project file")


def _on_closing(data):
	print('Clicked close')
	self._save_source()
	self._save_data()
	data['root'].destroy()


def _save_source(data):
	source_to_save_num = data['click_stream'][-1]
	data['collection_data'][source_to_save_num]['all_notes']  = data['widgets']['text_widget'].get("1.0",END)
	return data


def _read_source(data):
	read_source_num = data['click_stream'][-1]
	read_dummy = data['collection_data'][read_source_num]['read'] 
	read_dummy = not read_dummy
	data['collection_data'][read_source_num]['read'] = read_dummy
	_save_source(data)


	if read_dummy == True:
		text = 'Read'
	else:
		text = 'Unread'
	print(f'Changing source read status to {text}')
	data['widgets']['read_label'].configure(text=text)


def _open_link(dest):
	if dest == '':
		return
	else:
		webbrowser.open_new(dest)


def _on_frame_configure(canvas):
    '''Reset the scroll region to encompass the inner frame'''
    canvas.configure(scrollregion=canvas.bbox("all"))


def _hover(event):
	# Check widget foreground and change only if not green
	current_fg = event.widget.cget("fg")
	print(f'Foreground color: {current_fg}')

	event.widget.config(background='#32ade6')
	if current_fg != '#006400':
		event.widget.config(foreground='white')


def _leave(event):
	current_fg = event.widget.cget("fg")
	event.widget.config(background='#E5E5E5')
	if current_fg != '#006400':
		event.widget.config(foreground='black')


def _on_mousewheel(event, canvas):
	change = int(-1*(event.delta/120))
	canvas.yview_scroll(change, "units")


def _set_mousewheel(widget, command):
    """Activate / deactivate mousewheel scrolling when 
    cursor is over / not over the widget respectively."""
    widget.bind("<Enter>", lambda _: widget.bind_all('<MouseWheel>', command))
    widget.bind("<Leave>", lambda _: widget.unbind_all('<MouseWheel>'))


def _display_source(event, labels, data, source_num):

	if event !='setup':
		for label in labels:
			label.config(background='#E5E5E5')
			label.config(relief='flat')
			if label.cget('fg') == 'white':
				label.config(foreground='black')
			label.bind('<Leave>', _leave)

		if event.widget.cget('fg') == 'black':
			event.widget.config(foreground='white')  

		event.widget.config(background='#32ade6')
		event.widget.unbind('<Leave>')

		data = _save_source(data)

	title_label = data['widgets']['title_label']
	url_label = data['widgets']['url_label']
	text_widget = data['widgets']['text_widget']
	text_widget.delete('1.0', END)
	read_label = data['widgets']['read_label']


	title_text = data['collection_data'][source_num]['title']
	url_text = data['collection_data'][source_num]['url']
	text_text = data['collection_data'][source_num]['all_notes'].strip()
	loc_text = data['collection_data'][source_num]['attachment']
	
	if data['collection_data'][source_num]['read'] == False:
		read_text = 'Unread'
	else:
		read_text = 'Read'

	title_label.config(text=title_text)
	title_label.bind("<Button-1>", lambda e: _open_link(loc_text))

	url_label.config(text=url_text)
	url_label.bind("<Button-1>", lambda e: _open_link(url_text))

	text_widget.insert('end', text_text)
	text_widget.config(font=('open sans', 10))

	read_label.config(text=read_text)
	read_label.bind("<Button-1>", lambda e: _read_source(data))


	data['click_stream'].append(source_num)

	if data['show_pdf'] == True:
		_display_PDF(data)

	return data


def _create_source_pane(data):
	'''Create clickeable buttons for each source
	'''
	# Create widgets
	canvas = Canvas(data['root'], background="#E5E5E5", width=220) 
	frame = Frame(canvas, background='#E5E5E5')
	source_scroll = Scrollbar(data['root'], orient="vertical", command=canvas.yview)
	source_label = Label(data['root'], text='Sources', font=('open sans', 10), bg='#E5E5E5', padx=0)

	# Configure widgets
	canvas.create_window((0,0), window=frame, anchor="nw")
	canvas.configure(yscrollcommand=source_scroll.set)
	frame.bind("<Configure>", lambda event, canvas=canvas: _on_frame_configure(canvas))

	# Grid widgets
	canvas.grid(row=2, column=0, sticky='nsew', padx=0)
	source_scroll.grid(row=2, column=1, sticky='ns')
	source_label.grid(row=1, column=0, rowspan=1, columnspan=2, sticky='nsew')

	labels=[]

	for source_num, source in enumerate(data['collection_data']):
		if source['short_title'] is not None:
			text = source['short_title']
		
		elif source['title'] is not None:
			text = source['title']

		else:
			text = 'Title unavailable'

		if len(text) > 80:
			text = text[ :80] + '...'

		label = Label(
						frame, 
						text=text,
						width=30,
						font=('open sans',10),
                        wraplength=200, 
                        bg='#E5E5E5', 
                        justify=LEFT,
                        anchor='w',
                        pady=10,
                        cursor='hand2'
						)
		if source['read'] == False:
			label.config(text='NEW: ' + text)
			label.config(fg= '#006400')

		label.bind('<Enter>', _hover)
		label.bind('<Leave>', _leave)
		labels.append(label)
		label.bind('<Button-1>', lambda event, source_num=source_num: _display_source(event, labels, data, source_num))
		label.grid(row=source_num, column=0, sticky='nsew')


	_set_mousewheel(canvas, lambda e, canvas=canvas: _on_mousewheel(e, canvas))



	return canvas


def _expand(data):
	if data['show_pdf'] == False:
		data['widgets']['pdf_frame'] = Frame(data['root'])
		data['widgets']['pdf_frame'].grid(row=2, column=4, sticky='nsew')
		data['widgets']['pdf_scroll'] = Scrollbar(data['widgets']['pdf_frame'], 
											orient="vertical"
											)
		data['widgets']['pdf_scroll'].grid(row=0, column=1, sticky='ns')
		data['widgets']['pdf_text'] = Text(data['widgets']['pdf_frame'], 
										yscrollcommand=data['widgets']['pdf_scroll'].set, 
										width=90, 
										bg='#F9F9F9', 
										font=('open sans', 10), 
										relief='flat'
										)
		data['widgets']['pdf_text'].grid(row=0, column=0, sticky='nsew')
		data['widgets']['pdf_scroll'].config(command=data['widgets']['pdf_text'].yview)
		data['widgets']['pdf_text'].configure(state="disabled")

		data['widgets']['pdf_frame'].columnconfigure(0, weight=3, minsize=100)
		data['widgets']['pdf_frame'].rowconfigure(0, weight=3, minsize=25)
		data['widgets']['pdf_label'].configure(text='Hide PDF')


		# Show PDF of current source
		_display_PDF(data)

		data['show_pdf'] = True

	else:
		data['widgets']['pdf_frame'].destroy()
		data['widgets']['pdf_label'].configure(text='Show PDF')


		data['widgets']['title_label'].grid(row=0, column=2, columnspan=2, sticky='nsew')
		data['widgets']['url_label'].grid(row=1, column=2, columnspan=2, sticky='nsew')

		data['show_pdf'] = False

	return data


def _create_source_display(root):

	# Create widgets
	text_widget = Text(root, bg='#F9F9F9', font=('open sans', 10), relief='flat')
	text_scroll = Scrollbar(root, orient='vertical', command=text_widget.yview)
	title_label = Label(root, text='Title', font=('open sans', 10), bg='#E5E5E5', wraplength=700) 
	url_label = Label(root, text='URL', font=('open sans', 10, 'italic'), fg='blue', bg='#E5E5E5', cursor='hand2',  wraplength=700)
	text_widget.configure(yscrollcommand=text_scroll.set)
	read_label = Label(root, text='Read label text initial', font=('open sans', 10), bg='#E5E5E5', wraplength=50) 

	# Grid widgets
	text_widget.grid(row=2, column=2, sticky='nsew')
	text_scroll.grid(row=2, column=3, sticky='ns')
	title_label.grid(row=0, column=2, columnspan=2, sticky='nsew')
	url_label.grid(row=1, column=2, columnspan=2, sticky='nsew')
	read_label.grid(row=1, column=4, columnspan=1, sticky='nsew')


	widgets = {
			   'title_label': title_label, 
			   'url_label': url_label, 
			   'text_widget': text_widget,
			   'pdf_text': '',
			   'read_label': read_label
		   	  }
	
	return widgets


def _display_PDF(data):

	source_num = data['click_stream'][-1]
	attachment = data['collection_data'][source_num]['attachment']

	if attachment == None:
		data['widgets']['title_label'].configure(cursor='arrow')
		data['widgets']['pdf_text'].configure(state="normal")
		data['widgets']['pdf_text'].delete('1.0', END)
		data['widgets']['pdf_text'].insert(END, 'PDF unavailable')
		data['widgets']['pdf_text'].configure(state="disabled")

	else:
		data['widgets']['title_label'].configure(cursor='hand2')
		data['widgets']['pdf_text'].configure(state="normal")
		data['widgets']['pdf_text'].delete('1.0', END)

		open_pdf = fitz.open(attachment)
		
		data['images'] = []
		
		for page in open_pdf:
			pix = page.get_pixmap()
			pix1 = fitz.Pixmap(pix, 0) if pix.alpha else pix
			img = pix1.tobytes("ppm")
			timg = PhotoImage(data=img)
			data['images'].append(timg)
		
		for i, img in enumerate(data['images']):
			data['widgets']['pdf_text'].image_create(END, image=img)
			data['widgets']['pdf_text'].insert(END, '\n\n')
		data['widgets']['pdf_text'].configure(state="disabled")

	return data


def _select_collection(dummy, selected, notes_data, data, canvas):

	# TASK add pop up warning for dummy[-1] == False

	if dummy[-1] == True:
		collection_name = selected.get().lower()
		data['root'].title("Research Reader: " + collection_name.title() + " Collection") 

		print(f'Change to {selected.get()} collection')
		_save_source(data)
		
		canvas.destroy()
		selected_collection = [source for source in notes_data if collection_name in source['collections']]
		selected_collection = sorted(selected_collection, key=lambda source: source['date_added'], reverse=True)
		selected_collection =sorted(selected_collection, key=lambda source: source['read'], reverse=False)
		data['collection_data']  = selected_collection
		_create_source_pane(data)

		# data['click_stream'].append(0) TASK could remove probably
		_display_source('setup', 'setup', data, 0) 

	else:
		return


def _main(notes_data, collection_name):
	'''Main function'''
	
	# Create Tkinter window
	root = Tk()
	root.title("Research Reader: " + collection_name.title() + " Collection") 
	root.geometry("1200x450")
	root.config(bg='#E5E5E5')
	root.iconbitmap(r"C:\Users\dlwal\Dropbox\research_projects\Scripts\research_reader.ico")

	# Select queried collection sources
	selected_collection = [source for source in notes_data if collection_name in source['collections']]
	selected_collection = sorted(selected_collection, key=lambda source: source['date_added'], reverse=True)
	selected_collection = sorted(selected_collection, key=lambda source: source['read'], reverse=False)


	# Create source display
	widgets = _create_source_display(root)

	# Initialize PDF view pane
	show_pdf = False
	pdf_label = Label(root, text='Show PDF', font=('open sans', 10), bg='#E5E5E5', wraplength=50)
	pdf_label.bind('<Button-1>', lambda e: _expand(data))
	pdf_label.grid(row=0, column=4, rowspan=1, sticky='nsew')
	widgets['pdf_label'] = pdf_label


	# Initialize click_stream
	click_stream = []

	# PDF images
	images=[]

	# Create data packet
	data = {
			'file_path': r"C:\Users\dlwal\Zotero\notes_app_data.json", # TASK: remove hardcoding
			'collection_data': selected_collection,
			'all_sources' : notes_data,
			'root': root,
			'widgets': widgets,
			'click_stream': click_stream,
			'images': images,
			'show_pdf': show_pdf,
			}

	# Create source pane
	canvas = _create_source_pane(data)

	# Display 1st source
	click_stream.append(0)
	_display_source('setup', 'setup', data, 0) 

	
	# Configure cols/rows
	root.rowconfigure(2, weight=3)
	root.rowconfigure(0, minsize=50)
	root.columnconfigure(2, weight=3, minsize=300)

	# Testing Thread
	dummy = [False]
	t1 = Thread(target=db.update_data, args=(notes_data, collection_name, dummy))
	t1.start()

	# Changing collections
	selected = StringVar()
	selected.set(collection_name.title())
	
	collections_names = set()
	for source in notes_data:
		for collection in source['collections']:
			collections_names.add(collection.title())

	collections_names = sorted(collections_names)
	collections_dropdown = OptionMenu(root, selected, *collections_names, command=lambda _: _select_collection(dummy, selected, notes_data, data, canvas))
	collections_dropdown.grid(row=0, column=0, columnspan=1, sticky='ew')

	# Run GUI
	root.bind('<Control-w>', lambda e: _on_closing(data))
	root.protocol("WM_DELETE_WINDOW", lambda: _on_closing(data))
	root.mainloop()

	t1.join()


if __name__ == '__main__':
    _main(sys.argv[1:])
