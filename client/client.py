# Code taken from https://www.binpress.com/tutorial/building-a-text-editor-with-pyqt-part-one/143
# Code for line numbers
# https://stackoverflow.com/questions/40386194/create-text-area-textedit-with-line-number-in-pyqt-5

import logging
import sys
import threading
import select
from PyQt4 import QtCore
from Queue import Queue
from PyQt4 import QtGui
from argparse import ArgumentParser
from socket import AF_INET, SOCK_STREAM, socket, error as so_err

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
DEFAULT_BUFFER_SIZE = 1024*1024

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
        init_txt = self.sock.recv(DEFAULT_BUFFER_SIZE)

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
                        print(s)
                        data = self.Q_out.get_nowait()
                        s.send(data)
                for s in read:
                    LOG.debug("Select: %s, %s, %s." % (read, write, error))
                    msg = s.recv(DEFAULT_BUFFER_SIZE)
                    LOG.debug("Got message from server: %s." % msg)
                    if msg.split('*')[0] == 'a':
                        self.update_text(msg)
                    else:
                        # Might use better block/timeout <- check this out
                        self.Q.put(msg, block=True, timeout=1)
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
        # txt = '[]' if self.Q.empty() else self.Q.get(timeout=2)
        if text != '[]':
            for elem in eval(text):
                self.text.appendPlainText(unicode(elem.strip(), 'utf-8'))
            self.text.setDisabled(False)
        else:
            self.text.setPlainText("")

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
            if self.Q.get(timeout=2).split('*')[0] == 'OK':
                LOG.debug("File %s created in server" % filename)
                self.filename = str(filename)
                self.setWindowTitle(self.filename)
                self.text.clear()
                self.text.setDisabled(False)
                LOG.info("Window activated for editing")
        elif not str(filename).endswith('.txt') and ok:
            LOG.debug("Filename %s doesn't end with .txt" % filename)
            warning = QMessageBox()
            warning.setIconPixmap(QPixmap("icons/Error-96.png"))
            warning.setText("The file name has to end with .txt!")
            warning.setWindowTitle("Warning")
            warning.setStandardButtons(QMessageBox.Ok)
            warning.exec_()

    def open(self):
        self.Q_out.put('%s*' % 'l', timeout=2)

        response = self.Q.get(timeout=2).split('*')
        LOG.debug("Received filenames %s from server %s" % (response, self.sock.getpeername()))

        if response[0] == 'OK':
            fileslist = eval(response[1])
            if fileslist:
                self.dialog_for_files(fileslist)

    # Create connection to server
    def connect_to_server(self, server_addr, port):
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

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(button_box)
        button_box.accepted.connect(lambda: self.open_file_handler(str(box.currentText()), dialog))
        button_box.rejected.connect(dialog.reject)

    # Sends the filename to server for open and closes the dialog box
    def open_file_handler(self, txt, dialog):
        self.Q_out.put('o*' + txt, timeout=2)
        LOG.debug("Sent filename %s to server %s to be opened" % (txt, self.sock.getpeername()))
        response = self.Q.get(timeout=2).split('*')
        if response[0] == "OK":
            self.text.clear()
            for elem in eval(response[1]):
                self.text.appendPlainText(unicode(elem.strip(), 'utf-8'))
            LOG.debug("Inserted %s into file %s" % (response[1], txt))
            self.filename = txt
            self.setWindowTitle(self.filename)
            self.text.setDisabled(False)
            LOG.info("Window activated for editing")
            dialog.hide()
            # self.handle_request()
        else:
            LOG.warning("File with such name does not exist.")
    """
    def handle_request(self):
        response = self.Q.get(timeout=2).split('*')
        while True:
            if response[0] == 'a':
                LOG.debug("Received response from server")
                self.update_text()
                response = self.Q.get(timeout=2).split('*')
            elif response[0] == 'OK' and len(response[1]) == 0:
                self.new()
            elif response[0] == 'OK' and len(response[1]) > 0:
                self.open()
            else:
                print("Whyyyy???")
    """

    def update_text(self, msg):
        data = msg.split('*')
        letter = data[1]
        blck = data[2]
        col = data[3]
        LOG.debug("Letter: %s, blck: %s, col: %s" % (letter, blck, col))
        # algus = self.text.cursor()
        cursor = self.text.textCursor()
        block_nr = cursor.blockNumber() + 1
        col_nr = cursor.columnNumber()
        LOG.debug("Line: %d, column: %d" % (block_nr, col_nr))
        #self.text.moveCursor(2, 2)
        cursor.setPosition(0)
        cursor.movePosition(QTextCursor.NextBlock, QTextCursor.MoveAnchor, n=int(blck))
        cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.MoveAnchor, n=int(col))
        self.text.setTextCursor(cursor) # sets the cursor to the new place
        LOG.debug("New! Line: %d, column: %d" % (cursor.blockNumber(), cursor.columnNumber()))
        self.text.insertPlainText(letter)
        #self.text.moveCursor(block_nr, col_nr)

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

    registerMe = QtCore.QVariant(Main)
    app = QtGui.QApplication(sys.argv)
    main_window = Main(args.host, args.port)
    main_window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
