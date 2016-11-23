# Code taken from https://www.binpress.com/tutorial/building-a-text-editor-with-pyqt-part-one/143
# Code for line numbers
# https://stackoverflow.com/questions/40386194/create-text-area-textedit-with-line-number-in-pyqt-5

import logging
import sys
from PyQt4 import QtGui
from argparse import ArgumentParser
from socket import AF_INET, SOCK_STREAM, socket

from PyQt4.QtGui import QComboBox
from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QInputDialog
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QPixmap
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QVBoxLayout

from texteditor import CodeEditor

DEFAULT_SERVER_INET_ADDR = '127.0.0.1'
DEFAULT_SERVER_PORT = 49995

FORMAT = '%(asctime)-15s %(levelname)s %(threadName)s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
LOG = logging.getLogger()


class Main(QtGui.QMainWindow):
    def __init__(self, server_addr, port, parent=None):
        QtGui.QMainWindow.__init__(self, parent)

        LOG.info("Client started. ")

        self.server_addr = server_addr
        self.port = port
        self.sock = self.connectToServer(self.server_addr, self.port)

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

        self.undoAction = QtGui.QAction(QtGui.QIcon("icons/undo.png"), "Undo last action", self)
        self.undoAction.setStatusTip("Undo last action")
        self.undoAction.setShortcut("Ctrl+Z")
        self.undoAction.triggered.connect(self.text.undo)

        self.redoAction = QtGui.QAction(QtGui.QIcon("icons/redo.png"), "Redo last action", self)
        self.redoAction.setStatusTip("Redo last undone thing")
        self.redoAction.setShortcut("Ctrl+Y")
        self.redoAction.triggered.connect(self.text.redo)

        self.toolbar.addAction(self.undoAction)
        self.toolbar.addAction(self.redoAction)

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

    def init_ui(self):
        self.text = CodeEditor(self.sock)
        self.setCentralWidget(self.text)

        self.init_toolbar()
        self.init_formatbar()
        self.init_menubar()

        # Initialize a statusbar for the window
        self.statusbar = self.statusBar()

        self.setFixedSize(1030, 800)
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
            self.sock.sendall('%s*%s' % ('n', filename))
            LOG.debug("Sent filename %s to server %s to be created" % (filename, self.sock.getpeername()))
            if self.sock.recv(1024).split('*')[0] == 'OK':
                LOG.debug("File %s created in server" % filename)
        elif not str(filename).endswith('.txt') and ok:
            LOG.debug("Filename %s doesn't end with .txt" % filename)
            warning = QMessageBox()
            warning.setIconPixmap(QPixmap("icons/Error-96.png"))
            warning.setText("The file name has to end with .txt!")
            warning.setWindowTitle("Warning")
            warning.setStandardButtons(QMessageBox.Ok)
            warning.exec_()

    def open(self):
        self.sock.sendall('%s*' % 'l')

        response = self.sock.recv(1024)
        LOG.debug("Received filenames %s from server %s" % (response, self.sock.getpeername()))

        if response:
            fileslist = eval(response)
            if fileslist:
                self.dialog_for_files(fileslist)

                # TODO: Serverilt saab vastuse, kui fail olemas, aga lugemine ja n2itamine aknas puudu

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
        sokk = socket(AF_INET, SOCK_STREAM)
        sokk.connect((server_addr, port))
        LOG.info("Connected to server: %s" % ((server_addr, port),))
        return sokk

    # Opens a dialog which shows the files in server and where client can choose the file to be opened
    def dialog_for_files(self, fileslist):
        layout = QVBoxLayout()

        dialog = QDialog(self)
        dialog.setLayout(layout)
        dialog.setWindowTitle('Choose file from the list')
        dialog.setMinimumSize(200, 80)
        dialog.setGeometry(400, 400, 300, 80)
        dialog.show()

        box = QComboBox()
        box.clear()
        box.addItems(fileslist)

        layout.addWidget(box)

        button = QPushButton("OK")
        layout.addWidget(button)
        button.clicked.connect(lambda: self.open_file_handler(str(box.currentText()), dialog))

    # Sends the filename to server for open and closes the dialog box
    def open_file_handler(self, txt, dialog):
        self.sock.sendall('o*' + txt)
        LOG.debug("Sent filename %s to server %s to be opened" % (txt, self.sock.getpeername()))
        response = self.sock.recv(1024).split('*')
        if response[0] == "OK":
            self.text.clear()
            for elem in eval(response[1]):
                self.text.appendPlainText(unicode(elem.strip(), 'utf-8'))
            LOG.debug("Inserted %s into file %s" % (response[1], txt))
            dialog.hide()
            self.updateText()
        else:
            LOG.warning("File with such name does not exist.")

    def updateText(self):
        # algus = self.text.cursor()
        cursor = self.text.textCursor()
        response = self.sock.recv(1024).split('*')
        while response[0] == 'a':
            block_nr = cursor.blockNumber() + 1
            col_nr = cursor.columnNumber()
            self.text.moveCursor(2, 2)
            self.text.insertPlainText("tere")
            self.text.moveCursor(block_nr, col_nr)
            response = self.sock.recv(1024).split('*')
            # self.text.moveCursor(algus)

    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Confirm exit', "Are you sure you want to exit?",
                                           QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


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
    main_window = Main(args.host, args.port)
    main_window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
