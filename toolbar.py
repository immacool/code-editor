from PyQt6.QtGui import 
from PyQt6.QtWidgets import QWidget, QHBoxLayout

class ToolBar(QWidget):

    def __init__(self, parent=None):
        super(ToolBar, self).__init__(parent)
        self.layout().addWidget(self.Button)

        self.Button.menu().resizeEvent = self.onResize

    def onResize(self, event):
        self.MyW.resize(event.size())
