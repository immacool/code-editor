import sys

from PyQt6.QtWidgets import QApplication, QStyleFactory

from palettes import get_dark_palette, Theme
from utils import SettingsInstance
from window import CustomMainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)

    QApplication.setStyle(QStyleFactory.create('Fusion'))
    
    settings = SettingsInstance()
    if settings.default_theme == Theme.DARK:
        app.setPalette(get_dark_palette())
    gui = CustomMainWindow(settings)

    sys.exit(app.exec())
