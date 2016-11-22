class ServerProtocol:
    def __init__(self):
        self.text = []

    def handleEvent(self, eventString):
        print(eventString)
        ##TODO: kuidagi peab handlima ka lockimise protokolli, toenaoliselt teiste protokollide sees
        ##TODO: naiteks newline symboli puhul vms
        protocolType = eventString.split('*')[1]
        msg = eventString.split("*")[1]
        position = int(eventString.split('*')[3]) - 1
        linenr = int(eventString.split('*')[2]) - 1
        if protocolType == 'insert':
            self.insertProtocol()
        elif protocolType == 'delete':
            self.deleteProtocol()
        elif protocolType == 'swap':
            self.swapProtocol()
        elif protocolType == 'undo':
            self.undoProtocol()
        elif protocolType == 'redo':
            self.redoProtocol()
        elif protocolType == 'open':
            self.openProtocol()
        elif protocolType == 'new':
            self.newProtocol()
        elif protocolType == 'authent':
            self.authentProtocol()
        return msg
    def insertProtocol(self,msg,position,linenr):
        ##olemas symbol, asukoht reas, reanumber
        self.text = self.text[linenr][:position] + msg + self.text[linenr][position:]
        return "inserted"

    def deleteProtocol(self,msg,position,linenr):
        ##olemas symbol, asukoht reas, reanumber
        self.text[linenr][position].remove()
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

    def openProtocol(self):
        return "opened file"

    def newProtocol(self):
        return "new text created"

    def authentProtocol(self):
        return "authenticated"