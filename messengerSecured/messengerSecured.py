from fbchat import Client, log
from fbchat.models import *
import Crypto
import RSAencryption
import getpass
import datetime
import threading
import json

# todo:
# add list of pending requests to verify responses
# cache messages


key = 0


class Bot(Client):
    global key
    messageLog = dict()  # dictionary of threadID paired with list of messages formatted as dict, try open from json 1st
    friendKeyLog = dict()  # dictionary of threadID paired with public key to encrypt with

    def onMessage(self, author_id=None, message_object=None, thread_id=None,
                  thread_type=ThreadType.USER, **kwargs):
        print("new message received!")

        # add to logged messages
        dictMsg = self.messageToDict(message_object)
        try:
            self.messageLog[thread_id].append(dictMsg)
        except:
            self.messageLog[thread_id] = []
            self.messageLog[thread_id].append(dictMsg)

        # print(self.messageLog)

    def loadKeyLog(self):
        try:
            with open('friendKeys.txt') as json_file:
                self.friendKeyLog = json.load(json_file)
        except json.JSONDecodeError:
            print("no recoverable stored keys in friendKeys.txt")

    def loadMessageLog(self):
        try:
            with open('messageLog.txt') as json_file:
                self.messageLog = json.load(json_file)
        except json.JSONDecodeError:
            print("no recoverable stored messages in messageLog.txt")

    # convert message fbchat object to dictionary object format for json
    def messageToDict(self, message_object):
        return {'uid': message_object.uid, 'text': message_object.text, 'author': message_object.author,
                'timestamp': message_object.timestamp}

    # message to send to users who dont have their public key in your friendsKeys log
    def requestUserKey(self, thread_id, thread_type):
        reqString = "-----PUBLIC KEY REQUEST-----"
        # send request msg
        self.send(Message(text=reqString), thread_id=thread_id, thread_type=thread_type)

    def processKeyReturn(self, threadID, keyMsg):

        if self.friendKeyLog.get(threadID) is not None:
            pass  # handle existing
        else:
            self.friendKeyLog[threadID] = keyMsg
        print("added key details for thread: {}".format(threadID))

        with open('friendKeys.txt', 'w') as outfile:
            json.dump(self.friendKeyLog, outfile)

    def respondKeyRequest(self, thread_id, thread_type):
        resString = RSAencryption.keyToString(key, 0)
        self.send(Message(text=resString), thread_id=thread_id, thread_type=thread_type)

    def sendEncryptedMsg(self, thread_id, thread_type, msg):

        if self.friendKeyLog.get(thread_id) is not None:
            keyString = self.friendKeyLog[thread_id]
            friendKey = RSAencryption.stringToPublicKey(keyString)
            encryptedMsg = RSAencryption.encryptMessage(msg, friendKey)

            self.send(Message(text=encryptedMsg), thread_id=thread_id, thread_type=thread_type)
        else:
            print("public key for this user not found, sending a key request now...")
            print("please try again after the user returns their public key")
            self.requestUserKey(thread_id, thread_type)

    def searchUsers(self):
        searchResults = self.searchForUsers(input("enter a name: "))
        print("Search results: ")
        i = 1
        for result in searchResults:
            print("{}) {}".format(i, result.name))
            i += 1

    def handleMessage(self, message, thread, mostRecentFlag):
        if message.author != self.uid:

            if str(message.text).startswith("-----BEGIN PUBLIC KEY-----") and mostRecentFlag:
                # handle errors
                self.processKeyReturn(message.author, message.text)

            if str(message.text) == "-----PUBLIC KEY REQUEST-----" and mostRecentFlag:
                self.respondKeyRequest(thread.uid, thread.type)
                return

        try:
            decryptedMsg = RSAencryption.decryptMessage(message.text, key)
            # print("decrypted message: {}".format(decryptedMsg))
            print('"{}" from {} at {} *secured*\n'.format(decryptedMsg,
                                                          self.fetchUserInfo(message.author).get(
                                                              message.author).name,
                                                          message.timestamp))
        except:
            print('"{}" from {} at {} *unsecured*\n'.format(message.text,
                                                            self.fetchUserInfo(message.author).get(
                                                                message.author).name,
                                                            message.timestamp))

    # given a thread, append new messages into the messageLog until a pre-logged message is found, or until limit of x
    def backLogMessages(self, thread):
        print("syncing messages...")
        messages = self.fetchThreadMessages(thread.uid, limit=10)

        messageNumToAdd = -1
        emptyThreadFlag = self.messageLog.get(thread.uid) is None

        for message in messages:
            if not emptyThreadFlag:
                if message.uid == self.messageLog[thread.uid][-1].get(
                        'uid'):  # if message id = most recent message in log
                    break
            messageNumToAdd += 1

        if emptyThreadFlag:
            self.messageLog[thread.uid] = []

        for i in range(messageNumToAdd, -1, -1):
            self.messageLog[thread.uid].append(self.messageToDict(messages[i]))

    def interactiveMessagingThread(self, thread):
        while 1:
            print("\n\n\nconversation with {}".format(thread.name))

            # fetch new messages until a pre logged message is found (or until limit of **), then add new messages
            # to the log

            self.backLogMessages(thread)

            print(self.messageLog)

            messages = self.fetchThreadMessages(thread.uid, limit=10)
            messages.reverse()

            msgNum = 1
            for message in messages:
                lastMsgFlag = msgNum == 10
                self.handleMessage(message, thread, lastMsgFlag)
                msgNum += 1

            print("\nr) refresh messages... \ns) send message to thread... \nb) go back...")
            choice2 = input("select an option: ")
            if choice2 == "r":
                pass
            elif choice2 == "s":
                msg = input("type msg: ")
                # self.send(Message(text=msg), thread_id=thread.uid, thread_type=thread.type)
                self.sendEncryptedMsg(thread.uid, thread.type, msg)

            elif choice2 == "b":
                break

    def interactiveMode1(self):
        while 1:
            thread_id = input("enter thread id: ")
            if input("enter thread type: ('user' or 'group'") == 'user':
                thread_type = ThreadType.USER
            else:
                thread_type = ThreadType.GROUP
            msg = input("type msg: ")

            self.send(Message(text=msg), thread_id=thread_id, thread_type=thread_type)

    def interactiveMode2(self):
        # option to view threads or to search for thread/user (fetch thread list)
        # interact in thread, list recent messages (fetchThreadMessages)

        # listenerThread = threading.Thread(target=self.listen)
        # listenerThread.start()

        while 1:
            print("s) Search...")
            i = 1
            threads = self.fetchThreadList(offset=0, limit=10)
            for thread in threads:
                print("{}) {}".format(i, thread.name))
                i += 1
            print("l) Logout safely")
            choice = input("select an option: ")

            if choice == "s":
                # search functionality here
                pass
            elif choice == "l":
                with open('messageLog.txt', 'w') as outfile:  # save msg log
                    json.dump(self.messageLog, outfile)
                self.logout()
                return
                # fix to exit
            # check if int
            elif 0 < int(choice) < 11:
                thread = threads[int(choice) - 1]
                self.interactiveMessagingThread(thread)


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

    # print(RSAencryption.keyToString(key, 0))

    cookie = dict()

    try:
        with open('sessionCookie.txt') as json_file:
            cookie = json.load(json_file)
    except json.JSONDecodeError:
        print("no recoverable cookies")

    client = Bot(input("type your email: "), getpass.getpass(), session_cookies=cookie)

    with open('sessionCookie.txt', 'w') as outfile:
        json.dump(client.getSession(), outfile)

    # client.searchUsers()
    # listenerThread = threading.Thread(target=client.listen())
    # interactiveThread = threading.Thread(target=client.interactiveMode2())
    # listenerThread.start()
    # interactiveThread.start()
    # client.startListening()

    client.loadKeyLog()
    client.loadMessageLog()

    # client.listen()
    client.interactiveMode2()


startUp()
