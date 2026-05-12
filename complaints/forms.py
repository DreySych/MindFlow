from django import forms

class ComplaintForm(forms.Form):
    description = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'required': True,
            'placeholder': 'Введите причину жалобы'
        })
    )
