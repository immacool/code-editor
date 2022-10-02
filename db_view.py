import logging
from globals import LOGGING_LEVEL

from PyQt6.Qsci import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtSql import *

import sqlite3

from editor import File

logger = logging.getLogger(__name__)
logger.setLevel(LOGGING_LEVEL)
logger.debug("Creating database connection")

class Database:
    def __init__(self, file: File | str):
        self.error_while_reading = False
        self.file = file if isinstance(file, File) else File(file)
        try:
            self.connection = sqlite3.connect(self.file.path)
            logger.debug(f"Подключение к базе данных {self.file.path} успешно")
        except sqlite3.OperationalError as e:
            logger.error(f"Не удалось открыть базу данных: {e}")
            QMessageBox.critical(None, "Ошибка", f"Не удалось открыть базу данных: {e}")
            self.error_while_reading = True
            return
        self.cursor = self.connection.cursor()
        self.current_table = self.get_tables()[0][0]
        # select current table
        self.cursor.execute(f"SELECT * FROM {self.current_table}")
        
        self.tables = self.get_tables()
        
    def get_tables(self) -> list:
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return self.cursor.fetchall()
    
    def get_columns(self, table):
        self.cursor.execute(f"PRAGMA table_info({table})")
        return self.cursor.fetchall()
    
    def execute(self, query) -> list:
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def edit_element(self, column, value, table, identifier):
        table = table if table else self.table
        command = f"UPDATE {table} SET {column} = '{value}' WHERE id = {identifier}"
        logger.debug(command)
        self.cursor.execute(command)
        self.connection.commit()
        
    def delete_element(self, table, row_id):
        self.cursor.execute(f"DELETE FROM {table} WHERE id = {row_id}")
        self.connection.commit()
        
    def add_element(self, table, values):
        self.cursor.execute(f"INSERT INTO {table} VALUES ({values})")
        self.connection.commit()


class DatabaseEditor(QTableView):
    def __init__(self, database: Database, *args, **kwargs):
        super(DatabaseEditor, self).__init__(*args, **kwargs)
        
        self.database = database
        self.file = database.file
        self.error_while_reading = False
        if database.error_while_reading:
            self.error_while_reading = True
            return
        self.model = QStandardItemModel()
        self.setModel(self.model)
        
        self.setEditTriggers(QAbstractItemView.EditTrigger.AllEditTriggers)
        
        self.update()
        
    def update(self):
        self.model.clear()
        self.model.setHorizontalHeaderLabels([column[1] for column in self.database.get_columns(self.database.tables[0][0])])
        for row in self.database.execute(f"SELECT * FROM {self.database.tables[0][0]}"):
            items = [QStandardItem(str(item)) for item in row]
            self.model.appendRow(items)
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        
    def contextMenuEvent(self, event: QContextMenuEvent):
        menu = QMenu(self)
        add_element_action = QAction("Добавить элемент", self)
        add_element_action.triggered.connect(self.add_element)
        menu.addAction(add_element_action)
        menu.exec(event.globalPos())
        
        super(DatabaseEditor, self).contextMenuEvent(event)
        
    def add_element(self):
        self.model.appendRow([QStandardItem() for _ in range(self.model.columnCount())])
        self.database.add_element(self.database.tables[0][0], ",".join(["NULL" for _ in range(self.model.columnCount())]))
        self.update()
        
        
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Delete:
            self.database.delete_element(self.model.item(self.currentIndex().row(), 0).text(), self.currentIndex().row())
            self.update()
            
        super(DatabaseEditor, self).keyPressEvent(event)
        
    def dataChanged(self, topLeft: QModelIndex, bottomRight: QModelIndex, roles: list[int]):
        element = self.model.item(topLeft.row(), topLeft.column()).text()
        column = self.model.horizontalHeaderItem(topLeft.column()).text()
        table = self.database.current_table
        identifier = topLeft.row() + 1
        self.database.edit_element(column, element, table, identifier)

        
    