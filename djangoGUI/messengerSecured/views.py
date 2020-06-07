from django.shortcuts import render, redirect
from messengerSecured.forms import LogInForm, MessageForm
from .functionality import messengerSecured as MS
import json

client = MS.Bot("ff", "ff", None, True)
cache_username_author = dict()


def home(request):
    return redirect('ms-login')
    # return render(request, 'messengerSecured/home.html')


def about(request):
    return render(request, 'messengerSecured/about.html')


def login(request):
    global client

    if request.method == 'POST':
        form = LogInForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            client = MS.start_up(email, password)

            return redirect('ms-recent')
    else:
        form = LogInForm()

    return render(request, 'messengerSecured/login.html', {'form': form})


def recent_threads(request):
    global client

    raw_threads = client.get_recent_threads(offset=0)

    clean_threads = []

    for thread in raw_threads:
        text = client.fetchThreadMessages(thread.uid, limit=1)[0].text
        clean_threads.append({'name': thread.name, 'text': text, 'id': thread.uid, 'image': thread.photo})

    print(clean_threads)

    return render(request, 'messengerSecured/recentThreads.html', {'threads': clean_threads})


def thread(request):
    global client

    thread_id = request.GET.get('thread_id')  # todo: error handle
    messages = []
    thread_obj = client.fetchThreadInfo(thread_id).get(thread_id)

    # HANDLE POST

    if request.method == 'POST':
        form = MessageForm(request.POST, auto_id=False)

        if form.is_valid():
            message = form.cleaned_data.get('message')
            print(f"{message}")

            client.send_encrypted_msg(thread_obj.uid, thread_obj.type, message)
    else:
        form = MessageForm(auto_id=False)

    # PROCESS MESSAGES

    name = thread_obj.name

    print('processing messages...')

    client.back_log_messages(thread_obj)

    raw_messages = client.message_log[thread_obj.uid][-10:]

    msg_num = 1
    for message in raw_messages:
        last_msg_flag = msg_num == 10  # todo: can't assume this?

        formatted_msg = client.handle_message(message, thread_obj, last_msg_flag)

        # temp fix below
        username = cache_username_author.get(formatted_msg.get('author'))
        if username is None:
            username = client.fetchUserInfo(formatted_msg.get('author')).get(
                formatted_msg.get('author')).name
            cache_username_author[formatted_msg.get('author')] = username

        formatted_msg['username'] = username

        formatted_msg['div'] = 'not-me'

        if client.uid == formatted_msg.get('author'):
            formatted_msg['div'] = 'me'

        messages.append(formatted_msg)

        msg_num += 1

    print("... done.")

    print("saving log...")
    with open(f'messengerSecured/functionality/user-{MS.username}/messageLog.txt', 'w') as outfile:  # save msg log
        json.dump(client.message_log, outfile)
    print("... done")

    return render(request, 'messengerSecured/thread.html', {'name': name, 'msgs': messages, 'form': form})
