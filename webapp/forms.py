from django import forms 
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class TestManualeForm(forms.Form):
    numeroTest = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control"}), label = False)
    inSequenza = forms.BooleanField(widget=forms.CheckboxInput(attrs={"class": "form-control"}), label = "In sequenza", required=False)
    secondiRitardo = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control"}), label = False)
    