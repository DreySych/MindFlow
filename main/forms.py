from email.policy import default
from django import forms
from .models import *

class SearchForm(forms.Form):
    input_text = forms.CharField()