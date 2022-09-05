import ntpath
from PyQt6.QtWidgets import QTabWidget
from editor import CustomEditor


class TabManager(QTabWidget):

    def __init__(self):
        super(TabManager, self).__init__()

    def show_file(self, filepath):
        with open(filepath, "r") as f:
            text = f.read()

        newtab = CustomEditor(text)
        newtabName = ntpath.basename(filepath)

        self.addTab(newtab, newtabName)
        self.setCurrentWidget(newtab)

        newtab.setCursorPosition(0, 0)
        newtab.ensureCursorVisible()
        newtab.setFocus()