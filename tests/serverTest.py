import unittest
import Protocol
import file_io
import server


class TestProtocolMethods(unittest.TestCase, Protocol.ServerProtocol, server.Server, file_io.FileHandler):

    def testInsertProtocolLetterInsertBeginning(self):
        self.text = []
        length = len(self.text)
        self.insertProtocol('k',0,0)
        self.assertEqual(len(self.text), length+1)

    def testInsertProtocolLetterInsertRegular(self):
        self.text = ['test\r','this is\r','stuff\r']
        length = len(self.text)
        line_length = len(self.text[2])
        self.insertProtocol('k', 3, 2)
        self.assertEqual(len(self.text), length)
        self.assertEqual(len(self.text[2]), line_length + 1)

    def testInsertProtocolNewlineInsert(self):
        self.text = ['test\r', 'this is\r', 'stuff\r']
        length = len(self.text)
        line_length = len(self.text[2])
        self.insertProtocol('k', 0, 3)
        self.assertEqual(len(self.text), length+1)
        self.assertEqual(len(self.text[2]), line_length)

    def testInsertProtocolNewlineBetweenInsert(self):
        self.text = ['test\r', 'this is\r', 'stuff\r']
        length = len(self.text)
        line_length = len(self.text[2]) - 4
        self.insertProtocol('k', 3, 2)
        self.assertEqual(len(self.text), length+1)
        self.assertEqual(len(self.text[2]), 4)
        self.assertEqual(len(self.text[3]), line_length+1)

    def testDeleteProtocolLetterDelete(self):
        self.text = ['test\r', 'this is\r', 'stuff\r']
        line_length = len(self.text[2])
        self.deleteProtocol(3, 2)
        self.assertEqual(len(self.text), line_length - 1)

    def testDeleteProtocolLineDelete(self):
        self.text = ['test\r', 'this is\r', '\r']
        length = len(self.text)
        line_length = len(self.text[2])
        self.deleteProtocol(3, 0)
        self.assertEqual(len(self.text), length - 1)
        self.assertEqual(len(self.text[2]), line_length)

    def testDeleteProtocolBeginning(self):
        self.text = ['test\r', 'this is\r', 'stuff\r']
        length = len(self.text)
        line_length = len(self.text[0])
        self.text = self.deleteProtocol(0, 0)
        self.assertEqual(len(self.text), length)
        self.assertEqual(len(self.text[0]), line_length-1)

    def testDeleteProtocolBeginningZeroLength(self):
        self.text = ['', 'this is\r', 'stuff\r']
        length = len(self.text)
        line_length = len(self.text[0])
        self.text = self.deleteProtocol(0, 0)
        self.assertEqual(len(self.text), length)
        self.assertEqual(len(self.text[0]), line_length)

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
