from django.shortcuts import render, redirect
from messengerSecured.forms import LogInForm
from .functionality import messengerSecured as MS

client = MS.Bot("ff", "ff", None, True)


def home(request):
    return render(request, 'messengerSecured/home.html')


def about(request):
    return render(request, 'messengerSecured/about.html')


def login(request):
    global client

    if request.method == 'POST':
        form = LogInForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            print(f"{email} {password}")
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
        clean_threads.append({'name': thread.name, 'text': text})

    print(clean_threads)

    return render(request, 'messengerSecured/recentThreads.html', {'threads': clean_threads})
