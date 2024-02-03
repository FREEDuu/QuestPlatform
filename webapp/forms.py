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

class TestManualeForm(forms.Form):
    numeroTest = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control"}), label = False, validators=[validators.MinValueValidator(0)], error_messages=messages)
    inSequenza = forms.BooleanField(widget=forms.CheckboxInput(attrs={"class": "form-control"}), label = "In sequenza", required=False)
    secondiRitardo = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control"}), label = False, validators=[validators.MinValueValidator(0)], error_messages=messages)

class GruppiForm(forms.Form):
    nGruppo = forms.IntegerField()

   
class TestOrarioEsattoForm(forms.Form):
    numeroTest = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control"}), label = False, validators=[validators.MinValueValidator(0)], error_messages=messages)
    inSequenza = forms.BooleanField(widget=forms.CheckboxInput(attrs={"class": "form-control"}), label = "In sequenza", required=False)
    secondiRitardo = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control"}), label = False, validators=[validators.MinValueValidator(0)], error_messages=messages)
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
        