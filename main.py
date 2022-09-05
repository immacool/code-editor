import sys
from PyQt6.QtWidgets import QApplication, QStyleFactory

from window import CustomMainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    QApplication.setStyle(QStyleFactory.create('Fusion'))
    myGUI = CustomMainWindow()

    sys.exit(app.exec())