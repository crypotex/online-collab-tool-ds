from file_io import FileHandler

class ServerProtocol:
    def __init__(self):
        self.text = []
        self.file = FileHandler("")

    def handleEvent(self, eventString):
        print(type(eventString))
        if eventString.startswith('k'):
            return self.handle_kbe(eventString)
        elif eventString.startswith('n'):
            self.file = FileHandler(eventString)
        elif eventString.startswith('o'):
            self.file = FileHandler(eventString)
        else:
            raise RuntimeError("No such thing")

        ##TODO: kuidagi peab handlima ka lockimise protokolli, toenaoliselt teiste protokollide sees
        ##TODO: naiteks newline symboli puhul vms

    def handle_kbe(self, eventString):
        event = eventString.split('*')
        msg = event[1]
        blk, col = map(int, event[2:])
        if msg == '\x08':
            return_msg = self.deleteProtocol(blk, col)
        else:
            return_msg = self.insertProtocol(msg, blk, col)
        return return_msg

    def insertProtocol(self, msg, position, linenr):
        # olemas symbol, asukoht reas, reanumber
        try:
            self.text = self.text[linenr][:position] + msg + self.text[linenr][position:]
        except IndexError:
            try:
                self.text = self.text[linenr][:position] + msg
            except IndexError:
                self.text += msg
        # Need better return message - going to distribute these things to others - return the updated char/line
        return "inserted"

    def deleteProtocol(self,position,linenr):
        ##olemas symbol, asukoht reas, reanumber
        self.text.pop([linenr][position])
        return "deleted"

    def swapProtocol(self,msg,position,linenr):
        ##olemas symbol, asukoht reas, reanumber
        self.text[linenr][position] = msg
        return "swapped"

    def undoProtocol(self):
        return "undone"

    def redoProtocol(self):
        return "redone"

    def lockProtocol(self):
        return "locked"

    def authentProtocol(self):
        return "authenticated"