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
        self.setWindowTitle("QScintilla Test")

        # 2. Create frame and layout
        frame = QFrame(self)
        frame.setStyleSheet("QWidget { background-color: #ffeaeaea }")
        layout = QVBoxLayout()
        frame.setLayout(layout)
        self.setCentralWidget(frame)
        
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
        
    
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    QApplication.setStyle(QStyleFactory.create('Fusion'))
    myGUI = CustomMainWindow()

    sys.exit(app.exec())
