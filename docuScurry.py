import sys
import os
from glob import glob

from scraper import MuPDFScurrier

from PyQt5.QtGui import QPixmap, QFont, QIcon
from PyQt5.QtCore import QSize, Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QMainWindow, QFileDialog, 
	QProgressBar, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QSizePolicy, QStackedWidget, 
	QCheckBox, QComboBox, QGroupBox, QTextEdit)

class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()

		self.setWindowTitle("DocuScurry")
		self.setWindowIcon(QIcon('./sqrl_icon.png'))

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
		self.scraperStyleUI()

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
		self.file_paths = []
		self.textual_output = ""

		mega_hbox = QHBoxLayout(self.scrape_window)
		mega_hbox.setContentsMargins(10, 10, 10, 10)

		vbox = QVBoxLayout()

		# RETURN BUTTON
		back_button = QPushButton("Return", self.scrape_window)
		back_button.setFixedSize(50,30)
		back_button.clicked.connect(self.returnMain)
		back_button.setGeometry(10, 10, 50, 30)
		back_button.raise_()

		# TITLE
		title_font = QFont()
		title_font.setPointSize(20)
		head_label = QLabel("DocuScraper")
		head_label.setFont(title_font)
		vbox.addWidget(head_label, 0, Qt.AlignCenter | Qt.AlignTop)

		# SELECT PATH BUTTONS
		self.file_button = QPushButton("Append PDF")
		self.file_button.clicked.connect(self.file_selection)

		self.folder_button = QPushButton("Append from Folder")
		self.folder_button.clicked.connect(self.folder_selection)

		self.clear_button = QPushButton("Clear Selection")
		self.clear_button.clicked.connect(self.clear_selected_files)

		top_hbox = QHBoxLayout()
		top_hbox.addWidget(self.file_button)
		top_hbox.addWidget(self.folder_button)
		top_hbox.addWidget(self.clear_button)
		vbox.addLayout(top_hbox)

		# FILE PATHS DISPLAY
		self.files_display = QTextEdit()
		self.files_display.setReadOnly(True)
		self.files_display.setPlaceholderText("Selected PDF files will appear here...")
		vbox.addWidget(self.files_display)

		# SETTINGS
		settings_box = QGroupBox("Options")
		settings_layout = QVBoxLayout()

		middle_hbox = QHBoxLayout()

		left_vbox = QVBoxLayout()
		right_vbox = QVBoxLayout()

		# LEFT VBOX
		self.ocr_check = QCheckBox("Image Text Extraction")
		left_vbox.addWidget(self.ocr_check, 0, Qt.AlignCenter)

		self.ref_check = QCheckBox("Include References")
		left_vbox.addWidget(self.ref_check, 0, Qt.AlignCenter)

		self.link_check = QCheckBox("Remove In-text Links")
		left_vbox.addWidget(self.link_check, 0, Qt.AlignCenter)

		self.latex_check = QCheckBox("LaTeX Extraction")
		left_vbox.addWidget(self.latex_check, 0, Qt.AlignCenter)

		# RIGHT VBOX
		table_label = QLabel("Table Extraction Mode")
		self.table_dropdown = QComboBox()
		self.table_dropdown.addItem("None")
		self.table_dropdown.addItem("Textual")
		self.table_dropdown.addItem("Data")
		right_vbox.addWidget(table_label, 0, Qt.AlignCenter | Qt.AlignTop)
		right_vbox.addWidget(self.table_dropdown, 0, Qt.AlignCenter | Qt.AlignTop)

		headtail_label = QLabel("Headers & Footers Mode")
		self.headtail_dropdown = QComboBox()
		self.headtail_dropdown.addItem("Keep Both")
		self.headtail_dropdown.addItem("Keep Headers")
		self.headtail_dropdown.addItem("Keep Footers")
		self.headtail_dropdown.addItem("Remove Both")
		right_vbox.addWidget(headtail_label, 0, Qt.AlignCenter | Qt.AlignTop)
		right_vbox.addWidget(self.headtail_dropdown, 0, Qt.AlignCenter | Qt.AlignTop)

		output_label = QLabel("Output Format")
		self.output_dropdown = QComboBox()
		self.output_dropdown.addItem(".json")
		self.output_dropdown.addItem(".csv")
		self.output_dropdown.addItem(".txt")
		right_vbox.addWidget(output_label, 0, Qt.AlignCenter | Qt.AlignTop)
		right_vbox.addWidget(self.output_dropdown, 0, Qt.AlignCenter | Qt.AlignTop)

		# LAYOUT STACKING
		middle_hbox.addLayout(left_vbox)
		middle_hbox.addLayout(right_vbox)
		settings_layout.addLayout(middle_hbox)

		settings_box.setLayout(settings_layout)
		vbox.addWidget(settings_box)

		# SCRAPE & EXPORT
		self.scrape_button = QPushButton("Begin Scrape")
		self.scrape_button.clicked.connect(self.scrape_pdfs)

		self.export_button = QPushButton("Export Result")
		self.export_button.clicked.connect(self.export_to_file)
		self.export_button.setEnabled(False)

		scrape_hbox = QHBoxLayout()
		scrape_hbox.addWidget(self.scrape_button, 1)
		scrape_hbox.addWidget(self.export_button, 0)

		vbox.addLayout(scrape_hbox)

		vbox.addStretch(1)

		mega_hbox.addLayout(vbox)
		# OUTPUT FILEDISPLAY AND PROGRESS BAR
		output_vbox = QVBoxLayout()

		self.output_display = QTextEdit()
		self.output_display.setReadOnly(True)
		self.output_display.setPlaceholderText("Extraction Output will appear here...")
		output_vbox.addWidget(self.output_display, 1)

		self.progress_bar = QProgressBar()
		#self.progress_bar.setMinimumWidth(self.output_display.width())
		self.progress_bar.setTextVisible(True)
		#self.progress_bar.setFormat("%p%")
		output_vbox.addWidget(self.progress_bar, 0)

		mega_hbox.addLayout(output_vbox)

	def scraperStyleUI(self):
		self.progress_bar.setStyleSheet("""
		QProgressBar {
			border: 1px solid grey;
			border-radius: 3px;
			text-align: center;
		}
		QProgressBar::chunk {
			background-color: #05B8CC;
			width: 10px;
		}
		""")

	def folder_selection(self):
		options = QFileDialog.Options()

		home_directory = os.path.expanduser("~")
		directory = QFileDialog.getExistingDirectory(self,
		"Select Folder", home_directory, options=options)

		if directory:
			directory += "/*.pdf"
			self.update_selected_files(glob(directory))

	def file_selection(self):
		options = QFileDialog.Options()
		home_directory = os.path.expanduser("~")

		fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", home_directory,"PDF Files (*.pdf)", options=options)
		if fileName:
			self.update_selected_files([fileName])

	def update_selected_files(self, paths):
		for path in paths:
			self.file_paths.append(path)
			self.files_display.append(path)

	def clear_selected_files(self):
		self.files_display.clear()
		self.file_paths.clear()

	def scrape_result(self):
		if len(self.file_paths) == 0:
			return

	def output_scrape_results(self, output):
		if output:
			self.output_display.clear()
			self.output_display.append(output)
			self.textual_output = output
			self.export_button.setEnabled(True)

	def update_progress(self, value):
		self.progress_bar.setValue(value)

	def processing_finished(self):
		pass

	def scrape_pdfs(self):
		if len(self.file_paths) > 0:
			settings = []
			settings.append(self.ocr_check.isChecked())
			settings.append(self.ref_check.isChecked())
			settings.append(self.link_check.isChecked())
			settings.append(self.latex_check.isChecked())
			settings.append(self.table_dropdown.currentText())
			settings.append(self.headtail_dropdown.currentText())
			settings.append(self.output_dropdown.currentText())

			self.scurrier = MuPDFScurrier(settings, self.file_paths)
			self.scurrier.progress.connect(self.update_progress) # (For Progress bar)
			#self.scurrier.finished.connect(self.processing_finished) (Re-enable buttons)
			self.scurrier.output.connect(self.output_scrape_results)
			self.scurrier.start()

	def export_to_file(self):
		if(self.textual_output):
			file_extension = ".json"
			file_filter = "JSON Files (*.json)"
			file_path, _ = QFileDialog.getSaveFileName(
			self, "Save Results", f"output{file_extension}", file_filter
			)

			if file_path:
				with open(file_path, 'w', encoding='utf-8') as f:
					if(file_extension == ".json"):
						f.write(self.textual_output)

					f.close()

	def initViewerUI(self):
		pass

	def returnMain(self):
		self.setFixedSize(QSize(400, 220))
		self.stacked_widget.setCurrentIndex(0)

	def switchScrape(self):
		self.setFixedSize(QSize(1100, 500))
		self.stacked_widget.setCurrentIndex(1)

	def switchViewer(self):
		self.stacked_widget.setCurrentIndex(2)

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()