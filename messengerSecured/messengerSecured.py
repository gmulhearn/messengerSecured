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
    message_log = dict()  # dictionary of thread_id paired with list of messages formatted as dict, try open from json 1st
    friend_key_log = dict()  # dictionary of thread_id paired with public key to encrypt with

    # init method to allow bypass of super init, used in GUI.py
    def __init__(self, email, password, cookies, null, Frames=None):
        self.frames = Frames

        if not null:
            super().__init__(email, password, session_cookies=cookies)
        else:
            pass

        if Frames is not None:
            # Frames.get('RecentThreadsPage').testPrint()
            pass

    def onMessage(self, author_id=None, message_object=None, thread_id=None,
                  thread_type=ThreadType.USER, **kwargs):
        print("new message received!")

        # add to logged messages
        dict_msg = self.message_to_dict(message_object)
        try:
            # self.message_log[thread_id].append(dict_msg)
            pass
        except:
            # self.message_log[thread_id] = []
            # self.message_log[thread_id].append(dict_msg)
            pass

        # refresh GUI if there - todo: check what page they're on and dont refresh unnessecerily
        if self.frames is not None:
            self.frames.get('RecentThreadsPage').load_threads()
            self.frames.get('ThreadPage').show_messages()

        # print(self.message_log)

    def load_key_log(self):
        try:
            with open('user/friendKeys.txt') as json_file:
                self.friend_key_log = json.load(json_file)
        except json.JSONDecodeError:
            print("no recoverable stored keys in friendKeys.txt")
        except FileNotFoundError:
            print("no friendsKeys file found")

    def load_message_log(self):
        try:
            with open('user/messageLog.txt') as json_file:
                self.message_log = json.load(json_file)
        except json.JSONDecodeError:
            print("no recoverable stored messages in messageLog.txt")
        except FileNotFoundError:
            print("no message log file found")

    # convert message fbchat object to dictionary object format for json
    def message_to_dict(self, message_object):
        return {'uid': message_object.uid, 'text': message_object.text, 'author': message_object.author,
                'timestamp': message_object.timestamp}

    # message to send to users who dont have their public key in your friendsKeys log
    def request_user_key(self, thread_id, thread_type):
        req_string = "-----PUBLIC KEY REQUEST-----"
        # send request msg
        self.send(Message(text=req_string), thread_id=thread_id, thread_type=thread_type)

    def process_key_return(self, thread_id, key_msg):

        if self.friend_key_log.get(thread_id) is not None:
            pass  # handle existing
        else:
            self.friend_key_log[thread_id] = key_msg
        print("added key details for thread: {}".format(thread_id))

        with open('user/friendKeys.txt', 'w') as outfile:
            json.dump(self.friend_key_log, outfile)

    def respond_key_request(self, thread_id, thread_type):
        res_string = RSAencryption.keyToString(key, 0)
        self.send(Message(text=res_string), thread_id=thread_id, thread_type=thread_type)

    def send_encrypted_msg(self, thread_id, thread_type, msg):

        if self.friend_key_log.get(thread_id) is not None:
            key_string = self.friend_key_log[thread_id]
            friend_key = RSAencryption.stringToPublicKey(key_string)
            encrypted_msg = RSAencryption.encryptMessage(msg, friend_key)

            self.send(Message(text=encrypted_msg), thread_id=thread_id, thread_type=thread_type)

            # log the sent message as unencrypted
            sent_msg = self.fetchThreadMessages(thread_id, limit=1)[0]
            dict_msg = {'uid': sent_msg.uid, 'text': msg, 'author': sent_msg.author,
                        'timestamp': sent_msg.timestamp}
            self.message_log[thread_id].append(dict_msg)
        else:
            print("public key for this user not found, sending a key request now...")
            print("please try again after the user returns their public key")
            self.request_user_key(thread_id, thread_type)

    # print users that match your search request
    def search_users(self):
        search_results = self.searchForUsers(input("enter a name: "))
        print("Search results: ")
        i = 1
        for result in search_results:
            print("{}) {}".format(i, result.name))
            i += 1

    # read the message (in dict format) and determine what action to take.
    # returns the message in dict format made for GUI
    def handle_message(self, message, thread, most_recent_flag):
        if message.get('author') != self.uid:

            if str(message.get('text')).startswith("-----BEGIN PUBLIC KEY-----") and most_recent_flag:
                # handle errors
                self.process_key_return(message.get('author'), message.get('text'))
                message['secured'] = False
                return message

            if str(message.get('text')) == "-----PUBLIC KEY REQUEST-----" and most_recent_flag:
                print("received key request, now responding...")
                self.respond_key_request(thread.uid, thread.type)
                message['secured'] = False
                return message

        try:
            decrypted_msg = RSAencryption.decryptMessage(message.get('text'), key)
            # print("decrypted message: {}".format(decrypted_msg))
            # print('"{}" from {} at {} *secured*\n'.format(decrypted_msg,
            #                                              self.fetchUserInfo(message.get('author')).get(
            #                                                  message.get('author')).name,
            #                                              message.get('timestamp')))
            message['secured'] = True
            message['text'] = decrypted_msg
            return message
        except:
            # print('"{}" from {} at {} *unsecured*\n'.format(message.get('text'),
            #                                                self.fetchUserInfo(message.get('author')).get(
            #                                                    message.get('author')).name,
            #                                                message.get('timestamp')))
            message['secured'] = False
            return message

    # given a thread, append new messages into the messageLog until a pre-logged message is found, or until limit of x
    def back_log_messages(self, thread):
        print("syncing messages...")
        messages = self.fetchThreadMessages(thread.uid, limit=10)

        msg_num_to_add = -1
        empty_thread_flag = self.message_log.get(thread.uid) is None

        for message in messages:
            if not empty_thread_flag:
                if message.uid == self.message_log[thread.uid][-1].get(
                        'uid'):  # if message id = most recent message in log
                    break
            msg_num_to_add += 1

        if empty_thread_flag:
            self.message_log[thread.uid] = []

        # print("DEBUG: msg num to add: {}".format(msg_num_to_add))

        for i in range(msg_num_to_add, -1, -1):
            self.message_log[thread.uid].append(self.message_to_dict(messages[i]))

    # given a thread, provide interactive messaging and printing of messageLogs to users
    def interactive_msg_thread(self, thread):
        while 1:
            print("\n\n\nconversation with {}".format(thread.name))

            # fetch new messages until a pre logged message is found (or until limit of **), then add new messages
            # to the log

            self.back_log_messages(thread)

            print(self.message_log)

            messages = self.message_log[thread.uid][-10:]

            msg_num = 1
            for message in messages:
                last_msg_flag = msg_num == 10
                self.handle_message(message, thread, last_msg_flag)
                msg_num += 1

            print("\nr) refresh messages... \ns) send message to thread... \nb) go back...")
            choice2 = input("select an option: ")
            if choice2 == "r":
                pass
            elif choice2 == "s":
                self.setTypingStatus(TypingStatus.TYPING, thread.uid, thread.type)
                msg = input("type msg: ")
                self.setTypingStatus(TypingStatus.STOPPED, thread.uid, thread.type)
                self.send_encrypted_msg(thread.uid, thread.type, msg)

            elif choice2 == "b":
                break

    def interactive_mode1(self):
        while 1:
            thread_id = input("enter thread id: ")
            if input("enter thread type: ('user' or 'group'") == 'user':
                thread_type = ThreadType.USER
            else:
                thread_type = ThreadType.GROUP
            msg = input("type msg: ")

            self.send(Message(text=msg), thread_id=thread_id, thread_type=thread_type)

    def interactive_mode2(self):
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
                    json.dump(self.message_log, outfile)
                self.logout()
                return
                # fix to exit
            # check if int
            elif 0 < int(choice) < 11:
                thread = threads[int(choice) - 1]
                self.interactive_msg_thread(thread)

    # FOR GUI!! ###

    def get_recent_threads(self, offset):
        return self.fetchThreadList(offset=offset, limit=10)


def start_key():
    global key
    try:
        key = RSAencryption.importKeyFromFile("user/personalKey.pem")
    except:
        key = Crypto.PublicKey.RSA.generate(2048)
        RSAencryption.exportKeyToFile(key, "user/personalKey")
        print("personal key not found in file 'personalKey.pem', a new key has been generated")


# initialize the client, cookies, logs, key
def start_up(email, password, Frames=None):
    if not os.path.exists('user'):
        os.mkdir('user')
        print("made user directory")

    start_key()

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

    client.load_key_log()
    client.load_message_log()

    # client.interactive_mode2()
    listener_thread = threading.Thread(target=client.listen)
    listener_thread.start()

    return client

# start_up(input("type your email: "), getpass.getpass())
