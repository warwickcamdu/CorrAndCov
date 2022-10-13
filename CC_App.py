from PyQt5.QtWidgets import QWidget, QPushButton, QMainWindow
from PyQt5.QtWidgets import QLabel, QLineEdit, QGridLayout
from PyQt5.QtWidgets import QFileDialog, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSettings
import os.path
import webbrowser
import CorrFunctions


class home(QMainWindow):
    def __init__(self):
        QWidget.__init__(self)
        # Window setup
        self.resize(600, 600)
        self.setWindowTitle('Corr and CoV')
        self.setWindowIcon(QIcon('square_black.jpg'))
        self.settings = QSettings()
        # Default settings
        if not self.settings.value('Data Folder'):
            user_home = os.path.expanduser("~")
            self.settings.setValue('Data Folder', user_home)
        # Menu setup
        menu_bar = self.menuBar()
        help_menu = menu_bar.addMenu('&Help')
        document = QAction('&Documentation', self)
        document.triggered.connect(self.open_doc)
        help_menu.addAction(document)
        self.setCentralWidget(self.centralWidget())

    def centralWidget(self):
        self.folder = False
        font = self.font()
        font.setPointSize(16)
        self.window().setFont(font)
        folder_lbl = QLabel()
        folder_lbl.setText(
            "Select data folder <html><img height=16 src='info.png'></html>")
        folder_lbl.setToolTip(
            "Select folder where images are stored")
        self.folder_edt = QLineEdit()
        self.folder = self.settings.value('Data Folder')
        self.folder_edt.setText(self.folder)
        browse = QPushButton('Browse')
        browse.clicked.connect(self.get_folder)  # change to get folder path
        description_lbl = QLabel()
        description_lbl.setText(
            "Scale Factor <html><img height=16 src='info.png'></html>")
        description_lbl.setToolTip(
            "Amount to downscale image by")
        self.description_edt = QLineEdit()
        bioentity_lbl = QLabel()
        bioentity_lbl.setText(
            "Offset <html><img height=16 src='info.png'></html>")
        bioentity_lbl.setToolTip(
            "How much to displace images by (in time)")
        self.bioentity_edt = QLineEdit()
        # Save and Close Button
        close_btn = QPushButton('Save and Close')
        close_btn.clicked.connect(self.save_and_close)
        # Layout
        self.grid = QGridLayout()
        self.grid.addWidget(folder_lbl, 0, 0)
        self.grid.addWidget(self.folder_edt, 0, 1)
        self.grid.addWidget(browse, 0, 2)
        self.grid.addWidget(description_lbl, 1, 0)
        self.grid.addWidget(self.description_edt, 1, 1, 1, 2)
        self.grid.addWidget(bioentity_lbl, 2, 0)
        self.grid.addWidget(self.bioentity_edt, 2, 1, 1, 2)
        self.grid.addWidget(close_btn, 6, 1)
        w = QWidget()
        w.setLayout(self.grid)
        return(w)

    def get_folder(self):
        self.folder = QFileDialog.getExistingDirectory(
            None, "Select Folder", self.folder_edt.text())
        self.folder_edt.setText(self.folder)

    def save_and_close(self):
        exit()

    def open_doc(self):
        webbrowser.open(
            "https://laura190.github.io/MetadataCollection/")
