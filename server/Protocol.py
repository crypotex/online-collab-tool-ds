from file_io import FileHandler
import logging

FORMAT = '%(asctime)-15s %(levelname)s %(threadName)s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
LOG = logging.getLogger()


class ServerProtocol:
    def __init__(self):
        self.text = []
        self.file = FileHandler()

    def handle_event(self, eventString):
        if eventString.startswith('k'):
            return 'a', self.handle_kbe(eventString)
        elif eventString.startswith('n'):
            fname = eventString.strip().split("*")[-1]
            if len(self.text) > 0:
                self.file.save(self.text)
            msg, txt = self.file.new_file(fname)
            if msg == "OK":
                self.text = txt
            return 'b', "%s*%s" % (msg, fname)
        elif eventString.startswith('o'):
            if len(self.text) > 0:
                self.file.save(self.text)
            fname = eventString.strip().split("*")[-1]
            msg, txt = self.file.open_file(fname)
            if msg == "KK":
                self.text = txt
            return 'b', "%s*%s*%s" % (msg, fname, self.text)
        elif eventString.startswith('l'):
            return 's', "%s*%s" % ("f", self.file.list_files())
        else:
            raise RuntimeError("No such thing")

    def save_text(self):
        self.file.save(self.text)

    def handle_kbe(self, eventString):
        event = eventString.split('*')
        msg = event[1]
        blk, col = map(int, event[2:])
        if msg == 'backspace':
            self.delete_protocol(col + 1, blk - 1)
            return 'd*%s*%s' % (blk, col)
        else:
            self.insert_protocol(msg, col, blk - 1)
            return 'a' + eventString[1:]

    def insert_protocol(self, msg, position, linenr):

        LOG.debug("File before typing: %s" % str(self.text))
        try:
            self.text[linenr] = self.text[linenr][:position] + msg + self.text[linenr][position:]
        except IndexError:
            try:
                self.text[linenr] = msg
            except IndexError:
                self.text += msg
        LOG.debug("File after typing: %s" % str(self.text))

    def delete_protocol(self, position, linenr):
        LOG.debug("Line: %s, col: %s" % (linenr, position))
        LOG.debug("len text: %s" % len(self.text))
        ##olemas symbol, asukoht reas, reanumber
        LOG.debug("File before deleting: %s" % str(self.text))
        if position == 0 and linenr != 0 and linenr != 1:
            try:
                self.text[linenr - 1] += self.text[linenr][1:]
                try:
                    self.text = self.text[:linenr] + self.text[linenr + 1:]
                except IndexError:
                    self.text = self.text[:linenr]
            except IndexError:
                LOG.debug("On the first line")
        elif position == 0 and linenr == 0:
            self.text[0] = self.text[0][1:]
            LOG.debug("In the beginning")
        elif linenr == 1 and position == 0:
            try:
                self.text[linenr - 1] += self.text[linenr]
                try:
                    self.text = self.text[:linenr] + self.text[linenr + 1:]
                except IndexError:
                    self.text = self.text[:linenr]
            except IndexError:
                LOG.debug("On the first line")
        else:
            try:
                self.text[linenr] = self.text[linenr][:position - 2] + self.text[linenr][position:]
                LOG.debug("%s, %d" % (self.text, linenr))
            except IndexError:
                self.text[linenr] = self.text[linenr][:position - 2]
        LOG.debug("File after deleting: %s" % str(self.text))
