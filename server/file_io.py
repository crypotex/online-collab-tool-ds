from os import listdir
from os.path import exists, join, abspath, dirname

from PasswordHandler import PasswordHandler


class FileHandler:
    dump_dir = 'dump'

    def __init__(self):
        self.fname = ""
        self.cur_dir = dirname(abspath(__file__))
        self.pwdb = PasswordHandler()

    def new_file(self, fstring, passw = ""):
        fs = join(self.cur_dir, self.dump_dir, fstring)
        if exists(fs):
            return "File with such name already exists", None
        else:
            self.fname = fs
            self.pwdb.new_pw(fs, passw)
            return "OK", []

    def list_files(self):
        return listdir(join(self.cur_dir, self.dump_dir))

    def open_file(self, fstring, passw = ""):
        fs = join(self.cur_dir, self.dump_dir, fstring)
        if fs in self.pwdb.db:
            if self.pwdb.pw_correct(fs, passw):
                self.fname = fs
            else:
                return "Password Incorrect", None
        else:
            print(fstring)
            print(self.pwdb.db)
            return "File with such name does not exist", None
        txt = []
        try:
            with open(self.fname, "r") as f:
                for line in f:
                    txt.append(line)
        except IOError:
            return "ERRRRRRRRORTRAIN", None
        return "OK", txt

    def save(self, txt):
        self.pwdb.save()
        try:
            with open(self.fname, "w") as f:
                for line in txt:
                    f.write(line)
        except IOError:
            return "Errrrrrrrrrortrain", None
