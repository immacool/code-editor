from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtCore import Qt

GlobalColor = Qt.GlobalColor

dark_palette = QPalette()
dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
dark_palette.setColor(QPalette.WindowText, GlobalColor.white)
dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
dark_palette.setColor(QPalette.ToolTipBase, GlobalColor.white)
dark_palette.setColor(QPalette.ToolTipText, GlobalColor.white)
dark_palette.setColor(QPalette.Text, GlobalColor.white)
dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
dark_palette.setColor(QPalette.ButtonText, GlobalColor.white)
dark_palette.setColor(QPalette.BrightText, GlobalColor.red)
dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
dark_palette.setColor(QPalette.HighlightedText, GlobalColor.black)