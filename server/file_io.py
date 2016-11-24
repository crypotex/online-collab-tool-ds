from os import listdir
from os.path import exists, join, abspath, dirname


class FileHandler:
    dump_dir = 'dump'

    def __init__(self):
        self.fname = ""
        self.cur_dir = dirname(abspath(__file__))

    def new_file(self, fstring):
        fs = join(self.cur_dir, self.dump_dir, fstring)
        if exists(fs):
            return "File with such name already exists", None
        else:
            self.fname = fs
            return "OK", []

    def list_files(self):
        return str(listdir(join(self.cur_dir, self.dump_dir)))

    def open_file(self, fstring):
        fs = join(self.cur_dir, self.dump_dir, fstring)
        if exists(fs):
            self.fname = fs
        else:
            return "File with such name does not exist", None
        txt = []
        try:
            with open(self.fname, "r") as f:
                for line in f:
                    txt.append(line[:-1])
        except IOError:
            return "ERRRRRRRRORTRAIN", None
        return "KK", txt

    def save(self, txt):
        try:
            with open(self.fname, "w") as f:
                for line in txt:
                    f.write(line+'\n')
        except IOError:
            return "Errrrrrrrrrortrain", None
