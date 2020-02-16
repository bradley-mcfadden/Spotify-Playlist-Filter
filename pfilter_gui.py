from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import (QWidget, QApplication, QHBoxLayout, QTableWidget, QTableWidgetItem, QVBoxLayout, QListWidget, QListWidgetItem, QLabel, QGroupBox, QRadioButton, QCheckBox, QLineEdit, QFormLayout, QPlainTextEdit,QPushButton)
from pfilter import PFilter


class Widget(QWidget):
	def __init__(self):
		QWidget.__init__(self)
		
		self.layout = QHBoxLayout() # start 	main panel
		
		self.list = QListWidget()
		self.table = QTableWidget()
		self.table.setColumnCount(3)
		self.table.setHorizontalHeaderLabels(["Track Name", "Artist", "Album"])
		self.right = QVBoxLayout()
		self.right.setMargin(10)
		# self.right.addStretch()

		self.filter_group = QGroupBox("Filters")
		filter_artist = QRadioButton("By Artist")
		filter_genre = QRadioButton("By Genre")
		filter_track = QRadioButton("By Track")
		filter_artist.setChecked(True)
		vbox = QVBoxLayout()
		vbox.addWidget(filter_artist)
		vbox.addWidget(filter_genre)
		vbox.addWidget(filter_track)
		# vbox.addStretch(1)
		self.filter_group.setLayout(vbox)

		self.search_layout = QHBoxLayout()
		self.search_field = QLineEdit()
		self.search_layout.addWidget(QLabel("Search Term"))
		self.search_layout.addWidget(self.search_field)
		self.neg_search_button = QCheckBox("Enable Negative Search")
		
		create_box = QGroupBox("Create Playlist")
		vbox_create_playlist = QVBoxLayout()
		hbox_name = QHBoxLayout()
		self.create_name_field = QLineEdit()
		hbox_name.addWidget(QLabel("Name"))
		hbox_name.addWidget(self.create_name_field)
		self.desc_edit = QPlainTextEdit()
		self.create_button = QPushButton("Create Playlist")
		vbox_create_playlist.addLayout(hbox_name)
		vbox_create_playlist.addWidget(QLabel("Description"))
		vbox_create_playlist.addWidget(self.desc_edit)
		vbox_create_playlist.addWidget(self.create_button)
		create_box.setLayout(vbox_create_playlist)
		
		self.right.addWidget(self.filter_group)
		self.right.addLayout(self.search_layout)	
		self.right.addWidget(self.neg_search_button)
		self.right.addWidget(create_box)

		self.layout.addWidget(self.list)
		self.layout.addWidget(self.table)
		self.layout.addLayout(self.right)

		self.setLayout(self.layout) # end 		main panel
