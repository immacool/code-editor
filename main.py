import sys

from PyQt6.QtWidgets import QApplication, QStyleFactory
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt

from window import CustomMainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)

    QApplication.setStyle(QStyleFactory.create('Fusion'))
    
    # palette = QPalette()
    # palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    # palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    # app.setPalette(palette)
    
    myGUI = CustomMainWindow()

    sys.exit(app.exec())