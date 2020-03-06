import unittest
import RSAencryption
from Crypto.PublicKey import RSA


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, True)

class RSATests(unittest.TestCase):

    def testPublicKeyImportExport(self):
        key = RSA.generate(2048)
        key1string = RSAencryption.keyToString(key, 0)
        key2 = RSAencryption.stringToPublicKey(key1string)
        key2string = RSAencryption.keyToString(key2, 0)
        self.assertEqual(key1string, key2string)


if __name__ == '__main__':
    unittest.main()

