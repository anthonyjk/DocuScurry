import sys
import os
from dataScurrier import MuPDFScurrier

from PyQt5.QtCore import QSize, Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QMainWindow, QFileDialog, 
	QProgressBar, QVBoxLayout, QWidget, QLabel, QSizePolicy, QGridLayout)

class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()

		self.setWindowTitle("DocuScurry")

		self.setFixedSize(QSize(400, 400))
		#setMinimumSize
		#setMaximumSize

		self.initUI()

	def initUI(self):
		w = QWidget()
		self.setCentralWidget(w)
		vbox = QVBoxLayout(w)

		# Buttons
		self.dir_button = QPushButton("Directory")
		self.dir_button.setCheckable(True)
		self.dir_button.clicked.connect(self.directory_scrape)
		self.dir_button.setFixedWidth(150)
		self.dir_button.setFixedHeight(100)

		self.file_button = QPushButton("File")
		self.file_button.setCheckable(True)
		self.file_button.clicked.connect(self.file_scrape)
		self.file_button.setFixedWidth(150)
		self.file_button.setFixedHeight(100)

		# Details
		# Progress Bar has its own window?
		self.progress_bar = QProgressBar()
		self.progress_bar.setVisible(False)

		vbox.setSpacing(10)
		vbox.setContentsMargins(10, 10, 10, 10)
		vbox.addWidget(self.dir_button, 0, Qt.AlignLeft | Qt.AlignTop)
		vbox.addWidget(self.file_button, 0, Qt.AlignLeft | Qt.AlignTop)

		vbox.addStretch(1)


	def directory_scrape(self):
		options = QFileDialog.Options()

		home_directory = os.path.expanduser("~")
		directory = QFileDialog.getExistingDirectory(self,
		"Select Directory", home_directory, options=options)

		if directory:
			directory += "/*.pdf"
			print(directory)
			self.process_pdfs(directory)

	def file_scrape(self): # change to file later
		options = QFileDialog.Options()

		home_directory = os.path.expanduser("~")
		directory = QFileDialog.getExistingDirectory(self,
		"Select Directory", home_directory, options=options)

		if directory:
			directory += "/*.pdf"
			print(directory)
			self.process_pdfs(directory)

	def process_pdfs(self, path):
		self.dir_button.setEnabled(False) # Turn off button
		self.progress_bar.setVisible(True)
		self.progress_bar.setValue(0)

		# Threading
		self.scurrier = MuPDFScurrier(path)
		self.scurrier.progress.connect(self.update_progress)
		self.scurrier.finished.connect(self.processing_finished)
		self.scurrier.start()

	def update_progress(self, value):
		self.progress_bar.setValue(value)

	def processing_finished(self, results):
		self.dir_button.setEnabled(True)
		self.progress_bar.setVisible(False)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()