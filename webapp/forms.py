from django import forms 
from django.contrib.auth.models import User
from django.core import validators
from django.core.validators import MinValueValidator
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from .models import *
from  random import randint, random
import string
def Create_other_var(array):

    for _ in range(randint(4,10)):
        array.append(''.join(random.choices(string.ascii_lowercase, k=randint(6,13))))

    return array
messages={
            'required': _("Non fare il furbo :D"),
        }

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class FormTestCollettivi(forms.Form):
    
    nPagine = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control"}), label = False, error_messages=messages)
    ora = forms.DateTimeField(widget=forms.DateTimeInput(
        attrs={
            "class": "form-control",
            "data-field": "datetime",
            "required": "required",
            "name": "dataOraInizio", 
            "type": "text",
        }), label = False)
    def clean_dataOraInizio(self):
        input_date = self.cleaned_data.get('dataOraInizio')
        if input_date:
            if input_date < timezone.now():
                raise ValidationError("La data deve essere nel futuro.")
            return input_date
        return None

class FormDomandaCollettiva(forms.Form):
    
    tipo = forms.CharField()
    Domanda = forms.CharField()
    Risposta = forms.CharField()
    Varianti = forms.CharField()

class GruppiForm(forms.Form):

    def __init__(self,req, nDomande, idTest):
        super().__init__()

        domande = Test_Domande_Varianti.objects.filter(
            test = idTest
        )

        for i in range(len(domande)):
            field_name = 'domanda_%s' % (i,)
            self.fields[field_name] = forms.ChoiceField(required=True, choices = ())

    
class TestManualeForm(forms.Form):
    numeroTest = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control"}), label = False, validators=[validators.MinValueValidator(0)], error_messages=messages)
    secondiRitardo = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control"}), label = False, validators=[validators.MinValueValidator(30)], error_messages=messages)
    dataOraInizio = forms.DateTimeField(widget=forms.DateTimeInput(
        attrs={
            "class": "form-control",
            "data-field": "datetime",
            "required": "required",
            "name": "dataOraInizio", 
            "type": "text",
        }), label = False)
    
    def clean_dataOraInizio(self):
        input_date = self.cleaned_data.get('dataOraInizio')
        if input_date:
            if input_date < timezone.now():
                raise ValidationError("La data deve essere nel futuro.")
            return input_date
        return None
    
class TestSfidaManualeForm(forms.Form):

    utenteSfidato = forms.ChoiceField()
    numeroTest = forms.IntegerField(widget=forms.NumberInput(), label = False, validators=[validators.MinValueValidator(0)], error_messages=messages)
    
class TestOrarioEsattoForm(forms.Form):
    numeroTest = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control"}), label = False, validators=[validators.MinValueValidator(0)], error_messages=messages)
    secondiRitardo = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control"}), label = False, validators=[validators.MinValueValidator(0)], error_messages=messages)
        
class TestSfidaOrarioEsattoForm(forms.Form):
    utenteSfidato = forms.CharField()
    numeroTest = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control"}), label = False, validators=[validators.MinValueValidator(0)], error_messages=messages)
    secondiRitardo = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control"}), label = False, validators=[validators.MinValueValidator(0)], error_messages=messages)
        