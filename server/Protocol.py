class ServerProtocol:
    def __init__(self):
        self.text = []

    def handleEvent(self, eventString):
        print(eventString)
        ##TODO: kuidagi peab handlima ka lockimise protokolli, toenaoliselt teiste protokollide sees
        ##TODO: naiteks newline symboli puhul vms
        try:
            protocolType = eventString.split('*')[0]
            msg = eventString.split("*")[1]
            try:
                position = int(eventString.split('*')[3]) - 1
                linenr = int(eventString.split('*')[2]) - 1
            except IndexError:
                pass
        except IndexError:
            msg = eventString.split("*")[0]
            position = int(eventString.split('*')[2]) - 1
            linenr = int(eventString.split('*')[1]) - 1

        if protocolType == 'insert':
            return_msg = self.insertProtocol(msg,position,linenr)
        elif protocolType == 'delete':
            return_msg = self.deleteProtocol(position,linenr)
        elif protocolType == 'swap':
            return_msg = self.swapProtocol(msg,position,linenr)
        elif protocolType == 'undo':
            self.undoProtocol()
        elif protocolType == 'redo':
            self.redoProtocol()
        elif protocolType == 'open':
            self.openProtocol()
        elif protocolType == 'new':
            return_msg = self.newProtocol(msg)
        elif protocolType == 'authent':
            self.authentProtocol()
        return return_msg
    def insertProtocol(self,msg,position,linenr):
        ##olemas symbol, asukoht reas, reanumber
        self.text = self.text[linenr][:position] + msg + self.text[linenr][position:]
        return "inserted"

    def deleteProtocol(self,position,linenr):
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

    def openProtocol(self,filename):
        return "opened file"

    def newProtocol(self,filename):
        f = open(filename, 'w')
        ##save file with filename to dump directory
        self.openProtocol(filename)
        return "new file created"

    def authentProtocol(self):
        return "authenticated"