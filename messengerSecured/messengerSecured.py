from fbchat import Client, log
from fbchat.models import *
import Crypto
import RSAencryption
import getpass
import datetime
import threading
import json
import os

# pip install pycryptodome
# pip install fbchat
# pip install Pillow


# todo:
# - add list of pending requests to verify responses
# - cache messages decrypted! (to avoid lag)
# - fetch Messages one by one


key = 0


class Bot(Client):
    global key
    messageLog = dict()  # dictionary of threadID paired with list of messages formatted as dict, try open from json 1st
    friendKeyLog = dict()  # dictionary of threadID paired with public key to encrypt with

    # init method to allow bypass of super init, used in GUI.py
    def __init__(self, email, password, cookies, null, Frames=None):
        self.frames = Frames

        if not null:
            super().__init__(email, password, session_cookies=cookies)
        else:
            pass

        if Frames is not None:
            Frames.get('RecentThreadsPage').testPrint()

    def onMessage(self, author_id=None, message_object=None, thread_id=None,
                  thread_type=ThreadType.USER, **kwargs):
        print("new message received!")

        # add to logged messages
        dictMsg = self.messageToDict(message_object)
        try:
            # self.messageLog[thread_id].append(dictMsg)
            pass
        except:
            # self.messageLog[thread_id] = []
            # self.messageLog[thread_id].append(dictMsg)
            pass

        # refresh GUI if there - todo: check what page they're on and dont refresh unnessecerily
        if self.frames is not None:
            self.frames.get('RecentThreadsPage').loadThreads()
            self.frames.get('ThreadPage').showMessages()

        # print(self.messageLog)

    def loadKeyLog(self):
        try:
            with open('user/friendKeys.txt') as json_file:
                self.friendKeyLog = json.load(json_file)
        except json.JSONDecodeError:
            print("no recoverable stored keys in friendKeys.txt")
        except FileNotFoundError:
            print("no friendsKeys file found")

    def loadMessageLog(self):
        try:
            with open('user/messageLog.txt') as json_file:
                self.messageLog = json.load(json_file)
        except json.JSONDecodeError:
            print("no recoverable stored messages in messageLog.txt")
        except FileNotFoundError:
            print("no message log file found")

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

        with open('user/friendKeys.txt', 'w') as outfile:
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

            # log the sent message as unencrypted
            sentMessage = self.fetchThreadMessages(thread_id, limit=1)[0]
            dictMsg = {'uid': sentMessage.uid, 'text': msg, 'author': sentMessage.author,
                       'timestamp': sentMessage.timestamp}
            self.messageLog[thread_id].append(dictMsg)
        else:
            print("public key for this user not found, sending a key request now...")
            print("please try again after the user returns their public key")
            self.requestUserKey(thread_id, thread_type)

    # print users that match your search request
    def searchUsers(self):
        searchResults = self.searchForUsers(input("enter a name: "))
        print("Search results: ")
        i = 1
        for result in searchResults:
            print("{}) {}".format(i, result.name))
            i += 1

    # read the message (in dict format) and determine what action to take.
    # returns the message in dict format made for GUI
    def handleMessage(self, message, thread, mostRecentFlag):
        if message.get('author') != self.uid:

            if str(message.get('text')).startswith("-----BEGIN PUBLIC KEY-----") and mostRecentFlag:
                # handle errors
                self.processKeyReturn(message.get('author'), message.get('text'))
                message['secured'] = False
                return message

            if str(message.get('text')) == "-----PUBLIC KEY REQUEST-----" and mostRecentFlag:
                print("received key request, now responding...")
                self.respondKeyRequest(thread.uid, thread.type)
                message['secured'] = False
                return message

        try:
            decryptedMsg = RSAencryption.decryptMessage(message.get('text'), key)
            # print("decrypted message: {}".format(decryptedMsg))
            # print('"{}" from {} at {} *secured*\n'.format(decryptedMsg,
            #                                              self.fetchUserInfo(message.get('author')).get(
            #                                                  message.get('author')).name,
            #                                              message.get('timestamp')))
            message['secured'] = True
            message['text'] = decryptedMsg
            return message
        except:
            # print('"{}" from {} at {} *unsecured*\n'.format(message.get('text'),
            #                                                self.fetchUserInfo(message.get('author')).get(
            #                                                    message.get('author')).name,
            #                                                message.get('timestamp')))
            message['secured'] = False
            return message

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

    # given a thread, provide interactive messaging and printing of messageLogs to users
    def interactiveMessagingThread(self, thread):
        while 1:
            print("\n\n\nconversation with {}".format(thread.name))

            # fetch new messages until a pre logged message is found (or until limit of **), then add new messages
            # to the log

            self.backLogMessages(thread)

            print(self.messageLog)

            messages = self.messageLog[thread.uid][-10:]

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
                self.setTypingStatus(TypingStatus.TYPING, thread.uid, thread.type)
                msg = input("type msg: ")
                self.setTypingStatus(TypingStatus.STOPPED, thread.uid, thread.type)
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
                with open('user/messageLog.txt', 'w') as outfile:  # save msg log
                    json.dump(self.messageLog, outfile)
                self.logout()
                return
                # fix to exit
            # check if int
            elif 0 < int(choice) < 11:
                thread = threads[int(choice) - 1]
                self.interactiveMessagingThread(thread)

    ### FOR GUI!! ###

    def getRecentThreads(self, offset):
        return self.fetchThreadList(offset=offset, limit=10)


def startKey():
    global key
    try:
        key = RSAencryption.importKeyFromFile("user/personalKey.pem")
    except:
        key = Crypto.PublicKey.RSA.generate(2048)
        RSAencryption.exportKeyToFile(key, "user/personalKey")
        print("personal key not found in file 'personalKey.pem', a new key has been generated")


# initialize the client, cookies, logs, key
def startUp(email, password, Frames=None):
    if not os.path.exists('user'):
        os.mkdir('user')
        print("made user directory")

    startKey()

    # print(RSAencryption.keyToString(key, 0))

    cookie = dict()

    try:
        with open('user/sessionCookie.txt') as json_file:
            cookie = json.load(json_file)
    except json.JSONDecodeError:
        print("no recoverable cookies")
    except FileNotFoundError:
        print("no recoverable cookies")

    client = Bot(email, password, cookie, False, Frames=Frames)

    with open('user/sessionCookie.txt', 'w') as outfile:
        json.dump(client.getSession(), outfile)

    client.loadKeyLog()
    client.loadMessageLog()

    # client.interactiveMode2()
    listenerThread = threading.Thread(target=client.listen)
    listenerThread.start()

    return client

# startUp(input("type your email: "), getpass.getpass())
