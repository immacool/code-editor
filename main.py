import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.Qsci import *


class CustomEditor(QsciScintilla):
    def keyPressEvent(self, e: QKeyEvent):
        if e.modifiers() == Qt.KeyboardModifier.ControlModifier and e.key() == Qt.Key.Key_Space:
            self.autoCompleteFromAll()
            return
            
        super().keyPressEvent(e)
        

class CustomMainWindow(QMainWindow):
    def __init__(self):
        super(CustomMainWindow, self).__init__()

        # Window setup
        # --------------

        # 1. Define the geometry of the main window
        self.setGeometry(300, 300, 800, 400)
        self.setWindowTitle("Code editor")

        # 2. Create frame and layout
        frame = QFrame(self)
        frame.setStyleSheet("QWidget { background-color: #ffeaeaea }")
        layout = QVBoxLayout()
        frame.setLayout(layout)
        self.setCentralWidget(frame)
        
        self._createActions()
        self._createMenuBar()
        # self._createToolBars()
        
        lexer = QsciLexerPython()
        lexer.setFont(QFont('Fira Code'))

        # QScintilla editor setup
        # ------------------------

        # ! Make instance of QsciScintilla class!
        editor = CustomEditor()

        editor.setLexer(lexer)
        editor.setUtf8(True)  # Set encoding to UTF-8
        
        editor.setCaretLineVisible(True)
        editor.setCaretLineBackgroundColor(QColor('gainsboro'))
        
        editor.setAutoIndent(True)
        editor.setIndentationGuides(False)
        editor.setIndentationsUseTabs(True)
        editor.setIndentationWidth(4)
        
        editor.setMarginsBackgroundColor(QColor("gainsboro"))
        editor.setMarginLineNumbers(1, True)
        editor.setMarginWidth(1, 50)
        
        editor.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsAll)
        editor.setAutoCompletionCaseSensitivity(True)
        editor.setAutoCompletionReplaceWord(True);
        editor.setAutoCompletionUseSingle(QsciScintilla.AutoCompletionUseSingle.AcusAlways);
        editor.setAutoCompletionThreshold(0);

        editor.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch);
        editor.setMatchedBraceBackgroundColor(QColor("white"));
        editor.setUnmatchedBraceForegroundColor(QColor("blue"));
        
        self.editor = editor;
            
        layout.addWidget(editor)

        self.show()
        
        
    def _createActions(self):
        newAction = QAction("&New", self)
        newAction.setStatusTip("Create new file")
        newAction.triggered.connect(self.newActionHandler)

        openAction = QAction("&Open...", self)
        openAction.setStatusTip("Open file")
        openAction.triggered.connect(self.openActionHandler)
        
        self.saveAction = QAction("&Save", self)
        self.exitAction = QAction("&Exit", self)
        self.copyAction = QAction("&Copy", self)
        self.pasteAction = QAction("&Paste", self)
        self.cutAction = QAction("C&ut", self)
        self.helpContentAction = QAction("&Help Content", self)
        self.aboutAction = QAction("&About", self)
        
        self.newAction = newAction
        self.openAction = openAction
        
    def _createMenuBar(self):
        menuBar = self.menuBar()
        # Creating menus using a QMenu object
        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)
        fileMenu.addAction(self.newAction)
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.saveAction)
        fileMenu.addAction(self.exitAction)
        # Edit menu
        editMenu = menuBar.addMenu("&Edit")
        editMenu.addAction(self.copyAction)
        editMenu.addAction(self.pasteAction)
        editMenu.addAction(self.cutAction)
        # Help menu
        helpMenu = menuBar.addMenu(QIcon(":help-content.svg"), "&Help")
        helpMenu.addAction(self.aboutAction)
        
        
    def newActionHandler(self): pass
    def openActionHandler(self):
        file_name = self.get_file()
        with open(file_name) as f:
            self.editor.setText(f.read())
            
    def saveActionHandler(self): pass
    def exitActionHandler(self): pass
    
    def copyActionHandler(self): pass
    def pasteActionHandler(self): pass
    def cutActionHandler(self): pass
    
    def aboutActionHandler(self): pass

    def get_file(self):
        return QFileDialog.getOpenFileName(self, 'Open file', __file__)[0] or __file__
    
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    QApplication.setStyle(QStyleFactory.create('Fusion'))
    myGUI = CustomMainWindow()

    sys.exit(app.exec())