from django import forms 
from django.contrib.auth.models import User
from django.core import validators
from django.core.validators import MinValueValidator
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

messages={
            'required': _("Questo campo non può essere negativo"),
        }

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class GruppiForm(forms.Form):
    nGruppo = forms.IntegerField()
    
class TestManualeForm(forms.Form):
    numeroTest = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control"}), label = False, validators=[validators.MinValueValidator(0)], error_messages=messages)

class TestSfidaManualeForm(forms.Form):
    CHOICES = (('Option 1', 'Option 1'),('Option 2', 'Option 2'),)
    utenteSfidato = forms.ChoiceField(choices=CHOICES, widget=forms.ChoiceField(attrs={"class": "selectpicker","data-live-search": "true"}))
    numeroTest = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control"}), label = False, validators=[validators.MinValueValidator(0)], error_messages=messages)
    
class TestOrarioEsattoForm(forms.Form):
    numeroTest = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control"}), label = False, validators=[validators.MinValueValidator(0)], error_messages=messages)
    secondiRitardo = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control"}), label = False, validators=[validators.MinValueValidator(0)], error_messages=messages)
        
class TestSfidaOrarioEsattoForm(forms.Form):
    utenteSfidato = forms.CharField()
    numeroTest = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control"}), label = False, validators=[validators.MinValueValidator(0)], error_messages=messages)
    secondiRitardo = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control"}), label = False, validators=[validators.MinValueValidator(0)], error_messages=messages)
        