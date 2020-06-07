from django import forms


class LogInForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Email...'}), label="")
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password...'}), label="")


class MessageForm(forms.Form):
    message = forms.CharField(label="")
    # encrypted = forms.BooleanField(label="")
