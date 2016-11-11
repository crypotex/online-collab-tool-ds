# Code taken from https://www.binpress.com/tutorial/building-a-text-editor-with-pyqt-part-one/143

import sys
from PyQt4 import QtGui


from PyQt4.Qt import QFrame
from PyQt4.Qt import QPainter
from PyQt4.Qt import QPlainTextEdit
from PyQt4.Qt import QRect
from PyQt4.Qt import QTextEdit
from PyQt4.Qt import QTextFormat
from PyQt4.Qt import QVariant
from PyQt4.Qt import QWidget
from PyQt4.Qt import Qt


class NumberBar(QWidget):
    def __init__(self, edit):
        QWidget.__init__(self, edit)

        self.edit = edit
        self.adjustWidth(1)

    def paintEvent(self, event):
        self.edit.numberbarPaint(self, event)
        QWidget.paintEvent(self, event)

    def adjustWidth(self, count):
        width = self.fontMetrics().width(unicode(count))
        if self.width() != width:
            self.setFixedWidth(width)

    def updateContents(self, rect, scroll):
        if scroll:
            self.scroll(0, scroll)
        else:
            # It would be nice to do
            # self.update(0, rect.y(), self.width(), rect.height())
            # But we can't because it will not remove the bold on the
            # current line if word wrap is enabled and a new block is
            # selected.
            self.update()


class PlainTextEdit(QPlainTextEdit):
    def __init__(self, *args):
        QPlainTextEdit.__init__(self, *args)

        self.setFrameStyle(QFrame.NoFrame)
        self.highlight()
        self.setLineWrapMode(QPlainTextEdit.NoWrap)

        # self.cursorPositionChanged.connect(self.highlight)

    def highlight(self):
        hi_selection = QTextEdit.ExtraSelection()

        hi_selection.format.setBackground(self.palette().alternateBase())
        hi_selection.format.setProperty(QTextFormat.FullWidthSelection, QVariant(True))
        hi_selection.cursor = self.textCursor()
        hi_selection.cursor.clearSelection()

        self.setExtraSelections([hi_selection])

    def numberbarPaint(self, number_bar, event):
        font_metrics = self.fontMetrics()
        current_line = self.document().findBlock(self.textCursor().position()).blockNumber() + 1

        block = self.firstVisibleBlock()
        line_count = block.blockNumber()
        painter = QPainter(number_bar)
        painter.fillRect(event.rect(), self.palette().base())

        # Iterate over all visible text blocks in the document.
        while block.isValid():
            line_count += 1
            block_top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()

            # Check if the position of the block is out side of the visible
            # area.
            if not block.isVisible() or block_top >= event.rect().bottom():
                break

            # We want the line number for the selected line to be bold.
            if line_count == current_line:
                font = painter.font()
                font.setBold(True)
                painter.setFont(font)
            else:
                font = painter.font()
                font.setBold(False)
                painter.setFont(font)

            # Draw the line number right justified at the position of the line.
            paint_rect = QRect(0, block_top, number_bar.width(), font_metrics.height())
            painter.drawText(paint_rect, Qt.AlignRight, unicode(line_count))

            block = block.next()

        painter.end()


