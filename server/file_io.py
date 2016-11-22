from os import listdir
from os.path import exists


class FileHandler:
    dump_dir = 'dump'

    def __init__(self):
        self.fname = ""

    def new_file(self, filestring):
        fs = "%s/%s" % (self.dump_dir, filestring)
        if exists(fs):
            return "File with such name already exists"
        else:
            self.fname = fs
        return self.__open_file()

    def __open_file(self):
        try:
            with open(self.fname, 'w') as f:
                f.write("")
            return "1"
        except IOError:
            return "0"

    def list_files(self):
        return str(listdir(self.dump))

    def open_file(self, filestring):
        fs = "%s/%s" % (self.dump_dir, filestring)
        if exists(fs):
            return "File with such name already exists"
        else:
            self.fname = fs
        return self.__open_file()

