import sys
import os

from pdf import PDF
from glob import glob
import re
import time
import pandas as pd

from PyQt5.QtCore import QSize, Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QMainWindow, QFileDialog, 
	QProgressBar, QVBoxLayout, QWidget, QLabel)

class MuPDFScurrier(QThread):
	progress = pyqtSignal(int)
	current_pdf = pyqtSignal(str)
	finished = pyqtSignal(list)
	error = pyqtSignal(str)

	def __init__(self, settings, directory):
		super().__init__()
		self.directory = directory
		self.results = []

		self.use_image_ocr = settings[0]
		self.include_references = settings[1]
		self.no_links = settings[2]
		self.get_latex = settings[3]
		self.table_mode = settings[4]
		self.headtail_mode = settings[5]
		self.output_type = settings[6]

	def run(self):
		'''
		DOCSTRING HERE
		'''

		name = "data"
		folder = self.directory
		progress_percentage = 0

		file_paths = glob(folder)
		print(file_paths)

		start_time = time.time()
		t_info = []
		progress_percentage = 0
		completed = 0
		n = len(file_paths)

		f = open(name+".json", 'w', encoding='utf-8')

		# Open
		f.write('[\n')

		tot_end = ","
		print(f"Scraped {completed}/{n}", end='\r')
		for i in range(len(file_paths)):

			temp_start = time.time()
			if(i == len(file_paths) - 1):
				tot_end = ""

			# Get PDF Data
			data = self.pdf_scrape(file_paths[i])
			print(data["title"])
			self.current_pdf.emit(data["title"])

			# Begin PDF insertion
			f.write('\t{\n')

			# Title
			f.write(f'\t\t"title": "{data["title"]}",\n')

			# Text
			end = ","
			f.write('\t\t"text": [\n')
			for i in range(len(data["text"])):
				if i == len(data["text"]) - 1:
					end = "" # Last
				if data["text"][i] != "":
					f.write(f'\t\t\t"{data["text"][i]}"{end}\n')
				else:
					f.write(f'\t\t\tnull{end}\n')
			f.write('\t\t],\n')

			# Tables
			end = ","
			f.write(f'\t\t"tables": [\n')
			for i in range(len(data["tables"])):
				if i == len(data["tables"]) - 1:
					end = ""

				if len(data["tables"][i]) == 0 or data["tables"][i] == [""]:
					f.write(f'\t\t\tnull{end}\n')
				elif len(data["tables"][i]) == 1:
					f.write(f'\t\t\t"{data["tables"][i][0]}"{end}\n')
				else:
					f.write('\t\t\t[')
					collect = ''
					for j in range(len(data["tables"][i])):
						collect += f'"{data["tables"][i][j]}", '
					collect = collect[:-2] # Remove last ', '
					f.write(f'{collect}]{end}\n')
			f.write('\t\t],\n')

			# Images
			if(self.use_image_ocr == True): # If checkbox for Image Text Extraction is checked
				end = ","
				f.write('\t\t"images": [\n')
				for i in range(len(data["images"])):
					if i == len(data["images"]) - 1:
						end = ""

					#print(data["images"][i])
					if data["images"][i] == []:
						f.write(f'\t\t\tnull{end}\n')
					elif len(data["images"][i]) == 1:
						f.write(f'\t\t\t"{data["images"][i][0]}"{end}\n')
					else:
						f.write('\t\t\t[')
						collect = ''
						for j in range(len(data["images"][i])):
							if(data["images"][i][j] != ""):
								collect += f'"{data["images"][i][j]}", '
						collect = collect[:-2] # Remove last ', '
						f.write(f'{collect}]{end}\n')
				f.write('\t\t]\n')

			# End PDF Data
			f.write('\t}' + tot_end + '\n')
			completed += 1
			progress_percentage = (int)((completed / n) * 100)
			self.progress.emit(progress_percentage)

			temp_end = time.time()
			elapsed = round(temp_end-temp_start, 2)
			print(f"Scraped {completed}/{n}, t(s): {elapsed}", end='\r')
			t_info.append(elapsed)

		f.write(']')
		f.close()

		try:
			os.remove('./temp.jpeg')
		except:
			pass

		self.convert_output()
		self.progress.emit(100)
		self.finished.emit(self.results)


	def pdf_scrape(self, path):
		'''
		DOCSTRING HERE
		'''
		pdf = PDF(path)
		pages = len(pdf.mu_pdf)
		ocr_all = False # FOR OCR ALL MOMENTS

		text = []
		tables = []
		images = []

		for i in range(pages):
			pg_txt = pdf.raw_text(i, encode="utf-8")
			if ocr_all == True or (type(pg_txt) == str and pg_txt == "NULL"): # If PDF Page info is improperly stored
				print("ocr")
				#print("OCR Utilization")
				pg_txt = pdf.ocr_text(i) # OCR Read Page
				text.append(pdf.collapse_text(pg_txt))

				# Pass nothing
				tables.append([])
				images.append([])

			else:
				text.append(pdf.collapse_text(pg_txt))
				tables.append(pdf.collapse_tables(pdf.raw_tables(i)))

				if(self.use_image_ocr == True): # Get Images Check
					pg_img = []
					for txt in pdf.raw_images(i):
						pg_img.append(pdf.collapse_text(txt))
					images.append(pg_img)

		try:
			title = path[::-1].index('\\')
			title = path[len(path) - title:len(path) - 4]
		except:
			title = path[::-1].index('/')
			title = path[len(path) - title:len(path) - 4]

		# Headers
		if(self.headtail_mode == "Remove Both" or self.headtail_mode == "Keep Footers"):
			text = self.remove_nonword_leads(text)
			text = self.strip_headers(text)
			text = self.remove_nonword_leads(text)

		# Footers
		if(self.headtail_mode == "Remove Both" or self.headtail_mode == "Keep Headers"):
			text = self.strip_footers(text)
			text = self.remove_nonword_leads(text, flip=True)

		# In-Text
		text = self.remove_links(text)

		# Tables
		tables = self.remove_table_repeats(tables)

		data = {
		"text": text,
		"tables":tables,
		"images":images,
		"title": title,
		"pages": pages
		}

		return data

	def convert_output(self):
		if(self.output_type == ".json"):
			pass # Do nothing

		elif(self.output_type == ".csv"):
			df = pd.read_json('./data.json')
			df.to_csv('data.csv', index=False)
			os.remove('./data.json')



	def strip_headers(self, text):
		"""
		Finds repeating headers in text array and removes it from the text

		text: the text array

		returns: modified text array
		"""

		def header_info(text, first, alternate=True):
			'''
			DOCSTRING HERE
			'''
			if first >= len(text):
				return [[], ""]

			# To make header search easier
			text = text.copy()
			text = text[first:]

			for pg in range(len(text)):
				text[pg] = text[pg].replace(' ', '')

			str1 = ""
			string_idx = []
			for i in range(len(text)):
				if(alternate):
					if i % 2 == 0: string_idx.append(i) # Only alternating pages
				else:
					string_idx.append(i)

			# Get header repeats in text based off of first input
			str_col = []
			for pg in string_idx[1:]:
				if len(text[pg]) > 0 and len(text[0]) > 0:
					str1 = ""
					str_col.append("")
					idx = 0
					while str1 == str_col[-1] and idx < len(text[pg]) and idx < len(text[0]):
						if text[pg][idx].isdigit() or text[0][idx].isdigit():
							idx += 1
						else:
							str1 += text[0][idx]
							str_col[-1] += text[pg][idx]
							idx += 1

					# Remove last mismatching character
					str_col[-1] = str_col[-1][:-1]
					str1 = str1[:-1]

			highest = 0
			for i in range(len(str_col)): # Find most common header instance in text
				n = str_col.count(str_col[i])
				if n > highest:
					highest = n
					str1 = str_col[i]

			# Check if length is appropriate
			if len(str1) < 2:
				str1 = "" # If too short, then do not update anything

			for i in range(len(string_idx)): # Update string idx to have the correct indices to update
				string_idx[i] += first

			return [string_idx, str1]
			# END OF HEADER_INFO


		if(len(text) > 3):
			# Even and Odd page numbers
			for i in range(4):
				occurs, string = header_info(text, i)
				if(len(string) > 0):
					for p in occurs:
						idx = 0
						t_str = ""
						matches = True
						while matches and idx < len(string):
							if text[p][0].isdigit() or text[p][0] == ' ':
								text[p] = text[p].replace(text[p][0], '', 1) # Don't update idx, removes numbers & spaces
							elif text[p][0] == string[idx]:
								t_str += text[p][0]
								idx += 1

								# Update string
								text[p] = text[p].replace(text[p][0], '', 1)
							else:
								matches = False # If no conditions can be met, it does not match
		else:
			occurs, string = header_info(text, 0, False)
			print(occurs)
			if(len(string) > 0):
				for p in occurs:
					if(len(text[p]) < len(string)): continue
					idx = 0
					t_str = ""
					while(idx < len(string)):
						if(text[p][idx].isdigit() or text[p][idx] == ' '):
							text[p] = text[p].replace(text[p][idx], '', 1)
						elif(text[p][idx] == string[idx]):
							t_str += text[p][0]
							idx += 1

					text[p] = text[p].replace(string, '', 1)

		return text

	def strip_footers(self, text):
		# Flip Text
		for i in range(len(text)):
			text[i] = text[i][::-1]

		# Removes Footers due to Flipped State
		text = self.strip_headers(text)

		# Flip back to original
		for i in range(len(text)):
			text[i] = text[i][::-1]

		return text

	def remove_nonword_leads(self, text, flip=False):
		"""
		Removes all numbers or non-alphabet characters at beginning of each string in text array

		string: given text array to modify

		returns: modified text array
		"""
		if flip == True: # Flips each string to be backwards for end-of-string removals
			for i in range(len(text)):
				text[i] = text[i][::-1]

		# Remove characters
		for i in range(len(text)):
			try:
				while text[i][0].isdigit() or text[i][0] == ' ' or text[i][0].isalnum() == False:
					text[i] = text[i][1:]
			except: pass

		# Reflip each string to be readable again
		if flip == True:
			for i in range(len(text)):
				text[i] = text[i][::-1]

		return text

	def remove_links(self, text):
		"""
		Removes any found links within each string in text array

		text: given text array

		returns: modified text array
		"""
		for i in range(len(text)):
			split = text[i].split(" ")
			mark_del = []
			for j in range(len(split)):
				if '//' in split[j]:
					if split[j].index('//') + 2 == len(split[j]) and j+1 < len(split): # Check if link was cut by a space (ends on //)
						mark_del.append(split[j])
						mark_del.append(split[j+1])
					else:
						mark_del.append(split[j])
				elif '​' in split[j]: # Space character only found in links
					mark_del.append(split[j])

			# Remove
			for item in mark_del:
				if item in split:
					split.remove(item)

			text[i] = " ".join(split)

		return text

	def remove_table_repeats(self, tables):
		"""
		Attempts to remove any unnecessary repeating elements from given table array

		tables: given array of table information on each page

		returns: new table array
		"""

		# Check if table fix is necessary
		empty = 0
		for t in tables:
			if len(t) == 0 or t == [""]:
				empty += 1

		if len(tables) - empty <= 2:
			return tables # No modifications needed

		def table_info(tables, first):
			str1 = ""
			str2 = ""
			occurs = []
			idx = 0
			for t in tables[first:]:
				if str1 == "":
					if len(t) == 0 or t == [""]:
						str1 == "" # Table here empty, move to next
					else:
						if type(t) == str:
							str1 = re.sub('[^a-zA-Z]+', '', t)
						elif type(t) == list:
							str1 = t[0]
							for i in range(len(t)): # Find shortest string in list
								if len(t[i]) < len(str1):
									str1 = t[i]
							str1 = re.sub('[^a-zA-Z]+', '', str1)
						occurs.append(idx)
				else:
					if len(t) == 0 or t == [""]:
						str2 == "" # Table here empty, move to next
					else:
						if type(t) == str:
							str2 = re.sub('[^a-zA-Z]+', '', t)
						elif type(t) == list:
							str2 = t[0]
							for i in range(len(t)): # Find shortest string in list
								if len(t[i]) < len(str2):
									str2 = t[i]
							str2 = re.sub('[^a-zA-Z]+', '', str2)

						if(str1.lower() == str2.lower()):
							occurs.append(idx)
				idx += 1

			return [occurs, str1]

		for i in range(2): # Run for first and second indexes
			occurs, repeat = table_info(tables, i)
			if len(occurs) > 1:
				break

		if len(occurs) <= 1:
			return tables # No modifications

		for idx in occurs:
			if type(tables[idx]) == str:
				tables[idx] = [""]
			elif type(tables[idx]) == list:
				temp = tables[idx].copy()
				for i in range(len(temp)):
					temp[i] = re.sub('[^a-zA-Z]+', '', temp[i]).lower()
				try:
					elem_idx = temp.index(repeat.lower())

					tables[idx].pop(elem_idx)
				except: pass

		return tables
