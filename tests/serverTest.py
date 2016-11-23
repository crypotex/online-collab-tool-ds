import unittest
import server.Protocol
import client.client


class TestProtocolMethods(unittest.TestCase):

    def testInsertProtocol(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def testDeleteProtocol(self):
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
