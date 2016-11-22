# Code taken from https://www.binpress.com/tutorial/building-a-text-editor-with-pyqt-part-one/143
# Code for line numbers
# https://stackoverflow.com/questions/40386194/create-text-area-textedit-with-line-number-in-pyqt-5

import sys
from PyQt4 import QtGui
from argparse import ArgumentParser
from socket import AF_INET, SOCK_STREAM, socket

from PyQt4.Qt import QPainter
from PyQt4.Qt import QPlainTextEdit
from PyQt4.Qt import QRect
from PyQt4.Qt import QTextEdit
from PyQt4.Qt import QTextFormat
from PyQt4.Qt import QWidget
from PyQt4.Qt import Qt
from PyQt4.QtCore import QSize, SIGNAL
from PyQt4.QtGui import QColor
from PyQt4.QtGui import QInputDialog
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QPixmap

DEFAULT_SERVER_INET_ADDR = '127.0.0.1'
DEFAULT_SERVER_PORT = 49995


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super(LineNumberArea, self).__init__(editor)
        self.myeditor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.myeditor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    def __init__(self, sokk):
        super(CodeEditor, self).__init__()
        self.lineNumberArea = LineNumberArea(self)

        self.connect(self, SIGNAL('blockCountChanged(int)'), self.update_line_number_area_width)
        self.connect(self, SIGNAL('updateRequest(QRect,int)'), self.update_line_number_area)
        self.connect(self, SIGNAL('cursorPositionChanged()'), self.highlight_current_line)

        self.update_line_number_area_width(0)
        self.sokk = sokk

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

    def keyReleaseEvent(self, QKeyEvent):
        l = QKeyEvent.text()
        cursor_loc = self.textCursor()
        blck_nr = cursor_loc.blockNumber() + 1
        col_nr = cursor_loc.columnNumber()
        self.sokk.send("%s*%s*%d*%d" % ("k", l, blck_nr, col_nr))
        msg = self.sokk.recv(1024)
        print("GODRESPONSE. GOD: %s" % msg)


class Main(QtGui.QMainWindow):
    def __init__(self, server_addr, port, parent=None):
        QtGui.QMainWindow.__init__(self, parent)

        self.server_addr = server_addr
        self.port = port
        self.sokk = self.connectToServer(self.server_addr, self.port)

        self.filename = ""

        self.init_ui()

    def init_toolbar(self):
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

    def init_formatbar(self):
        self.formatbar = self.addToolBar("Format")

    def init_menubar(self):
        menubar = self.menuBar()

        menubar_file = menubar.addMenu("File")
        menubar_edit = menubar.addMenu("Edit")

        menubar_file.addAction(self.newAction)
        menubar_file.addAction(self.openAction)
        menubar_file.addAction(self.saveAction)

        menubar_edit.addAction(self.undoAction)
        menubar_edit.addAction(self.redoAction)
        # edit.addAction(self.cutAction)
        # edit.addAction(self.copyAction)
        # edit.addAction(self.pasteAction)

    def init_ui(self):
        self.text = CodeEditor(self.sokk)
        self.setCentralWidget(self.text)

        self.init_toolbar()
        self.init_formatbar()
        self.init_menubar()

        # Initialize a statusbar for the window
        self.statusbar = self.statusBar()

        # x and y coordinates on the screen, width, height
        self.setGeometry(100, 100, 1030, 800)

        self.setWindowTitle("Writer")

        self.text.setTabStopWidth(33)
        self.setWindowIcon(QtGui.QIcon("icons/icon.png"))
        self.text.cursorPositionChanged.connect(self.cursor_position)

    def cursor_position(self):

        cursor = self.text.textCursor()

        # Mortals like 1-indexed things
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber()

        self.statusbar.showMessage("Line: {} | Column: {}".format(line, col))

    def new(self):
        filename, ok = QInputDialog.getText(self, 'Choose file name', 'Enter file name:')
        if str(filename).endswith('.txt') and ok:
            self.sokk.send('%s*%s' % ('n', filename))
        else:
            warning = QMessageBox()
            warning.setIconPixmap(QPixmap("icons/Error-96.png"))
            warning.setText("The file name has to end with .txt!")
            warning.setWindowTitle("Warning")
            warning.setStandardButtons(QMessageBox.Ok)
            warning.exec_()
            # TODO: Saa serverilt vastus, kas OK v NOK

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
        with open(self.filename, "wt") as save_file:
            save_file.write(self.text.toPlainText())

    # Create connection to server
    def connectToServer(self, server_addr, port):
        print("Connecting to server")
        sokk = socket(AF_INET, SOCK_STREAM)
        sokk.connect((server_addr, port))
        return sokk


def main():
    # Parsing arguments
    parser = ArgumentParser()
    parser.add_argument('-H', '--host',
                        help='Server INET address '
                             'defaults to %s' % DEFAULT_SERVER_INET_ADDR,
                        default=DEFAULT_SERVER_INET_ADDR)
    parser.add_argument('-p', '--port', type=int,
                        help='Server TCP port, '
                             'defaults to %d' % DEFAULT_SERVER_PORT,
                        default=DEFAULT_SERVER_PORT)

    args = parser.parse_args()
    app = QtGui.QApplication(sys.argv)
    main = Main(args.host, args.port)
    main.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
