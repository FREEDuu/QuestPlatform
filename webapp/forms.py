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
    

class FormDomanda(forms.Form):
    
    def __init__(self, domande, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i in range(len(domande)):
            field_name = 'domanda_%s' % (i,)
            if domande[i] == 't':
                self.fields[field_name] = forms.CharField(widget = forms.TextInput(attrs={"class": "form-control"}))
            elif domande[i] == 'c':
                self.fields[field_name] = forms.ChoiceField(widget = forms.RadioSelect(attrs={"class": "forms-control"})) 
            else:
                self.fields[field_name] = forms.ChoiceField(widget = forms.Select(attrs={"class": "form-control"}), 
                choices = ([('1','1'), ('2','2'),('3','3'), ]), required = True,)
            
    def get_interest_fields(self):
        ret = []
        for field_name in self.fields:
            print(self[field_name])
            yield self[field_name]
    

class FormDomandaCollettiva(forms.Form):
    
    tipo = forms.CharField()
    Domanda = forms.CharField()
    Risposta = forms.CharField()
    Varianti = forms.CharField()

    
class TestManualeForm(forms.Form):
    numeroTest = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control"}), label = False, validators=[validators.MinValueValidator(0)], error_messages=messages)
    secondiRitardo = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control"}), label = False, validators=[validators.MinValueValidator(30)], error_messages=messages, initial = 30)
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
    secondiRitardo = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control"}), label = False, validators=[validators.MinValueValidator(0)], error_messages=messages, initial= 5)
        
class TestSfidaOrarioEsattoForm(forms.Form):
    utenteSfidato = forms.CharField()
    numeroTest = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control"}), label = False, validators=[validators.MinValueValidator(0)], error_messages=messages)
    secondiRitardo = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control"}), label = False, validators=[validators.MinValueValidator(0)], error_messages=messages)
        