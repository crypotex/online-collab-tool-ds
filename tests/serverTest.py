import unittest
import server.Protocol
import server.file_io
import server.server


class TestProtocolMethods(unittest.TestCase):
    def __init__(self):
        self.text = []
        self.serverProt = server.Protocol.ServerProtocol()

    def testInsertProtocolLetterInsertBeginning(self):
        self.text = []
        length = len(self.text)
        self.text = self.serverProt.insertProtocol('k',0,0)
        self.assertEqual(len(self.text), length+1)

    def testInsertProtocolLetterInsertRegular(self):
        self.text = ['test\r','this is\r','stuff\r']
        length = len(self.text)
        line_length = len(self.text[2])
        self.text = self.serverProt.insertProtocol('k', 3, 2)
        self.assertEqual(len(self.text), length)
        self.assertEqual(len(self.text[2]), line_length + 1)

    def testInsertProtocolNewlineInsert(self):
        self.text = ['test\r', 'this is\r', 'stuff\r']
        length = len(self.text)
        line_length = len(self.text[2])
        self.text = self.serverProt.insertProtocol('k', 0, 3)
        self.assertEqual(len(self.text), length+1)
        self.assertEqual(len(self.text[2]), line_length)

    def testInsertProtocolNewlineBetweenInsert(self):
        self.text = ['test\r', 'this is\r', 'stuff\r']
        length = len(self.text)
        line_length = len(self.text[2]) - 4
        self.text = self.serverProt.insertProtocol('k', 3, 2)
        self.assertEqual(len(self.text), length+1)
        self.assertEqual(len(self.text[2]), 4)
        self.assertEqual(len(self.text[3]), line_length+1)

    def testDeleteProtocolLetterDelete(self):
        self.text = []
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def testDeleteProtocolLineDelete(self):
        self.text = []
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def testDeleteProtocolLineMerge(self):
        self.text = []
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def testDeleteProtocolBeginning(self):
        self.text = []
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())



    def testLockProtocol(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

    def testAuthentProtocol(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def testHandleEvent(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def testSaveText(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def testHandleKbe(self):
        self.assertEqual('foo'.upper(), 'FOO')

class TestFileIOMethods(unittest.TestCase):

    def testNewFile(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def testOpenFile(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def testSaveFile(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

class TestServerMethods(unittest.TestCase):

    def testMainThreader(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def testRunClientThread(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

if __name__ == '__main__':
    unittest.main()
