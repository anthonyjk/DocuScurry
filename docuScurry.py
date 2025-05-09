import sys
import os

#from dataScurrier import MuPDFScurrier

from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import QSize, Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QMainWindow, QFileDialog, 
	QProgressBar, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QSizePolicy, QStackedWidget, 
	QCheckBox, QComboBox)

class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()

		self.setWindowTitle("DocuScurry")
		self.setFixedSize(QSize(400, 220))

		self.stacked_widget = QStackedWidget()
		self.main_window = QWidget()
		self.scrape_window = QWidget()
		self.viewer_window = QWidget()

		self.stacked_widget.addWidget(self.main_window)
		self.stacked_widget.addWidget(self.scrape_window)
		self.stacked_widget.addWidget(self.viewer_window)

		self.initMainUI()
		self.initScraperUI()

		self.setCentralWidget(self.stacked_widget)
		self.stacked_widget.setCurrentIndex(0)

	def initMainUI(self):
		vbox = QVBoxLayout(self.main_window)

		# Buttons
		scrape_button = QPushButton("Scraper")
		scrape_button.setFixedSize(180,65)
		scrape_button.clicked.connect(self.switchScrape)

		viewer_button = QPushButton("Viewer")
		viewer_button.setFixedSize(180,65)
		#self.viewer_button.clicked.connect(self.file_scrape)

		pixmap = QPixmap("./cerl_sqrl.png")
		scaled_pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
		sqrl_label = QLabel()
		sqrl_label.setPixmap(scaled_pixmap)

		title_font = QFont()
		title_font.setPointSize(20)
		ds_title = QLabel("DocuScurry")
		ds_title.setFont(title_font)

		vbox.setSpacing(10)
		vbox.setContentsMargins(10, 10, 10, 10)
		vbox.addWidget(ds_title, 0, Qt.AlignCenter)

		smaller_vbox = QVBoxLayout()
		smaller_vbox.setContentsMargins(10, 10, 10, 10)
		smaller_vbox.addWidget(scrape_button, 0, Qt.AlignLeft | Qt.AlignCenter)
		smaller_vbox.addWidget(viewer_button, 0, Qt.AlignLeft | Qt.AlignCenter)

		hbox = QHBoxLayout()
		#hbox.setContentsMargins(10, 10, 10, 10)
		hbox.addWidget(sqrl_label, 0, Qt.AlignCenter | Qt.AlignLeft)
		hbox.addLayout(smaller_vbox)
		hbox.setSpacing(1)

		vbox.addLayout(hbox)

		vbox.addStretch(1)

	def initScraperUI(self):
		vbox = QVBoxLayout(self.scrape_window)

		# Label
		title_font = QFont()
		title_font.setPointSize(20)
		head_label = QLabel("DocuScraper")
		head_label.setFont(title_font)

		# Settings
		ocr_check = QCheckBox("Image OCR Scanning")

		ref_check = QCheckBox("Include References")

		table_label = QLabel("Table Extraction Mode")
		table_dropdown = QComboBox()
		table_dropdown.addItem("None")
		table_dropdown.addItem("Textual")
		table_dropdown.addItem("Data")

		# Start Scrape Buttons & Label
		scrape_font = QFont()
		scrape_font.setPointSize(12)
		scrape_label = QLabel("Scrape Method")
		scrape_label.setFont(scrape_font)

		self.directory_button = QPushButton("Directory")
		self.directory_button.clicked.connect(self.directoryScrape)
		self.directory_button.setFixedSize(180,65)

		self.file_button = QPushButton("File")
		self.file_button.clicked.connect(self.fileScrape)
		self.file_button.setFixedSize(180,65)

		# Add all elements to widget
		vbox.setSpacing(10)

		# UPPER SECTION
		left_vbox = QVBoxLayout()
		left_vbox.addWidget(ocr_check, 0, Qt.AlignCenter | Qt.AlignTop)
		left_vbox.addWidget(ref_check, 0, Qt.AlignCenter | Qt.AlignTop)

		right_vbox = QVBoxLayout()
		right_vbox.addWidget(table_label, 0, Qt.AlignCenter | Qt.AlignTop)
		right_vbox.addWidget(table_dropdown, 0, Qt.AlignCenter | Qt.AlignTop)

		hbox_top = QHBoxLayout()
		hbox_top.addLayout(left_vbox)
		hbox_top.addLayout(right_vbox)

		# LOWER SECTION
		hbox_bottom = QHBoxLayout()
		hbox_bottom.addWidget(self.directory_button, 0, Qt.AlignCenter)
		hbox_bottom.addWidget(self.file_button, 0, Qt.AlignCenter)

		#vbox.addWidget(back_button, 0, Qt.AlignLeft)
		vbox.addWidget(head_label, 0, Qt.AlignCenter | Qt.AlignTop)

		vbox.addLayout(hbox_top)
		vbox.addWidget(scrape_label, 0, Qt.AlignCenter)
		vbox.addLayout(hbox_bottom)

		vbox.addStretch(1)

		# Return Button
		back_button = QPushButton("Return", self.scrape_window)
		back_button.setFixedSize(50,30)
		back_button.clicked.connect(self.returnMain)
		back_button.setGeometry(10, 10, 50, 30)
		back_button.raise_()
		#self.scrape_button.clicked.connect(self.switchScrape)

	def directoryScrape(self):
		options = QFileDialog.Options()

		home_directory = os.path.expanduser("~")
		directory = QFileDialog.getExistingDirectory(self,
		"Select Directory", home_directory, options=options)

		if directory:
			directory += "/*.pdf"
			print(directory)
			self.processDocuments(directory)

	def fileScrape(self): # change to file later
		options = QFileDialog.Options()
		home_directory = os.path.expanduser("~")

		fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", home_directory,"PDF Files (*.pdf)", options=options)
		if fileName:
			self.processDocuments(fileName) 

	def processDocuments(self, path):
		self.directory_button.setEnabled(False) # Turn off buttons
		self.file_button.setEnabled(False)

		#self.scurrier = MuPDFScurrier(path)
		#elf.scurrier.progress.connect(self.update_progress)
		#self.scurrier.finished.connect(self.processing_finished)
		#self.scurrier.current_pdf.connect(self.pass_current_pdf)
		#self.scurrier.start()

	def initViewerUI(self):
		pass

	def returnMain(self):
		self.setFixedSize(QSize(400, 220))
		self.stacked_widget.setCurrentIndex(0)

	def switchScrape(self):
		self.setFixedSize(QSize(400, 400))
		self.stacked_widget.setCurrentIndex(1)

	def switchViewer(self):
		self.stacked_widget.setCurrentIndex(2)

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()