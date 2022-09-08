import ntpath
import PyQt6.Qsci as lexers
from PyQt6.Qsci import QsciScintilla
from PyQt6.QtGui import QColor, QKeyEvent, QFont
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import Qt


class File:
    def __init__(self, file_path=None, saved=False, new=None):
        if file_path:
            self.path = file_path
            self.name = ntpath.basename(file_path)
            self.extention = ntpath.splitext(file_path)[1]
            
            self.new = False
        else:
            self.new = True
        
        self.saved = False
        
    def update_path(self, file_path):
        self.path = file_path
        self.name = ntpath.basename(file_path)
        self.extention = ntpath.splitext(file_path)[1]
    
    def save(self, data: str) -> None:
        with open(self.path, 'w', encoding='utf8') as f:
            f.write(data)
        
        self.saved = True
        if self.new:
            self.new = False

class CustomEditor(QsciScintilla):

    def __init__(self, file_path=None, *args, key_press_handler=None, **kwargs):
        super(CustomEditor, self).__init__(*args, **kwargs)
        
        self.key_press_handler = key_press_handler
        
        if file_path:
            try:
                with open(file_path, "r", encoding='utf8') as f:
                    text = f.read()
            except UnicodeDecodeError:
                msgBox = QMessageBox()
                msgBox.setIcon(QMessageBox.Icon.Critical)
                msgBox.setText(
                    "Неподдерживаемый тип файла"
                )
                msgBox.setWindowTitle("Ошибка")
                msgBox.addButton('Продолжить', QMessageBox.ButtonRole.AcceptRole)
                msgBox.exec()
            self.setText(text)
            self.file = File(file_path)
            self.reload_lexer(self.file.extention)
        else:
            self.file = File()

        self.setUtf8(True)

        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor('gainsboro'))

        self.setAutoIndent(True)
        self.setIndentationGuides(False)
        self.setIndentationsUseTabs(True)
        self.setIndentationWidth(4)

        self.setMarginsBackgroundColor(QColor("gainsboro"))
        self.setMarginLineNumbers(1, True)
        self.setMarginWidth(1, 50)

        self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsAll)
        self.setAutoCompletionCaseSensitivity(True)
        self.setAutoCompletionReplaceWord(True)
        self.setAutoCompletionUseSingle(
            QsciScintilla.AutoCompletionUseSingle.AcusAlways)
        self.setAutoCompletionThreshold(0)

        self.setFolding(QsciScintilla.FoldStyle.BoxedTreeFoldStyle)

        self.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)
        self.setMatchedBraceBackgroundColor(QColor("white"))
        self.setUnmatchedBraceForegroundColor(QColor("red"))
        
    def reload_lexer(self, file_extention):
        match file_extention[1:]:
            case 'json':
                lexer = lexers.QsciLexerJSON()
            case 'py':
                lexer = lexers.QsciLexerPython()
            case 'html':
                lexer = lexers.QsciLexerHTML()
            case 'cs':
                lexer = lexers.QsciLexerCSharp()
            case 'cpp':
                lexer = lexers.QsciLexerCPP()
            case 'java':
                lexer = lexers.QsciLexerJava()
            case 'css':
                lexer = lexers.QsciLexerCSS()
            case 'js':
                lexer = lexers.QsciLexerJavaScript()
            case _:
                lexer = None
            
        if lexer:
            font = QFont('Fira Code')
            font.setPointSize(10)
            lexer.setFont(font)
            self.setLexer(lexer)

    def changeEvent(self, event):
        """
        The changeEvent function is called whenever the user changes a text in the editor. 
        It is used to track whether there are unsaved changes in the code.
        """
        self.unsaved_changes = True

    def keyPressEvent(self, e: QKeyEvent) -> None:
        """
        The keyPressEvent function is called whenever the user presses a key. 
        If the control modifier and spacebar are pressed at the same time, 
        the autoCompleteFromAll function is called to show all possible completions.
        
        :param e:QKeyEvent: Pass the event to the parent class
        """
        if self.key_press_handler:
            self.key_press_handler()

        if e.modifiers() == Qt.KeyboardModifier.ControlModifier and e.key(
        ) == Qt.Key.Key_Space:
            self.autoCompleteFromAll()
            return

        super().keyPressEvent(e)
