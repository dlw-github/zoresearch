from tkinter import *
from tkinter import Tk, font
import sources_db
import webbrowser
import fitz
import json
import time


class Note_gui:
	def __init__(self, app_data, collection_name, app_data_location):
		
		# Create Tkinter window
		self.root = Tk()
		self.root.title("Research Reader: " + collection_name.title() + " Collection") 
		self.root.geometry("1200x450")
		self.root.config(bg='#E5E5E5')
		self.root.iconbitmap(r"C:\Users\dlwal\Dropbox\researcher\icons\researcher.ico")

		# Initialize metadata
		self.app_data_location = app_data_location
		self.app_data = app_data
		self.collection_name = collection_name
		self.show_pdf = False

		# Initialize collection dropdown
		self.collection_names = sorted(set(collection.title() for source in self.app_data for collection in source.collections))
		self.dropdown_selection = StringVar()
		self.dropdown_selection.set(self.collection_name.title())

		# Initialize source type dropdown
		self.source_types = ['All', 'Starred', 'Unread']
		self.source_type_dropdown_selection = StringVar()
		self.source_type_dropdown_selection.set('All')

		# Create main display and widgets
		self._main_display()
		for source in self.app_data:
			source._create_label(self.frame)

		# Display queried collection
		self._display_collection()

		# Display first source in collection
		self.selected_source = self.selected_collection[0]
		self._display_source(self.selected_source)

		# Configure GUI
		# self.root.rowconfigure(0, minsize=50)
		self.root.rowconfigure(3, weight=3)
		self.root.columnconfigure(2, weight=0, minsize=50)
		self.root.columnconfigure(3, weight=0, minsize=50)
		self.root.columnconfigure(4, weight=3, minsize=200)


		# Run GUI
		self.root.bind('<Control-w>', lambda e: self._on_closing())
		self.root.protocol("WM_DELETE_WINDOW", lambda: self._on_closing())
		self.root.mainloop()


	def _on_closing(self):
		print('Clicked close')
		self._save_source()
		self._save_data()
		self.root.destroy()


	def _save_source(self):
		self.selected_source.all_notes = self.text_widget.get("1.0",END)


	def _save_data(self):
		data = [vars(source) for source in self.app_data]
		with open(self.app_data_location, 'w') as f:
			json.dump(data, f, indent=4, default=str)
		print("Saved project file")


	def _on_frame_configure(self):
		'''Reset the scroll region to encompass the inner frame'''
		self.canvas.configure(scrollregion=self.canvas.bbox("all"))


	def _on_mousewheel(self, event):
		change = int(-1*(event.delta/120))
		self.canvas.yview_scroll(change, "units")


	def _set_mousewheel(self, command):
	    """Activate / deactivate mousewheel scrolling when 
	    cursor is over / not over the widget respectively."""
	    self.canvas.bind("<Enter>", lambda _: self.canvas.bind_all('<MouseWheel>', command))
	    self.canvas.bind("<Leave>", lambda _: self.canvas.unbind_all('<MouseWheel>'))


	def _open_link(self, dest):
		if dest == '':
			return
		else:
			webbrowser.open_new(dest)	


	def _mark_unread(self, e):

		# Change read status of selected source
		self.selected_source.read = False

		# Change source label
		self.selected_source.label.configure(font=('open sans', 10, 'bold'))


		# Recenter scroll bar on selected source
		# source_position = float((self.selected_collection.index(self.selected_source)) / (len(self.selected_collection)))
		# self.canvas.yview_moveto(source_position)


	def _star_source(self, e):
		self.selected_source.starred = not self.selected_source.starred

		# Starred source
		if self.selected_source.starred == True:
			text = u'\u2605 ' + self.selected_source.label.cget('text')
			self.selected_source.label.configure(text=text)
			self.star_label.config(text = u'\u2605')

		# Unstarred source
		else:
			# Change source label
			self.star_label.config(text = u'\u2606')
			text = self.selected_source.label.cget('text')[2:]
			self.selected_source.label.configure(text=text)



	def _select_collection(self):
		self.collection_name = self.dropdown_selection.get().lower()
		print(f'Change to {self.collection_name.title()} collection')

		self.root.title("Research Reader: " + self.collection_name.title() + " Collection") 
		self._save_source()
		self.text_widget.delete('1.0', END)

		# Display queried collection
		self._display_collection()

		# Display first source in collection
		self.selected_source = self.selected_collection[0]
		self._display_source(self.selected_source)


	def _select_source_type(self):
		source_type = self.source_type_dropdown_selection.get().lower()
		print(source_type)
		self._save_source()
		self.text_widget.delete('1.0', END)

		
		self._display_collection(source_type)
		self.selected_source = self.selected_collection[0]
		self._display_source(self.selected_source)


	def _main_display(self):

		# Create widgets
		self.canvas = Canvas(self.root, background="#E5E5E5", width=220) 
		self.frame = Frame(self.canvas, background='#E5E5E5')
		self.text_widget = Text(self.root, bg='#F9F9F9', font=('open sans', 10), relief='flat')
		self.collections_dropdown = OptionMenu(self.root, self.dropdown_selection, *self.collection_names, command = lambda _: self._select_collection())

		self.source_label = Label(self.root, text='Sources', font=('open sans', 10), bg='#E5E5E5', padx=0)
		self.title_label = Label(self.root, text='Title', font=('open sans', 10), bg='#E5E5E5', wraplength=700) 
		self.url_label = Label(self.root, text='URL', font=('open sans', 10, 'italic'), fg='blue', bg='#E5E5E5', cursor='hand2',  wraplength=700)
		self.read_label = Label(self.root, text='', font=('open sans', 10), bg='#E5E5E5', wraplength=50) 
		self.pdf_label = Label(self.root, text='Show PDF', font=('open sans', 10), bg='#E5E5E5', wraplength=50)

		self.text_scroll = Scrollbar(self.root, orient='vertical', command=self.text_widget.yview)
		self.source_scroll = Scrollbar(self.root, orient="vertical", command=self.canvas.yview)

		self.pdf_frame = Frame(self.root)
		self.pdf_scroll = Scrollbar(self.pdf_frame, orient='vertical')
		self.pdf_text = Text(self.pdf_frame, yscrollcommand=self.pdf_scroll.set, width=90, bg='#F9F9F9', font=('open sans', 10), relief='flat')

		self.star_label = Label(self.root, text = u'\u2606', font=('open sans', 10), bg='#E5E5E5', padx=0)
		self.source_type_label = OptionMenu(self.root, self.source_type_dropdown_selection, *self.source_types, command = lambda _: self._select_source_type())

		# Configure widgets
		self.canvas.create_window((0,0), window=self.frame, anchor="nw")
		self.canvas.configure(yscrollcommand=self.source_scroll.set)
		self.frame.bind("<Configure>", lambda event: self._on_frame_configure())
		self._set_mousewheel(lambda event: self._on_mousewheel(event))
		self.text_widget.configure(yscrollcommand=self.text_scroll.set)
		self.pdf_label.bind('<Button-1>', lambda event: self._expand())

		self.pdf_frame.columnconfigure(0, weight=3, minsize=100)
		self.pdf_frame.rowconfigure(0, weight=3, minsize=25)
		self.pdf_scroll.config(command=self.pdf_text.yview)
		self.pdf_text.configure(state="disabled")
		
		# Grid widgets
		self.collections_dropdown.grid(row=0, column=0, columnspan=2, sticky='ew')
		self.title_label.grid(row=0, column=2, columnspan=3, sticky='ew')
		
		self.source_type_label.grid(row=1, column=0, columnspan=2, sticky='ew')
		self.url_label.grid(row=1, column=2, columnspan=3, sticky='ew')
		
		self.source_label.grid(row=2, column=0, rowspan=1, columnspan=1, sticky='ew')
		self.star_label.grid(row=2, column=2, sticky='ew', pady=20)
		self.read_label.grid(row=2, column=3, columnspan=1, sticky='ew', pady=20)
		self.pdf_label.grid(row=2, column=4, rowspan=1, sticky='w', pady=20)

		self.canvas.grid(row=3, column=0, sticky='nsew')
		self.source_scroll.grid(row=3, column=1, sticky='ns')
		self.text_widget.grid(row=3, column=2, columnspan=3, sticky='nsew')
		self.text_scroll.grid(row=3, column=5, sticky='ns')



	def _display_collection(self, source_type='all'):

		# Ungrid current sources (if any)
		for source in self.frame.grid_slaves():
			source.grid_forget()

		# Grid new source labels
		self.selected_collection = sources_db._select_collection(self.app_data, self.collection_name, source_type)

		for i, source in enumerate(self.selected_collection):
			print(f'[{i+1}/{len(self.selected_collection)}] {source.title}')
			# source._create_label(self.frame)
			print()
			source.label.grid(row=i, column=0, sticky='nsew')
			source.label.bind('<Button-1>', lambda event, source=source: self._display_source(source))


	def _display_source(self, source):

		# Save data from previously selected source
		if self.text_widget.get("1.0",END).strip():
			self._save_source()
		
		# Reset formatting of source label widgets
		for tile in self.selected_collection:
			tile.label.config(background='#E5E5E5', relief='flat', fg='black')
			
			if not tile.read:
				tile.label.config(font=('open sans', 10, 'bold'))
			else:
				tile.label.config(font=('open sans', 10))

			tile.label.bind('<Enter>', _hover)
			tile.label.bind('<Leave>', _leave)

		# Highlight selected source widget
		self.selected_source = source
		source.read = True
		source.label.unbind('<Enter>')
		source.label.unbind('<Leave>')
		source.label.config(background='#32ade6', fg='white', font=('open sans', 10))

		# Change GUI labels to match selected source
		self.title_label.config(text=source.title)
		self.title_label.bind("<Button-1>", lambda e: self._open_link(source.attachment))

		self.url_label.config(text=source.url)
		self.url_label.bind("<Button-1>", lambda e: self._open_link(source.url))

		self.text_widget.delete('1.0', END)
		self.text_widget.insert('end', source.all_notes.strip())
		self.text_widget.config(font=('open sans', 10))

		self.read_label.config(text="Mark 'Unread'")
		self.read_label.bind("<Button-1>", self._mark_unread)

		if source.starred:
			self.star_label.config(text = u'\u2605')
		else:
			self.star_label.config(text = u'\u2606')
		self.star_label.bind("<Button-1>", self._star_source)

		if self.show_pdf == True:
			self._display_PDF()

	def _display_PDF(self):
		source = self.selected_source

		if source.attachment == None:
			self.title_label.configure(cursor='arrow')
			self.pdf_text.configure(state="normal")
			self.pdf_text.delete('1.0', END)
			self.pdf_text.insert(END, 'PDF unavailable')
			self.pdf_text.configure(state="disabled")

		else:
			self.title_label.configure(cursor='hand2')
			self.pdf_text.configure(state="normal")
			self.pdf_text.delete('1.0', END)

			open_pdf = fitz.open(source.attachment)
			
			self.images = []
			
			for page in open_pdf:
				pix = page.get_pixmap()
				pix1 = fitz.Pixmap(pix, 0) if pix.alpha else pix
				img = pix1.tobytes("ppm")
				timg = PhotoImage(data=img)
				self.images.append(timg)
			
			for i, img in enumerate(self.images):
				self.pdf_text.image_create(END, image=img)
				self.pdf_text.insert(END, '\n\n')

			self.pdf_text.configure(state="disabled")


	def _expand(self):
		self.show_pdf = not self.show_pdf

		# To display PDF pane
		if self.show_pdf == True:
			self.pdf_label.configure(text='Hide PDF')

			# Configure and grid widgets
			self.pdf_frame.grid(row=3, column=6, sticky='nsew')	
			# self.pdf_frame.columnconfigure(1, minsize=1000)
			self.pdf_text.grid(row=0, column=0, sticky='nsew')			
			self.pdf_scroll.grid(row=0, column=1, sticky='ns')

			# Display PDF
			self._display_PDF()

		# To remove pdf pane
		else:
			self.pdf_label.configure(text='Show PDF')
			self.pdf_frame.grid_forget()

			# self.title_label.grid(row=0, column=2, columnspan=2, sticky='nsew')
			# self.url_label.grid(row=1, column=2, columnspan=2, sticky='nsew')
	

def _hover(event):
	'''Check widget foreground and change only if not green'''
	current_fg = event.widget.cget("fg")
	# print(f'Foreground color: {current_fg}')

	event.widget.config(background='#32ade6')
	if current_fg != '#006400':
		event.widget.config(foreground='white')


def _leave(event):
	current_fg = event.widget.cget("fg")
	event.widget.config(background='#E5E5E5')
	if current_fg != '#006400':
		event.widget.config(foreground='black')


def _main(app_data, collection_name, app_data_location):


	# Create GUI object
	gui = Note_gui(app_data, collection_name, app_data_location)
