# messengerSecured
This is a client for facebook messenger that allows users to log in and user messenger in an encrypted mode (RSA 2048 encryption). 

It uses protocols for requesting and storing public keys to associate with friends who are also using this messenger encrypted client, and ofcourse protocols to encrypt and decrypt outgoing and incoming messages with friends.

The app can be ran with a very minimal tkinter python3+ GUI via messengerSecured/GUI.py, however preferably it is ran with python3+ via djangoGUI/manange.py - `python manage.py runserver`


**!IMPORTANT NOTES!**

Since this client uses an unofficial facebook API (fbchat) to comunicate with servers, the following should be done to decrease chances of facebook temporarily locking your account:
- Enable 2FA on facebook account before using (and then enter in CLI 
- Test on alt account first
- Do not spam create sessions
- Do not spam messages
