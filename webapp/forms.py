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
from django.forms.widgets import RadioSelect

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
    
    nPagine = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control"}), label = False, error_messages=messages , validators=[validators.MinValueValidator(1)])
    dataOraInizio = forms.DateTimeField(widget=forms.DateTimeInput(
        attrs={
            "class": "form-control",
            "data-field": "datetime",
            "required": "required",
            "name": "dataOraInizio", 
            "type": "text",
            "autocomplete": "off"
        }), label = False)

class CustomMultiWidget(forms.MultiWidget):
    def __init__(self, common_attrs, widgetCount, attrs=None):
        widgets = [forms.TextInput(attrs=common_attrs) for _ in range(widgetCount)]
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return value
        return [None for _ in range(len(self.widgets))]


class CustomMultiValueField(forms.MultiValueField):
    def __init__(self, char_fields, common_attrs, *args, **kwargs):
        fields = (char_fields)
        super().__init__(fields, widget=CustomMultiWidget(common_attrs, len(char_fields)), *args, **kwargs)

    def compress(self, data_list):
        return data_list


class FormDomanda(forms.Form):
    
    def __init__(self, domande, risposte_esatte, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i in range(len(domande)):
            field_name = 'domanda_%s' % (i,)
            if domande[i] == 't':
                self.fields[field_name] = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control", "autocomplete": "off"}), required= False)
            elif domande[i] == 'c':
                self.fields[field_name] = forms.ChoiceField(widget=forms.RadioSelect(attrs={"class": "forms-control"}),  required= False) 
            elif domande[i] == 'cr':
                self.fields[field_name] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple() , required= False)
            elif domande[i] == 'm':
                common_attrs = {"class": "form-control", "autocomplete": "off", "maxlength": "1", "style": "width: 38px; margin-right: 10px;"}
                numero_input = len(risposte_esatte[i])
                
                char_fields = [forms.CharField() for _ in range(numero_input)]

                self.fields[field_name] = CustomMultiValueField(char_fields, common_attrs, required= False)
            else:
                self.fields[field_name] = forms.ChoiceField(widget=forms.Select(attrs={"class": "form-control"}), choices=[('', 'Selezionare opzione'), ('1', '1'), ('2', '2'), ('3', '3')], initial='', required= False)

    def get_interest_fields(self):
        ret = []
        for field_name in self.fields:
            print(self[field_name])
            yield self[field_name]
    

class FormDomandaCollettiva(forms.Form):
    tipo = forms.CharField(
        widget=forms.TextInput(attrs={
            "required": "required",
            "class": "form-control",
            "autocomplete": "off",
            'placeholder': 'Tipo'  # Placeholder text adjusted for clarity
        })
    )
    Domanda = forms.CharField(
        widget=forms.Textarea(attrs={
            "required": "required",
            "class": "form-control",
            "autocomplete": "off",
            'placeholder': 'Inserisci la domanda qui...',
            'rows': 2
        })
    )
    Risposta = forms.CharField(
        widget=forms.Textarea(attrs={
            "required": "required",
            "class": "form-control",
            "autocomplete": "off",
            'placeholder': 'Inserisci la risposta qui...',
            'rows': 2
        })
    )
    Varianti = forms.CharField(
        widget=forms.Textarea(attrs={
            "required": "required",
            "class": "form-control",
            "autocomplete": "off",
            'placeholder': 'Inserisci varianti separate da punto e virgola...',
            'rows': 2
        })
    )
class FormDomandaCollettivaCrea(forms.Form):
    
    tipo = forms.CharField(widget = forms.TextInput(attrs={"required": "required","class": "form-control", "autocomplete": "off",'placeholder': 'tipo'}))
    Domanda = forms.CharField(widget = forms.TextInput(attrs={"required": "required","class": "form-control", "autocomplete": "off",'placeholder': 'domanda'}))
    Risposta = forms.CharField(widget = forms.TextInput(attrs={"required": "required","class": "form-control", "autocomplete": "off", 'placeholder': 'risposta'}))

    
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
            "autocomplete": "off"
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

    utente = forms.ChoiceField(widget = forms.Select(attrs={"class": "form-control"}), required = True,)
    
    dataOraInizio = forms.DateTimeField(widget=forms.DateTimeInput(
        attrs={
            "class": "form-control",
            "data-field": "datetime",
            "required": "required",
            "name": "dataOraInizio", 
            "type": "text",
            "autocomplete": "off"
        }), label = False)
