import sys
import os

from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import QSize, Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QMainWindow, QFileDialog, 
	QProgressBar, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QSizePolicy, QGridLayout)

class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()

		self.setWindowTitle("DocuScurry")
		self.setFixedSize(QSize(400, 220))
		#setMinimumSize
		#setMaximumSize

		self.initUI()

	def initUI(self):
		w = QWidget()
		self.setCentralWidget(w)
		vbox = QVBoxLayout(w)

		# Buttons
		self.scrape_button = QPushButton("Scraper")
		self.scrape_button.setCheckable(True)
		self.scrape_button.setFixedSize(180,65)
		#self.scrape_button.clicked.connect(self.directory_scrape)

		self.viewer_button = QPushButton("Viewer")
		self.viewer_button.setCheckable(True)
		self.viewer_button.setFixedSize(180,65)
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
		smaller_vbox.addWidget(self.scrape_button, 0, Qt.AlignLeft | Qt.AlignCenter)
		smaller_vbox.addWidget(self.viewer_button, 0, Qt.AlignLeft | Qt.AlignCenter)


		hbox = QHBoxLayout()
		#hbox.setContentsMargins(10, 10, 10, 10)
		hbox.addWidget(sqrl_label, 0, Qt.AlignCenter | Qt.AlignLeft)
		hbox.addLayout(smaller_vbox)
		hbox.setSpacing(1)

		vbox.addLayout(hbox)

		vbox.addStretch(1)

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()