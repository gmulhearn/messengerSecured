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
        string += (pubKeyPEM.decode('utf-8'))

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


def encryptMessage(msg, key):
    bytes = msg.encode('ascii')
    encryptor = PKCS1_OAEP.new(key)
    encrypted = encryptor.encrypt(bytes)

    return str(b64.b64encode(encrypted), "ascii")

def decryptMessage(msg, key):
    bytes64 = msg.encode("ascii")
    bytes = b64.b64decode(bytes64)
    decryptor = PKCS1_OAEP.new(key)
    decrypted = decryptor.decrypt(bytes)

    return str(decrypted, "ascii")


def interactive():

    while 1:
        print("1) gen a key\n2)encrypt message\n3)decrypt message\n")
        option = input("enter an option: ")

        if option == "1":
            key = RSA.generate(2048)
            print(keyToString(key, 2))
        elif option == "2":
            key = stringToPublicKey(input("enter public key: ").split("-----BEGIN RSA PRIVATE KEY-----")[0])
            print(encryptMessage(input("enter messsage to encrypt: "), key))
        elif option == "3":
            key = stringToPublicKey(input("enter private key: "))
            print(decryptMessage(input("enter message to decrypt: "), key))


# key = RSA.generate(2048)
# interactive()

f = open('keytest.txt', 'r')
string = f.read().split("-----BEGIN RSA PRIVATE KEY-----")[0]
print(string)
key = stringToPublicKey(string)

