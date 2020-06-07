from django import forms


class LogInForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class MessageForm(forms.Form):
    message = forms.CharField(label="")
    encrypted = forms.BooleanField(label="Encrypt?")
