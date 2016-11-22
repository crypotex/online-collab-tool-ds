class ServerProtocol:
    def __init__(self):
        self.text = []

    def handleEvent(self, eventString):
        print(eventString)
        msg = eventString.split("*")[0]
        return msg