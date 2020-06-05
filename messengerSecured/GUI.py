import base64
import getpass
import json
from tkinter import *
import tkinter.ttk
import messengerSecured as MS
from fbchat import Client
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
####
# - GUI
#   - login error pop up screen
#   - positioning of messages


LARGE_FONT = ("Verdana", 12)

# client = MS.startUp(input("type your email: "), getpass.getpass())
client = MS.Bot("ff", "ff", None, True)
current_thread_id = 0
cache_username_author = dict()


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

        self.show_frame(LogInPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.on_show()
        frame.tkraise()


class LogInPage(Frame):
    global client

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        self.parent = parent
        self.controller = controller

        self.configure(bg="white")

        email_label = Label(self, text="Email", bg="white")
        pwd_label = Label(self, text="Password", bg="white")

        email_entry = Entry(self)
        password_entry = Entry(self, show="*")

        button = Button(self, text="Log In",
                        command=lambda: self.login(email_entry.get(), password_entry.get()))
        # cookie_button = Button(self, text="Log In with cookie", command=self.cookie_login)

        email_label.grid(row=1, column=0, sticky='e', padx=20)
        email_entry.grid(row=1, column=1, sticky='w', )
        self.columnconfigure(0, weight=1, pad=100)
        pwd_label.grid(row=2, column=0, sticky='e', padx=20)
        password_entry.grid(row=2, column=1, sticky='w')
        self.columnconfigure(1, weight=1, pad=100)
        button.grid(row=3, column=0, columnspan=2)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, pad=100)
        self.rowconfigure(2, pad=100)
        self.rowconfigure(4, weight=1)

    def cookie_login(self):
        pass
        # todo: functionality in messengerSecure.py

    def login(self, email, password):
        global client
        # print(self.controller.frames.get(RecentThreadsPage))
        frames_dict = {'LogInPage': self.controller.frames.get(LogInPage),
                       'RecentThreadsPage': self.controller.frames.get(RecentThreadsPage),
                       'ThreadPage': self.controller.frames.get(ThreadPage)}

        client = MS.start_up(email, password, Frames=frames_dict)

        # print(client.fetchThreadList())

        self.controller.show_frame(RecentThreadsPage)

    def on_show(self):
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
        self.name_label = []
        self.msg_label = []
        for i in range(8):
            self.name_label.append(Label(self))
            self.msg_label.append(Label(self))

    def logout(self):
        client.logout()
        with open('user/sessionCookie.txt', 'w') as f:
            f.write("")

        self.controller.show_frame(LogInPage)

    def load_threads(self):
        global client

        for i in range(8):
            self.name_label[i].grid_forget()
            self.msg_label[i].grid_forget()

        threads = client.get_recent_threads(self.offset)

        refresh_button = Button(self, text="Refresh", command=self.load_threads)
        refresh_button.grid(row=0, column=0)

        logout_button = Button(self, text='Logout', command=self.logout)
        logout_button.grid(row=0, column=3)

        # todo: consider less than 8 threads
        range_length = 8
        if len(threads) < 8:
            range_length = len(threads
                               )
        for i in range(range_length):
            thread = threads[i]
            self.name_label[i] = Label(self, text=thread.name, bg='white', font="bold")
            self.name_label[i].bind("<Button-1>", self.clicked_thread)

            text = client.fetchThreadMessages(thread.uid, limit=1)[0].text
            if text is not None:
                text = text[0:21]
            else:
                text = ""

            if len(text) > 20:
                text += "..."
            # print(text)
            self.msg_label[i] = Label(self, text=text.encode('utf-8'), bg='white')
            self.msg_label[i].bind("<Button-1>", self.clicked_thread)

            # GET IMAGE FROM URL
            image_url = thread.photo
            if image_url is not None:
                canvas = Canvas(self, width=50, height=50)
                pil_image = Image.open(urllib.request.urlopen(image_url))
                image = ImageTk.PhotoImage(pil_image)
                canvas.create_image(400, 400, image=image)
                canvas.grid(row=i + 1, column=0)

            # print(icon)
            self.name_label[i].grid(row=i + 1, column=1, sticky='w')
            self.msg_label[i].grid(row=i + 1, column=2, sticky='w')

            self.rowconfigure(i + 1, pad=40)

    def clicked_thread(self, event):
        global current_thread_id
        selected_number = event.widget.grid_info()["row"] - 1

        current_thread_id = client.get_recent_threads(self.offset)[selected_number].uid

        self.controller.show_frame(ThreadPage)

    def on_show(self):
        self.load_threads()

    # def testPrint(self):
    #    print("it worked!")
    #    pass


