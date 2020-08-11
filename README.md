# messengerSecured (Alpha 1.0)
This is a client for facebook messenger that allows users to log in and use messenger in an encrypted mode (RSA-2048 encryption). 

It uses custom protocols for requesting and storing public keys to associate with friends who are also using messengerSecured, and ofcourse protocols to encrypt and decrypt outgoing and incoming messages with friends.

Encryption keys are held only locally to allow for completely secure messaging through facebook servers.


## Requirements
1. Python 3+ 
2. Pip (Use `python get-pip.py` in commandline if not already installed)
3. Virtual Environment (Use `pip install virtualenv` in commandline if not already installed)

## Installation Process
This application is best ran through a virtual environment on python 3+
1. From inside djangoGUI directory, initialize a virtual environment (in commandline `virtualenv venv`)
2. Activate the virtual environment (Windows: `venv\Scripts\activate`. Linux/Mac: `source venv/bin/activate`)
3. Install the requirements (In commandline: `pip install -r requirements.txt`)

## Launch Process
1. From inside djangoGUI directory, run manage.py runserver (`python manage.py runserver`)
2. In browser go to URL "localhost:8000/messenger"
3. That's it!

## Secure Messaging Process
1. After logging in with messengerSecured, open up a chat window with anyone on your messenger contacts
2. Send any random message to this person, if it is the first time you have sent them a message through messengerSecured, they will be sent a public key request
3. After they open your chat on their own messengerSecured app, a public key response will automatically be sent to you from them
4. Your app will now remember this persons public key and use it to automatically encrypt any more messages you send to them


This app can also be ran with the minimal tkinter GUI found inside messengerSecured/GUI.py, however the djangoGUI is preferred

## Important Notes

Since this client uses an unofficial facebook API (fbchat) to comunicate with servers, the following actions are reccomended to decrease chances of facebook temporarily locking your account:
- Enable 2FA on facebook account before using
- Test on alt account first
- Do not spam create sessions
- Do not spam messages

## Disclaimer
messengerSecured isn't authorised by facebook and is against their ToS, so proceed with caution.. I'm not responsible for any actions taken against your facebook/messenger account when using this app.
