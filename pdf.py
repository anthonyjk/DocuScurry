import pymupdf
import re
from PIL import Image
from io import BytesIO
import pytesseract
import enchant

class PDF:
	def __init__(self, path):
		self.mu_pdf = pymupdf.open(path)

		self.removable = ""

	# TEXT SCRAPING
	def raw_text(self, index, encode="utf-8"):
		text = self.mu_pdf[index].get_text()
		broken_page = '\x00' in text

		if broken_page:
			return 'NULL'

		else:
			text = text.encode(encode, errors="replace")

			return text

	def collapse_text(self, text):
		# Decode bytes string
		if type(text) == bytes:
			text = text.decode("utf-8")

		# Error Fixing "?"
		# Replace w PyEnchant
		# Codecs for custom error replacement

		# Replace " to avoid format issues
		text = text.replace('"', "'")

		# Remove sequence characters
		sequences = ['\n', '\t', '\\n', '\\t', '\\', '\r', '\\r', ' ']
		for s in sequences:
			text = text.replace(s, ' ')

		# Fix format issues from pymupdf
		text = text.replace('- ', '')
		text = text.replace('  ', ' ')

		# Fix false read errors
		text = text.replace('ﬁ', 'fi')
		text = text.replace('ﬀ', 'ff')
		text = text.replace('ﬃ', 'ffi')
		text = text.replace('ﬂ', 'fl')

		return text

	# TABLE SCRAPING
	def raw_tables(self, index):
		tabs = self.mu_pdf[index].find_tables()

		tables = []
		for i in range(len(tabs.tables)):
			tables.append(tabs[i].extract())
		return tables

	def collapse_tables(self, table_array):
		new_array = []
		for i in range(len(table_array)):
			str_table = ""
			for row in table_array[i]:
				for item in row:
					try:
						str_table += item + ' '
					except: pass
				try:
					str_table = str_table[:-1] + ', '
					str_table = str_table.replace('\n', ' ')
				except: pass

			if bool(re.search(r'\w', str_table)) == False: # If there are no alphanumeric characters (Empty Table)
				str_table = ""

			if self.removable != "" and self.removable in re.sub('[^0-9a-zA-Z]+', '', str_table.replace(" ", "")):
				str_table = ""

			# Replace quotation type
			str_table = str_table.replace('"', "'")

			new_array.append(str_table)

		return new_array

	# IMAGE SCRAPING
	def raw_images(self, index):
		img_text = []
		page = self.mu_pdf.load_page(index)
		for img in page.get_images(full=True):
			xref = img[0]
			image = self.mu_pdf.extract_image(xref)
			image_bytes = image["image"]

			try:
				image = Image.open(BytesIO(image_bytes))
				image.save("temp.jpeg")

				img_text.append(pytesseract.image_to_string("temp.jpeg"))
			except: pass

		return img_text

	# OCR SCRAPE
	def ocr_text(self, index):
		#print("OCR")
		z_factor = 2.0 # Zoom scale
		# Larger z_factor means more accurate OCR reading,
		#		However it also means longer jpeg download time.
		z_matrix = pymupdf.Matrix(z_factor, z_factor)

		page_image = self.mu_pdf[index].get_pixmap(matrix=z_matrix)
		page_image.save("temp_page.jpeg")

		page_text = pytesseract.image_to_string("temp_page.jpeg")
		return page_text
