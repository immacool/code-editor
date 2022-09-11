import os
import subprocess
from functools import partial
from typing import Tuple

from PyQt6.QtCore import QCoreApplication, QModelIndex, Qt, pyqtSlot
from PyQt6.QtGui import QAction, QFileSystemModel, QIcon
from PyQt6.QtWidgets import (QDockWidget, QFileDialog, QFrame, QLabel,
                             QMainWindow, QMessageBox, QVBoxLayout)

from globals import WINDOW_ICON
from tabmanager import TabManager
from tree import FileTree
from utils import SettingsInstance


class CustomMainWindow(QMainWindow):

    def __init__(self):
        super(CustomMainWindow, self).__init__()

        self.setWindowIcon(QIcon(WINDOW_ICON))
        self.setGeometry(300, 300, 800, 400)
        self.setWindowTitle("Редактор кода")

        self.settings = SettingsInstance()

        layout = QVBoxLayout()

        frame = QFrame(self)
        # frame.setStyleSheet("QWidget { background-color: #ffeaeaea }")
        frame.setLayout(layout)

        self.setCentralWidget(frame)

        self.tab_manager = TabManager()
        self.tab_manager.setVisible(False)

        self.file_tree = FileTree()
        self.file_tree.doubleClicked.connect(self.openFromTree)

        self.directory_sidebar = QDockWidget("Проводник", self)
        self.directory_sidebar.setFloating(False)
        self.directory_sidebar.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea)
        self.directory_sidebar.setWidget(self.file_tree)
        self.directory_sidebar.setVisible(False)

        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea,
                           self.directory_sidebar)

        self.placeholder = QLabel(
            'Создайте новый файл (Ctrl + n)\nили\nоткройте существующий (Ctrl + o).'
        )
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._createActions()
        self._createMenuBar()

        layout.addWidget(self.tab_manager)
        layout.addWidget(self.placeholder)

        self.show()

    def get_editors(self):
        return [
            self.tab_manager.widget(i) for i in range(self.tab_manager.count())
        ]

    def closeEvent(self, event):
        """
        The closeEvent function is called when the user closes the window.
        It checks if there are any unsaved changes in the file and prompts for confirmation before closing.
        
        :param event: PyQt automatically passes the event object to the function
        """
        unsaved_changes = any(self.tab_manager.editors_states().values())

        if unsaved_changes:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Icon.Warning)
            msgBox.setText(
                "Один из файлов не был сохранен, вы действительно хотите выйти?"
            )
            msgBox.setWindowTitle("Несохраненные изменения")
            msgBox.addButton('Сохранить', QMessageBox.ButtonRole.ActionRole)
            msgBox.addButton('Да', QMessageBox.ButtonRole.YesRole)
            msgBox.addButton('Нет', QMessageBox.ButtonRole.NoRole)
            
            reply = msgBox.exec()

            # 0 - Сохранить
            # 1 - Да
            # 2 - Нет
            if reply == 0:
                for editor in self.get_editors():
                    if not editor.file.saved:
                        self.saveActionHandler(editor)
                event.accept()
            elif reply == 1:
                event.accept()
            else:
                event.ignore()

    def _createActions(self):
        """
        The _createActions function creates actions for the menu bar.
        """
        self.newAction = QAction("&Создать новый файл", self)
        self.newAction.setShortcut(
            self.settings.hotkeys_settings['Создать новый файл'])
        self.newAction.triggered.connect(self.newActionHandler)

        # TODO: сделать чтобы хоть как-то работало
        self.newWindowAction = QAction("&Новое окно", self)
        self.newWindowAction.setShortcut(
            self.settings.hotkeys_settings['Новое окно'])
        self.newWindowAction.triggered.connect(self.newWindowActionHandler)

        self.openAction = QAction("&Открыть файл...", self)
        self.openAction.setShortcut(
            self.settings.hotkeys_settings['Открыть файл'])
        self.openAction.triggered.connect(self.openActionHandler)

        self.openDirectoryAction = QAction("&Открыть директорию...", self)
        self.openDirectoryAction.setShortcut(
            self.settings.hotkeys_settings['Открыть директорию'])
        self.openDirectoryAction.triggered.connect(
            self.openDirectoryActionHandler)

        self.saveAction = QAction("&Сохранить", self)
        self.saveAction.setShortcut(
            self.settings.hotkeys_settings['Сохранить'])
        self.saveAction.triggered.connect(self.saveActionHandler)

        self.saveAsAction = QAction("&Сохранить как...", self)
        self.saveAsAction.setShortcut(
            self.settings.hotkeys_settings['Сохранить как'])
        self.saveAsAction.triggered.connect(self.saveAsActionHandler)

        self.closeAction = QAction("&Закрыть файл", self)
        self.closeAction.setShortcut(
            self.settings.hotkeys_settings['Закрыть файл'])
        self.closeAction.triggered.connect(self.closeActionHandler)

        self.exitAction = QAction("&Выйти", self)
        self.exitAction.setShortcut(self.settings.hotkeys_settings['Выйти'])
        self.exitAction.triggered.connect(QCoreApplication.instance().quit)

        self.copyAction = QAction("&Копировать", self)
        self.pasteAction = QAction("&Вставить", self)
        self.cutAction = QAction("&Вырезать", self)

        self.runAction = QAction("&Запуск открытого файла", self)
        self.runAction.setShortcut(
            self.settings.hotkeys_settings['Запуск файла'])
        self.runAction.triggered.connect(self.runActionHandler)

        self.helpContentAction = QAction("&Документация", self)
        self.aboutAction = QAction("&О редакторе", self)
        self.aboutAction.setShortcut(
            self.settings.hotkeys_settings['О редакторе'])
        self.aboutAction.triggered.connect(self.aboutActionHandler)

    def _createMenuBar(self):
        """
        The _createMenuBar function creates the menu bar for the application.
        It adds actions to each of its menus, and sets icons where applicable.
        """
        menuBar = self.menuBar()

        fileMenu = menuBar.addMenu("&Файл")
        fileMenu.addAction(self.newAction)
        fileMenu.addAction(self.newWindowAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.openDirectoryAction)

        self.openRecentMenu = fileMenu.addMenu("&Открыть последние")
        self.openRecentMenu.aboutToShow.connect(self.populateOpenRecent)

        fileMenu.addSeparator()
        fileMenu.addAction(self.saveAction)
        fileMenu.addAction(self.saveAsAction)
        fileMenu.addAction(self.closeAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAction)

        editMenu = menuBar.addMenu("&Правка")
        editMenu.addAction(self.copyAction)
        editMenu.addAction(self.pasteAction)
        editMenu.addAction(self.cutAction)

        editMenu = menuBar.addMenu("&Запуск")
        editMenu.addAction(self.runAction)

        helpMenu = menuBar.addMenu("&Справка")
        helpMenu.addAction(self.aboutAction)

    def populateOpenRecent(self):
        self.openRecentMenu.clear()
        actions = []
        self.settings.refresh()
        paths = self.settings.recent_files
        for path in paths:
            action = QAction(path, self)
            action.triggered.connect(partial(self.openActionHandler, path))
            actions.append(action)
        self.openRecentMenu.addActions(actions)

    @pyqtSlot(QModelIndex)
    def openFromTree(self, index):
        ix = self.file_tree.proxy.mapToSource(index)
        path = ix.data(QFileSystemModel.Roles.FilePathRole)
        print('test')

        if not os.path.isdir(path):
            self.openActionHandler(path)

    def add_recent(self):
        new_recent = self.tab_manager.currentWidget().file.path
        self.settings.add_recent(new_recent)

    def add_tab(self, path='', is_new_file=False):
        if self.tab_manager.count() == 0:
            self.placeholder.setVisible(False)
            self.tab_manager.setVisible(True)

        return self.tab_manager.show_file(path, is_new_file)

    def remove_tab(self, idx):
        self.tab_manager.removeTab(idx)

        if self.tab_manager.count() == 0:
            self.placeholder.setVisible(True)
            self.tab_manager.setVisible(False)

    def newActionHandler(self):
        """
        The newActionHandler function creates a new file in the editor.
        """
        self.add_tab(is_new_file=True)

    def newWindowActionHandler(self):
        new_window = CustomMainWindow()

    def openActionHandler(self, file_path=None):
        """
        The openActionHandler function opens a file dialog and sets the text of the editor to the contents of 
        the chosen file. If no file is chosen, nothing happens.
        """
        if not file_path:
            file_path, _ = self.choose_file()

        if file_path:
            if self.add_tab(path=file_path):
                self.add_recent()

    def choose_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Выберите папку",
                                                     os.path.expanduser('~'))
        return directory

    def openDirectoryActionHandler(self):
        directory = self.choose_directory()
        if directory:
            self.file_tree = FileTree(directory)
            self.file_tree.doubleClicked.connect(self.openFromTree)
            self.directory_sidebar.setWidget(self.file_tree)
            self.directory_sidebar.setVisible(True)

    def openRecentActionHandler(self):
        pass

    def saveFile(self):
        """
        The saveFile function saves the contents of the editor to a file.
        It does this by writing to an open file object, which is created with
        the 'w' flag (indicating that it is opened for writing). The function 
        also sets self.unsaved_changes to False and updates self.opened_file_path 
        to reflect the new path of the saved file.
        
        :param file_path: Save the file to a specific location
        """
        editor = self.tab_manager.currentWidget()
        if editor.file.new:
            self.tab_manager.currentWidget().reload_lexer(
                editor.file.extention)
            current_tab_index = self.tab_manager.currentIndex()
            self.tab_manager.setTabText(current_tab_index, editor.file.name)
            self.add_recent()

        code = editor.text()
        code = code.replace('\r', '')
        editor.file.save(code)

    def runActionHandler(self):
        if editor := self.tab_manager.currentWidget():
            file = editor.file
            command = self.settings.run_settings.get(file.extention[1:], None)
            if command:
                self.saveActionHandler()
                command = command.replace('$file_path', file.path)
                subprocess.Popen('start /wait ' + command,
                                 shell=True,
                                 creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setText("Нет настроек запуска для данного файла. Их можно установить в файле settings.json в папке редактора.")
                msg.setWindowTitle("Ошибка")
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()

    def saveActionHandler(self, editor=None):
        """
        The saveActionHandler method is called when the user selects the save action from the file menu or presses Ctrl+S.
        """
        if not editor:
            editor = self.tab_manager.currentWidget()
        
        if editor.file.new:
            file_path, _ = self.choose_file_save()
            if file_path:
                editor.file.update_path(file_path)
                self.saveFile()
        else:
            self.saveFile()

    def saveAsActionHandler(self):
        """
        Сохранение файла с выбором пути, а так же обработчик действия "Сохранить как"
        """
        editor = self.tab_manager.currentWidget()
        file_path, _ = self.choose_file_save()
        if file_path:
            editor.file.update_path(file_path)
            self.saveFile(file_path)

    def closeActionHandler(self):
        """
        Метод закрытия файла, а так же обработчик действия "Закрыть"
        """
        self.remove_tab(self.tab_manager.currentIndex())

    def copyActionHandler(self):
        """
        Обработчик действия "Копировать"
        """
        self.tab_manager.currentWidget().copy()

    def pasteActionHandler(self):
        """
        Обработчик действия "Вставить"
        """
        self.tab_manager.currentWidget().paste()

    def cutActionHandler(self):
        """
        Обработчик действия "Вырезать"
        """
        self.tab_manager.currentWidget().cut()

    def aboutActionHandler(self):
        """
        The aboutActionHandler function displays a message box containing information about the editor.
        """
        text = "<center>" \
            "<h1>Редактор кода Light</h1>" \
            "<p>Light - это редактор кода с подсветкой синтаксиса, автодополнением и множеством других функций.</p>" \
            "<p>Он был создан в качестве курсового проекта для колледжа, и построен на виджетах PyQt6 и Qscintilla</p>" \
            f"<img src={WINDOW_ICON}>" \
            "</center>" \
            "<p>Вресия 1.0.0<br/>" \
            "Copyright &copy; Жужелица Inc.</p>"
        QMessageBox.about(self, "О программе", text)

    def choose_file(self) -> Tuple[str, str]:
        """
        The choose_file function allows the user to select a file from their computer.
        The function returns a tuple containing the path and filter used to choose the file.
        
        `path, filters = self.choose_file()`
        :return: A tuple containing the path and filter
        """
        return QFileDialog.getOpenFileName(self, 'Open file',
                                           __file__) or __file__

    def choose_file_save(self) -> Tuple[str, str]:
        return QFileDialog.getSaveFileName(self, 'Save File')
