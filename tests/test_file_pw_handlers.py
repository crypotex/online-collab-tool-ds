import unittest
from os.path import join, abspath, dirname, exists
from os import remove

from server.file_io import FileHandler


class TestFilePasswHandlers(unittest.TestCase):
    def setUp(self):
        tmp = dirname(dirname(abspath(__file__)))
        self.test_dir = join(tmp, 'server')
        self.fh = FileHandler()
        # This is stupid, but I am in a hurry. No time to setup proper test environment ... :(
        self.quickfix = self.fh.pwdb.db

    def test_default_is_there(self):
        self.assertTrue(len(self.fh.list_files()) > 0,
                        "File list does not have any files -> default.txt should be there")

    def test_pwhandler(self):
        self.assertTrue(len(self.fh.pwdb.db.keys()) > 0, "Should have atleast one key in db (default)")
        self.assertTrue(self.fh.pwdb.pw_correct('default.txt', "") == "OK", "default.txt has password no passwd")
        self.assertTrue(self.fh.pwdb.new_pw('default.txt', 'kala') == "OK", "New Password not set.")
        self.assertTrue(self.fh.pwdb.pw_correct('default.txt', "kala") == "OK", "default.txt does not accept valid pw.")
        self.assertTrue(self.fh.pwdb.pw_correct('default.txt', "kkkk") == "Passwords don't match.",
                        "default.txt does accept valid pw.")
        # Stupid test case but works for now (Files should not contain : anyway) - no error handling for this
        self.assertTrue(self.fh.pwdb.pw_correct('twgwrgawrgwr::agrwagr','fewfw') == "No such file",
                        "Finds a file that is not there")
        self.assertTrue(self.fh.pwdb.new_pw('twgwrgawrgwr::agrwagr', "kala") == "No such file",
                        "Lets update password for non-existing file")

    def test_filehandler(self):
        self.assertTrue(len(self.fh.list_files()) > 0,
                        "File list does not have any files -> default.txt should be there")
        self.assertTrue(self.fh.new_file('default.txt', '') == ("File with such name already exists", None),
                        "Can create file that is already there")
        self.assertTrue(self.fh.new_file('test1.txt', 'kala') == ("OK", []), "Cannot create file with password")
        self.assertTrue(self.fh.new_file('test2.txt') == ("OK", []), "Cannot create file with empty pw.")
        t = [('test1.txt', 'kala'), ('test2.txt', '')]
        init_txt = ['tere\r', 'kala\r']
        for i, ipw in t:
            with open(join(self.test_dir, i), 'w') as f:
                for line in init_txt:
                    f.write(line)
            msg, text = self.fh.open_file(i, ipw)
            if i == "test1.txt":
                print(msg)
                self.assertEquals(msg, "OK", "Cannot open a file with password")
            else:
                self.assertEquals(msg, "OK", "Cannot open a file without pw when there is no pw")
            self.assertEquals(text, init_txt, "Strings don't mach that were written by filehandler.")



    def test_consistency(self):
        pass

    def tearDown(self):
        t = ['test1.txt', 'test2.txt', 'test3.txt']
        for i in t:
            ti = join(self.test_dir, i)
            if exists(ti):
                remove(ti)
        self.fh.pwdb.db = self.quickfix
        self.fh.pwdb.save()




