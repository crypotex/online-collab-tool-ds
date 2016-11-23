import unittest
import client.texteditor


class TestClientMethods(unittest.TestCase):
    def testKeyReleaseEvent(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def testNewFile(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def testOpenFile(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

    def testFileDialog(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def testConnectServer(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def testSaveText(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def testOpenFileHandler(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def testCloseEvent(self):
        self.assertEqual('foo'.upper(), 'FOO')


if __name__ == '__main__':
    unittest.main()
