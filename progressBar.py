import sys
import os
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QSize, Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QMainWindow, QFileDialog, 
	QProgressBar, QVBoxLayout, QWidget, QLabel, QSizePolicy, QGridLayout)

class ProgressWidget:
	def __init__(self):
		self.initUI();

	def initUI(self):
		self.widget = QWidget()
		self.widget.resize(400, 50)
		self.widget.setFixedWidth(400)
		self.widget.setWindowTitle("Scurrying...")
		vbox = QVBoxLayout(self.widget)

		self.progress_bar = QProgressBar()
		self.information_label = QLabel("Current PDF: None")

		# Stylization
		font = QFont()
		font.setPointSize(8)
		self.information_label.setFont(font)

		vbox.setSpacing(10)
		vbox.setContentsMargins(10, 10, 10, 10)
		vbox.addWidget(self.progress_bar, 0, Qt.AlignTop)
		vbox.addWidget(self.information_label, 0, Qt.AlignTop | Qt.AlignLeft)

	def update_progress(self, value):
		self.progress_bar.setValue(value)

	def showWidget(self, appear):
		self.widget.setVisible(appear)

	def current_pdf(self, title):
		self.information_label.setText(f"Current PDF: {title}")