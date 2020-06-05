import base64
import getpass
import json
from tkinter import *
import tkinter.ttk
import messengerSecured as MS
from fbchat import Client, log
from fbchat.models import *
import urllib.request
from PIL import Image, ImageTk

# todo
# - fix recent threads to not disappear temporarily on reloading
# - figure out images
# - clean git
# - not refresh on EVERY event
# - fix display lag..
# - option to send unecncrypted msg
# - fix code that assumes certain number of messages or threads etc
# - fix scaling
# - option to destroy session (logout)
# - option to log in with session
# - option to log in without session (logout of previous session!!)
# - different options for different accounts?



LARGE_FONT = ("Verdana", 12)

# client = MS.startUp(input("type your email: "), getpass.getpass())
client = MS.Bot("ff", "ff", None, True)
currentThreadID = 0


class MessengerSecuredApp(Tk):

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        Tk.wm_title(self, "Messenger Secured")

        Tk.geometry(self, "900x800")
        # Tk.resizable(self, 0, 0)

        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = dict()

        for F in (LogInPage, RecentThreadsPage, ThreadPage):
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky='nsew')

        self.showFrame(LogInPage)

    def showFrame(self, cont):
        frame = self.frames[cont]
        frame.onShow()
        frame.tkraise()


class LogInPage(Frame):
    global client

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        self.parent = parent
        self.controller = controller

        self.configure(bg="white")

        emailLabel = Label(self, text="Email", bg="white")
        passwordLabel = Label(self, text="Password", bg="white")

        emailEntry = Entry(self)
        passwordEntry = Entry(self, show="*")

        button = Button(self, text="Log In",
                        command=lambda: self.logIn(emailEntry.get(), passwordEntry.get()))

        emailLabel.grid(row=1, column=0, sticky='e', padx=20)
        emailEntry.grid(row=1, column=1, sticky='w', )
        self.columnconfigure(0, weight=1, pad=100)
        passwordLabel.grid(row=2, column=0, sticky='e', padx=20)
        passwordEntry.grid(row=2, column=1, sticky='w')
        self.columnconfigure(1, weight=1, pad=100)
        button.grid(row=3, column=0, columnspan=2)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, pad=100)
        self.rowconfigure(2, pad=100)
        self.rowconfigure(4, weight=1)

    def logIn(self, email, password):
        global client
        # print(self.controller.frames.get(RecentThreadsPage))
        FramesDict = {'LogInPage': self.controller.frames.get(LogInPage),
                   'RecentThreadsPage': self.controller.frames.get(RecentThreadsPage),
                   'ThreadPage': self.controller.frames.get(ThreadPage)}

        client = MS.startUp(email, password, Frames=FramesDict)

        # print(client.fetchThreadList())

        self.controller.showFrame(RecentThreadsPage)

    def onShow(self):
        pass


class RecentThreadsPage(Frame):
    global client

    def __init__(self, parent, controller):
        global client
        Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg="white")
        self.offset = 0

        # clear labels
        self.nameLabel = []
        self.messageLabel = []
        for i in range(8):
            self.nameLabel.append(Label(self))
            self.messageLabel.append(Label(self))

    def loadThreads(self):
        global client

        for i in range(8):
            self.nameLabel[i].grid_forget()
            self.messageLabel[i].grid_forget()

        threads = client.getRecentThreads(self.offset)

        refreshButton = Button(self, text="Refresh", command=self.loadThreads)
        refreshButton.grid(row=0, column=0)

        # todo: consider less than 8 threads
        range_length = 8
        if len(threads) < 8:
            range_length = len(threads
                               )
        for i in range(range_length):
            thread = threads[i]
            self.nameLabel[i] = Label(self, text=thread.name, bg='white', font="bold")
            self.nameLabel[i].bind("<Button-1>", self.clickedThread)

            text = client.fetchThreadMessages(thread.uid, limit=1)[0].text
            if text is not None:
                text = text[0:21]
            else:
                text = ""

            if len(text) > 20:
                text += "..."
            # print(text)
            self.messageLabel[i] = Label(self, text=text.encode('utf-8'), bg='white')
            self.messageLabel[i].bind("<Button-1>", self.clickedThread)

            # GET IMAGE FROM URL
            image_url = thread.photo
            if image_url is not None:
                canvas = Canvas(self, width=50, height=50)
                PILImage = Image.open(urllib.request.urlopen(image_url))
                image = ImageTk.PhotoImage(PILImage)
                canvas.create_image(400, 400, image=image)
                canvas.grid(row=i + 1, column=0)

            # print(icon)
            self.nameLabel[i].grid(row=i + 1, column=1, sticky='w')
            self.messageLabel[i].grid(row=i + 1, column=2, sticky='w')

            self.rowconfigure(i + 1, pad=40)

    def clickedThread(self, event):
        global currentThreadID
        selectedNumber = event.widget.grid_info()["row"] - 1

        currentThreadID = client.getRecentThreads(self.offset)[selectedNumber].uid

        self.controller.showFrame(ThreadPage)

    def onShow(self):
        self.loadThreads()

    def testPrint(self):
        print("it worked!")


