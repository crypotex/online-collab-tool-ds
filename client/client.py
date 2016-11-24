# Code taken from https://www.binpress.com/tutorial/building-a-text-editor-with-pyqt-part-one/143

import logging
import sys
import threading
import select
from PyQt4 import QtCore
from Queue import Queue
from PyQt4 import QtGui
from argparse import ArgumentParser
from socket import AF_INET, SOCK_STREAM, socket, error as so_err

from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QComboBox
from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QDialogButtonBox
from PyQt4.QtGui import QInputDialog
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QPixmap
from PyQt4.QtGui import QTextCursor
from PyQt4.QtGui import QVBoxLayout

from texteditor import CodeEditor

DEFAULT_SERVER_INET_ADDR = '127.0.0.1'
DEFAULT_SERVER_PORT = 49995
DEFAULT_BUFFER_SIZE = 1024 * 1024

FORMAT = '%(asctime)-15s %(levelname)s %(threadName)s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
LOG = logging.getLogger()


class Main(QtGui.QMainWindow):
    def __init__(self, server_addr, port, parent=None):
        QtGui.QMainWindow.__init__(self, parent)

        LOG.info("Client started. ")

        self.server_addr = server_addr
        self.port = port
        self.sock = self.connect_to_server(self.server_addr, self.port)

        self.filename = "Untitled"
        self.connect(self, SIGNAL('add'), self.update_text)
        self.connect(self, SIGNAL('open'), self.open_file_handler)
        self.connect(self, SIGNAL('new'), self.new_file_handler)
        self.connect(self, SIGNAL('delete'), self.delete_text)
        init_txt = self.sock.recv(DEFAULT_BUFFER_SIZE)
        self.dialog = QDialog()

        self.Q = Queue(maxsize=1024)
        self.Q_out = Queue(maxsize=1024)
        self.MAGIC = threading.Event()
        threading.Thread(target=self.run_listener_thread, name="listener").start()
        self.init_ui(init_txt)

    def run_listener_thread(self):
        LOG.info("New listener thread initialized with :%s socket." % self.sock)
        while not self.MAGIC.isSet():
            try:
                read, write, error = select.select([self.sock], [self.sock], [])
                if not self.Q_out.empty():
                    LOG.debug("Select: %s, %s, %s." % (read, write, error))
                    for s in write:
                        data = self.Q_out.get_nowait()
                        s.send(data.encode('utf-8'))
                for s in read:
                    msg = s.recv(DEFAULT_BUFFER_SIZE).decode('utf-8').split('*')
                    c = 0
                    while c < len(msg):
                        LOG.debug("Got message from server: %s." % msg)
                        if len(msg[c]) == 1:
                            if msg[c] == 'd':
                                self.emit(SIGNAL('delete'), "*".join(msg[c:c+3]))
                                c += 3
                            elif msg[c] == 'a':
                                self.emit(SIGNAL('add'), "*".join(msg[c:c+4]))
                                c += 4
                            elif msg[c] == 'f':
                                self.Q.put("*".join(msg[c:c+2]))
                                c += 2
                            else:
                                LOG.debug("Response unknown: %s" % msg)
                                break
                        elif msg[c] == 'OK':
                            self.emit(SIGNAL('new'), "*".join(msg[c:c+2]))
                            c += 2
                        elif msg[c] == 'KK':
                            self.emit(SIGNAL('open'), "*".join(msg[c:c+3]), self.dialog)
                            c += 3
                        else:
                            # Might use better block/timeout <- check this out
                            self.Q.put("*".join(msg[c:c+3]), block=True, timeout=1)
                            c += 3
                            LOG.debug("Response: %s added to Q." % msg)
            except so_err as e:
                LOG.error("Socket error: %s" % (str(e)))
                break
            except KeyboardInterrupt:
                LOG.exception('Ctrl+C - terminating server')
                break
        if self.sock is not None:
            try:
                self.sock.close()
            except so_err:
                LOG.debug("Client disconnected.")

    def init_toolbar(self):
        self.newAction = QtGui.QAction(QtGui.QIcon("icons/add-file.png"), "New", self)
        self.newAction.setStatusTip("Create a new document from scratch.")
        self.newAction.setShortcut("Ctrl+N")
        self.newAction.triggered.connect(self.new)

        self.openAction = QtGui.QAction(QtGui.QIcon("icons/open-folder.svg"), "Open file", self)
        self.openAction.setStatusTip("Open existing document")
        self.openAction.setShortcut("Ctrl+O")
        self.openAction.triggered.connect(self.open)

        self.toolbar = self.addToolBar("Options")

        self.toolbar.addAction(self.newAction)
        self.toolbar.addAction(self.openAction)
        self.toolbar.addSeparator()

    def init_formatbar(self):
        self.formatbar = self.addToolBar("Format")

    def init_menubar(self):
        menubar = self.menuBar()

        menubar_file = menubar.addMenu("File")
        menubar_file.addAction(self.newAction)
        menubar_file.addAction(self.openAction)

    def init_ui(self, text):
        self.text = CodeEditor(self.Q, self.Q_out)
        self.setCentralWidget(self.text)

        # window is disabled until new file is made
        # or some file is opened
        self.text.setDisabled(True)

        for elem in eval(text):
            self.text.appendPlainText(elem.strip())
        self.text.setDisabled(False)

        self.init_toolbar()
        self.init_formatbar()
        self.init_menubar()

        # Initialize a statusbar for the window
        self.statusbar = self.statusBar()

        self.setFixedSize(1030, 800)

        # center the window
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        self.setWindowTitle(self.filename)

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
            self.Q_out.put('%s*%s' % ('n', filename), timeout=2)
            LOG.debug("Sent filename %s to server %s to be created" % (filename, self.sock.getpeername()))
        elif not str(filename).endswith('.txt') and ok:
            LOG.debug("Filename %s doesn't end with .txt" % filename)
            warning = QMessageBox()
            warning.setIconPixmap(QPixmap("icons/Error-96.png"))
            warning.setText("The file name has to end with .txt!")
            warning.setWindowTitle("Warning")
            warning.setStandardButtons(QMessageBox.Ok)
            warning.exec_()

    def new_file_handler(self, response):
        response = response.split('*')
        if response[0] == 'OK':
            LOG.debug("File %s created in server" % response[1])
            self.filename = str(response[1])
            self.setWindowTitle(self.filename)
            self.text.clear()
            self.text.setDisabled(False)
            LOG.info("Window activated for editing")

    def open(self):
        self.Q_out.put('%s*' % 'l', timeout=2)

        response = self.Q.get(timeout=2).split('*')
        LOG.debug("Received filenames %s from server %s" % (response, self.sock.getpeername()))

        if response[0] == 'f':
            fileslist = eval(response[1])
            if fileslist:
                self.dialog_for_files(fileslist)

    # Opens a dialog which shows the files in server and where client can choose the file to be opened
    def dialog_for_files(self, fileslist):
        layout = QVBoxLayout()

        self.dialog.setLayout(layout)
        self.dialog.setWindowTitle('Open file from the list')
        self.dialog.setMinimumSize(200, 80)
        self.dialog.setGeometry(400, 400, 300, 80)
        self.dialog.show()

        box = QComboBox()
        box.clear()
        box.addItems(fileslist)

        layout.addWidget(box)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(button_box)
        button_box.accepted.connect(lambda: self.send_filename_to_server(str(box.currentText())))
        button_box.rejected.connect(self.dialog.reject)

    # Sends the filename to server for opening
    def send_filename_to_server(self, txt):
        self.Q_out.put('o*' + txt, timeout=2)
        LOG.debug("Sent filename %s to server %s to be opened" % (txt, self.sock.getpeername()))

    #  Closes the dialog box, enters text inside textbox and sets filename
    def open_file_handler(self, response, dialog):
        response = response.split('*')
        if response[0] == "KK":
            self.text.clear()
            for elem in eval(response[2]):
                self.text.appendPlainText(unicode(elem.strip(), 'utf-8'))
                LOG.debug("Inserted %s into file %s" % (elem, response[1]))
            self.filename = response[1]
            self.setWindowTitle(self.filename)
            self.text.setDisabled(False)
            LOG.info("Window activated for editing")
            dialog.hide()
        else:
            LOG.warning("File with such name does not exist.")

    def update_text(self, msg):
        data = msg.split('*')
        letter = data[1]
        blck = int(data[2]) - 1
        col = int(data[3])

        # old place for cursor
        cursor = self.text.textCursor()
        block_nr = cursor.blockNumber()
        col_nr = cursor.columnNumber()

        # move cursor to new position to enter the letter
        cursor.setPosition(0)
        cursor.movePosition(QTextCursor.NextBlock, QTextCursor.MoveAnchor, n=blck)
        cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.MoveAnchor, n=col)
        cursor.insertText(letter)

        # move the cursor back to the original place for the user
        cursor.setPosition(0)
        cursor.movePosition(QTextCursor.NextBlock, QTextCursor.MoveAnchor, n=block_nr)
        cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.MoveAnchor, n=col_nr)
        self.text.setTextCursor(cursor)

    def delete_text(self, msg):
        data = msg.split('*')
        blck = int(data[1]) - 1
        col = int(data[2])

        # old place for cursor
        cursor = self.text.textCursor()
        block_nr = cursor.blockNumber()
        col_nr = cursor.columnNumber()

        # move cursor to new position to enter the letter
        cursor.setPosition(0)
        cursor.movePosition(QTextCursor.NextBlock, QTextCursor.MoveAnchor, n=blck)
        cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.MoveAnchor, n=col)
        cursor.deletePreviousChar()

        # move the cursor back to the original place for the user
        cursor.setPosition(0)
        cursor.movePosition(QTextCursor.NextBlock, QTextCursor.MoveAnchor, n=block_nr)
        cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.MoveAnchor, n=col_nr)
        self.text.setTextCursor(cursor)

    # Create connection to server
    def connect_to_server(self, server_addr, port):
        sokk = socket(AF_INET, SOCK_STREAM)
        sokk.connect((server_addr, port))
        LOG.info("Connected to server: %s" % ((server_addr, port),))
        return sokk

    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Confirm exit', "Are you sure you want to exit?",
                                           QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            event.accept()
            LOG.info("Killing thread.")
            self.MAGIC.set()
            LOG.debug("Thread killed.")
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

    QtCore.QVariant(Main)
    app = QtGui.QApplication(sys.argv)
    main_window = Main(args.host, args.port)
    main_window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
