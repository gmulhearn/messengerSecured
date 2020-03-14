import logging
import threading
import time


class Client:

    def thread(self):
        t = threading.Thread(name='my_service', target=self.my_service())
        w = threading.Thread(name='worker', target=self.worker())

        w.start()
        t.start()

    def worker(self):
        # logging.debug('Starting')
        while 1:
            print("listening ")
            time.sleep(2)
        # logging.debug('Exiting')

    def my_service(self):
        # logging.debug('Starting')
        while 1:
            input("type")
        # logging.debug('Exiting')


client1 = Client()
client1.thread()