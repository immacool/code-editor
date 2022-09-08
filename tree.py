from PyQt6.QtWidgets import QTreeView, QApplication
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtCore import QDir, QModelIndex, QSortFilterProxyModel

from globals import PROJECT_DIRECTORY


class ProxyModel(QSortFilterProxyModel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._root_path = ""

    def filterAcceptsRow(self, source_row, source_parent):
        source_model = self.sourceModel()
        if self._root_path and isinstance(source_model, QFileSystemModel):
            root_index = source_model.index(self._root_path).parent()
            if root_index == source_parent:
                index = source_model.index(source_row, 0, source_parent)
                return index.data(
                    QFileSystemModel.Roles.FilePathRole) == self._root_path
        return True

    @property
    def root_path(self):
        return self._root_path

    @root_path.setter
    def root_path(self, p):
        self._root_path = p
        self.invalidateFilter()


class FileTree(QTreeView):

    def __init__(self, path=PROJECT_DIRECTORY):
        QTreeView.__init__(self)
        
        self.dirModel = QFileSystemModel()
        self.dirModel.setRootPath(QDir.rootPath())
        self.dirModel.setFilter(QDir.Filter.Files)

        root_index = self.dirModel.index(path).parent()

        self.proxy = ProxyModel(self.dirModel)
        self.proxy.setSourceModel(self.dirModel)
        self.proxy.root_path = path

        self.setModel(self.proxy)

        proxy_root_index = self.proxy.mapFromSource(root_index)
        self.setRootIndex(proxy_root_index)
        
        self.setHeaderHidden(True)
        self.hideColumn(1)
        self.hideColumn(2)
        self.hideColumn(3)
        self.setMaximumWidth(1000)
        self.setMinimumWidth(0)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    w = FileTree()
    w.show()
    sys.exit(app.exec())