class Main(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)

        self.filename = ""

        self.initUI()

    def initToolbar(self):
        self.newAction = QtGui.QAction(QtGui.QIcon("icons/add-file.png"), "New", self)
        self.newAction.setStatusTip("Create a new document from scratch.")
        self.newAction.setShortcut("Ctrl+N")
        self.newAction.triggered.connect(self.new)

        self.openAction = QtGui.QAction(QtGui.QIcon("icons/open-folder.svg"), "Open file", self)
        self.openAction.setStatusTip("Open existing document")
        self.openAction.setShortcut("Ctrl+O")
        self.openAction.triggered.connect(self.open)

        self.saveAction = QtGui.QAction(QtGui.QIcon("icons/save-file.png"), "Save", self)
        self.saveAction.setStatusTip("Save document")
        self.saveAction.setShortcut("Ctrl+S")
        self.saveAction.triggered.connect(self.save)

        self.toolbar = self.addToolBar("Options")

        self.toolbar.addAction(self.newAction)
        self.toolbar.addAction(self.openAction)
        self.toolbar.addAction(self.saveAction)

        self.toolbar.addSeparator()

        # Makes the next toolbar appear underneath this one
        self.addToolBarBreak()

        # self.cutAction = QtGui.QAction(QtGui.QIcon("icons/cut.png"), "Cut to clipboard", self)
        # self.cutAction.setStatusTip("Delete and copy text to clipboard")
        # self.cutAction.setShortcut("Ctrl+X")
        # self.cutAction.triggered.connect(self.text.cut)
        #
        # self.copyAction = QtGui.QAction(QtGui.QIcon("icons/copy.png"), "Copy to clipboard", self)
        # self.copyAction.setStatusTip("Copy text to clipboard")
        # self.copyAction.setShortcut("Ctrl+C")
        # self.copyAction.triggered.connect(self.text.copy)
        #
        # self.pasteAction = QtGui.QAction(QtGui.QIcon("icons/paste.png"), "Paste from clipboard", self)
        # self.pasteAction.setStatusTip("Paste text from clipboard")
        # self.pasteAction.setShortcut("Ctrl+V")
        # self.pasteAction.triggered.connect(self.text.paste)

        self.undoAction = QtGui.QAction(QtGui.QIcon("icons/undo.png"), "Undo last action", self)
        self.undoAction.setStatusTip("Undo last action")
        self.undoAction.setShortcut("Ctrl+Z")
        self.undoAction.triggered.connect(self.text.undo)

        self.redoAction = QtGui.QAction(QtGui.QIcon("icons/redo.png"), "Redo last action", self)
        self.redoAction.setStatusTip("Redo last undone thing")
        self.redoAction.setShortcut("Ctrl+Y")
        self.redoAction.triggered.connect(self.text.redo)

        # self.toolbar.addAction(self.cutAction)
        # self.toolbar.addAction(self.copyAction)
        # self.toolbar.addAction(self.pasteAction)
        self.toolbar.addAction(self.undoAction)
        self.toolbar.addAction(self.redoAction)

        self.toolbar.addSeparator()

    def initFormatbar(self):
        self.formatbar = self.addToolBar("Format")

    def initMenubar(self):
        menubar = self.menuBar()

        file = menubar.addMenu("File")
        edit = menubar.addMenu("Edit")

        file.addAction(self.newAction)
        file.addAction(self.openAction)
        file.addAction(self.saveAction)

        edit.addAction(self.undoAction)
        edit.addAction(self.redoAction)
        # edit.addAction(self.cutAction)
        # edit.addAction(self.copyAction)
        # edit.addAction(self.pasteAction)

    def initUI(self):
        self.text = PlainTextEdit(self)
        self.setCentralWidget(self.text)

        self.number_bar = NumberBar(self.text)

        self.initToolbar()
        self.initFormatbar()
        self.initMenubar()

        # Initialize a statusbar for the window
        self.statusbar = self.statusBar()

        # x and y coordinates on the screen, width, height
        self.setGeometry(100, 100, 1030, 800)

        self.setWindowTitle("Writer")

        self.text.setTabStopWidth(33)
        self.setWindowIcon(QtGui.QIcon("icons/icon.png"))
        self.text.cursorPositionChanged.connect(self.cursorPosition)

    def cursorPosition(self):

        cursor = self.text.textCursor()

        # Mortals like 1-indexed things
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber()

        self.statusbar.showMessage("Line: {} | Column: {}".format(line, col))

    def new(self):

        spawn = Main(self)
        spawn.show()

    def open(self):

        # Get filename and show only .writer files
        self.filename = QtGui.QFileDialog.getOpenFileName(self, 'Open File', ".", "(*.txt)")

        if self.filename:
            with open(self.filename, "rt") as file:
                self.text.setPlainText(file.read())

    def save(self):

        # Only open dialog if there is no filename yet
        if not self.filename:
            self.filename = QtGui.QFileDialog.getSaveFileName(self, 'Save File')

        # Append extension if not there yet
        if not self.filename.endsWith(".txt"):
            self.filename += ".txt"

        # We just store the contents of the text file along with the
        # format in html, which Qt does in a very nice way for us
        with open(self.filename, "wt") as file:
            file.write(self.text.toPlainText())


def main():
    app = QtGui.QApplication(sys.argv)

    main = Main()
    main.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
