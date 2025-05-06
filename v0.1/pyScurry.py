import sys
import os
from dataScurrier import MuPDFScurrier
from progressBar import ProgressWidget

from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import QSize, Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QMainWindow, QFileDialog, 
	QProgressBar, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QSizePolicy, QGridLayout)

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
		self.dir_button.setFixedWidth(380)
		self.dir_button.setFixedHeight(100)

		self.file_button = QPushButton("File")
		self.file_button.setCheckable(True)
		self.file_button.clicked.connect(self.file_scrape)
		self.file_button.setFixedWidth(380)
		self.file_button.setFixedHeight(100)

		# Details
		self.progress_widget = ProgressWidget() # Hidden on initialization
		self.progress_widget.showWidget(False)

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

		hbox = QHBoxLayout()
		hbox.addWidget(sqrl_label, 0, Qt.AlignCenter)
		hbox.addWidget(ds_title, 0, Qt.AlignCenter)

		vbox.addLayout(hbox)
		vbox.addWidget(self.dir_button, 1, Qt.AlignCenter | Qt.AlignTop)
		vbox.addWidget(self.file_button, 1, Qt.AlignCenter | Qt.AlignTop)

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

		fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", home_directory,"PDF Files (*.pdf)", options=options)
		if fileName:
			self.process_pdfs(fileName)

	def process_pdfs(self, path):
		self.dir_button.setEnabled(False) # Turn off buttons
		self.file_button.setEnabled(False)
		self.progress_widget.showWidget(True)
		self.progress_widget.update_progress(0)

		# Signaling
		self.scurrier = MuPDFScurrier(path)
		self.scurrier.progress.connect(self.update_progress)
		self.scurrier.finished.connect(self.processing_finished)
		self.scurrier.current_pdf.connect(self.pass_current_pdf)
		self.scurrier.start()

	def pass_current_pdf(self, title):
		self.progress_widget.current_pdf(title)

	def update_progress(self, value):
		self.progress_widget.update_progress(value)

	def processing_finished(self, results):
		self.dir_button.setEnabled(True)
		self.file_button.setEnabled(True)
		self.progress_widget.showWidget(False)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()