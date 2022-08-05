import fitz
import sys
import os
import pdfkit
import fitz
import tkinter as tk

import zoresearcher.gui

class Source:
	def __init__(self, metadata):

		# Set initial values
		self.title= ''
		self.short_title = ''
		self.url = ''
		self.attachment = ''
		self.date_added = ''
		self.collections = []
		self.annots = []
		self.all_notes = ''
		self.read = False
		self.starred = False

		# Add any passed data as attributes
		for key in metadata:
		 	setattr(self, key, metadata[key])


	def _describe(self):
		print(f'SOURCE DESCRIPTION\nTitle: {self.title}\nKey: {self.key}\nURL: {self.url}\nAll notes: {self.all_notes}')


	def _create_label(self, frame):
		
		if self.short_title is not None:
			text = self.short_title

		elif self.title is not None:
			text = self.title

		else:
			text = 'Title unavailable'

		if self.starred:
			text =u'\u2605 ' +  text

		if len(text) > 80:
			text = text[ :80] + '...'

		self.label = tk.Label(
						frame, 
						text=text,
						width=30,
						font=('open sans',10),
                        wraplength=200, 
                        bg='#E5E5E5', 
                        justify=tk.LEFT,
                        anchor='w',
                        pady=10,
                        cursor='hand2'
						)
		if self.read == False:
			self.label.config(font=('open sans', 10, 'bold'))

		self.label.bind('<Enter>', zoresearcher.gui._hover)
		self.label.bind('<Leave>', zoresearcher.gui._leave)
		

	def _html_to_pdf(self, html):
		# print('\t\tConverting HTML file to PDF: {}'.format(html))
		html = self.attachment + html
		pdf_path = html[ : -4] + 'pdf'
		try:
			self.attachment = pdfkit.from_file(html, pdf_path, verbose=False, options=(
					{
					'disable-javascript': True
					, 'load-error-handling': 'ignore'
					}
				)
			)
		
		except OSError:
			# print('\t\t\tWKHTML is complaining')
			pass
		
		self.attachment = pdf_path
		return


	def _get_attachment(self):
		# print('\t\tInitial attachment value: {}'.format(self.attachment))

		# Return if PDF is already located or if no attachment exists
		if self.attachment is None:
			return

		if self.attachment.endswith('.pdf'):
			# print('\t\tPDF already exists or no attachment: {}'.format(self.attachment))
			return

		# Otherwise, attachment points to directory. Convert HTML to PDF if needed
		else:
			# print('\t\t\tSearching for file in folder {}'.format(self.attachment))
			try:
				directory = os.listdir(self.attachment)
				pdf = [match for match in directory if '.pdf' in match]
				if pdf:
					# print('\t\tPDF found in source folder: {}'.format(pdf[0]))
					self.attachment = self.attachment + pdf[0]
					return

				else:
					html = [match for match in directory if '.html' in match]
					if html:
						self.attachment = self._html_to_pdf(html[0])
						return
					else:
						# print('\t\tNo attachment found in folder; return none')
						self.attachment = None
						return
			
			except FileNotFoundError:
				return


	def _check_contain(self, rect_annot, rect_reference, threshold=0.75):
	    '''Check if word rectangle overlaps with annotation rectangle'''
	    x_a1, y_a1, x_a2, y_a2 = rect_annot
	    x_b1, y_b1, x_b2, y_b2 = rect_reference

	    if x_a1 >= x_b2 or x_b1 >= x_a2:
	        return False
	    elif y_a1 >= y_b2 or y_b1 >= y_a2:
	        return False
	    else:
	        b_area = (y_b2 - y_b1) * (x_b2 - x_b1)
	        overlap_area = (
	                        (min(y_a2, y_b2) - max(y_a1, y_b1))
	                        * (min(x_a2, x_b2) - max(x_a1, x_b1))
	                       )
	        return (overlap_area / b_area) > threshold


	def _iterate_words(self, page):
	    '''Iterate through all words in a page and return word'''
	    for wb in sorted(page.get_text('words'), key=lambda w: (w[1], w[0])):
	        yield(wb)


	def _get_highlight_text(self, annot):
	    '''Get highlighted text'''
	    annot_text_raw = ''
	    rect_counts = len(annot.vertices) // 4
	    for i in range(rect_counts):
	        for word in self._iterate_words(annot.parent):
	            if self._check_contain(
	                              annot.vertices[i * 4]
	                              + annot.vertices[(i * 4) + 3],
	                              word[:4],
	                             ):
	                annot_text_raw = annot_text_raw + ' ' + word[4]
	    return annot_text_raw



	def _create_annot(self, annot):
	    '''Create annot entry in source_entry dict
	       for sticky comments and highlights
	    '''
	    # Get text from sticky comment
	    if(annot.type[0] == 0):
	        annot_text_raw = annot.info['content']

	    # Get text from highlight
	    elif(annot.type[0] == 8):
	        annot_text_raw = self._get_highlight_text(annot)

	    else:
	        annot_text_raw = 'None'

	    # Create annot entry
	    annot_text = ('PAGE '
	                  + str(annot.parent.number + 1)
	                  + ' ('
	                  + annot.type[1]
	                  + '): '
	                  + annot_text_raw
	                  )
	    annot_entry = {
	                       'page': annot.parent.number + 1,
	                       'type': annot.type[1],
	                       'text': annot_text
	                       }

	    # Append annot entry if not already present
	    if annot_entry not in self.annots:
	        self.annots.append(annot_entry)
	        self.all_notes += '\n\n' + annot_text 
	        # print('\t\t\tAnnot added to dictionary')
	    else:
	        # print('\t\t\tAnnot already in dictionary')
	        pass



	def _get_annots(self):

	    if self.attachment == None:
	        return
	    try:
	        file_path = os.path.normpath(self.attachment)
	        doc = fitz.open(file_path)
	        # print('\t\tExtracting annotations')

	        for page in doc.pages():
	            for annot in page.annots():
	                self._create_annot(annot)
	        return
	   
	    except RuntimeError:
	        # print('\t\tUnable to extract annotations')
	        self.attachment = None 
	        return