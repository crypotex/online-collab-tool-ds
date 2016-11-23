from os.path import join, abspath, dirname


class PasswordHandler():
    def __init__(self):
        self.db = {}
        self.db_file = join(abspath(dirname(__file__)), 'pw_db.txt')
        try:
            with open(self.db_file, 'r') as f:
                for line in f:
                    line = line.strip().split(':')
                    self.db[line[0]] = line[1]
        except IOError as ioe:
            print("Errortrain with error: %s." % str(ioe))

    def save(self):
        try:
            # We overwrite previous file, doesn't mather much, because files are so small and update happens
            # before client disconnects
            with open(self.db_file) as f:
                for fname, pw in self.db.items():
                    prep_s = "%s:%s" % (fname, pw)
                    f.write(prep_s)
        except IOError as ioe:
            print("Errortrain with error: %s." % str(ioe))

    def pw_correct(self, fname, pw=""):
        if fname not in self.db.keys():
            return "No such file"
        else:
            if self.db[fname] == pw:
                return "OK"
            else:
                return "Passwords don't match."

    def new_pw(self, fname, pw):
        if fname in self.db.keys():
            self.db[fname] = pw
            return "OK"
        else:
            return "No such file"
