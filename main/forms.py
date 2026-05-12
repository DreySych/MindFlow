from email.policy import default
from django import forms


class SearchForm(forms.Form):
    input_text = forms.CharField()
