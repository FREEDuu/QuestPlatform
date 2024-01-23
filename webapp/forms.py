from django import forms 
from django.contrib.auth.models import User

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class TestManualeForm(forms.Form):
    testNumber = forms.IntegerField
    inSequenza = forms.BooleanField
    secondiRitardo = forms.IntegerField