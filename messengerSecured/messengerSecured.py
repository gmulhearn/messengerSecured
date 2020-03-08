from fbchat import Client, log
from fbchat.models import *
import Crypto
import RSAencryption

# todo:
# add list of pending requests to verify responses
#


key = 0


class Bot(Client):
    global key

    def onMessage(self, author_id=None, message_object=None, thread_id=None,
                  thread_type=ThreadType.USER, **kwargs):

        self.markAsRead(author_id)

        if author_id != self.uid:

            msgText = message_object.text

            print("Message {} received from {} in {}".format(msgText, self.fetchUserInfo(author_id).get(author_id).name,
                                                             thread_type))

            if str(msgText).startswith("-----BEGIN PUBLIC KEY-----"):
                # handle errors
                self.processKeyReturn(author_id, thread_type, thread_type, msgText)

            if str(msgText) == "-----PUBLIC KEY REQUEST-----":
                self.respondKeyRequest(author_id, thread_id, thread_type)
                return

            try:
                decryptedMsg = RSAencryption.decryptMessage(msgText, key)
                print("decrypted message: {}".format(decryptedMsg))
            except:
                print("error decrypting")

            if input("reply to user {}? (y/n)".format(author_id)) == 'y':
                # self.send(Message(text=input("type a msg: ")), thread_id=thread_id, thread_type=thread_type)
                self.sendEncryptedMsg(author_id,thread_id, thread_type, input("type a msg: "))

        self.markAsDelivered(author_id, thread_id)

    # message to send to users who dont have their public key in your friendsKeys log
    def requestUserKey(self, userID, thread_id, thread_type):
        reqString = "-----PUBLIC KEY REQUEST-----"
        # send request msg
        self.send(Message(text=reqString), thread_id=thread_id, thread_type=thread_type)


    def processKeyReturn(self, userID, thread_id, thread_type, keyMsg):
        # handle if user already exists
        # handle formatting of msg
        file = open("friendKeys.txt", "a+")
        string = "user: {}\n{}\n".format(userID, keyMsg)
        file.write(string)
        file.close()
        print("added key details for user: {}".format(userID))


    def respondKeyRequest(self, userID, thread_id, thread_type):
        resString = RSAencryption.keyToString(key, 0)
        self.send(Message(text=resString), thread_id=thread_id, thread_type=thread_type)


    def sendEncryptedMsg(self, userID, thread_id, thread_type, msg):

        stringSearch = "user: " + userID + "\n"

        friendKeys = open("friendKeys.txt", "r").read()

        try:
            keyString = friendKeys.split(stringSearch)[1].split("-----END PUBLIC KEY-----")[0]
            keyString += "-----END PUBLIC KEY-----"
            friendKey = RSAencryption.stringToPublicKey(keyString)
            encryptedMsg = RSAencryption.encryptMessage(msg, friendKey)

            self.send(Message(text=encryptedMsg), thread_id=thread_id, thread_type=thread_type)
        except:
            print("public key for this user not found, sending a key request now...")
            print("please try again after the user returns their public key")
            self.requestUserKey(userID, thread_id, thread_type)

    def interactive(self):
        while 1:
            thread_id = input("enter thread id: ")
            if input("enter thread type: ('user' or 'group'") == 'user':
                thread_type = ThreadType.USER
            else:
                thread_type = ThreadType.GROUP
            msg = input("type msg: ")

            self.send(Message(text=msg), thread_id=thread_id, thread_type=thread_type)


def startKey():
    global key
    try:
        key = RSAencryption.importKeyFromFile("personalKey.pem")
    except:
        key = Crypto.PublicKey.RSA.generate(2048)
        RSAencryption.exportKeyToFile(key, "personalKey")
        print("personal key not found in file 'personalKey.pem', a new key has been generated")


def startUp():
    startKey()

    print(RSAencryption.keyToString(key, 0))

    print("type your email: ")
    email = input()

    print("type your password: ")
    password = input()

    client = Bot(email, password)


    client.listen()

    # client.interactive()


startUp()
