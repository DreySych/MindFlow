from django import forms

class ComplaintForm(forms.Form):
    description = forms.CharField()