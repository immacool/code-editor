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


class CustomMainWindow(QMainWindow):

    def __init__(self, settings):
        super(CustomMainWindow, self).__init__()

        self.setWindowIcon(QIcon(WINDOW_ICON))
        self.setGeometry(300, 300, 800, 400)
        self.setWindowTitle("Редактор кода")

        self.settings = settings
        self.theme = self.settings.default_theme

        layout = QVBoxLayout()

        frame = QFrame(self)
        frame.setLayout(layout)

        self.setCentralWidget(frame)

        self.tab_manager = TabManager(theme=self.theme)
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
        """
        Возвращает список всех редакторов.
        """
        return [
            self.tab_manager.widget(i) for i in range(self.tab_manager.count())
        ]

    def closeEvent(self, event):
        """
        Переопределение метода закрытия окна.
        """
        are_all_saved = all(e.file.saved for e in self.get_editors())

        if not are_all_saved:
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
        Описание действий, которые будут выполняться при нажатии на кнопки в меню, а так же
        инициализация горячих клавиш для них.
        """
        self.newAction = QAction("&Создать новый файл", self)
        self.newAction.setShortcut(
            self.settings.hotkeys_settings['Создать новый файл'])
        self.newAction.triggered.connect(self.newActionHandler)
        
        self.newDatabaseAction = QAction("&Создать новую базу данных", self)
        self.newDatabaseAction.setShortcut(
            self.settings.hotkeys_settings['Создать новую базу данных'])
        self.newDatabaseAction.triggered.connect(self.newDatabaseActionHandler)

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
        _createMenuBar создает меню и добавляет в них действия.
        """
        menuBar = self.menuBar()

        fileMenu = menuBar.addMenu("&Файл")
        fileMenu.addAction(self.newAction)
        fileMenu.addAction(self.newDatabaseAction)
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
        """
        Обновляет список последних открытых файлов.
        """
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
        """
        openFromTree открывает файл, который был выбран в дереве файлов.
        """
        ix = self.file_tree.proxy.mapToSource(index)
        path = ix.data(QFileSystemModel.Roles.FilePathRole)
        if not os.path.isdir(path):
            self.openActionHandler(path)

    def add_recent(self):
        """
        add_recent добавляет открытый файл в список последних файлов.
        """
        new_recent = self.tab_manager.currentWidget().file.path
        self.settings.add_recent(new_recent)

    def add_tab(self, path='', is_new_file=False):
        """
        add_tab добавляет новую вкладку в редактор.
        """
        if self.tab_manager.count() == 0:
            self.placeholder.setVisible(False)
            self.tab_manager.setVisible(True)

        return self.tab_manager.show_file(path, is_new_file)

    def remove_tab(self, idx):
        """
        remove_tab удаляет вкладку с индексом idx.
        """
        self.tab_manager.removeTab(idx)

        if self.tab_manager.count() == 0:
            self.placeholder.setVisible(True)
            self.tab_manager.setVisible(False)

    def newActionHandler(self):
        """
        The newActionHandler function creates a new file in the editor.
        """
        self.add_tab(is_new_file=True)
        
    def newDatabaseActionHandler(self):
        """
        newDatabaseActionHandler создает новую базу данных.
        """
        import sqlite3
        path = QFileDialog.getSaveFileName(
            self, "Создать базу данных", "", "База данных (*.db)")[0]
        if path:
            sqlite3.connect(path)
            self.openActionHandler(path)
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось создать базу данных")

    def newWindowActionHandler(self):
        """
        Метод создает новое окно редактора.
        """
        raise NotImplementedError

    def openActionHandler(self, file_path=None):
        """
        openActionHandler открывает диалоговое окно выбора файла и открывает его в редакторе, или
        открывает файл, который был передан в качестве аргумента.
        Так же является обработчиком действия "Открыть файл".
        """
        if not file_path:
            file_path, _ = self.choose_file()

        if file_path:
            if self.add_tab(path=file_path):
                self.add_recent()
                self.tab_manager.currentWidget().file.saved = True

    def choose_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Выберите папку",
                                                     os.path.expanduser('~'))
        return directory

    def openDirectoryActionHandler(self):
        """
        Этот метод открывает диалоговое окно выбора папки и открывает дерево файлов в док панели.
        Так же является обработчиком действия "Открыть папку".
        """
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
        saveFile сохраняет файл в зависимости от его типа: новый или уже сущестующий.
        Так же является обработчиком действия "Сохранить".
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
        """
        Запуск файла в соответствии с его расширением.
        Так же является обработчиком действия "Запустить".
        """
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
                msg.setText(
                    "Нет настроек запуска для данного файла. Их можно установить в файле settings.json в папке редактора."
                )
                msg.setWindowTitle("Ошибка")
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()

    def saveActionHandler(self, editor=None):
        """
        Сохранение файла в запрошенной директории, а так же обработчик действия "Сохранить как"
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
        Метод choose_file открывает диалоговое окно выбора файла и возвращает путь к нему.
        
        `path, filters = self.choose_file()`
        :return: Путь к файлу и фильтры
        """
        return QFileDialog.getOpenFileName(self, 'Открыть файл',
                                           __file__) or __file__

    def choose_file_save(self) -> Tuple[str, str]:
        return QFileDialog.getSaveFileName(self, 'Save File')
