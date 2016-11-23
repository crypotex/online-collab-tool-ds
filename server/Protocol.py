from file_io import FileHandler

class ServerProtocol:
    def __init__(self):
        self.text = []
        self.file = FileHandler()

    def handleEvent(self, eventString):
        if eventString.startswith('k'):
            return self.handle_kbe(eventString)
        elif eventString.startswith('n'):
            if len(self.text) > 0:
                self.file.save(self.text)
            msg, txt = self.file.new_file(eventString[2:])
            if msg == "OK":
                self.text = txt
            return msg
        elif eventString.startswith('o'):
            if len(self.text) > 0:
                self.file.save(self.text)
            print(self.text)
            fname = eventString.strip().split("*")[-1]
            msg, txt = self.file.open_file(fname)
            if msg == "OK":
                self.text = txt
            return "%s*%s" % (msg, self.text)
        elif eventString.startswith('l'):
            return "OK*" + self.file.list_files()
        else:
            raise RuntimeError("No such thing")

    def save_text(self):
        self.file.save(self.text)

        ##TODO: kuidagi peab handlima ka lockimise protokolli, toenaoliselt teiste protokollide sees
        ##TODO: naiteks newline symboli puhul vms

    def handle_kbe(self, eventString):
        print eventString
        event = eventString.split('*')
        msg = event[1]
        print [msg]
        blk, col = map(int, event[2:])
        print blk
        print col
        if msg == '\x08':
            self.deleteProtocol(col, blk-1)
        else:
            self.insertProtocol(msg, col-1, blk-1)
        return 'a'+eventString[1:]

    def insertProtocol(self, msg, position, linenr):
        # olemas symbol, asukoht reas, reanumber
        print self.text
        ##TODO: needs fixing prolly
        try:
            self.text[linenr] = self.text[linenr][:position] + msg + self.text[linenr][position:]
        except IndexError:
            try:
                self.text[linenr] = msg
            except IndexError:
                self.text += msg
        ####TODO: line change in the middle of the line
        #if self.text[linenr][position] == '\r':
        #    self.text = self.text[:linenr] + list(self.text[linenr][:position+1]) + \
        #                list(self.text[linenr][position+1:]) + self.text[linenr+1:]
        print self.text
        # Need better return message - going to distribute these things to others - return the updated char/line
        return 'inserted'

    def deleteProtocol(self,position,linenr):
        ##olemas symbol, asukoht reas, reanumber
        print self.text
        if position == 0 and linenr != 0 and linenr != 1:
            try:
                self.text[linenr-1] += self.text[linenr][1:]
                try:
                    self.text = self.text[:linenr] + self.text[linenr+1:]
                except IndexError:
                    self.text = self.text[:linenr]
            except IndexError:
                print "On the first line"
        ###TODO: remove this after correct line exchange places added to client
        elif position == 0 and linenr == 0:
            self.text[0] = self.text[0][1:]
            print "In the beginning"
        elif linenr == 1 and position == 0:
            try:
                self.text[linenr-1] += self.text[linenr]
                try:
                    self.text = self.text[:linenr] + self.text[linenr+1:]
                except IndexError:
                    self.text = self.text[:linenr]
            except IndexError:
                print "On the first line"
        else:
            try:
                print "test1"
                self.text[linenr] = self.text[linenr][:position] + self.text[linenr][position+1:]
            except IndexError:
                print "test"
                self.text[linenr] = self.text[linenr][:position]
        print self.text
        return "deleted"
    def swapProtocol(self,msg,position,linenr):
        ##olemas symbol, asukoht reas, reanumber
        self.text[linenr][position] = msg
        return "swapped"

    def lockProtocol(self):
        return "locked"