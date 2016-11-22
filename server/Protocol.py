class ServerProtocol:
    def __init__(self):
        self.text = []

    def handleEvent(self, eventString):
        print(eventString)
        ##TODO: kuidagi peab handlima ka lockimise protokolli, tõenäoliselt teiste protokollide sees
        ##TODO: näiteks newline sümboli puhul vms
        protocolType = eventString.split('*')[1]
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
        msg = eventString.split("*")[1]
        return msg
    def insertProtocol(self):
        ##olemas sümbol, asukoht reas, reanumber
        return None

    def deleteProtocol(self):
        ##olemas sümbol, asukoht reas, reanumber
        return None

    def swapProtocol(self):
        ##olemas sümbol, asukoht reas, reanumber
        return None

    def undoProtocol(self):
        return None

    def redoProtocol(self):
        return None

    def lockProtocol(self):
        return None

    def openProtocol(self):
        return None

    def newProtocol(self):
        return None

    def authentProtocol(self):
        return None