class ThreadPage(Frame):
    global client

    def __init__(self, parent, controller):
        global client
        global current_thread_id

        Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg="white")

        # clear labels!
        self.sender_label = []
        self.msg_label = []
        self.encryption_label = []
        for i in range(11):
            self.sender_label.append(Label(self, text=""))
            self.msg_label.append(Label(self, text=""))
            self.encryption_label.append(Label(self, text=""))
        self.thread_name_label = Label(self, text="")

    def on_show(self):

        global current_thread_id
        thread = client.fetchThreadInfo(current_thread_id).get(current_thread_id)
        self.thread_name_label = Label(self, text=thread.name, bg='white')
        self.thread_name_label.grid(row=0, column=0, columnspan=5)
        self.columnconfigure(1, weight=1, pad=20)
        self.columnconfigure(0, pad=20)

        back_button = Button(self, text="Back", command=lambda: self.controller.show_frame(RecentThreadsPage))
        back_button.grid(row=0, column=0, sticky='w')

        msg_box = Entry(self)
        msg_box.grid(row=12, column=1, columnspan=3, sticky='w')

        refresh_button = Button(self, text="Refresh", command=self.show_messages)
        refresh_button.grid(row=12, column=0)

        send_button = Button(self, text="Send", command=lambda: self.send_msg(msg_box.get()))
        send_button.grid(row=12, column=4, sticky='w')

        self.show_messages()

    def show_messages(self):
        global cache_username_author
        # clear labels!
        for i in range(11):
            self.sender_label[i].grid_forget()
            self.msg_label[i].grid_forget()
            self.encryption_label[i].grid_forget()
        self.thread_name_label.grid_forget()

        print("loading messages...")
        thread = client.fetchThreadInfo(current_thread_id).get(current_thread_id)

        self.thread_name_label = Label(self, text=thread.name, bg='white')
        self.thread_name_label.grid(row=0, column=0, columnspan=5)

        client.back_log_messages(thread)

        messages = client.message_log[thread.uid][-10:]

        msg_num = 1
        for message in messages:
            last_msg_flag = msg_num == 10  # todo: can't assume this?

            formatted_msg = client.handle_message(message, thread, last_msg_flag)

            # cache user names as fetching is expensive
            username = cache_username_author.get(formatted_msg.get('author'))
            if username is None:
                username = client.fetchUserInfo(formatted_msg.get('author')).get(formatted_msg.get('author')).name
                cache_username_author[formatted_msg.get('author')] = username

            self.sender_label[msg_num] = Label(self, text=username + ":",
                                               bg='white')  # client.fetchUserInfo(formatted_msg.get('author')).get(
            # formatted_msg.get('author')).name + ":", bg='white')
            self.sender_label[msg_num].grid(row=msg_num, column=0, sticky='w')

            if formatted_msg.get('text') is None:
                text = ""
            else:
                text = formatted_msg.get('text').encode("utf-8")
            self.msg_label[msg_num] = Label(self, text=text, bg='white')
            self.msg_label[msg_num].grid(row=msg_num, column=1, sticky='w')

            encryption_status = "!"
            if formatted_msg.get('secured'):
                encryption_status = "*"
            self.encryption_label[msg_num] = Label(self, text=encryption_status, bg='white')
            self.encryption_label[msg_num].grid(row=msg_num, column=2)

            self.rowconfigure(msg_num, pad=20)

            msg_num += 1

        print("... done.")

        print("saving log...")
        with open('user/messageLog.txt', 'w') as outfile:  # save msg log
            json.dump(client.message_log, outfile)
        print("... done")

    def send_msg(self, message):
        thread = client.fetchThreadInfo(current_thread_id).get(current_thread_id)

        client.send_encrypted_msg(thread.uid, thread.type, message)

        self.show_messages()


app = MessengerSecuredApp()
app.mainloop()
