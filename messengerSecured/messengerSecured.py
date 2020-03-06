from fbchat import Client, log
from fbchat.models import *
import credentials
import Crypto

class Bot(Client):

    def onMessage(self, author_id=None, message_object=None, thread_id=None,
                  thread_type=ThreadType.USER, **kwargs):
        self.markAsRead(author_id)

        log.info("Message {} from {} in {}".format(message_object, thread_id, thread_type))

        msgText = message_object.text

        reply = 'nghai, wyd now'

        if author_id != self.uid and author_id == 100000515967471: # (kate)
            self.send(Message(text=reply), thread_id=thread_id, thread_type=thread_type)

        self.markAsDelivered(author_id, thread_id)

print("type your email: ")
email = input()

print("type your password: ")
password = input()

client = Bot(email, password)

client.listen()
