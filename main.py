import sys
from pfilter_gui import Widget
from PySide2.QtWidgets import QApplication, QMainWindow, QAction, QInputDialog, QLineEdit
from PySide2.QtCore import Slot


class MainWindow(QMainWindow):
	def __init__(self, widget):
		QMainWindow.__init__(self)
		self.setWindowTitle("Playlist Filter for Spotify")

		self.menu = self.menuBar()
		self.file_menu = self.menu.addMenu("File")
		setup_action = QAction("Setup", self)
		setup_action.triggered.connect(self.setup)
		self.file_menu.addAction(setup_action)

		exit_action = QAction("Exit", self)
		exit_action.triggered.connect(self.exit_app)
		self.file_menu.addAction(exit_action)
		self.setCentralWidget(widget)


	@Slot()
	def setup(self):
		# Get spotify username
		username, ok = QInputDialog().getText(self, "Enter Spotify username", "Spotify Username", QLineEdit.Normal)
		while not ok:
			username, ok = QInputDialog().getText(self, "Enter Spotify username", "Spotify Username", QLineEdit.Normal)
		
		# write id, secret, username to file in same directory
		f = open("_config.txt", 'w')
		username += '\n'
		f.write(username)
		f.close()


	@Slot()
	def exit_app(self):
		QApplication.quit()


if __name__ == "__main__":
	app = QApplication(sys.argv)

	widget = Widget()
	window = MainWindow(widget)
	window.resize(1000, 600)
	window.show()
	
	sys.exit(app.exec_())
