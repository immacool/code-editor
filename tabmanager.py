from PyQt6.QtWidgets import QTabWidget

from editor import CustomEditor


class TabManager(QTabWidget):

    def __init__(self, theme):
        super(TabManager, self).__init__()
        self.theme = theme

    def editors_states(self) -> dict:
        """
        The editors_states function returns a dictionary of the unsaved_changes attribute for each editor.
        The unsaved_changes attribute is True if there are any changes to the editor's document that have not been saved.
        """
        return {i: self.widget(i).file.saved for i in range(self.count())}
    
    def get_files(self):
        """
        The get_fiels function returns a list of the file paths for each editor.
        """
        return [self.widget(i).file for i in range(self.count())]

    def show_file(self, filepath=None, is_new=False):
        """
        The show_file function creates a new tab in the editor and displays the file contents.
        If no filepath is provided, it creates an empty editor instead.
        
        :param filepath=None: Determine whether the file is opened from a file or created new
        :param is_new=False: Determine whether the file should be opened in a new tab or not
        
        :return: True if the file was opened successfully, False otherwise
        """
        if filepath:
            newtab = CustomEditor(self.theme, file_path=filepath)
            if newtab.error_while_reading:
                return False
            newtabName = newtab.file.name
        elif is_new:
            newtab = CustomEditor(self.theme)
            newtabName = "Без имени"

        self.addTab(newtab, newtabName)
        self.setCurrentWidget(newtab)

        newtab.setCursorPosition(0, 0)
        newtab.ensureCursorVisible()
        newtab.setFocus()
        
        return True
