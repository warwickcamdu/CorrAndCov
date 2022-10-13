# Packages
# PyQt
import sys
from PyQt5.QtWidgets import QApplication
import CC_App

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CC_App.home()
    window.show()
    app.exec()
