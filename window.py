from typing import Tuple
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QFrame, QMessageBox, QFileDialog
from PyQt6.QtGui import QFont, QAction, QIcon
from PyQt6.Qsci import QsciLexerPython
from PyQt6.QtCore import QCoreApplication

from editor import CustomEditor
from tabmanager import TabManager

class CustomMainWindow(QMainWindow):
    def __init__(self):
        super(CustomMainWindow, self).__init__()

        self.setGeometry(300, 300, 800, 400)
        self.setWindowTitle("Code editor")
        
        self.is_new_file = False
        self.opened_file_path = None
        self.opened_file_name = None
        
        layout = QVBoxLayout()

        frame = QFrame(self)
        frame.setStyleSheet("QWidget { background-color: #ffeaeaea }")
        frame.setLayout(layout)
        
        self.setCentralWidget(frame)
    
        self._createActions()
        self._createMenuBar()
        # self._createToolBars()
        
        lexer = QsciLexerPython()
        lexer.setFont(QFont('Fira Code'))
        
        self.editor = CustomEditor("")
        self.editor.setLexer(lexer)
        self.editor.setVisible(False)
        layout.addWidget(self.editor)

        self.show()
        
    def closeEvent(self, event):
        """
        The closeEvent function is called when the user closes the window.
        It checks if there are any unsaved changes in the file and prompts for confirmation before closing.
        
        :param event: PyQt automatically passes the event object to the function
        """
        if self.opened_file_path and self.editor.unsaved_changes and not self.is_new_file:
            self.saveFile(self.opened_file_path)
            return
        
        if self.is_new_file:
            reply = QMessageBox.question(self, 'Несохраненные изменения', 'Файл не был сохранен, вы действительно хотите выйти?',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                event.accept()
            else:
                event.ignore()
        
    def _createActions(self):
        """
        The _createActions function creates actions for the menu bar.
        """
        self.newAction = QAction("&Создать новый файл", self)
        self.newAction.setShortcut("Ctrl+n")
        self.newAction.triggered.connect(self.newActionHandler)

        self.openAction = QAction("&Открыть файл...", self)
        self.openAction.setShortcut("Ctrl+o")
        self.openAction.triggered.connect(self.openActionHandler)
        
        self.saveAction = QAction("&Сохранить", self)
        self.saveAction.setShortcut("Ctrl+s")
        self.saveAction.triggered.connect(self.saveActionHandler)
        
        self.saveAsAction = QAction("&Сохранить как...", self)
        self.saveAsAction.setShortcut("Ctrl+Shift+s")
        self.saveAsAction.triggered.connect(self.saveAsActionHandler)
        
        self.closeAction = QAction("&Закрыть файл", self)
        self.closeAction.setShortcut("Ctrl+w")
        self.closeAction.triggered.connect(self.closeActionHandler)
        
        self.exitAction = QAction("&Выйти", self)
        self.exitAction.setShortcut("Alt+f4")
        self.exitAction.triggered.connect(QCoreApplication.instance().quit)
        
        self.copyAction = QAction("&Копировать", self)
        self.pasteAction = QAction("&Вставить", self)
        self.cutAction = QAction("&Вырезать", self)
        self.helpContentAction = QAction("&Документация", self)
        self.aboutAction = QAction("&О редакторе", self)

        
    def _createMenuBar(self):
        """
        The _createMenuBar function creates the menu bar for the application.
        It adds actions to each of its menus, and sets icons where applicable.
        """
        menuBar = self.menuBar()

        fileMenu = menuBar.addMenu("&Файл")
        fileMenu.addAction(self.newAction)
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.saveAction)
        fileMenu.addAction(self.exitAction)
        fileMenu.addAction(self.closeAction)

        editMenu = menuBar.addMenu("&Редактировать")
        editMenu.addAction(self.copyAction)
        editMenu.addAction(self.pasteAction)
        editMenu.addAction(self.cutAction)

        helpMenu = menuBar.addMenu(QIcon(":help-content.svg"), "&Помощь")
        helpMenu.addAction(self.aboutAction)
        
        
    def newActionHandler(self):
        """
        The newActionHandler function creates a new file in the editor.
        """
        self.editor.setVisible(True)
        self.editor.setText("")
        
        self.is_new_file = True
    
    def openActionHandler(self):
        """
        The openActionHandler function opens a file dialog and sets the text of the editor to the contents of 
        the chosen file. If no file is chosen, nothing happens.
        """
        file_path, _ = self.choose_file()
        if file_path:
            with open(file_path, 'r', encoding='utf8') as f:
                self.opened_file_path = file_path
                self.is_new_file = False
                self.editor.setVisible(True)
                self.editor.setText(f.read())
                
    def saveFile(self, file_path):
        """
        The saveFile function saves the contents of the editor to a file.
        It does this by writing to an open file object, which is created with
        the 'w' flag (indicating that it is opened for writing). The function 
        also sets self.unsaved_changes to False and updates self.opened_file_path 
        to reflect the new path of the saved file.
        
        :param file_path: Save the file to a specific location
        """
        with open(file_path, 'w', encoding='utf8') as f:
            text = self.editor.text()
            text = text.replace('\r', '')
            f.write(text)
                
            if self.is_new_file:
                self.opened_file_path = file_path
                self.is_new_file = False
                
            self.unsaved_changes = False
            
    def saveActionHandler(self): 
        """
        The saveActionHandler method saves the current file to a specified location.
        If no location is specified, it will save the file to its original location.
        """
        if self.is_new_file or self.opened_file_path:
            if self.is_new_file:
                file_path, _ = self.choose_file_save()
            else:
                file_path = self.opened_file_path
                
            if file_path:
                self.saveFile(file_path)
            
    def saveAsActionHandler(self):
        """
        The saveAsActionHandler method is called when the user selects the saveAsAction from the file menu. 
        It opens a dialog box to allow them to choose where they want to save their file and what name they want it saved as. 
        If a path is chosen, then that path is used in self.saveFile(file_path) which saves the current document.
        """
        if self.is_new_file or self.opened_file_path:
            file_path, _ = self.choose_file_save()

            if file_path:
                self.saveFile(file_path)
            
    def closeActionHandler(self):
        """
        The closeActionHandler function clears the editor and makes it invisible when file closes.
        """
        self.editor.clear()
        self.editor.setVisible(False)
    
    # TODO: implement cringe usless functions
    def exitActionHandler(self): raise NotImplementedError
    
    def copyActionHandler(self): raise NotImplementedError
    def pasteActionHandler(self): raise NotImplementedError
    def cutActionHandler(self): raise NotImplementedError
    
    def aboutActionHandler(self): raise NotImplementedError

    def choose_file(self) -> Tuple[str, str]:
        """
        The choose_file function allows the user to select a file from their computer.
        The function returns a tuple containing the path and filter used to choose the file.
        
        `path, filters = self.choose_file()`
        :return: A tuple containing the path and filter
        """
        return QFileDialog.getOpenFileName(self, 'Open file', __file__) or __file__
    
    def choose_file_save(self) -> Tuple[str, str]:
        return QFileDialog.getSaveFileName(self, 'Save File')
        

