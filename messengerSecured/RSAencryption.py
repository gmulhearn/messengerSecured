from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import binascii
import base64 as b64

# convert int to base64
def integerToBase64(num):
    bytes = num.to_bytes((num.bit_length() // 8) + 1, byteorder='big')
    return str(b64.b64encode(bytes), "utf-8")

#convert base64 to int
def base64ToInteger(string):
    bytes = string.encode("utf-8")
    decoded = b64.b64decode(bytes)
    return int.from_bytes(decoded, byteorder='big')

# mode, 0 = public only, 1 = private only, 2 = all
def keyToString(key, mode):

    string = ""

    publicKey = key.publickey()
    pubKeyPEM = publicKey.exportKey()
    if mode != 1:
        string += (pubKeyPEM.decode('ascii'))

    if key.has_private and mode != 0:
        privateKeyPEM = key.exportKey()
        string +=(privateKeyPEM.decode('ascii'))

    return string

def exportKeyToFile(key, path, name):
    f = open(path + name + ".pem", 'w')
    f.write(key.exportKey('PEM'))
    f.close()

def importKeyFromFile(path):
    f = open(path, 'r')
    return RSA.importKey(f.read())

def stringToPublicKey(string):
    return RSA.importKey(string)