class ThreadPage(Frame):
    global client

    def __init__(self, parent, controller):
        global client
        global currentThreadID

        Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg="white")

        # clear labels!
        self.senderLabel = []
        self.msgLabel = []
        self.encryptionLabel = []
        for i in range(11):
            self.senderLabel.append(Label(self, text=""))
            self.msgLabel.append(Label(self, text=""))
            self.encryptionLabel.append(Label(self, text=""))
        self.threadNameLabel = Label(self, text="")

    def onShow(self):

        global currentThreadID
        thread = client.fetchThreadInfo(currentThreadID).get(currentThreadID)
        self.threadNameLabel = Label(self, text=thread.name, bg='white')
        self.threadNameLabel.grid(row=0, column=0, columnspan=5)
        self.columnconfigure(1, weight=1, pad=20)
        self.columnconfigure(0, pad=20)

        backButton = Button(self, text="Back", command=lambda: self.controller.showFrame(RecentThreadsPage))
        backButton.grid(row=0, column=0, sticky='w')

        messageBox = Entry(self)
        messageBox.grid(row=12, column=1, columnspan=3, sticky='w')

        refreshButton = Button(self, text="Refresh", command=self.showMessages)
        refreshButton.grid(row=12, column=0)

        sendButton = Button(self, text="Send", command=lambda: self.sendMessage(messageBox.get()))
        sendButton.grid(row=12, column=4, sticky='w')

        self.showMessages()

    def showMessages(self):

        # clear labels!
        for i in range(11):
            self.senderLabel[i].grid_forget()
            self.msgLabel[i].grid_forget()
            self.encryptionLabel[i].grid_forget()
        self.threadNameLabel.grid_forget()

        print("loading messages...")
        thread = client.fetchThreadInfo(currentThreadID).get(currentThreadID)

        self.threadNameLabel = Label(self, text=thread.name, bg='white')
        self.threadNameLabel.grid(row=0, column=0, columnspan=5)

        client.backLogMessages(thread)

        messages = client.messageLog[thread.uid][-10:]

        msgNum = 1
        for message in messages:
            lastMsgFlag = msgNum == 10  # todo: can't assume this
            formatedMsg = client.handleMessage(message, thread, lastMsgFlag)

            self.senderLabel[msgNum] = Label(self, text=client.fetchUserInfo(formatedMsg.get('author')).get(
                formatedMsg.get('author')).name + ":", bg='white')
            self.senderLabel[msgNum].grid(row=msgNum, column=0, sticky='w')

            if formatedMsg.get('text') is None:
                text = ""
            else:
                text = formatedMsg.get('text').encode("utf-8")
            self.msgLabel[msgNum] = Label(self, text=text, bg='white')
            self.msgLabel[msgNum].grid(row=msgNum, column=1, sticky='w')

            encryptionStatus = "!"
            if formatedMsg.get('secured'):
                encryptionStatus = "*"
            self.encryptionLabel[msgNum] = Label(self, text=encryptionStatus, bg='white')
            self.encryptionLabel[msgNum].grid(row=msgNum, column=2)

            self.rowconfigure(msgNum, pad=20)

            msgNum += 1

        print("... done.")

        print("saving log...")
        with open('messageLog.txt', 'w') as outfile:  # save msg log
            json.dump(client.messageLog, outfile)
        print("... done")

    def sendMessage(self, message):
        thread = client.fetchThreadInfo(currentThreadID).get(currentThreadID)

        client.sendEncryptedMsg(thread.uid, thread.type, message)

        self.showMessages()


app = MessengerSecuredApp()
app.mainloop()
