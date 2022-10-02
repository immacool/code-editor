import ntpath

import PyQt6.Qsci as lexers
from PyQt6.Qsci import QsciScintilla
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QKeyEvent
from PyQt6.QtWidgets import QMessageBox

from palettes import Theme


class File:
    DATABASE_EXTENTIONS = ('.db', '.sqlite', '.sqlite3', '.sqlitedb', '.sqlitedb3', '.sqlitedb3-shm', '.sqlitedb3-wal',)
    
    def __init__(self, file_path=None, saved=True):
        if file_path:
            self.path = file_path
            self.name = ntpath.basename(file_path)
            self.extention = ntpath.splitext(file_path)[1]
            self.new = False
        else:
            self.path = None
            self.name = None
            self.extention = None
            self.new = True
        
        self.saved = saved
        
    def update_path(self, file_path):
        """
        Метод `update_path` обновляет путь к файлу а так же поля `name` и `extention`.
        """
        self.path = file_path
        self.name = ntpath.basename(file_path)
        self.extention = ntpath.splitext(file_path)[1]
    
    def save(self, data: str) -> None:
        """
        Метод `save` сохраняет изменения в файл.
        """
        with open(self.path, 'w', encoding='utf8') as f:
            f.write(data)
        
        self.saved = True
        if self.new:
            self.new = False
            
    def __repr__(self) -> str:
        return f"File({self.path}, {self.saved})"

class CustomEditor(QsciScintilla):

    def __init__(self, theme, file_path=None, file_object=None, *args, key_press_handler=None, **kwargs):
        super(CustomEditor, self).__init__(*args, **kwargs)
        
        self.key_press_handler = key_press_handler
        self.theme = theme
        
        if file_path or file_object:
            try:
                self.file = file_object if file_object else File(file_path)
                with open(self.file.path, "r", encoding='utf8') as f:
                    text = f.read()
                self.setText(text)
                self.reload_lexer(self.file.extention)
            except UnicodeDecodeError:
                msgBox = QMessageBox()
                msgBox.setIcon(QMessageBox.Icon.Critical)
                msgBox.setText(
                    "Неподдерживаемый тип файла"
                )
                msgBox.setWindowTitle("Ошибка")
                msgBox.addButton('Продолжить', QMessageBox.ButtonRole.AcceptRole)
                msgBox.exec()
                
                self.error_while_reading = True
                return
        else:
            self.file = File()
            
        self.error_while_reading = False

        self.setUtf8(True)

        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor('#e5e5e5'))

        self.setTabIndents(True)
        self.setAutoIndent(True)
        self.setIndentationGuides(False)
        self.setIndentationsUseTabs(True)
        self.setIndentationWidth(4)

        self.setMarginsBackgroundColor(QColor("#efefef"))
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
        
        if self.theme == Theme.DARK:
            self.setCaretLineBackgroundColor(QColor('#3b3b3b'))
            
            editor_bg = QColor("#353535")
            margins_bg = QColor("#818181")
            margins_text = QColor('white')
            
            self.setFoldMarginColors(margins_bg, margins_bg)
            
            self.setMarginsForegroundColor(margins_text)
            self.setMarginsBackgroundColor(margins_bg)
            self.setPaper(editor_bg)
            

        
    def reload_lexer(self, file_extention):
        """
        Метод для перезагрузки лексера в зависимости от расширения файла.
        """
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
            
        if not lexer:
            return
        
        font = QFont('Fira Code')
        font.setPointSize(10)
        lexer.setFont(font)
        
        if self.theme == Theme.DARK:
            blue = QColor('#9ecbf2')
            magenta = QColor('#b389c9')
            
            lexer.setColor(QColor('white'), lexers.QsciLexerPython.Default)
            lexer.setColor(QColor('white'), lexers.QsciLexerPython.Identifier)
            lexer.setColor(QColor('white'), lexers.QsciLexerPython.Operator)
            
            lexer.setColor(QColor(blue), lexers.QsciLexerPython.Number)
            
            lexer.setColor(QColor('#f97578'), lexers.QsciLexerPython.Keyword)
            
            lexer.setColor(QColor('#4c6a7d'), lexers.QsciLexerPython.Comment)
            lexer.setColor(QColor(blue), lexers.QsciLexerPython.CommentBlock)
            
            lexer.setColor(QColor(blue), lexers.QsciLexerPython.SingleQuotedString)
            lexer.setColor(QColor(blue), lexers.QsciLexerPython.SingleQuotedFString)
            lexer.setColor(QColor(blue), lexers.QsciLexerPython.DoubleQuotedString)
            lexer.setColor(QColor(blue), lexers.QsciLexerPython.DoubleQuotedFString)
            
            lexer.setColor(QColor(blue), lexers.QsciLexerPython.TripleSingleQuotedFString)
            lexer.setColor(QColor(blue), lexers.QsciLexerPython.TripleSingleQuotedString)
            lexer.setColor(QColor(blue), lexers.QsciLexerPython.TripleDoubleQuotedFString)
            lexer.setColor(QColor(blue), lexers.QsciLexerPython.TripleDoubleQuotedString)

            lexer.setColor(QColor(magenta), lexers.QsciLexerPython.ClassName)            
            lexer.setColor(QColor(magenta), lexers.QsciLexerPython.FunctionMethodName)
            lexer.setColor(QColor(magenta), lexers.QsciLexerPython.Decorator)
            
            lexer.setPaper(QColor("#353535"))
            
        
        self.setLexer(lexer)

    def changeEvent(self, event):
        """
        The changeEvent function is called whenever the user changes a text in the editor. 
        It is used to track whether there are unsaved changes in the code.
        """
        self.file.saved = False
        print(self.file)

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
