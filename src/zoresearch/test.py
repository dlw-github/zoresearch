import pdfkit
import os

html = r"C:\Users\dlwal\Zotero\storage\8634HXQH\0.0.2.html"
pdf_path=r"C:\Users\dlwal\Zotero\storage\8634HXQH\better_name_8.pdf"

try:
	if os.path.exists(r"C:\Program Files\wkhtmltopdf\bwin\wkhtmltopdf.exe"):
		print('config option')
		config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
		attachment = pdfkit.from_file(html, pdf_path, verbose=False, configuration=config, options=(
					{
					'disable-javascript': True
					, 'load-error-handling': 'skip'
					}
				)
			)
	else:
		print('no config')
		attachment = pdfkit.from_file(html, pdf_path, verbose=False, options=(
					{
					'disable-javascript': True
					, 'load-error-handling': 'skip'
					}
				)
			)
except OSError as error:
	print('HEREEE')
	# print(error)

if os.path.exists(pdf_path):
	print('created something')

