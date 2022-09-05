from PyQt6.Qsci import QsciScintilla
from PyQt6.QtGui import QColor, QKeyEvent
from PyQt6.QtCore import Qt

class CustomEditor(QsciScintilla):

    def __init__(self, text, *args, key_press_handler=None, **kwargs):
        super(CustomEditor, self).__init__(*args, **kwargs)
        self.key_press_handler = key_press_handler

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
