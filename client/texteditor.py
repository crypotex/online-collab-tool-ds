# Code for line numbers
# https://stackoverflow.com/questions/40386194/create-text-area-textedit-with-line-number-in-pyqt-5

from PyQt4.Qt import Qt
from PyQt4.QtCore import QRect
from PyQt4.QtCore import QSize
from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QColor
from PyQt4.QtGui import QPainter
from PyQt4.QtGui import QPlainTextEdit
from PyQt4.QtGui import QTextEdit
from PyQt4.QtGui import QTextFormat
from PyQt4.QtGui import QWidget


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super(LineNumberArea, self).__init__(editor)
        self.myeditor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.myeditor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    def __init__(self, Q, outq):
        super(CodeEditor, self).__init__()
        self.lineNumberArea = LineNumberArea(self)
        self.previous_loc = (0, 0)

        self.connect(self, SIGNAL('blockCountChanged(int)'), self.update_line_number_area_width)
        self.connect(self, SIGNAL('updateRequest(QRect,int)'), self.update_line_number_area)
        self.connect(self, SIGNAL('cursorPositionChanged()'), self.highlight_current_line)

        self.update_line_number_area_width(0)
        self.Q = Q
        self.Q_out = outq

    def line_number_area_width(self):
        digits = 1
        count = max(1, self.blockCount())
        while count >= 10:
            count /= 10
            digits += 1
        space = 3 + self.fontMetrics().width('30') * digits
        return space

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):

        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(),
                                       rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super(CodeEditor, self).resizeEvent(event)

        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(),
                                              self.line_number_area_width(), cr.height()))

    def line_number_area_paint_event(self, event):
        mypainter = QPainter(self.lineNumberArea)

        mypainter.fillRect(event.rect(), Qt.lightGray)

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        # Just to make sure I use the right font
        height = self.fontMetrics().height()
        while block.isValid() and (top <= event.rect().bottom()):
            if block.isVisible() and (bottom >= event.rect().top()):
                number = str(block_number + 1)
                mypainter.setPen(Qt.black)
                mypainter.drawText(0, top, self.lineNumberArea.width(), height,
                                   Qt.AlignCenter, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

    def highlight_current_line(self):
        extra_selections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()

            line_color = QColor(Qt.yellow).lighter(160)

            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        self.setExtraSelections(extra_selections)

    def keyPressEvent(self, QKeyEvent):
        self.previous_loc = (self.textCursor().blockNumber() + 1, self.textCursor().columnNumber())
        print "Prev_blck: %s, prev_col: %s" % self.previous_loc
        return super(CodeEditor, self).keyPressEvent(QKeyEvent)


    def keyReleaseEvent(self, QKeyEvent):
        l = QKeyEvent.text()
        self.Q_out.put("%s*%s*%d*%d" % ("k", l, self.previous_loc[0], self.previous_loc[1]), timeout=1)
