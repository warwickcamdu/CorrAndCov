from PyQt5.QtWidgets import QWidget, QPushButton, QMainWindow
from PyQt5.QtWidgets import QLabel, QLineEdit, QGridLayout, QStyle
from PyQt5.QtWidgets import QFileDialog, QAction, QMessageBox
from PyQt5.QtGui import QIcon, QDoubleValidator, QIntValidator
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
        if not self.settings.value('Actin Folder'):
            self.settings.setValue(
                'Actin Folder', os.path.basename(
                    self.settings.value('Data Folder')))
        if not self.settings.value('Scale Factor'):
            self.settings.setValue('Scale Factor', 0.25)
        if not self.settings.value('Offset'):
            self.settings.setValue('Offset', 60)
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
        # Info icon
        icon = self.style().standardIcon(QStyle.SP_MessageBoxInformation)
        pixmap = icon.pixmap(icon.availableSizes()[0])
        # Data folder
        folder_lbl = QLabel()
        folder_lbl.setText(
            "<html><pre>    Data folder </pre></html>")
        ficon_lbl = QLabel()
        ficon_lbl.setPixmap(pixmap)
        ficon_lbl.setToolTip(
            "Select folder where images are stored")
        self.folder_edt = QLineEdit()
        self.folder = self.settings.value('Data Folder')
        self.folder_edt.setText(self.folder)
        folder_browse = QPushButton('Browse')
        folder_browse.clicked.connect(self.get_folder)
        # Actin folder
        actinfolder_lbl = QLabel()
        actinfolder_lbl.setText(
            "<html><pre>    Actin folder </pre></html>")
        aicon_lbl = QLabel()
        aicon_lbl.setPixmap(pixmap)
        aicon_lbl.setToolTip(
            "Select folder where actin images are stored")
        self.actinfolder_edt = QLineEdit()
        self.actinfolder = self.settings.value('Actin Folder')
        self.actinfolder_edt.setText(self.actinfolder)
        actinfolder_browse = QPushButton('Browse')
        actinfolder_browse.clicked.connect(self.get_actinfolder)
        # Scale factor
        scalefactor_lbl = QLabel()
        scalefactor_lbl.setText(
            "<html><pre>    Scale Factor </pre></html>")
        sicon_lbl = QLabel()
        sicon_lbl.setPixmap(pixmap)
        sicon_lbl.setToolTip(
            "Amount to downscale image by (less than 1)")
        self.scalefactor_edt = QLineEdit()
        self.scalefactor_edt.setText(self.settings.value('Scale Factor'))
        self.scalefactor_edt.setValidator(
            QDoubleValidator(0.001, 0.999, 4, self.scalefactor_edt))
        self.scalefactor = self.scalefactor_edt.text()
        # Offset
        offset_lbl = QLabel()
        offset_lbl.setText(
            "<html><pre>    Offset </pre></html>")
        oicon_lbl = QLabel()
        oicon_lbl.setPixmap(pixmap)
        oicon_lbl.setToolTip(
            "How much to displace images by (in time)")
        self.offset_edt = QLineEdit()
        self.offset_edt.setText(self.settings.value('Offset'))
        self.offset_edt.setValidator(QIntValidator(self.offset_edt))
        self.offset = self.offset_edt.text()
        # Run Button
        run_btn = QPushButton('Run')
        run_btn.clicked.connect(self.run)
        # Layout
        self.grid = QGridLayout()
        self.grid.addWidget(folder_lbl, 0, 0)
        self.grid.addWidget(ficon_lbl, 0, 0)
        self.grid.addWidget(self.folder_edt, 0, 1)
        self.grid.addWidget(folder_browse, 0, 2)
        self.grid.addWidget(actinfolder_lbl, 1, 0)
        self.grid.addWidget(aicon_lbl, 1, 0)
        self.grid.addWidget(self.actinfolder_edt, 1, 1)
        self.grid.addWidget(actinfolder_browse, 1, 2)
        self.grid.addWidget(scalefactor_lbl, 2, 0)
        self.grid.addWidget(sicon_lbl, 2, 0)
        self.grid.addWidget(self.scalefactor_edt, 2, 1, 1, 2)
        self.grid.addWidget(offset_lbl, 3, 0)
        self.grid.addWidget(oicon_lbl, 3, 0)
        self.grid.addWidget(self.offset_edt, 3, 1, 1, 2)
        self.grid.addWidget(run_btn, 6, 1, 1, 2)
        w = QWidget()
        w.setLayout(self.grid)
        return(w)

    def get_folder(self):
        self.folder = QFileDialog.getExistingDirectory(
            None, "Select Folder", self.folder_edt.text())
        self.folder_edt.setText(self.folder)
        self.settings.setValue('Data Folder', self.folder)
        self.actinfolder_edt.setText(self.folder)

    def get_actinfolder(self):
        self.actinfolder = os.path.basename(QFileDialog.getExistingDirectory(
            None, "Select Folder", self.folder_edt.text()))
        self.actinfolder_edt.setText(self.actinfolder)
        self.settings.setValue('Actin Folder', self.actinfolder)

    def msgbtn(self):
        self.msg.done()

    def run(self):
        self.scalefactor = float(self.scalefactor_edt.text())
        self.offset = int(self.offset_edt.text())
        self.settings.setValue('Scale Factor', self.scalefactor_edt.text())
        self.settings.setValue('Offset', self.offset_edt.text())
        if self.scalefactor < 1:
            CorrFunctions.calculate_and_create_figures(
                self.folder,
                self.actinfolder,
                float(self.scalefactor),
                int(self.offset)
                )
            self.msg = QMessageBox()
            self.msg.setIcon(QMessageBox.Information)
            self.msg.setText("Calculations Complete")
            self.msg.setWindowTitle("Finished")
            self.msg.setStandardButtons(QMessageBox.Ok)
            self.msg.exec_()
            self.msg.buttonClicked.connect(self.msgbtn)

    def open_doc(self):
        webbrowser.open(
            "https://laura190.github.io/CorrAndCov/")
