from os import listdir
from os.path import exists


class FileHandler:
    dump_dir = 'dump'

    def __init__(self):
        self.fname = ""

    def new_file(self, fstring):
        fs = "%s/%s" % (self.dump_dir, fstring)
        if exists(fs):
            return "File with such name already exists", None
        else:
            self.fname = fs
            return "OK", []

    def list_files(self):
        return str(listdir(self.dump_dir))

    def open_file(self, fstring):
        fs = "%s/%s" % (self.dump_dir, fstring)
        if exists(fs):
            return "File with such name already exists", None
        else:
            self.fname = fs
        txt = []
        try:
            with open(self.fname, "r") as f:
                for line in f:
                    txt.append(line)
        except IOError:
            return "ERRRRRRRRORTRAIN", None
        return "OK", txt

    def save(self, txt):
        try:
            with open(self.fname, "w") as f:
                for line in txt:
                    f.write(line)
        except IOError:
            return "Errrrrrrrrrortrain", None
