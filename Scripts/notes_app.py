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


def _save_source(data):
	source_to_save_num = data['click_stream'][-1]
	data['project_data'][source_to_save_num]['all_notes']  = data['widgets']['text_widget'].get("1.0",END)
	return data


def _open_link(dest):
	if dest == '':
		return
	else:
		webbrowser.open_new(dest)


def _display_source(event, labels, data, source_num):

	if event !='setup':
		for label in labels:
			label.config(background='#E5E5E5')
			label.config(relief='flat')
			label.config(foreground='black')
			label.bind('<Leave>', leave)
			event.widget.config(background='#32ade6', foreground='white')   
			event.widget.unbind('<Leave>')
		data = _save_source(data)

	title_label = data['widgets']['title_label']
	url_label = data['widgets']['url_label']
	text_widget = data['widgets']['text_widget']
	text_widget.delete('1.0', END)

	title_text = data['project_data'][source_num]['title']
	url_text = data['project_data'][source_num]['url']
	text_text = data['project_data'][source_num]['all_notes']
	loc_text = data['project_data'][source_num]['file_loc']

	title_label.config(text=title_text)
	title_label.bind("<Button-1>", lambda e: _open_link(loc_text))

	url_label.config(text=url_text)
	url_label.bind("<Double-Button-1>", lambda e: _open_link(url_text))

	text_widget.insert('end', text_text)
	text_widget.config(font=('open sans', 10))

	data['click_stream'].append(source_num)

	if data['show_pdf'] == True:
		_display_PDF(data)

	return data

def onFrameConfigure(canvas):
    '''Reset the scroll region to encompass the inner frame'''
    canvas.configure(scrollregion=canvas.bbox("all"))


def hover(event):
    event.widget.config(background='#32ade6', foreground='white')


def leave(event):
    event.widget.config(background='#E5E5E5')
    event.widget.config(foreground='black')


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
	frame.bind("<Configure>", lambda event, canvas=canvas: onFrameConfigure(canvas))

	# Grid widgets
	canvas.grid(row=2, column=0, sticky='nsew', padx=0)
	source_scroll.grid(row=2, column=1, sticky='ns')
	source_label.grid(row=0, column=0, rowspan=2, columnspan=2, sticky='nsew')

	labels=[]

	for source_num, source in enumerate(data['project_data']):

		if source['short_title'] != 'None':
			text = source['short_title']
		else:
			text = source['title']

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
		label.bind('<Enter>', hover)
		label.bind('<Leave>', leave)
		labels.append(label)
		label.bind('<Button-1>', lambda event, source_num=source_num: _display_source(event, labels, data, source_num))
		label.grid(row=source_num, column=0, sticky='nsew')


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

	# Grid widgets
	text_widget.grid(row=2, column=2, sticky='nsew')
	text_scroll.grid(row=2, column=3, sticky='ns')
	title_label.grid(row=0, column=2, columnspan=2, sticky='nsew')
	url_label.grid(row=1, column=2, columnspan=2, sticky='nsew')

	widgets = {
			   'title_label': title_label, 
			   'url_label': url_label, 
			   'text_widget': text_widget,
			   'pdf_text': ''
		   	  }
	return widgets


def _get_data(file_path):
	'''Return data from project JSON'''
	with open(file_path, 'r') as f:
		project_data = json.loads(f.read())
		return project_data

def _save_data(data):
	with open(data['file_path'], 'w') as f:
		json.dump(data['project_data'], f, indent=4)
	print("Saved project file")

def _on_closing(data):
	print('Clicked close')
	_save_source(data)
	_save_data(data)
	data['root'].destroy()


def _display_PDF(data):

	source_num = data['click_stream'][-1]
	file_loc = data['project_data'][source_num]['file_loc']

	if file_loc == None:
		data['widgets']['title_label'].configure(cursor='arrow')
		data['widgets']['pdf_text'].configure(state="normal")
		data['widgets']['pdf_text'].delete('1.0', END)
		data['widgets']['pdf_text'].insert(END, 'PDF unavailable')
		data['widgets']['pdf_text'].configure(state="disabled")

	else:
		data['widgets']['title_label'].configure(cursor='hand2')
		data['widgets']['pdf_text'].configure(state="normal")
		data['widgets']['pdf_text'].delete('1.0', END)

		open_pdf = fitz.open(file_loc)
		
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


def _main(file_path):
	'''Main function'''
	
	# Create Tkinter window
	root = Tk()
	root.title("Notes App") 
	root.geometry("1200x450")
	root.config(bg='#E5E5E5')
	root.iconbitmap("C:\\Users\\dlwal\\Downloads\\moose-icons-noun-project-62605.ico")

	# Get project data from project file JSON
	project_data = _get_data(file_path)

	# Create source display
	widgets = _create_source_display(root)

	# Initialize PDF view pane
	show_pdf = False
	pdf_label = Label(root, text='Show PDF', font=('open sans', 10), bg='#E5E5E5', wraplength=50)
	pdf_label.bind('<Button-1>', lambda e: _expand(data))
	pdf_label.grid(row=0, column=4, rowspan=2, sticky='nsew')
	widgets['pdf_label'] = pdf_label


	# Initialize click_stream
	click_stream = []

	# PDF images
	images=[]

	# Create data packet
	data = {
			'file_path': file_path,
			'project_data': project_data,
			'root': root,
			'widgets': widgets,
			'click_stream': click_stream,
			'images': images,
			'show_pdf': show_pdf,
			}

	# Create source pane
	_create_source_pane(data)

	# Display 1st source
	click_stream.append(0)
	_display_source('setup', 'setup', data, 0) 

	
	# Configure cols/rows
	root.rowconfigure(2, weight=3)
	root.rowconfigure(0, minsize=50)
	root.columnconfigure(2, weight=3, minsize=300)
	

	# Run GUI
	root.protocol("WM_DELETE_WINDOW", lambda: _on_closing(data))
	root.mainloop()

if __name__ == '__main__':
    _main(sys.argv[1])
