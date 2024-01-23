from django import forms 
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class TestManualeForm(forms.Form):
    testNumber = forms.IntegerField(
        validators=[MinValueValidator(0)],
    )
    inSequenza = forms.BooleanField()
    secondiRitardo = forms.IntegerField()
